# STDD Session: Backend Sequencing & Resume Handle

## Context Snapshot
- **Goal**: Implement `seq` assignment for outbound messages and handle `protocol.resume` to replay missed messages.
- **Relevant Scopes**:
  - [Scopes/Product/Backend/WebSocket_Runtime.md](../../Product/Backend/WebSocket_Runtime.md)
  - [Scopes/Work/Tasks/2026-02-01-backend-assign-seq-and-handle-resume.md](../Tasks/2026-02-01-backend-assign-seq-and-handle-resume.md)
- **Code Standards**: [Scopes/Work/Standards/WRITE_STYLE.md](../Standards/WRITE_STYLE.md)

## Working Memory

### Short-Term (Now)
- **Active Scenario**: 1. Assign `seq` to outbound messages. 2. Handle `protocol.resume`.
- **Focused Command**: `cd agentprinter-fastapi && uv run pytest tests/test_resume_handling.py`
- **Last Signal (Observed)**: N/A
- **Hypothesis**: N/A
- **Next Micro-step**: Write failing test for `seq` assignment and resume handling.

### Long-Term (Track)
- **Definition of Done**:
  - [ ] Outbound messages have `seq`.
  - [ ] `protocol.resume` triggers replay of messages > `last_seen_seq`.
  - [ ] Replay uses stored history from `HTTPPollingTransport`.
- **Constraints**:
  - Reuse `HTTPPollingTransport` memory queue as source of truth.
  - Keep it simple.

## Parking Lot
- [ ] Frontend integration (Task 3).

## Test List (The Plan)
- [x] Scenario 1: Verify outbound messages have monotonic `seq`.
- [x] Scenario 2: Verify `protocol.resume` replays missed messages.

## Execution Log

### Cycle 2: Backend Resume Support
- **RED**: `tests/test_resume_handling.py`
  - *Outcome*: Failed as expected (TypeError: broadcast got unexpected arg; then AssertionError on seq check).
- **GREEN**: 
  - Updated `agentprinter-fastapi/src/agentprinter_fastapi/manager.py` to stamp `seq` using `http_polling` queue length.
  - Updated `agentprinter-fastapi/src/agentprinter_fastapi/router.py` to handle `protocol.resume` and trigger replay.
- **REFACTOR**: Updated `tests/test_resume_handling.py` to use correct broadcast signature and session id.
- **SCOPE UPDATE**: Updated `Scopes/Product/Backend/WebSocket_Runtime.md` with new use case and trace.
#### Micro-steps
1) Edit: Created `tests/test_resume_handling.py` with failing assertions.
   - Rerun: `pytest tests/test_resume_handling.py` → Fail.
2) Edit: Implemented `seq` assignment in `ConnectionManager`.
   - Rerun: `pytest tests/test_resume_handling.py` → Fail (TypeError in test).
3) Edit: Fixed test case arguments.
   - Rerun: `pytest tests/test_resume_handling.py` → Pass.
4) Edit: Implemented `protocol.resume` handler in `router.py`.
   - Rerun: `pytest tests/test_resume_handling.py` → Pass.
5) Edit: Full backend test run.
   - Rerun: `uv run pytest` → All Pass.
