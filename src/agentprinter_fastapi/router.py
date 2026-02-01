from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from uuid import uuid4
import logging
import asyncio

from .manager import ConnectionManager
from .schemas import Message, MessageHeader, ComponentNode, Page
from .actions import action_router

logger = logging.getLogger(__name__)

router = APIRouter()
manager = ConnectionManager() # Global connection manager for this module

_initial_page: Page | None = None

def set_initial_page(page: Page):
    global _initial_page
    _initial_page = page

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send Proof of Life (Hello)
        # We generate a session/trace ID for this connection
        trace_id = str(uuid4())
        
        hello_msg = Message(
            type="protocol.hello",
            header=MessageHeader(trace_id=trace_id),
            payload={
                "message": "Connected to AgentPrinter",
                "server": "agentprinter-fastapi"
            }
        )
        
        # Send using pydantic dump
        await websocket.send_json(hello_msg.model_dump(mode='json'))
        
        if _initial_page:
            render_msg = Message(
                type="ui.render",
                header=MessageHeader(trace_id=trace_id),
                payload=_initial_page.model_dump(mode='json')
            )
            await websocket.send_json(render_msg.model_dump(mode='json'))
        
        while True:
            # Wait for messages
            data = await websocket.receive_text()
            try:
                # Parse incoming message
                message = Message.model_validate_json(data)
                
                # Route user.action messages
                if message.type == "user.action":
                    try:
                        await action_router.handle_message(message, websocket)
                    except KeyError as e:
                        # Unknown action
                        error_msg = Message(
                            type="protocol.error",
                            header=MessageHeader(trace_id=message.header.trace_id),
                            payload={
                                "code": "unknown_action",
                                "message": str(e),
                                "retryable": False
                            }
                        )
                        await websocket.send_json(error_msg.model_dump(mode='json'))
                    except Exception as e:
                        # Handler error
                        logger.exception("Error in action handler")
                        error_msg = Message(
                            type="protocol.error",
                            header=MessageHeader(trace_id=message.header.trace_id),
                            payload={
                                "code": "handler_error",
                                "message": str(e),
                                "retryable": True
                            }
                        )
                        await websocket.send_json(error_msg.model_dump(mode='json'))
                
            except Exception as e:
                logger.warning(f"Failed to parse message: {data}. Error: {e}")
                error_msg = Message(
                    type="protocol.error",
                    header=MessageHeader(trace_id=trace_id),
                    payload={
                        "code": "invalid_message",
                        "message": "Failed to parse message envelope",
                        "details": str(e)
                    }
                )
                await websocket.send_json(error_msg.model_dump(mode='json'))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
