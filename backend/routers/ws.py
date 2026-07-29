from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websockets.manager import manager
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("WebSocket connection attempt received from %s", websocket.client)
    await manager.connect(websocket)
    logger.info("WebSocket connected successfully from %s", websocket.client)
    try:
        while True:
            # We don't expect the dashboard to send much, but keep connection open
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Dashboard WebSocket disconnected")
