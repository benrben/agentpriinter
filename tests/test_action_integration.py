from fastapi import FastAPI
from fastapi.testclient import TestClient
from agentprinter_fastapi.router import router
from agentprinter_fastapi.actions import action_router, Message
import pytest
import json
from agentprinter_fastapi import set_template_loader
from agentprinter_fastapi.schemas import Page, ComponentNode

app = FastAPI()
app.include_router(router)

def _set_test_template_loader():
    """Ensure `/ws` sends `ui.render` for this test only."""
    def _loader():
        return Page(path="/test", root=ComponentNode(id="root", type="container"))

    set_template_loader(_loader)

def test_action_routing_integration():
    client = TestClient(app)
    
    # Register a test handler
    called = []
    @action_router.action("integration_test")
    async def handler(message: Message, websocket):
        called.append(message.payload["data"])
        await websocket.send_json({
            "type": "test.response",
            "header": {"trace_id": message.header.trace_id},
            "payload": {"status": "ok"}
        })

    _set_test_template_loader()
    try:
        with client.websocket_connect("/ws") as websocket:
            # Skip Hello and UI Render
            websocket.receive_json() # hello
            websocket.receive_json() # ui.render
            
            # Send action
            action_msg = {
                "type": "user.action",
                "header": {"trace_id": "trace-123"},
                "payload": {
                    "action_id": "integration_test",
                    "trigger": "click",
                    "target": "backend:integration_test",
                    "data": "hello-backend",
                },
            }
            websocket.send_json(action_msg)
            
            # Verify handler was called and response received
            response = websocket.receive_json()
            assert response["type"] == "test.response"
            assert response["payload"]["status"] == "ok"
            assert called == ["hello-backend"]
    finally:
        set_template_loader(None)

def test_unknown_action_error():
    client = TestClient(app)
    _set_test_template_loader()
    try:
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json() # hello
            websocket.receive_json() # ui.render
            
            # Send unknown action
            action_msg = {
                "type": "user.action",
                "header": {"trace_id": "trace-456"},
                "payload": {"action_id": "non_existent", "trigger": "click", "target": "backend:non_existent"},
            }
            websocket.send_json(action_msg)
            
            # Verify error response
            response = websocket.receive_json()
            assert response["type"] == "protocol.error"
            assert response["payload"]["code"] == "unknown_action"
            assert "non_existent" in response["payload"]["message"]
    finally:
        set_template_loader(None)

def test_handler_exception_error():
    client = TestClient(app)
    
    @action_router.action("fail_action")
    async def failing_handler(message, websocket):
        raise ValueError("Boom!")

    _set_test_template_loader()
    try:
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json() # hello
            websocket.receive_json() # ui.render
            
            websocket.send_json({
                "type": "user.action",
                "header": {"trace_id": "trace-789"},
                "payload": {"action_id": "fail_action", "trigger": "click", "target": "backend:fail_action"},
            })
            
            response = websocket.receive_json()
            assert response["type"] == "protocol.error"
            assert response["payload"]["code"] == "handler_error"
            assert "Boom!" in response["payload"]["message"]
    finally:
        set_template_loader(None)

def test_invalid_json_error():
    client = TestClient(app)
    _set_test_template_loader()
    try:
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json() # hello
            websocket.receive_json() # ui.render
            
            # Send garbage
            websocket.send_text("not json")
            
            response = websocket.receive_json()
            assert response["type"] == "protocol.error"
            assert response["payload"]["code"] == "invalid_message"
    finally:
        set_template_loader(None)


def test_invalid_action_payload_missing_action_id_returns_protocol_error():
    client = TestClient(app)
    _set_test_template_loader()
    try:
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json() # hello
            websocket.receive_json() # ui.render
    
            websocket.send_json({
                "type": "user.action",
                "header": {"trace_id": "trace-missing-action-id"},
                "payload": {
                    "trigger": "click",
                    "target": "agent:run"
                }
            })
    
            response = websocket.receive_json()
            assert response["type"] == "protocol.error"
            assert response["payload"]["code"] == "invalid_action_payload"
    finally:
        set_template_loader(None)


def test_invalid_action_payload_bad_trigger_returns_protocol_error():
    client = TestClient(app)
    _set_test_template_loader()
    try:
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json() # hello
            websocket.receive_json() # ui.render
    
            websocket.send_json({
                "type": "user.action",
                "header": {"trace_id": "trace-bad-trigger"},
                "payload": {
                    "action_id": "some_action",
                    "trigger": "not-a-real-trigger",
                    "target": "agent:run"
                }
            })
    
            response = websocket.receive_json()
            assert response["type"] == "protocol.error"
            assert response["payload"]["code"] == "invalid_action_payload"
    finally:
        set_template_loader(None)
