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

    openai_base_url: str = "http://localhost:8080"
    openai_model_name: str = "Qwen3.8-27B"


# Instantiate global configuration object
config = Config()
