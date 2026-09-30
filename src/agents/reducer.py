from __future__ import annotations

import base64
import logging
import re
from pathlib import Path

import requests
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from core.config import settings
from core.llm import get_llm
from schemas.models import GlobalImagePlan, State

logger = logging.getLogger("blogpilot.reducer")


def merge_content(state: State) -> dict:
    plan = state["plan"]

    ordered_sections = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered_sections).strip()
    merged_md = f"# {plan.blog_title}\n\n{body}\n"
    return {"merged_md": merged_md}


DECIDE_IMAGES_SYSTEM = """You are an expert technical editor.
Decide if images/diagrams are needed for THIS blog.

You receive the blog's outline: every heading with its section's opening paragraph.

Rules:
- Max 3 images total.
- Each image must materially improve understanding (diagram/flow/table-like visual).
- Insert placeholders exactly: [[IMAGE_1]], [[IMAGE_2]], [[IMAGE_3]] on their own line,
  directly after the paragraph or heading they illustrate.
- md_with_placeholders is the outline you received with the placeholders inserted.
- If no images needed: md_with_placeholders must equal input and images=[].
- Avoid decorative images; prefer technical diagrams with short labels.
- Each image prompt must name the concrete components and how they connect
  (the boxes, arrows and their labels), since it will be drawn as a diagram.
Return strictly GlobalImagePlan.
"""


def _outline_for_image_planning(md: str) -> str:
    out: list[str] = []
    para: list[str] = []
    in_code = False
    want_para = False

    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            if para:
                out.append("\n".join(para))
                para, want_para = [], False
            continue
        if in_code:
            continue
        if re.match(r"^#{1,6} ", line):
            if para:
                out.append("\n".join(para))
            out.append(line)
            para, want_para = [], True
            continue
        if want_para:
            if line.strip():
                para.append(line)
            elif para:
                out.append("\n".join(para))
                para, want_para = [], False

    if para:
        out.append("\n".join(para))
    return "\n\n".join(out)


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
                        f"{_outline_for_image_planning(merged_md)}"
                    )
                ),
            ]
        )
    except Exception:
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
    pattern = re.compile(rf"^#{{1,{level}}} ", re.M)
    line_end = md.find("\n", heading_pos)
    if line_end == -1:
        return len(md)
    nxt = pattern.search(md, line_end + 1)
    return nxt.start() if nxt else len(md)


def _place_placeholders(original: str, llm_md: str, specs: list[dict]) -> tuple[str, list[dict]]:
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


MERMAID_SYSTEM = """You draw technical diagrams as Mermaid code.

Return ONLY the Mermaid source - no prose, no code fences.

Rules:
- Pick the type that fits: flowchart, sequenceDiagram, stateDiagram-v2,
  classDiagram or erDiagram.
- The diagram is shown in a narrow article column (~760px), so it must not be
  wide: use `flowchart TD` (top-down). Use `flowchart LR` only for a single
  short chain of 5 nodes or fewer.
- Short node labels (about 5 words max). Put any label containing
  punctuation, parentheses or special characters in double quotes.
- At most about 12 nodes; show only what the description asks for.
- No styling: no classDef, style, linkStyle or %%{init}%% directives.
"""

MERMAID_THEME = (
    '%%{init: {"theme": "base", "themeVariables": {'
    '"primaryColor": "#fcfbf9", "primaryBorderColor": "#b65f3a", '
    '"primaryTextColor": "#171717", "lineColor": "#737373", '
    '"secondaryColor": "#f5f3ef", "tertiaryColor": "#f7f5f0", '
    '"fontFamily": "Helvetica, Arial, sans-serif"}}}%%\n'
)


def _clean_mermaid(text: str) -> str:
    fenced = re.search(r"```(?:mermaid)?\s*\n(.*?)```", text, re.S)
    code = fenced.group(1) if fenced else text
    lines = [ln for ln in code.strip().splitlines() if not ln.strip().startswith("%%{")]
    return "\n".join(lines).strip()


def _render_mermaid(code: str) -> bytes:
    source = MERMAID_THEME + code
    try:
        resp = requests.post(
            f"{settings.kroki_url.rstrip('/')}/mermaid/png",
            data=source.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
            timeout=60,
        )
    except requests.RequestException:
        encoded = base64.urlsafe_b64encode(source.encode("utf-8")).decode("ascii")
        resp = requests.get(f"https://mermaid.ink/img/{encoded}", params={"type": "png"}, timeout=60)

    if resp.status_code == 400:
        raise ValueError(resp.text[:500])
    resp.raise_for_status()
    if not resp.headers.get("content-type", "").startswith("image/"):
        raise RuntimeError("Diagram renderer did not return an image.")
    return resp.content


def _mermaid_generate_image_bytes(prompt: str) -> bytes:
    llm = get_llm("images")
    messages = [SystemMessage(content=MERMAID_SYSTEM), HumanMessage(content=prompt)]
    code = _clean_mermaid(str(llm.invoke(messages).content))

    try:
        return _render_mermaid(code)
    except ValueError as err:
        messages += [
            AIMessage(content=code),
            HumanMessage(
                content=f"That Mermaid failed to render:\n{err}\n\nReturn corrected Mermaid only."
            ),
        ]
        code = _clean_mermaid(str(llm.invoke(messages).content))
        return _render_mermaid(code)


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
                img_bytes = _mermaid_generate_image_bytes(spec["prompt"])
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
