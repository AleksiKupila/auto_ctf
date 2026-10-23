import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


@dataclass
class Config:
    """Simple configuration object reading environment variables."""

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model_name: str = os.getenv("MODEL_NAME", "llama3.2")

    # OpenAI/llama.cpp
    openai_base_url: str = "http://localhost:8080"
    openai_model_name: str = "Qwen3.8-27B"

    max_steps: int = 50
    max_tool_retries: int = 2
    model_timeout: int = 100
    max_context_tokens = 8000
    max_tool_chars = 1000
    
    executor_container = "command_executor"

# Instantiate global configuration object
config = Config()
