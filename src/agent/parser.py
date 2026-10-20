from src.tools.registry import execute
from src.tools.handlers import ToolOutput
from pydantic import BaseModel, ConfigDict

# tool-call validation + single repair attempt
class Tool_message(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    id: str
    role: str
    status: bool
    stdout: str
    stderr: str


def parse(message, container):

    print(f"Assistant:\n")
    print(message.get("content"))

    tool_messages = []
    for call in message.get("tool_calls"):

        call_id = call["id"]
        tool = call["function"]
        name = tool["name"]
        args = tool["arguments"]

        print(f"Model called tool: {name}, args: {args}\n")

        if name == "run_command":
            accept = input("Run command? (y/n) ")

            if accept.lower() == "y":
                try:
                    output = execute(call, container)
                    tool_messages.append(
                        Tool_message(id=call_id, status=output.status, role="tool", stdout=output.stdout, stderr=output.stderr)
                        )

                
                except Exception  as e:
                    output = ToolOutput(status=False, stdout="", stderr=f"Tool execution error: {e}")
                    tool_messages.append(
                        Tool_message(id=call_id, status=output.status, role="tool", stdout=output.stdout, stderr=output.stderr)
                    )


            else:
                output = ToolOutput(status=False, stdout="", stderr=f"User refused command")
                tool_messages.append(id=call_id, status=output.status, role="tool", stdout=output.stdout, stderr=output.stderr)
                
        else:
            try:
                output = execute(call, container)
                tool_messages.append(
                    Tool_message(id=call_id, status=output.status, role="tool", stdout=output.stdout, stderr=output.stderr)
                )
            
            except Exception  as e:
                output = ToolOutput(status=False, stdout="", stderr=f"Tool execution error: {e}")
                tool_messages.append(
                    Tool_message(id=call_id, status=output.status, role="tool", stdout=output.stdout, stderr=output.stderr)
                )

    return tool_messages
