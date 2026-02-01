"""Runtime devtools panel for debugging and monitoring."""
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DevtoolsMessage:
    """Structured message for devtools."""
    
    def __init__(self, category: str, level: str, message: str, data: Optional[Dict] = None):
        self.timestamp = datetime.now().isoformat()
        self.category = category  # "message", "action", "error", "performance"
        self.level = level  # "debug", "info", "warn", "error"
        self.message = message
        self.data = data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "category": self.category,
            "level": self.level,
            "message": self.message,
            "data": self.data
        }

class DevtoolsPanel:
    """Runtime devtools for monitoring WebSocket traffic and state."""
    
    def __init__(self, max_history: int = 1000, enabled: bool = True):
        """Initialize devtools panel.
        
        Args:
            max_history: Max messages to keep in history
            enabled: Whether devtools is enabled
        """
        self.enabled = enabled
        self.max_history = max_history
        self.messages: List[DevtoolsMessage] = []
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "actions_processed": 0,
        }
    
    def log_message(self, direction: str, message_type: str, payload: Dict):
        """Log a message (sent or received).
        
        Args:
            direction: "send" or "receive"
            message_type: Type like "ui.render", "user.action"
            payload: Message payload
        """
        if not self.enabled:
            return
        
        level = "warn" if message_type == "protocol.error" else "info"
        msg = DevtoolsMessage(
            category="message",
            level=level,
            message=f"{direction.upper()}: {message_type}",
            data={"direction": direction, "type": message_type, "payload": payload}
        )
        
        self._add_message(msg)
        
        if direction == "send":
            self.stats["messages_sent"] += 1
        else:
            self.stats["messages_received"] += 1
    
    def log_action(self, action_id: str, status: str, details: Optional[Dict] = None):
        """Log action processing.
        
        Args:
            action_id: Action identifier
            status: "received", "processing", "completed", "failed"
            details: Additional details
        """
        if not self.enabled:
            return
        
        level = "error" if status == "failed" else "info"
        msg = DevtoolsMessage(
            category="action",
            level=level,
            message=f"Action {action_id}: {status}",
            data={"action_id": action_id, "status": status, **(details or {})}
        )
        
        self._add_message(msg)
        self.stats["actions_processed"] += 1
    
    def log_error(self, error_code: str, message: str, details: Optional[Dict] = None):
        """Log an error.
        
        Args:
            error_code: Error code
            message: Error message
            details: Error details
        """
        if not self.enabled:
            return
        
        msg = DevtoolsMessage(
            category="error",
            level="error",
            message=f"[{error_code}] {message}",
            data={"code": error_code, **(details or {})}
        )
        
        self._add_message(msg)
        self.stats["errors"] += 1
    
    def log_performance(self, operation: str, duration_ms: float, details: Optional[Dict] = None):
        """Log performance metric.
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            details: Additional details
        """
        if not self.enabled:
            return
        
        level = "warn" if duration_ms > 1000 else "info"
        msg = DevtoolsMessage(
            category="performance",
            level=level,
            message=f"{operation}: {duration_ms:.2f}ms",
            data={"operation": operation, "duration_ms": duration_ms, **(details or {})}
        )
        
        self._add_message(msg)
    
    def _add_message(self, msg: DevtoolsMessage):
        """Add message to history, maintaining size limit."""
        self.messages.append(msg)
        
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_messages(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get devtools messages.
        
        Args:
            category: Filter by category (optional)
            limit: Max messages to return
            
        Returns:
            List of message dicts
        """
        messages = self.messages
        
        if category:
            messages = [m for m in messages if m.category == category]
        
        # Return most recent
        return [m.to_dict() for m in messages[-limit:]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get devtools statistics."""
        return {
            **self.stats,
            "message_count": len(self.messages),
            "enabled": self.enabled
        }
    
    def clear(self):
        """Clear all devtools history."""
        self.messages = []
        self.stats = {k: 0 for k in self.stats}

# Global devtools instance
devtools = DevtoolsPanel(enabled=True)
