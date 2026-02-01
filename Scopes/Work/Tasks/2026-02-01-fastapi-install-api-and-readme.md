# Task: FastAPI install API + package README (“10-minute integration”)

## 1. Summary
**Goal**: Provide a single-call “install” API for `agentprinter-fastapi` and write a real package README that matches the “10 minute integration” promise in `PROJECT_GOAL.md`.
**Context**: Today the backend exposes a global `router` and a set of module-level config functions, and the package README is empty.

## 2. Current State (Scopes)
- **Anchor Scope**: [Backend WebSocket Runtime](../../Product/Backend/WebSocket_Runtime.md)
- **Current Behavior**:
  - Backend exposes a module-level `router = APIRouter()` and includes fallback routes. [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L39-L41](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L39-L41)
  - Configuration is done via module-level setters (`set_auth_hook`, `set_template_loader`, `set_version_negotiation`, etc.). [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L49-L71](../../../agentprinter-fastapi/src/agentprinter_fastapi/router.py#L49-L71)
  - Demo wiring is documented in `examples/README.md`. [examples/README.md:L16-L66](../../../examples/README.md#L16-L66)
  - The backend package README is currently empty. [Scopes/Product/Examples/Demo_Apps.md:L131-L134](../../Product/Examples/Demo_Apps.md#L131-L134)

## 3. Desired State
- **New Behavior**:
  - Backend devs can do:
    - `pip install agentprinter-fastapi`
    - call one function (e.g., `install_agentprinter(app, prefix="/agentprinter", ...)`)
    - optionally point at a templates directory / register action handlers
  - `agentprinter-fastapi/README.md` explains:
    - minimal install snippet
    - how to mount under a prefix
    - how to set auth + version negotiation hooks
    - how to enable templates
    - how to run the demo
- **Constraints**:
  - The install API should be a thin wrapper around existing primitives (less code).
  - Preserve the existing low-level API (do not break examples).

## 4. Implementation Steps
1. **Add an install helper** (thin wrapper):
   - Create `install_agentprinter(app, *, prefix="/agentprinter", auth_hook=None, version_negotiation=None, template_loader=None, template_dir=None, template_name=None, max_message_size=None)` (names can vary but keep minimal).
   - Internally call existing setters and `app.include_router(router, prefix=prefix)`.
2. **Write `agentprinter-fastapi/README.md`**:
   - Add “10-minute integration” Quick Start and link to `examples/README.md` for a runnable reference.
3. **Docs alignment**:
   - Ensure `Scopes/DEVELOPER_INFO.md` includes the canonical run/test commands (if new commands are introduced).

## 5. Acceptance Criteria (Verification)
- [ ] Install helper exists and is used in (at least) the demo app:
  - [ ] Run: `cd examples && uv run python backend_demo.py`
- [ ] Backend tests remain green:
  - [ ] Run: `cd agentprinter-fastapi && uv run pytest`
- [ ] README provides copy/pasteable integration snippet:
  - [ ] Manual check: `agentprinter-fastapi/README.md` includes a Quick Start and a minimal code sample.
- [ ] **Scope Maintenance**:
  - [ ] Update `Scopes/Product/Backend/WebSocket_Runtime.md`:
    - Add a **Use case** for “install_agentprinter mounts router under prefix”
    - Add evidence links to the new install helper and updated demo wiring
  - [ ] Update `Scopes/Product/Examples/Demo_Apps.md` if the demo wiring changes (evidence-backed).
  - [ ] Update `Scopes/DEVELOPER_INFO.md` only if new dev commands are introduced.

## 6. Dependencies
- None (docs + wrapper around existing API).

## Audit Checklist
- [ ] Anchor Scope is under `Scopes/Product/**`
- [ ] Verification includes a concrete command to run
- [ ] Change is minimal (wrapper + docs), not a refactor

