from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class EventSchema(BaseModel):
    event_id: str
    detected_at: datetime
    source: str
    vessel_id: str
    route: str
    description: str

class ExposureSchema(BaseModel):
    matched_pos: List[str]
    total_inventory_value_usd: float

class FreightQuoteSchema(BaseModel):
    quote_id: str
    carrier: str
    mode: str
    cost_usd: float
    transit_days: int

class BestQuoteRef(BaseModel):
    quote_id: str

class CostAnalysisSchema(BaseModel):
    stockout_cost_usd: float
    reroute_savings_usd: float
    recommendation: str
    best_reroute_option: Optional[BestQuoteRef] = None

class FreightOptionsSchema(BaseModel):
    quotes: List[FreightQuoteSchema] = Field(default_factory=list)

class ApprovalCard(BaseModel):
    event: EventSchema
    exposure: ExposureSchema
    cost_analysis: CostAnalysisSchema
    freight_options: FreightOptionsSchema
    status: str = "pending"
    chosen_quote_id: Optional[str] = None

class ApprovalDecision(BaseModel):
    event_id: str
    decision: str
    chosen_quote_id: Optional[str] = None
    manager_note: Optional[str] = None

# WebSocket Schemas
class AgentThoughtData(BaseModel):
    node: str
    thought: str
    confidence_score: float
    tool_calls: List[dict] = Field(default_factory=list)

class AgentThoughtEvent(BaseModel):
    type: str = "agent_thought"
    data: AgentThoughtData

class StateUpdateData(BaseModel):
    current_node: str
    tracking_id: str
    state_summary: str

class StateUpdateEvent(BaseModel):
    type: str = "state_update"
    data: StateUpdateData
