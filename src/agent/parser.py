from src.tools.registry import execute
from typing import Any
from src.tools.handlers import ToolOutput
from pydantic import BaseModel, ConfigDict, ValidationError, Field
from src.tools.registry import get_tools

# tool-call validation + single repair attempt
class ToolCall(BaseModel):

    id: str
    role: str
    name: str
    args: dict[str, Any] = Field(default_factory=dict)
    valid: bool = True
    invalid_reason: str | None=None
    needs_approval: bool = False

def parse_message(message):
    '''
    Parses a LLM message into toolcalls
    '''

    parsed = []
    TOOLS = get_tools()

    for call in message.get("tool_calls"):

        needs_approval = False
        valid = True
        invalid_reason = ""

        if "run_command" == call["function"]["name"]:
            needs_approval = True

        id = call["id"]
        name = call["function"]["name"]

        if name not in TOOLS:
            valid = False
            invalid_reason =f"Unknown tool '{name}'. Available: {list(TOOLS)}"

        _, model = TOOLS[name]

        try:
            args = model.model_validate_json(call["function"]["arguments"] or {}).model_dump()

        except ValidationError as e:
            valid = False
            invalid_reason = f"Invalid arguments for {name}: {e}"
        
        parsed.append(ToolCall(id=id, role="tool", name=name, args=args, valid=valid, invalid_reason=invalid_reason, needs_approval=needs_approval))

    return parsed

def fetch_msg(resp):
    return resp.choices[0].message.model_dump(exclude_none=True) # Get message from response