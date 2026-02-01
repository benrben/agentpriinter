from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

# Delay import to inside test or fixture if possible to avoid module errors if not created yet
# But TestClient needs app...

def create_app():
    from agentprinter_fastapi.router import router
    app = FastAPI()
    app.include_router(router)
    return app

def test_websocket_lifecycle():
    try:
        app = create_app()
    except ImportError:
        pytest.fail("Could not import router from agentprinter_fastapi.router")

    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # 1. Expect Hello
        data = websocket.receive_json()
        assert data["type"] == "protocol.hello"
        assert "trace_id" in data["header"]
        
        # 2. Send something (simulate client)
        websocket.send_json({"type": "ping", "header": {"trace_id": "test"}, "payload": {}})
        
        # 3. Connection stays open until we close context
        # (Implicitly tests graceful disconnect when context exits)
