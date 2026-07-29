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

@app.on_event("startup")
async def startup():
    from .models.database import init_db, DATABASE_URL
    from psycopg_pool import AsyncConnectionPool
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from .graph.builder import graph

    print("Initializing database tables...")
    try:
        await init_db()
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")

    # Set up LangGraph Postgres checkpointer
    print("Setting up LangGraph Postgres checkpointer...")
    try:
        # Create a connection pool for the checkpointer
        psycopg_url = DATABASE_URL.replace("+asyncpg", "")
        app.state.pool = AsyncConnectionPool(
            conninfo=psycopg_url,
            max_size=20,
            kwargs={"autocommit": True},
            open=False
        )
        await app.state.pool.open()
        
        # Checkpointer needs a running pool
        saver = AsyncPostgresSaver(app.state.pool)
        await saver.setup() # creates checkpoint tables if missing
        
        # Override the graph's default MemorySaver
        graph.checkpointer = saver
        print("LangGraph checkpointer set up successfully.")
    except Exception as e:
        print(f"Failed to initialize checkpointer: {e}")

@app.on_event("shutdown")
async def shutdown():
    if hasattr(app.state, "pool"):
        await app.state.pool.close()

@app.get("/dashboard", include_in_schema=False)
def serve_dashboard():
    return FileResponse(str(STATIC_DIR / "dashboard.html"))

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
