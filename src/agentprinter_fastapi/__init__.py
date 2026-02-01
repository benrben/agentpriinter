from .router import router, manager

def hello() -> str:
    return "Hello from agentprinter-fastapi!"

__all__ = ["router", "manager", "hello"]
