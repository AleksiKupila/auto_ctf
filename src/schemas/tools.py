from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional, Any

class RunCommand(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    cmd: str = Field(min_length=2, max_length=1000)

class ListDir(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    path: str = Field(min_length=1, max_length=1000)

class ReadFile(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    path: str = Field(min_length=1, max_length=1000)
    filetype: Literal["txt", "json", "md", "pdf", "docx", "py", "html", "js", "css"]

class Finish(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    reason: str
    finished: bool

class ToolOutput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    id: Optional[str] = None
    role: Optional[str] = None
    status: bool
    stdout: str
    stderr: str

class ToolCall(BaseModel):

    id: str
    role: str
    name: str
    args: dict[str, Any] = Field(default_factory=dict)
    valid: bool = True
    invalid_reason: str | None=None
    needs_approval: bool = False