# Scope Network Graph

## Legend
- `-->` Depends On / Uses
- `..>` Possible Relation (Low confidence)

## Graph
```mermaid
flowchart TD
  Backend[Backend WebSocket Runtime] --> Contracts[Protocol Schema & Codegen]
  Backend --> Examples[Demo Apps (Examples)]
  Contracts --> Frontend[Remote UI Runtime]
  Frontend --> Backend
  Frontend --> Examples
```

## Evidence Table
| From | To | Relationship | Evidence Link |
|------|----|--------------|---------------|
| Backend WebSocket Runtime | Protocol Schema & Codegen | Exports protocol schema | [agentprinter-fastapi/scripts/export_schema.py:L24-L41](agentprinter-fastapi/scripts/export_schema.py#L24-L41) |
| Backend WebSocket Runtime | Demo Apps (Examples) | Demo mounts AgentPrinter router | [examples/backend_demo.py:L24-L24](examples/backend_demo.py#L24-L24) |
| Protocol Schema & Codegen | Remote UI Runtime | Generates frontend contracts | [agentprinter-react/package.json:L21-L22](agentprinter-react/package.json#L21-L22) |
| Remote UI Runtime | Backend WebSocket Runtime | Sends `user.action` messages | [agentprinter-react/src/renderer.tsx:L70-L88](agentprinter-react/src/renderer.tsx#L70-L88) |
| Remote UI Runtime | Demo Apps (Examples) | Demo mounts `AgentPrinterRuntime` | [examples/frontend_demo/src/main.tsx:L3-L10](examples/frontend_demo/src/main.tsx#L3-L10) |
| Remote UI Runtime | Protocol Schema & Codegen | Validates headers with identity | [agentprinter-react/src/contracts.ts:L109-L118](agentprinter-react/src/contracts.ts#L109-L118) |
| Backend WebSocket Runtime | Protocol Schema & Codegen | Uses structured error payloads | [agentprinter-fastapi/src/agentprinter_fastapi/router.py:L60-L71](agentprinter-fastapi/src/agentprinter_fastapi/router.py#L60-L71) |
