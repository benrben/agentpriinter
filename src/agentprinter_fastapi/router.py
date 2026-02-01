from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.responses import StreamingResponse
from uuid import uuid4
import logging
import asyncio
import json
from typing import Any

from .manager import ConnectionManager
from .schemas import Message, MessageHeader, ComponentNode, Page, ErrorPayload
from .actions import action_router
from .actions import InvalidActionPayloadError
from .transports import sse_transport, http_polling, router as transports_router

logger = logging.getLogger(__name__)

def make_protocol_error(trace_id: str, code: str, message: str, details: dict[str, Any] | None = None) -> Message:
    """Build a protocol.error message that conforms to ErrorPayload schema.
    
    Args:
        trace_id: Distributed trace ID
        code: Error code (e.g., auth_failed, unknown_action, handler_error, invalid_message)
        message: Human-readable error message
        details: Additional error context (defaults to empty dict)
    
    Returns:
        Message with validated ErrorPayload
    """
    if details is None:
        details = {}
    
    error_payload = ErrorPayload(code=code, message=message, details=details)
    return Message(
        type="protocol.error",
        header=MessageHeader(trace_id=trace_id),
        payload=error_payload.model_dump(mode='json')
    )

router = APIRouter()
router.include_router(transports_router)  # Include SSE/HTTP fallback endpoints
manager = ConnectionManager() # Global connection manager for this module

_initial_page: Page | None = None
_auth_hook = None  # Optional auth hook function
_template_loader = None  # Optional template loader function
_version_negotiation_hook = None  # Optional version negotiation hook function
_max_message_size: int | None = None  # Optional max message size in bytes

def set_initial_page(page: Page):
    global _initial_page
    _initial_page = page

def set_auth_hook(hook):
    """Set an optional auth hook function that receives websocket scope."""
    global _auth_hook
    _auth_hook = hook

def set_template_loader(loader):
    """Set an optional template loader function that returns a Page."""
    global _template_loader
    _template_loader = loader

def set_version_negotiation(hook):
    """Set an optional version negotiation hook function that receives client version and returns negotiated version or None."""
    global _version_negotiation_hook
    _version_negotiation_hook = hook

def set_max_message_size(size: int | None):
    """Set maximum message size in bytes. None disables size checking."""
    global _max_message_size
    _max_message_size = size

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Check connection rate limit (only if explicitly configured)
    from .backpressure import connection_rate_limiter
    # Only enforce if rate is configured low (not default high value of 100)
    if connection_rate_limiter.rate < 100:
        connection_id = websocket.client.host if websocket.client and hasattr(websocket.client, 'host') else str(id(websocket))
        if not connection_rate_limiter.is_allowed(connection_id):
            trace_id = str(uuid4())
            error_msg = make_protocol_error(
                trace_id=trace_id,
                code="connection_rate_limit_exceeded",
                message="Connection rate limit exceeded"
            )
            await websocket.send_json(error_msg.model_dump(mode='json'))
            await websocket.close()
            manager.disconnect(websocket)
            return
    try:
        trace_id = str(uuid4())
        
        # Call auth hook if set
        if _auth_hook:
            auth_result = _auth_hook(websocket.scope)
            if not auth_result:
                error_msg = make_protocol_error(
                    trace_id=trace_id,
                    code="auth_failed",
                    message="Authentication failed"
                )
                await websocket.send_json(error_msg.model_dump(mode='json'))
                await websocket.close()
                return
        
        # Version negotiation
        negotiated_version = "1.0.0"  # Default version
        if _version_negotiation_hook:
            # Parse version from query string
            query_string = websocket.scope.get("query_string", b"").decode()
            client_version = None
            if query_string:
                params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
                client_version = params.get("version")
            
            if client_version:
                negotiated_version = _version_negotiation_hook(client_version)
                if negotiated_version is None:
                    error_msg = make_protocol_error(
                        trace_id=trace_id,
                        code="version_mismatch",
                        message=f"Protocol version mismatch. Client requested {client_version}, server does not support it."
                    )
                    await websocket.send_json(error_msg.model_dump(mode='json'))
                    await websocket.close()
                    return
        
        # Send Proof of Life (Hello)
        hello_msg = Message(
            type="protocol.hello",
            header=MessageHeader(trace_id=trace_id, version=negotiated_version),
            payload={
                "message": "Connected to AgentPrinter",
                "server": "agentprinter-fastapi"
            }
        )
        
        # Send using pydantic dump
        await websocket.send_json(hello_msg.model_dump(mode='json'))
        
        # Use template loader if available, otherwise use initial page
        page_to_send = None
        if _template_loader:
            page_to_send = _template_loader()
        elif _initial_page:
            page_to_send = _initial_page
        
        if page_to_send:
            render_msg = Message(
                type="ui.render",
                header=MessageHeader(trace_id=trace_id),
                payload=page_to_send.model_dump(mode='json')
            )
            await websocket.send_json(render_msg.model_dump(mode='json'))
        
        # Get client ID for rate limiting
        client_id = str(id(websocket))
        
        # Import rate limiter
        from .backpressure import rate_limiter
        
        while True:
            # Wait for messages
            data = await websocket.receive_text()
            
            # Check message size limit
            if _max_message_size is not None and len(data.encode('utf-8')) > _max_message_size:
                error_msg = make_protocol_error(
                    trace_id=trace_id,
                    code="message_too_large",
                    message=f"Message size {len(data.encode('utf-8'))} exceeds maximum {_max_message_size} bytes",
                    details={"size": len(data.encode('utf-8')), "max_size": _max_message_size}
                )
                await websocket.send_json(error_msg.model_dump(mode='json'))
                continue
            
            # Check rate limit for inbound messages
            if not rate_limiter.is_allowed(client_id):
                error_msg = make_protocol_error(
                    trace_id=trace_id,
                    code="rate_limit_exceeded",
                    message="Rate limit exceeded for inbound messages",
                    details={"remaining": rate_limiter.get_remaining(client_id)}
                )
                await websocket.send_json(error_msg.model_dump(mode='json'))
                continue
            
            try:
                # Parse incoming message
                message = Message.model_validate_json(data)
                
                # Route user.action messages
                if message.type == "user.action":
                    try:
                        await action_router.handle_message(message, websocket)
                    except InvalidActionPayloadError as e:
                        error_msg = make_protocol_error(
                            trace_id=message.header.trace_id,
                            code="invalid_action_payload",
                            message="Invalid user.action payload",
                            details={"issues": e.issues},
                        )
                        await websocket.send_json(error_msg.model_dump(mode="json"))
                    except KeyError as e:
                        # Unknown action
                        error_msg = make_protocol_error(
                            trace_id=message.header.trace_id,
                            code="unknown_action",
                            message=str(e)
                        )
                        await websocket.send_json(error_msg.model_dump(mode='json'))
                    except Exception as e:
                        # Handler error
                        logger.exception("Error in action handler")
                        error_msg = make_protocol_error(
                            trace_id=message.header.trace_id,
                            code="handler_error",
                            message=str(e)
                        )
                        await websocket.send_json(error_msg.model_dump(mode='json'))
                
                # Handle resume
                elif message.type == "protocol.resume":
                     current_session_id = message.header.session_id or "default"
                     last_seen_seq = message.payload.get("last_seen_seq")
                     
                     if last_seen_seq is not None:
                         # Replay messages
                         messages = http_polling.dequeue_messages(current_session_id, cursor=last_seen_seq, count=100)
                         for msg in messages:
                             await websocket.send_json(msg)
                
            except Exception as e:
                logger.warning(f"Failed to parse message: {data}. Error: {e}")
                error_msg = make_protocol_error(
                    trace_id=trace_id,
                    code="invalid_message",
                    message="Failed to parse message envelope",
                    details={"parse_error": str(e)}
                )
                await websocket.send_json(error_msg.model_dump(mode='json'))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")


