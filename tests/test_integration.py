from fastapi import FastAPI
from fastapi.testclient import TestClient
from agentprinter_fastapi.router import router

def create_app():
    app = FastAPI()
    app.include_router(router)
    return app

def test_walking_skeleton_flow():
    client = TestClient(create_app())
    
    with client.websocket_connect("/ws") as websocket:
        # 1. Expect Hello
        hello = websocket.receive_json()
        assert hello["type"] == "protocol.hello"
        
        # 2. Expect Render
        render = websocket.receive_json()
        assert render["type"] == "ui.render"
        assert "root" in render["payload"]
        assert render["payload"]["root"]["type"] == "container"
