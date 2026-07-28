from typing import Any, Dict
from ..state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from ...tools.erp import query_erp
from ...tools.freight import get_freight_quotes
from ...tools.cost_engine import calculate_stockout_cost
import json

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
tools = [query_erp, get_freight_quotes, calculate_stockout_cost]
llm_with_tools = llm.bind_tools(tools)

async def reasoning_node(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates the current state, uses tools to gather missing information (ERP, Freight, Cost),
    and updates the state. 
    Outputs a transparent reasoning trace to the frontend.
    """
    
    # Broadcast that we're starting reasoning
    from ...websockets.manager import broadcast_agent_thought
    await broadcast_agent_thought(
        node="reasoning_node",
        thought="Analyzing disruption event and determining required actions...",
        confidence_score=0.9
    )
    
    # Check what is missing in the state and call tools appropriately
    updates = {}
    
    if not state.get("matched_pos"):
        # We need to query ERP
        result = query_erp.invoke({"vessel_id": state["raw_event"].get("vessel_id")})
        updates["matched_pos"] = result.get("matched_pos", [])
        updates["exposure_value"] = result.get("total_inventory_value_usd", 0.0)
        
        await broadcast_agent_thought(
            node="reasoning_node",
            thought=f"Queried ERP. Found {len(updates['matched_pos'])} impacted POs.",
            confidence_score=0.95,
            tool_calls=[{"tool_name": "query_erp", "rationale": "Checking for impacted inventory."}]
        )
        
    elif not state.get("freight_quotes"):
        # We need to get freight quotes
        quotes = get_freight_quotes.invoke({"origin": "Shanghai", "destination": "Los Angeles"})
        updates["freight_quotes"] = quotes
        
        await broadcast_agent_thought(
            node="reasoning_node",
            thought=f"Obtained {len(quotes)} alternative freight quotes.",
            confidence_score=0.92,
            tool_calls=[{"tool_name": "get_freight_quotes", "rationale": "Finding rerouting options."}]
        )
        
    elif not state.get("cost_analysis"):
        # We need to run the cost engine
        delay_days = 10 # Hardcoded for demo based on Suez blockage
        cost_res = calculate_stockout_cost.invoke({
            "inventory_value": state.get("exposure_value", 0.0),
            "delay_days": delay_days
        })
        
        # Calculate reroute savings
        quotes = state.get("freight_quotes", [])
        best_quote = min(quotes, key=lambda q: q["cost_usd"]) if quotes else None
        
        cost_analysis = {
            "stockout_cost_usd": cost_res["stockout_cost_usd"],
            "reroute_savings_usd": cost_res["stockout_cost_usd"] - (best_quote["cost_usd"] if best_quote else 0),
            "recommendation": cost_res["recommendation"],
            "best_reroute_option": {"quote_id": best_quote["quote_id"]} if best_quote else None
        }
        
        updates["cost_analysis"] = cost_analysis
        
        await broadcast_agent_thought(
            node="reasoning_node",
            thought="Calculated stockout risks and projected savings.",
            confidence_score=0.88,
            tool_calls=[{"tool_name": "calculate_stockout_cost", "rationale": "Evaluating financial impact."}]
        )
        
    return updates
