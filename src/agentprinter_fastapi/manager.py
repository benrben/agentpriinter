from fastapi import WebSocket
from typing import List, Any, Dict
import logging
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self, patch_coalesce_window: float = 0.05):
        self.active_connections: List[WebSocket] = []
        self.patch_coalesce_window = patch_coalesce_window  # 50ms default
        self.pending_patches: Dict[str, List[Dict]] = defaultdict(list)
        self.patch_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def _flush_patches(self, session_id: str):
        """Flush coalesced patches for a session."""
        try:
            await asyncio.sleep(self.patch_coalesce_window)
            # Check again after sleep - patches might have been cleared by a newer task
            if session_id in self.pending_patches and self.pending_patches[session_id]:
                patches = self.pending_patches[session_id]
                self.pending_patches[session_id] = []
                
                # If multiple patches, combine them into a single message
                if len(patches) > 1:
                    # Combine patches - take the latest version and merge operations
                    combined_patch = patches[-1].copy()  # Use latest patch as base
                    # Merge all patch operations
                    combined_ops = [p.get("payload", {}) for p in patches]
                    combined_patch["payload"] = {"patches": combined_ops}
                else:
                    combined_patch = patches[0]
                
                # Send the coalesced patch
                await self._send_message(combined_patch)
        except asyncio.CancelledError:
            # If cancelled, don't flush - let the new task handle it
            # Just clean up this task reference
            pass
        finally:
            # Clean up task only if this is still the current task
            if session_id in self.patch_tasks and self.patch_tasks[session_id] == asyncio.current_task():
                del self.patch_tasks[session_id]
    
    async def _send_message(self, payload: Dict):
        """Send a message to all connections and fallback transports."""
        
        # Extract session_id
        session_id = None
        if isinstance(payload, dict) and "header" in payload:
            header = payload.get("header", {})
            if isinstance(header, dict):
                session_id = header.get("session_id") or "default"
        
        # 1. Enqueue to polling transport (Source of Truth for History)
        # We do this FIRST to assign the sequence number
        if session_id:
            try:
                from .transports import http_polling
                # Get current queue length to determine next seq
                queue_len = len(http_polling.message_queues.get(session_id, []))
                next_seq = queue_len + 1
                
                # Stamp sequence number if missing
                if "header" in payload and isinstance(payload["header"], dict):
                     # Only assign if not present or None
                     if payload["header"].get("seq") is None:
                        payload["header"]["seq"] = next_seq
                
                http_polling.enqueue_message(session_id, payload)
            except ImportError:
                pass  # Transports module not available

        # 2. Broadcast to WebSockets
        # Snapshot list to avoid modification during iteration issues
        for connection in list(self.active_connections):
            try:
                await connection.send_json(payload)
            except Exception as e:
                logger.warning(f"Error broadcasting to client, removing: {e}")
                self.disconnect(connection)
        
        # 3. Fan out to SSE
        if session_id:
            try:
                from .transports import sse_transport
                await sse_transport.broadcast_to_client(session_id, payload)
            except ImportError:
                pass
    
    async def broadcast(self, message: dict[str, Any] | Any):
        """Broadcast a message (dict or Pydantic model) to all connected clients."""
        payload = message
        if hasattr(message, "model_dump"):
            payload = message.model_dump(mode='json')
        elif hasattr(message, "dict"): # pydantic v1 fallback
            payload = message.dict()
        
        # Check if this is a patch message that should be coalesced
        message_type = payload.get("type") if isinstance(payload, dict) else None
        
        # Ensure header exists
        if "header" not in payload:
            payload["header"] = {}
            
        header = payload.get("header", {})
        if isinstance(header, dict):
             session_id = header.get("session_id") or "default"
        else:
             session_id = "default"
        
        # Coalesce ui.patch and state.patch messages
        if message_type in ("ui.patch", "state.patch") and session_id:
            self.pending_patches[session_id].append(payload)
            
            # Cancel existing flush task and create new one
            if session_id in self.patch_tasks:
                old_task = self.patch_tasks[session_id]
                old_task.cancel()
                # Don't wait - let cancellation happen in background
            
            # Create new flush task
            self.patch_tasks[session_id] = asyncio.create_task(self._flush_patches(session_id))
        else:
            # Send immediately for non-patch messages
            await self._send_message(payload)
