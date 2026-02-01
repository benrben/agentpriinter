from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

class ErrorPayload(BaseModel):
    """Structured error response for protocol.error messages."""
    code: str = Field(..., description="Error code (e.g., AUTH_FAILED, NOT_FOUND)")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional error context")

class Navigation(BaseModel):
    """Navigation routing contract for frontend navigation events."""
    to: str = Field(..., description="Target route (e.g., /dashboard, /settings)")
    params: dict[str, Any] = Field(default_factory=dict, description="Route parameters")
    replace: bool = Field(default=False, description="Replace current history entry instead of push")
    open: str = Field(default="same", description="Open in same window/tab or new")

class MessageHeader(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str = Field(..., description="Distributed tracing ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
    app_id: str | None = Field(default=None, description="Application identity")
    session_id: str | None = Field(default=None, description="Session identity")
    workspace_id: str | None = Field(default=None, description="Workspace identity for multi-tenancy")
    user_id: str | None = Field(default=None, description="User identity")

class Message(BaseModel):
    """The universal envelope for all WebSocket communication."""
    type: str # e.g., "ui.render", "agent.event", "rpc.request"
    header: MessageHeader
    payload: dict[str, Any]
