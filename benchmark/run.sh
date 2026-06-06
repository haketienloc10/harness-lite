#!/usr/bin/env bash
# One-command benchmark: set up an isolated venv (pytest + coverage), run every
# task through the Codex agent, score the results, and print + write a report.
#
# Prereqs: `codex` CLI installed and logged in (`codex login`). Python 3.10+.
#
# Examples:
#   ./run.sh                      # run all tasks
#   ./run.sh --tasks T2-feature-tdd
#   ./run.sh --timeout 900
set -euo pipefail
cd "$(dirname "$0")"

VENV=".venv"
if [ ! -x "$VENV/bin/python" ]; then
  echo "[run.sh] creating venv at $VENV ..." >&2
  python3 -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install -q --disable-pip-version-check --upgrade pip >/dev/null
"$VENV/bin/python" -m pip install -q --disable-pip-version-check pytest coverage >/dev/null

if ! command -v codex >/dev/null 2>&1; then
  echo "[run.sh] WARNING: 'codex' CLI not found in PATH. Tasks will be marked" >&2
  echo "         DID NOT RUN. Install + 'codex login', then re-run." >&2
fi

exec "$VENV/bin/python" -m bench run --py "$VENV/bin/python" "$@"
