import os
import time
import requests
import argparse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from google import genai
from google.genai import types

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from shared.schemas import DisruptionEvent, ERPExposureResponse, FreightQuoteResponse, ApprovalCard, FreightQuote, PurchaseOrder
from monitoring.monitor import manual_trigger, fetch_live_disruptions
from agent.cost_engine import analyze_costs
from hitl.notifier import notify_channels

# Service URLs
ERP_API_URL = "http://localhost:8001"
FREIGHT_API_URL = "http://localhost:8002"
APPROVAL_API_URL = "http://localhost:8004"

# Setup Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Pydantic schemas for Gemini structured output
class RelevanceJudgment(BaseModel):
    relevant: bool
    confidence: float
    reasoning: str

class AmbiguityDecision(BaseModel):
    action: str  # e.g., 'proceed_with_caveat', 'skip_event', 'flag_for_scrutiny'
    explanation: str

def safe_request(method: str, url: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None, retries: int = 2) -> Optional[requests.Response]:
    """Helper for HTTP calls with retry backoff."""
    delay = 1.0
    for attempt in range(retries + 1):
        try:
            if method.upper() == 'GET':
                resp = requests.get(url, params=params, timeout=10)
            else:
                resp = requests.post(url, json=json_data, timeout=10)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            if attempt == retries:
                print(f"HTTP call failed after {retries} retries: {e}")
                return None
            print(f"HTTP call to {url} failed. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
    return None

def judge_relevance(event: DisruptionEvent) -> RelevanceJudgment:
    """Uses Gemini function calling to determine if a disruption event is relevant to supply chain operations."""
    prompt = f"Analyze this disruption event: {event.description}. Is it likely to cause supply chain delays?"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RelevanceJudgment,
                temperature=0.1
            ),
        )
        return RelevanceJudgment.model_validate_json(response.text)
    except Exception as e:
        print(f"Gemini relevance judgment failed: {e}. Falling back to basic threshold.")
        return RelevanceJudgment(
            relevant=(event.confidence > 0.7),
            confidence=event.confidence,
            reasoning="Fallback threshold used due to API failure."
        )

def handle_erp_ambiguity(exposure: ERPExposureResponse, event: DisruptionEvent) -> AmbiguityDecision:
    """Uses Gemini to decide what to do when ERP returns ambiguous match data."""
    prompt = (
        f"We found some purchase orders possibly affected by event '{event.source}' (vessel {event.vessel_id}), "
        f"but the ERP returned this warning: '{exposure.data_quality_note}'. "
        f"We have {len(exposure.matched_pos)} total POs matched. "
        "Should we 'proceed_with_caveat' (add a warning), 'skip_event' (too risky to act), or 'flag_for_scrutiny' (force human review)?"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AmbiguityDecision,
                temperature=0.1
            ),
        )
        return AmbiguityDecision.model_validate_json(response.text)
    except Exception as e:
        print(f"Gemini ambiguity handling failed: {e}. Falling back to 'flag_for_scrutiny'.")
        return AmbiguityDecision(action="flag_for_scrutiny", explanation="Fallback action due to API failure.")

def draft_summary(card_data: dict) -> str:
    """Uses Gemini to draft a human-readable summary (plain text generation)."""
    prompt = f"Summarize this supply chain situation briefly for a human manager: {card_data}"
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4)
        )
        return response.text
    except Exception:
        return "Summary generation failed."

def run_loop(manual: bool = False):
    print("--- Starting Orchestrator Loop ---")
    events = manual_trigger() if manual else fetch_live_disruptions()
    
    if not events:
        print("No active events found. Exiting.")
        return

    for event in events:
        print(f"\nProcessing Event: {event.event_id}")
        
        # 1. Assess Relevance
        judgment = judge_relevance(event)
        print(f"Relevance Judgment: {judgment.relevant} ({judgment.reasoning})")
        if not judgment.relevant:
            continue
            
        # 2. Query ERP
        vessel = event.vessel_id or "Unknown"
        route = event.route or "Unknown"
        erp_resp_raw = safe_request('GET', f"{ERP_API_URL}/exposure", params={'vessel_id': vessel, 'route': route})
        if not erp_resp_raw:
            print("Failed to get ERP data. Skipping.")
            continue
            
        exposure = ERPExposureResponse.model_validate(erp_resp_raw.json())
        
        if len(exposure.matched_pos) == 0:
            print("No POs matched. Stopping loop cleanly.")
            continue
            
        # 3. Handle Ambiguity if present
        if exposure.data_quality_note:
            print(f"ERP Note: {exposure.data_quality_note}")
            ambiguity_decision = handle_erp_ambiguity(exposure, event)
            print(f"Ambiguity Action: {ambiguity_decision.action} ({ambiguity_decision.explanation})")
            
            if ambiguity_decision.action == "skip_event":
                print("Skipping event due to ambiguity.")
                continue
            elif ambiguity_decision.action == "flag_for_scrutiny":
                exposure.data_quality_note += " (AI FLAGGED FOR SCRUTINY: " + ambiguity_decision.explanation + ")"
            # If proceed_with_caveat, we just continue
            
        # 4. Query Freight
        weight_kg = sum(po.quantity * 2 for po in exposure.matched_pos) # Assume 2kg per unit
        
        # Extract origin/destination from route (e.g. "Shanghai to Los Angeles")
        parts = route.split(" to ")
        if len(parts) == 2:
            origin, dest = parts[0], parts[1]
        else:
            origin, dest = "Unknown", "Unknown"
            
        freight_resp_raw = safe_request('GET', f"{FREIGHT_API_URL}/quotes", params={
            'origin': origin, 'destination': dest, 'weight_kg': weight_kg
        })
        
        freight_options = FreightQuoteResponse(origin=origin, destination=dest, quotes=[])
        if freight_resp_raw:
            freight_options = FreightQuoteResponse.model_validate(freight_resp_raw.json())
        else:
            print("Warning: Failed to fetch freight quotes. Proceeding with empty options.")
            
        # 5. Compare Cost
        cost_analysis = analyze_costs(exposure, event.delay_days_estimate, freight_options.quotes)
        
        # 6. Build Approval Card
        card = ApprovalCard(
            event=event,
            exposure=exposure,
            freight_options=freight_options,
            cost_analysis=cost_analysis
        )
        
        summary = draft_summary(card.model_dump())
        print(f"Generated Summary: {summary}")
        
        # 7. Register with Approval API
        reg_resp = safe_request('POST', f"{APPROVAL_API_URL}/cards", json_data=card.model_dump(mode='json'))
        if not reg_resp:
            print("Failed to register card with Approval API.")
            continue
            
        print(f"Card registered on Approval API for event {event.event_id}")
        
        # 8. Notify Channels
        notify_channels(card)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", action="store_true", help="Trigger a manual demo event")
    args = parser.parse_args()
    
    if not api_key:
        print("WARNING: GEMINI_API_KEY environment variable not set! Exiting.")
        sys.exit(1)
        
    run_loop(manual=args.manual)
