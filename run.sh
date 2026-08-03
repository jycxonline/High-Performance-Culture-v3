#!/usr/bin/env bash
# High Performance Diagnostic Tool launcher (macOS/Linux)
set -e
cd "$(dirname "$0")"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi
echo "Starting High Performance Diagnostic Tool at http://localhost:8501"
streamlit run app.py
