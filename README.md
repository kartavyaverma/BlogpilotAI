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
  - `OPENAI_API_KEY`: Required for LLM reasoning and writing
  - `TAVILY_API_KEY`: Required for online research and fact-finding
  - `GOOGLE_API_KEY`: Optional, used by Gemini for automated technical diagrams/illustrations

---

## Environment Configuration

Create a `.env` file in the project root by copying `.env.example`:

```bash
cp .env.example .env
```

Configure the following variables in `.env`:

| Variable | Description | Required | Default |
|---|---|:---:|---|
| `OPENAI_API_KEY` | OpenAI API access key | **Yes** | — |
| `OPENAI_MODEL` | Primary LLM model for agents | No | `gpt-4o-mini` |
| `LLM_TEMPERATURE` | Generation temperature for agents | No | `0` |
| `DATABASE_URL` | PostgreSQL connection URI for state checkpointing | **Yes** | `postgresql://user:pass@localhost:5432/blogpilot` |
| `TAVILY_API_KEY` | Tavily Search API key for research agent | No* | — (*Required for hybrid/open search) |
| `TAVILY_MAX_RESULTS` | Number of web search results per query | No | `6` |
| `GOOGLE_API_KEY` | Google AI key for Gemini image generation | No | — |
| `GEMINI_IMAGE_MODEL` | Model used for technical illustrations | No | `gemini-2.5-flash-image` |
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
4. Configure your secret environment variables (`OPENAI_API_KEY`, `TAVILY_API_KEY`, `DATABASE_URL`, and optionally `GOOGLE_API_KEY`) under the service settings.

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
