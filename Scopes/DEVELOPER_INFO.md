# Developer Info & Commands

## Quick Start
- **Install (frontend)**: `bun install` ([agentprinter-react/README.md:L3-L7](agentprinter-react/README.md#L3-L7))
- **Install (backend)**: `uv sync` ([agentprinter-fastapi/pyproject.toml:L1-L15](agentprinter-fastapi/pyproject.toml#L1-L15))
- **Run (frontend)**: `bun run index.ts` ([agentprinter-react/README.md:L9-L13](agentprinter-react/README.md#L9-L13))
- **Run (backend demo app)**: `cd examples && uv run python backend_demo.py` ([examples/README.md:L26-L36](examples/README.md#L26-L36))
- **Codegen (frontend)**: `bun run codegen` ([agentprinter-react/package.json:L21-L22](agentprinter-react/package.json#L21-L22))
- **Export protocol schema (backend)**: `python agentprinter-fastapi/scripts/export_schema.py` ([agentprinter-fastapi/scripts/export_schema.py:L68-L69](agentprinter-fastapi/scripts/export_schema.py#L68-L69))

## Test Commands
| Scope/Area | Command | Source |
|------------|---------|--------|
| Backend | `cd agentprinter-fastapi && uv run pytest` | [agentprinter-fastapi/pyproject.toml:L21-L26](agentprinter-fastapi/pyproject.toml#L21-L26) |
| Frontend | `bun test` | [agentprinter-react/package.json:L21-L23](agentprinter-react/package.json#L21-L23) |

**Note**: Backend tests must be run from the `agentprinter-fastapi` directory so that `uv run` can properly resolve the package in the local environment.

## Environment & Setup
- Python Version: `>=3.12` ([agentprinter-fastapi/pyproject.toml:L9-L9](agentprinter-fastapi/pyproject.toml#L9-L9))
- Node Runtime: `bun >= 1.0` ([agentprinter-react/package.json:L3-L3](agentprinter-react/package.json#L3-L3))

## Deployment / CI
- Not yet implemented.
