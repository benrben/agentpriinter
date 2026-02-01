"""Tests for UI template loader."""
import pytest
import tempfile
import json
from pathlib import Path
from agentprinter_fastapi.schemas import Page, ComponentNode

@pytest.mark.asyncio
async def test_load_template_from_file():
    """Test that a valid JSON template is loaded and parsed into Page."""
    # Create a temporary template file
    with tempfile.TemporaryDirectory() as tmpdir:
        template_data = {
            "path": "/dashboard",
            "layout": "default",
            "root": {
                "id": "root",
                "type": "container",
                "props": {"layout": "flex"},
                "children": [
                    {
                        "id": "header",
                        "type": "heading",
                        "props": {"text": "Welcome"},
                    }
                ]
            }
        }
        
        template_path = Path(tmpdir) / "dashboard.json"
        with open(template_path, "w") as f:
            json.dump(template_data, f)
        
        # Import and use the loader
        from agentprinter_fastapi.templates import load_template
        
        page = load_template(template_path)
        
        assert page is not None
        assert page.path == "/dashboard"
        assert page.root.id == "root"
        assert page.root.type == "container"

@pytest.mark.asyncio
async def test_set_template_loader():
    """Test that template loader can be configured on the router."""
    from agentprinter_fastapi import set_template_loader
    
    def mock_loader():
        return Page(
            path="/test",
            root=ComponentNode(id="root", type="div")
        )
    
    set_template_loader(mock_loader)
    # Verify it doesn't raise
    assert True

@pytest.mark.asyncio
async def test_page_builder_api():
    """Test that PageBuilder API creates Page objects programmatically."""
    from agentprinter_fastapi.templates import PageBuilder
    
    builder = PageBuilder(path="/dashboard")
    builder.add_component("content", "container")
    builder.add_component("header", "heading", props={"text": "Welcome"}, parent="content")
    
    page = builder.build()
    
    assert page.path == "/dashboard"
    assert page.root.id == "content"
    assert page.root.type == "container"
    assert len(page.root.children) == 1
    assert page.root.children[0].id == "header"

@pytest.mark.asyncio
async def test_set_template_directory():
    """Test that setting a template directory creates a loader automatically."""
    import tempfile
    import json
    from pathlib import Path
    from agentprinter_fastapi.templates import set_template_directory
    
    with tempfile.TemporaryDirectory() as tmpdir:
        template_data = {
            "path": "/home",
            "layout": "default",
            "root": {
                "id": "root",
                "type": "container",
                "props": {},
                "children": []
            }
        }
        
        template_path = Path(tmpdir) / "home.json"
        with open(template_path, "w") as f:
            json.dump(template_data, f)
        
        # Set template directory
        set_template_directory(tmpdir, "home")
        
        # Verify loader was set
        from agentprinter_fastapi.router import _template_loader
        assert _template_loader is not None
        
        # Call loader and verify it returns the correct page
        page = _template_loader()
        assert page.path == "/home"
        assert page.root.id == "root"
