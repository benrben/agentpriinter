"""Action routing system for handling user actions."""
from typing import Callable, Dict, Any
from fastapi import WebSocket
from .schemas.protocol import Message
from .schemas.actions import ActionPayload
from pydantic import ValidationError


class InvalidActionPayloadError(Exception):
    """Raised when a user.action payload fails ActionPayload validation."""

    def __init__(self, issues: list[dict[str, Any]]):
        super().__init__("Invalid action payload")
        self.issues = issues


class ActionRouter:
    """Routes user.action messages to registered handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}  # action_id -> handler
        self._target_handlers: Dict[str, Callable] = {}  # target_prefix -> handler
    
    def register_handler(self, action_id: str, handler: Callable) -> None:
        """Register a handler for a specific action_id.
        
        Args:
            action_id: The action identifier to handle
            handler: Async or sync callable that receives (message, websocket)
        """
        self._handlers[action_id] = handler
    
    def register_target_handler(self, target_prefix: str, handler: Callable) -> None:
        """Register a handler for actions with a specific target prefix.
        
        Args:
            target_prefix: The target prefix to match (e.g., "agent", "tool", "http")
            handler: Async or sync callable that receives (message, websocket)
        """
        self._target_handlers[target_prefix] = handler
    
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
            raise InvalidActionPayloadError(
                issues=[{"loc": ["payload"], "msg": "payload must be an object", "type": "type_error"}]
            )

        try:
            # Validate shape and enum values, but preserve original payload dict for handlers.
            ActionPayload.model_validate(payload)
        except ValidationError as e:
            issues = [
                {"loc": list(err.get("loc", ())), "msg": err.get("msg"), "type": err.get("type")}
                for err in e.errors()
            ]
            raise InvalidActionPayloadError(issues=issues) from e

        target = payload.get("target", "")
        action_id = payload.get("action_id")
        
        # Try target-based routing first (if target has prefix like "agent:", "tool:", "http:")
        handler = None
        if target and ":" in target:
            target_prefix = target.split(":")[0]
            handler = self._target_handlers.get(target_prefix)
        
        # Fallback to action_id-based routing
        if not handler:
            handler = self._handlers.get(action_id)
        
        if not handler:
            raise KeyError(f"No handler registered for action_id: {action_id} or target: {target}")
        
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
