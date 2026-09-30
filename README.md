# BlogPilot AI
### Autonomous Multi-Agent Technical Blog Writing System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED.svg)](Dockerfile)

**BlogPilot AI** is a production-grade, multi-agent editorial pipeline powered by **LangGraph**, **FastAPI**, and modern LLMs. It transforms a single topic or prompt into an in-depth, research-backed, structured technical blog post complete with automated diagram planning, multi-modal illustrations, and real-time streaming to an interactive web UI via Server-Sent Events (SSE).

---

## Key Highlights

- **Intelligent Routing**: Dynamically classifies user prompts into *closed-book* (in-depth reasoning), *hybrid* (verification required), or *open-book* (breaking/fast-evolving topics requiring web search).
- **Autonomous Deep Research**: Leverages **Tavily Search API** to fetch up-to-date facts, documentation, and industry benchmarks before drafting.
- **Parallel Section Fan-Out**: The Orchestrator agent crafts a comprehensive blog outline and fans out section generation to parallel worker agents simultaneously.
- **Reducer Subgraph & Visuals**: An editorial reducer agent stitches content seamlessly, audits the post for visual diagram opportunities, and draws technical diagrams for free: the LLM writes each figure as **Mermaid** code and **Kroki** renders it to PNG, so every label is exact (Gemini image generation remains available via `IMAGE_PROVIDER=gemini`).
- **Free by Default, Kimi for Quality**: Runs for $0 on **Groq** (`openai/gpt-oss-120b`), tested end to end. Switch to **Kimi (Moonshot)** (262K context, ~$0.06 per article) for the best results. Gemini and OpenAI remain drop-in alternatives, and each agent task can use its own model.
- **Real-Time SSE Streaming**: Live progress events, agent status updates, and tokens stream directly to the browser interface.
- **Durable State Checkpointing**: Integrated PostgreSQL checkpointer preserves agent graph state across interrupts and execution steps.
- **Clean Architecture**: Strictly separated concerns (Core, Schemas, Agents, Graph Topology, API Routes, and UI Assets).

---

## Architecture & Multi-Agent Flow

The system orchestrates specialized agents in an acyclic directed graph with persistent state and dynamic subgraphs:

```mermaid
flowchart TD
    Start([User Prompt]) --> Router[Router Agent]
    
    Router -->|Open / Hybrid Book| Researcher[Research Agent\nTavily Web Search]
    Router -->|Closed Book| Orchestrator[Orchestrator Agent\nPlan & Section Outlines]
    Researcher --> Orchestrator

    subgraph ParallelWorkers [Parallel Fan-Out]
        W1[Section Worker 1]
        W2[Section Worker 2]
        W3[Section Worker N]
    end

    Orchestrator --> ParallelWorkers

    subgraph ReducerSubgraph [Reducer Subgraph]
        Merge[Merge Content] --> Decide[Decide Diagrams & Images]
        Decide --> Generate[Generate & Place Visuals\nMermaid + Kroki]
    end

    ParallelWorkers --> ReducerSubgraph
    ReducerSubgraph --> DB[(PostgreSQL\nCheckpointer)]
    ReducerSubgraph --> Output([Final Markdown Post + Visuals])
```

---

## Project Structure

