import json
from pathlib import Path
from pydantic import BaseModel
from typing import Union, List

# Import all our types
from agentprinter_fastapi.schemas import (
    Message, 
    MessageHeader,
    ActionPayload,
    ErrorPayload,
    Page, 
    ComponentNode,
    Bindings,
    AgentEvent,
    StatePatch
)

class ProtocolContract(BaseModel):
    """
    A unified model acting as the root for schema generation.
    This ensures all sub-models are discovered and included in the $defs.
    """
    message: Message
    page: Page
    event: AgentEvent
    error: ErrorPayload
    patch: StatePatch
    # Include list types if they appear alone in API responses
    nodes: List[ComponentNode] 

def export():
    # Generate the full JSON Schema
    schema = ProtocolContract.model_json_schema()
    
    # Define output path (relative to this script or repo root)
    # Assuming this script is in: /src/agentprinter_fastapi/scripts/ (nested deeper?) 
    # Actually, current CWD is project root usually, but let's trust __file__
    # File is: agentprinter-fastapi/scripts/export_schema.py
    # Parent: agentprinter-fastapi/scripts
    # Parent.parent: agentprinter-fastapi
    # Parent.parent.parent: agentprinter (REPO ROOT)
    repo_root = Path(__file__).resolve().parent.parent.parent
    
    # Ensure directory exists just in case
    (repo_root / "contracts").mkdir(parents=True, exist_ok=True)
    
    output_path = repo_root / "contracts" / "schemas.json"
    
    print(f"Generating schema to: {output_path}")
    
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=2)
        
    print("Done.")

if __name__ == "__main__":
    export()
