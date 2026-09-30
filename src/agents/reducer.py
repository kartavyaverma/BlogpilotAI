from __future__ import annotations

import logging
import re
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from core.config import settings
from core.llm import get_llm
from schemas.models import GlobalImagePlan, State

logger = logging.getLogger("blogpilot.reducer")


def _sanitize_filename(title: str) -> str:
    """Strip filesystem-unsafe characters from blog_title for use as a filename."""
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", title)
    sanitized = sanitized.strip(". ")
    return sanitized[:200] or "blog"


def merge_content(state: State) -> dict:
    plan = state["plan"]

    ordered_sections = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered_sections).strip()
    merged_md = f"# {plan.blog_title}\n\n{body}\n"
    return {"merged_md": merged_md}


DECIDE_IMAGES_SYSTEM = """You are an expert technical editor.
Decide if images/diagrams are needed for THIS blog.

Rules:
- Max 3 images total.
- Each image must materially improve understanding (diagram/flow/table-like visual).
- Insert placeholders exactly: [[IMAGE_1]], [[IMAGE_2]], [[IMAGE_3]].
- If no images needed: md_with_placeholders must equal input and images=[].
- Avoid decorative images; prefer technical diagrams with short labels.
Return strictly GlobalImagePlan.
"""


def decide_images(state: State) -> dict:
    planner = get_llm("images").with_structured_output(GlobalImagePlan)
    merged_md = state["merged_md"]
    plan = state["plan"]
    assert plan is not None

    try:
        image_plan = planner.invoke(
            [
                SystemMessage(content=DECIDE_IMAGES_SYSTEM),
                HumanMessage(
                    content=(
                        f"Blog kind: {plan.blog_kind}\n"
                        f"Topic: {state['topic']}\n\n"
                        "Insert placeholders + propose image prompts.\n\n"
                        f"{merged_md}"
                    )
                ),
            ]
        )
    except Exception:
        # Diagrams are optional; a failure here must not discard the article
        # the writers already produced.
        logger.warning("Image planning failed; publishing without diagrams.", exc_info=True)
        return {"md_with_placeholders": merged_md, "image_specs": []}

    md, specs = _place_placeholders(
        merged_md,
        image_plan.md_with_placeholders,
        [img.model_dump() for img in image_plan.images],
    )

    return {
        "md_with_placeholders": md,
        "image_specs": specs,
    }


def _section_end(md: str, heading_pos: int, level: int) -> int:
    """Index where the section starting at heading_pos ends (next heading of the same or higher level)."""
    pattern = re.compile(rf"^#{{1,{level}}} ", re.M)
    line_end = md.find("\n", heading_pos)
    if line_end == -1:
        return len(md)
    nxt = pattern.search(md, line_end + 1)
    return nxt.start() if nxt else len(md)


def _place_placeholders(original: str, llm_md: str, specs: list[dict]) -> tuple[str, list[dict]]:
    """Insert image placeholders into the untouched merged article.

    The model is asked to return the whole article with placeholders, but when
    it copies ~3k words back it can truncate ("... remaining sections unchanged
    ...") or silently reword. So its copy is used only to learn *where* each
    placeholder goes: after the paragraph it followed, else at the end of its
    section. The article text itself always comes from the writers.
    Specs that cannot be anchored are dropped, so no image is generated for a
    slot that would never be shown.
    """
    md = original
    kept: list[dict] = []

    for spec in specs:
        placeholder = spec.get("placeholder", "")
        idx = llm_md.find(placeholder) if placeholder else -1
        if idx == -1:
            continue

        before = llm_md[:idx].rstrip()
        insert_at = -1

        preceding_block = before.split("\n\n")[-1].strip()
        if preceding_block and not preceding_block.startswith("[[IMAGE_"):
            pos = md.find(preceding_block)
            if pos != -1:
                insert_at = pos + len(preceding_block)

        if insert_at == -1:
            headings = list(re.finditer(r"^(#{1,6}) .+$", before, re.M))
            if headings:
                heading = headings[-1]
                pos = md.find(heading.group(0))
                if pos != -1:
                    insert_at = _section_end(md, pos, len(heading.group(1)))

        if insert_at == -1:
            continue

        head = md[:insert_at].rstrip()
        tail = md[insert_at:].lstrip("\n")
        md = f"{head}\n\n{placeholder}\n\n{tail}"
        kept.append(spec)

    return md, kept


def _gemini_generate_image_bytes(prompt: str) -> bytes:
    from google import genai
    from google.genai import types

    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set.")

    client = genai.Client(api_key=settings.google_api_key)

    resp = client.models.generate_content(
        model=settings.gemini_image_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",
                )
            ],
        ),
    )

    parts = getattr(resp, "parts", None)
    if not parts and getattr(resp, "candidates", None):
        try:
            parts = resp.candidates[0].content.parts
        except Exception:
            parts = None

    if not parts:
        raise RuntimeError("No image content returned (safety/quota/SDK change).")

    for part in parts:
        inline = getattr(part, "inline_data", None)
        if inline and getattr(inline, "data", None):
            return inline.data

    raise RuntimeError("No inline image bytes found in response.")


def generate_and_place_images(state: State) -> dict:
    plan = state["plan"]
    assert plan is not None

    md = state.get("md_with_placeholders") or state["merged_md"]
    image_specs = state.get("image_specs", []) or []

    settings.ensure_directories()

    if not image_specs:
        return {"final": md}

    images_dir = settings.images_dir
    images_dir.mkdir(parents=True, exist_ok=True)

    for spec in image_specs:
        placeholder = spec["placeholder"]
        raw_filename = spec.get("filename", "")
        filename = Path(raw_filename).name or f"image_{placeholder}.png"
        if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            filename = f"{filename}.png"

        out_path = images_dir / filename

        if not out_path.exists():
            try:
                img_bytes = _gemini_generate_image_bytes(spec["prompt"])
                out_path.write_bytes(img_bytes)
            except Exception as e:
                prompt_block = (
                    f"\n\n> **[IMAGE GENERATION FAILED]** {spec.get('caption','')}\n>\n"
                    f"> **Alt:** {spec.get('alt','')}\n>\n"
                    f"> **Prompt:** {spec.get('prompt','')}\n>\n"
                    f"> **Error:** {e}\n\n"
                )
                md = md.replace(placeholder, prompt_block)
                continue

        alt_text = spec.get("alt", "").strip() or spec.get("caption", "").strip() or "Technical Diagram"
        caption_text = spec.get("caption", "").strip()
        caption_md = f"\n*{caption_text}*\n" if caption_text else ""
        image_md = f"\n\n![{alt_text}](/images/{filename}){caption_md}\n"
        md = md.replace(placeholder, image_md)

    return {"final": md}


def build_reducer_subgraph():
    reducer_graph = StateGraph(State)
    reducer_graph.add_node("merge_content", merge_content)
    reducer_graph.add_node("decide_images", decide_images)
    reducer_graph.add_node("generate_and_place_images", generate_and_place_images)
    reducer_graph.add_edge(START, "merge_content")
    reducer_graph.add_edge("merge_content", "decide_images")
    reducer_graph.add_edge("decide_images", "generate_and_place_images")
    reducer_graph.add_edge("generate_and_place_images", END)
    return reducer_graph.compile()
