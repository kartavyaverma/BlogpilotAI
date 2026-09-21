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


@dataclass(frozen=True)
class Settings:
    llm_provider: str = field(
        default_factory=lambda: _optional(
            "LLM_PROVIDER",
            "gemini" if os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY") else "openai",
        ).lower()
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
        if self.llm_provider == "gemini":
            if not self.google_api_key:
                raise ValueError(
                    "GOOGLE_API_KEY is missing. Please add GOOGLE_API_KEY=... to your .env file "
                    "(see .env.example) when using LLM_PROVIDER=gemini."
                )
        elif self.llm_provider == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY is missing. Please add OPENAI_API_KEY=... to your .env file "
                    "(see .env.example) when using LLM_PROVIDER=openai."
                )
        else:
            raise ValueError(
                f"Unsupported LLM_PROVIDER '{self.llm_provider}'. Supported values are 'gemini' or 'openai'."
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
