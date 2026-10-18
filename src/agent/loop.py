from typing import Optional
from src.agent.context import ContextManager
from src.agent.heuristics import count_tokens
from src.llm.openai_compat import (
    ModelClient
)
from src.tools.registry import tool_schemas, execute
class Agent():
      
   def __init__(self, llm: ModelClient, tools: list, context: ContextManager, container: str):
      self.llm = llm
      self.context = context
      self.tools = tools
      self.step_count = 0
      self.done = False
      self.container = container


   def step(self):

      if self.done:
         raise Exception("step() called while finished or awaiting approval")

      if self.step_count == 0:
         goal = input("Give task")

      self.llm.generate()
      return
