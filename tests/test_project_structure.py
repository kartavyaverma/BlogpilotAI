"""
tests/test_project_structure.py

Basic structural checks: the expected files/packages exist, key modules
import cleanly, and there is a single source of truth for each concern
(no stale imports back to the old monolithic app.py/backend.py).

These are intentionally lightweight "does the refactor hold together"
checks, not full behavioral tests (those would need a live Postgres
instance and real API keys).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"


def test_top_level_layout_exists():
    expected = [
        "src/app.py",
        "src/core/config.py",
        "src/core/llm.py",
        "src/schemas/models.py",
        "src/agents/router.py",
        "src/agents/research.py",
        "src/agents/orchestrator.py",
        "src/agents/worker.py",
        "src/agents/reducer.py",
        "src/graph/builder.py",
        "src/graph/streaming.py",
        "src/api/routes/pages.py",
        "src/api/routes/health.py",
        "src/api/routes/runs.py",
        "src/templates/index.html",
        "src/static/css/style.css",
        "src/static/js/app.js",
        "requirements.txt",
        "Dockerfile",
        ".dockerignore",
        ".env.example",
        "render.yaml",
    ]

    missing = [path for path in expected if not (PROJECT_ROOT / path).is_file()]
    assert not missing, f"Missing expected files: {missing}"


def test_packages_have_init_files():
    packages = ["core", "schemas", "agents", "graph", "api", "api/routes"]
    missing = [
        pkg for pkg in packages if not (SRC_DIR / pkg / "__init__.py").is_file()
    ]
    assert not missing, f"Missing __init__.py in: {missing}"


def test_no_stale_imports_to_old_monolith():
    """The old backend.py / top-level app.py no longer exist as import targets."""
    offenders = []
    for py_file in SRC_DIR.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        if "from backend import" in text or "import backend" in text:
            offenders.append(str(py_file))

    assert not offenders, f"Stale 'backend' imports found in: {offenders}"


def test_source_files_compile():
    """Every .py file under src/ is syntactically valid (py_compile), without
    requiring API keys or a live database connection to actually import it."""
    py_files = list(SRC_DIR.rglob("*.py"))
    assert py_files, "No Python files found under src/"

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", *[str(p) for p in py_files]],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"py_compile failed:\n{result.stderr}"


def test_config_is_single_source_of_env_vars():
    """No module other than core/config.py should call os.getenv directly."""
    offenders = []
    for py_file in SRC_DIR.rglob("*.py"):
        if py_file == SRC_DIR / "core" / "config.py":
            continue
        text = py_file.read_text(encoding="utf-8")
        if "os.getenv(" in text or "os.environ.get(" in text:
            offenders.append(str(py_file.relative_to(PROJECT_ROOT)))

    assert not offenders, (
        "Only core/config.py should read environment variables directly, "
        f"but found direct env access in: {offenders}"
    )
