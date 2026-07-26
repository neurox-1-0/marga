from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Integer
from pgvector.sqlalchemy import Vector
from .database import Base
from datetime import datetime

class DisruptionEventDB(Base):
    __tablename__ = "disruption_events"

    id = Column(String, primary_key=True, index=True) # e.g. EVT-1234
    detected_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
    vessel_id = Column(String)
    route = Column(String)
    description = Column(Text)
    
    # Store history for memory/observability
    resolution_status = Column(String, default="pending")
    resolution_details = Column(JSON, nullable=True)
    
    # pgvector embedding of the disruption context
    embedding = Column(Vector(1536), nullable=True)
