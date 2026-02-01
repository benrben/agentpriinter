# System Glossary

## Core Terms
- **Action**: A user interaction (click, submit) that sends a `user.action` message to the server for processing.
- **ComponentNode**: The JSON object structure representing a single logical component in the SDUI tree (includes `type`, `props`, `children`).
- **Protocol**: The JSON-over-WebSocket contract defining message envelopes, identity headers, and payloads for rendering/actions.
- **Runtime**: The active execution layer—either `Backend/WebSocket_Runtime` (FastAPI) or `Frontend/Remote_UI_Runtime` (React).
- **Scope**: A unit of documented capability covering a specific boundary of the system (e.g., a feature, library, or workflow).
- **SDUI (Server-Driven UI)**: The paradigm where the backend dictates the component tree structure and the frontend acts as a generic renderer.
- **Trace ID**: A unique string identifier generated at the start of a flow (connection or request) to correlate logs and messages across backend/frontend.

## Domain Terms
- **Agent Runner**: The backend service that executes agent loops and streams lifecycle events (`start`, `token`, `tool_call`) to the client.
- **Page**: A top-level container for a component tree, often associated with a route path.
- **Patch**: An incremental update operation (`ui.patch` or `state.patch`) to modify the existing client state without a full re-render.
