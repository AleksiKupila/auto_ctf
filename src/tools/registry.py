import json
from src.tools.handlers import (
    RunCommand, 
    ListDir, 
    ReadFile, 
    ToolOutput,
    run_command,
    list_dir,
    read_file
)
from pydantic import ValidationError


# tool definitions + JSON schemas for the LLM
TOOLS = {
    "run_command": (run_command, RunCommand),
    "read_file": (read_file, ReadFile),
    "list_dir": (list_dir, ListDir)
}

def tool_schemas():

    return [{"type": "function", "function": {
                "name": name,
                "description": (function.__doc__ or "").strip(),
                "parameters": model.model_json_schema()}}
        for name, (function, model) in TOOLS.items()]


def execute(toolcall, container):
    '''
    Call a handler if tool exists
    '''
    name = toolcall["function"]["name"]
    if name not in TOOLS:
        return ToolOutput(status=False, stdout="",
                          stderr=f"Unknown tool '{name}'. Available: {list(TOOLS)}")

    function, model = TOOLS[name]

    try:
        args = model.model_validate_json(toolcall["function"]["arguments"] or {})
    except ValidationError as e:
        return ToolOutput(status=False, stdout="", stderr=f"Invalid arguments for {name}: {e}")
    try:
        output = function(**args.model_dump(), container = container)
        print(f"Stdout:\n\n {output.stdout}\n")
        print(f"Stderr: {output.stderr}")
        return output
    
    except Exception as e:   # bad JSON or wrong/extra kwargs
        return ToolOutput(status=False, stdout="", stderr=f"Invalid arguments: {e}")
