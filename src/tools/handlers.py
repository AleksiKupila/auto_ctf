import shlex, io
import subprocess
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from markitdown import MarkItDown, StreamInfo
from pydantic import ValidationError

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

_md = MarkItDown()
# run_command, read_file, list_dir, finish

def run_command(cmd, container):
    '''
    Executes a command in the executor container
    '''
    try:
        args = RunCommand(cmd=cmd)

    except ValidationError as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

    try:
        cmd_output = subprocess.run(
            ['docker', 'exec', '-u', 'target', container, 
             'timeout', '120', 'bash', '-c', args.cmd],
            capture_output=True,
            text=True
        )
        if cmd_output.returncode != 0:
            return ToolOutput(status=False, stdout="", stderr=cmd_output.stderr)
        
        return ToolOutput(status=True, stdout=cmd_output.stdout, stderr=cmd_output.stderr)
 
    except Exception as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")


def read_file(path, filetype, container, max_size=1000):
    '''
    Read contents of a file inside a docker container
    '''
    try:
        args = ReadFile(path=path, filetype=filetype)

    except ValidationError as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

    try:
        cmd_output = subprocess.run(
            ['docker', 'exec', '-u', 'target', container, 
             'timeout', '60', "cat", args.path],
            capture_output=True,
            text=True
        )
        if cmd_output.returncode != 0:
            return ToolOutput(status=False, stdout="", stderr=cmd_output.stderr)

        ext = args.filetype.lower() if "." in path else None

        if ext == "pdf" or ext == "docx":
            result = _md.convert_stream(io.BytesIO(cmd_output.stdout), stream_info=StreamInfo(extension=ext))
            
            return ToolOutput(status=True, stdout=result.text_content[:max_size], stderr="")
        else:
            return ToolOutput(status=True, stdout=cmd_output.stdout, stderr="")

    except Exception as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

def list_dir(path, container):
    '''
    List a directory inside a docker container
    '''
    try:
        args = ListDir(path=path)
    except ValidationError as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

    try:
        cmd_output = subprocess.run(
            ['docker', 'exec', '-u', 'target', container, 
             'timeout', '60', 'ls', '-la', args.path],
            capture_output=True,
            text=True
        )
        if cmd_output.returncode != 0:
            return ToolOutput(status=False, stdout="", stderr=cmd_output.stderr)
        
        return ToolOutput(status=True, stdout=cmd_output.stdout, stderr="")

    except Exception as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

def finish():
    '''
    Finish the task
    '''
    return 
