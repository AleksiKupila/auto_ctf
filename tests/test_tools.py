from src.tools.handlers import run_command, list_dir, read_file
import pytest

EXECUTOR_CONTAINER = "command_executor"

def test_command_execution():
    '''
    Tests command execution in the executor container
    Ensures the command returns an output without errors
    '''
    output = run_command("ip a", EXECUTOR_CONTAINER)

    assert output.status == True

def test_directory_listing():
    '''
    Tests directory listing in the executor container
    '''
    output = list_dir("/home/scanner/", EXECUTOR_CONTAINER)
    
    assert output.status == True

def test_file_read():
    '''
    Tests reading a file inside the docker executor
    '''
    txt_output = read_file("/home/scanner/tests/test.txt", "txt", 5000, EXECUTOR_CONTAINER)

    assert txt_output.status == True