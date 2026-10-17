import shlex, io
import subprocess
from src.tools.registry import RunCommand, ListDir, ReadFile, ToolOutput
from markitdown import MarkItDown, StreamInfo
from pydantic import ValidationError

_md = MarkItDown()
# run_command, read_file, list_dir, finish

def run_command(cmd, EXECUTOR_CONTAINER):
    '''
    Executes a command in the executor container
    '''
    try:
        args = RunCommand(cmd=cmd)

    except ValidationError as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")
    # TODO: Check policy

    split_cmd = shlex.split(args.cmd)

    try:
        cmd_output = subprocess.run(
            ['docker', 'exec', EXECUTOR_CONTAINER] + split_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return ToolOutput(status=True, stdout=cmd_output.stdout, stderr=cmd_output.stderr)
 
    except Exception as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")


def read_file(path, filetype, EXECUTOR_CONTAINER, max_size=1000):
    '''
    Read contents of a file inside a docker container
    '''
    try:
        args = ReadFile(path=path, filetype=filetype)

    except ValidationError as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

    try:
        cmd_output = subprocess.run(
            ['docker', 'exec', EXECUTOR_CONTAINER, "cat", "--", args.path],
            capture_output=True,
            text=True,
            timeout=60
        )
        if cmd_output.returncode != 0:
            return ToolOutput(status=False, stdout="", stderr=cmd_output.stderr)

        ext = args.filetype.lower() if "." in path else None
        print(ext)
        if ext == "pdf" or ext == "docx":
            result = _md.convert_stream(io.BytesIO(cmd_output.stdout), stream_info=StreamInfo(extension=ext))
            
            return ToolOutput(status=True, stdout=result.text_content[:max_size], stderr="")
        else:
            return ToolOutput(status=True, stdout=cmd_output.stdout, stderr="")

    except Exception as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

def list_dir(path, EXECUTOR_CONTAINER):
    '''
    List a directory inside a docker container
    '''
    try:
        args = ListDir(path=path)

    except ValidationError as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

    try:
        cmd_output = subprocess.run(
            ['docker', 'exec', EXECUTOR_CONTAINER, "ls -lha", args.path],
            capture_output=True,
            text=True,
            timeout=60
        )

        return ToolOutput(status=True, stdout=cmd_output.stdout, stderr="")

    except Exception as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

def finish(summary, answer):
    return
