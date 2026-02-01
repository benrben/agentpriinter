from pydantic import BaseModel, Field
from typing import Any, Dict

class Tool(BaseModel):
    """Tool metadata contract for tool panels and invocations."""
    name: str = Field(..., description="Tool name (e.g., search, email)")
    description: str = Field(..., description="Human-readable tool description")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for tool inputs")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for tool outputs")
    ui_schema: Dict[str, Any] = Field(default_factory=dict, description="UI schema for form rendering (RJSF)")
    render_hints: Dict[str, Any] = Field(default_factory=dict, description="Display hints (e.g., panel layout)")

class SchemaContract(BaseModel):
    """Form/UI schema contract for dynamic form generation."""
    title: str = Field(..., description="Form title")
    json_schema: Dict[str, Any] = Field(..., description="JSON Schema for form fields")
    ui_schema: Dict[str, Any] = Field(default_factory=dict, description="UI schema for field rendering (RJSF)")
    render_hints: Dict[str, Any] = Field(default_factory=dict, description="Display hints (e.g., layout, validation)")
