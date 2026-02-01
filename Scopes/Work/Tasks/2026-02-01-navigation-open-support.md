# Task: Support `protocol.navigate.open` (modal/drawer/new tab) in React runtime

## 1. Summary
**Goal**: Implement handling for the `Navigation.open` field so server-driven navigation can open routes in the same tab, a new tab/window, or via modal/drawer semantics (via adapter).
**Context**: The navigation contract includes `open`, but the current React runtime ignores it.

## 2. Current State (Scopes)
- **Anchor Scope**: [Remote UI Runtime (React)](../../Product/Frontend/Remote_UI_Runtime.md)
- **Current Behavior**:
  - `Navigation` contract includes `open: str` (default `"same"`). [agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py:L12-L17](../../../agentprinter-fastapi/src/agentprinter_fastapi/schemas/protocol.py#L12-L17)
  - React runtime handles `protocol.navigate` by calling the navigation adapter with `to`, `replace`, and `params`, but it does not pass `open`. [agentprinter-react/src/runtime.tsx:L107-L124](../../../agentprinter-react/src/runtime.tsx#L107-L124)

## 3. Desired State
- **New Behavior**:
  - If a `navigationAdapter` is provided, the runtime passes `open` through so apps can implement modal/drawer/new-tab behavior.
  - If no adapter is provided:
    - `open: "same"` behaves as today (history push/replace)
    - `open: "new"` opens a new tab/window (best effort) rather than silently ignoring
- **Constraints**:
  - Keep it minimal: don’t build a modal system inside the runtime; delegate modal/drawer semantics to the adapter.

## 4. Implementation Steps
1. **Adapter type update**:
   - Extend `NavigationAdapter.navigate(...)` options to include `open?: string` (or a small union).
2. **Runtime update**:
   - Pass `payload.open` through to adapter.
   - Implement a default fallback behavior for `open !== "same"` when no adapter exists.
3. **Tests**:
   - Add/extend `agentprinter-react/tests/ui-patch-nav.test.tsx` (or a new focused test) asserting:
     - adapter receives `open`
     - fallback opens a new window when `open: "new"` (mock `window.open`)

## 5. Acceptance Criteria (Verification)
- [ ] Tests pass:
  - [ ] Run: `cd agentprinter-react && bun test`
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Update **What Happens** / **Rules & Constraints** to reflect `open` handling
    - Add evidence links to the updated runtime + tests

## 6. Dependencies
- None.

## Audit Checklist
- [ ] Anchor Scope is under `Scopes/Product/**`
- [ ] `open` is not silently ignored anymore
- [ ] Modal/drawer behavior is adapter-driven (runtime stays thin)

