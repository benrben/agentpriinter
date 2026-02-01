# Task: Backend emits `header.seq` and replays on `protocol.resume`

## 1. Summary
**Goal**: Make the backend runtime assign a monotonic `header.seq` to outbound messages (per session), and handle inbound `protocol.resume` by replaying missed messages to the reconnecting client.
**Context**: `PROJECT_GOAL.md` calls for best-effort resume “by last seen version”; the frontend already sends a resume message, but the backend currently ignores it.

## 2. Current State (Scopes)
- **Anchor Scope**: [Backend WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Current Behavior**:
  - Backend only routes inbound `user.action` messages; other message types are ignored (no resume handling). [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L165-L224](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L165-L224)
  - Fallback HTTP polling stores per-session message queues and supports cursor-based retrieval, but the WebSocket path does not expose replay/resume semantics. [agentprinter-fastapi/src/agentprinter_fastapi/transports.py:L32-L85](../../../agentprinter-fastapi/src/agentprinter_fastapi/transports.py#L32-L85)
  - The connection manager fans out outbound messages to the polling queue and SSE transport when a `session_id` exists (or defaults to `"default"`). [agentprinter-fastapi/src/agentprinter_fastapi/manager.py:L64-L80](../../../agentprinter-fastapi/src/agentprinter_fastapi/manager.py#L64-L80)
- **Evidence**:
  - No `protocol.resume` handling in the message loop. [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L165-L224](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L165-L224)

## 3. Desired State
- **New Behavior**:
  - Every outbound message includes `header.seq` (monotonic increasing per `session_id`).
  - When the server receives `protocol.resume { last_seen_seq }`, it replays queued messages with `seq > last_seen_seq` to that client (best effort).
- **Constraints**:
  - Prefer reusing the existing per-session queue in `HTTPPollingTransport` as the “source of truth” for replay (less code).
  - Keep replay bounded (e.g., max N messages) to avoid unbounded memory or huge bursts.

## 4. Implementation Steps
1. **Assign `header.seq` for outbound messages**:
   - Ensure the message has a `session_id` (use current logic: header session_id or `"default"`). [agentprinter-fastapi/src/agentprinter_fastapi/manager.py:L66-L71](../../../agentprinter-fastapi/src/agentprinter_fastapi/manager.py#L66-L71)
   - When enqueueing to `HTTPPollingTransport`, stamp `header.seq` based on the queue index (cursor) so it’s stable across transports.
2. **Handle inbound `protocol.resume`**:
   - Extend the WebSocket receive loop to detect `message.type == "protocol.resume"`.
   - Validate payload against the new resume contract (introduced in the schema task).
   - Load queued messages for the session and send the slice `(last_seen_seq+1 .. last_seen_seq+limit)` to the WebSocket client.
3. **Tests**:
   - Add/extend a backend test proving:
     - outbound messages include `header.seq`
     - after disconnect + resume, the client receives replayed messages in order

## 5. Acceptance Criteria (Verification)
- [ ] `protocol.resume` is handled in the WS loop and triggers replay.
- [ ] Outbound messages include `header.seq` monotonically increasing per session.
- [ ] Tests:
  - [ ] Add or update pytest coverage under `agentprinter-fastapi/tests/` (prefer a focused test file).
  - [ ] Run: `cd agentprinter-fastapi && uv run pytest`
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md`:
    - Add a **Use case**: “Client reconnects and requests replay via protocol.resume”
    - Add **Trace** row(s) for `protocol.resume` handling and replay send loop
    - Update **Rules & Constraints** to document replay bounds (max messages) with evidence
    - Keep diagrams at exactly **2** (update if flow changes materially)
  - [ ] Update `Scopes/GRAPH.md` evidence table if replay introduces a new dependency on the polling transport (or strengthens it).

## 6. Dependencies
- [ ] Task: [Add explicit sequencing + resume contracts](./2026-02-01-protocol-seq-and-resume-contract.md)

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Verification is concrete and repeatable (`uv run pytest`)
- [ ] Scope maintenance lists traces + evidence updates explicitly

