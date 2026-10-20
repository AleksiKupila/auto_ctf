from typing import Optional
from src.agent.context import ContextManager
from src.agent.parser import parse
from src.agent.heuristics import count_tokens
from src.agent.prompts import sys_message
from src.llm.openai_compat import (
    ModelClient
)
from src.tools.registry import tool_schemas, execute
from src.config import config

# TESTING
exec_container = config.executor_container

class Agent():
      
   def __init__(self):
      self.llm = test_client()
      self.context = test_context()
      self.tools = tool_schemas()
      self.step_count = 0
      self.done = False
      self.container = exec_container


   def step(self):

      if self.done:
         raise Exception("step() called while finished or awaiting approval")

      if self.step_count == 0:
         goal = "Explore the working environment"

      prompt = self.context.fetch_context()
      resp = self.llm.generate(prompt)

      message = resp.choices[0].message.model_dump(exclude_none=True)
      self.context.add_assistant(message)

      #print(message)
      try:
         tool_messages = parse(message, self.container)
      except Exception as e:
         raise Exception(e)

      for msg in tool_messages:
         self.context.add_tool_result(msg)
         self.step_count +=1

   def run(self):
      while True:
         self.step()

# TESTS
def test_client():
   return ModelClient(tools=tool_schemas())

def test_context():
   return ContextManager(sys_message(), "Explore weaknesses of the target machine, dvwa using Nikto and Nmap", 10000, count_tokens)

if __name__=="__main__":
   agent = Agent()
   agent.run()