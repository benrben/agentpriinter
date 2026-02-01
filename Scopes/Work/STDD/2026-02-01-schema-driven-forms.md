# STDD Session: Schema-driven forms

## Context Snapshot
- **Goal**: Implement `SchemaContract` rendering (JSON Schema -> Form UI).
- **Relevant Scopes**:
  - [Remote UI Runtime (React)](../../Product/Frontend/Remote_UI_Runtime.md)
  - [Protocol Schema](../../Product/Contracts/Protocol_Schema.md)
- **Code Standards**: [Scopes/Work/Standards/WRITE_STYLE.md](../../Standards/WRITE_STYLE.md)

## Working Memory

### Short-Term (Now)
- **Active Scenario**: Render minimal JSON Schema fields (string, number, boolean, enum).
- **Focused Command**: `cd agentprinter-react && bun test tests/schema-form.test.tsx`
- **Last Signal (Observed)**: All tests passing (1 pass, 0 fail).
- **Hypothesis**: Can map JSON Schema types to existing inputs dynamically. Verified.

### Long-Term (Track)
- **Definition of Done**:
  - [x] `Form` (as `schema_form`) component accepts `schema_contract` prop.
  - [x] Renders string (input), number (input type=number), boolean (checkbox), enum (select).
  - [x] Validates `required` fields (manual check in `handleSubmit`).
  - [x] Emits `user.action` on submit with all values.
  - [x] Verified via new `schema-form.test.tsx`.
- **Constraints**:
  - Minimal subset first. Done.
- **Decisions**:
  - Reusing `buildActionMessage` for consistent emission.
  - Component identifier: `schema_form`.
  - Added polished styling and hover effects for premium feel.

## Test List (The Plan)
- [x] Scenario 1: Render empty form from empty schema (sanity).
- [x] Scenario 2: Render string field (label + input).
- [x] Scenario 3: Render number field.
- [x] Scenario 4: Render boolean field.
- [x] Scenario 5: Render enum field.
- [x] Scenario 6: Submit collects all values and emits action.

## Execution Log
- Created `agentprinter-react/src/components/schema-form.tsx`.
- Registered `schema_form` in `REGISTRY` within `agentprinter-react/src/renderer.tsx`.
- Added `tests/schema-form.test.tsx` with comprehensive test case.
- Updated `examples/backend_demo.py` with a new "Configure" page demonstrating `schema_form`.
- Fixed `Switch` and `Slider` components in `renderer.tsx` to use `buildActionMessage`.
- Verified all frontend tests pass.
