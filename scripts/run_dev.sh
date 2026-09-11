#!/usr/bin/env bash
# Run BlogPilot AI locally in development mode (autoreload).
# Usage: ./scripts/run_dev.sh   (run from the project root)
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  echo ".env not found — copying .env.example. Fill in your real keys before running again."
  cp .env.example .env
  exit 1
fi

echo "Starting BlogPilot AI on http://127.0.0.1:8000 ..."
cd src
uvicorn app:app --reload
