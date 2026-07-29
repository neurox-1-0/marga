from typing import Any, Dict
from datetime import datetime, timezone
from ..state import AgentState
from langgraph.types import interrupt
import datetime
from ..schemas.api import ApprovalCard, EventSchema, ExposureSchema, CostAnalysisSchema, FreightOptionsSchema, FreightQuoteSchema, BestQuoteRef

def hitl_gate_node(state: AgentState) -> Dict[str, Any]:
    """
    Builds an ApprovalCard from the current agent state, stores it in cards_db
    so the dashboard can display it, then halts execution via LangGraph's
    interrupt() and waits for a human decision from the dashboard.
    """
    from ..routers.hitl import cards_db
    
    cost_analysis_dict = state.get("cost_analysis", {}) or {}
    
    # Handle the case where best_reroute_option is a string vs dict
    best_option = cost_analysis_dict.get("best_reroute_option")
    best_quote_ref = None
    if best_option:
        if isinstance(best_option, dict):
            best_quote_ref = BestQuoteRef(quote_id=best_option.get("quote_id", ""))
        else:
            best_quote_ref = BestQuoteRef(quote_id=best_option)
    
    # Map state to ApprovalCard
    card = ApprovalCard(
        event=EventSchema(
            event_id=state.get("event_id", "Unknown"),
            detected_at=datetime.datetime.now(),
            source=state.get("raw_event", {}).get("source", "System"),
            vessel_id=state.get("raw_event", {}).get("vessel_id", "Unknown"),
            route=state.get("raw_event", {}).get("route", "Unknown"),
            description=state.get("raw_event", {}).get("description", "Unknown")
        ),
        exposure=ExposureSchema(
            matched_pos=state.get("matched_pos", []) or [],
            total_inventory_value_usd=state.get("exposure_value", 0.0) or 0.0
        ),
        cost_analysis=CostAnalysisSchema(
            stockout_cost_usd=cost_analysis_dict.get("stockout_cost_usd", 0.0) or 0.0,
            reroute_savings_usd=cost_analysis_dict.get("reroute_savings_usd", 0.0) or 0.0,
            recommendation=cost_analysis_dict.get("recommendation", ""),
            best_reroute_option=best_quote_ref
        ),
        freight_options=FreightOptionsSchema(
            quotes=[FreightQuoteSchema(**q) for q in (state.get("freight_quotes") or [])]
        ),
        status="pending"
    )

    # Put it in the DB!
    cards_db[state["event_id"]] = card

    # We use LangGraph's interrupt to pause the graph.
    decision_payload = interrupt("Waiting for human approval via dashboard.")

    return {
        "approval_decision": decision_payload.get("decision"),
        "chosen_quote_id": decision_payload.get("chosen_quote_id"),
        "manager_note": decision_payload.get("manager_note"),
    }
