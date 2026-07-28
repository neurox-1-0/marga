from typing import Any, Dict
from ..state import AgentState
from langgraph.types import interrupt

def hitl_gate_node(state: AgentState) -> Dict[str, Any]:
    """
    Halts execution and waits for human approval from the dashboard.
    """
    
    # Generate the ApprovalCard data structure (this would be fetched by the dashboard)
    # The dashboard polls /cards/pending which would look at the DB or memory.
    
    # We use LangGraph's interrupt to pause the graph.
    decision_payload = interrupt("Waiting for human approval via dashboard.")
    
    # When resumed, decision_payload will contain the chosen action
    return {
        "approval_decision": decision_payload.get("decision"),
        "chosen_quote_id": decision_payload.get("chosen_quote_id"),
        "manager_note": decision_payload.get("manager_note")
    }
