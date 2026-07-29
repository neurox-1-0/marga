from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from .routers.ws import router as ws_router
from .routers.hitl import router as hitl_router
import uuid

app = FastAPI(title="Marga Backend API", description="LangGraph-powered supply chain disruption agent.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the HITL dashboard at /dashboard
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/dashboard", include_in_schema=False)
def serve_dashboard():
    return FileResponse(str(STATIC_DIR / "dashboard.html"))

app.include_router(ws_router)
app.include_router(hitl_router)


@app.post("/trigger_disruption")
async def trigger_disruption(event_id: str = "EVT-9999"):
    """
    Entry point: starts the LangGraph agentic loop for a demo disruption event.
    The graph will pause at hitl_gate — the dashboard will show the approval card.
    """
    from .graph.builder import graph
    import asyncio

    thread_id = event_id
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "event_id": event_id,
        "raw_event": {
            "vessel_id": "V-559",
            "source": "NOAA",
            "route": "Suez",
            "description": "Sandstorm disrupting Suez Canal passage.",
        },
    }

    asyncio.create_task(graph.ainvoke(initial_state, config=config))
    return {"status": "started", "thread_id": thread_id, "dashboard": "/dashboard"}
