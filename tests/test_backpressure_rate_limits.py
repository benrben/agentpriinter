"""Tests for backpressure controls and rate limiting."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from agentprinter_fastapi.router import router, set_auth_hook
from agentprinter_fastapi.backpressure import rate_limiter, backpressure
from agentprinter_fastapi import set_max_message_size, set_initial_page, set_template_loader


@pytest.fixture
def app():
    """FastAPI app for backpressure tests."""
    from agentprinter_fastapi import set_max_message_size, set_initial_page, set_template_loader
    from agentprinter_fastapi.backpressure import connection_rate_limiter
    app = FastAPI()
    app.include_router(router)
    # Reset rate limiter state between tests
    rate_limiter.buckets.clear()
    # Reset connection rate limiter to default (high value, effectively disabled)
    connection_rate_limiter.rate = 100
    connection_rate_limiter.buckets.clear()
    # Reset max message size to None (disabled) between tests
    set_max_message_size(None)
    # Reset any template/initial page to avoid extra ui.render messages
    set_template_loader(None)
    set_initial_page(None)
    return app


def test_message_over_size_limit_returns_protocol_error(app):
    """Test that messages over size limit return protocol.error."""
    # Set max message size to 100 bytes
    set_max_message_size(100)
    
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # Receive hello
        hello = websocket.receive_json()
        assert hello["type"] == "protocol.hello"
        
        # Consume any ui.render if template loader is set
        try:
            msg = websocket.receive_json(timeout=0.1)
            if msg.get("type") == "ui.render":
                pass  # Expected, consume it
        except:
            pass  # No ui.render, that's fine
        
        # Send message that exceeds size limit (large payload)
        large_payload = "x" * 200  # 200 bytes, exceeds 100 byte limit
        large_message = {
            "type": "user.action",
            "header": {"trace_id": "test-1"},
            "payload": {"action_id": "test_action", "data": large_payload}
        }
        
        websocket.send_json(large_message)
        
        # Should receive protocol.error
        response = websocket.receive_json()
        assert response["type"] == "protocol.error"
        assert response["payload"]["code"] == "message_too_large"


def test_rate_limit_rejects_excess_inbound_messages(app):
    """Test that rate limiter rejects excess inbound messages."""
    # Set rate limit to 1 message per second (very restrictive for test)
    rate_limiter.rate = 1
    rate_limiter.window = 1
    rate_limiter.buckets.clear()  # Clear any existing state
    
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # Receive hello
        websocket.receive_json()
        
        # Send first message (should be allowed, but will fail action validation - that's ok)
        message1 = {
            "type": "user.action",
            "header": {"trace_id": "test-1"},
            "payload": {"action_id": "test_action", "data": {}}
        }
        websocket.send_json(message1)
        # Consume first response (invalid_action_payload or unknown_action)
        resp1 = websocket.receive_json()
        assert resp1["type"] == "protocol.error"
        # First message should have been processed (rate limit allows 1)
        
        # Second message should be rate limited (rate is 1, already used)
        message2 = {
            "type": "user.action",
            "header": {"trace_id": "test-2"},
            "payload": {"action_id": "test_action", "data": {}}
        }
        websocket.send_json(message2)
        
        # Should receive protocol.error for rate limit (not invalid_action_payload)
        response = websocket.receive_json()
        assert response["type"] == "protocol.error"
        # This should be rate_limit_exceeded, not invalid_action_payload
        assert response["payload"]["code"] == "rate_limit_exceeded", f"Expected rate_limit_exceeded, got {response['payload']['code']}"


def test_connection_rate_limit_rejects_excess_attempts(app):
    """Test that connection rate limit rejects excess connection attempts."""
    from agentprinter_fastapi.backpressure import connection_rate_limiter
    
    # Set connection rate limit to 1 per second (very restrictive)
    connection_rate_limiter.rate = 1
    connection_rate_limiter.window = 1
    connection_rate_limiter.buckets.clear()
    
    client = TestClient(app)
    
    # Make first successful connection
    with client.websocket_connect("/ws") as websocket:
        hello = websocket.receive_json()
        assert hello["type"] == "protocol.hello"
    
    # Second connection attempt should be rejected (rate is 1)
    with client.websocket_connect("/ws") as websocket:
        # Should receive protocol.error instead of hello
        response = websocket.receive_json()
        assert response["type"] == "protocol.error"
        assert response["payload"]["code"] == "connection_rate_limit_exceeded"


@pytest.mark.asyncio
async def test_rapid_patches_are_coalesced(app):
    """Test that rapid ui.patch messages are coalesced into a single send."""
    import asyncio
    from agentprinter_fastapi.router import manager
    from agentprinter_fastapi.schemas import Message, MessageHeader
    
    received_messages = []
    
    # Create a mock websocket that captures messages
    class MockWebSocket:
        async def send_json(self, data):
            received_messages.append(data)
        async def accept(self):
            pass
    
    mock_ws = MockWebSocket()
    await manager.connect(mock_ws)
    
    # Send 3 rapid ui.patch messages (within coalescing window)
    for i in range(3):
        patch_msg = Message(
            type="ui.patch",
            header=MessageHeader(trace_id=f"patch-{i}"),
            payload={"target_id": "button-1", "operation": "update_props", "props": {"disabled": i % 2 == 0}}
        )
        await manager.broadcast(patch_msg)
        # Small delay to ensure they're within coalescing window
        await asyncio.sleep(0.01)
    
    # Wait for coalescing to complete
    await asyncio.sleep(0.15)
    
    # Should have received fewer than 3 messages (coalesced)
    # Filter for ui.patch messages
    patch_messages = [m for m in received_messages if m.get("type") == "ui.patch"]
    # With coalescing, we should get 1 message instead of 3
    assert len(patch_messages) <= 1, f"Expected coalesced patches (1 message), got {len(patch_messages)} separate messages"
