from typing import Optional
from src.config import config
from src.tools.registry import tool_schemas
import openai


class ModelClient:

    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None, tools: Optional[list] = None):
            self.base_url = base_url or config.openai_base_url
            self.model_name = model_name or config.openai_model_name
            self.tools = tools
            self._client = openai.OpenAI(
                  base_url=self.base_url,
                  api_key="local",
                  timeout=120,
                  max_retries=1
            )

    def generate(self, prompt: list) -> str:

        try:
                response = self._client.chat.completions.create(
                        model=self.model_name,
                        messages=prompt,
                        tools=self.tools,
                        stream=False
                )

                return response

        except Exception as e:
              raise ConnectionError(e)
