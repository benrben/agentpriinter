# Task: Define seq/resume semantics + session identity across transports (WS/SSE/poll)

## 1. Summary
**Goal**: Write down a single “seq + resume + session identity” contract that applies consistently across WebSocket, SSE, and HTTP polling, and enumerate the code paths that must follow it.
**Context**: Today, session identity can silently default to `"default"`, and message sequencing (`header.seq`) is only assigned for messages that pass through the connection manager’s fan-out path (not for direct `websocket.send_json`).

## 2. Current State (Scopes)
- **Anchor Scope**: [Backend WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Current Behavior**:
  - Backend defaults `session_id` to `"default"` when extracting from headers for fan-out. [agentprinter-fastapi/src/agentprinter_fastapi/manager.py:L57-L63](../../../agentprinter-fastapi/src/agentprinter_fastapi/manager.py#L57-L63)
  - Backend stamps `header.seq` based on the current polling queue length, but only inside the manager send path. [agentprinter-fastapi/src/agentprinter_fastapi/manager.py:L64-L79](../../../agentprinter-fastapi/src/agentprinter_fastapi/manager.py#L64-L79)
  - Backend resume handler derives session identity from `message.header.session_id` (or `"default"`) and replays using `cursor=last_seen_seq`. [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L225-L235](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L225-L235)
  - Polling transport defines `cursor` as a **message index** into an unbounded list. [agentprinter-fastapi/src/agentprinter_fastapi/transports.py:L44-L61](../../../agentprinter-fastapi/src/agentprinter_fastapi/transports.py#L44-L61)
  - Frontend resume message header does not include `session_id`. [agentprinter-react/src/provider.tsx:L78-L92](../../../agentprinter-react/src/provider.tsx#L78-L92)
  - Backend hello is sent directly via `websocket.send_json(...)` (not via manager), so it will not be seq-stamped. [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L131-L142](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L131-L142)

## 3. Desired State
- **New Behavior**:
  - Session identity is explicit and stable across reconnects:
    - Clients and server agree on how `session_id` is assigned and propagated (header and/or query param).
  - `header.seq` stamping rules are explicit:
    - Which outbound messages must have `seq` (hello/render/events/patches).
    - What “monotonic” means (per session).
  - `protocol.resume` semantics are explicit:
    - Which messages are replayable.
    - How `last_seen_seq` relates to polling cursor/index.
- **Constraints**:
  - Keep it minimal and evidence-backed (document what exists; propose the smallest set of changes to remove ambiguity).
  - Avoid any behavior that mixes multiple clients into the same `"default"` session implicitly.

## 4. Implementation Steps
1. **Define “session_id source of truth”** (choose and document):
   - Option A: server assigns session_id and sends it to client (hello header/payload); client echoes it back in subsequent message headers.
   - Option B: client supplies session_id (query param) on connect; server echoes/uses it everywhere.
2. **Define `seq` stamping scope**:
   - Enumerate all backend outbound code paths (manager broadcast, direct `send_json` in router) and decide which must stamp seq.
3. **Define resume semantics precisely**:
   - What `last_seen_seq` means (e.g., last processed message seq where \(seq = index + 1\) in polling queue).
   - What the replay window/limit is.
4. **Write the contract note under Scopes**:
   - Create `Scopes/Research/2026-02-02-seq-resume-session-contract.md` with:
     - contract rules
     - examples (hello, patch, resume)
     - a list of backend code paths that must comply

## 5. Acceptance Criteria (Verification)
- [ ] A decision note exists: `Scopes/Research/2026-02-02-seq-resume-session-contract.md`
  - [ ] Explicitly defines session_id assignment + propagation rules.
  - [ ] Explicitly defines seq stamping scope and ordering guarantees.
  - [ ] Explicitly defines resume semantics and how it maps to polling cursor/index.
  - [ ] Includes at least 5 evidence links from backend manager/router/transports + frontend provider.
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md`:
    - Update **Rules & Constraints** with the contract.
    - Update **Trace** table entries for hello/seq stamping and resume replay.
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Document what header fields the provider must include (session_id/seq) to make resume reliable.
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Ensure docs align: `seq` for ordering, `version` for protocol negotiation.
    - Keep diagrams at exactly **2**.

## 6. Dependencies
- [ ] Task: [Model `protocol.hello` payload explicitly (contract + schema export)](./2026-02-02-07-protocol-hello-payload-contract.md)

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Contract removes implicit `"default"` session mixing as a default behavior
- [ ] Replay semantics are defined in terms of existing cursor/index behavior (or explicitly changed)

