from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from core.config import settings


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    if settings.llm_provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=settings.groq_model,
            temperature=settings.llm_temperature,
            api_key=settings.groq_api_key,
        )

    if settings.llm_provider == "openrouter":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openrouter_model,
            temperature=settings.llm_temperature,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )

    if settings.llm_provider == "moonshot":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.moonshot_model,
            temperature=settings.llm_temperature,
            api_key=settings.moonshot_api_key,
            base_url=settings.moonshot_base_url,
        )

    if settings.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=settings.llm_temperature,
            google_api_key=settings.google_api_key,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.llm_temperature,
        api_key=settings.openai_api_key,
    )
