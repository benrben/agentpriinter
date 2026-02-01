# STDD Session: Protocol Sequencing & Resume Contract

## Context Snapshot
- **Goal**: Add explicit sequencing (`seq`) and resume contract (`ResumePayload`) to the protocol schema to decouple ordering/resume from protocol version negotiation.
- **Relevant Scopes**:
  - [Scopes/Product/Contracts/Protocol_Schema.md](../../Product/Contracts/Protocol_Schema.md)
  - [Scopes/Work/Tasks/2026-02-01-protocol-seq-and-resume-contract.md](../Tasks/2026-02-01-protocol-seq-and-resume-contract.md)
- **Code Standards**: [Scopes/Work/Standards/WRITE_STYLE.md](../Standards/WRITE_STYLE.md)

## Working Memory

### Short-Term (Now)
- **Active Scenario**: Define `seq` in `MessageHeader` and `ResumePayload` contract.
- **Focused Command**: `cd agentprinter-fastapi && uv run pytest tests/test_contracts_update.py`
- **Last Signal (Observed)**: N/A (Starting)
- **Hypothesis**: New test will fail because fields/models do not exist.
- **Next Micro-step**: Write failing test `tests/test_contracts_update.py`.

### Long-Term (Track)
- **Definition of Done**:
  - [ ] `MessageHeader.seq` exists.
  - [ ] `ResumePayload` exists.
  - [ ] Schema export includes these.
  - [ ] Frontend codegen runs successfully.
  - [ ] Tests pass.
- **Constraints from Scopes**:
  - `seq` is optional for backward compatibility.
  - Minimal changes.
- **Decisions**:
  - Use `seq` (integer) for monotonic ordering.
  - Use `ResumePayload` for resume arguments.

## Parking Lot
- [ ] Backend implementation of resume logic (Task 2).
- [ ] Frontend implementation of resume logic (Task 3).

## Test List (The Plan)
- [x] Scenario 1: Verify `MessageHeader` has `seq` and `ResumePayload` exists and validates correctly.

## Execution Log

### Cycle 1: Protocol Contract Updates
- **RED**: `tests/test_contracts_update.py`
  - *Outcome*: Failed as expected (AttributeError: 'MessageHeader' object has no attribute 'seq').
- **GREEN**: `agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py`
  - *Outcome*: Added `seq` and `ResumePayload`. Updated `export_schema.py`.
- **REFACTOR**: Added new test coverage to `tests/test_schemas.py` and removed temp test.
- **SCOPE UPDATE**: Updated `Scopes/Product/Contracts/Protocol_Schema.md` with new fields and evidence.
#### Micro-steps
1) Edit: Added `tests/test_contracts_update.py` to assert missing fields.
   - Rerun: `pytest tests/test_contracts_update.py` → Fail.
2) Edit: Added `seq` and `ResumePayload` to `protocol.py`.
   - Rerun: `pytest tests/test_contracts_update.py` → Pass.
3) Edit: Updated `export_schema.py` and `__init__.py` to export new types.
   - Rerun: `python scripts/export_schema.py` → Success.
4) Edit: Frontend Codegen.
   - Rerun: `bun run codegen` → Success.
5) Edit: Added permanent test to `test_schemas.py`.
   - Rerun: `uv run pytest` → All Pass.
