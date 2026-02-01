from pydantic import BaseModel, Field
from typing import Optional, Any

class Bindings(BaseModel):
    """Connects a prop key to a state path."""
    prop: str # e.g., "value"
    path: str # e.g., "user.name" (dot notation)

class ComponentNode(BaseModel):
    """Recursive UI Node."""
    id: str
    type: str # e.g., "container", "button", "input"
    key: Optional[str] = None
    props: dict[str, Any] = Field(default_factory=dict)
    bindings: list[Bindings] = Field(default_factory=list)
    # The magic of recursion:
    children: list["ComponentNode"] = Field(default_factory=list)

class Page(BaseModel):
    path: str # e.g., "/settings"
    layout: str = "default"
    root: ComponentNode
