# Task: Component bank minimum version negotiation

## 1. Summary
**Goal**: Implement a minimal “component bank minimum version” negotiation so the backend can declare a minimum supported component bank version and the frontend can reject/flag incompatibility.
**Context**: `PROJECT_GOAL.md` calls for component bank semver + backend requesting a minimum version; today there is no evidence of a compatibility check.

## 2. Current State (Scopes)
- **Anchor Scope**: [Protocol Schema & Codegen](../../Product/Contracts/Protocol_Schema.md)
- **Current Behavior**:
  - Backend has a `ComponentDefinition.version` field in a component bank module, but there is no protocol-level negotiation that uses it. [agentprinter-fastapi/src/agentprinter_fastapi/components.py:L8-L15](../../../agentprinter-fastapi/src/agentprinter_fastapi/components.py#L8-L15)
  - Backend handshake negotiates protocol version via a hook and sends `protocol.hello`, but does not include any component bank version metadata. [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L109-L143](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L109-L143)
  - Frontend renders unknown components with a fallback placeholder, but does not enforce a minimum component-bank version contract. [agentprinter-react/src/renderer.tsx:L1860-L1888](../../../agentprinter-react/src/renderer.tsx#L1860-L1888)

## 3. Desired State
- **New Behavior**:
  - Backend can advertise `component_bank_version` and `min_component_bank_version` (or equivalent) during connect (e.g., in `protocol.hello` payload).
  - Frontend checks compatibility and:
    - logs a clear warning (at minimum), and/or
    - surfaces an in-UI “incompatible version” placeholder to avoid silent breakage.
- **Constraints**:
  - Keep it minimal: negotiation is informational + guardrails; do not block rendering unless clearly unsafe.

## 4. Implementation Steps
1. **Contract**:
   - Extend the `protocol.hello` payload shape to include component bank version metadata (schema-exported).
2. **Backend**:
   - Emit the version fields in `protocol.hello` (source of truth: component bank module).
3. **Frontend**:
   - Validate the hello payload (typed).
   - Compare versions and warn/surface incompatibility.
4. **Tests**:
   - Backend: hello includes the fields.
   - Frontend: incompatible version triggers warning / UI signal.

## 5. Acceptance Criteria (Verification)
- [ ] Schema export + codegen:
  - [ ] Run: `python agentprinter-fastapi/scripts/export_schema.py`
  - [ ] Run: `cd agentprinter-react && bun run codegen`
- [ ] Tests:
  - [ ] Run: `cd agentprinter-fastapi && uv run pytest`
  - [ ] Run: `cd agentprinter-react && bun test`
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md` with hello payload additions + evidence.
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md` (hello emission contents + evidence).
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md` (compatibility check behavior + evidence).

## 6. Dependencies
- None (but should be coordinated with any other `protocol.hello` payload typing work).

## Audit Checklist
- [ ] Anchor Scope is under `Scopes/Product/**`
- [ ] Version comparison behavior is explicit + tested

