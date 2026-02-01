# Task: React README + Provider API (`serverUrl`, `appId`, `getToken`)

## 1. Summary
**Goal**: Align `@agentprinter/react`’s public API + README with the “10 minute integration” promise: a single Provider + Runtime component, with simple auth and app identity hooks.
**Context**: `PROJECT_GOAL.md` describes `<AgentPrinterProvider serverUrl appId getToken>`; today the provider expects a raw `url` string and the README is a generic Bun template.

## 2. Current State (Scopes)
- **Anchor Scope**: [Remote UI Runtime (React)](../../Product/Frontend/Remote_UI_Runtime.md)
- **Current Behavior**:
  - Provider signature is `{ url, children }`. [agentprinter-react/src/provider.tsx:L21-L27](../../../agentprinter-react/src/provider.tsx#L21-L27)
  - Runtime composes `<AgentPrinterProvider url={url}>`. [agentprinter-react/src/runtime.tsx:L142-L147](../../../agentprinter-react/src/runtime.tsx#L142-L147)
  - README is a generic Bun scaffold and does not document embedding into an existing React app. [agentprinter-react/README.md:L1-L15](../../../agentprinter-react/README.md#L1-L15)

## 3. Desired State
- **New Behavior**:
  - README provides copy/pasteable integration steps for an existing React/Next.js app.
  - Provider can be constructed from a `serverUrl` (HTTP base) rather than requiring consumers to hand-build a `ws://.../ws?...` URL.
  - Provider accepts:
    - `appId?: string` and `sessionId?: string` (identity hints)
    - `getToken?: () => string | Promise<string>` (auth hook) that is attached to the connection (e.g., query param or header via a negotiated mechanism).
  - Maintain backwards compatibility: `url` remains supported.
- **Constraints**:
  - Keep changes minimal and avoid inventing a complex auth mechanism; the goal is “hooks”, not “auth framework”.
  - Avoid breaking the demo (`examples/frontend_demo`) wiring.

## 4. Implementation Steps
1. **Provider API**:
   - Add new props (`serverUrl`, `appId`, `sessionId`, `getToken`) and derive the final WebSocket URL internally.
   - Keep existing `url` prop supported (mutually exclusive rules documented).
2. **Connection identity**:
   - If `appId/sessionId` exist, include them in the connection (likely as query params) so the backend can reflect them in message headers.
3. **README**:
   - Replace Bun scaffold README content with:
     - install step
     - minimal Provider + Runtime usage
     - devtools usage
     - how to run against the backend demo
4. **Tests**:
   - Add/adjust tests to verify:
     - URL construction from `serverUrl` + optional identity params
     - behavior is unchanged when using `url` directly

## 5. Acceptance Criteria (Verification)
- [ ] README documents integration and demo usage:
  - [ ] Manual check: `agentprinter-react/README.md` includes a Quick Start with `<AgentPrinterProvider ...>` and `<AgentPrinterRuntime />`.
- [ ] Tests pass:
  - [ ] Run: `cd agentprinter-react && bun test`
- [ ] Demo still runs (manual smoke):
  - [ ] Run: `cd examples/frontend_demo && bun run dev`
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Frontend/Remote_UI_Runtime.md`:
    - Update **Users & Triggers** and **Rules & Constraints** to reflect new provider props (serverUrl/appId/getToken)
    - Add evidence links to provider prop definitions and tests
  - [ ] Update `Scopes/DEVELOPER_INFO.md` only if new dev commands are introduced.

## 6. Dependencies
- None (API/docs polish; resume/seq work is separate).

## Audit Checklist
- [ ] Anchor Scope is under `Scopes/Product/**`
- [ ] Backwards compatibility preserved (`url` still works)
- [ ] Verification is concrete (`bun test`)

