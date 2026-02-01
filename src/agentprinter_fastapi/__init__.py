from .router import router, manager, set_auth_hook, set_initial_page, set_template_loader, set_version_negotiation, set_max_message_size

def hello() -> str:
    return "Hello from agentprinter-fastapi!"

__all__ = ["router", "manager", "set_auth_hook", "set_initial_page", "set_template_loader", "set_version_negotiation", "set_max_message_size", "hello"]
