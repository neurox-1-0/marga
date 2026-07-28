import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy import select
from ..models.domain import DisruptionEventDB
from ..models.database import AsyncSessionLocal

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

async def embed_and_store_resolution(event_id: str, resolution_details: dict):
    """
    Called after a disruption is resolved to embed the context and outcome
    for future reference by the agent.
    """
    text_to_embed = json.dumps(resolution_details)
    vector = await embeddings.aembed_query(text_to_embed)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(DisruptionEventDB).where(DisruptionEventDB.id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if event:
            event.resolution_status = "resolved"
            event.resolution_details = resolution_details
            event.embedding = vector
            await session.commit()
            
async def search_similar_disruptions(query: str, limit: int = 3):
    """
    Used by the reasoning node to find historical context.
    """
    query_embedding = await embeddings.aembed_query(query)
    
    async with AsyncSessionLocal() as session:
        # pgvector L2 distance operator is <->
        stmt = select(DisruptionEventDB).order_by(
            DisruptionEventDB.embedding.l2_distance(query_embedding)
        ).limit(limit)
        
        results = await session.execute(stmt)
        return results.scalars().all()