```
BlogPilot-AI/
├── src/
│   ├── app.py                     FastAPI entrypoint (mounts API routers & UI)
│   │
│   ├── core/
│   │   ├── config.py              Centralized environment settings & paths
│   │   └── llm.py                 LLM factory (shared client across agents)
│   │
│   ├── schemas/
│   │   └── models.py              Pydantic schemas (Task, Plan, State, Evidence)
│   │
│   ├── agents/
│   │   ├── router.py              Routing decision (closed/hybrid/open book)
│   │   ├── research.py            Tavily search query synthesis & summarization
│   │   ├── orchestrator.py        Section planning & worker fan-out
│   │   ├── worker.py              Parallel section writer
│   │   └── reducer.py             Merge subgraph + image decision & generation
│   │
│   ├── graph/
│   │   ├── builder.py             LangGraph compilation & PostgreSQL checkpointer
│   │   └── streaming.py           SSE streaming runner for graph execution
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── pages.py           GET / (Frontend UI)
│   │       ├── health.py          GET /api/health (Liveness check)
│   │       └── runs.py            POST /api/run, GET /api/runs/{id}/download
│   │
│   ├── templates/
│   │   └── index.html             Interactive frontend UI
│   └── static/
│       ├── css/style.css          Modern dark-mode styling
│       └── js/app.js              SSE consumer & real-time UI logic
│
├── scripts/
│   ├── run_dev.sh                 Linux/macOS dev launcher
│   └── run_dev.ps1                Windows PowerShell dev launcher
│
├── tests/
│   └── test_project_structure.py  Architecture and integrity tests
│
├── .env.example                   Template for environment variables
├── .gitignore                     Git exclusion rules
├── .dockerignore                  Docker build exclusions
├── Dockerfile                     Containerization specification
├── render.yaml                    Production deployment blueprint for Render
├── requirements.txt               Pinned Python dependencies
├── LICENSE                        Apache 2.0 License
└── README.md                      Project documentation
```

### Separation of Concerns

| Layer | Responsibility | What It Never Does |
|---|---|---|
| `core/` | Configuration, environment loading, shared LLM initialization | Agent prompt logic, HTTP handling, graph wiring |
| `schemas/` | Pydantic data contracts (`State`, `Plan`, `EvidenceItem`) | Business logic or execution side-effects |
| `agents/` | Pure business logic and prompts for individual nodes | Graph topology, routing transport, HTTP endpoints |
| `graph/builder.py` | Graph wiring, state transitions, and checkpointer setup | Direct prompt authoring or HTTP responses |
| `graph/streaming.py` | Executing the graph and yielding Server-Sent Events (SSE) | Business decisions or API routing |
| `api/routes/` | HTTP request validation and response dispatching | Agent execution internals (delegates to graph) |
| `src/app.py` | FastAPI application lifecycle and static/router mounting | Direct agent invocation |

---

## Prerequisites

