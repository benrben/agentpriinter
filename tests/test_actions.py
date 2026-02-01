"""Tests for action routing system."""
import pytest
from agentprinter_fastapi.actions import ActionRouter
from agentprinter_fastapi.schemas.protocol import Message, MessageHeader


@pytest.mark.asyncio
async def test_handler_is_called_when_action_sent():
    """Test that registered handler is called when action message is received."""
    router = ActionRouter()
    
    # Track if handler was called
    called_with = {}
    
    async def test_handler(message: Message, websocket):
        called_with["message"] = message
        called_with["websocket"] = websocket
    
    # Register handler
    router.register_handler("test_action", test_handler)
    
    # Create test message
    message = Message(
        type="user.action",
        header=MessageHeader(
            trace_id="test-trace",
            id="msg-1",
            timestamp="2026-02-01T12:00:00Z"
        ),
        payload={"action_id": "test_action", "foo": "bar"}
    )
    
    # Mock websocket
    mock_ws = object()
    
    # Handle message
    await router.handle_message(message, mock_ws)
    
    # Verify handler was called
    assert "message" in called_with
    assert called_with["message"] == message
    assert called_with["websocket"] == mock_ws


@pytest.mark.asyncio
async def test_unknown_action_raises_key_error():
    """Test that unregistered action_id raises KeyError."""
    router = ActionRouter()
    
    # Create test message with unregistered action_id
    message = Message(
        type="user.action",
        header=MessageHeader(trace_id="test-trace"),
        payload={"action_id": "unknown_btn"}
    )
    
    with pytest.raises(KeyError, match="No handler registered for action_id: unknown_btn"):
        await router.handle_message(message, object())
