#!/usr/bin/env bash
set -euo pipefail

SUBDIR="submission/task"

# 0) Start clean
rm -rf "$SUBDIR"
mkdir -p "$SUBDIR"

# 1) Copy what the checker needs (flatten)
cp main.py "$SUBDIR"/
cp app/agents/*.py "$SUBDIR"/
cp app/services/llm_client.py "$SUBDIR"/
cp app/models.py "$SUBDIR"/
# rename logging to avoid shadowing stdlib logging
cp app/logging.py "$SUBDIR"/app_logging.py

# 2) Rewrite imports across ALL copied files and tweak main.py
python3 - "$SUBDIR" <<'PY'
import sys, re, pathlib
root = pathlib.Path(sys.argv[1])

# Patterns to flatten imports (app.* -> flat) and rename logging -> app_logging
subs = [
    # Agents
    (r"\bfrom\s+app\.agents\.(\w+)\s+import\s+([\w\*,\s]+)", r"from \1 import \2"),
    (r"\bimport\s+app\.agents\.(\w+)\s+as\s+(\w+)", r"import \1 as \2"),

    # Services
    (r"\bfrom\s+app\.services\.llm_client\s+import\s+([\w\*,\s]+)", r"from llm_client import \1"),
    (r"\bimport\s+app\.services\.llm_client\b", r"import llm_client"),

    # Models
    (r"\bfrom\s+app\.models\s+import\s+([\w\*,\s]+)", r"from models import \1"),
    (r"\bimport\s+app\.models\b", r"import models"),

    # Logging -> app_logging (submission copy only)
    (r"\bfrom\s+app\.logging\s+import\s+([\w\*,\s]+)", r"from app_logging import \1"),
    (r"\bimport\s+app\.logging\s+as\s+(\w+)", r"import app_logging as \1"),
    (r"(^|\n)\s*import\s+app\.logging(\s|$)", r"\1import app_logging\2"),

    # Drop any leading-dot relative imports
    (r"\bfrom\s+\.(\w+)\s+import\s+([\w\*,\s]+)", r"from \1 import \2"),
]

# Apply to all *.py in submission
for py in root.glob("*.py"):
    s = py.read_text(encoding="utf-8")
    for pat, repl in subs:
        s = re.sub(pat, repl, s, flags=re.M)
    # Remove __main__ blocks from helpers to avoid multiple entrypoints
    if py.name != "main.py":
        s = re.sub(r"\nif\s+__name__\s*==\s*['\"]__main__['\"]:\s*.*\Z", "\n", s, flags=re.S)
    py.write_text(s, encoding="utf-8")

# Edit submission main.py: drop agent/llm imports and nonexistent MyModel import
mp = root / "main.py"
if mp.exists():
    text = mp.read_text(encoding="utf-8").splitlines()
    keep = []
    for ln in text:
        if ln.startswith("from diet_agent import "): continue
        if ln.startswith("from inventory_agent import "): continue
        if ln.startswith("from manager_agent import "): continue
        if ln.startswith("from planner_agent import "): continue
        if ln.startswith("from llm_client import "): continue
        if ln.strip() == "from models import MyModel": continue
        keep.append(ln)
    mp.write_text("\n".join(keep) + "\n", encoding="utf-8")
PY

echo "✔ Submission ready at $SUBDIR"

