from typing import Any, Dict
from datetime import datetime, timezone
from ..state import AgentState
from langgraph.types import interrupt
from ...storage import cards_db
from ...schemas.api import (
    ApprovalCard, EventSchema, ExposureSchema,
    CostAnalysisSchema, FreightOptionsSchema, FreightQuoteSchema, BestQuoteRef
)

def hitl_gate_node(state: AgentState) -> Dict[str, Any]:
    """
    Builds an ApprovalCard from the current agent state, stores it in cards_db
    so the dashboard can display it, then halts execution via LangGraph's
    interrupt() and waits for a human decision from the dashboard.
    """
    event_id = state["event_id"]
    raw = state.get("raw_event", {})

    # ── Build EventSchema ──────────────────────────────────────────────────
    event = EventSchema(
        event_id=event_id,
        detected_at=datetime.now(timezone.utc),
        source=raw.get("source", "Unknown"),
        vessel_id=raw.get("vessel_id", "Unknown"),
        route=raw.get("route", "Unknown"),
        description=raw.get("description", "No description provided."),
    )

    # ── Build ExposureSchema ───────────────────────────────────────────────
    matched_pos = state.get("matched_pos") or []
    exposure = ExposureSchema(
        matched_pos=matched_pos,
        total_inventory_value_usd=state.get("exposure_value") or 0.0,
    )

    # ── Build FreightOptionsSchema ─────────────────────────────────────────
    raw_quotes = state.get("freight_quotes") or []
    quotes = [
        FreightQuoteSchema(
            quote_id=q.get("quote_id", "Q-?"),
            carrier=q.get("carrier", "Unknown"),
            mode=q.get("mode", "Unknown"),
            cost_usd=float(q.get("cost_usd", 0)),
            transit_days=int(q.get("transit_days", 0)),
        )
        for q in raw_quotes
    ]
    freight_options = FreightOptionsSchema(quotes=quotes)

    # ── Build CostAnalysisSchema ───────────────────────────────────────────
    raw_cost = state.get("cost_analysis") or {}
    best_quote_raw = raw_cost.get("best_reroute_option")
    cost_analysis = CostAnalysisSchema(
        stockout_cost_usd=float(raw_cost.get("stockout_cost_usd", 0)),
        reroute_savings_usd=float(raw_cost.get("reroute_savings_usd", 0)),
        recommendation=raw_cost.get("recommendation", "Insufficient data to recommend."),
        best_reroute_option=BestQuoteRef(quote_id=best_quote_raw["quote_id"]) if best_quote_raw else None,
    )

    # ── Store card so dashboard can find it ───────────────────────────────
    card = ApprovalCard(
        event=event,
        exposure=exposure,
        cost_analysis=cost_analysis,
        freight_options=freight_options,
        status="pending",
    )
    cards_db[event_id] = card

    # ── Broadcast state update via WebSocket ──────────────────────────────
    import asyncio
    try:
        from ...websockets.manager import manager
        import json
        asyncio.get_event_loop().run_until_complete(
            manager.broadcast(json.dumps({
                "type": "state_update",
                "data": {
                    "current_node": "hitl_gate",
                    "tracking_id": event_id,
                    "state_summary": f"Waiting for human approval. {len(matched_pos)} POs at risk.",
                }
            }))
        )
    except Exception:
        pass  # WebSocket broadcast is non-critical

    # ── Pause graph, wait for human via POST /cards/{id}/decision ─────────
    decision_payload = interrupt("Waiting for human approval via dashboard.")

    return {
        "approval_decision": decision_payload.get("decision"),
        "chosen_quote_id": decision_payload.get("chosen_quote_id"),
        "manager_note": decision_payload.get("manager_note"),
    }
