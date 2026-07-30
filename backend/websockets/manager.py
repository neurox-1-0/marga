from typing import Dict, Any
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass # Optionally handle disconnected sockets

manager = ConnectionManager()

async def broadcast_graph_update(tracking_id: str, current_node: str, state_summary: str):
    await manager.broadcast({
        "type": "state_update",
        "data": {
            "current_node": current_node,
            "tracking_id": tracking_id,
            "state_summary": state_summary
        }
    })

async def broadcast_agent_thought(node: str, thought: str, confidence_score: float, tool_calls: list = None):
    await manager.broadcast({
        "type": "agent_thought",
        "data": {
            "node": node,
            "thought": thought,
            "confidence_score": confidence_score,
            "tool_calls": tool_calls or []
        }
    })

async def broadcast_api_call(service: str, endpoint: str, request_payload: dict, response_payload: dict, status: int = 200):
    await manager.broadcast({
        "type": "api_call",
        "data": {
            "service": service,
            "endpoint": endpoint,
            "request": request_payload,
            "response": response_payload,
            "status": status
        }
    })
