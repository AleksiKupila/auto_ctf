from src.agent.context import ContextManager
from src.agent.parser import parse_message, ToolCall, fetch_msg, clean_message
from src.tools.registry import ToolOutput
from src.policy.engine import ask_approval_simple
from dataclasses import dataclass
from src.llm.openai_compat import (
    ModelClient
)
from src.schemas.tools import ToolOutput
from src.tools.registry import tool_schemas, execute

TERMINAL_STATES = {"FINISHED", "CONNECTION_LOST", "MAX_STEPS"}
class Approval_request():
   def __init__(self, tool_call):

      self.tool_call = tool_call
      self.decision = None
@dataclass
class Event():
   def __init__(self, kind, data):

      self.kind: str = kind
      self.data: dict = data
class Agent():
      
   def __init__(self, llm: ModelClient, context: ContextManager, tools, max_steps: int, container):
      self.llm = llm
      self.context = context
      self.tools = tools
      self.step_count = 0
      self.max_steps = max_steps
      self.container = container

      self.status = "RUNNING"
      self.done = False
      self.current_request = None
      self.pending_calls = []
      self.tool_outputs = []
      self.events = []
      self.analysis = None

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
            self.emit(kind="assistant", data=cleaned_message.get("content"))

         self.context.add_assistant(cleaned_message) # Add to context

      elif self.status == "WAITING_APPROVAL":   # A pending request/decision
         if self.current_request.decision == True: # If approved, execute and add to tool_outputs
            try:
               output = execute(self.current_request.tool_call, self.container)

            except Exception as e:
               output = ToolOutput(id=self.current_request.tool_call.id, role="tool", status=False, stdout="", stderr=str(e))

         else: # Else, add an output with an error message
            output = ToolOutput(id=self.current_request.tool_call.id, role="tool", status=False, stdout="", stderr="User refused command")

         self.add_event("tool", self.current_request.tool_call, output)
         self.pending_calls.remove(self.current_request.tool_call)   # Remove from pending calls, resume running status
         self.status = "RUNNING"
         print(f"Agent status: 'RUNNING'")

      for call in self.pending_calls: # Handle finishing call
         if call.name == "finish" and call.valid: 
               if len(self.pending_calls) > 1 or self.tool_outputs: # If other calls in the same message, add output with error message
                  self.context.add_tool_result(ToolOutput(id=call.id, role="tool", status=False, stdout="", stderr="Finishing tool call can't be called along with other tool calls"))
                  self.pending_calls.remove(call)
                  break

               self.context.add_tool_result(ToolOutput(id=call.id, role="tool", status=True, stdout=f"", stderr=""))
               self.context.finish_reason = call.args
               self.pending_calls.clear()
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
            output = ToolOutput(id=call.id, role="tool", status=False, stdout="", stderr=call.invalid_reason)

         else: # No problems, execute
            try:
               output = execute(call, self.container)
            except Exception as e:
               output =  ToolOutput(id=call.id, role="tool", status=False, stdout="", stderr=str(e))

         self.add_event("tool", call, output)
         self.pending_calls.pop(0)  # Remove from queue

      for output in self.tool_outputs: # Add results to context, clean outputs list
         self.context.add_tool_result(output)

      self.tool_outputs.clear()

      return None

   def advance(self):
      if self.status not in TERMINAL_STATES and self.step_count >= self.max_steps:
         self.status = "MAX_STEPS"

      if self.status in TERMINAL_STATES:
         self.analysis = self.finish()
         self.done = True
         return None

      req = self.step()
      self.step_count +=1

      if req:
         self.current_request = req
         self.emit("approval", call=req.tool_call)

      return req

   def run(self):

      while not self.done:

         req = self.advance()
         for ev in self.drain_events():
            self.print_event(ev)

         if req:
            req.decision = ask_approval_simple(req.tool_call)
            
      return

   def _flush_pending(self, reason):
      for call in self.pending_calls:
         self.add_event("tool", call, ToolOutput(id=call.id, role="tool", status=False,
                                            stdout="", stderr=reason))
      self.pending_calls.clear()

      for output in self.tool_outputs:
         self.context.add_tool_result(output)

      self.tool_outputs.clear()

   def finish(self):

      self._flush_pending(f"Not executed: agent stopped ({self.status})")
      self.context.finish_status = self.status
      prompt = self.context.final_analysis_context()

      print("Generating final analysis...")

      try:
         resp = self.llm.generate(prompt, False) 
      except Exception as e:
         resp = None
      
      if not resp:
        return f"Failed generating final analysis: {e}"

      message = fetch_msg(resp) 
      self.emit("finish", data=message.get("content"))

      return message.get("content")

   def emit(self, kind, **data):
      self.events.append(Event(kind=kind, data=data))

   def add_event(self, kind, tool_call, output):
      self.tool_outputs.append(output)
      self.emit(kind=kind, call=tool_call, output=output)

   def drain_events(self):
      evs, self.events = self.events, []
      return evs

   def print_event(self, event):
      if event.kind == "assistant":
         print(f"Assistant:")
         print(f"{event.data["data"]}\n")

      elif event.kind == "tool":
         call = event.data.get("call")
         print(f"Tool: {call.name}: {call.args.get("cmd")}")
         print(f"Tool output:\n")
         print(f"{event.data.get("output").stdout}\n")