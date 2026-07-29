from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..graph.builder import graph
from ..schemas.api import ApprovalCard, ApprovalDecision
from ..models.database import get_db
from ..db import crud

router = APIRouter()

@router.get("/cards/pending", response_model=List[ApprovalCard])
async def list_pending_cards(db: AsyncSession = Depends(get_db)):
    return await crud.get_pending_cards(db)

@router.get("/cards/{event_id}", response_model=ApprovalCard)
async def get_card(event_id: str, db: AsyncSession = Depends(get_db)):
    card = await crud.get_card(db, event_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.post("/cards/{event_id}/decision")
async def record_decision(
    event_id: str,
    decision: ApprovalDecision,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    card = await crud.get_card(db, event_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Update state in DB
    await crud.update_card_status(db, event_id, decision.decision, decision.chosen_quote_id)

    # Resume the LangGraph using Command
    from langgraph.types import Command
    
    # In a real app we'd load the thread_id associated with the event
    thread_id = await crud.get_thread_id(db, event_id) or event_id
    config = {"configurable": {"thread_id": thread_id}}
    
    async def resume_graph():
        try:
            print(f"Resuming graph for thread_id {thread_id}...")
            await graph.ainvoke(
                Command(resume={
                    "decision": decision.decision,
                    "chosen_quote_id": decision.chosen_quote_id,
                    "manager_note": decision.manager_note
                }),
                config=config
            )
            print(f"Graph resumed and completed successfully for {thread_id}.")
        except Exception as e:
            print(f"CRITICAL ERROR IN GRAPH RESUMPTION: {e}")
            import traceback
            traceback.print_exc()
        
    background_tasks.add_task(resume_graph)

    return {"status": "recorded", "decision": decision.decision}
