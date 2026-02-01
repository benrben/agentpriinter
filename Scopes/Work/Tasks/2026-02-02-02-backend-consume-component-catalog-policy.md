# Task: Decide backend policy for unknown component types (consume the catalog)

## 1. Summary
**Goal**: Decide what the backend should do when a `ui.render` page/template contains component types not present in the frontend’s exported Component Catalog (strict reject vs lenient allow).
**Context**: Today, backend validation accepts any `ComponentNode.type` string; frontend renders unknown types as a placeholder.

## 2. Current State (Scopes)
- **Anchor Scope**: [Backend WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Current Behavior**:
  - Backend validates templates by parsing JSON into a `Page` model. [agentprinter-fastapi/src/agentprinter_fastapi/templates.py:L7-L30](../../../agentprinter-fastapi/src/agentprinter_fastapi/templates.py#L7-L30)
  - Backend programmatic page construction (`PageBuilder`) accepts arbitrary `type: str` and produces `ComponentNode(type=...)`. [agentprinter-fastapi/src/agentprinter_fastapi/templates.py:L73-L157](../../../agentprinter-fastapi/src/agentprinter_fastapi/templates.py#L73-L157)
  - Backend schema defines `ComponentNode.type: str` (unconstrained). [agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py:L62-L71](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py#L62-L71)
  - Frontend renders unknown component types as a non-crashing placeholder. [agentprinter-react/src/renderer.tsx:L1743-L1784](../../../agentprinter-react/src/renderer.tsx#L1743-L1784)

## 3. Desired State
- **New Behavior**:
  - A written backend policy exists for unknown component types, including where it is enforced:
    - **Strict**: reject templates/pages containing unknown types (return `protocol.error` and/or refuse to send `ui.render`), or
    - **Lenient**: allow unknown types through (frontend placeholder is the fallback), optionally logging/telemetry.
- **Constraints**:
  - Prefer a single enforcement point (avoid scattered checks).
  - Keep it compatible with both template JSON loading and `PageBuilder`-created pages.

## 4. Implementation Steps
1. **Define the decision surface**:
   - Identify which backend paths create/send pages:
     - Template JSON (`load_template`)
     - Programmatic builder (`PageBuilder`)
2. **Pick a policy**:
   - Decide whether unknown types are:
     - a **developer error** (strict), or
     - an **acceptable runtime condition** (lenient).
3. **Choose the enforcement layer** (write down the chosen layer and why):
   - Option A: enforce in `load_template()` (template-time).
   - Option B: enforce in `PageBuilder.build()` (construction-time).
   - Option C: enforce in the send path right before emitting `ui.render` (send-time).
4. **Specify the backend behavior**:
   - Error code/message shape (if strict).
   - What is logged and at what level (if lenient or strict).
5. **Write the decision note under Scopes**:
   - Create `Scopes/Research/2026-02-02-component-catalog-backend-consumption-policy.md`.

## 5. Acceptance Criteria (Verification)
- [ ] A decision note exists: `Scopes/Research/2026-02-02-component-catalog-backend-consumption-policy.md`
  - [ ] States the chosen policy (strict vs lenient) and the enforcement layer.
  - [ ] Includes at least 3 evidence links showing current validation/construction behavior.
  - [ ] Includes a short “failure mode” example (what happens when `type: "unknown_x"` appears).
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md`:
    - Add/refresh **Rules & Constraints** documenting the chosen policy.
    - Add a **Use Case** (strict: “invalid template rejected”; lenient: “unknown types forwarded”).
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Clarify whether unknown types are treated as contract-invalid or tolerated (policy link).
    - Keep diagrams at exactly **2**.

## 6. Dependencies
- [ ] Task: [Define the one-way “Component Catalog Contract” (frontend registry → backend)](./2026-02-02-01-one-way-component-catalog-contract.md)

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Policy choice is explicit + located (layer)
- [ ] Scope maintenance calls out exact sections to update (rules/use cases/traces/evidence)

