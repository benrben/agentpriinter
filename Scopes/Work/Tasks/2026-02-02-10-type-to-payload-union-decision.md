# Task: Decide whether to introduce typed “message type → payload” unions (vs generic payload)

## 1. Summary
**Goal**: Make an explicit decision about whether the protocol envelope should remain “generic payload dict” or evolve into a discriminated union where `type` determines a typed payload schema.
**Context**: Today, both backend and frontend treat `Message.payload` as a generic dict and only a small subset of message types get typed payload validation.

## 2. Current State (Scopes)
- **Anchor Scope**: [Protocol Schema & Codegen](../../Product/Contracts/Protocol_Schema.md)
- **Current Behavior**:
  - Backend protocol envelope defines `Message.payload: dict[str, Any]`. [agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py:L34-L38](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py#L34-L38)
  - Frontend generated `messageSchema` validates `payload` as an unstructured record. [agentprinter-react/src/contracts.ts:L176-L180](../../../agentprinter-react/src/contracts.ts#L176-L180)
  - Frontend provider performs typed payload validation only for `protocol.error` via `errorPayloadSchema`. [agentprinter-react/src/provider.tsx:L37-L49](../../../agentprinter-react/src/provider.tsx#L37-L49)

## 3. Desired State
- **New Behavior**:
  - A clear decision exists:
    - **Option A (keep generic)**: Keep `Message` generic and validate only selected payloads (fast iteration).
    - **Option B (typed unions)**: Introduce a discriminated union contract where `type` implies a specific payload schema (strong correctness).
  - If Option B is chosen, define the minimum viable subset (which message types become typed first).
- **Constraints**:
  - Prefer minimal surface area: don’t type everything at once unless it’s required.
  - Avoid duplicating validation logic across backend and frontend.

## 4. Implementation Steps
1. **List core message types** currently used and their payload sources:
   - `protocol.hello`, `protocol.error`, `protocol.resume`, `ui.render`, `ui.patch`, `state.patch`, `user.action`, `agent.event`.
2. **Evaluate tradeoffs**:
   - Correctness vs flexibility and iteration speed.
   - How typed unions interact with schema export/codegen pipeline.
3. **Choose a direction**:
   - If generic: define “typed payload whitelist” (which message types must be validated) and where (provider vs runtime).
   - If unions: define the union type structure and which payloads are modeled first.
4. **Write the decision note under Scopes**:
   - Create `Scopes/Research/2026-02-02-type-to-payload-union-decision.md` documenting:
     - chosen option
     - phased plan (if any)
     - evidence links

## 5. Acceptance Criteria (Verification)
- [ ] A decision note exists: `Scopes/Research/2026-02-02-type-to-payload-union-decision.md`
  - [ ] States Option A vs Option B and why.
  - [ ] If Option B: lists the first message types to type and the expected enforcement points.
  - [ ] Includes at least 3 evidence links showing current generic envelope + limited typed validation.
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Document the decision (generic vs union) and how payload validation is expected to work.
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Document provider payload validation policy (typed whitelist vs union-driven).
    - Keep diagrams at exactly **2**.

## 6. Dependencies
- None (but related to Task 07 hello payload typing and patch/state payload alignment tasks).

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Decision is explicit and actionable (who validates what, where)
- [ ] “Less code” bias is considered (start small if adopting unions)

