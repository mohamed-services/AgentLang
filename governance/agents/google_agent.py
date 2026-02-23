"""
Google (Gemini) council agent.
"""

from __future__ import annotations

import os
import google.generativeai as genai

from agents.base_agent import BaseAgent


class GoogleAgent(BaseAgent):
    async def _call_api(self, system_prompt: str, user_prompt: str) -> str:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt,
        )
        # google-generativeai doesn't have a native async client; run synchronously
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(user_prompt),
        )
        return response.text
