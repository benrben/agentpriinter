# Task: Tool contract metadata messages (backend emit + frontend surface)

## 1. Summary
**Goal**: Implement a minimal, explicit protocol message for tool metadata (`Tool` contract) so tools are “first-class” as described in `PROJECT_GOAL.md`.
**Context**: The `Tool` contract exists in the exported schema, but there is no implemented message type that sends tool metadata to the frontend at runtime.

## 2. Current State (Scopes)
- **Anchor Scope**: [Protocol Schema & Codegen](../../Product/Contracts/Protocol_Schema.md)
- **Current Behavior**:
  - Backend defines a `Tool` contract with `name`, `description`, `input_schema`, `output_schema`, `ui_schema`, `render_hints`. [agentprinter-fastapi/src/agentprinter_fastapi/schemas/tools.py:L4-L12](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/tools.py#L4-L12)
  - Frontend codegen includes `toolSchema`, but there is no evidence of a runtime message type like `tool.register`/`tool.list` being emitted or handled. [agentprinter-react/src/contracts.ts:L190-L197](../../../agentprinter-react/src/contracts.ts#L190-L197)
  - The backend does not emit any `tool.*` messages today (no matches in runtime code). [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L150-L224](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L150-L224)

## 3. Desired State
- **New Behavior**:
  - Backend can emit a `tool.list` message containing an array of `Tool` metadata (or `tool.register` per-tool), ideally during connect after `protocol.hello`.
  - Frontend stores tool metadata (e.g., in provider state) and exposes it via context so apps/devtools can display it.
- **Constraints**:
  - Keep it minimal: implement “metadata delivery” only (not full tool invocation UX).

## 4. Implementation Steps
1. **Backend**:
   - Add a small tool registry (could be a list/set) and an API to register tools at app startup.
   - On connect, emit `tool.list` (type string is fine; contract lives in payload) with `tools: Tool[]`.
2. **Frontend**:
   - Add typed payload validation for `tool.list` and store the tool list in provider state.
   - Expose `tools` in `AgentPrinterContextType`.
   - Optionally: show tool list in existing devtools snapshot export.
3. **Tests**:
   - Backend: ensure `tool.list` payload matches schema and is sent on connect (websocket test).
   - Frontend: receiving `tool.list` updates context state (unit test).

## 5. Acceptance Criteria (Verification)
- [ ] Schema/codegen still succeed:
  - [ ] Run: `python agentprinter-fastapi/scripts/export_schema.py`
  - [ ] Run: `cd agentprinter-react && bun run codegen`
- [ ] Backend tests pass:
  - [ ] Run: `cd agentprinter-fastapi && uv run pytest`
- [ ] Frontend tests pass:
  - [ ] Run: `cd agentprinter-react && bun test`
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md` with a new **Use case** for tool metadata emission (evidence-backed).
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md` with a new **Use case** for receiving/storing tool metadata (evidence-backed).
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md` to document the `tool.list` (or `tool.register`) message payload shape and evidence.

## 6. Dependencies
- None.

## Audit Checklist
- [ ] Anchor Scope is under `Scopes/Product/**`
- [ ] Message type is explicitly documented and tested
- [ ] Scope maintenance lists traces + evidence updates explicitly

