"""Tests for agent streaming system."""
import pytest
from agentprinter_fastapi.agent import AgentRunner
from agentprinter_fastapi.schemas.protocol import Message
import asyncio

@pytest.mark.asyncio
async def test_agent_runner_streams_events():
    """Test that AgentRunner sends agent.event messages over WebSocket."""
    runner = AgentRunner()
    
    # Mock WebSocket that records sent messages
    sent_messages = []
    class MockWebSocket:
        async def send_json(self, data):
            sent_messages.append(data)
            
    ws = MockWebSocket()
    
    # Simple generator that simulates agent steps
    async def mock_agent():
        yield "start", "Agent starting"
        yield "token", "H"
        yield "token", "ello"
        yield "finish", "Agent done"
        
    trace_id = "test-trace"
    run_id = "run-123"
    
    await runner.run_stream(run_id, trace_id, ws, mock_agent())
    
    # Verify messages
    assert len(sent_messages) == 4
    
    # Check start message
    msg1 = sent_messages[0]
    assert msg1["type"] == "agent.event"
    assert msg1["header"]["trace_id"] == trace_id
    assert msg1["payload"]["run_id"] == run_id
    assert msg1["payload"]["event"] == "start"
    assert msg1["payload"]["data"] == "Agent starting"
    
    # Check tokens
    assert sent_messages[1]["payload"]["event"] == "token"
    assert sent_messages[1]["payload"]["data"] == "H"
    assert sent_messages[2]["payload"]["event"] == "token"
    assert sent_messages[2]["payload"]["data"] == "ello"
    
    # Check finish
    assert sent_messages[3]["payload"]["event"] == "finish"

@pytest.mark.asyncio
async def test_agent_runner_handles_error():
    """Test that AgentRunner sends agent.event with event='error' on exception."""
    runner = AgentRunner()
    
    sent_messages = []
    class MockWebSocket:
        async def send_json(self, data):
            sent_messages.append(data)
            
    async def failing_agent():
        yield "start", "Starting before disaster"
        raise ValueError("Something went wrong")
        
    await runner.run_stream("run-err", "trace-err", MockWebSocket(), failing_agent())
    
    assert len(sent_messages) == 2
    assert sent_messages[1]["payload"]["event"] == "error"
    assert "Something went wrong" in str(sent_messages[1]["payload"]["data"])
