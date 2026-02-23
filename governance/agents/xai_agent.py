"""
xAI (Grok) council agent.
Uses the OpenAI SDK pointed at api.x.ai.
"""

from __future__ import annotations

from agents.openai_agent import OpenAIAgent


class XAIAgent(OpenAIAgent):
    base_url = "https://api.x.ai/v1"
