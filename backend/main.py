from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.ws import router as ws_router
from .routers.hitl import router as hitl_router
from .graph.builder import graph
import uuid

app = FastAPI(title="Marga Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)
app.include_router(hitl_router)

@app.post("/trigger_disruption")
async def trigger_disruption(event_id: str = "EVT-9999"):
    # This acts as the entry point to start the LangGraph
    thread_id = event_id
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "event_id": event_id,
        "raw_event": {
            "vessel_id": "V-559",
            "source": "NOAA",
            "route": "Suez",
            "description": "Sandstorm"
        }
    }
    
    import asyncio
    asyncio.create_task(graph.ainvoke(initial_state, config=config))
    return {"status": "started", "thread_id": thread_id}
