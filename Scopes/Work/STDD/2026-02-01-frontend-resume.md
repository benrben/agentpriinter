# STDD Session: Frontend Sequencing & Resume

## Context Snapshot
- **Goal**: Implement `seq`-based ordering and resume in the React SDK.
- **Relevant Scopes**:
  - [Scopes/Product/Frontend/Remote_UI_Runtime.md](../../Product/Frontend/Remote_UI_Runtime.md)
  - [Scopes/Work/Tasks/2026-02-01-frontend-use-seq-for-ordering-and-resume.md](../Tasks/2026-02-01-frontend-use-seq-for-ordering-and-resume.md)
- **Code Standards**: [Scopes/Work/Standards/WRITE_STYLE.md](../Standards/WRITE_STYLE.md)

## Working Memory

### Short-Term (Now)
- **Active Scenario**: 1. Track `seq` in Provider. 2. Send `protocol.resume` with `last_seen_seq`. 3. Use `seq` for patch ordering.
- **Focused Command**: `cd agentprinter-react && bun test tests/transport-backoff.test.tsx`
- **Last Signal (Observed)**: N/A
- **Hypothesis**: Tests will fail because we changed the protocol contract but frontend logic still uses version.
- **Next Micro-step**: Update `transport-backoff.test.tsx` to assert new payload structure.

### Long-Term (Track)
- **Definition of Done**:
  - [ ] `protocol.resume` uses `last_seen_seq`.
  - [ ] `ui.patch` uses `seq` for ordering.
  - [ ] `parseInt(version)` Hack removed.
- **Constraints**:
  - `seq` is optional, degrade gracefully.

## Parking Lot
- [ ] Computed bindings (Task 4).

## Test List (The Plan)
- [x] Scenario 1: `protocol.resume` sends `last_seen_seq`.
- [x] Scenario 2: `ui.patch` uses `seq` for ordering.

## Execution Log

### Cycle 3: Frontend Resume Support
- **RED**: `tests/transport-backoff.test.tsx` and `tests/ui-patch-nav.test.tsx`
  - *Outcome*: Failed as expected (resume used `last_seen_version`, patch used `version` ordering).
- **GREEN**: 
  - Updated `agentprinter-react/src/provider.tsx` to track `lastSeenSeq` from `header.seq` and send correct resume shape.
  - Updated `agentprinter-react/src/runtime.tsx` to order patches by `header.seq` instead of parsing `header.version`.
- **REFACTOR**: Updated tests `tests/transport-backoff.test.tsx` and `tests/ui-patch-nav.test.tsx` to align with new contract.
- **SCOPE UPDATE**: Updated `Scopes/Product/Frontend/Remote_UI_Runtime.md` with new `seq`-based use cases and traces.
#### Micro-steps
1) Edit: Updated `tests/transport-backoff.test.tsx` to expect `last_seen_seq`.
   - Rerun: `bun test tests/transport-backoff.test.tsx` → Fail.
2) Edit: Updated `provider.tsx` to track `seq` and use `last_seen_seq` payload.
   - Rerun: `bun test tests/transport-backoff.test.tsx` → Pass.
3) Edit: Updated `runtime.tsx` to use `seq` for patch ordering.
   - Rerun: `bun test` → Fail (`ui-patch-nav.test.tsx` failure).
4) Edit: Updated `tests/ui-patch-nav.test.tsx` to use `seq` for ordering test case.
   - Rerun: `bun test` → All Pass.
