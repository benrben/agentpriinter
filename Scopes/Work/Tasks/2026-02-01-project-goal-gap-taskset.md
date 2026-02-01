# Task: Close PROJECT_GOAL gaps (ordered task set)

## 1. Summary
**Goal**: Produce a sequenced set of small tasks that, when completed, closes the remaining gaps between `Scopes/Work/Planning/PROJECT_GOAL.md` and the currently implemented product scopes.
**Context**: Derived from [Scopes/Work/Planning/PROJECT_GOAL.md](../Planning/PROJECT_GOAL.md) and the current top-level Product scopes listed in [Scopes/INDEX.md](../../INDEX.md).

## 2. Current State (Scopes)
- **Anchor Scope**: [Backend WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Current Behavior**: Core backend+frontend runtime exists (WebSocket + SSE/HTTP fallback, schema/codegen, React runtime + devtools), but several “production-ready by default” contracts from `PROJECT_GOAL.md` are either incomplete or implemented with mismatched semantics.
- **Evidence**:
  - Backend routes only `user.action` inbound messages; other types (e.g. `protocol.resume`) are currently ignored. [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L165-L224](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L165-L224)
  - Frontend runtime currently uses `MessageHeader.version` for `ui.patch` ordering by `parseInt(...)`, which conflicts with protocol-version semantics. [agentprinter-react/src/runtime.tsx:L90-L106](../../../agentprinter-react/src/runtime.tsx#L90-L106)
  - Frontend provider sends a `protocol.resume` message with `payload.last_seen_version`, but there is no server-side handler. [agentprinter-react/src/provider.tsx:L78-L97](../../../agentprinter-react/src/provider.tsx#L78-L97)
  - `Bindings` contract is currently a direct state path mapping with no computed operators (if/format/concat). [agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py:L23-L27](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py#L23-L27), [agentprinter-react/src/renderer.tsx:L1890-L1899](../../../agentprinter-react/src/renderer.tsx#L1890-L1899)
  - `SchemaContract` exists in the protocol schema, but the React SDK does not yet render schema-driven forms from it. [agentprinter-fastapi/src/agentprinter_fastapi/schemas/tools.py:L13-L19](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/tools.py#L13-L19), [agentprinter-react/src/contracts.ts:L199-L204](../../../agentprinter-react/src/contracts.ts#L199-L204)

## 3. Desired State
- **New Behavior**: Completing the linked tasks below closes the remaining feature gaps called out in `PROJECT_GOAL.md`, with clear message sequencing + resume semantics, computed bindings, schema-driven forms, and documented “10-minute integration” APIs.

## 4. Implementation Steps
Execute the tasks in this order (each task is scoped to 1–4 hours):
1. [Task: Define the one-way “Component Catalog Contract” (frontend registry → backend)](./2026-02-02-01-one-way-component-catalog-contract.md)
2. [Task: Decide backend policy for unknown component types (consume the catalog)](./2026-02-02-02-backend-consume-component-catalog-policy.md)
3. [Task: Decide where the component catalog artifact lives + how it’s generated/consumed](./2026-02-02-03-component-catalog-artifact-generation-path.md)
4. [Task: Unify the `ui.patch` contract end-to-end (design + mapping plan)](./2026-02-02-04-ui-patch-contract-alignment-plan.md)
5. [Task: Unify the `state.patch` contract end-to-end (design decision)](./2026-02-02-05-state-patch-contract-alignment-plan.md)
6. [Task: Decide what to do about patch coalescing payload shape (batch vs remove)](./2026-02-02-06-patch-coalescing-batch-protocol-decision.md)
7. [Task: Model `protocol.hello` payload explicitly (contract + schema export)](./2026-02-02-07-protocol-hello-payload-contract.md)
8. [Task: Define seq/resume semantics + session identity across transports (WS/SSE/poll)](./2026-02-02-08-seq-resume-and-session-identity-contract.md)
9. [Task: Bound the HTTP polling message queue (retention policy + plan)](./2026-02-02-09-bound-http-polling-queue.md)
10. [Task: Decide whether to introduce typed “message type → payload” unions (vs generic payload)](./2026-02-02-10-type-to-payload-union-decision.md)
11. [x] [Task: Add explicit sequencing + resume contracts](./2026-02-01-protocol-seq-and-resume-contract.md)
12. [x] [Task: Backend emits seq + handles protocol.resume replay](./2026-02-01-backend-assign-seq-and-handle-resume.md)
13. [x] [Task: Frontend uses seq for ordering + resume](./2026-02-01-frontend-use-seq-for-ordering-and-resume.md)
14. [x] [Task: Computed bindings (if/concat/format)](./2026-02-01-computed-bindings-ops.md)
15. [x] [Task: Align `user.action` emission with backend `ActionPayload` validation](./2026-02-01-action-contract-alignment.md)
16. [x] [Task: Schema-driven form component (SchemaContract)](./2026-02-01-schema-driven-forms.md)
17. [Task: Support `protocol.navigate.open` (modal/drawer/new tab) in React runtime](./2026-02-01-navigation-open-support.md)
18. [Task: Tool contract metadata messages (backend emit + frontend surface)](./2026-02-01-tool-contract-metadata-messages.md)
19. [Task: Component bank minimum version negotiation](./2026-02-01-component-bank-min-version-negotiation.md)
20. [Task: Auth refresh + permission hints](./2026-02-01-auth-refresh-and-permissions-hints.md)
21. [Task: FastAPI install API + README (10-minute integration)](./2026-02-01-fastapi-install-api-and-readme.md)
22. [Task: React README + Provider API (serverUrl/appId/getToken)](./2026-02-01-react-readme-and-provider-api.md)

## 5. Acceptance Criteria (Verification)
- [ ] All tasks listed above are present under `Scopes/Work/Tasks/` and each contains concrete verification commands pulled from `Scopes/DEVELOPER_INFO.md`.

## 6. Dependencies
- None (this is the top-level ordering task).

## Audit Checklist
- [ ] Anchor Scope is under `Scopes/Product/**`
- [ ] Every linked task includes: evidence-backed current state, concrete verification, and explicit scope maintenance instructions

