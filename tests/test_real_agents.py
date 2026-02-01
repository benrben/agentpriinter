"""Tests for real LangChain and LangGraph agent integration."""
import pytest
import asyncio
from agentprinter_fastapi.agent_adapters import (
    LangChainAgentAdapter,
    LangGraphAgentAdapter,
    AgentWebSocketBridge
)

class MockAgentExecutor:
    """Mock LangChain AgentExecutor for testing."""
    
    def invoke(self, input_data: dict, config: dict = None):
        """Mock invoke method."""
        return {
            "output": f"Processed: {input_data.get('input', 'no input')}"
        }

@pytest.mark.asyncio
async def test_langchain_adapter_run():
    """Test LangChain agent adapter execution."""
    events = []
    
    async def on_event(event):
        events.append(event)
    
    adapter = LangChainAgentAdapter(on_event)
    executor = MockAgentExecutor()
    
    input_data = {"input": "What is 2+2?"}
    result = await adapter.run_agent(executor, input_data)
    
    # Verify events were collected and match AgentEvent contract
    assert len(events) >= 1  # at least start
    assert events[0]["event"] == "start"
    # Last event should be finish
    assert any(e["event"] == "finish" for e in events)
    assert "Processed" in str(result)

@pytest.mark.asyncio
async def test_langchain_adapter_history():
    """Test execution history tracking."""
    async def on_event(event):
        pass
    
    adapter = LangChainAgentAdapter(on_event)
    executor = MockAgentExecutor()
    
    # Run multiple times
    await adapter.run_agent(executor, {"input": "query 1"})
    await adapter.run_agent(executor, {"input": "query 2"})
    
    history = adapter.get_history()
    assert len(history) == 2
    assert history[0]["input"]["input"] == "query 1"
    assert history[1]["input"]["input"] == "query 2"

@pytest.mark.asyncio
async def test_websocket_bridge_agent_events():
    """Test WebSocket bridge converts agent events to UI patches."""
    messages_sent = []
    
    async def send_message(msg):
        messages_sent.append(msg)
    
    bridge = AgentWebSocketBridge(send_message)
    
    # Simulate agent events
    await bridge.on_agent_event({
        "type": "agent.start",
        "input": {"query": "test"}
    })
    
    await bridge.on_agent_event({
        "type": "agent.tool_start",
        "tool": "calculator"
    })
    
    await bridge.on_agent_event({
        "type": "agent.result",
        "output": "42"
    })
    
    # Verify UI patches were sent
    assert len(messages_sent) > 0
    assert bridge.get_accumulated_output() == "\n42"
    assert bridge.get_state() == "idle"

@pytest.mark.asyncio
async def test_langgraph_adapter_mock():
    """Test LangGraph adapter with mock graph."""
    events = []
    
    async def on_event(event):
        events.append(event)
    
    adapter = LangGraphAgentAdapter(on_event)
    
    # Verify adapter setup
    assert adapter.get_history() == []
    assert adapter.node_outputs == {}

@pytest.mark.asyncio
async def test_agent_state_transitions():
    """Test agent state transitions in bridge."""
    async def send_message(msg):
        pass
    
    bridge = AgentWebSocketBridge(send_message)
    
    assert bridge.get_state() == "idle"
    
    await bridge.on_agent_event({"type": "agent.start"})
    assert bridge.get_state() == "running"
    
    await bridge.on_agent_event({"type": "agent.result", "output": "done"})
    assert bridge.get_state() == "idle"
    
    await bridge.on_agent_event({"type": "agent.error", "error": "failed"})
    assert bridge.get_state() == "error"
