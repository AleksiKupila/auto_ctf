from typing import Optional
from src.config import config
from src.tools.registry import tool_schemas
import openai


class ModelClient:

    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None, tools: Optional[list] = None, timeout: int = 120):
            self.base_url = base_url or config.openai_base_url
            self.model_name = model_name or config.openai_model_name
            self.tools = tools
            self._client = openai.OpenAI(
                  base_url=self.base_url,
                  api_key="local",
                  timeout=timeout,
                  max_retries=1
            )

    def generate(self, prompt: list, use_tools: bool) -> str:

        try:    
                response = self._client.chat.completions.create(
                        model=self.model_name,
                        messages=prompt,
                        tools=self.tools if use_tools else [],
                        stream=False
                )

                return response

        except Exception as e:
              raise ConnectionError(e)
