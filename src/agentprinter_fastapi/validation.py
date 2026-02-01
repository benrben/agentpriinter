"""Style allowlist and prop validation for safe UI rendering."""
from typing import Optional, Set, Any
from pydantic import BaseModel, Field
import logging
import re

logger = logging.getLogger(__name__)

# Allowlisted CSS properties safe for dynamic styling
SAFE_CSS_PROPERTIES = {
    # Colors
    "color", "background-color", "border-color", "text-color",
    # Layout
    "display", "width", "height", "padding", "margin", "gap",
    # Typography
    "font-size", "font-weight", "text-align", "line-height",
    # Borders & shadows
    "border", "border-radius", "box-shadow",
    # Visibility
    "opacity", "visibility", "pointer-events",
    # Transitions
    "transition", "transform",
}

# Blocklisted CSS properties (security risk)
BLOCKED_CSS_PROPERTIES = {
    "behavior",  # IE specific
    "binding",  # Mozilla specific
    "-moz-binding",
    "expression",  # IE expression
}

# Allowlisted CSS values (no eval, no url() without validation)
BLOCKED_CSS_VALUES = {
    r"javascript:",
    r"vbscript:",
    r"eval\(",
    r"expression\(",
}

class StyleValidator:
    """Validates inline styles against allowlist."""
    
    def __init__(self, allowed_properties: Optional[Set[str]] = None):
        """Initialize validator.
        
        Args:
            allowed_properties: Custom set of allowed CSS properties
        """
        self.allowed = allowed_properties or SAFE_CSS_PROPERTIES
    
    def is_property_allowed(self, prop: str) -> bool:
        """Check if CSS property is allowlisted."""
        prop_lower = prop.lower().strip()
        return prop_lower in self.allowed and prop_lower not in BLOCKED_CSS_PROPERTIES
    
    def is_value_safe(self, value: str) -> bool:
        """Check if CSS value contains unsafe patterns."""
        value_lower = value.lower()
        for blocked_pattern in BLOCKED_CSS_VALUES:
            if re.search(blocked_pattern, value_lower):
                return False
        return True
    
    def validate_style_dict(self, styles: dict[str, str]) -> dict[str, str]:
        """Validate a style dict, removing unsafe properties.
        
        Args:
            styles: Dict of CSS properties and values
            
        Returns:
            Cleaned style dict with only safe properties
        """
        cleaned = {}
        
        for prop, value in styles.items():
            if not self.is_property_allowed(prop):
                logger.warning(f"Blocked CSS property: {prop}")
                continue
            
            if not self.is_value_safe(value):
                logger.warning(f"Blocked CSS value for {prop}: {value}")
                continue
            
            cleaned[prop] = value
        
        return cleaned

class PropValidator:
    """Validates component props against schema."""
    
    @staticmethod
    def validate_type(value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        expected = type_map.get(expected_type)
        if expected is None:
            return True  # Unknown type, allow
        
        return isinstance(value, expected)
    
    @staticmethod
    def validate_props(props: dict[str, Any], schema: dict[str, str]) -> dict[str, Any]:
        """Validate props against schema.
        
        Args:
            props: Props dict to validate
            schema: Schema dict with type definitions
            
        Returns:
            Validated props with invalid values removed
        """
        validated = {}
        
        for prop_name, prop_value in props.items():
            expected_type = schema.get(prop_name)
            
            if expected_type is None:
                logger.warning(f"Unknown prop: {prop_name}")
                continue
            
            if not PropValidator.validate_type(prop_value, expected_type):
                logger.warning(f"Invalid type for {prop_name}: expected {expected_type}")
                continue
            
            validated[prop_name] = prop_value
        
        return validated

# Global instances
style_validator = StyleValidator()
prop_validator = PropValidator()
