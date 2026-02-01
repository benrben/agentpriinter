# Writing Style & Engineering Standards (The North Star)

## 1. The Core Philosophy
This project is built on **Protocol-Driven Development**. We favor structured schemas over ad-hoc code, and evidence over speculation. The repository is a living encyclopedia of its own capabilities.

## 2. Universal Directives
These are non-negotiable standards for all work:
- **JSON-First Directive**: Before writing React components or FastAPI logic, define the interface. Prioritize JSON schema definitions and minimal custom code for all new UI implementations. 
- **Protocol as Source of Truth**: The `contracts/schemas.json` file is the heartbeat of the project. Changes start in Pydantic (backend), flow through `export_schema.py`, and generate Zod/TS (frontend) via `bun run codegen`.
- **Evidence-First Scopes**: A capability does not exist in documentation unless it is linked to the specific line of code that implements it.

## 3. The Encyclopedia Standard (Documentation)
Documentation in the `Scopes/` directory must be optimized for fast retrieval ("Skimmability"):
- **Structure**: Every scope must have a **Summary**, **Where to Start in Code** (links), and a **Scope Network** (cross-links).
- **Claim only observable reality**: Scopes describe what *is*, not what *should be*. Planned work belongs in `Work/Tasks/`.
- **Terminology Consistency**: Use the exact names from the code (e.g., `ComponentNode`, `ActionRouter`, `ui.render`) in documentation.
- **Cross-Link Aggressively**: If Scope A uses Scope B, they must link to each other.

## 4. The Engineering Standard (Implementation)
- **SDUI-First**: Never hardcode a complex layout in React if it can be represented as a serialized `ComponentNode` tree.
- **Library Reuse**:
  - **Identify**: Search the codebase for existing utilities (`utils.ts`, `manager.py`, `router.py`) before adding new ones.
  - **Extend**: Prefer enhancing an existing tested service over creating a parallel "v2" implementation.
  - **Delete**: If an abstraction is unused or superseded, delete it immediately.
- **Localized Logic**: Keep functions pure and components small. If logic is shared between the local demo and the library, move it into the core library packages.

## 5. Verification & The Loop
Every engineering change follows the **Protocol loop**:
1. **Define/Update**: Modify Pydantic models in `agentprinter-fastapi`.
2. **Export**: Run `python agentprinter-fastapi/scripts/export_schema.py`.
3. **Generate**: Run `bun run codegen` in `agentprinter-react`.
4. **Test**: Run `uv run pytest` and `bun test` to ensure zero regressions.
5. **Document**: Update the relevant `Scopes/Product/**` documentation with new evidence links.

**Test Timeout Rule**: Any test that awaits network/streaming behavior must set a timeout to avoid hangs.
- Python: wrap awaits with `asyncio.wait_for(...)` (or pytest timeouts) when reading streaming endpoints.
- Bun: use the per-test timeout argument (e.g., `it("name", fn, 1000)`) for UI/runtime tests.

---
*Note: This standard is self-enforcing. If a pull request lacks schema updates for new UI or lacks evidence for new claims, it is considered incomplete.*
