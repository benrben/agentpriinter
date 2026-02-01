# Task: Align `user.action` emission with backend `ActionPayload` validation

## 1. Summary
**Goal**: Make the React SDK emit `user.action` payloads that actually pass the backend’s `ActionPayload` validation, and document the minimal server-provided `action` object shape required for reliable routing.
**Context**: Today, the backend validates every `user.action` payload as `ActionPayload`, but the frontend emitter does not include required fields like `target`, which makes end-to-end actions fail once they hit the backend.

## 2. Current State (Scopes)
- **Anchor Scope**: [Backend WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Current Behavior**:
  - Backend validates `user.action` payloads with `ActionPayload.model_validate(payload)` and raises `InvalidActionPayloadError` on missing/invalid fields. [agentprinter-fastapi/src/agentprinter_fastapi/actions.py:L61-L69](../../../agentprinter-fastapi/src/agentprinter_fastapi/actions.py#L61-L69)
  - `ActionPayload` requires `action_id`, `trigger`, and `target`; `mode` defaults and `payload_mapping` defaults. [agentprinter-fastapi/src/agentprinter_fastapi/schemas/actions.py:L4-L11](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/actions.py#L4-L11)
  - Frontend `buildActionMessage` emits payload with `action_id` and `trigger`, but **does not include `target`** (unless the caller stuffed it into `action.payload`). [agentprinter-react/src/renderer.tsx:L101-L120](../../../agentprinter-react/src/renderer.tsx#L101-L120)
  - Frontend interactive test constructs an action object that does not include `target` (so messages it asserts as “correct” would be rejected by the backend). [agentprinter-react/tests/interactive.test.tsx:L19-L24](../../../agentprinter-react/tests/interactive.test.tsx#L19-L24)

## 3. Desired State
- **New Behavior**:
  - A server-provided action object can include `target` (and optionally `mode`, `payload_mapping`) and the React SDK forwards these fields into the emitted `user.action` payload so the backend accepts it.
  - The `examples/backend_demo.py` (or another example) demonstrates an action that round-trips successfully (frontend emits → backend routes).
- **Constraints**:
  - Keep it minimal: don’t redesign the entire action system—just make the current contract actually work end-to-end.

## 4. Implementation Steps
1. **React emitter fix** (`agentprinter-react/src/renderer.tsx`):
   - Update `buildActionMessage(...)` to include:
     - `target: action.target` (required for backend validation)
     - `mode: action.mode` (optional; default is fine)
     - `payload_mapping: action.payload_mapping` (optional)
   - Keep `trigger` as it is (defaults to the component event if not provided).
2. **React tests**:
   - Update `agentprinter-react/tests/interactive.test.tsx` fixtures to include `target` in the action objects and assert it is present in the emitted payload.
3. **Backend demo alignment** (if needed for a true end-to-end proof):
   - Ensure demo-provided action shapes include `target` where they are expected to round-trip to backend routing.
4. **(Optional, if needed for backwards compatibility)**:
   - If existing JSON templates omit `target`, decide and document one policy:
     - either: backend `ActionPayload.target` becomes optional (default empty string) and target-based routing remains optional
     - or: frontend fills a safe default target (and document it)

## 5. Acceptance Criteria (Verification)
- [x] Frontend tests updated and passing:
  - [x] Run: `cd agentprinter-react && bun test`
- [x] Backend still accepts + routes valid actions (no regressions):
  - [x] Run: `cd agentprinter-fastapi && uv run pytest`
- [x] **Scope Maintenance**:
  - [x] Update `Scopes/Product/Backend/WebSocket_Runtime.md`:
    - Ensure the `invalid_action_payload` behavior is still accurately documented and add a note about required fields (`trigger`, `target`) with evidence.
  - [x] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Add/update evidence for how actions are serialized into `user.action` payloads (including `target`).
  - [x] If any contract changes, update `Scopes/Product/Contracts/Protocol_Schema.md` with evidence.

## 6. Dependencies
- None (but this should be done before any new feature that depends on actions, like schema-driven forms).

## Audit Checklist
- [x] Anchor Scope is under `Scopes/Product/**`
- [x] Acceptance includes concrete test commands (`bun test`, `uv run pytest`)
- [x] End-to-end action payloads conform to `ActionPayload`

