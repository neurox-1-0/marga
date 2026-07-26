from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    event_id: str
    raw_event: Dict[str, Any]
    matched_pos: List[str]
    exposure_value: float
    cost_analysis: Dict[str, Any]
    freight_quotes: List[Dict[str, Any]]
    
    # State tracking
    current_step: str
    messages: List[Any]
    
    # HITL Action
    approval_decision: Optional[str]
    chosen_quote_id: Optional[str]
    manager_note: Optional[str]
    
    # Final outcome
    execution_result: Optional[str]
