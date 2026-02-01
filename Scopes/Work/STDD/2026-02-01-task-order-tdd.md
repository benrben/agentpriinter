# STDD Session: Task Order Todo

## Context Snapshot
- **Goal**: Finish remaining 2026-02-01 task set (SSE streaming test, backpressure scope docs, prop validation test) and add test timeouts to avoid hangs.
- **Relevant Scopes**: [Backend WebSocket Runtime](../Product/Backend/WebSocket_Runtime.md), [Remote UI Runtime (React)](../Product/Frontend/Remote_UI_Runtime.md)
- **Code Standards**: [Scopes/Work/Standards/WRITE_STYLE.md](../Standards/WRITE_STYLE.md)
- **Risks**: Tests can hang without timeouts; backend test status unclear from preflight output.

## Working Memory

### Short-Term (Now)
- **Active Scenario**: Finalize scope and standards updates.
- **Focused Command**: `bun test tests/style-validation.test.tsx`
- **Last Signal (Observed)**: `3 pass` in style validation tests after prop validation changes.
- **Hypothesis**: Backend suite may still show preflight failures; focused tests are green for changed scenarios.
- **Next Micro-step**: Close out scope updates and log verification commands.

### Long-Term (Track)
- **Definition of Done**:
  - [x] SSE streaming test validates `protocol.hello` and `ui.render`.
  - [x] Prop validation test asserts warning + fallback.
  - [x] Backpressure scope docs updated (use cases, traces, diagram, evidence).
  - [x] WRITE_STYLE includes test timeout guidance.
- **Constraints from Scopes**:
  - Protocol-driven, evidence-first, minimal code.
- **Decisions**:
  - Use strict TDD per scenario; one behavior per cycle.
- **Drift to Document**:
  - Backpressure documentation missing from scope.
- **Env/Setup Notes**:
  - Backend tests must run in `agentprinter-fastapi`.

## Parking Lot
- [ ] Verify overall backend suite status once focused scenarios are complete.

## Test List (The Plan)
- [x] Scenario 1: SSE endpoint streams `protocol.hello` and `ui.render`.
- [x] Scenario 2: Invalid props trigger validation warning + fallback.
- [x] Scenario 3: Update backpressure scope documentation.

## Execution Log
### Cycle 1: SSE Streaming Test
- **RED**: `agentprinter-fastapi/tests/test_sse_fallback.py`
  - *Outcome*: Failed as expected (`TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'`).
- **GREEN**: `agentprinter-fastapi/tests/test_sse_fallback.py`
  - *Outcome*: Passed (`1 passed in 0.12s`).
- **REFACTOR**: Simplified SSE read path to use StreamingResponse iterator with explicit timeouts.
- **SCOPE UPDATE**: Not required for this task.
#### Micro-steps (Edit → Rerun)
1) Edit: `agentprinter-fastapi/tests/test_sse_fallback.py` — add async streaming test using httpx.
   - Rerun: `uv run pytest tests/test_sse_fallback.py::test_sse_streams_protocol_hello_and_ui_render` → fail (TypeError on AsyncClient app arg)
2) Edit: `agentprinter-fastapi/tests/test_sse_fallback.py` — switch to `sse_endpoint` StreamingResponse iterator with `asyncio.wait_for`.
   - Rerun: same command → pass

### Cycle 2: Prop Validation Test
- **RED**: `agentprinter-react/tests/style-validation.test.tsx`
  - *Outcome*: Failed as expected (renderer parse errors during initial run).
- **GREEN**: `agentprinter-react/tests/style-validation.test.tsx`
  - *Outcome*: Passed (`3 pass`).
- **REFACTOR**: Cleaned duplicate/garbled component blocks while adding prop validation fallback.
- **SCOPE UPDATE**: Updated `Scopes/Product/Frontend/Remote_UI_Runtime.md` (summary, rules, traces, diagram, evidence).
#### Micro-steps (Edit → Rerun)
1) Edit: `agentprinter-react/tests/style-validation.test.tsx` — add invalid props test with timeout.
   - Rerun: `bun test tests/style-validation.test.tsx` → fail (renderer parse errors)
2) Edit: `agentprinter-react/src/renderer.tsx` — store registration metadata + add prop validation fallback.
   - Rerun: same command → fail (remaining renderer parse errors)
3) Edit: `agentprinter-react/src/renderer.tsx` — remove duplicate/garbled component blocks, fix MultiSelect.
   - Rerun: same command → pass
4) Edit: `agentprinter-react/src/renderer.tsx` — add `buildActionMessage` helper and fix Switch handler.
   - Rerun: `bun test tests/style-validation.test.tsx` → pass

### Cycle 3: Backpressure Scope Docs
- **RED**: N/A (docs-only scope update)
- **GREEN**: Updated `Scopes/Product/Backend/WebSocket_Runtime.md`
  - *Outcome*: Backpressure use cases, traces, diagram gates, and evidence links added.
- **REFACTOR**: N/A (docs-only)
- **SCOPE UPDATE**: Updated `Scopes/Product/Backend/WebSocket_Runtime.md` (use cases, trace entries, diagram, evidence).
#### Micro-steps (Edit → Rerun)
1) Edit: `Scopes/Product/Backend/WebSocket_Runtime.md` — add backpressure use cases, traces, diagram, evidence.
