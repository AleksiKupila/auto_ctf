import json
from src.schemas.tools import RunCommand, ListDir, ReadFile, ToolOutput, Finish
from src.tools.handlers import (
    run_command,
    list_dir,
    read_file,
    finish
)


# tool definitions + JSON schemas for the LLM
TOOLS = {
    "run_command": (run_command, RunCommand),
    "read_file": (read_file, ReadFile),
    "list_dir": (list_dir, ListDir),
    'finish': (finish, Finish)
}

def get_tools():
    return TOOLS

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
    try:
        function, _ = TOOLS[toolcall.name]
        output = function(**toolcall.args, container = container)
        output.id, output.role = toolcall.id, toolcall.role
        return output
    
    except Exception as e:   # bad JSON or wrong/extra kwargs
        return ToolOutput(id=toolcall.id, role=toolcall.role, status=False, stdout="", stderr=f"Invalid arguments: {e}")
