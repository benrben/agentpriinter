"""UI template loader for loading and validating Page templates."""
import json
from pathlib import Path
from typing import Callable, Optional, Union
from .schemas import Page, ComponentNode

def load_template(template_path: Path | str) -> Page:
    """Load a JSON template file and return a validated Page object.
    
    Args:
        template_path: Path to the JSON template file
        
    Returns:
        Validated Page object
        
    Raises:
        FileNotFoundError: If template file does not exist
        ValueError: If template is invalid JSON
    """
    path = Path(template_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    
    with open(path, "r") as f:
        template_data = json.load(f)
    
    # Validate and return as Page
    page = Page.model_validate(template_data)
    return page

def load_templates_from_dir(template_dir: Path | str) -> dict[str, Page]:
    """Load all JSON templates from a directory.
    
    Args:
        template_dir: Directory containing JSON template files
        
    Returns:
        Dict mapping template name (without .json) to Page objects
    """
    dir_path = Path(template_dir)
    templates = {}
    
    for template_file in dir_path.glob("*.json"):
        try:
            page = load_template(template_file)
            template_name = template_file.stem
            templates[template_name] = page
        except Exception as e:
            # Skip invalid templates, log warning
            import logging
            logging.warning(f"Failed to load template {template_file}: {e}")
    
    return templates


class PageBuilder:
    """Builder API for programmatically creating Page objects."""
    
    def __init__(self, path: str, layout: str = "default"):
        """Initialize a PageBuilder.
        
        Args:
            path: Page path (e.g., "/dashboard")
            layout: Layout name (default: "default")
        """
        self.path = path
        self.layout = layout
        self._components: dict[str, dict] = {}  # Store component data as dicts
        self._children: dict[str, list[Union[str, ComponentNode]]] = {}  # Store child relationships
        self._root_id: Optional[str] = None
    
    def add_component(
        self,
        id: str,
        type: str,
        props: Optional[dict] = None,
        children: Optional[list[Union[str, ComponentNode]]] = None,
        parent: Optional[str] = None
    ) -> "PageBuilder":
        """Add a component to the page.
        
        Args:
            id: Component identifier
            type: Component type (e.g., "container", "button")
            props: Component properties
            children: List of child component IDs or ComponentNode objects
            parent: Parent component ID (if None, component is added to root)
            
        Returns:
            Self for method chaining
        """
        if props is None:
            props = {}
        
        # Store component data
        self._components[id] = {
            "id": id,
            "type": type,
            "props": props
        }
        
        # Store children if provided
        if children:
            self._children[id] = children
        
        # If no root is set, this becomes the root
        if self._root_id is None:
            self._root_id = id
        
        # If parent is specified, add as child to parent
        if parent:
            if parent not in self._children:
                self._children[parent] = []
            if id not in self._children[parent]:
                self._children[parent].append(id)
        
        return self
    
    def build(self) -> Page:
        """Build and return the Page object.
        
        Returns:
            Validated Page object
        """
        if self._root_id is None:
            raise ValueError("Page must have at least one component (root)")
        
        # Resolve component tree (convert child IDs to ComponentNode objects)
        def resolve_component(comp_id: str) -> ComponentNode:
            comp_data = self._components[comp_id]
            resolved_children = []
            
            # Get children for this component
            if comp_id in self._children:
                for child in self._children[comp_id]:
                    if isinstance(child, str):
                        # Resolve child ID to ComponentNode
                        resolved_children.append(resolve_component(child))
                    elif isinstance(child, ComponentNode):
                        resolved_children.append(child)
            
            return ComponentNode(
                id=comp_data["id"],
                type=comp_data["type"],
                props=comp_data["props"],
                children=resolved_children
            )
        
        root = resolve_component(self._root_id)
        
        return Page(
            path=self.path,
            layout=self.layout,
            root=root
        )


def set_template_directory(template_dir: Path | str, template_name: str) -> None:
    """Set a template directory and template name to use as the loader.
    
    This creates a loader function that loads the specified template from the directory
    and sets it via set_template_loader().
    
    Args:
        template_dir: Directory containing JSON template files
        template_name: Name of the template file (without .json extension)
    """
    from .router import set_template_loader
    
    def loader():
        template_path = Path(template_dir) / f"{template_name}.json"
        return load_template(template_path)
    
    set_template_loader(loader)
