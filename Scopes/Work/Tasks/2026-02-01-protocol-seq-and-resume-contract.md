# Task: Add explicit sequencing + resume contracts

## 1. Summary
**Goal**: Introduce an explicit message sequencing field and a typed resume payload in the exported protocol schema, so ordering/resume no longer conflates “protocol version” with “message sequence”.
**Context**: `PROJECT_GOAL.md` calls for protocol version negotiation plus reliable ordering/resume; current implementation conflates these concepts in `MessageHeader.version`.

## 2. Current State (Scopes)
- **Anchor Scope**: [Protocol Schema & Codegen](../../Product/Contracts/Protocol_Schema.md)
- **Current Behavior**:
  - `MessageHeader.version` exists and is used for protocol version negotiation (semver-like). [agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py:L19-L27](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py#L19-L27), [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L109-L131](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L109-L131)
  - The exported schema includes `message`, `page`, `event`, `error`, `action`, `navigation`, `tool`, `schema_contract`, etc., but does not include a typed resume payload contract. [agentprinter-fastapi/scripts/export_schema.py:L24-L41](../../../agentprinter-fastapi/scripts/export_schema.py#L24-L41)
  - The React runtime currently uses `MessageHeader.version` as a numeric ordering signal (via `parseInt(...)`) for `ui.patch`, conflicting with the semver/protocol meaning. [agentprinter-react/src/runtime.tsx:L90-L106](../../../agentprinter-react/src/runtime.tsx#L90-L106)
- **Evidence**:
  - `MessageHeader` definition (currently: `version: str = "1.0.0"`). [agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py:L19-L27](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py#L19-L27)

## 3. Desired State
- **New Behavior**:
  - The protocol schema includes `MessageHeader.seq?: integer` (monotonic per session, used for ordering/resume).
  - The protocol schema includes a typed `ResumePayload` (or equivalent) with `last_seen_seq: integer`.
  - `MessageHeader.version` remains protocol-version negotiation (e.g., `1.0.0`), not used as an ordering counter.
- **Constraints**:
  - Keep the schema changes minimal and backwards-compatible: `seq` is optional.
  - Prefer reuse over new abstractions (follow `WRITE_STYLE.md` “Less code = better work”). [Scopes/Work/Standards/WRITE_STYLE.md](../Standards/WRITE_STYLE.md)

## 4. Implementation Steps
1. **Contracts (backend models)**:
   - Add `seq: int | None` to `MessageHeader` (optional).
   - Add a `ResumePayload` Pydantic model with `last_seen_seq: int`.
2. **Schema export**:
   - Extend `ProtocolContract` to include the new `resume` contract field (e.g., `resume: ResumePayload`), so it appears in `contracts/schemas.json`.
3. **Frontend codegen**:
   - Run schema export + codegen so `types.ts` and `contracts.ts` include `seq` and `resume` schemas.

## 5. Acceptance Criteria (Verification)
- [ ] Backend schema export includes the new header field and resume contract:
  - [ ] Run: `python agentprinter-fastapi/scripts/export_schema.py`
  - [ ] Confirm `contracts/schemas.json` includes `MessageHeader.seq` and `resume` payload shape (grep/inspect file).
- [ ] Frontend codegen succeeds:
  - [ ] Run: `cd agentprinter-react && bun run codegen`
- [ ] Tests remain green:
  - [ ] Run: `cd agentprinter-fastapi && uv run pytest`
  - [ ] Run: `cd agentprinter-react && bun test`
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Add “seq + resume contract” to **Summary** and **Rules & Constraints**
    - Add at least 1 new **Use Case** for “resume contract exists in schema”
    - Update exactly **2** diagrams if they materially change (otherwise keep diagrams unchanged)
    - Add evidence links to the new models and updated `export_schema.py`
  - [ ] Update `Scopes/GRAPH.md` evidence table if any new cross-scope edge is introduced or an existing edge’s evidence changes.

## 6. Dependencies
- None (this is the foundational contract change; subsequent resume/order tasks depend on it).

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Verification commands come from `Scopes/DEVELOPER_INFO.md` where possible
- [ ] Scope maintenance lists traces + evidence updates explicitly

