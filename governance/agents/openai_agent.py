"""
OpenAI (GPT-4o) council agent.
"""

from __future__ import annotations

import os
from openai import AsyncOpenAI

from agents.base_agent import BaseAgent


class OpenAIAgent(BaseAgent):
    base_url: str | None = None  # Override in subclasses (e.g. xAI, DeepSeek)

    async def _call_api(self, system_prompt: str, user_prompt: str) -> str:
        kwargs: dict = {"api_key": os.environ[self.config["api_key_env"]]}
        if self.base_url:
            kwargs["base_url"] = self.base_url

        client = AsyncOpenAI(**kwargs)
        response = await client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
