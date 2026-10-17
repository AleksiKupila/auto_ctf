from src.tools.handlers import run_command, list_dir, read_file
import pytest

EXECUTOR_CONTAINER = "command_executor"

long_str = "Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of de Finibus Bonorum et Malorum (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, Lorem ipsum dolor sit amet.., comes from a line in section 1.10.32."

def test_command_execution():
    '''
    Tests command execution in the executor container
    Ensures the command returns an output without errors
    '''
    output = run_command("ip a", EXECUTOR_CONTAINER)
    assert output.status == True
    # Empty command
    output = run_command("", EXECUTOR_CONTAINER)
    assert output.status == False
    # Long string
    output = run_command(long_str, EXECUTOR_CONTAINER)
    assert output.status == False

def test_directory_listing():
    '''
    Tests directory listing in the executor container
    '''
    output = list_dir("/home/scanner/", EXECUTOR_CONTAINER)
    assert output.status == True
    # Faulty path
    output = list_dir(long_str, EXECUTOR_CONTAINER)
    assert output.status == False


def test_file_read():
    '''
    Tests reading a file inside the docker executor
    '''
    txt_output = read_file("/home/scanner/tests/test.txt", "txt", EXECUTOR_CONTAINER)
    assert txt_output.status == True
    # Faulty filetype
    txt_output = read_file("/home/scanner/tests/test.txt", "safetensors", EXECUTOR_CONTAINER)
    assert txt_output.status == False