- **Python**: 3.11 or higher
- **PostgreSQL**: Required for state checkpointing (use a local instance, Docker, or managed service such as Supabase / Neon / Render Postgres)
- **API Keys**:
  - `GROQ_API_KEY`: **Free, and the default.** Runs `openai/gpt-oss-120b` (Groq serves no Kimi model). [console.groq.com](https://console.groq.com) -> *API Keys*
  - `MOONSHOT_API_KEY`: **Best quality.** Runs **Kimi** straight from Moonshot - 262K context and excellent agent/tool use. [platform.moonshot.ai](https://platform.moonshot.ai) -> *API Keys*. **Paid: there is no free tier, the account needs a balance**
  - `GOOGLE_API_KEY`: Only if using Gemini (`LLM_PROVIDER=gemini` or `IMAGE_PROVIDER=gemini`). Diagrams are free and keyless by default
  - `OPENAI_API_KEY`: Required if using OpenAI (`LLM_PROVIDER=openai`)
  - `TAVILY_API_KEY`: Required for online research and fact-finding (open/hybrid mode)

### Choosing a model provider

| Provider | `LLM_PROVIDER` | Default model | Context | Cost |
|---|---|---|---|---|
| **Moonshot** (best quality, Kimi) | `moonshot` | `kimi-k2.6` | 262K | Paid only - $0.95 / M input, $4.00 / M output |
| **Groq** (free, tested) | `groq` | `openai/gpt-oss-120b` | 131K nominal, **8K tokens/min on free tier** | Free: 200K tokens/day per model (~6 articles/day) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | 1M | Free tier / paid |
| OpenAI | `openai` | `gpt-4o-mini` | 128K | Paid |

If `LLM_PROVIDER` is not set, the provider is picked from whichever key is present, preferring `MOONSHOT_API_KEY`, then `GROQ_API_KEY`.

### What each run costs

Only the **LLM provider** and **Tavily** meter usage; the app, PostgreSQL and diagram rendering are free.

| Component | When it bills | Rough cost |
|---|---|---|
| Kimi (`moonshot`) | Every agent call: router, research extraction, planner, one call per section, reducer | ~$0.06 per article (measured) |
| Groq | Free tier: 8K tokens/minute and 200K tokens/day per model (~6 articles/day at ~30K tokens each) | $0 |
| Diagrams (`IMAGE_PROVIDER=mermaid`) | One small LLM call per figure + Kroki render | Free (Kroki is free and keyless) |
| Diagrams (`IMAGE_PROVIDER=gemini`) | Once per planned figure (needs `GOOGLE_API_KEY`) | Free tier, then per image |
| Tavily research | Only on `hybrid` / `open_book` topics, ~5 searches per run | Free tier: 1,000 searches / month |
| PostgreSQL | Checkpointer storage | Free tier on Neon / Supabase / Render |

A measured run - a 2,553-word article on "How vector databases actually retrieve information" - consumed **8,940 input and 11,591 output tokens** across ~10 agent calls, which is **$0.055** at Kimi's `kimi-k2.6` rates. Research-heavy (`open_book`) topics push input tokens higher, since Tavily results are fed into the prompt.

Output tokens dominate the bill at 4x the input rate, so `LLM_MAX_TOKENS` is the most effective cost lever. Kimi also charges only $0.16 / M for cached input, so repeated runs on similar topics cost less.

### Choosing models per task

The pipeline makes five kinds of LLM call. Each can use its own model through `LLM_MODEL_<TASK>`; any task left unset uses the provider's default model.

| Task (`LLM_MODEL_…`) | What it does | What matters | Free: Groq | Paid: Kimi |
|---|---|---|---|---|
| `ROUTER` | Classify the topic, write search queries | Reliable JSON, speed | `openai/gpt-oss-120b` | `kimi-k2.6` |
| `RESEARCH` | Extract evidence from search results | Largest input | `openai/gpt-oss-120b` | `kimi-k2.6` |
| `PLANNER` | Design the outline and section goals | Reasoning | `openai/gpt-oss-120b` | `kimi-k2.6` |
| `WRITER` | Write each section (parallel) | Writing quality, most tokens | `openai/gpt-oss-120b` | `kimi-k2.6` |
| `IMAGES` | Choose where diagrams go, then write each as Mermaid | Reliable structure | `openai/gpt-oss-120b` | `kimi-k2.6` |

**Why one model everywhere on Groq?** Each candidate was run through the full pipeline on the same research-heavy topic:

| Groq model | Result |
|---|---|
| `openai/gpt-oss-120b` | **Completed** - 7/7 sections, 2,210 words, 8 code samples, ~4 min with `LLM_MAX_CONCURRENCY=2` |
| `openai/gpt-oss-20b` | Failed - produced a malformed tool call during research (`evidencePack` instead of `EvidencePack`) |
| `qwen/qwen3.8-27b` | Failed - a reasoning model; spent ~2,700 tokens thinking in the first step and exhausted its per-minute budget |

\*Groq's free tier caps every model at **8,000 tokens per minute, and a single request cannot exceed that.** The 131K context window is therefore not reachable on the free tier. A full article (~8K tokens) is larger than one request may be, so image planning works from a compact outline instead: each heading plus its opening paragraph (~1K tokens).

**Settings that make the free tier work** (already the defaults in `.env.example`):
- `LLM_MAX_CONCURRENCY=2` - writes sections two at a time instead of all at once, so a run stays under 8K tokens/min. Set `0` (unlimited) on paid plans for full speed.
- `LLM_MAX_RETRIES=6` - waits out the provider's `retry-after` window on HTTP 429.
- `RESEARCH_MAX_RESULTS=24`, `RESEARCH_SNIPPET_CHARS=500` - dedupe, clip and cap search results before extraction. Without this, a topic that triggers research sent ~12K tokens in one request.

### Diagrams: free, and why not an AI image model

With the default `IMAGE_PROVIDER=mermaid`, the pipeline draws each figure in two steps:

1. Your LLM writes it as [Mermaid](https://mermaid.js.org) code (flowchart, sequence, state, class or ER diagram).
2. [Kroki](https://kroki.io) renders that to PNG. If Kroki is unreachable, [mermaid.ink](https://mermaid.ink) is used instead.

Both renderers are free and need no key. The app's colour palette is applied automatically. If the Mermaid has a syntax error, the renderer's message goes back to the LLM for one repair pass.

Free AI image models were tested for this and rejected. Asked for a labelled RAG pipeline diagram, Pollinations/Flux produced unreadable pseudo-text and meaningless shapes, which is the known weakness of diffusion models on diagrams. Mermaid labels come out exactly as written.

Diagrams are prompted to lay out top-down, so they stay readable in the ~760px article column. A wide left-to-right layout of a 12-node architecture rendered 1642px wide and had to be shrunk to under half size.

Set `IMAGE_PROVIDER=gemini` to use Gemini's image model instead (needs a working `GOOGLE_API_KEY`).

> **Model IDs move.** Moonshot has already retired `kimi-k2-0905-preview`, and Groq dropped every Kimi model from its catalogue. If a run fails with a 404, check the provider's current model list and update `MOONSHOT_MODEL` / `GROQ_MODEL`.

> **Keep `LLM_MAX_TOKENS` set.** OpenAI-compatible endpoints reserve the model's entire output window up front unless a cap is given, which low-balance accounts reject with HTTP 402.

---

## Environment Configuration

Create a `.env` file in the project root by copying `.env.example`:

```bash
cp .env.example .env
```

Configure the following variables in `.env`:

| Variable | Description | Required | Default |
|---|---|:---:|---|
| `LLM_PROVIDER` | LLM backend (`moonshot`, `groq`, `gemini` or `openai`) | No | `moonshot` if `MOONSHOT_API_KEY` is set |
| `LLM_MAX_TOKENS` | Max output tokens per agent call | No | `8000` |
| `LLM_MAX_RETRIES` | Retries on HTTP 429 (honours `retry-after`) | No | `6` |
| `LLM_MAX_CONCURRENCY` | Agent calls in flight at once; `0` = unlimited | No | `0` |
| `LLM_MODEL_ROUTER` / `_RESEARCH` / `_PLANNER` / `_WRITER` / `_IMAGES` | Per-task model override | No | provider default |
| `MOONSHOT_API_KEY` | Moonshot key serving Kimi (paid) | Yes (if Moonshot) | — |
| `MOONSHOT_MODEL` | Kimi model ID on Moonshot | No | `kimi-k2.6` |
| `MOONSHOT_BASE_URL` | OpenAI-compatible endpoint for Moonshot | No | `https://api.moonshot.ai/v1` |
| `GROQ_API_KEY` | Groq key (no Kimi model available) | Yes (if Groq) | — |
| `GROQ_MODEL` | Model ID on Groq | No | `openai/gpt-oss-120b` |
| `IMAGE_PROVIDER` | How diagrams are drawn: `mermaid` (free) or `gemini` | No | `mermaid` |
| `KROKI_URL` | Mermaid renderer (self-hostable) | No | `https://kroki.io` |
| `GOOGLE_API_KEY` | Google AI key for Gemini reasoning, and diagrams when `IMAGE_PROVIDER=gemini` | Only for Gemini | — |
| `GEMINI_MODEL` | Gemini model for blog agents | No | `gemini-2.5-flash` |
| `GEMINI_IMAGE_MODEL` | Gemini model for technical illustrations | No | `gemini-2.5-flash-image` |
| `OPENAI_API_KEY` | OpenAI API access key | Yes (if OpenAI) | — |
| `OPENAI_MODEL` | Primary LLM model if using OpenAI | No | `gpt-4o-mini` |
| `LLM_TEMPERATURE` | Generation temperature for agents | No | `0` |
| `DATABASE_URL` | PostgreSQL connection URI for state checkpointing | **Yes** | `postgresql://user:pass@localhost:5432/blogpilot` |
| `TAVILY_API_KEY` | Tavily Search API key for research agent | No* | — (*Required for hybrid/open search) |
| `TAVILY_MAX_RESULTS` | Number of web search results per query | No | `6` |
| `RESEARCH_SNIPPET_CHARS` | Max characters kept per search snippet | No | `500` |
| `RESEARCH_MAX_RESULTS` | Max unique sources sent to the research model | No | `24` |
| `APP_HOST` | FastAPI server bind host | No | `127.0.0.1` |
| `APP_PORT` | FastAPI server bind port | No | `8000` |
| `APP_RELOAD` | Enable hot reloading in development | No | `true` |

---

## Quickstart Guide

### Option 1: Local Development

#### Windows (PowerShell)
```powershell
git clone <your-repo-url>
cd Blog-Writing-Refactored

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Copy-Item .env.example .env

cd src
uvicorn app:app --reload
```

#### macOS / Linux
```bash
git clone <your-repo-url>
cd Blog-Writing-Refactored

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

cd src
uvicorn app:app --reload
```

Once running, visit **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

### Option 2: Docker Container

```bash
docker build -t blogpilot-ai .
docker run --rm -it -p 8000:8000 --env-file .env blogpilot-ai
```

Then navigate to **[http://localhost:8000](http://localhost:8000)**.

---

### Option 3: Deploy to Render

This repository includes a native [`render.yaml`](render.yaml) blueprint:

1. Push your repository to GitHub.
2. Link your repository in the [Render Dashboard](https://dashboard.render.com).
3. Create a **New Blueprint Instance**.
4. Configure your secret environment variables under **Service settings -> Environment -> Add Environment Variable**:
   - `GROQ_API_KEY` - your free key from [console.groq.com](https://console.groq.com) (never commit it to the repo)
   - `DATABASE_URL` - PostgreSQL connection URI
   - `GOOGLE_API_KEY` - only needed with `IMAGE_PROVIDER=gemini`; the default diagram renderer is free and keyless
   - `TAVILY_API_KEY` - optional, enables web research

   `LLM_PROVIDER=groq`, `GROQ_MODEL`, `LLM_MAX_TOKENS`, `LLM_MAX_CONCURRENCY=2` and `IMAGE_PROVIDER=mermaid` are already set for you in [`render.yaml`](render.yaml).

   To switch to Kimi: add `MOONSHOT_API_KEY`, then set `LLM_PROVIDER=moonshot` and `LLM_MAX_CONCURRENCY=0` in the Render dashboard.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web application user interface |
| `GET` | `/api/health` | Health check endpoint returning system status |
| `POST` | `/api/run` | Triggers a blog generation run (streamed via SSE). Request body: `{"topic": "string"}` |
| `GET` | `/api/runs/{run_id}/download` | Downloads the compiled Markdown article for a completed run |
| `GET` | `/static/*` | Static assets (CSS styles, frontend JavaScript) |
| `GET` | `/images/*` | Generated technical diagrams and illustrations |

---

## Testing & Validation

The test suite validates architectural integrity, import cleanliness, syntax validity, and environment safety:

```bash
pytest tests/
```

Tests ensure:
- All required project modules, templates, and configurations are present.
- Every Python package contains appropriate `__init__.py` markers.
- No stale or monolithic imports remain.
- All Python modules compile successfully without syntax errors.
- `src/core/config.py` is enforced as the sole authority for accessing environment variables.

---

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for complete details.
