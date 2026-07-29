from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
from ..graph.builder import graph
from ..schemas.api import ApprovalCard, ApprovalDecision
from ..storage import cards_db
import uuid

router = APIRouter()

@router.get("/cards/pending", response_model=List[ApprovalCard])
def list_pending_cards():
    return [card for card in cards_db.values() if card.status == "pending"]

@router.post("/cards/{event_id}/decision")
async def record_decision(event_id: str, decision: ApprovalDecision, background_tasks: BackgroundTasks):
    if event_id not in cards_db:
        # Mock finding the card
        pass

    # Update state
    if event_id in cards_db:
        cards_db[event_id].status = decision.decision
        cards_db[event_id].chosen_quote_id = decision.chosen_quote_id

    # Resume the LangGraph using Command
    from langgraph.types import Command
    
    # In a real app we'd load the thread_id associated with the event
    thread_id = event_id
    config = {"configurable": {"thread_id": thread_id}}
    
    def resume_graph():
        graph.invoke(
            Command(resume={"decision": decision.decision, "chosen_quote_id": decision.chosen_quote_id, "manager_note": decision.manager_note}),
            config=config
        )
        
    background_tasks.add_task(resume_graph)

    return {"status": "recorded", "decision": decision.decision}
