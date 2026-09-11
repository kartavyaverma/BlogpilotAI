# Run BlogPilot AI locally in development mode (autoreload).
# Usage: .\scripts\run_dev.ps1   (run from the project root)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    py -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..."
pip install -q -r requirements.txt

if (-not (Test-Path ".env")) {
    Write-Host ".env not found - copying .env.example. Fill in your real keys before running again."
    Copy-Item ".env.example" ".env"
    exit 1
}

Write-Host "Starting BlogPilot AI on http://127.0.0.1:8000 ..."
Set-Location "src"
uvicorn app:app --reload
