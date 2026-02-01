import pytest
import asyncio
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from agentprinter_fastapi.router import manager, set_initial_page
from agentprinter_fastapi.schemas import Message, Page, ComponentNode

# Add parent directory to path to import examples
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from examples.backend_demo import app, demo_page


async def receive_json_with_timeout(websocket, timeout: float = 2.0):
    return await asyncio.wait_for(asyncio.to_thread(websocket.receive_json), timeout=timeout)

@pytest.mark.asyncio
async def test_demo_initial_ui():
    """Test that the demo app sends the correct initial UI."""
    client = TestClient(app)
    set_initial_page(demo_page)
    with client.websocket_connect("/ws") as websocket:
        # Hello
        data = await receive_json_with_timeout(websocket)
        assert data["type"] == "protocol.hello"
        
        # UI Render
        data = await receive_json_with_timeout(websocket)
        assert data["type"] == "ui.render"
        assert data["payload"]["path"] == "/"
        assert "CogniFlow Builder" in str(data["payload"])

@pytest.mark.asyncio
async def test_demo_agent_flow():
    """Test the full agent flow triggered by an action."""
    client = TestClient(app)
    set_initial_page(demo_page)
    with client.websocket_connect("/ws") as websocket:
        # Skip hello and render
        await receive_json_with_timeout(websocket)
        await receive_json_with_timeout(websocket)
        
        # Trigger agent
        websocket.send_json({
            "type": "user.action",
            "header": {"trace_id": "test-trace", "id": "1", "timestamp": "2024-01-01T00:00:00Z"},
            "payload": {"action_id": "run_agent", "trigger": "click", "target": "agent"}
        })
        
        # Receive events
        events = []
        print("\nWaiting for events...")
        for _ in range(20): # Increased limit
            try:
                data = await receive_json_with_timeout(websocket)
                print(f"Received: {data['type']} - {data.get('payload', {}).get('event')}")
                if data["type"] == "protocol.error":
                    print(f"Error payload: {data['payload']}")
                if data["type"] == "agent.event":
                    events.append(data["payload"]["event"])
                    if data["payload"]["event"] == "finish":
                        break
            except Exception as e:
                print(f"Error receiving: {e}")
                break
                
        print(f"Collected events: {events}")
        assert "start" in events
        assert "token" in events
        assert "tool_call" in events
        assert "tool_result" in events
        assert "finish" in events
