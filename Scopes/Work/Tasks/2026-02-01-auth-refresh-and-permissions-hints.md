# Task: Auth refresh event + permission hints plumbing

## 1. Summary
**Goal**: Add a minimal `auth.refresh_required` protocol event and a permissions hint mechanism that can disable/hide actions in the React runtime, enabling “production-ready auth flows” described in `PROJECT_GOAL.md`.
**Context**: `PROJECT_GOAL.md` explicitly calls out `auth.refresh_required` and permission hints; current implementation has an auth hook but no refresh event contract or frontend handling.

## 2. Current State (Scopes)
- **Anchor Scope**: [Backend WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Current Behavior**:
  - Backend supports an optional auth hook during handshake; failures return `protocol.error` and close. [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L96-L107](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L96-L107)
  - The goal doc calls out `auth.refresh_required`, but the codebase has no implementation matches. [Scopes/Work/Planning/PROJECT_GOAL.md:L127-L134](../Planning/PROJECT_GOAL.md#L127-L134)
  - Frontend interactive components generally respect `disabled` props, but there is no first-class permission-hints contract being applied from protocol messages. [agentprinter-react/src/renderer.tsx:L1526-L1564](../../../agentprinter-react/src/renderer.tsx#L1526-L1564)

## 3. Desired State
- **New Behavior**:
  - Backend can emit an `auth.refresh_required` message to the client (typed payload) when it detects an expired token / auth context.
  - React SDK exposes a provider callback (e.g., `onAuthRefreshRequired`) that is invoked when this message arrives, enabling apps to refresh tokens and reconnect.
  - Permission hints can disable or hide actions without custom frontend glue (minimal mechanism; does not require a full RBAC system).
- **Constraints**:
  - Keep it minimal: focus on the event + hook plumbing; do not build a full auth provider.
  - Ensure contracts are schema-exported and codegen’d (so consumers can rely on types).

## 4. Implementation Steps
1. **Contracts**:
   - Define `AuthRefreshRequiredPayload` in backend schemas.
   - Export it via `ProtocolContract` so frontend codegen includes it.
2. **Backend emission**:
   - Add a helper to emit `auth.refresh_required` and (optionally) close the socket after sending.
   - Integrate with auth hook or a dedicated “auth check” hook point (minimal surface).
3. **Frontend handling**:
   - Add `onAuthRefreshRequired?: (payload) => void` to `AgentPrinterProvider` props.
   - Validate `auth.refresh_required` payload (typed validation policy: drop invalid payloads).
   - Invoke callback when received.
4. **Permission hints (minimal)**:
   - Define a tiny `PermissionHint` payload shape and a message type (e.g., `ui.permissions`) OR define a convention that permission hints are delivered via `state.patch` for `disabled/hidden` props (choose one and document).
   - Implement frontend application of hints (e.g., update local state used by bindings) and renderer behavior (disable/hide).
5. **Tests**:
   - Backend: message shape emitted and validates against schema export.
   - Frontend: receiving `auth.refresh_required` triggers callback; invalid payload is dropped.

## 5. Acceptance Criteria (Verification)
- [ ] Contract export + codegen:
  - [ ] Run: `python agentprinter-fastapi/scripts/export_schema.py`
  - [ ] Run: `cd agentprinter-react && bun run codegen`
- [ ] Backend tests pass:
  - [ ] Run: `cd agentprinter-fastapi && uv run pytest`
- [ ] Frontend tests pass (including new callback test):
  - [ ] Run: `cd agentprinter-react && bun test`
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md` with the new auth refresh + permissions contract(s) and evidence links.
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md` with a new **Use case** for auth refresh emission (include evidence).
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md` with a new **Use case** for handling auth refresh and applying permission hints.

## 6. Dependencies
- [ ] Task: [Add explicit sequencing + resume contracts](./2026-02-01-protocol-seq-and-resume-contract.md) (if the schema export path is being modified in the same area)

## Audit Checklist
- [ ] Anchor Scope is under `Scopes/Product/**`
- [ ] Verification commands are concrete and repeatable
- [ ] Permission-hints mechanism is explicitly defined (no “magic”)

