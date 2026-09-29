from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


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


def _default_provider() -> str:
    """Pick a provider from whichever key is actually present.

    Kimi K2 on Groq wins when its key is set: it is free, fast and the best
    tool caller of the bunch, which is what the agent graph leans on.
    """
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    if os.getenv("OPENROUTER_API_KEY"):
        return "openrouter"
    if os.getenv("MOONSHOT_API_KEY"):
        return "moonshot"
    if os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        return "gemini"
    return "openai"


@dataclass(frozen=True)
class Settings:
    llm_provider: str = field(
        default_factory=lambda: _optional(
            "LLM_PROVIDER",
            _default_provider(),
        ).lower()
    )

    # Kimi K2 (Moonshot) served by Groq - 256K context, strong tool use.
    groq_api_key: str = field(default_factory=lambda: _optional("GROQ_API_KEY"))
    groq_model: str = field(
        default_factory=lambda: _optional(
            "GROQ_MODEL", "moonshotai/kimi-k2-instruct-0905"
        )
    )

    # Kimi K2 through OpenRouter (free variant) - OpenAI-compatible.
    openrouter_api_key: str = field(
        default_factory=lambda: _optional("OPENROUTER_API_KEY")
    )
    openrouter_model: str = field(
        default_factory=lambda: _optional("OPENROUTER_MODEL", "moonshotai/kimi-k2:free")
    )
    openrouter_base_url: str = field(
        default_factory=lambda: _optional(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
    )

    # Kimi K2 straight from Moonshot (paid, OpenAI-compatible).
    moonshot_api_key: str = field(default_factory=lambda: _optional("MOONSHOT_API_KEY"))
    moonshot_model: str = field(
        default_factory=lambda: _optional("MOONSHOT_MODEL", "kimi-k2-0905-preview")
    )
    moonshot_base_url: str = field(
        default_factory=lambda: _optional(
            "MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"
        )
    )

    openai_api_key: str = field(default_factory=lambda: _optional("OPENAI_API_KEY"))
    openai_model: str = field(
        default_factory=lambda: _optional("OPENAI_MODEL", "gpt-4o-mini")
    )
    llm_temperature: float = field(
        default_factory=lambda: float(_optional("LLM_TEMPERATURE", "0"))
    )

    gemini_model: str = field(
        default_factory=lambda: _optional("GEMINI_MODEL", "gemini-2.5-flash")
    )
    google_api_key: str = field(default_factory=lambda: _optional("GOOGLE_API_KEY"))
    gemini_image_model: str = field(
        default_factory=lambda: _optional("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    )

    tavily_api_key: str = field(default_factory=lambda: _optional("TAVILY_API_KEY"))
    tavily_max_results: int = field(
        default_factory=lambda: int(_optional("TAVILY_MAX_RESULTS", "6"))
    )

    database_url_raw: str = field(default_factory=lambda: _require("DATABASE_URL"))

    app_host: str = field(default_factory=lambda: _optional("APP_HOST", "127.0.0.1"))
    app_port: int = field(default_factory=lambda: int(_optional("APP_PORT", "8000")))
    app_reload: bool = field(
        default_factory=lambda: _optional("APP_RELOAD", "true").lower() == "true"
    )

    base_dir: Path = field(default_factory=lambda: BASE_DIR)
    templates_dir: Path = field(default_factory=lambda: BASE_DIR / "src" / "templates")
    static_dir: Path = field(default_factory=lambda: BASE_DIR / "src" / "static")
    images_dir: Path = field(default_factory=lambda: BASE_DIR / "images")
    outputs_dir: Path = field(default_factory=lambda: BASE_DIR / "outputs")

    def __post_init__(self) -> None:
        required_key = {
            "groq": ("GROQ_API_KEY", self.groq_api_key),
            "openrouter": ("OPENROUTER_API_KEY", self.openrouter_api_key),
            "moonshot": ("MOONSHOT_API_KEY", self.moonshot_api_key),
            "gemini": ("GOOGLE_API_KEY", self.google_api_key),
            "openai": ("OPENAI_API_KEY", self.openai_api_key),
        }.get(self.llm_provider)

        if required_key is None:
            raise ValueError(
                f"Unsupported LLM_PROVIDER '{self.llm_provider}'. Supported values are "
                "'groq', 'openrouter', 'moonshot', 'gemini' or 'openai'."
            )

        name, value = required_key
        if not value:
            raise ValueError(
                f"{name} is missing. Please add {name}=... to your .env file "
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
