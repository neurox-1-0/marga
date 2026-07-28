import os
from dotenv import load_dotenv

# Load environment variables before importing routers that initialize the LLM
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv() # Fallback for root .env

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
    thread_id = f"{event_id}-{str(uuid.uuid4())}"
    config = {"configurable": {"thread_id": thread_id}}
    
    from .routers.hitl import thread_db
    thread_db[event_id] = thread_id
    
    initial_state = {
        "event_id": event_id,
        "raw_event": {
            "vessel_id": "V-559",
            "source": "NOAA",
            "route": "Suez",
            "description": "Sandstorm"
        }
    }
    
    async def run_graph_task():
        try:
            print(f"Starting graph for {event_id}...")
            await graph.ainvoke(initial_state, config=config)
            print(f"Graph completed successfully for {event_id}.")
        except Exception as e:
            print(f"CRITICAL ERROR IN GRAPH EXECUTION: {e}")
            import traceback
            traceback.print_exc()

    import asyncio
    asyncio.create_task(run_graph_task())
    return {"status": "started", "thread_id": thread_id}
