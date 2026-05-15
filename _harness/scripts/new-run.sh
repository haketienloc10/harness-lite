#!/usr/bin/env bash
set -euo pipefail

HARNESS_DIR="_harness"
TEMPLATES_DIR="$HARNESS_DIR/templates"
RUNS_DIR="$HARNESS_DIR/runs"

TASK_SLUG="${1:-}"

if [ -z "$TASK_SLUG" ]; then
  echo "usage: $0 <task-slug>" >&2
  echo "example: $0 fix-power-charge-bug" >&2
  exit 1
fi

DATE="$(date +%Y-%m-%d)"
RUN_ID="${DATE}-${TASK_SLUG}"
RUN_DIR="$RUNS_DIR/$RUN_ID"

mkdir -p "$RUN_DIR"

cp "$TEMPLATES_DIR/00-input.template.md" \
  "$RUN_DIR/00-input.md"

cp "$TEMPLATES_DIR/01-planner-brief.template.md" \
  "$RUN_DIR/01-planner-brief.md"

echo "RUN_ID: $RUN_ID"
echo "created run: $RUN_DIR"
ls "$RUN_DIR"