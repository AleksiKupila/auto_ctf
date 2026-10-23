from typing import Optional
from src.agent.context import ContextManager
from src.agent.parser import parse_message, ToolCall, fetch_msg, clean_message
from src.tools.registry import ToolOutput
from src.agent.heuristics import count_tokens
from src.agent.prompts import sys_message
from src.policy.engine import ask_approval_simple
from src.llm.openai_compat import (
    ModelClient
)
from src.tools.registry import tool_schemas, execute
from src.config import config
class Approval_request():
   def __init__(self, tool_call):

      self.tool_call = tool_call
      self.decision = None
class Agent():
      
   def __init__(self, llm: ModelClient, context: ContextManager, tools, max_steps: int, container):
      self.llm = llm
      self.context = context
      self.tools = tools
      self.step_count = 0
      self.max_steps = max_steps
      self.container = container

      self.status = "RUNNING"
      self.current_request = None
      self.pending_calls = []
      self.tool_outputs = []

   def step(self):

      if self.status == "RUNNING":  # No pending requests
         prompt = self.context.fetch_context() # Fetch context for LLM
         resp = self.llm.generate(prompt, True) # Ask LLM

         if not resp:
            self.status = "CONNECTION_LOST"
            print(f"Agent status: 'CONNECTION_LOST'")
            return None

         message = fetch_msg(resp) # Get message from response
         cleaned_message, finish = clean_message(message)

         try:
            self.pending_calls = parse_message(cleaned_message) # Parse message into tool calls

         except Exception as e:
            raise Exception(e)
         
         if not finish:
            print(f"Assistant:\n")
            print(cleaned_message.get("content"))

         self.context.add_assistant(cleaned_message) # Add to context

      elif self.status == "WAITING_APPROVAL":   # A pending request/decision
         if self.current_request.decision == True: # If approved, execute and add to tool_outputs
            output = execute(self.current_request.tool_call, self.container)
            self.tool_outputs.append(output)

         else: # Else, add an output with an error message
            self.tool_outputs.append(ToolOutput(id=self.current_request.tool_call.id, role="tool", status=False, stdout="", stderr="User refused command"))

         self.pending_calls.remove(self.current_request.tool_call)   # Remove from pending calls, resume running status
         self.status = "RUNNING"
         print(f"Agent status: 'RUNNING'")

      for call in self.pending_calls: # Handle finishing call
         if call.name == "finish": 
               if len(self.pending_calls) > 1 or self.tool_outputs: # If other calls in the same message, add output with error message
                  self.context.add_tool_result(ToolOutput(id=call.id, role="tool", status=False, stdout="", stderr="Finishing tool call can't be called along with other tool calls"))
                  self.pending_calls.remove(call)
                  break

               self.context.add_tool_result(ToolOutput(id=call.id, role="tool", status=True, stdout=f"", stderr=""))
               self.context.finish_reason = call.args
               self.status = "FINISHED"
               print(f"Agent status: 'FINISHED'")
               return None

      while self.pending_calls:  # Iterate through tool calls

         call =self.pending_calls[0]

         if call.needs_approval:  # If custom command, set status to waiting and return
            self.status = "WAITING_APPROVAL" 
            print(f"Agent status: 'WAITING_APPROVAL'")
            return Approval_request(call)

         elif not call.valid: # Invalid tool name or arguments
            self.tool_outputs.append(ToolOutput(id=call.id, role="tool", status=False, stdout="", stderr=call.invalid_reason))

         else: # No problems, execute
            self.tool_outputs.append(execute(call, self.container))
         
         self.pending_calls.pop(0)  # Remove from queue

      for output in self.tool_outputs: # Add results to context, clean outputs list
         self.context.add_tool_result(output)

      self.tool_outputs.clear()

      return None

   def run(self):

      while self.step_count < self.max_steps:

         if self.status == "FINISHED" or self.status == "CONNECTION_LOST":

            return self.finish()
         
         new_request = self.step()
         self.step_count +=1

         if new_request:
            decision = ask_approval_simple(new_request.tool_call)
            if decision:
               new_request.decision = True
            else:
               new_request.decision = False

            self.current_request = new_request

      self.status = "MAX_STEPS"
      return self.finish()

   def finish(self):

      self.context.finish_status = self.status
      prompt = self.context.final_analysis_context()

      print("Generating final analysis...")
      resp = self.llm.generate(prompt, False) 
      
      if not resp:
         print("Failed generating final analysis (LLM connection failed)")
         return None

      message = fetch_msg(resp) 
      print(f"Assistant:\n")
      print(message.get("content"))

      return message.get("content")
   