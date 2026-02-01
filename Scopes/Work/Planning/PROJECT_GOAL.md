Production-ready GOAL (using all your comments + the best patterns)

Build two drop-in libraries—one for backend and one for frontend—that let developers add AI-first, agent-driven, server-defined multi-page UIs to existing apps with almost zero friction:
	1.	agentprinter-fastapi (Python): a FastAPI plugin that can be added to any existing FastAPI codebase to stream UI JSON + agent events over WebSockets (and optionally SSE/HTTP fallbacks). FastAPI supports sending/receiving JSON over WebSockets, which is the backbone of your “stream JSONs” requirement.  ￼
	2.	@agentprinter/react (TypeScript): a generic React SDK that can be embedded in any React/Next.js application as a single provider + runtime component. It renders pages dynamically from the backend JSON, maintains state, and sends user actions back to the backend.

Your product is not a new framework. It’s a thin, production-grade runtime:
	•	Backend = source of truth (pages/components/actions/styles/state)
	•	Frontend = renderer + event pipe (render what you receive; send back events)

⸻

What developers get (the “10 minute integration” promise)

Backend devs (existing FastAPI apps)

They should be able to:
	•	pip install agentprinter-fastapi
	•	add one install call (router/middleware)
	•	point to a folder of UI JSON templates (optional)
	•	register agents (LangChain/LangGraph) or just normal endpoints
	•	and instantly have a working streamed UI runtime

FastAPI’s WebSocket interface is simple and built in (accept, receive, send—incl. JSON).  ￼

Frontend devs (existing React apps)

They should be able to:
	•	npm install @agentprinter/react
	•	wrap app with <AgentPrinterProvider serverUrl appId getToken>
	•	drop <AgentPrinterRuntime />
	•	and the SDK renders multi-page UI from backend JSON automatically

⸻

The core idea (1 protocol, but with “easy contracts” inside)

You deliver one universal message envelope and a small set of contracts that cover everything needed for real apps: pages, props, CSS, actions, routing, streaming, auth.

0) Universal envelope (every message)

Every WebSocket message is:
	•	type (e.g. ui.render, event, agent.event)
	•	app_id, session_id, trace_id
	•	id + timestamp
	•	payload (the contract)

This keeps SDK logic tiny: parse envelope → update state/UI → render → dispatch events.

⸻

Contracts (simple, complete, production-friendly)

1) UI Contract — “what to render”

Defines multi-page web apps as JSON:
	•	routes/pages (/, /settings, /runs/:id)
	•	layouts (shell/sidebar, split panes, tabs, grids)
	•	component tree (component, key, props, children)
	•	bindings (props reference state.*)

This is the server-driven UI model: backend describes UI, frontend renders it.

2) Props & Binding Contract — “how data flows”
	•	bind component props to state paths (no custom glue code)
	•	allow computed props (minimal operators: if, format, concat)
	•	support incremental updates (so you don’t re-send entire pages)

3) Style Contract — “CSS/theming but safe”

To render “every web application”, you must support styling, but keep it safe/easy:
	•	theme tokens (colors, spacing, typography, radius)
	•	className (utility classes)
	•	allowlisted style (bounded inline CSS)
	•	variants (primary, danger, etc.)

4) Action Contract — “behavior without custom frontend logic”

Actions are declarative:
	•	action_id
	•	trigger (click, submit, change, navigate)
	•	payload_mapping (what values to send)
	•	target (agent run / tool / endpoint / route)
	•	mode (stream over WS or http)

Frontend just emits a single event message; backend routes it.

5) Navigation Contract — “multi-page routing”

Backend can push navigation:
	•	navigate.to, params, replace, open (modal/drawer)

6) State Contract — “single source of truth”

A unified state tree that UI binds to:
	•	state.patch (JSON-pointer style patches)
	•	version (ordering + out-of-order protection)
	•	scopes: app, page, agent_run

7) Agent Streaming Contract — “live execution”

A minimal set of agent lifecycle events:
	•	agent.run.started
	•	agent.run.step
	•	agent.run.token (partial streaming)
	•	agent.run.tool_call
	•	agent.run.tool_result
	•	agent.run.done / agent.run.error

LangGraph explicitly emphasizes streaming events to improve responsiveness (exactly what you want for “AI-first” UX).  ￼
AG-UI is also an example of a lightweight event-based agent↔UI protocol you can align with (or be compatible with).  ￼

8) Tool Contract — “tools are first-class”

Standard tool messages:
	•	tool metadata (name, description)
	•	input_schema / output_schema (JSON Schema)
	•	render hints (table, markdown, code, json, etc.)

9) Schema Contract — “auto forms + validation”

Use JSON Schema + UI schema so the backend can generate forms and validate inputs:
	•	JSON Schema = what data is valid  ￼
	•	UI schema = how it should render (layout/controls), as used by JSON Forms and RJSF  ￼
This lets devs build complex settings pages and tool input panels without writing custom form UIs.  ￼

10) Auth + App Identity Contract — “easy integrations”

A clean handshake:
	•	app_id, workspace_id (optional), user_id (optional)
	•	token/cookie support
	•	refresh events (auth.refresh_required)
	•	permission hints (disable/hide actions)

