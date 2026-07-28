import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from routers.ws import router
from websockets.manager import manager

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_websocket_connection():
    with client.websocket_connect("/ws/dashboard") as websocket:
        assert len(manager.active_connections) == 1
        
        # Test broadcast manually
        import asyncio
        async def mock_broadcast():
            await manager.broadcast({"type": "test", "data": "hello"})
            
        asyncio.run(mock_broadcast())
        
        data = websocket.receive_json()
        assert data == {"type": "test", "data": "hello"}

    assert len(manager.active_connections) == 0
