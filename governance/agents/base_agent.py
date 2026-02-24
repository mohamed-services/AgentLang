"""
Abstract base class for all AgentLang council agents.
"""

from __future__ import annotations

import asyncio
import random
import re
from abc import ABC, abstractmethod

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0  # seconds; doubles each attempt (2s, 4s, 8s) plus jitter

VOTE_LINE_RE = re.compile(r"^VOTE:\s*(APPROVE|REJECT|ABSTAIN)", re.IGNORECASE)
REASONING_RE = re.compile(r"REASONING:\s*(.+)", re.DOTALL | re.IGNORECASE)


class BaseAgent(ABC):
    """
    Each agent subclass implements `_call_api` which returns the raw LLM response text.
    `vote()` is the public interface used by the orchestrator.
    """

    def __init__(self, config: dict):
        self.config = config
        self.agent_name: str = config["name"]
        self.company: str = config["company"]
        self.model: str = config["model"]

    @abstractmethod
    async def _call_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call the underlying LLM API and return the raw text response."""

    async def vote(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        """
        Returns (vote_value, reasoning) where vote_value is APPROVE/REJECT/ABSTAIN.
        Retries up to MAX_RETRIES times with exponential backoff on transient errors.
        Raises on the final failure (caller handles as ERROR).
        """
        last_exc: Exception
        for attempt in range(MAX_RETRIES):
            try:
                raw = await self._call_api(system_prompt, user_prompt)
                return self.parse_vote(raw)
            except Exception as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)
        raise last_exc

    @staticmethod
    def parse_vote(raw: str) -> tuple[str, str]:
        """
        Parse the LLM response.
        Expected format (first two non-blank lines):
          VOTE: APPROVE|REJECT|ABSTAIN
          REASONING: ...
        """
        raw = raw.strip()
        vote_match = VOTE_LINE_RE.search(raw)
        vote = vote_match.group(1).upper() if vote_match else "ABSTAIN"

        reasoning_match = REASONING_RE.search(raw)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else raw

        return vote, reasoning
