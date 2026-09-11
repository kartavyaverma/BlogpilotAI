from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from core.config import settings
from graph.streaming import stream_workflow

router = APIRouter(prefix="/api", tags=["runs"])


class AgentRunRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The technical blog topic.",
    )


@router.post("/run")
def run_agent(request_data: AgentRunRequest):
    topic = request_data.topic.strip()

    if len(topic) < 3:
        raise HTTPException(status_code=422, detail="Please provide a valid topic.")

    run_id = uuid.uuid4().hex

    return StreamingResponse(
        stream_workflow(topic=topic, run_id=run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/runs/{run_id}/download")
def download_markdown(run_id: str):
    safe_run_id = "".join(c for c in run_id if c.isalnum() or c in {"-", "_"})

    if safe_run_id != run_id:
        raise HTTPException(status_code=400, detail="Invalid run ID.")

    output_file = settings.outputs_dir / safe_run_id / "blog.md"

    if not output_file.is_file():
        raise HTTPException(status_code=404, detail="Generated Markdown file was not found.")

    return FileResponse(
        path=output_file,
        media_type="text/markdown",
        filename=f"generated-blog-{safe_run_id[:8]}.md",
    )
