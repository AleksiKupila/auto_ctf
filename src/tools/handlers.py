from registry import ToolCall, ToolOutput

# run_command, read_file, list_dir, finish

def run_command(cmd):

    args = ToolCall(
        cmd=cmd
    )
    # TODO: Check policy
    # TODO: Execute in container
    cmd_output, completed = "", True # EXAMPLE

    return ToolOutput(
        status=completed,
        output=cmd_output 
    )

def read_file(path, max_size):
    return

def list_dir(path):
    return

def finish(summary, answer):
    return