from pydantic import BaseModel, ConfigDict, Field, ValidationError

# tool definitions + JSON schemas for the LLM

class ToolCall(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    cmd: str = Field(min_length=2, max_length=50)

class ToolOutput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    successful: bool
    output: str
    

RUN_COMMAND = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": (
            "Execute a non-destructive Linux command"
            "in a sandboxed docker environment"
        ),
        "parameters": ToolCall.model_json_schema(),

    },
}