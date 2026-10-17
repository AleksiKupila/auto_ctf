import shlex
import subprocess
from src.tools.registry import ToolCall, ToolOutput

# run_command, read_file, list_dir, finish

def run_command(cmd, EXECUTOR_CONTAINER):

    args = ToolCall(
        cmd=cmd
    )
    # TODO: Check policy
    # TODO: Execute in container

    completed = False
    split_cmd = shlex.split(cmd)

    try:
        cmd_output = subprocess.run(
            ['docker', 'exec', EXECUTOR_CONTAINER] + split_cmd,
            capture_output=True,
            text=True,
        )
        completed = True
        print("Command executed succesfully!")

    except Exception as e:
        print(f"Error running command: {e}")

    stdout = cmd_output.stdout
    stderr = cmd_output.stderr
    
    return ToolOutput(
        status=completed,
        stdout=stdout,
        stderr=stderr
    )


def read_file(path, max_size):
    return

def list_dir(path):
    return

def finish(summary, answer):
    return