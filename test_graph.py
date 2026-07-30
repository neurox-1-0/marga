import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from backend.graph.builder import graph
import uuid

async def run():
    event_id = "EVT-9999"
    thread_id = f"{event_id}-{str(uuid.uuid4())}"
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
    
    print("Starting graph...")
    async for event in graph.astream(initial_state, config=config, stream_mode="values"):
        print(f"STATE EVENT: {list(event.keys())}")
        if 'current_step' in event:
            print(f"STEP: {event['current_step']}")

    print("Graph execution finished.")
    
    from backend.routers.hitl import cards_db
    print("CARDS DB:", cards_db)

if __name__ == "__main__":
    asyncio.run(run())