@router.get("/sse")
async def sse_endpoint(request: Request):
    """Server-Sent Events endpoint for clients that can't use WebSocket."""
    import asyncio
    from fastapi import Query
    
    # Get session_id from query or generate one
    session_id = request.query_params.get("session_id", f"sse-{uuid4()}")
    
    # Auth check (reuse auth hook if available)
    if _auth_hook:
        # Create a mock scope for auth hook
        mock_scope = {
            "type": "http",
            "method": "GET",
            "path": "/sse",
            "query_string": request.url.query.encode() if request.url.query else b"",
            "headers": dict(request.headers),
        }
        auth_result = _auth_hook(mock_scope)
        if not auth_result:
            return Response(
                content=json.dumps({"error": "Authentication failed"}),
                status_code=401,
                media_type="application/json"
            )
    
    # Version negotiation
    negotiated_version = "1.0.0"
    if _version_negotiation_hook:
        client_version = request.query_params.get("version")
        if client_version:
            negotiated_version = _version_negotiation_hook(client_version)
            if negotiated_version is None:
                return Response(
                    content=json.dumps({"error": "Version mismatch"}),
                    status_code=400,
                    media_type="application/json"
                )
    
    async def event_generator():
        trace_id = str(uuid4())
        
        # Send protocol.hello
        hello_msg = Message(
            type="protocol.hello",
            header=MessageHeader(trace_id=trace_id, version=negotiated_version),
            payload={
                "message": "Connected to AgentPrinter via SSE",
                "server": "agentprinter-fastapi"
            }
        )
        yield f"data: {json.dumps(hello_msg.model_dump(mode='json'))}\n\n"
        
        # Send initial page if available
        page_to_send = None
        if _template_loader:
            page_to_send = _template_loader()
        elif _initial_page:
            page_to_send = _initial_page
        
        if page_to_send:
            render_msg = Message(
                type="ui.render",
                header=MessageHeader(trace_id=trace_id),
                payload=page_to_send.model_dump(mode='json')
            )
            yield f"data: {json.dumps(render_msg.model_dump(mode='json'))}\n\n"
        
        # Register client for future messages
        message_queue = asyncio.Queue()
        
        async def send_to_client(msg: dict):
            await message_queue.put(msg)
        
        sse_transport.register_client(session_id, send_to_client)
        
        try:
            # Keep connection alive and stream messages
            while True:
                try:
                    # Wait for message with timeout to keep connection alive
                    msg = await asyncio.wait_for(message_queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield ": keepalive\n\n"
        finally:
            # Cleanup
            if session_id in sse_transport.clients:
                sse_transport.clients[session_id].remove(send_to_client)
                if not sse_transport.clients[session_id]:
                    del sse_transport.clients[session_id]
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
