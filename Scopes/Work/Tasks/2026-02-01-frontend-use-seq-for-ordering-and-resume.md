# Task: Frontend uses `header.seq` for ordering + resume

## 1. Summary
**Goal**: Update the React SDK to use `MessageHeader.seq` (not `MessageHeader.version`) for ordering and resume, aligning the runtime with protocol-version negotiation semantics.
**Context**: `PROJECT_GOAL.md` calls for correct streaming ordering + best-effort resume; current frontend code uses `parseInt(header.version)` for ordering, which conflicts with `version: "1.0.0"` semantics.

## 2. Current State (Scopes)
- **Anchor Scope**: [Remote UI Runtime (React)](../../Product/Frontend/Remote_UI_Runtime.md)
- **Current Behavior**:
  - Provider tracks `lastSeenVersionRef` from `msg.header.version` and sends `protocol.resume` with `payload.last_seen_version`. [agentprinter-react/src/provider.tsx:L34-L35](../../../agentprinter-react/src/provider.tsx#L34-L35), [agentprinter-react/src/provider.tsx:L78-L97](../../../agentprinter-react/src/provider.tsx#L78-L97), [agentprinter-react/src/provider.tsx:L119-L126](../../../agentprinter-react/src/provider.tsx#L119-L126)
  - Runtime orders `ui.patch` by `parseInt(lastMessage.header.version)`. [agentprinter-react/src/runtime.tsx:L90-L106](../../../agentprinter-react/src/runtime.tsx#L90-L106)
  - Typed payload validation currently only enforces `protocol.error` payload shape. [agentprinter-react/src/provider.tsx:L37-L49](../../../agentprinter-react/src/provider.tsx#L37-L49)

## 3. Desired State
- **New Behavior**:
  - Provider tracks `lastSeenSeq` from `msg.header.seq` (optional) and sends `protocol.resume` with `payload.last_seen_seq`.
  - Runtime orders `ui.patch` by `header.seq` (or a defined fallback policy if seq missing).
  - (Optional but recommended) Provider typed-validates `protocol.resume` and other core payloads once schemas exist.
- **Constraints**:
  - Backwards-compatible: if `header.seq` is absent, do not break rendering; just skip resume/order guarantees.
  - Keep changes minimal and tested (less code).

## 4. Implementation Steps
1. **Update provider resume tracking**:
   - Replace `lastSeenVersionRef` tracking with `lastSeenSeqRef` tracking from `msg.header.seq`.
   - Update outbound resume message payload shape to `last_seen_seq`.
2. **Update runtime ordering**:
   - Replace `parseInt(header.version)` ordering with `header.seq` ordering for `ui.patch`.
3. **Update tests**:
   - Update `agentprinter-react/tests/transport-backoff.test.tsx` expectations for the resume payload shape.
   - Add/adjust a test proving `ui.patch` ordering uses seq and ignores stale patches by seq.

## 5. Acceptance Criteria (Verification)
- [ ] Resume message uses `payload.last_seen_seq` and is based on `header.seq`.
- [ ] `ui.patch` ordering uses `header.seq` (no longer parses `header.version`).
- [ ] Tests:
  - [ ] Run: `cd agentprinter-react && bun test`
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Update **Rules & Constraints** to define ordering/resume field semantics (`seq` vs protocol version)
    - Update **Edge Cases** to mention “no seq → no resume guarantees”
    - Update **Use Cases** + **Trace** rows for resume + ordering changes with evidence links
    - Keep diagrams at exactly **2** (update if materially changed)

## 6. Dependencies
- [ ] Task: [Add explicit sequencing + resume contracts](./2026-02-01-protocol-seq-and-resume-contract.md)
- [ ] Task: [Backend emits `header.seq` and replays on `protocol.resume`](./2026-02-01-backend-assign-seq-and-handle-resume.md)

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Verification is concrete (`bun test`)
- [ ] Scope maintenance lists traces + evidence updates explicitly

