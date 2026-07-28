from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websockets.manager import manager
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    print("WebSocket connection attempt received!")
    await manager.connect(websocket)
    print("WebSocket connected successfully!")
    try:
        while True:
            # We don't expect the dashboard to send much, but keep connection open
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Dashboard WebSocket disconnected")
