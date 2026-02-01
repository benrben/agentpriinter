# Task: Decide what to do about patch coalescing payload shape (batch vs remove)

## 1. Summary
**Goal**: Decide whether to keep patch coalescing, and if so define an explicit batch message payload/schema that both backend and frontend understand.
**Context**: The backend currently coalesces rapid `ui.patch`/`state.patch` messages by emitting a payload shaped like `{ patches: [...] }`, which is not a recognized shape by the frontend patch handlers.

## 2. Current State (Scopes)
- **Anchor Scope**: [Backend WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Current Behavior**:
  - Backend coalesces patch messages by combining multiple pending patches into one message whose payload becomes `{"patches": combined_ops}`. [agentprinter-fastapi/src/agentprinter_fastapi/manager.py:L24-L44](../../../agentprinter-fastapi/src/agentprinter_fastapi/manager.py#L24-L44)
  - Coalescing logic collects `p.get("payload", {})` for each pending patch. [agentprinter-fastapi/src/agentprinter_fastapi/manager.py:L33-L40](../../../agentprinter-fastapi/src/agentprinter_fastapi/manager.py#L33-L40)
  - Frontend `ui.patch` handler expects a single patch payload with `target_id` + `operation` fields. [agentprinter-react/src/runtime.tsx:L33-L74](../../../agentprinter-react/src/runtime.tsx#L33-L74)
  - Frontend `state.patch` handler expects `{version, operations}` (batch semantics), not `{patches: [...]}`. [agentprinter-react/src/state.tsx:L6-L9](../../../agentprinter-react/src/state.tsx#L6-L9)

## 3. Desired State
- **New Behavior**:
  - Either:
    - **Coalescing is removed/disabled** (simplest, “less code”), or
    - Coalescing emits a **well-defined, schema-documented batch payload** that receivers handle deterministically.
- **Constraints**:
  - Don’t silently emit an “unknown payload shape” that receivers ignore.
  - Prefer one canonical batching story (not multiple competing wrappers).

## 4. Implementation Steps
1. **Decide whether coalescing is actually needed**:
   - Identify the intended benefit (perf/backpressure) vs complexity.
2. **Pick one approach**:
   - Option A (remove): stop wrapping/coalescing and emit patches individually.
   - Option B (batch message types): introduce `ui.patch.batch` and `state.patch.batch` message types with explicit schemas.
   - Option C (in-place payload change): keep message type (`ui.patch`) but change payload to a canonical batch payload (only if receivers are updated first / safely).
3. **Write the decision note under Scopes**:
   - Create `Scopes/Research/2026-02-02-patch-coalescing-decision.md` including:
     - chosen option
     - payload schema (if batching)
     - compatibility plan / rollout order

## 5. Acceptance Criteria (Verification)
- [ ] A decision note exists: `Scopes/Research/2026-02-02-patch-coalescing-decision.md`
  - [ ] States which option is chosen (remove vs batch vs in-place).
  - [ ] If batching: includes canonical payload schema and message type name(s).
  - [ ] Includes at least 3 evidence links showing the current `{patches: [...]}` shape and receiver expectations.
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md`:
    - Ensure patch coalescing behavior is documented accurately (or removed from docs if you choose removal).
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Document whether `ui.patch.batch`/`state.patch.batch` is supported (or that patches arrive individually).
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Document whether batch message payloads are schema-exported and where.
    - Keep diagrams at exactly **2**.

## 6. Dependencies
- [ ] Task: [Unify the `ui.patch` contract end-to-end (design + mapping plan)](./2026-02-02-04-ui-patch-contract-alignment-plan.md)
- [ ] Task: [Unify the `state.patch` contract end-to-end (design decision)](./2026-02-02-05-state-patch-contract-alignment-plan.md)

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Decision prevents “unknown payload wrapper” states
- [ ] Rollout order is explicit if it requires coordinated changes

