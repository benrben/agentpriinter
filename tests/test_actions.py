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
        payload={"action_id": "test_action", "trigger": "click", "target": "backend:test_action", "foo": "bar"}
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
        payload={"action_id": "unknown_btn", "trigger": "click", "target": "backend:unknown_btn"}
    )
    
    with pytest.raises(KeyError, match="No handler registered for action_id: unknown_btn"):
        await router.handle_message(message, object())

@pytest.mark.asyncio
async def test_action_with_agent_target():
    """Test that action with target='agent' can be routed."""
    router = ActionRouter()
    
    called_with = {}
    
    async def test_handler(message: Message, websocket):
        called_with["message"] = message
    
    router.register_handler("run_agent", test_handler)
    
    message = Message(
        type="user.action",
        header=MessageHeader(trace_id="test-trace"),
        payload={
            "action_id": "run_agent",
            "trigger": "click",
            "target": "agent",
            "params": {"query": "hello"}
        }
    )
    
    await router.handle_message(message, object())
    assert "message" in called_with
    assert called_with["message"].payload["target"] == "agent"

@pytest.mark.asyncio
async def test_action_with_tool_target():
    """Test that action with target='tool' can be routed."""
    router = ActionRouter()
    
    called_with = {}
    
    async def test_handler(message: Message, websocket):
        called_with["message"] = message
    
    router.register_handler("call_tool", test_handler)
    
    message = Message(
        type="user.action",
        header=MessageHeader(trace_id="test-trace"),
        payload={
            "action_id": "call_tool",
            "trigger": "click",
            "target": "tool",
            "tool_name": "search"
        }
    )
    
    await router.handle_message(message, object())
    assert "message" in called_with
    assert called_with["message"].payload["target"] == "tool"

@pytest.mark.asyncio
async def test_invalid_action_payload_validation():
    """Test that invalid action payload is rejected during validation."""
    from agentprinter_fastapi.schemas.actions import ActionPayload
    from pydantic import ValidationError
    
    # Missing required action_id
    with pytest.raises(ValidationError):
        ActionPayload(trigger="click")


@pytest.mark.asyncio
async def test_action_router_rejects_missing_action_id():
    """ActionRouter must not silently ignore invalid action payloads."""
    from agentprinter_fastapi.actions import InvalidActionPayloadError

    router = ActionRouter()
    message = Message(
        type="user.action",
        header=MessageHeader(trace_id="test-trace"),
        payload={
            "trigger": "click",
            "target": "agent:run",
        },
    )

    with pytest.raises(InvalidActionPayloadError):
        await router.handle_message(message, object())

@pytest.mark.asyncio
async def test_action_routes_to_agent_by_target():
    """Test that action with target starting with 'agent:' routes to agent handler."""
    router = ActionRouter()
    
    called_with = {}
    
    async def agent_handler(message: Message, websocket):
        called_with["message"] = message
        called_with["handler_type"] = "agent"
    
    router.register_target_handler("agent", agent_handler)
    
    message = Message(
        type="user.action",
        header=MessageHeader(trace_id="test-trace"),
        payload={
            "action_id": "any_id",
            "trigger": "click",
            "target": "agent:run_analysis",
        }
    )
    
    await router.handle_message(message, object())
    assert "handler_type" in called_with
    assert called_with["handler_type"] == "agent"

@pytest.mark.asyncio
async def test_action_routes_to_tool_by_target():
    """Test that action with target starting with 'tool:' routes to tool handler."""
    router = ActionRouter()
    
    called_with = {}
    
    async def tool_handler(message: Message, websocket):
        called_with["message"] = message
        called_with["handler_type"] = "tool"
    
    router.register_target_handler("tool", tool_handler)
    
    message = Message(
        type="user.action",
        header=MessageHeader(trace_id="test-trace"),
        payload={
            "action_id": "any_id",
            "trigger": "click",
            "target": "tool:search",
        }
    )
    
    await router.handle_message(message, object())
    assert "handler_type" in called_with
    assert called_with["handler_type"] == "tool"

@pytest.mark.asyncio
async def test_action_routes_to_http_by_target():
    """Test that action with target starting with 'http:' routes to HTTP handler."""
    router = ActionRouter()
    
    called_with = {}
    
    async def http_handler(message: Message, websocket):
        called_with["message"] = message
        called_with["handler_type"] = "http"
    
    router.register_target_handler("http", http_handler)
    
    message = Message(
        type="user.action",
        header=MessageHeader(trace_id="test-trace"),
        payload={
            "action_id": "any_id",
            "trigger": "click",
            "target": "http:POST:/api/endpoint",
        }
    )
    
    await router.handle_message(message, object())
    assert "handler_type" in called_with
    assert called_with["handler_type"] == "http"
