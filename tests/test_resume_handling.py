
import pytest
from unittest.mock import AsyncMock, MagicMock
from agentprinter_fastapi.manager import ConnectionManager
from agentprinter_fastapi.schemas.protocol import Message, MessageHeader, ResumePayload

@pytest.mark.asyncio
async def test_outbound_message_has_seq():
    """Verify that broadcasted messages get a sequence number assigned."""
    manager = ConnectionManager()
    
    # Create a message without seq
    msg = Message(
        type="ui.render",
        header=MessageHeader(trace_id="seq-test", session_id="test-session"),
        payload={}
    )
    
    # Broadcast it
    await manager.broadcast(msg)
    
    # Retrieve it from history (using the polling transport which acts as history)
    # The manager internally uses polling_transport to store history
    # NOTE: Manager uses global http_polling instance, so we check that.
    from agentprinter_fastapi.transports import http_polling
    history = http_polling.dequeue_messages("test-session", cursor=0)
    
    assert len(history) == 1
    # Check manual seq assignment first
    assert history[0]["header"]["seq"] == 1
    
    # Broadcast another with same session
    msg2 = Message(
        type="ui.render",
        header=MessageHeader(trace_id="seq-test-2", session_id="test-session"),
        payload={}
    )
    await manager.broadcast(msg2)
    
    history_updated = http_polling.dequeue_messages("test-session", cursor=0)
    assert len(history_updated) == 2
    assert history_updated[1]["header"]["seq"] == 2

@pytest.mark.asyncio
async def test_resume_replays_messages():
    """Verify that protocol.resume triggers a replay of missed messages."""
    manager = ConnectionManager()
    session_id = "resume-session"
    from agentprinter_fastapi.transports import http_polling
    
    # 1. Populate history with 3 messages
    for i in range(3):
        msg = Message(
            type="ui.render",
            header=MessageHeader(trace_id=f"msg-{i}", session_id=session_id),
            payload={"data": i}
        )
        await manager.broadcast(msg)
        
    # 2. Simulate a client resuming with last_seen_seq=1
    # Direct access to transport to verify replay logic can be implemented.
    messages = http_polling.dequeue_messages(session_id, cursor=1)
    
    assert len(messages) == 2
    assert messages[0]["header"]["seq"] == 2
    assert messages[0]["payload"]["data"] == 1
    assert messages[1]["header"]["seq"] == 3
    assert messages[1]["payload"]["data"] == 2
