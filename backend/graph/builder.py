from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes.router import router_node
from .nodes.reasoning import reasoning_node
from .nodes.hitl_gate import hitl_gate_node
from .nodes.execute import execute_node
from langgraph.checkpoint.memory import MemorySaver

def route_next(state: AgentState) -> str:
    # Router node output determines the next step
    return state.get("current_step", END)

def build_graph():
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("router_node", router_node)
    builder.add_node("reasoning_node", reasoning_node)
    builder.add_node("hitl_gate", hitl_gate_node)
    builder.add_node("execute", execute_node)
    
    # Entry point is the router
    builder.set_entry_point("router_node")
    
    # Conditional edges from the router
    builder.add_conditional_edges(
        "router_node",
        route_next,
        {
            "reasoning_node": "reasoning_node",
            "hitl_gate": "hitl_gate",
            "execute": "execute",
            "end": END
        }
    )
    
    # Other nodes always loop back to the router to reassess state
    builder.add_edge("reasoning_node", "router_node")
    builder.add_edge("hitl_gate", "router_node")
    builder.add_edge("execute", "router_node")
    
    # For now using MemorySaver, but will swap to PostgresSaver in production
    memory = MemorySaver()
    
    return builder.compile(checkpointer=memory)

graph = build_graph()
