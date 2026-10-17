from typing import Optional
from src.config import config
import openai

class ModelClient:

    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None):
            self.base_url = base_url or config.openai_base_url
            self.model_name = model_name or config.openai_model_name
            self._client = openai.OpenAI()

    def generate(self, prompt: str) -> str:
          
          
          return