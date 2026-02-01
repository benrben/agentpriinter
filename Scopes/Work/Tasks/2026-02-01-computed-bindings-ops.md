# Task: Computed bindings (if/concat/format)

## 1. Summary
**Goal**: Extend the bindings contract to support minimal computed props operators (`if`, `concat`, `format`) so servers can declare simple computed UI values without bespoke frontend logic.
**Context**: `PROJECT_GOAL.md` calls for computed props with minimal operators; current bindings are direct `prop -> state path` mappings only.

## 2. Current State (Scopes)
- **Anchor Scope**: [Protocol Schema & Codegen](../../Product/Contracts/Protocol_Schema.md)
- **Current Behavior**:
  - Bindings are currently `{ prop, path }` only. [agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py:L23-L27](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py#L23-L27)
  - Frontend resolves bindings by calling `getStateValue(binding.path)` and assigning `props[binding.prop] = value`. [agentprinter-react/src/renderer.tsx:L1890-L1899](../../../agentprinter-react/src/renderer.tsx#L1890-L1899)

## 3. Desired State
- **New Behavior**:
  - Bindings can represent computed expressions using a small operator set:
    - `concat`: join string fragments and/or state-path lookups
    - `format`: fill a template string using named args (from state paths / literals)
    - `if`: conditional selection based on a boolean-ish state path
  - Frontend evaluates these expressions deterministically and safely (no code execution).
- **Constraints**:
  - Do not introduce an “eval” or arbitrary expression language.
  - Keep operator semantics minimal and well-tested.

## 4. Implementation Steps
1. **Contracts (backend + schema export)**:
   - Extend `Bindings` schema in `agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py` to support either:
     - the existing `{ prop, path }` form, or
     - a new `{ prop, expr: <BindingExpr> }` form.
   - Define `BindingExpr` as a discriminated union (e.g., `op: "concat" | "format" | "if" | "path"`) with a JSON-serializable shape.
2. **Frontend evaluator**:
   - Add an evaluator in `agentprinter-react/src/renderer.tsx` that:
     - resolves `path` expressions via `getStateValue`
     - computes `concat` / `format` / `if` deterministically
     - falls back safely on missing paths (e.g., treat as `undefined` and skip assignment)
3. **Tests**:
   - Add/extend `agentprinter-react/tests/` to cover:
     - concat literal + path
     - format with named args from state
     - if conditional selection
     - missing paths do not crash; result is omitted
4. **Codegen**:
   - Run schema export + `bun run codegen` to ensure TS/Zod represent the new binding shapes.

## 5. Acceptance Criteria (Verification)
- [ ] Schema export and frontend codegen succeed:
  - [ ] Run: `python agentprinter-fastapi/scripts/export_schema.py`
  - [ ] Run: `cd agentprinter-react && bun run codegen`
- [ ] Renderer supports computed bindings with tests:
  - [ ] Run: `cd agentprinter-react && bun test`
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Add computed bindings operator coverage under **Rules & Constraints**
    - Add evidence links to the updated `Bindings` / expression models
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Update **What Happens** and **Rules & Constraints** for computed bindings evaluation
    - Add at least one **Use case** and trace entries for computed binding evaluation

## 6. Dependencies
- None (standalone feature; compatible with existing binding resolution).

## Audit Checklist
- [ ] Anchor Scope is under `Scopes/Product/**`
- [ ] Operators are safe (no arbitrary code execution)
- [ ] Verification uses existing test commands (`bun test`)

