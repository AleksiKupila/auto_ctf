from typing import Optional

from src.schemas.responses import UserRequest, AIResponse
from src.agent.context import ContextManager
from src.agent.loop import Agent
from src.tools.registry import tool_schemas, execute
from src.llm.openai_compat import ModelClient
from src.config import config
from src.agent.prompts import sys_message

config = config


class AgentSession:
    """
    Application service layer
    """

    def new_agent(self, goal):
        '''
        Wrapper for session building with print messages
        '''

        print(f"Building agent...")
        try:
            agent = self.build_agent(goal)
            print(f"Agent built succesfully!")
            return agent

        except Exception as e:
            print(f"Failed building agent, aborting... {e}")
            return None

    def run_agent(self, agent):
        '''
        Wrapper for agent.run with print messages
        '''

        try:
            print(f"Starting pipeline...")
            print(f"----------")
            agent.run()
            print(f"Exiting...")

        except Exception as e:
           print(f"Encountered error while running agent, aborting... {e}")

    def build_agent(self, goal):

        client = ModelClient(
            base_url=config.openai_base_url,
            model_name=config.openai_model_name,
            tools=tool_schemas(),
            timeout=config.model_timeout
            )
        
        context_manager = ContextManager(
            system_message=sys_message(),
            goal=goal,
            max_tokens=config.max_context_tokens,
            max_tool_chars=config.max_tool_chars,
        )

        agent = Agent(
            llm=client,
            tools=tool_schemas(),
            context=context_manager,
            container=config.executor_container,
            max_steps=config.max_steps
        )
        return agent

        
        