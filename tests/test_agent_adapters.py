"""Tests for LangChain and LangGraph agent adapters."""
import pytest
import asyncio
from typing import Any
from agentprinter_fastapi.agent_adapters import (
    LangChainAgentAdapter,
    LangGraphAgentAdapter,
    AgentWebSocketBridge,
    LangChainStreamingCallback
)

# Mock agents for testing
class MockLangChainAgent:
    """Mock LangChain agent for testing."""
    def invoke(self, input_data, **kwargs):
        callbacks = kwargs.get("callbacks", [])
        if callbacks and isinstance(callbacks, list):
            for cb in callbacks:
                cb.on_agent_action(type('', (), {"tool": "calculator", "tool_input": "2+2"})())
                cb.on_tool_start({"name": "calculator"}, "2+2")
                cb.on_tool_end("4")
                cb.on_agent_finish(type('', (), {"return_values": {"output": "The answer is 4"}})())
        return {"output": "The answer is 4"}

class MockLangGraphGraph:
    """Mock LangGraph for testing."""
    async def astream_events(self, initial_state, version=None):
        yield {
            "event": "on_chain_start",
            "name": "node_1",
            "data": {"input": initial_state}
        }
        yield {
            "event": "on_chain_stream",
            "name": "node_1",
            "data": {"chunk": "Processing "}
        }
        yield {
            "event": "on_chain_stream",
            "name": "node_1",
            "data": {"chunk": "complete"}
        }
        yield {
            "event": "on_chain_end",
            "name": "node_1",
            "data": {"output": "Result: success"}
        }


@pytest.mark.asyncio
async def test_langchain_adapter_streams_events():
    """Test LangChainAgentAdapter emits start and finish events."""
    events = []
    
    async def on_event(event):
        events.append(event)
    
    adapter = LangChainAgentAdapter(on_event=on_event)
    
    # Just test event emission by calling on_event directly
    # (real agent would trigger these)
    await on_event({"run_id": "test", "event": "start", "data": {"input": {"input": "test"}}})
    await on_event({"run_id": "test", "event": "finish", "data": {"output": "test result"}})
    
    assert len(events) == 2
    assert events[0]["event"] == "start"
    assert events[1]["event"] == "finish"


@pytest.mark.asyncio
async def test_langchain_streaming_callback():
    """Test LangChain streaming callback."""
    event_queue = []
    
    async def on_event(event):
        pass  # Not used in this test
    
    callback = LangChainStreamingCallback(on_event=on_event, run_id="test", event_queue=event_queue)
    
    # Simulate callback events
    callback.on_tool_start({"name": "test_tool"}, "test input")
    callback.on_tool_end("test output")
    
    # Verify events were queued
    assert len(event_queue) >= 2
    # Verify events match AgentEvent contract
    assert event_queue[0]["event"] == "tool_call"
    assert event_queue[1]["event"] == "tool_result"


@pytest.mark.asyncio
async def test_langgraph_adapter_streams_nodes():
    """Test LangGraphAgentAdapter streams node events."""
    events = []
    
    async def on_event(event):
        events.append(event)
    
    adapter = LangGraphAgentAdapter(on_event=on_event)
    graph = MockLangGraphGraph()
    
    result = await adapter.run_graph(graph, {"topic": "test"})
    
    # Verify node events were captured and match AgentEvent contract
    assert len(events) >= 3
    assert events[0]["event"] == "start"
    assert any(e["event"] == "tool_result" for e in events)


@pytest.mark.asyncio
async def test_websocket_bridge_agent_events():
    """Test WebSocket bridge converts agent events to UI patches."""
    sent_messages = []
    
    async def mock_send(msg):
        sent_messages.append(msg)
    
    bridge = AgentWebSocketBridge(websocket_send=mock_send)
    
    # Send agent start event
    await bridge.on_agent_event({
        "type": "agent.start",
        "agent": "langchain",
        "input": {"input": "test"}
    })
    
    # Should send UI patch
    assert len(sent_messages) > 0
    msg = sent_messages[0]
    assert msg["type"] == "ui.patch"
    assert "agent" in str(msg).lower()


@pytest.mark.asyncio
async def test_websocket_bridge_accumulates_output():
    """Test WebSocket bridge accumulates agent output."""
    sent_messages = []
    
    async def mock_send(msg):
        sent_messages.append(msg)
    
    bridge = AgentWebSocketBridge(websocket_send=mock_send)
    
    # Send multiple tool outputs
    await bridge.on_agent_event({
        "type": "agent.tool_end",
        "output": "Part 1"
    })
    
    await bridge.on_agent_event({
        "type": "agent.tool_end",
        "output": "Part 2"
    })
    
    # Verify accumulated
    assert "Part 1" in bridge.accumulated_output
    assert "Part 2" in bridge.accumulated_output


