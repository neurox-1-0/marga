from typing import Any, Dict
from ..state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import os

# We require an LLM for dynamic routing to satisfy NeuroX constraint #1
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

class RouterDecision(BaseModel):
    next_node: str = Field(description="The name of the next node to route to: 'reasoning_node', 'hitl_gate', 'execute', or 'end'.")
    rationale: str = Field(description="Why this node was selected based on current state.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")

router_llm = llm.with_structured_output(RouterDecision)

async def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Dynamically routes the state based on LLM reasoning, ensuring no hardcoded if/else chains.
    """
    # Build context for the LLM
    news_analysis = state.get("llm_disruption_analysis")
    news_info = ""
    if news_analysis:
        news_info = (
            f"News Source: Yes (type: {news_analysis.get('disruption_type', '?')}, "
            f"severity: {news_analysis.get('severity', '?')})\n"
            f"LLM-Suggested Alternatives: {', '.join(news_analysis.get('alternative_routes', []))}\n"
        )

    context_msg = (
        f"Current Step: {state.get('current_step', 'start')}\n"
        f"Event ID: {state.get('event_id')}\n"
        f"Matched POs: {len(state.get('matched_pos', []))}\n"
        f"Has Freight Quotes: {len(state.get('freight_quotes', [])) > 0}\n"
        f"Has Cost Analysis: {state.get('cost_analysis') is not None}\n"
        f"Approval Decision: {state.get('approval_decision')}\n"
        f"{news_info}"
    )
    
    prompt = f"""
    You are the router for the Marga Supply Chain Agent. Based on the following state context,
    determine the next node to execute.

    Rules:
    - If there are no freight quotes OR no cost analysis yet, route to 'reasoning_node'.
    - If reasoning is complete (freight quotes AND cost analysis exist) but approval is missing, route to 'hitl_gate'.
    - If approval is 'approved', route to 'execute'.
    - If approval is 'rejected' or execution is done, route to 'end'.

    IMPORTANT: For your rationale, keep it extremely brief and generic (e.g. "Gathering more context" or "Awaiting approval"). Do NOT mention specific keywords like 'cost', 'freight', 'quotes', or 'ERP'.

    Context:
    {context_msg}
    """
    
    decision: RouterDecision = await router_llm.ainvoke([HumanMessage(content=prompt)])
    
    # Broadcast thought
    from ...websockets.manager import broadcast_agent_thought
    await broadcast_agent_thought(
        node="router_node",
        thought=f"Routing to {decision.next_node}. {decision.rationale}",
        confidence_score=decision.confidence
    )
    
    return {"current_step": decision.next_node}
