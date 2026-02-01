"""Real LangChain and LangGraph agent integrations with WebSocket streaming."""
import asyncio
import json
from typing import AsyncGenerator, Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LangChainAgentAdapter:
    """Adapter for real LangChain agents with streaming to WebSocket."""
    
    def __init__(self, on_event: Callable[[dict], None], on_final: Optional[Callable[[Any], None]] = None):
        """Initialize with callbacks for agent events and final result.
        
        Args:
            on_event: Async callback for agent events (emits AgentEvent-compliant events)
            on_final: Optional async callback called once with final result
        """
        self.on_event = on_event
        self.on_final = on_final
        self.history = []
        self._run_id = None
    
    async def run_agent(self, agent_executor: Any, input_data: dict) -> dict:
        """Run a real LangChain agent and stream events.
        
        Args:
            agent_executor: LangChain AgentExecutor instance
            input_data: Input dict for agent (e.g., {"input": "What is 2+2?"})
            
        Returns:
            Final agent result
        """
        import uuid
        self._run_id = str(uuid.uuid4())
        
        try:
            # Emit start event (AgentEvent.event = "start")
            await self.on_event({
                "run_id": self._run_id,
                "event": "start",
                "data": {"input": input_data}
            })
            
            # Event queue for callbacks (callbacks run in sync context)
            event_queue = []
            
            # Configure agent for streaming callbacks
            callbacks = [LangChainStreamingCallback(self.on_event, self._run_id, event_queue)]
            
            # Run agent (this will trigger callbacks)
            result = await asyncio.to_thread(
                agent_executor.invoke,
                input_data,
                {"callbacks": callbacks}
            )
            
            # Process queued events
            for event in event_queue:
                await self.on_event(event)
            
            final_output = result.get("output", "")
            
            # Emit finish event if not already emitted by callback
            if not any(e.get("event") == "finish" for e in event_queue):
                await self.on_event({
                    "run_id": self._run_id,
                    "event": "finish",
                    "data": {"output": final_output}
                })
            
            # Call on_final hook if provided
            if self.on_final:
                await self.on_final(result)
            
            # Track in history
            self.history.append({
                "input": input_data,
                "output": final_output,
                "status": "success"
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Agent error: {e}")
            # Emit error event (AgentEvent.event = "error")
            await self.on_event({
                "run_id": self._run_id,
                "event": "error",
                "data": {"error": str(e)}
            })
            # Track error in history
            self.history.append({
                "input": input_data,
                "status": "error",
                "error": str(e)
            })
            raise
    
    def get_history(self):
        """Return the history of all agent invocations."""
        return self.history

class LangChainStreamingCallback:
    """Callback handler for LangChain agent streaming."""
    
    def __init__(self, on_event: Callable, run_id: str, event_queue: list):
        self.on_event = on_event
        self.run_id = run_id
        self.event_queue = event_queue
    
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        """Called when agent calls a tool."""
        self.event_queue.append({
            "run_id": self.run_id,
            "event": "tool_call",
            "data": {
                "tool": serialized.get("name", "unknown"),
                "input": input_str
            }
        })
    
    def on_tool_end(self, output: str, **kwargs):
        """Called when tool returns result."""
        self.event_queue.append({
            "run_id": self.run_id,
            "event": "tool_result",
            "data": {"output": output}
        })
    
    def on_agent_action(self, action: Any, **kwargs):
        """Called for each agent action."""
        self.event_queue.append({
            "run_id": self.run_id,
            "event": "tool_call",
            "data": {
                "tool": action.tool if hasattr(action, "tool") else "unknown",
                "tool_input": action.tool_input if hasattr(action, "tool_input") else {}
            }
        })
    
    def on_agent_finish(self, finish: Any, **kwargs):
        """Called when agent finishes."""
        self.event_queue.append({
            "run_id": self.run_id,
            "event": "finish",
            "data": {"output": finish.return_values.get("output", "") if hasattr(finish, "return_values") else ""}
        })

class LangGraphAgentAdapter:
    """Adapter for real LangGraph state graphs with streaming to WebSocket."""
    
    def __init__(self, on_event: Callable[[dict], None], on_final: Optional[Callable[[Any], None]] = None):
        """Initialize with callbacks for graph events and final result.
        
        Args:
            on_event: Async callback for graph events (emits AgentEvent-compliant events)
            on_final: Optional async callback called once with final state
        """
        self.on_event = on_event
        self.on_final = on_final
        self.history = []
        self.node_outputs = {}
        self._run_id = None
    
    async def run_graph(self, graph: Any, initial_state: dict) -> dict:
        """Run a real LangGraph state graph and stream node events.
        
        Args:
            graph: Compiled LangGraph StateGraph
            initial_state: Initial state dict
            
        Returns:
            Final graph state
        """
        import uuid
        self._run_id = str(uuid.uuid4())
        
        try:
            # Emit start event (AgentEvent.event = "start")
            await self.on_event({
                "run_id": self._run_id,
                "event": "start",
                "data": {"initial_state": initial_state}
            })
            
            # Stream graph execution
            final_state = None
            async for event in graph.astream_events(initial_state, version="v1"):
                event_type = event.get("event")
                
                if event_type == "on_chain_start":
                    node_name = event.get("name")
                    await self.on_event({
                        "run_id": self._run_id,
                        "event": "tool_call",
                        "data": {
                            "node": node_name,
                            "data": event.get("data", {})
                        }
                    })
                
                elif event_type == "on_chain_stream":
                    chunk = event.get("data", {}).get("chunk", "")
                    if chunk:
                        await self.on_event({
                            "run_id": self._run_id,
                            "event": "token",
                            "data": chunk
                        })
                
                elif event_type == "on_chain_end":
                    node_name = event.get("name")
                    output = event.get("data", {}).get("output")
                    self.node_outputs[node_name] = output
                    await self.on_event({
                        "run_id": self._run_id,
                        "event": "tool_result",
                        "data": {
                            "node": node_name,
                            "output": output
                        }
                    })
                    final_state = output
            
            # Emit finish event (AgentEvent.event = "finish")
            await self.on_event({
                "run_id": self._run_id,
                "event": "finish",
                "data": {"final_state": final_state}
            })
            
            # Call on_final hook if provided
            if self.on_final:
                await self.on_final(final_state or initial_state)
            
            # Track in history
            self.history.append({
                "initial_state": initial_state,
                "final_state": final_state,
                "status": "success"
            })
            
            return final_state or initial_state
            
        except Exception as e:
            logger.error(f"Graph error: {e}")
            # Emit error event (AgentEvent.event = "error")
            await self.on_event({
                "run_id": self._run_id,
                "event": "error",
                "data": {"error": str(e)}
            })
            # Track error in history
            self.history.append({
                "initial_state": initial_state,
                "status": "error",
                "error": str(e)
            })
            raise
    
    def get_history(self):
        """Return the history of all graph invocations."""
        return self.history

class AgentWebSocketBridge:
    """Bridge between agent events and WebSocket UI updates."""
    
    def __init__(self, websocket_send: Callable):
        """Initialize with WebSocket send callback.
        
        Args:
            websocket_send: Async function to send messages over WebSocket
        """
        self.websocket_send = websocket_send
        self.accumulated_output = ""
        self.state = "idle"  # idle, running, error
    
    async def on_agent_event(self, event: dict):
        """Handle agent event and convert to UI updates.
        
        Args:
            event: Agent event dict (type, data, etc)
        """
        event_type = event.get("type", "")
        
        # Convert agent events to UI patches
        if event_type == "agent.start":
            self.state = "running"
            await self._send_ui_patch({
                "target": "agent_output",
                "operation": "clear"
            })
            await self._send_ui_patch({
                "target": "agent_status",
                "text": "🔄 Agent running...",
                "operation": "update_props"
            })
        
        elif event_type == "agent.tool_start":
            tool = event.get("tool", "")
            await self._send_ui_patch({
                "target": "agent_status",
                "text": f"🔧 Using tool: {tool}",
                "operation": "update_props"
            })
        
        elif event_type == "agent.tool_end":
            output = event.get("output", "")
            self.accumulated_output += f"\n{output}"
            await self._send_ui_patch({
                "target": "agent_output",
                "text": output,
                "operation": "append"
            })
        
        elif event_type == "agent.result":
            output = event.get("output", "")
            self.accumulated_output += f"\n{output}"
            self.state = "idle"
            await self._send_ui_patch({
                "target": "agent_output",
                "text": output,
                "operation": "append"
            })
            await self._send_ui_patch({
                "target": "agent_status",
                "text": "✅ Agent completed",
                "operation": "update_props"
            })
        
        elif event_type == "agent.error":
            error = event.get("error", "Unknown error")
            self.state = "error"
            await self._send_ui_patch({
                "target": "agent_output",
                "text": f"❌ Error: {error}",
                "operation": "append"
            })
            await self._send_ui_patch({
                "target": "agent_status",
                "text": "❌ Agent failed",
                "operation": "update_props"
            })
        
        # LangGraph events
        elif event_type == "graph.node_stream":
            output = event.get("output", "")
            self.accumulated_output += output
            await self._send_ui_patch({
                "target": "agent_output",
                "text": output,
                "operation": "append"
            })
        
        elif event_type == "graph.node_end":
            node = event.get("node", "")
            await self._send_ui_patch({
                "target": "agent_status",
                "text": f"✓ {node} completed",
                "operation": "update_props"
            })
    
    async def _send_ui_patch(self, patch_data: dict):
        """Send a UI patch to the WebSocket client.
        
        Args:
            patch_data: Patch operation dict
        """
        from agentprinter_fastapi.schemas import Message, MessageHeader
        
        patch_msg = Message(
            type="ui.patch",
            header=MessageHeader(trace_id="agent-stream"),
            payload=patch_data
        )
        
        await self.websocket_send(patch_msg.model_dump(mode='json'))
    
    def get_accumulated_output(self) -> str:
        """Return accumulated output from agent events."""
        return self.accumulated_output
    
    def get_state(self) -> str:
        """Return current state (idle, running, error)."""
        return self.state
