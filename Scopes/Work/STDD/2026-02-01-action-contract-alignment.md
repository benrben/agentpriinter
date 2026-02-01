# STDD Session: Align user.action emission with backend ActionPayload validation

## Context Snapshot
- **Goal**: Align React SDK `user.action` emission with backend `ActionPayload` contract (specifically `target`).
- **Relevant Scopes**:
  - [Remote UI Runtime](../../Product/Frontend/Remote_UI_Runtime.md)
  - [WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Code Standards**: [Scopes/Work/Standards/WRITE_STYLE.md](../../Standards/WRITE_STYLE.md)

## Working Memory

### Short-Term (Now)
- **Active Scenario**: Ensure `target` field is forwarded from component `action` prop to `user.action` payload.
- **Focused Command**: `cd agentprinter-react && bun test tests/interactive.test.tsx`
- **Last Signal (Observed)**: **GREEN** (All 73 tests passed).

### Long-Term (Track)
- **Definition of Done**:
  - [x] `user.action` payload includes `target` when present in component action.
  - [x] All interactive components (`Button`, `Input`, `Form`, `DatePicker`, `FileUpload`, `Navigation`, etc.) use the shared builder.
  - [x] Backend validation passes (verified via existing backend tests + potentially manual check).
- **Decisions**:
  - Refactored `buildActionMessage` into `agentprinter-react/src/utils.ts` and updated all interactive components to use it.
  - Verified `target` forwarding with a focused test case in `interactive.test.tsx`.

## Execution Log

### Cycle 1: Forward Target in Action Payload
- **RED**: `tests/interactive.test.tsx`
  - Added test case expecting `target` in `user.action`.
  - *Outcome*: Failed as expected (missing `target`).
- **GREEN**: `src/renderer.tsx` + `src/utils.ts`
  - Moved `buildActionMessage` to `utils.ts` and added `target`, `mode`, `payload_mapping` support.
  - Updated `Button`, `IconButton`, `Link`, `TextInput`, `Form`, `RichTextEditor` in `renderer.tsx`.
- **REFACTOR**:
  - Updated `datetime.tsx`, `file.tsx`, `navigation.tsx` to use `buildActionMessage`.
  - Verified all tests pass.
- **SCOPE UPDATE**: Updated `Scopes/Product/Frontend/Remote_UI_Runtime.md` with new traces and evidence.
