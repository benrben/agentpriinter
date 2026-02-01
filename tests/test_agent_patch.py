from typing import Literal
import pytest

def test_agent_event_structure():
    try:
        from agentprinter_fastapi.schemas.agent import AgentEvent
    except ImportError:
        pytest.fail("Could not import AgentEvent")

    event = AgentEvent(
        run_id="run-1",
        event="token",
        data="hello"
    )
    assert event.event == "token"

def test_state_patch_structure():
    try:
        from agentprinter_fastapi.schemas.patch import StatePatch
    except ImportError:
        pytest.fail("Could not import StatePatch")
        
    patch = StatePatch(
        op="replace",
        path="/user/name",
        value="Ben",
        version=101
    )
    assert patch.op == "replace"
    assert patch.version == 101

def test_state_patch_invalid_op():
    from pydantic import ValidationError
    try:
        from agentprinter_fastapi.schemas.patch import StatePatch
    except ImportError:
        pytest.fail("Import failed")
        
    with pytest.raises(ValidationError):
        StatePatch(op="destroy", path="/", value=None, version=1)
