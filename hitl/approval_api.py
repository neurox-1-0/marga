from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from shared.schemas import ApprovalCard, ApprovalDecision

app = FastAPI(title="Approval API")

# Allow CORS for dashboard.html running locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for the prototype
cards_db: Dict[str, ApprovalCard] = {}
decisions_db: Dict[str, ApprovalDecision] = {}

@app.post("/cards")
def create_card(card: ApprovalCard):
    event_id = card.event.event_id
    cards_db[event_id] = card
    return {"status": "created", "event_id": event_id}

@app.get("/cards/pending", response_model=List[ApprovalCard])
def list_pending_cards():
    return [card for card in cards_db.values() if card.status == "pending"]

@app.get("/cards/{event_id}", response_model=ApprovalCard)
def get_card(event_id: str):
    if event_id not in cards_db:
        raise HTTPException(status_code=404, detail="Card not found")
    return cards_db[event_id]

@app.post("/cards/{event_id}/decision")
def record_decision(event_id: str, decision: ApprovalDecision):
    if event_id not in cards_db:
        raise HTTPException(status_code=404, detail="Card not found")
    
    if decision.event_id != event_id:
        raise HTTPException(status_code=400, detail="Mismatched event ID")

    card = cards_db[event_id]
    if card.status != "pending":
        raise HTTPException(status_code=400, detail="Card is already processed")
        
    card.status = decision.decision
    card.chosen_quote_id = decision.chosen_quote_id
    
    decisions_db[event_id] = decision
    return {"status": "recorded", "decision": decision.decision}

@app.get("/decisions/{event_id}", response_model=ApprovalDecision)
def get_decision(event_id: str):
    if event_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decisions_db[event_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
