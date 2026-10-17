from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# tool definitions + JSON schemas for the LLM

class RunCommand(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    cmd: str = Field(min_length=2, max_length=100)

class ListDir(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    path: str = Field(min_length=2, max_length=100)

class ReadFile(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    path: str = Field(min_length=2, max_length=100)
    filetype: Literal["txt", "json", "md", "pdf", "docx"]

class ToolOutput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    status: bool
    stdout: str
    stderr: str
    

RUN_COMMAND = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": (
            "Execute a Linux command"
            "in a sandboxed docker environment"
        ),
        "parameters": RunCommand.model_json_schema(),
    },
}

LIST_DIR = {
    "type": "function",
    "function": {
        "name": "list_dir",
        "description": (
            "Lists a directory"
            "in a sandboxed docker environment"
        ),
        "parameters": ListDir.model_json_schema(),
    },
}

READ_FILE = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Reads a file"
            "in a sandboxed docker environment"
        ),
        "parameters": ReadFile.model_json_schema(),
    },
}

#AVAILABLE_TOOLS = {[RUN_COMMAND, LIST_DIR, READ_FILE]}
