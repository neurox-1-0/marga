from typing import Any, Dict
from ..state import AgentState

async def execute_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes the approved reroute using the mock booking client.
    """
    from ...websockets.manager import broadcast_agent_thought
    
    decision = state.get("approval_decision")
    quote_id = state.get("chosen_quote_id")
    
    if decision == "approved" and quote_id:
        await broadcast_agent_thought(
            node="execute",
            thought=f"Executing reroute using quote {quote_id}. Contacting carrier...",
            confidence_score=0.99
        )
        
        # Here we would call the booking client.
        result = "Successfully booked reroute."
    else:
        await broadcast_agent_thought(
            node="execute",
            thought="Reroute rejected by human operator. No action taken.",
            confidence_score=1.0
        )
        result = "Reroute rejected or no quote selected. No action taken."
        
    return {"execution_result": result}
