# Autonomous Supply Chain Disruption Agent

This project is a working prototype of an autonomous B2B agent that monitors global shipping disruptions, identifies affected purchase orders (POs), evaluates alternative routing costs, and requests human approval before booking.

## Setup Instructions

1. Ensure you have Python 3.11+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate synthetic data (PO and freight rates):
   ```bash
   python data/generate_data.py
   ```
4. Copy `.env.example` to `.env` and fill in your `GEMINI_API_KEY`. (Optional: Add Slack webhook and email config for notifications). Set `NOTIFICATION_CHANNELS` as desired.

## Running the Services

You need to start four separate FastAPI services, a simple HTTP server for the dashboard, and then you can trigger the Orchestrator.

Open separate terminal windows and run:

**1. Mock ERP API (Port 8001)**
```bash
python mock_erp_api/main.py
```

**2. Mock Freight API (Port 8002)**
```bash
python mock_freight_api/main.py
```

**3. Booking API (Port 8003)**
```bash
python booking_api/main.py
```

**4. Approval API (Port 8004)**
```bash
python hitl/approval_api.py
```

**5. Dashboard (Port 8000)**
```bash
# Serve the hitl directory so dashboard.html is accessible
python -m http.server 8000 --directory hitl
```
Access the dashboard at: `http://localhost:8000/dashboard.html`

## Running a Demo

Once all services are up and running, you can trigger a hardcoded manual disruption event to demonstrate the agent's full loop. This uses `--manual` to skip live NOAA polling and inject a reliable demo event.

```bash
# Run the orchestrator
python agent/orchestrator.py --manual
```

Watch the orchestrator output as it:
1. Assesses the relevance of the event via Gemini.
2. Queries the ERP API, encountering an ambiguous data note due to a 0.6 match confidence PO.
3. Uses Gemini to determine how to handle the ambiguity.
4. Queries the Freight API for options.
5. Computes cost comparisons in the Cost Engine.
6. Submits an Approval Card to the Approval API and notifies enabled channels.

Once the card is generated, go to the **Dashboard** in your browser, review the event, select an alternative quote, and click **Approve**.

## Hackathon Simplifications (Notes for Judges)
- **Data APIs:** ERP (SAP) and Freight API integrations are mocked using simple JSON responses.
- **Booking consequences:** The `/book` endpoint validates that a human approved it, but doesn't actually book anything.
- **In-memory state:** The Approval API uses an in-memory dictionary rather than a database. State resets on restart.
- **Dashboard routing:** The dashboard directly polls the Approval API instead of using WebSockets or SSE for real-time updates.
