# Task: Unify the `state.patch` contract end-to-end (design decision)

## 1. Summary
**Goal**: Decide a single `state.patch` payload shape (single-op vs batch) and document how schema export + frontend runtime should align.
**Context**: The exported contract defines `StatePatch` as a single RFC6902-style operation, but the frontend state runtime expects a `{version, operations[]}` batch payload.

## 2. Current State (Scopes)
- **Anchor Scope**: [Protocol Schema & Codegen](../../Product/Contracts/Protocol_Schema.md)
- **Current Behavior**:
  - Exported schema defines `StatePatch` as a single op (`op`, `path`, optional `value`, plus `version`). [contracts/schemas.json:L732-L764](../../../contracts/schemas.json#L732-L764)
  - Frontend generated contracts expose `statePatchSchema` matching the single-op shape (and `ProtocolContract.patch` points at it). [agentprinter-react/src/contracts.ts:L225-L296](../../../agentprinter-react/src/contracts.ts#L225-L296)
  - Frontend runtime state handler expects a payload batch: `{ version: number; operations: Operation[] }`. [agentprinter-react/src/state.tsx:L6-L9](../../../agentprinter-react/src/state.tsx#L6-L9)
  - Frontend only applies patches when both `payload.version` and `payload.operations` exist. [agentprinter-react/src/state.tsx:L43-L52](../../../agentprinter-react/src/state.tsx#L43-L52)

## 3. Desired State
- **New Behavior**:
  - A single documented `StatePatchPayload` shape exists and matches what the runtime applies.
  - The schema export + codegen produce a contract that matches the chosen payload shape.
- **Constraints**:
  - Keep it minimal and compatible with `fast-json-patch` operation semantics.
  - Avoid introducing multiple `state.patch` dialects (single-op *and* batch) unless versioned explicitly.

## 4. Implementation Steps
1. **Decide the canonical payload shape**:
   - Option A (batch): `{ version: number, operations: Operation[] }`
   - Option B (single-op): `{ version: number, op: ..., path: ..., value?: ... }`
2. **Document the choice and why**:
   - Consider how coalescing/batching should work (Task 06).
   - Consider how ordering should work (header `seq` vs payload `version`).
3. **Define migration strategy** (docs-first):
   - If switching shapes, define how existing senders/receivers transition (e.g., accept both temporarily, or bump message type).
4. **Write the alignment note under Scopes**:
   - Create `Scopes/Research/2026-02-02-state-patch-contract-alignment.md` including:
     - canonical schema (human-readable)
     - migration strategy
     - list of code touch points to update later (export schema, codegen, runtime handler)

## 5. Acceptance Criteria (Verification)
- [ ] A decision note exists: `Scopes/Research/2026-02-02-state-patch-contract-alignment.md`
  - [ ] Explicitly chooses batch vs single-op and includes the canonical payload schema.
  - [ ] Includes at least 3 evidence links showing the current mismatch (schema vs runtime).
  - [ ] Lists the exact files/modules that will need updates in implementation follow-up.
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Ensure “StatePatch” documentation matches the chosen canonical payload.
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Ensure `state.patch` behavior description matches the chosen canonical payload.
    - Keep diagrams at exactly **2**.

## 6. Dependencies
- None (but Task 06 depends on this decision if state patch coalescing/batching is kept).

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Decision is unambiguous (single canonical shape)
- [ ] Migration plan is explicit (even if it’s “no migration needed because unused”)

