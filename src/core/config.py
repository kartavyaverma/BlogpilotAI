from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

PROVIDER_KEYS = {"groq": "GROQ_API_KEY", "moonshot": "MOONSHOT_API_KEY"}


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(
            f"{name} is missing. Please add {name}=... to your .env file "
            f"(see .env.example)."
        )
    return value


def _optional(name: str, default: str = "") -> str:
    return os.getenv(name, default) or default


def _provider() -> str:
    explicit = _optional("LLM_PROVIDER").lower()
    if explicit:
        return explicit
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    if os.getenv("MOONSHOT_API_KEY"):
        return "moonshot"
    return "groq"


@dataclass(frozen=True)
class Settings:
    llm_provider: str = field(default_factory=_provider)

    groq_api_key: str = field(default_factory=lambda: _optional("GROQ_API_KEY"))
    groq_model: str = field(
        default_factory=lambda: _optional("GROQ_MODEL", "openai/gpt-oss-120b")
    )

    moonshot_api_key: str = field(default_factory=lambda: _optional("MOONSHOT_API_KEY"))
    moonshot_model: str = field(
        default_factory=lambda: _optional("MOONSHOT_MODEL", "kimi-k2.6")
    )
    moonshot_base_url: str = field(
        default_factory=lambda: _optional(
            "MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"
        )
    )

    llm_temperature: float = field(
        default_factory=lambda: float(_optional("LLM_TEMPERATURE", "0"))
    )
    llm_max_tokens: int = field(
        default_factory=lambda: int(_optional("LLM_MAX_TOKENS", "8000"))
    )
    llm_max_retries: int = field(
        default_factory=lambda: int(_optional("LLM_MAX_RETRIES", "6"))
    )
    llm_max_concurrency: int = field(
        default_factory=lambda: int(
            _optional("LLM_MAX_CONCURRENCY", "2" if _provider() == "groq" else "0")
        )
    )

    task_models: dict = field(
        default_factory=lambda: {
            task: _optional(f"LLM_MODEL_{task.upper()}")
            for task in ("router", "research", "planner", "writer", "images")
        }
    )

    kroki_url: str = field(
        default_factory=lambda: _optional("KROKI_URL", "https://kroki.io")
    )

    tavily_api_key: str = field(default_factory=lambda: _optional("TAVILY_API_KEY"))
    tavily_max_results: int = field(
        default_factory=lambda: int(_optional("TAVILY_MAX_RESULTS", "6"))
    )
    research_snippet_chars: int = field(
        default_factory=lambda: int(_optional("RESEARCH_SNIPPET_CHARS", "500"))
    )
    research_max_results: int = field(
        default_factory=lambda: int(_optional("RESEARCH_MAX_RESULTS", "24"))
    )

    database_url_raw: str = field(default_factory=lambda: _require("DATABASE_URL"))

    templates_dir: Path = field(default_factory=lambda: BASE_DIR / "src" / "templates")
    static_dir: Path = field(default_factory=lambda: BASE_DIR / "src" / "static")
    images_dir: Path = field(default_factory=lambda: BASE_DIR / "images")
    outputs_dir: Path = field(default_factory=lambda: BASE_DIR / "outputs")

    def __post_init__(self) -> None:
        key_name = PROVIDER_KEYS.get(self.llm_provider)
        if key_name is None:
            raise ValueError(
                f"Unsupported LLM_PROVIDER '{self.llm_provider}'. "
                "Supported values are 'groq' or 'moonshot'."
            )
        if not os.getenv(key_name):
            raise ValueError(
                f"{key_name} is missing. Please add {key_name}=... to your .env file "
                f"(see .env.example) when using LLM_PROVIDER={self.llm_provider}."
            )

    @property
    def database_url(self) -> str:
        url = self.database_url_raw
        if "sslmode=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}sslmode=require"
        return url

    def ensure_directories(self) -> None:
        for directory in (self.images_dir, self.outputs_dir):
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
