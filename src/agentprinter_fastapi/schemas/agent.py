from pydantic import BaseModel
from typing import Literal, Any

class AgentEvent(BaseModel):
    """A single event from the agent's lifecycle."""
    run_id: str
    event: Literal["start", "token", "tool_call", "tool_result", "finish", "error"]
    data: Any # String token, or dict tool call details
