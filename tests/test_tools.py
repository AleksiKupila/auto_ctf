from src.tools.handlers import run_command
import pytest

def test_command_execution():
    '''
    Tests command execution in the executor container
    Ensures the command returns an output without errors
    '''
    EXECUTOR_CONTAINER = "command_executor"
    output = run_command("ip a", EXECUTOR_CONTAINER)

    assert output.stdout != ""
    assert output.stderr == ""
    assert output.status == True