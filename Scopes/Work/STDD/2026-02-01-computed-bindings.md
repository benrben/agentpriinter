# STDD Session: Computed Bindings

## Context Snapshot
- **Goal**: Implement computed bindings (concat, format, if) in contracts and runtime.
- **Relevant Scopes**:
  - [Scopes/Product/Contracts/Protocol_Schema.md](../../Product/Contracts/Protocol_Schema.md)
  - [Scopes/Product/Frontend/Remote_UI_Runtime.md](../../Product/Frontend/Remote_UI_Runtime.md)
  - [Scopes/Work/Tasks/2026-02-01-computed-bindings-ops.md](../Tasks/2026-02-01-computed-bindings-ops.md)
- **Code Standards**: [Scopes/Work/Standards/WRITE_STYLE.md](../Standards/WRITE_STYLE.md)

## Working Memory

### Short-Term (Now)
- **Active Scenario**: 1. Update Backend Contracts. 2. Frontend Evaluator Implementation. 3. Tests.
- **Focused Command**: `python agentprinter-fastapi/scripts/export_schema.py && cd agentprinter-react && bun run codegen && bun test`
- **Last Signal (Observed)**: N/A
- **Hypothesis**: N/A
- **Next Micro-step**: Define new Pydantic models for BindingExpr in backend.

### Long-Term (Track)
- **Definition of Done**:
  - [ ] Ops: `concat`, `format`, `if` supported in schema.
  - [ ] Frontend evaluates them correctly.
  - [ ] Safe failure on missing data.
- **Constraints**:
  - No `eval()`.
  - JSON-serializable expressions.

## Parking Lot
- [ ] Action payload alignment (Task 5).

## Test List (The Plan)
- [x] Scenario 1: Verify Schema change and codegen correctness.
- [x] Scenario 2: Verify `concat` operator logic.
- [x] Scenario 3: Verify `format` operator logic.
- [x] Scenario 4: Verify `if` operator logic.
- [x] Scenario 5: Verify legacy simple bindings still work.

## Execution Log

### Cycle 1: Computed Bindings Implementation
- **GREEN**: 
  - Updated `agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py` to define `BindingExpression` union with `concat`, `format`, `if`, and primitives.
  - Exported schemas and ran `codegen` in frontend.
  - Updated `agentprinter-react/src/renderer.tsx` to implement `evaluateBindingExpr`.
- **RED**: 
  - First attempt at `if` operator test failed because I was passing a string literal "Welcome Guest" as `else_val`, but my frontend evaluator returned `undefined` for non-object bindings.
  - Fixed by updating `evaluateBindingExpr` to pass through primitives (strings/numbers/booleans) as valid leaf values.
- **GREEN**: 
  - Reran tests `tests/bindings.test.tsx` and all passed (legacy + computed variants).
- **SCOPE UPDATE**: 
  - Updated `Scopes/Product/Contracts/Protocol_Schema.md` and `Scopes/Product/Frontend/Remote_UI_Runtime.md` with new capabilities, uses cases, and traces.

#### Micro-steps
1) Edit: Defined `BindingExpr` models in `ui.py`.
   - Rerun: `export_schema` + `codegen` → Pass.
2) Edit: Implemented `evaluateBindingExpr` in `renderer.tsx` (initial version).
3) Edit: Added comprehensive tests in `tests/bindings.test.tsx`.
   - Rerun: `bun test` → Fail (`if` primitive handling).
4) Edit: Updated `evaluateBindingExpr` to return primitives.
5) Edit: Updated `ui.py` to recursively allow primitives in `BindingExpression` union (for correctness).
   - Rerun: `export_schema` + `codegen` + `bun test` → Pass.
