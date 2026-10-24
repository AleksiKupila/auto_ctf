from src.schemas.tools import ToolCall
from pydantic import BaseModel, ConfigDict, ValidationError, Field
from src.tools.registry import get_tools

# tool-call validation + single repair attempt

def parse_message(message):
    parsed = []
    TOOLS = get_tools()

    for call in message.get("tool_calls") or []:
        id = call["id"]
        name = call["function"]["name"]
        raw = call["function"].get("arguments") or "{}"

        if name not in TOOLS:
            parsed.append(ToolCall(id=id, role="tool", name=name, valid=False,
                invalid_reason=f"Unknown tool '{name}'. Available: {list(TOOLS)}"))
            continue

        _, model = TOOLS[name]
        try:
            args = model.model_validate_json(raw).model_dump()
        except ValidationError as e:
            parsed.append(ToolCall(id=id, role="tool", name=name, valid=False,
                invalid_reason=f"Invalid arguments for {name}: {e}"))
            continue

        parsed.append(ToolCall(id=id, role="tool", name=name, args=args,
                               needs_approval=(name == "run_command")))
    return parsed

def clean_message(message):
    finish = False
    for call in message.get("tool_calls"):
        if call["function"]["name"] == "finish":
            message.update({"content": ""})
            finish = True

    return message, finish

def fetch_msg(resp):
    return resp.choices[0].message.model_dump(exclude_none=True) # Get message from response