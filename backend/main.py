import os
from dotenv import load_dotenv

# Load environment variables before importing routers that initialize the LLM
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv() # Fallback for root .env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from .routers.ws import router as ws_router
from .routers.hitl import router as hitl_router
from .graph.builder import graph
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

import sys
import asyncio

# Fix Windows Psycopg event loop compatibility
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

@app.on_event("startup")
async def startup():
    from .models.database import init_db, DATABASE_URL
    from psycopg_pool import AsyncConnectionPool
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from .graph.builder import graph

    print("Initializing database connection...")
    try:
        await asyncio.wait_for(init_db(), timeout=3.0)
        print("Database tables initialized successfully.")

        # Set up LangGraph Postgres checkpointer
        psycopg_url = DATABASE_URL.replace("+asyncpg", "")
        app.state.pool = AsyncConnectionPool(
            conninfo=psycopg_url,
            max_size=20,
            kwargs={"autocommit": True},
            open=False
        )
        await asyncio.wait_for(app.state.pool.open(), timeout=3.0)
        saver = AsyncPostgresSaver(app.state.pool)
        await asyncio.wait_for(saver.setup(), timeout=3.0)
        graph.checkpointer = saver
        print("LangGraph Postgres checkpointer configured.")
    except Exception as e:
        print("Notice: Postgres database not available ({e}). Using in-memory state saver.")

    # Start NOAA background polling task
    from .services.noaa_poller import run_poller
    app.state.poller_task = asyncio.create_task(run_poller())
    print("NOAA maritime alert poller started.")


@app.on_event("shutdown")
async def shutdown():
    if hasattr(app.state, "pool"):
        await app.state.pool.close()
    if hasattr(app.state, "poller_task"):
        app.state.poller_task.cancel()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Marga Supply Chain Agent API is running.",
        "documentation": "http://localhost:8000/docs",
        "frontend_url": "http://localhost:3000",
        "dashboard_url": "http://localhost:8000/dashboard"
    }

@app.get("/dashboard", include_in_schema=False)
def serve_dashboard():
    dashboard_file = STATIC_DIR / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(str(dashboard_file))
    return {"message": "Dashboard HTML file not found."}

app.include_router(ws_router)
app.include_router(hitl_router)


@app.post("/trigger_disruption")
async def trigger_disruption(event_id: str = "EVT-9999"):
    # This acts as the entry point to start the LangGraph
    thread_id = f"{event_id}-{str(uuid.uuid4())}"
    config = {"configurable": {"thread_id": thread_id}}
    
    from .db import crud
    from .models.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await crud.save_thread(db, event_id, thread_id)
    
    initial_state = {
        "event_id": event_id,
        "raw_event": {
            "vessel_id": "V-559",
            "source": "NOAA",
            "route": "Suez",
            "description": "Sandstorm disrupting Suez Canal passage.",
        },
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


# ── NOAA Polling endpoints ──────────────────────────────────────────────────

@app.get("/events/polling/status", tags=["Events"])
def get_polling_status():
    """
    Returns the current status of the NOAA background poller:
    whether it's running, when it last polled, how many alerts have
    been triggered, and how many unique events have been seen.
    """
    from .services.noaa_poller import get_status
    return get_status()


@app.post("/events/simulate", tags=["Events"])
async def simulate_event(
    route: str = "Shanghai to Los Angeles",
    vessel_id: str = "Evergreen",
    description: str = "Simulated maritime disruption for testing.",
    event_type: str = "Gale Warning",
):
    """
    Manually simulate a maritime disruption event and trigger the
    LangGraph agent — useful for demos and frontend development without
    waiting for a real NOAA alert.
    """
    event_id = f"SIM-{str(uuid.uuid4())[:8].upper()}"
    thread_id = f"{event_id}-{str(uuid.uuid4())[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    from .db import crud
    from .models.database import AsyncSessionLocal
    try:
        async with AsyncSessionLocal() as db:
            await crud.save_thread(db, event_id, thread_id)
    except Exception:
        pass

    initial_state = {
        "event_id": event_id,
        "raw_event": {
            "vessel_id": vessel_id,
            "source": "SIMULATION",
            "route": route,
            "description": description,
            "event_type": event_type,
        },
    }

    async def run_graph_task():
        try:
            await graph.ainvoke(initial_state, config=config)
        except Exception as e:
            import traceback
            traceback.print_exc()

    asyncio.create_task(run_graph_task())
    return {
        "status": "started",
        "event_id": event_id,
        "thread_id": thread_id,
        "route": route,
        "vessel_id": vessel_id,
    }
