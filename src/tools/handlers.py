import shlex, io
import subprocess
from src.tools.registry import ToolCall, ToolOutput
from markitdown import MarkItDown, StreamInfo

_md = MarkItDown()
# run_command, read_file, list_dir, finish

def run_command(cmd, EXECUTOR_CONTAINER):
    '''
    Executes a command in the executor container
    '''

    args = ToolCall(
        cmd=cmd
    )
    # TODO: Check policy

    split_cmd = shlex.split(cmd)

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


def read_file(path, filetype, max_size, EXECUTOR_CONTAINER):
    '''
    Read contents of a file inside a docker container
    '''
    try:
        cmd_output = subprocess.run(
            ['docker', 'exec', EXECUTOR_CONTAINER, "cat", "--", path],
            capture_output=True,
            text=True,
            timeout=60
        )
        if cmd_output.returncode != 0:
            return ToolOutput(status=False, stdout="", stderr=cmd_output.stderr)

        ext = filetype.lower() if "." in path else None
        print(ext)
        if ext == "pdf" or ext == "docx":
            result = _md.convert_stream(io.BytesIO(cmd_output.stdout), stream_info=StreamInfo(extension=ext))
            
            return ToolOutput(status=True, stdout=result.text_content[:30_000], stderr="")
        else:
            return ToolOutput(status=True, stdout=cmd_output.stdout, stderr="")

    except Exception as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

def list_dir(path, EXECUTOR_CONTAINER):
    '''
    List a directory inside a docker container
    '''
    completed = False
    try:
        cmd_output = subprocess.run(
            ['docker', 'exec', EXECUTOR_CONTAINER, "ls -lha", path],
            capture_output=True,
            text=True,
            timeout=60
        )

        return ToolOutput(status=True, stdout=cmd_output.stdout, stderr="")

    except Exception as e:
        return ToolOutput(status=False, stdout="", stderr=f"{type(e).__name__}: {e}")

def finish(summary, answer):
    return
