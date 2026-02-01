# Task: Bound the HTTP polling message queue (retention policy + plan)

## 1. Summary
**Goal**: Define and document a retention policy for the HTTP polling transport message queue to prevent unbounded memory growth and to make resume replay behavior well-defined under retention.
**Context**: The polling transport stores per-session message lists that are appended to forever and never pruned.

## 2. Current State (Scopes)
- **Anchor Scope**: [Backend WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Current Behavior**:
  - Polling transport keeps `message_queues: dict[str, list[dict]]` in memory. [agentprinter-fastapi/src/agentprinter_fastapi/transports.py:L32-L37](../../../agentprinter-fastapi/src/agentprinter_fastapi/transports.py#L32-L37)
  - `enqueue_message()` appends to the per-session list and never prunes. [agentprinter-fastapi/src/agentprinter_fastapi/transports.py:L38-L43](../../../agentprinter-fastapi/src/agentprinter_fastapi/transports.py#L38-L43)
  - `dequeue_messages()` slices but does not remove or expire old entries. [agentprinter-fastapi/src/agentprinter_fastapi/transports.py:L44-L61](../../../agentprinter-fastapi/src/agentprinter_fastapi/transports.py#L44-L61)
  - The manager derives `header.seq` from polling queue length (`next_seq = queue_len + 1`). [agentprinter-fastapi/src/agentprinter_fastapi/manager.py:L69-L79](../../../agentprinter-fastapi/src/agentprinter_fastapi/manager.py#L69-L79)

## 3. Desired State
- **New Behavior**:
  - A clear retention policy exists (cap size and/or TTL) for polling queues.
  - Resume replay behavior is defined under retention (e.g., “if last_seen_seq is older than retained window, server sends a reset signal or only replays what it has”).
- **Constraints**:
  - Keep it simple and in-memory for now; avoid introducing new storage layers in this task.
  - Ensure `header.seq` semantics remain coherent if old messages are pruned (avoid reusing seq numbers).

## 4. Implementation Steps
1. **Choose a retention policy** (write down the decision):
   - Option A: fixed cap per session (e.g., keep last N messages).
   - Option B: time-based TTL per session (expire messages older than X seconds/minutes).
   - Option C: hybrid (cap + TTL).
2. **Define pruning mechanics**:
   - When pruning occurs (on enqueue, on dequeue, periodic sweep).
3. **Define resume behavior under retention**:
   - What happens when `last_seen_seq` is too old.
4. **Write the decision note under Scopes**:
   - Create `Scopes/Research/2026-02-02-http-polling-retention-policy.md` describing:
     - chosen policy
     - impact on `seq` and resume replay
     - any required protocol signal (e.g., `protocol.error` or `protocol.reset`) if needed

## 5. Acceptance Criteria (Verification)
- [ ] A decision note exists: `Scopes/Research/2026-02-02-http-polling-retention-policy.md`
  - [ ] Explicit retention policy (cap/TTL) with numeric defaults.
  - [ ] Explicit resume behavior when requested replay falls outside retention.
  - [ ] Includes at least 3 evidence links showing current unbounded behavior and seq assignment dependency.
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md`:
    - Add the retention policy to **Rules & Constraints** with evidence link targets (once implemented).
    - Add a resume edge case to **Edge Cases & Failure Outcomes** (“resume beyond retention window”).
    - Keep diagrams at exactly **2**.

## 6. Dependencies
- [ ] Task: [Define seq/resume semantics + session identity across transports (WS/SSE/poll)](./2026-02-02-08-seq-resume-and-session-identity-contract.md)

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Retention policy is compatible with monotonic seq semantics (no seq reuse)
- [ ] Resume behavior is defined, not “best effort” hand-waving

