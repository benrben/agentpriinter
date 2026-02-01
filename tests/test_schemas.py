from uuid import uuid4
from datetime import datetime
import pytest
from pydantic import ValidationError
from typing import Any

def test_message_header_instantiation():
    try:
        from agentprinter_fastapi.schemas.protocol import MessageHeader
    except ImportError:
        pytest.fail("Could not import MessageHeader from agentprinter_fastapi.schemas.protocol")

    # Test valid instantiation
    trace_id = "trace-123"
    header = MessageHeader(trace_id=trace_id)
    assert header.trace_id == trace_id
    assert header.version == "1.0.0"
    assert isinstance(header.id, str)
    assert isinstance(header.timestamp, datetime)

def test_message_header_requires_trace_id():
    from agentprinter_fastapi.schemas.protocol import MessageHeader
    with pytest.raises(ValidationError):
        MessageHeader() # trace_id is missing

def test_message_envelope():
    from agentprinter_fastapi.schemas.protocol import Message, MessageHeader
    trace_id = "trace-456"
    header = MessageHeader(trace_id=trace_id)
    payload = {"foo": "bar"}
    
    msg = Message(type="test.event", header=header, payload=payload)
    
    assert msg.type == "test.event"
    assert msg.header.trace_id == trace_id
    assert msg.payload["foo"] == "bar"

def test_message_validation_error():
    from agentprinter_fastapi.schemas.protocol import Message
    with pytest.raises(ValidationError):
        Message(type="bad", header="not-a-header", payload={})

def test_message_header_includes_app_id_and_session_id():
    """NEW: MessageHeader should accept optional app_id and session_id for auth context."""
    from agentprinter_fastapi.schemas.protocol import MessageHeader
    
    trace_id = "trace-789"
    app_id = "myapp-prod"
    session_id = "sess-abc123"
    
    header = MessageHeader(trace_id=trace_id, app_id=app_id, session_id=session_id)
    
    assert header.trace_id == trace_id
    assert header.app_id == app_id
    assert header.session_id == session_id

def test_message_header_includes_workspace_id_and_user_id():
    """NEW: MessageHeader should accept optional workspace_id and user_id for multi-tenancy."""
    from agentprinter_fastapi.schemas.protocol import MessageHeader
    
    trace_id = "trace-999"
    workspace_id = "ws-xyz789"
    user_id = "user-alice"
    
    header = MessageHeader(trace_id=trace_id, workspace_id=workspace_id, user_id=user_id)
    
    assert header.trace_id == trace_id
    assert header.workspace_id == workspace_id
    assert header.user_id == user_id

def test_error_payload_structure():
    """NEW: Protocol should support structured error payloads with code, message, and details."""
    from agentprinter_fastapi.schemas.protocol import ErrorPayload
    
    error = ErrorPayload(
        code="AUTH_FAILED",
        message="Authentication failed",
        details={"reason": "invalid_token"}
    )
    
    assert error.code == "AUTH_FAILED"
    assert error.message == "Authentication failed"
    assert error.details == {"reason": "invalid_token"}

def test_action_payload_is_exported():
    """NEW: ActionPayload should be part of protocol contracts for schema export."""
    from agentprinter_fastapi.schemas import ActionPayload
    
    action = ActionPayload(
        action_id="act-123",
        trigger="click",
        target="agent:run_analysis"
    )
    
    assert action.action_id == "act-123"
    assert action.trigger == "click"
    assert action.target == "agent:run_analysis"
    assert action.mode == "stream"

def test_navigation_payload_structure():
    """NEW: Navigation should define routing contracts."""
    from agentprinter_fastapi.schemas.protocol import Navigation
    
    nav = Navigation(
        to="/dashboard",
        params={"user_id": "123"},
        replace=False,
        open="same"
    )
    
    assert nav.to == "/dashboard"
    assert nav.params == {"user_id": "123"}
    assert nav.replace is False
    assert nav.open == "same"

def test_style_contract_structure():
    """NEW: Component nodes should support style contracts with theme tokens and allowlisted properties."""
    from agentprinter_fastapi.schemas.ui import ComponentStyle, ThemeTokens
    
    tokens = ThemeTokens(
        color_primary="#007AFF",
        spacing_unit=8,
        radius_default=4,
        font_size_base=14
    )
    
    assert tokens.color_primary == "#007AFF"
    assert tokens.spacing_unit == 8
    
    style = ComponentStyle(
        theme=tokens,
        className="p-4 rounded",
        variant="primary"
    )
    
    assert style.theme.color_primary == "#007AFF"
    assert style.className == "p-4 rounded"
    assert style.variant == "primary"

def test_component_node_with_style():
    """NEW: ComponentNode should accept optional style field."""
    from agentprinter_fastapi.schemas.ui import ComponentNode, ComponentStyle, ThemeTokens
    
    tokens = ThemeTokens(color_primary="#FF0000", spacing_unit=4)
    style = ComponentStyle(theme=tokens, variant="danger")
    
    node = ComponentNode(
        id="btn-1",
        type="button",
        style=style
    )
    
    assert node.id == "btn-1"
    assert node.style is not None
    assert node.style.theme.color_primary == "#FF0000"

def test_tool_contract_structure():
    """Test that Tool model can be imported and has required fields."""
    try:
        from agentprinter_fastapi.schemas.tools import Tool
    except ImportError:
        pytest.fail("Could not import Tool from agentprinter_fastapi.schemas.tools")
    
    tool = Tool(
        name="search",
        description="Search documents",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
    )
    
    assert tool.name == "search"
    assert tool.description == "Search documents"
    assert tool.input_schema is not None

def test_schema_contract_structure():
    """Test that SchemaContract model can be imported and has required fields."""
    try:
        from agentprinter_fastapi.schemas.tools import SchemaContract
    except ImportError:
        pytest.fail("Could not import SchemaContract from agentprinter_fastapi.schemas.tools")
    
    schema = SchemaContract(
        title="User Form",
        json_schema={"type": "object", "properties": {"name": {"type": "string"}}},
        ui_schema={"name": {"ui:widget": "text"}},
    )
    
    assert schema.title == "User Form"
    assert schema.json_schema is not None
    assert schema.ui_schema is not None

def test_protocol_resume_and_sequence():
    """NEW: MessageHeader should support monotonic sequence and ResumePayload should be defined."""
    from agentprinter_fastapi.schemas.protocol import MessageHeader, ResumePayload
    
    # Check MessageHeader seq
    header = MessageHeader(trace_id="seq-test", seq=42)
    assert header.seq == 42
    
    # Check ResumePayload
    resume = ResumePayload(last_seen_seq=100)
    assert resume.last_seen_seq == 100
