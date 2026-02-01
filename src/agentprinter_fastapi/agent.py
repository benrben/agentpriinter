"""Agent streaming runner for sending agent events over WebSockets."""
from typing import AsyncGenerator, Any, Tuple
from .schemas.protocol import Message, MessageHeader
from .schemas.agent import AgentEvent

class AgentRunner:
    """Runs an agent generator and streams its events over a WebSocket."""
    
    async def run_stream(self, run_id: str, trace_id: str, websocket: Any, generator: AsyncGenerator[Tuple[str, Any], None]):
        """Consumes a generator yielding (event_type, data) and streams agent.event messages.
        
        Args:
            run_id: Unique ID for this agent run
            trace_id: Distributed tracing ID
            websocket: WebSocket connection to stream over
            generator: Async generator yielding (event_type, data) pairs
        """
        try:
            async for event_type, data in generator:
                event = AgentEvent(
                    run_id=run_id,
                    event=event_type, # type: ignore
                    data=data
                )
                
                message = Message(
                    type="agent.event",
                    header=MessageHeader(trace_id=trace_id),
                    payload=event.model_dump(mode='json')
                )
                
                await websocket.send_json(message.model_dump(mode='json'))
        except Exception as e:
            error_event = AgentEvent(
                run_id=run_id,
                event="error",
                data=str(e)
            )
            error_message = Message(
                type="agent.event",
                header=MessageHeader(trace_id=trace_id),
                payload=error_event.model_dump(mode='json')
            )
            await websocket.send_json(error_message.model_dump(mode='json'))
            
    async def run_simple_agent(self, run_id: str, trace_id: str, websocket: Any, text: str):
        """A simple mock agent that streams back tokens and then finishes."""
        async def simple_gen():
            yield "start", "Simple agent starting"
            for token in text.split():
                yield "token", token + " "
            yield "finish", "Simple agent done"
            
        await self.run_stream(run_id, trace_id, websocket, simple_gen())
