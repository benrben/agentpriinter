# Task: Define the one-way “Component Catalog Contract” (frontend registry → backend)

## 1. Summary
**Goal**: Decide the exported “Component Catalog Contract” shape, with the frontend registry as the single source of truth, so the backend can validate/guard against unknown component types without duplicating component definitions.
**Context**: The React runtime already has a component registry + metadata hooks (props schema); the backend currently treats `ComponentNode.type` as an unconstrained string.

## 2. Current State (Scopes)
- **Anchor Scope**: [Remote UI Runtime (React)](../../Product/Frontend/Remote_UI_Runtime.md)
- **Current Behavior**:
  - Frontend has a registry keyed by component type strings plus a `registerComponent(...)` API with optional `propsSchema` metadata. [agentprinter-react/src/renderer.tsx:L1693-L1731](../../../agentprinter-react/src/renderer.tsx#L1693-L1731)
  - Frontend uses registry metadata to validate props and render a fallback placeholder on invalid props. [agentprinter-react/src/renderer.tsx:L1863-L1900](../../../agentprinter-react/src/renderer.tsx#L1863-L1900)
  - Unknown component types already render a placeholder (not a hard crash). [agentprinter-react/src/renderer.tsx:L1743-L1784](../../../agentprinter-react/src/renderer.tsx#L1743-L1784)
  - Backend schema allows any string `ComponentNode.type` (no catalog validation today). [agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py:L62-L71](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/ui.py#L62-L71)

## 3. Desired State
- **New Behavior**:
  - There is a documented “Component Catalog Contract” whose **source of truth is the frontend registry**.
  - The contract can be exported as an artifact (e.g., JSON manifest) that a backend can consume to validate template/page component types.
- **Constraints**:
  - Keep it minimal (“less code = better work”): start with a stable list of component `type` keys, and only add richer metadata if it’s actually needed.
  - Avoid serializing non-serializable runtime schemas; if “props schema” is included, define an intentionally lossy/portable representation (e.g., `has_props_schema: boolean`, or a JSON schema only when available).

## 4. Implementation Steps
1. **Inventory what’s already available**:
   - Identify what stable info exists in the registry today (keys + optional metadata). [agentprinter-react/src/renderer.tsx:L1693-L1739](../../../agentprinter-react/src/renderer.tsx#L1693-L1739)
2. **Choose the contract shape** (write it down as a small “contract note”):
   - Required fields (recommended): `catalog_version`, `generated_at`, `components: string[]`.
   - Optional per-component metadata (only if it’s truly useful): e.g. `has_props_schema`, `has_event_schema`.
3. **Define an example JSON manifest**:
   - Include at least 5 real component keys from the registry.
4. **Decide versioning rules**:
   - What constitutes a breaking change for the catalog (key removed/renamed, semantics changed).
5. **Write the decision note under Scopes**:
   - Create `Scopes/Research/2026-02-02-component-catalog-contract.md` documenting the chosen shape + rationale + example JSON.

## 5. Acceptance Criteria (Verification)
- [ ] A decision note exists: `Scopes/Research/2026-02-02-component-catalog-contract.md`
  - [ ] Includes a JSON example of the manifest with real component keys.
  - [ ] Explicitly states the one-way direction: frontend registry → exported manifest → backend consumption.
  - [ ] Contains at least 3 evidence links to the registry + metadata usage in code.
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Add/refresh **Rules & Constraints** describing “registry is truth” + that a catalog artifact exists (link to the research note).
    - Add at least 1 new **Trace** step showing “registry → catalog artifact” (even if artifact not implemented yet, mark it as `[Planned]` and keep evidence strictly about the registry).
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/Product/Contracts/Protocol_Schema.md`:
    - Add a short section clarifying the catalog is **not** currently produced by backend schema export (and will be a sibling contract/artifact).
    - Keep diagrams at exactly **2**.
  - [ ] Update `Scopes/GRAPH.md` if you add a new explicit cross-scope relation (e.g., “Remote UI Runtime exports component catalog”).

## 6. Dependencies
- None (foundational decision for subsequent catalog consumption + pipeline tasks).

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Every “current state” claim has evidence links
- [ ] Acceptance criteria are observable (a file exists + contains required sections/links)

