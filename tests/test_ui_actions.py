from typing import Literal
import pytest
from pydantic import ValidationError

def test_action_payload_structure():
    try:
        from agentprinter_fastapi.schemas.actions import ActionPayload
    except ImportError:
        pytest.fail("Could not import ActionPayload")

    action = ActionPayload(
        action_id="act-1",
        trigger="click",
        target="agent:run",
        payload_mapping={"query": "state.query"}
    )
    assert action.trigger == "click"
    assert action.mode == "stream" # default

def test_recursive_component_node():
    try:
        from agentprinter_fastapi.schemas.ui import ComponentNode
    except ImportError:
        pytest.fail("Could not import ComponentNode")
        
    child = ComponentNode(id="child-1", type="text", props={"content": "Hello"})
    parent = ComponentNode(
        id="parent-1", 
        type="container", 
        children=[child]
    )
    
    assert len(parent.children) == 1
    assert parent.children[0].id == "child-1"

def test_page_structure():
    try:
        from agentprinter_fastapi.schemas.ui import Page, ComponentNode
    except ImportError:
        pytest.fail("Could not import Page")
        
    root = ComponentNode(id="root", type="container")
    page = Page(path="/dashboard", root=root)
    
    assert page.layout == "default"
    assert page.root.id == "root"
