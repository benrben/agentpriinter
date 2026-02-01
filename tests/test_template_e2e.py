"""End-to-end tests for template loading + WebSocket integration."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from agentprinter_fastapi import set_template_loader
from agentprinter_fastapi.schemas import Page, ComponentNode


@pytest.fixture
def app_with_template():
    """FastAPI app with template loader configured."""
    from agentprinter_fastapi.router import router
    
    app = FastAPI()
    app.include_router(router)
    
    # Configure template loader
    def template_loader():
        return Page(
            path="/test",
            layout="default",
            root=ComponentNode(
                id="container",
                type="div",
                children=[
                    ComponentNode(
                        id="title",
                        type="h1",
                        props={"text": "E2E Test Page"}
                    )
                ]
            )
        )
    
    set_template_loader(template_loader)
    return app


def test_e2e_template_over_websocket(app_with_template):
    """Test that template-loaded page is sent to client over WebSocket."""
    client = TestClient(app_with_template)
    
    with client.websocket_connect("/ws") as websocket:
        # 1. Receive hello
        hello = websocket.receive_json()
        assert hello["type"] == "protocol.hello"
        
        # 2. Receive ui.render with template-loaded page
        render = websocket.receive_json()
        assert render["type"] == "ui.render"
        assert render["payload"]["path"] == "/test"
        assert render["payload"]["root"]["id"] == "container"
        assert render["payload"]["root"]["type"] == "div"
        assert len(render["payload"]["root"]["children"]) == 1
        assert render["payload"]["root"]["children"][0]["id"] == "title"


def test_e2e_action_to_backend(app_with_template):
    """Test that client can send actions and backend routes them."""
    from agentprinter_fastapi.actions import action_router
    
    client = TestClient(app_with_template)
    
    # Track if action handler was called
    handled_actions = []
    
    @action_router.action("test_button_click")
    async def handle_click(message, websocket):
        handled_actions.append(message.payload)
    
    with client.websocket_connect("/ws") as websocket:
        # Skip hello and render messages
        websocket.receive_json()
        websocket.receive_json()
        
        # Send action from client
        action_msg = {
            "type": "user.action",
            "header": {"trace_id": "e2e-test", "id": "msg-1", "timestamp": "2026-02-01T12:00:00Z", "version": "1.0.0"},
            "payload": {
                "action_id": "test_button_click",
                "trigger": "click",
                "target": "agent"
            }
        }
        websocket.send_json(action_msg)
        
        # Verify action was handled
        import asyncio
        asyncio.run(asyncio.sleep(0.1))  # Give handler time to run
        assert len(handled_actions) > 0
        assert handled_actions[0]["action_id"] == "test_button_click"
