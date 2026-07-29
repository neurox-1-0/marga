from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.domain import ApprovalCardDB, EventThreadDB
from backend.schemas.api import ApprovalCard
from typing import List, Optional

async def get_pending_cards(db: AsyncSession) -> List[ApprovalCard]:
    result = await db.execute(select(ApprovalCardDB).where(ApprovalCardDB.status == "pending"))
    db_cards = result.scalars().all()
    cards = []
    for db_card in db_cards:
        card = ApprovalCard(**db_card.card_data)
        card.status = db_card.status
        card.chosen_quote_id = db_card.chosen_quote_id
        cards.append(card)
    return cards

async def get_card(db: AsyncSession, event_id: str) -> Optional[ApprovalCard]:
    result = await db.execute(select(ApprovalCardDB).where(ApprovalCardDB.event_id == event_id))
    db_card = result.scalars().first()
    if not db_card:
        return None
    card = ApprovalCard(**db_card.card_data)
    card.status = db_card.status
    card.chosen_quote_id = db_card.chosen_quote_id
    return card

async def save_card(db: AsyncSession, card: ApprovalCard) -> None:
    event_id = card.event.event_id
    result = await db.execute(select(ApprovalCardDB).where(ApprovalCardDB.event_id == event_id))
    db_card = result.scalars().first()
    
    card_dict = card.model_dump()
    
    if db_card:
        db_card.status = card.status
        db_card.chosen_quote_id = card.chosen_quote_id
        db_card.card_data = card_dict
    else:
        db_card = ApprovalCardDB(
            event_id=event_id,
            status=card.status,
            chosen_quote_id=card.chosen_quote_id,
            card_data=card_dict
        )
        db.add(db_card)
    await db.commit()

async def update_card_status(db: AsyncSession, event_id: str, status: str, chosen_quote_id: Optional[str] = None) -> None:
    result = await db.execute(select(ApprovalCardDB).where(ApprovalCardDB.event_id == event_id))
    db_card = result.scalars().first()
    if db_card:
        db_card.status = status
        db_card.chosen_quote_id = chosen_quote_id
        card_data = dict(db_card.card_data)
        card_data["status"] = status
        card_data["chosen_quote_id"] = chosen_quote_id
        db_card.card_data = card_data
        await db.commit()

async def save_thread(db: AsyncSession, event_id: str, thread_id: str) -> None:
    result = await db.execute(select(EventThreadDB).where(EventThreadDB.event_id == event_id))
    db_thread = result.scalars().first()
    if db_thread:
        db_thread.thread_id = thread_id
    else:
        db_thread = EventThreadDB(event_id=event_id, thread_id=thread_id)
        db.add(db_thread)
    await db.commit()

async def get_thread_id(db: AsyncSession, event_id: str) -> Optional[str]:
    result = await db.execute(select(EventThreadDB).where(EventThreadDB.event_id == event_id))
    db_thread = result.scalars().first()
    if db_thread:
        return db_thread.thread_id
    return None
