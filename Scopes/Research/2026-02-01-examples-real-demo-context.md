# Context: Make `examples/` a Real Demo (Agents + “Living Storybook”)

## Goal (idea)
Turn the current `examples/` folder into a **real demo app** that showcases:
- Real agent runs (LangChain + LangGraph, with graceful fallback when optional deps are missing)
- A “living storybook” that demonstrates the component bank in a browsable, interactive way

## Current Reality (evidence)

### The demo already exists, but “run_agent” is mocked
- Backend demo sets an initial `Page` and streams `agent.event` messages. [examples/backend_demo.py:L200-L226](examples/backend_demo.py#L200-L226)
- The current `run_agent` handler uses a local async generator with simulated `token/tool_call/tool_result/finish` events (not LangChain/LangGraph). [examples/backend_demo.py:L205-L226](examples/backend_demo.py#L205-L226)

### Backend already has optional LangChain + LangGraph adapters
- `agentprinter_fastapi.agent_adapters` defines `LangChainAgentAdapter` and `LangGraphAgentAdapter`. [agentprinter-fastapi/src/agentprinter_fastapi/agent_adapters.py:L1-L259](agentprinter-fastapi/src/agentprinter_fastapi/agent_adapters.py#L1-L259)
- `agentprinter_fastapi.agent_examples` includes example agent builders (but they rely on optional deps and may need modernization). [agentprinter-fastapi/src/agentprinter_fastapi/agent_examples.py:L1-L146](agentprinter-fastapi/src/agentprinter_fastapi/agent_examples.py#L1-L146)

### Frontend runtime can render agent UX panels (already used by the demo UI)
- The component bank includes `agent_run_panel`, `streaming_text`, and `tool_call_panel`. [agentprinter-react/src/renderer.tsx:L1738-L1775](agentprinter-react/src/renderer.tsx#L1738-L1775)
- `AgentRunPanel` + `StreamingText` react to `agent.event` messages by `run_id`. [agentprinter-react/src/components/agent.tsx:L1-L69](agentprinter-react/src/components/agent.tsx#L1-L69)

### There is no Storybook (JS) in the repo today
- No existing Storybook config or dependencies found under `agentprinter-react/` or `examples/frontend_demo/` (manual scan).

## Constraints / Risks

### 1) Optional dependencies + keys
- `agentprinter-fastapi` does not depend on `langchain` or `langgraph`. [agentprinter-fastapi/pyproject.toml:L9-L18](agentprinter-fastapi/pyproject.toml#L9-L18)
- A “real” LangChain demo may require additional packages and often an API key; the demo must degrade gracefully when absent.

### 2) UI patch contract is not fully standardized
- The frontend runtime implements `ui.patch` application with a `target_id` + `operation` payload shape. [agentprinter-react/src/runtime.tsx:L26-L83](agentprinter-react/src/runtime.tsx#L26-L83)
- The backend schemas export `state.patch`, but there is no corresponding `ui.patch` schema yet. [agentprinter-fastapi/src/agentprinter_fastapi/schemas/patch.py:L1-L11](agentprinter-fastapi/src/agentprinter_fastapi/schemas/patch.py#L1-L11)
- Result: a “living storybook” should start with **full `ui.render` page swaps** (lowest risk), then optionally add a formal `ui.patch` contract later.

### 3) Multi-page navigation is not end-to-end
- Frontend supports `protocol.navigate` (URL changes), but it does not request a new page automatically. [agentprinter-react/src/runtime.tsx:L84-L121](agentprinter-react/src/runtime.tsx#L84-L121)
- A demo “multi-page” experience should therefore be implemented as **server-driven view switching** within a single rendered root, or as “navigate + immediate ui.render” in one action handler.

## Recommended Direction (MVP strategy)
1. Keep the demo frontend minimal (still just mounts `AgentPrinterRuntime`). [examples/frontend_demo/src/main.tsx:L1-L10](examples/frontend_demo/src/main.tsx#L1-L10)
2. Refactor `examples/backend_demo.py` into a small “demo app” module layout under `examples/demo_app/` (pages, agents, catalog).
3. Add a first-class **Demo Registry** concept:
   - `Demo Pages`: Dashboard / Agents / Workflows / Tools / Storybook
   - `Demo Agents`: at least one LangChain-backed demo + one LangGraph-backed demo + one fully-offline mock demo
4. Implement “living storybook” as a **server-driven component catalog page** (browse + preview). Start with curated samples and add optional “prop editing” using the existing `form` component later.

## Open Questions (to resolve during implementation)
- Which LLM provider is the default for the LangChain demo (OpenAI vs fully mocked)? Prefer “mock by default, real when configured”.
- Do we want an actual JS Storybook setup, or is the in-app “living storybook” enough? (This plan assumes in-app.)
- Should `examples/` be treated as “product surface” with stable UX, or purely “reference wiring”? (This plan treats it as a showcase.)

