"""Component bank and registration API for reusable UI components."""
from typing import Optional, Callable, Any
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class ComponentDefinition(BaseModel):
    """Definition of a reusable UI component."""
    name: str = Field(..., description="Component name (e.g., card, button-group)")
    version: str = Field(default="1.0.0", description="Component version")
    description: Optional[str] = Field(default=None, description="What this component does")
    props_schema: dict[str, Any] = Field(default_factory=dict, description="JSON Schema for props")
    slots: list[str] = Field(default_factory=list, description="Named slots (e.g., header, body)")
    defaults: dict[str, Any] = Field(default_factory=dict, description="Default prop values")

class ComponentBank:
    """Registry of reusable components."""
    
    def __init__(self):
        self._components: dict[str, ComponentDefinition] = {}
        self._factories: dict[str, Callable] = {}
    
    def register(
        self,
        name: str,
        definition: ComponentDefinition,
        factory: Optional[Callable] = None
    ):
        """Register a component.
        
        Args:
            name: Component identifier
            definition: Component metadata
            factory: Optional factory function to create instances
        """
        self._components[name] = definition
        if factory:
            self._factories[name] = factory
        logger.info(f"Registered component: {name}")
    
    def get(self, name: str) -> Optional[ComponentDefinition]:
        """Get component definition by name."""
        return self._components.get(name)
    
    def list_components(self) -> list[ComponentDefinition]:
        """List all registered components."""
        return list(self._components.values())
    
    def create(self, name: str, **props) -> Any:
        """Create a component instance using registered factory.
        
        Args:
            name: Component name
            **props: Component props
            
        Returns:
            Component instance
        """
        if name not in self._factories:
            raise ValueError(f"No factory for component: {name}")
        
        factory = self._factories[name]
        return factory(**props)
    
    def export_schema(self) -> dict[str, Any]:
        """Export component bank as JSON schema for frontend code generation."""
        return {
            "components": {
                name: comp.model_dump()
                for name, comp in self._components.items()
            },
            "version": "1.0.0"
        }

# Global registry
component_bank = ComponentBank()

# Decorator for easy registration
def register_component(name: str, **metadata):
    """Decorator to register a component factory."""
    def decorator(factory: Callable):
        definition = ComponentDefinition(
            name=name,
            **metadata
        )
        component_bank.register(name, definition, factory)
        return factory
    return decorator

# Example: Pre-registered common components
_common_components = [
    ComponentDefinition(
        name="card",
        description="Reusable card component",
        props_schema={"title": "string", "body": "string", "footer": "string"},
        slots=["header", "body", "footer"],
        defaults={"title": "Untitled"}
    ),
    ComponentDefinition(
        name="button-group",
        description="Group of buttons with consistent styling",
        props_schema={"buttons": "array", "orientation": "string"},
        defaults={"orientation": "horizontal"}
    ),
    ComponentDefinition(
        name="form-field",
        description="Labeled form input with validation",
        props_schema={"label": "string", "type": "string", "required": "boolean"},
        defaults={"required": False}
    ),
]

for comp in _common_components:
    component_bank.register(comp.name, comp)
