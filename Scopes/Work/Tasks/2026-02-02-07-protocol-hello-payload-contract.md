# Task: Model `protocol.hello` payload explicitly (contract + schema export)

## 1. Summary
**Goal**: Define a typed `HelloPayload` contract for `protocol.hello` so the handshake payload is schema-exported and can be validated/used consistently by the frontend and backend.
**Context**: The backend emits `protocol.hello` with an ad-hoc payload dict, but the schema export has no specific `HelloPayload` model.

## 2. Current State (Scopes)
- **Anchor Scope**: [Protocol Schema & Codegen](../../Product/Contracts/Protocol_Schema.md)
- **Current Behavior**:
  - Backend sends a `protocol.hello` message with a payload containing `"message"` and `"server"` fields. [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L131-L142](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L131-L142)
  - The protocol envelope defines `Message.payload` as an untyped `dict[str, Any]`. [agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py:L34-L38](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py#L34-L38)
  - Schema export roots include `message`, `page`, `event`, `error`, `resume`, etc., but there is no `hello`/`HelloPayload` field in `ProtocolContract`. [agentprinter-fastapi/scripts/export_schema.py:L25-L44](../../../agentprinter-fastapi/scripts/export_schema.py#L25-L44)

## 3. Desired State
- **New Behavior**:
  - A `HelloPayload` model exists in the backend schema module(s) and is included in schema export (so it appears in `contracts/schemas.json`).
  - Frontend codegen produces a Zod schema for `HelloPayload`.
  - (Decision-driven) The hello payload fields are explicitly documented (and evolve intentionally).
- **Constraints**:
  - Keep the payload minimal: only fields that are already emitted or clearly needed for cross-stack behavior.
  - Prefer backwards compatibility: add fields rather than rename/remove, unless versioned.

## 4. Implementation Steps
1. **Define the `HelloPayload` contract (docs-first)**:
   - Start from what is already emitted: `message`, `server`. [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L131-L138](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L131-L138)
   - Decide whether to include additional identity/version fields (if needed for session negotiation): e.g., `protocol_version`, `session_id`.
2. **Add `HelloPayload` model to backend schemas**:
   - Place it alongside other protocol payload models (e.g., `schemas/protocol.py`).
3. **Include it in schema export**:
   - Add `hello: HelloPayload` (or similarly named root) to `ProtocolContract` so it appears in `$defs`. [agentprinter-fastapi/scripts/export_schema.py:L25-L44](../../../agentprinter-fastapi/scripts/export_schema.py#L25-L44)
4. **Write the decision note under Scopes**:
   - Create `Scopes/Research/2026-02-02-protocol-hello-payload.md` with:
     - payload schema
     - versioning rules for changes
     - evidence links

## 5. Acceptance Criteria (Verification)
- [ ] A decision note exists: `Scopes/Research/2026-02-02-protocol-hello-payload.md` (schema + rationale + evidence).
- [ ] Schema export includes `HelloPayload`:
  - [ ] Run: `python agentprinter-fastapi/scripts/export_schema.py` (from `Scopes/DEVELOPER_INFO.md`). [Scopes/DEVELOPER_INFO.md:L8-L9](../../DEVELOPER_INFO.md#L8-L9)
  - [ ] Confirm `contracts/schemas.json` contains a hello payload model/def.
- [ ] Frontend codegen succeeds:
  - [ ] Run: `cd agentprinter-react && bun run codegen`. [Scopes/DEVELOPER_INFO.md:L8-L9](../../DEVELOPER_INFO.md#L8-L9)
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Add hello payload model to **Rules & Constraints** and **Use Cases** with evidence.
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md`:
    - Document hello payload fields with evidence.
    - Keep diagrams at exactly **2**.

## 6. Dependencies
- None (but coordinate with any tasks that change handshake/session identity).

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Evidence links point to the exact current hello emission and schema export root
- [ ] Verification commands match `Scopes/DEVELOPER_INFO.md`

