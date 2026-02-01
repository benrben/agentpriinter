# Task: Unify the `ui.patch` contract end-to-end (design + mapping plan)

## 1. Summary
**Goal**: Produce a single documented `ui.patch` payload schema and a mapping plan from the current backend-emitted patch shape to the frontend runtime’s expected patch shape.
**Context**: The backend emits `ui.patch` payloads with `{target, text, operation}` (including ops like `"append"`). The React runtime’s patch handler expects `{target_id, operation: update_props|update_children|add|remove, ...}`.

## 2. Current State (Scopes)
- **Anchor Scope**: [Protocol Schema & Codegen](../../Product/Contracts/Protocol_Schema.md)
- **Current Behavior**:
  - Backend emits `ui.patch` messages with ad-hoc payload dicts (example: `target`, `text`, `operation`). [agentprinter-fastapi/src/agentprinter_fastapi/agent_adapters.py:L365-L379](../../../agentprinter-fastapi/src/agentprinter_fastapi/agent_adapters.py#L365-L379)
  - Backend uses `operation: "append"` in emitted patch payloads. [agentprinter-fastapi/src/agentprinter_fastapi/agent_adapters.py:L333-L356](../../../agentprinter-fastapi/src/agentprinter_fastapi/agent_adapters.py#L333-L356)
  - Frontend `ui.patch` handler looks up a node by `patchPayload.target_id` and switches over `patchPayload.operation` values `update_props|update_children|add|remove`. [agentprinter-react/src/runtime.tsx:L33-L74](../../../agentprinter-react/src/runtime.tsx#L33-L74)

## 3. Desired State
- **New Behavior**:
  - A single `UiPatchPayload` schema is defined (in docs first; later in codegen/contracts), with explicit variants for each operation.
  - A mapping table exists from “old backend patch ops + keys” → “new canonical UiPatch ops + keys”.
  - The team has an explicit decision on what `"append"` means in canonical terms (or that it is removed).
- **Constraints**:
  - Prefer reusing the frontend runtime operation set (already implemented) rather than inventing a second patch language.
  - Keep the mapping minimal; avoid introducing multiple patch dialects.

## 4. Implementation Steps
1. **Write the canonical schema (docs-first)**:
   - Document each allowed `operation` and required fields.
   - Document allowed/expected semantics (e.g., `update_props` merges props).
2. **Inventory current backend patch emitters**:
   - Identify all call sites that emit `type="ui.patch"` and list their current payload shapes.
3. **Create a mapping table**:
   - For each backend payload shape, specify:
     - canonical `operation`
     - canonical field names (`target_id`, `props`, `children`, `child`, `child_id`)
     - any required transformation (e.g., text append behavior)
4. **Decide the `"append"` story** (pick one and document it):
   - Option A: represent as `update_props` with a well-defined “append to existing string prop” behavior (requires frontend support).
   - Option B: ban/remove `"append"` and require backend to construct the full new prop value (simpler contract).
5. **Write the alignment note under Scopes**:
   - Create `Scopes/Research/2026-02-02-ui-patch-contract-alignment.md`.

## 5. Acceptance Criteria (Verification)
- [ ] A decision note exists: `Scopes/Research/2026-02-02-ui-patch-contract-alignment.md`
  - [ ] Contains the canonical `UiPatchPayload` schema (human-readable, variant-by-variant).
  - [ ] Contains a mapping table from current backend patch payloads → canonical schema.
  - [ ] Includes at least 3 evidence links: backend emitter + frontend handler.
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Ensure the documented `ui.patch` operation set matches the canonical schema.
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md`:
    - Add a note that backend emitters must conform to the canonical schema (and list the known current mismatches if any remain).
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Document whether `ui.patch` will become schema-exported (and where) vs remain “ad-hoc”.
    - Keep diagrams at exactly **2**.

## 6. Dependencies
- None (but Task 06 depends on this decision if coalescing/batching is kept).

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Mapping table covers every known backend emitter of `ui.patch`
- [ ] Canonical operation set matches the frontend runtime handler

