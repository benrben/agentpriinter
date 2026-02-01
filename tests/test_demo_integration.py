import pytest
import asyncio
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from agentprinter_fastapi.router import manager, set_initial_page
from agentprinter_fastapi.schemas import Message, Page, ComponentNode

# Add parent directory to path to import examples
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from examples.backend_demo import app

def test_demo_initial_ui():
    """Test that the demo app sends the correct initial UI."""
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # Hello
        data = websocket.receive_json()
        assert data["type"] == "protocol.hello"
        
        # UI Render
        data = websocket.receive_json()
        assert data["type"] == "ui.render"
        assert data["payload"]["path"] == "/"
        assert "CogniFlow Builder" in str(data["payload"])

@pytest.mark.asyncio
async def test_demo_agent_flow():
    """Test the full agent flow triggered by an action."""
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # Skip hello and render
        websocket.receive_json()
        websocket.receive_json()
        
        # Trigger agent
        websocket.send_json({
            "type": "user.action",
            "header": {"trace_id": "test-trace", "id": "1", "timestamp": "2024-01-01T00:00:00Z"},
            "payload": {"action_id": "run_agent"}
        })
        
        # Receive events
        events = []
        print("\nWaiting for events...")
        for _ in range(20): # Increased limit
            try:
                data = websocket.receive_json()
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
