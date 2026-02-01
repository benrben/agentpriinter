from pydantic import BaseModel, Field
from typing import Optional, Any

class ThemeTokens(BaseModel):
    """Design system tokens for consistent theming."""
    color_primary: Optional[str] = Field(default=None, description="Primary brand color")
    color_secondary: Optional[str] = Field(default=None, description="Secondary color")
    color_danger: Optional[str] = Field(default=None, description="Error/danger color")
    color_success: Optional[str] = Field(default=None, description="Success color")
    spacing_unit: int = Field(default=4, description="Base spacing unit in pixels")
    radius_default: int = Field(default=4, description="Default border radius in pixels")
    font_size_base: int = Field(default=14, description="Base font size in pixels")
    font_size_large: Optional[int] = Field(default=None, description="Large font size in pixels")

class ComponentStyle(BaseModel):
    """Style contract for UI components."""
    theme: Optional[ThemeTokens] = Field(default=None, description="Theme tokens")
    className: Optional[str] = Field(default=None, description="Utility class names (allowlisted)")
    variant: Optional[str] = Field(default=None, description="Component variant (e.g., primary, danger)")
    # Allowlisted inline style properties only
    inline_style: Optional[dict[str, str]] = Field(default=None, description="Limited inline CSS properties")

from typing import Literal, Union

class BindingOp(BaseModel):
    op: str

class BindingPath(BindingOp):
    op: Literal["path"] = "path"
    path: str

class BindingConcat(BindingOp):
    op: Literal["concat"] = "concat"
    parts: list[Union[str, "BindingExpression"]]  # recursive strings or exprs

class BindingFormat(BindingOp):
    op: Literal["format"] = "format"
    template: str  # e.g. "Hello {name}"
    args: dict[str, "BindingExpression"]

class BindingIf(BindingOp):
    op: Literal["if"] = "if"
    condition: "BindingExpression"
    then_val: "BindingExpression"
    else_val: "BindingExpression"

# Recursive union for expressions
# We allow primitives (str, int, float, bool) as valid expressions (leaves)
BindingExpression = Union[
    str, int, float, bool, 
    BindingPath, BindingConcat, BindingFormat, BindingIf
]

class Bindings(BaseModel):
    """Connects a prop key to a state path or computed expression."""
    prop: str # e.g., "value"
    # Legacy direct path support
    path: Optional[str] = None 
    # New computed expression support
    expr: Optional[BindingExpression] = None

class ComponentNode(BaseModel):
    """Recursive UI Node."""
    id: str
    type: str # e.g., "container", "button", "input"
    key: Optional[str] = None
    props: dict[str, Any] = Field(default_factory=dict)
    bindings: list[Bindings] = Field(default_factory=list)
    style: Optional[ComponentStyle] = Field(default=None, description="Component style contract")
    # The magic of recursion:
    children: list["ComponentNode"] = Field(default_factory=list)

class Page(BaseModel):
    path: str # e.g., "/settings"
    layout: str = "default"
    root: ComponentNode
