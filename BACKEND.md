# Marga Backend Architecture & Integration Guide

## 1. Backend Overview
The Marga backend is a Python-based autonomous agent system designed to handle supply chain disruptions. 
- **Language/Framework:** Python with FastAPI.
- **Agentic Framework:** It uses **LangGraph** to manage the state machine and agentic loop, powered by the **Google Gemini API** (`gemini-flash-latest`) for reasoning.
- **External Tools Integrated:**
  1. **ERP API:** Fetches purchase orders (POs) and inventory exposed by a disruption.
  2. **Freight API:** Fetches live alternative routing quotes (e.g., Air-freight).
  3. **Cost Engine:** Calculates stockout costs and potential savings.
  4. **Live Monitoring:** Fetches disruption events (e.g., NOAA maritime alerts).
- **Agentic Loop:** Triggered by an incoming disruption event. The LangGraph `router_node` dictates the flow. The agent assesses the event's relevance, queries the ERP, handles any ambiguous data by reasoning through it, checks freight quotes, and finally pauses at a `hitl_gate` (Human-in-the-Loop) where it waits for an API call from the frontend to proceed.
- **Failures & Retries:** It uses a `safe_request` wrapper with exponential backoff for HTTP failures. If the Gemini API fails, the system safely falls back to deterministic thresholds or explicitly flags the event for human scrutiny.

---

## 2. API Endpoints for Frontend

The FastAPI server exposes the following endpoints that your Next.js frontend needs to call:

### A. Get Pending Approvals
- **URL:** `GET /cards/pending`
- **Description:** Fetches all disruption events that are currently paused at the HITL gate waiting for human review.
- **Input:** None
- **Output:** A JSON array of `ApprovalCard` objects.
```json
[
  {
    "event": {
      "event_id": "EVT-9999",
      "detected_at": "2026-07-28T12:00:00Z",
      "source": "NOAA",
      "vessel_id": "V-559",
      "route": "Suez",
      "description": "Sandstorm"
    },
    "exposure": {
      "matched_pos": ["PO-4471", "PO-4489"],
      "total_inventory_value_usd": 184000.0
    },
    "cost_analysis": {
      "stockout_cost_usd": 28000.0,
      "reroute_savings_usd": 23500.0,
      "recommendation": "Reroute via Air",
      "best_reroute_option": {"quote_id": "Q-101"}
    },
    "freight_options": {
      "quotes": [
        {
          "quote_id": "Q-101",
          "carrier": "FedEx",
          "mode": "Air",
          "cost_usd": 4500.0,
          "transit_days": 3
        }
      ]
    },
    "status": "pending",
    "chosen_quote_id": null
  }
]
```

### B. Submit Human Decision (HITL)
- **URL:** `POST /cards/{event_id}/decision`
- **Description:** Sends the human manager's decision back to the agent to resume the LangGraph workflow.
- **Input (JSON Body):**
```json
{
  "event_id": "EVT-9999",
  "decision": "approved",
  "chosen_quote_id": "Q-101",
  "manager_note": "Proceed with air freight."
}
```
- **Output:**
```json
{
  "status": "recorded",
  "decision": "approved"
}
```

### C. Trigger Demo Disruption
- **URL:** `POST /trigger_disruption?event_id=EVT-9999`
- **Description:** Kickstarts the agent graph for a demo.
- **Output:** `{"status": "started", "thread_id": "EVT-9999"}`

### D. Live Agent Thoughts (WebSocket)
- **URL:** `ws://localhost:8000/ws/dashboard`
- **Description:** Stream live reasoning and tool-call events to the frontend.

---

## 3. Running the Backend Locally

**Prerequisites:**
You need a Gemini API key. Add it to a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_key_here
```

**Starting the server:**
Navigate to the root directory and start the unified backend using uvicorn:
```bash
uvicorn backend.main:app --reload --port 8000
```
*(Note: If using the mock APIs described in the original README, you must also run those scripts on ports 8001, 8002, 8003).*