11) Errors + Observability Contract — “debuggable in production”

Standard error payload:
	•	code, message, retryable, details
Plus:
	•	trace_id on every message
	•	optional event timing fields for profiling

⸻

Component Bank (so it can render “every web application”)

Your React SDK ships with a ready component bank + a registry to add custom ones.

Built-in categories (practical MVP that still feels like a real app)

App Shell & Navigation
	•	AppShell (sidebar/topbar)
	•	Page, Breadcrumbs
	•	Tabs, Stepper
	•	Modal, Drawer

Forms & Input (JSON Schema powered)
	•	Form (schema + uiSchema)
	•	common inputs/selects
	•	validation summary
	•	wizard / multi-step forms

Data & Enterprise UI
	•	Table/DataGrid (filter/sort/paginate)
	•	Card, List, KeyValue
	•	JSONViewer, CodeViewer
	•	DiffViewer
	•	charts (via adapter)

Agent-first UI
	•	Chat
	•	StreamingText
	•	AgentRunPanel (steps/progress)
	•	ToolCallsPanel (request/result)
	•	ApprovalGate (human-in-the-loop)

Feedback & States
	•	Toast/Notifications
	•	Loading/Skeleton
	•	ErrorState, EmptyState

Component registration (the escape hatch)

Apps can extend the SDK:
	•	registerComponent(name, renderer, propsSchema, eventsSchema)

So teams can keep their design system and still render from your contract.

Optional “card mode” compatibility

If you want a proven JSON UI block standard for lightweight cards, Adaptive Cards are a strong reference: JSON-authored UI snippets rendered by hosts.  ￼

⸻

“Very easy” integration: what you must ship

Backend library (agentprinter-fastapi) MUST include
	•	A router you can mount under any prefix: /agentprinter/*
	•	WebSocket endpoint that:
	•	authenticates
	•	negotiates protocol version
	•	streams ui.render then ui.patch/state.patch/agent.event
	•	UI template loader (filesystem + python builder API)
	•	Action router:
	•	event → (agent run | tool call | http handler)
	•	LangChain/LangGraph adapters (optional but huge value)
	•	convert graph streaming events into your agent.event stream  ￼
	•	Testing utilities (FastAPI has documented patterns for testing WebSockets)  ￼

Frontend library (@agentprinter/react) MUST include
	•	Provider + runtime component
	•	WebSocket client:
	•	reconnect with backoff
	•	message ordering using version
	•	buffering + “resume” by last seen version (best effort)
	•	Renderer:
	•	component registry + safe prop validation
	•	patch application (UI + state)
	•	Router adapter (React Router / Next.js friendly)
	•	Devtools panel:
	•	event inspector
	•	UI tree viewer
	•	state viewer
	•	“copy snapshot” for bug reports

⸻

Best practices you need to be production-ready

Reliability & streaming correctness
	•	Incremental patching: send ui.render once, then ui.patch / state.patch frequently (cheaper + smoother).
	•	Backpressure controls: cap message size, cap patch frequency, and coalesce patches under load.
	•	Versioning: every state.patch and ui.patch has an increasing version so the client can ignore stale/out-of-order messages.

Security & abuse resistance
	•	Validate every incoming event against schema (size limits + allowed fields).
	•	Rate limit connection attempts and message frequency.
	•	Auth everywhere: handshake, refresh, permissions-based UI disabling.
	•	Allowlist styles: don’t allow arbitrary CSS that could break layout or create security risks.
	•	No “execute code” in UI JSON: keep contracts declarative.

Compatibility & upgrades
	•	Protocol version negotiation at connect time.
	•	Component versioning: component bank has semver; backend can request a minimum version.
	•	Graceful degradation: unknown components render as UnknownComponent with debug info.

Observability & debugging
	•	trace_id required on every message.
	•	structured logs on both sides.
	•	devtools UI to replay event streams for bugs.

⸻

Positioning with existing ecosystem work (so devs trust it)
	•	Event streaming compatibility inspiration: AG-UI (agent↔UI events; middleware bridging)  ￼
	•	Production agent serving surfaces: LangChain Agent Protocol (framework-agnostic APIs for serving agents)  ￼
	•	Streaming-first agent workflows: LangGraph streaming system  ￼
	•	Schema-driven form rendering: JSON Forms + RJSF concepts (JSON Schema + uiSchema)  ￼
	•	JSON-authored UI snippet reference: Microsoft Adaptive Cards  ￼
	•	Production server transport: FastAPI WebSockets with JSON support  ￼

⸻

The final “GOAL statement” you can paste into docs

Create a drop-in FastAPI plugin and a drop-in React UI runtime that implement a simple, fully declarative protocol for building AI-first web applications. The backend streams multi-page UI definitions (components/layout/styles/actions) and live agent execution events as JSON over WebSockets. The frontend SDK renders these definitions using a built-in bank of production components, applies patches in real time, and sends user interactions back as structured events. The system is production-ready by default: versioned protocol, schema validation, auth hooks, safe styling, reconnection, patching, testing utilities, and observability (trace IDs + devtools). This enables developers to turn any existing FastAPI app + agent stack into a fully interactive, streaming, AI-first web app with minimal code changes.