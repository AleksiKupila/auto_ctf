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


def execute(name, raw_args, container):
    '''
    Call a handler if tool exists
    '''
    if name not in TOOLS:
        return ToolOutput(status=False, stdout="",
                          stderr=f"Unknown tool '{name}'. Available: {list(TOOLS)}")

    function, _ = TOOLS[name]

    try:
        return function(**json.loads(raw_args), container = container)
    
    except Exception as e:   # bad JSON or wrong/extra kwargs
        return ToolOutput(status=False, stdout="", stderr=f"Invalid arguments: {e}")
