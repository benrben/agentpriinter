import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_ws():
    ws = AsyncMock()
    return ws

@pytest.mark.asyncio
async def test_connect_disconnect(mock_ws):
    from agentprinter_fastapi.manager import ConnectionManager
    manager = ConnectionManager()
    
    await manager.connect(mock_ws)
    assert mock_ws in manager.active_connections
    mock_ws.accept.assert_awaited_once()

    manager.disconnect(mock_ws)
    assert mock_ws not in manager.active_connections

@pytest.mark.asyncio
async def test_broadcast(mock_ws):
    from agentprinter_fastapi.manager import ConnectionManager
    manager = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    
    await manager.connect(ws1)
    await manager.connect(ws2)
    
    msg = {"type": "ping"}
    await manager.broadcast(msg)
    
    ws1.send_json.assert_awaited_with(msg)
    ws2.send_json.assert_awaited_with(msg)

@pytest.mark.asyncio
async def test_broadcast_removes_dead_clients():
    from agentprinter_fastapi.manager import ConnectionManager
    manager = ConnectionManager()
    
    dead_ws = AsyncMock()
    dead_ws.send_json.side_effect = Exception("Connection closed")
    
    live_ws = AsyncMock()
    
    await manager.connect(dead_ws)
    await manager.connect(live_ws)
    
    # Use patch logic (or just trust logic handles generic exceptions for now, 
    # but strictly we should check specific websocket exceptions if we imported fastapi.WebSocketDisconnect.
    # For now, simplistic check: broadcast shouldn't raise, and dead_ws should be removed)
    
    await manager.broadcast({"data": "test"})
    
    assert live_ws in manager.active_connections
    assert dead_ws not in manager.active_connections
    live_ws.send_json.assert_awaited()
