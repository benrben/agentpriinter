from pydantic import BaseModel, Field
from typing import Literal

class ActionPayload(BaseModel):
    """What to do when an event fires."""
    action_id: str
    trigger: Literal["click", "submit", "change", "mount"]
    target: str # e.g., "agent:run_analysis" or "nav:/home"
    mode: Literal["stream", "http"] = "stream"
    # Mapping form data/state to action arguments
    payload_mapping: dict[str, str] = Field(default_factory=dict)
