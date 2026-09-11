"""
src/app.py

FastAPI entrypoint. Single Responsibility: application wiring — mount
routers, static files, and the generated-images directory. All business
logic lives under core/, schemas/, agents/, graph/, and api/routes/.

Run with (from inside src/):
    uvicorn app:app --reload
or:
    python app.py
"""

from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routes import health, pages, runs
from core.config import settings

# ---------------------------------------------------------
# Ensure the runtime directories (images/, outputs/) exist.
# ---------------------------------------------------------
settings.ensure_directories()

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------
app = FastAPI(
    title="LangGraph Blog Agent",
    description="FastAPI frontend for the LangGraph multi-agent blog-writing workflow.",
    version="1.1.0",
)

# ---------------------------------------------------------
# Static files
# ---------------------------------------------------------
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

# Generated images are served from here (agents/reducer.py writes into settings.images_dir).
app.mount("/images", StaticFiles(directory=str(settings.images_dir)), name="images")

# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------
app.include_router(pages.router)
app.include_router(health.router)
app.include_router(runs.router)


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
