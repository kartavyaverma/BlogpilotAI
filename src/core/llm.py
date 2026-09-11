"""
src/core/llm.py

Single Responsibility: construct the one shared chat LLM client used by
every agent node (router, research, orchestrator, worker). Swapping
models/providers or tuning client-level settings happens only here.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI

from core.config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """Return the shared ChatOpenAI client (constructed once, memoized)."""
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.llm_temperature,
        api_key=settings.openai_api_key,
    )
