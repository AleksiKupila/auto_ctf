from typing import Optional
from src.agent.context import ContextManager
from src.agent.parser import parse_message, ToolCall, fetch_msg
from src.tools.registry import ToolOutput
from src.agent.heuristics import count_tokens
from src.agent.prompts import sys_message
from src.policy.engine import ask_approval_simple
from src.llm.openai_compat import (
    ModelClient
)
from src.tools.registry import tool_schemas, execute
from src.config import config

# TESTING
exec_container = config.executor_container

class Approval_request():
   def __init__(self, tool_call):

      self.tool_call = tool_call
      self.decision = None
class Agent():
      
   def __init__(self):
      self.llm = test_client()
      self.context = test_context()
      self.tools = tool_schemas()
      self.step_count = 0
      self.max_steps = 50
      self.container = exec_container

      self.status = "RUNNING"
      self.current_request = None
      self.pending_calls = []
      self.tool_outputs = []

   def step(self):

      if self.status == "RUNNING":
         prompt = self.context.fetch_context() # Fetch context for LLM
         resp = self.llm.generate(prompt) # Ask LLM

         message = fetch_msg(resp) # Get message from response

         print(f"Assistant:\n")
         print(message.get("content"))

         self.context.add_assistant(message) # Add to context

         try:
            self.pending_calls = parse_message(message) # Parse message into tool calls

         except Exception as e:
            raise Exception(e)

      elif self.status == "WAITING_APPROVAL":
         if self.current_request.decision == True:
            output = execute(self.current_request.tool_call, self.container)
            self.tool_outputs.append(output)

         else:
            self.tool_outputs.append(ToolOutput(id=self.current_request.tool_call.id, role="tool", status=False, stdout="", stderr="User refused command"))

         self.pending_calls.remove(self.current_request.tool_call)
         self.status = "RUNNING"
         print(f"Agent status: 'RUNNING'")

      for call in self.pending_calls:
         if call.needs_approval:

            self.status = "WAITING_APPROVAL"
            print(f"Agent status: 'WAITING_APPROVAL'")
            return Approval_request(call)

         elif not call.valid:
            self.tool_outputs.append(ToolOutput(status=False, stdout="", stderr=call.invalid_reason))

         else:
            self.tool_outputs.append(execute(call, self.container))
         
         self.pending_calls.remove(call)

      for output in self.tool_outputs:
         self.context.add_tool_result(output)
         self.tool_outputs.remove(output)

      return None

   def run(self):

      while self.step_count < self.max_steps:

         new_request = self.step(self.current_request)
         self.step_count +=1

         if new_request:
            decision = ask_approval_simple(new_request.tool_call)
            if decision:
               new_request.decision = True
            else:
               new_request.decision = False

            self.current_request = new_request

# TESTS
def test_client():
   return ModelClient(tools=tool_schemas())

def test_context():
   return ContextManager(sys_message(), "Explore weaknesses of the target machine, dvwa using Nikto and Nmap", 10000, count_tokens)

if __name__=="__main__":
   agent = Agent()
   agent.run()