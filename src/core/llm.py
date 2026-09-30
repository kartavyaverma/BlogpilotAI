from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from core.config import settings


def _default_model() -> str:
    if settings.llm_provider == "moonshot":
        return settings.moonshot_model
    return settings.groq_model


def model_for(task: str | None) -> str:
    return settings.task_models.get(task or "", "") or _default_model()


@lru_cache(maxsize=None)
def get_llm(task: str | None = None) -> BaseChatModel:
    model = model_for(task)

    if settings.llm_provider == "moonshot":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=settings.llm_temperature,
            max_retries=settings.llm_max_retries,
            max_tokens=settings.llm_max_tokens,
            api_key=settings.moonshot_api_key,
            base_url=settings.moonshot_base_url,
        )

    from langchain_groq import ChatGroq

    return ChatGroq(
        model=model,
        temperature=settings.llm_temperature,
        max_retries=settings.llm_max_retries,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.groq_api_key,
    )
