"""Comprehensive tests for all remaining features."""
import pytest
from agentprinter_fastapi.transports import SSETransport, HTTPPollingTransport
from agentprinter_fastapi.backpressure import RateLimiter, BackpressureController
from agentprinter_fastapi.components import ComponentBank, component_bank, ComponentDefinition
from agentprinter_fastapi.validation import StyleValidator, PropValidator
from agentprinter_fastapi.transport import ResumableTransport, ExponentialBackoff, OrderedMessageBuffer
from agentprinter_fastapi.devtools import DevtoolsPanel

# Task 9: SSE/HTTP Fallback Transport
def test_sse_transport():
    """Test SSE transport initialization."""
    sse = SSETransport()
    assert len(sse.clients) == 0
    
    async def callback(msg): pass
    sse.register_client("session-1", callback)
    assert "session-1" in sse.clients

def test_http_polling_transport():
    """Test HTTP polling transport."""
    poll = HTTPPollingTransport()
    
    poll.enqueue_message("client-1", {"type": "test"})
    poll.enqueue_message("client-1", {"type": "test2"})
    
    messages = poll.dequeue_messages("client-1", cursor=0, count=2)
    assert len(messages) == 2
    assert messages[0]["type"] == "test"

# Task 10: Backpressure & Rate Limits
def test_rate_limiter():
    """Test rate limiter."""
    limiter = RateLimiter(rate=5, window_seconds=1)
    
    # Allow 5 messages
    for i in range(5):
        assert limiter.is_allowed("client-1") == True
    
    # 6th should be blocked
    assert limiter.is_allowed("client-1") == False
    
    # Check remaining
    remaining = limiter.get_remaining("client-1")
    assert remaining == 0

@pytest.mark.asyncio
async def test_backpressure_controller():
    """Test backpressure controller."""
    bp = BackpressureController(max_queue_size=2)
    
    # Enqueue 2 messages
    assert await bp.enqueue("client-1", {"msg": 1}) == True
    assert await bp.enqueue("client-1", {"msg": 2}) == True
    
    # 3rd should be blocked (queue full)
    assert await bp.enqueue("client-1", {"msg": 3}) == False
    
    # Check depth
    assert bp.queue_depth("client-1") == 2

# Task 11: Component Bank
def test_component_bank():
    """Test component bank registration."""
    bank = ComponentBank()
    
    comp = ComponentDefinition(name="test-comp", description="Test")
    bank.register("test-comp", comp)
    
    assert bank.get("test-comp") is not None
    assert len(bank.list_components()) > 0

def test_component_bank_export_schema():
    """Test component bank schema export."""
    schema = component_bank.export_schema()
    
    assert "components" in schema
    assert "card" in schema["components"]
    assert schema["components"]["card"]["name"] == "card"

# Task 12: Style & Prop Validation
def test_style_validator():
    """Test CSS style validator."""
    validator = StyleValidator()
    
    # Safe styles
    styles = {"color": "red", "font-size": "16px"}
    cleaned = validator.validate_style_dict(styles)
    assert len(cleaned) == 2
    
    # Unsafe styles removed
    unsafe = {"behavior": "expression(alert('xss'))", "color": "blue"}
    cleaned = validator.validate_style_dict(unsafe)
    assert "behavior" not in cleaned
    assert "color" in cleaned

def test_style_validator_blocks_js():
    """Test style validator blocks JavaScript."""
    validator = StyleValidator()
    
    assert validator.is_value_safe("red") == True
    assert validator.is_value_safe("javascript:alert('xss')") == False
    assert validator.is_value_safe("expression(eval())") == False

def test_prop_validator():
    """Test prop validation."""
    schema = {"name": "string", "age": "number", "active": "boolean"}
    props = {"name": "John", "age": 30, "active": True}
    
    validated = PropValidator.validate_props(props, schema)
    assert len(validated) == 3
    
    # Invalid types removed
    props_invalid = {"name": "John", "age": "not a number"}
    validated = PropValidator.validate_props(props_invalid, schema)
    assert "age" not in validated

# Task 13: WebSocket Transport Improvements
def test_resumable_transport():
    """Test session resumption."""
    transport = ResumableTransport()
    
    session_id = transport.create_session("client-1")
    assert session_id is not None
    assert transport.can_resume_session(session_id) == True
    
    # Track message
    seq = transport.track_message(session_id, "msg-1", {"data": "test"})
    assert seq == 0
    
    # Ack message
    transport.ack_message(session_id, seq)

def test_exponential_backoff():
    """Test exponential backoff strategy."""
    backoff = ExponentialBackoff(initial=1.0, max_delay=10.0, factor=2.0)
    
    delay1 = backoff.next_delay()
    assert delay1 == 1.0
    
    delay2 = backoff.next_delay()
    assert delay2 == 2.0
    
    delay3 = backoff.next_delay()
    assert delay3 == 4.0
    
    # Reset
    backoff.reset()
    assert backoff.next_delay() == 1.0

def test_ordered_message_buffer():
    """Test message ordering buffer."""
    buf = OrderedMessageBuffer()
    
    # Add out of order
    ordered = buf.add_message(1, "msg-1")
    assert len(ordered) == 0  # Out of order, not yet delivered
    
    ordered = buf.add_message(0, "msg-0")
    assert len(ordered) == 2  # Now msg-0 and msg-1 delivered in order
    assert ordered == ["msg-0", "msg-1"]

# Task 15: Devtools Panel
def test_devtools_panel():
    """Test devtools panel."""
    devtools = DevtoolsPanel(enabled=True)
    
    devtools.log_message("send", "ui.render", {"path": "/home"})
    devtools.log_action("btn-click", "completed")
    devtools.log_error("NOT_FOUND", "Resource not found")
    devtools.log_performance("render", 25.5)
    
    assert len(devtools.messages) == 4
    
    stats = devtools.get_stats()
    assert stats["messages_sent"] == 1
    assert stats["actions_processed"] == 1
    assert stats["errors"] == 1

def test_devtools_message_filtering():
    """Test devtools message filtering."""
    devtools = DevtoolsPanel(enabled=True)
    
    devtools.log_message("send", "ui.render", {})
    devtools.log_error("ERR", "error")
    devtools.log_performance("op", 10.0)
    
    errors = devtools.get_messages(category="error")
    assert len(errors) == 1
    
    all_msgs = devtools.get_messages()
    assert len(all_msgs) >= 3
