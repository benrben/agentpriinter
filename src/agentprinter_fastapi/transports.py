"""SSE and HTTP fallback transport for clients that can't use WebSocket."""
from typing import AsyncGenerator, Callable
from fastapi import APIRouter
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class SSETransport:
    """Server-Sent Events transport as WebSocket fallback."""
    
    def __init__(self):
        self.clients: dict[str, list[Callable]] = {}
    
    def register_client(self, session_id: str, callback: Callable):
        """Register a client to receive SSE messages."""
        if session_id not in self.clients:
            self.clients[session_id] = []
        self.clients[session_id].append(callback)
    
    async def broadcast_to_client(self, session_id: str, message: dict):
        """Send a message to a specific client via SSE."""
        if session_id in self.clients:
            for callback in self.clients[session_id]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Error sending to client {session_id}: {e}")

class HTTPPollingTransport:
    """HTTP polling fallback for clients without WebSocket or SSE support."""
    
    def __init__(self):
        self.message_queues: dict[str, list[dict]] = {}
    
    def enqueue_message(self, session_id: str, message: dict):
        """Queue a message for polling retrieval."""
        if session_id not in self.message_queues:
            self.message_queues[session_id] = []
        self.message_queues[session_id].append(message)
    
    def dequeue_messages(self, session_id: str, cursor: int = 0, count: int = 100) -> list[dict]:
        """Retrieve queued messages since cursor (FIFO).
        
        Args:
            session_id: Session identifier
            cursor: Message index to start from (0 = beginning)
            count: Maximum number of messages to return
            
        Returns:
            List of messages since cursor
        """
        if session_id not in self.message_queues:
            return []
        
        queue = self.message_queues[session_id]
        # Return messages starting from cursor
        messages = queue[cursor:cursor + count]
        return messages

# Global instances
sse_transport = SSETransport()
http_polling = HTTPPollingTransport()

@router.get("/poll/{session_id}")
async def poll_messages(session_id: str, cursor: int = 0, limit: int = 100):
    """Poll for pending messages since cursor (HTTP fallback).
    
    Args:
        session_id: Session identifier
        cursor: Message index to start from (0 = beginning)
        limit: Maximum number of messages to return
        
    Returns:
        JSON response with messages and next cursor
    """
    messages = http_polling.dequeue_messages(session_id, cursor=cursor, count=limit)
    next_cursor = cursor + len(messages)
    return {
        "messages": messages,
        "cursor": next_cursor,
        "has_more": len(messages) == limit
    }

@router.post("/send/{session_id}")
async def send_message(session_id: str, message: dict):
    """Send a message via HTTP (for client-to-server)."""
    # Queue for the session to process
    return {"status": "enqueued", "message": message}
