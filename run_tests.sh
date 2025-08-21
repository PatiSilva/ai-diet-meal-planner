#!/usr/bin/env bash
set -euo pipefail

# Go into the task folder
cd "$(dirname "$0")/task"

# Use the venv’s python explicitly
PY="./.venv/bin/python"

if [ ! -x "$PY" ]; then
  echo "❌ No venv found at $PY"
  echo "Run: python3.12 -m venv .venv && source .venv/bin/activate"
  exit 1
fi

# Make sure deps for Hyperskill are there
$PY -m pip install --quiet --no-cache-dir -r ../requirements-hyperskill.txt

# Run the official Hyperskill tests
echo "▶ Running Hyperskill tests..."
$PY test/tests.py

