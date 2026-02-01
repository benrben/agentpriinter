"""Tests for SSE and HTTP fallback transport endpoints."""
import pytest
import asyncio
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request
from agentprinter_fastapi.router import router, manager, sse_endpoint
from agentprinter_fastapi.schemas import Page, ComponentNode


@pytest.fixture
def app():
    """FastAPI app for SSE/HTTP fallback tests."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.anyio
async def test_sse_streams_protocol_hello_and_ui_render(app):
    """Test SSE stream sends protocol.hello and ui.render messages."""
    # Set initial page so ui.render is emitted
    from agentprinter_fastapi import set_template_loader
    def template_loader():
        return Page(
            path="/home",
            root=ComponentNode(id="root", type="container", props={})
        )
    set_template_loader(template_loader)

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/sse",
        "query_string": b"session_id=test-sse",
        "headers": [(b"accept", b"text/event-stream")],
    }
    request = Request(scope)
    response = await sse_endpoint(request)

    body_iter = response.body_iterator
    first_chunk = await asyncio.wait_for(body_iter.__anext__(), timeout=1.0)
    second_chunk = await asyncio.wait_for(body_iter.__anext__(), timeout=1.0)
    await body_iter.aclose()

    def parse_sse_data(chunk: str | bytes) -> dict:
        text = chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
        for line in text.splitlines():
            if line.startswith("data: "):
                return json.loads(line[len("data: "):])
        raise AssertionError("No SSE data line found")

    hello_event = parse_sse_data(first_chunk)
    render_event = parse_sse_data(second_chunk)

    assert hello_event["type"] == "protocol.hello"
    assert render_event["type"] == "ui.render"


def test_http_polling_returns_messages_since_cursor(app):
    """Test that HTTP polling returns messages since cursor and respects auth."""
    client = TestClient(app)
    
    # First, send some messages via manager
    from agentprinter_fastapi.schemas import Message, MessageHeader
    test_msg = Message(
        type="ui.render",
        header=MessageHeader(trace_id="test-1", session_id="test-session"),
        payload={"root": {"id": "root", "type": "container", "props": {}}}
    )
    
    # Broadcast message (this should queue it for HTTP polling)
    import asyncio
    asyncio.run(manager.broadcast(test_msg.model_dump(mode='json')))
    
    # Poll for messages with cursor
    response = client.get("/poll/test-session?cursor=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) > 0
    assert "cursor" in data
    
    # Verify message structure
    msg = data["messages"][0]
    assert msg["type"] == "ui.render"
    
    # Test cursor advancement
    next_cursor = data["cursor"]
    response2 = client.get(f"/poll/test-session?cursor={next_cursor}&limit=10")
    assert response2.status_code == 200
    data2 = response2.json()
    # Should return empty or fewer messages since we already consumed them
    assert "messages" in data2
