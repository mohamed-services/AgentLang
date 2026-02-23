"""
Anthropic (Claude) council agent.
"""

from __future__ import annotations

import os
import anthropic

from agents.base_agent import BaseAgent


class AnthropicAgent(BaseAgent):
    async def _call_api(self, system_prompt: str, user_prompt: str) -> str:
        client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        message = await client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text