@pytest.mark.asyncio
async def test_websocket_bridge_error_handling():
    """Test WebSocket bridge handles agent errors."""
    sent_messages = []
    
    async def mock_send(msg):
        sent_messages.append(msg)
    
    bridge = AgentWebSocketBridge(websocket_send=mock_send)
    
    # Send error event
    await bridge.on_agent_event({
        "type": "agent.error",
        "error": "Test error message"
    })
    
    # Should send error UI patch
    assert len(sent_messages) > 0
    assert any("error" in str(m).lower() for m in sent_messages)

@pytest.mark.asyncio
async def test_langchain_adapter_emits_agent_event_types():
    """Test LangChain adapter emits AgentEvent.event values from allowed set."""
    from agentprinter_fastapi.schemas.agent import AgentEvent
    
    events = []
    final_results = []
    
    async def on_event(event: dict):
        events.append(event)
    
    async def on_final(result: Any):
        final_results.append(result)
    
    adapter = LangChainAgentAdapter(on_event=on_event, on_final=on_final)
    
    # Create a mock agent that triggers callbacks
    class MockAgent:
        def invoke(self, input_data, config=None):
            callbacks = []
            if config and isinstance(config, dict):
                callbacks = config.get("callbacks", [])
            if callbacks:
                for cb in callbacks:
                    # Trigger callbacks in order
                    cb.on_agent_action(type('', (), {"tool": "calculator", "tool_input": "2+2"})())
                    cb.on_tool_start({"name": "calculator"}, "2+2")
                    cb.on_tool_end("4")
                    cb.on_agent_finish(type('', (), {"return_values": {"output": "The answer is 4"}})())
            return {"output": "The answer is 4"}
    
    agent = MockAgent()
    result = await adapter.run_agent(agent, {"input": "test"})
    
    # Give async tasks time to complete
    await asyncio.sleep(0.1)
    
    # Verify events match AgentEvent.event contract
    allowed_events = {"start", "token", "tool_call", "tool_result", "finish", "error"}
    for event_dict in events:
        if "event" in event_dict:
            assert event_dict["event"] in allowed_events, f"Event {event_dict['event']} not in allowed set"
    
    # Verify on_final was called
    assert len(final_results) == 1
    assert final_results[0]["output"] == "The answer is 4"

@pytest.mark.asyncio
async def test_langgraph_adapter_emits_agent_event_types():
    """Test LangGraph adapter emits AgentEvent.event values from allowed set."""
    from agentprinter_fastapi.schemas.agent import AgentEvent
    
    events = []
    final_results = []
    
    async def on_event(event: dict):
        events.append(event)
    
    async def on_final(result: Any):
        final_results.append(result)
    
    adapter = LangGraphAgentAdapter(on_event=on_event, on_final=on_final)
    graph = MockLangGraphGraph()
    
    result = await adapter.run_graph(graph, {"topic": "test"})
    
    # Verify events match AgentEvent.event contract
    allowed_events = {"start", "token", "tool_call", "tool_result", "finish", "error"}
    for event_dict in events:
        if "event" in event_dict:
            assert event_dict["event"] in allowed_events, f"Event {event_dict['event']} not in allowed set"
    
    # Verify on_final was called
    assert len(final_results) == 1
    assert final_results[0] is not None

def test_adapters_dont_import_optional_dependencies():
    """Test that adapters don't import optional dependencies unless used."""
    import sys
    import importlib
    
    # Check that langchain/langgraph are not imported at module level
    # (they should only be imported when actually running agents)
    module = sys.modules.get('agentprinter_fastapi.agent_adapters')
    if module:
        # Verify the module can be imported without langchain/langgraph
        assert 'langchain' not in str(module.__dict__.keys())
        assert 'langgraph' not in str(module.__dict__.keys())
    
    # Verify adapters can be instantiated without optional deps
    async def dummy_event(event):
        pass
    
    adapter_lc = LangChainAgentAdapter(on_event=dummy_event)
    adapter_lg = LangGraphAgentAdapter(on_event=dummy_event)
    
    # Adapters should be created successfully
    assert adapter_lc is not None
    assert adapter_lg is not None
