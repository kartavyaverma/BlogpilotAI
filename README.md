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
- **Reducer Subgraph & Visuals**: An editorial reducer agent stitches content seamlessly, audits the post for visual diagram opportunities, and generates technical visuals using **Google Gemini**.
- **Kimi by Default**: Reasoning, planning and writing run on **Kimi (Moonshot)** with a 262K context window and excellent tool-use behaviour; Groq, Gemini and OpenAI remain drop-in alternatives.
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
        Decide --> Generate[Generate & Place Visuals\nGoogle Gemini]
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
  - `MOONSHOT_API_KEY`: **Recommended.** Runs **Kimi** straight from Moonshot - 262K context and excellent agent/tool use, which is what this graph relies on. Get one at [platform.moonshot.ai](https://platform.moonshot.ai) -> *API Keys*. **Paid: there is no free tier, the account needs a balance**
  - `GROQ_API_KEY`: Free fallback and the fastest option, but **Groq serves no Kimi model** - it runs `openai/gpt-oss-120b` here instead. [console.groq.com](https://console.groq.com) -> *API Keys*
  - `GOOGLE_API_KEY`: Required if using Gemini (`LLM_PROVIDER=gemini`), **and for visual diagram generation with any provider**. Without it, articles are still generated and diagrams are skipped
  - `OPENAI_API_KEY`: Required if using OpenAI (`LLM_PROVIDER=openai`)
  - `TAVILY_API_KEY`: Required for online research and fact-finding (open/hybrid mode)

### Choosing a model provider

| Provider | `LLM_PROVIDER` | Default model | Context | Cost |
|---|---|---|---|---|
| **Moonshot** (recommended, Kimi) | `moonshot` | `kimi-k2.6` | 262K | Paid only - $0.95 / M input, $4.00 / M output |
| Groq (fastest, free - no Kimi) | `groq` | `openai/gpt-oss-120b` | 128K | Free tier (per-minute / per-day limits) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | 1M | Free tier / paid |
| OpenAI | `openai` | `gpt-4o-mini` | 128K | Paid |

If `LLM_PROVIDER` is not set, the provider is picked from whichever key is present, preferring `MOONSHOT_API_KEY`, then `GROQ_API_KEY`.

### What each run costs

Only the **LLM provider** and **Tavily** meter usage; the app, PostgreSQL and Gemini image generation have free tiers.

| Component | When it bills | Rough cost |
|---|---|---|
| Kimi (`moonshot`) | Every agent call: router, research extraction, planner, one call per section, reducer | ~$0.06 per article (measured) |
| Groq | Free tier, rate limited per minute / per day | $0 |
| Gemini diagrams | Once per planned figure (needs `GOOGLE_API_KEY`) | Free tier, then per image |
| Tavily research | Only on `hybrid` / `open_book` topics, ~5 searches per run | Free tier: 1,000 searches / month |
| PostgreSQL | Checkpointer storage | Free tier on Neon / Supabase / Render |

A measured run - a 2,553-word article on "How vector databases actually retrieve information" - consumed **8,940 input and 11,591 output tokens** across ~10 agent calls, which is **$0.055** at Kimi's `kimi-k2.6` rates. Research-heavy (`open_book`) topics push input tokens higher, since Tavily results are fed into the prompt.

Output tokens dominate the bill at 4x the input rate, so `LLM_MAX_TOKENS` is the most effective cost lever. Kimi also charges only $0.16 / M for cached input, so repeated runs on similar topics cost less.

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
| `MOONSHOT_API_KEY` | Moonshot key serving Kimi (paid) | Yes (if Moonshot) | — |
| `MOONSHOT_MODEL` | Kimi model ID on Moonshot | No | `kimi-k2.6` |
| `MOONSHOT_BASE_URL` | OpenAI-compatible endpoint for Moonshot | No | `https://api.moonshot.ai/v1` |
| `GROQ_API_KEY` | Groq key (no Kimi model available) | Yes (if Groq) | — |
| `GROQ_MODEL` | Model ID on Groq | No | `openai/gpt-oss-120b` |
| `GOOGLE_API_KEY` | Google AI key for Gemini reasoning & visual diagrams | Yes (if Gemini); optional otherwise | — |
| `GEMINI_MODEL` | Gemini model for blog agents | No | `gemini-2.5-flash` |
| `GEMINI_IMAGE_MODEL` | Gemini model for technical illustrations | No | `gemini-2.5-flash-image` |
| `OPENAI_API_KEY` | OpenAI API access key | Yes (if OpenAI) | — |
| `OPENAI_MODEL` | Primary LLM model if using OpenAI | No | `gpt-4o-mini` |
| `LLM_TEMPERATURE` | Generation temperature for agents | No | `0` |
| `DATABASE_URL` | PostgreSQL connection URI for state checkpointing | **Yes** | `postgresql://user:pass@localhost:5432/blogpilot` |
| `TAVILY_API_KEY` | Tavily Search API key for research agent | No* | — (*Required for hybrid/open search) |
| `TAVILY_MAX_RESULTS` | Number of web search results per query | No | `6` |
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
   - `MOONSHOT_API_KEY` - your Kimi key from [platform.moonshot.ai](https://platform.moonshot.ai) (never commit it to the repo)
   - `DATABASE_URL` - PostgreSQL connection URI
   - `GOOGLE_API_KEY` - optional, enables generated diagrams
   - `TAVILY_API_KEY` - optional, enables web research

   `LLM_PROVIDER=moonshot`, `MOONSHOT_MODEL` and `LLM_MAX_TOKENS` are already set for you in [`render.yaml`](render.yaml).

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
