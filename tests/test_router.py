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

def test_websocket_handshake_with_auth_hook():
    """Test that websocket calls auth hook during handshake."""
    from agentprinter_fastapi import set_auth_hook
    
    auth_called = []
    
    def mock_auth_hook(websocket_scope):
        auth_called.append(True)
        return True  # Auth succeeds
    
    # Set auth hook
    set_auth_hook(mock_auth_hook)
    
    app = create_app()
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "protocol.hello"
        assert len(auth_called) > 0, "Auth hook was not called"
    
    # Cleanup
    set_auth_hook(None)

def test_websocket_handshake_protocol_version():
    """Test that protocol version is advertised in hello."""
    app = create_app()
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "protocol.hello"
        assert data["header"]["version"] == "1.0.0"

def test_auth_failure_returns_error_and_closes():
    """Test that auth failure returns protocol.error and closes socket."""
    from agentprinter_fastapi import set_auth_hook
    
    def mock_auth_hook_fail(websocket_scope):
        return False  # Auth fails
    
    set_auth_hook(mock_auth_hook_fail)
    
    app = create_app()
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # Should receive protocol.error
        data = websocket.receive_json()
        assert data["type"] == "protocol.error"
        assert data["payload"]["code"] == "auth_failed"
        # Socket should be closed (TestClient will raise if we try to receive again)
        try:
            websocket.receive_json()
            pytest.fail("Socket should be closed after auth failure")
        except Exception:
            pass  # Expected: socket closed
    
    set_auth_hook(None)

def test_version_mismatch_returns_error_and_closes():
    """Test that version mismatch returns protocol.error and closes socket."""
    from agentprinter_fastapi import set_version_negotiation
    
    def mock_version_negotiation(client_version):
        # Server only supports 1.0.0, client requests 2.0.0
        if client_version != "1.0.0":
            return None  # Version mismatch
        return "1.0.0"
    
    set_version_negotiation(mock_version_negotiation)
    
    app = create_app()
    client = TestClient(app)
    
    with client.websocket_connect("/ws?version=2.0.0") as websocket:
        # Should receive protocol.error for version mismatch
        data = websocket.receive_json()
        assert data["type"] == "protocol.error"
        assert data["payload"]["code"] == "version_mismatch"
        # Socket should be closed
        try:
            websocket.receive_json()
            pytest.fail("Socket should be closed after version mismatch")
        except Exception:
            pass  # Expected: socket closed
    
    set_version_negotiation(None)

def test_version_negotiation_success():
    """Test that successful version negotiation allows connection."""
    from agentprinter_fastapi import set_version_negotiation
    
    def mock_version_negotiation(client_version):
        # Server supports 1.0.0 and 2.0.0
        if client_version in ["1.0.0", "2.0.0"]:
            return client_version
        return None
    
    set_version_negotiation(mock_version_negotiation)
    
    app = create_app()
    client = TestClient(app)
    
    with client.websocket_connect("/ws?version=2.0.0") as websocket:
        # Should receive protocol.hello with negotiated version
        data = websocket.receive_json()
        assert data["type"] == "protocol.hello"
        assert data["header"]["version"] == "2.0.0"
    
    set_version_negotiation(None)
