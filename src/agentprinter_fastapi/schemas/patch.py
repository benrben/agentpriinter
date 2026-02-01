from pydantic import BaseModel
from typing import Literal, Any

class StatePatch(BaseModel):
    """An RFC 6902-style patch operation for state updates."""
    op: Literal["replace", "add", "remove"]
    path: str # e.g., "/user/name"
    value: Any = None
    # Monotonic version for ordering guarantees
    version: int
