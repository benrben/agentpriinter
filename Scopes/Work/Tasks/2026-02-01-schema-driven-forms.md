# Task: Schema-driven form component (SchemaContract)

## 1. Summary
**Goal**: Implement a minimal schema-driven form renderer in `@agentprinter/react` that can render a form from the `SchemaContract` (JSON Schema + ui_schema) and emit a `user.action` on submit.
**Context**: `PROJECT_GOAL.md` calls for JSON Schema + UI schema “auto forms + validation”. The protocol schema already defines `SchemaContract`, but the React SDK does not yet render it.

## 2. Current State (Scopes)
- **Anchor Scope**: [Remote UI Runtime (React)](../../Product/Frontend/Remote_UI_Runtime.md)
- **Current Behavior**:
  - The protocol includes `SchemaContract` in backend models and frontend-generated contracts. [agentprinter-fastapi/src/agentprinter_fastapi/schemas/tools.py:L13-L19](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/tools.py#L13-L19), [agentprinter-react/src/contracts.ts:L199-L204](../../../agentprinter-react/src/contracts.ts#L199-L204)
  - The component bank renders many built-in components, but there is no evidence of a JSON Schema-driven form component consuming `SchemaContract`. (Only contract/types exist.) [agentprinter-react/src/contracts.ts:L199-L204](../../../agentprinter-react/src/contracts.ts#L199-L204)

## 3. Desired State
- **New Behavior**:
  - A built-in `Form` component can be rendered via `ComponentNode.type: "form"` (or an explicit agreed-upon type).
  - The component accepts a `schema_contract` prop (matching the `SchemaContract` contract) and renders inputs for a minimal JSON Schema subset:
    - object with `properties`
    - string/number/boolean
    - enum (select)
    - required fields
  - On submit, it emits a `user.action` using an action payload mapping (or a simple `action` prop) containing the collected form values.
- **Constraints**:
  - Keep scope to a minimal subset (1–4 hours): no full RJSF integration unless it’s clearly the smallest change.
  - Avoid reimplementing validation frameworks; prefer minimal validation aligned with required fields.

## 4. Implementation Steps
1. **Decide component type + props shape** (documented and tested):
   - e.g. `type: "form"` with props:
     - `schema_contract: SchemaContract`
     - `action: { action_id, trigger: "submit", ... }` (reuse existing `buildActionMessage` patterns where possible)
2. **Implement renderer component**:
   - Add a `Form` renderer in `agentprinter-react/src/renderer.tsx` component bank.
   - Render inputs based on JSON Schema `properties` and `required`.
3. **Submit behavior**:
   - On submit, emit `user.action` with collected values (and include any configured `payload_mapping` semantics if present).
4. **Tests**:
   - Add a focused React test that:
     - renders a `form` node with a small `schema_contract`
     - fills fields
     - clicks submit
     - asserts the sent `user.action` payload includes the form values
5. **Demo (optional, if small)**:
   - Update `examples/backend_demo.py` to include a schema-driven form section in the rendered page.

## 5. Acceptance Criteria (Verification)
- [x] Form renders from SchemaContract minimal subset and emits `user.action` on submit (tested).
- [x] Tests:
  - [x] Run: `cd agentprinter-react && bun test`
- [x] (If demo updated) Demo still runs:
  - [x] Run: `cd examples && uv run python backend_demo.py`
  - [x] Run: `cd examples/frontend_demo && bun run dev` (manual smoke)
- [x] **Scope Maintenance**:
  - [x] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Add “schema-driven forms” to **Summary** (if shipped)
    - Add **Use case** and trace entries for `SchemaContract` form rendering + submit action
    - Add evidence links to the `Form` renderer and its tests
  - [x] Update `Scopes/Product/Contracts/Protocol_Schema.md` if the component’s expected prop shape or contract usage changes (evidence-backed).

## 6. Dependencies
- None (SchemaContract already exists in the exported schema).

## Audit Checklist
- [x] Anchor Scope is under `Scopes/Product/**`
- [x] Verification is concrete (`bun test`)
- [x] JSON Schema subset is explicitly documented and tested

