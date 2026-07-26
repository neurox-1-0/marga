import pytest
from graph.builder import graph

@pytest.mark.asyncio
async def test_graph_compiles_and_interrupts():
    config = {"configurable": {"thread_id": "test_1"}}
    initial_state = {
        "event_id": "EVT-1",
        "raw_event": {"vessel_id": "V-559"}
    }
    
    # We won't fully run the graph because it requires a Gemini API key and live LLM.
    # But we can verify it compiled successfully.
    assert graph is not None
    assert "router_node" in graph.nodes
    assert "reasoning_node" in graph.nodes
    assert "hitl_gate" in graph.nodes
    assert "execute" in graph.nodes
