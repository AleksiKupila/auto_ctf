from typing import Optional

from src.schemas.responses import UserRequest, AIResponse
from src.agent.context import ContextManager
from src.agent.loop import Agent
from src.tools.registry import tool_schemas, execute
from src.llm.openai_compat import ModelClient
from src.config import config

config = config


class Session:
    def __init__(self, agent: Agent, session_id=1,):
        self.agent = agent
        self.id = session_id
class AIService:
    """
    Application service layer responsible for validating user input,
    orchestrating model client requests, and catching exceptions gracefully.
    """

    def __init__(self, model_client: ModelClient, context: ContextManager, config):

        self.llm, self.context, self.config = model_client, context, config,
        self.model_client = model_client
        self.agent, self.agent

    def start_session(self):
        '''
        Starts a session
        '''
        agent = Agent(
            llm=self.llm,
            tools=tool_schemas(),
            context=self.context,
            container=self.config.executor_container
        )
        self.session = Session(agent)
        self.agent = agent
        
    def step_agent(self):

        yield self.agent.step()
        
        