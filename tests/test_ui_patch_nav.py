"""Tests for UI patch and navigation handling."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from agentprinter_fastapi import set_template_loader
from agentprinter_fastapi.schemas import Page, ComponentNode


@pytest.fixture
def app():
    """FastAPI app for UI patch and navigation tests."""
    from agentprinter_fastapi.router import router
    
    app = FastAPI()
    app.include_router(router)
    
    # Simple template loader
    def template_loader():
        return Page(
            path="/home",
            root=ComponentNode(id="root", type="div")
        )
    
    set_template_loader(template_loader)
    return app


def test_e2e_receive_ui_patch(app):
    """Test that frontend receives ui.patch messages from backend."""
    from agentprinter_fastapi import manager
    
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # Skip hello and render
        websocket.receive_json()
        websocket.receive_json()
        
        # Backend sends ui.patch (simulated via broadcast)
        patch_msg = {
            "type": "ui.patch",
            "header": {"trace_id": "patch-1", "id": "msg-2", "timestamp": "2026-02-01T12:00:00Z", "version": "1.0.0"},
            "payload": {
                "target_id": "root",
                "operation": "update_props",
                "props": {"visible": True}
            }
        }
        
        # Broadcast to all clients
        import asyncio

        async def send_patch():
            await manager.broadcast(patch_msg)
            await asyncio.sleep(manager.patch_coalesce_window * 2)

        asyncio.run(send_patch())
        
        # Client receives patch
        received = websocket.receive_json()
        assert received["type"] == "ui.patch"
        assert received["payload"]["target_id"] == "root"


def test_e2e_receive_navigation_message(app):
    """Test that frontend receives navigation messages from backend."""
    from agentprinter_fastapi import manager
    
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # Skip hello and render
        websocket.receive_json()
        websocket.receive_json()
        
        # Backend sends navigation message
        nav_msg = {
            "type": "protocol.navigate",
            "header": {"trace_id": "nav-1", "id": "msg-3", "timestamp": "2026-02-01T12:00:00Z", "version": "1.0.0"},
            "payload": {
                "to": "/settings",
                "params": {"tab": "profile"},
                "replace": False,
                "open": "same"
            }
        }
        
        # Broadcast to all clients
        import asyncio

        async def send_nav():
            await manager.broadcast(nav_msg)

        asyncio.run(send_nav())
        
        # Client receives navigation
        received = websocket.receive_json()
        assert received["type"] == "protocol.navigate"
        assert received["payload"]["to"] == "/settings"
