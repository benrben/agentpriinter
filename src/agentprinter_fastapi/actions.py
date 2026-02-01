"""Action routing system for handling user actions."""
from typing import Callable, Dict, Any
from fastapi import WebSocket
from .schemas.protocol import Message


class ActionRouter:
    """Routes user.action messages to registered handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}
    
    def register_handler(self, action_id: str, handler: Callable) -> None:
        """Register a handler for a specific action_id.
        
        Args:
            action_id: The action identifier to handle
            handler: Async or sync callable that receives (message, websocket)
        """
        self._handlers[action_id] = handler
    
    async def handle_message(self, message: Message, websocket: WebSocket) -> None:
        """Handle an incoming action message by routing to registered handler.
        
        Args:
            message: The validated Message object
            websocket: The WebSocket connection
            
        Raises:
            KeyError: If action_id is not registered
        """
        if message.type != "user.action":
            return  # Ignore non-action messages
        
        payload = message.payload
        if not isinstance(payload, dict):
            return
        
        action_id = payload.get("action_id")
        if not action_id:
            return
        
        handler = self._handlers.get(action_id)
        if not handler:
            raise KeyError(f"No handler registered for action_id: {action_id}")
        
        # Call handler (supports both sync and async)
        import inspect
        if inspect.iscoroutinefunction(handler):
            await handler(message, websocket)
        else:
            handler(message, websocket)

    def action(self, action_id: str):
        """Decorator for registering an action handler.
        
        Example:
            @router.action("submit_form")
            async def handle_submit(message, websocket):
                ...
        """
        def decorator(func: Callable):
            self.register_handler(action_id, func)
            return func
        return decorator


# Default instance for easy import
action_router = ActionRouter()
