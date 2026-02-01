from fastapi import WebSocket
from typing import List, Any
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any] | Any):
        """Broadcast a message (dict or Pydantic model) to all connected clients."""
        payload = message
        if hasattr(message, "model_dump"):
            payload = message.model_dump(mode='json')
        elif hasattr(message, "dict"): # pydantic v1 fallback
            payload = message.dict()
            
        # Snapshot list to avoid modification during iteration issues
        for connection in list(self.active_connections):
            try:
                await connection.send_json(payload)
            except Exception as e:
                logger.warning(f"Error broadcasting to client, removing: {e}")
                self.disconnect(connection)
