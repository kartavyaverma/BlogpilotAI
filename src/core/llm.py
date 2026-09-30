from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from core.config import settings

# Agent tasks that can each be pointed at their own model via LLM_MODEL_<TASK>.
TASKS = ("router", "research", "planner", "writer", "images")


def _default_model() -> str:
    return {
        "groq": settings.groq_model,
        "moonshot": settings.moonshot_model,
        "gemini": settings.gemini_model,
        "openai": settings.openai_model,
    }[settings.llm_provider]


def model_for(task: str | None) -> str:
    """Resolve the model for a task: its LLM_MODEL_<TASK> override, else the provider default."""
    return settings.task_models.get(task or "", "") or _default_model()


@lru_cache(maxsize=None)
def get_llm(task: str | None = None) -> BaseChatModel:
    model = model_for(task)

    if settings.llm_provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=model,
            temperature=settings.llm_temperature,
            max_retries=settings.llm_max_retries,
            max_tokens=settings.llm_max_tokens,
            api_key=settings.groq_api_key,
        )

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

    if settings.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=settings.llm_temperature,
            max_retries=settings.llm_max_retries,
            google_api_key=settings.google_api_key,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model,
        temperature=settings.llm_temperature,
        max_retries=settings.llm_max_retries,
        api_key=settings.openai_api_key,
    )
