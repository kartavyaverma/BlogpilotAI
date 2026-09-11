"""
src/core/config.py

Single Responsibility: load & validate environment variables and define
the filesystem layout (templates/static/images/outputs directories).

Every other module MUST import `settings` from here instead of calling
`os.getenv(...)` or hardcoding paths directly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env once. BASE_DIR is the project root (one level above src/).
# ---------------------------------------------------------------------------
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
    # --- LLM -------------------------------------------------------------
    openai_api_key: str = field(default_factory=lambda: _require("OPENAI_API_KEY"))
    openai_model: str = field(
        default_factory=lambda: _optional("OPENAI_MODEL", "gpt-4o-mini")
    )
    llm_temperature: float = field(
        default_factory=lambda: float(_optional("LLM_TEMPERATURE", "0"))
    )

    # --- Research (Tavily) -------------------------------------------------
    tavily_api_key: str = field(default_factory=lambda: _optional("TAVILY_API_KEY"))
    tavily_max_results: int = field(
        default_factory=lambda: int(_optional("TAVILY_MAX_RESULTS", "6"))
    )

    # --- Image generation (Gemini) -----------------------------------------
    google_api_key: str = field(default_factory=lambda: _optional("GOOGLE_API_KEY"))
    gemini_image_model: str = field(
        default_factory=lambda: _optional("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    )

    # --- Database / checkpointer -------------------------------------------
    database_url_raw: str = field(default_factory=lambda: _require("DATABASE_URL"))

    # --- App server ----------------------------------------------------------
    app_host: str = field(default_factory=lambda: _optional("APP_HOST", "127.0.0.1"))
    app_port: int = field(default_factory=lambda: int(_optional("APP_PORT", "8000")))
    app_reload: bool = field(
        default_factory=lambda: _optional("APP_RELOAD", "true").lower() == "true"
    )

    # --- Filesystem layout (relative to the project root, not cwd) --------
    base_dir: Path = field(default_factory=lambda: BASE_DIR)
    templates_dir: Path = field(default_factory=lambda: BASE_DIR / "src" / "templates")
    static_dir: Path = field(default_factory=lambda: BASE_DIR / "src" / "static")
    images_dir: Path = field(default_factory=lambda: BASE_DIR / "images")
    outputs_dir: Path = field(default_factory=lambda: BASE_DIR / "outputs")

    @property
    def database_url(self) -> str:
        """DATABASE_URL with sslmode=require appended if not already present."""
        url = self.database_url_raw
        if "sslmode=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}sslmode=require"
        return url

    def ensure_directories(self) -> None:
        for directory in (self.images_dir, self.outputs_dir):
            directory.mkdir(parents=True, exist_ok=True)


# Module-level singleton — import this, don't instantiate Settings() yourself.
settings = Settings()
