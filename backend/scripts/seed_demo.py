import asyncio
import httpx

async def seed():
    print("Seeding Marga backend for Live Demo...")
    
    # In a real app we'd insert into Postgres here.
    # For now, we trigger the endpoint.
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("http://localhost:8004/trigger_disruption?event_id=EVT-DEMO-001")
            print("Response:", resp.json())
        except Exception as e:
            print("Failed to trigger demo:", e)

if __name__ == "__main__":
    asyncio.run(seed())
