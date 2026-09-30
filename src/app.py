from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routes import health, pages, runs
from core.config import settings

settings.ensure_directories()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

app = FastAPI(
    title="LangGraph Blog Agent",
    description="FastAPI frontend for the LangGraph multi-agent blog-writing workflow.",
    version="1.1.0",
)

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.mount("/images", StaticFiles(directory=str(settings.images_dir)), name="images")

app.include_router(pages.router)
app.include_router(health.router)
app.include_router(runs.router)
