# Marga API Contract & Frontend Integration

This document defines the exact JSON shapes expected by the frontend (Dashboard) and the schemas the backend must expose.

## 1. REST Endpoints (HITL / Dashboard)

### `GET /cards/pending`
Returns a list of `ApprovalCard` objects that require a human decision.

**Response Body:**
```json
[
  {
    "event": {
      "event_id": "EVT-1234",
      "detected_at": "2026-07-27T10:00:00Z",
      "source": "NOAA / Reuters",
      "vessel_id": "V-559",
      "route": "Suez Canal",
      "description": "Vessel blocked due to sandstorm."
    },
    "exposure": {
      "matched_pos": ["PO-001", "PO-002"],
      "total_inventory_value_usd": 1500000.50
    },
    "cost_analysis": {
      "stockout_cost_usd": 500000.00,
      "reroute_savings_usd": 120000.00,
      "recommendation": "Reroute via air freight to minimize stockout costs.",
      "best_reroute_option": {
        "quote_id": "Q-001"
      }
    },
    "freight_options": {
      "quotes": [
        {
          "quote_id": "Q-001",
          "carrier": "FedEx",
          "mode": "Air",
          "cost_usd": 45000.00,
          "transit_days": 3
        }
      ]
    },
    "status": "pending"
  }
]
```

### `POST /cards/{event_id}/decision`
Submit a decision (Approve/Reject) for a disruption event. This endpoint triggers the LangGraph `Command(resume=...)`.

**Request Body:**
```json
{
  "event_id": "EVT-1234",
  "decision": "approved", // or "rejected"
  "chosen_quote_id": "Q-001", // can be null if rejected
  "manager_note": "Approved via Dashboard"
}
```

**Response Body:**
```json
{
  "status": "recorded",
  "decision": "approved"
}
```

## 2. WebSocket Events (Real-Time State)

The frontend will connect to `ws://localhost:8004/ws/dashboard`. The backend will push events to provide transparent reasoning and graph progression.

### Event: `agent_thought`
Pushed when the LangGraph agent is executing a tool or using the LLM.

```json
{
  "type": "agent_thought",
  "data": {
    "node": "reasoning_node",
    "thought": "I need to query the ERP system for POs on vessel V-559.",
    "confidence_score": 0.95,
    "tool_calls": [
      {
        "tool_name": "query_erp",
        "rationale": "Checking for impacted inventory."
      }
    ]
  }
}
```

### Event: `state_update`
Pushed when LangGraph transitions to a new node, effectively checkpointing the state.

```json
{
  "type": "state_update",
  "data": {
    "current_node": "hitl_gate",
    "tracking_id": "EVT-1234",
    "state_summary": "Waiting for human approval."
  }
}
```
