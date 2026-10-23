from src.services.ai_service import AgentSession
from src.config import config
from src.tools.registry import tool_schemas
from src.llm.openai_compat import ModelClient
from src.agent.context import ContextManager
from src.agent.prompts import sys_message

if __name__=="__main__":

    client = ModelClient(
        base_url=config.openai_base_url,
        model_name=config.openai_model_name,
        tools=tool_schemas(),
        timeout=config.model_timeout
        )
    
    context_manager = ContextManager(
        system_message=sys_message(),
        goal="Explore home directory",
        max_tokens=config.max_context_tokens,
        max_tool_chars=1000,
    )
    session = AgentSession(
        model_client=client,
        context=context_manager,
        config=config
    )

    print(f"Starting pipeline...")
    print(f"----------")

    session.start_session()

    print(f"Exiting...")
