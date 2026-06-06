"""CLI entrypoint: `python -m bench <run|score> [options]`.

  run    Build a clean workspace per task+variant, let `codex exec` perform the
         task, then score every workspace and write a report.
  score  Re-score an existing run directory (no agent invoked) — deterministic,
         used for regression and for validating the scorer on fixtures.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from . import report
from .runner import run_task_variant
from .score import score_run

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH_ROOT = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(BENCH_ROOT)
TASKS_DIR = os.path.join(BENCH_ROOT, "tasks")
RUNS_DIR = os.path.join(BENCH_ROOT, "runs")


def load_tasks(only: list[str] | None) -> list[dict]:
    tasks = []
    for name in sorted(os.listdir(TASKS_DIR)):
        tdir = os.path.join(TASKS_DIR, name)
        meta = os.path.join(tdir, "task.json")
        if not os.path.isfile(meta):
            continue
        with open(meta, encoding="utf-8") as fh:
            task = json.load(fh)
        task.setdefault("id", name)
        prompt_path = os.path.join(tdir, "prompt.md")
        task["prompt"] = open(prompt_path, encoding="utf-8").read() if os.path.exists(prompt_path) else ""
        task.setdefault("variants", ["default"])
        if only and task["id"] not in only:
            continue
        tasks.append(task)
    return tasks


def resolve_py(py: str | None) -> str:
    """Make the scoring interpreter an absolute path (subprocesses run with
    cwd set to the workspace, so a relative `.venv/bin/python` would break)."""
    if not py:
        return sys.executable
    if os.sep in py or os.path.exists(py):
        return os.path.abspath(py)
    return py


def write_outputs(records, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    md = report.to_markdown(records)
    js = report.to_json(records)
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    with open(os.path.join(out_dir, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(js, fh, indent=2)
    print(md)
    print(f"\nWrote {os.path.join(out_dir, 'report.md')} and result.json")


def cmd_run(args):
    py = resolve_py(args.py)
    tasks = load_tasks(args.tasks.split(",") if args.tasks else None)
    if not tasks:
        print("No tasks found.", file=sys.stderr)
        return 1
    run_dir = args.run_dir or os.path.join(RUNS_DIR, time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(run_dir, exist_ok=True)
    records = []
    for task in tasks:
        for variant in task["variants"]:
            print(f">>> {task['id']} [{variant}] ...", file=sys.stderr)
            run = run_task_variant(REPO_ROOT, task, variant, run_dir, args.timeout)
            score = score_run(run["workspace"], task, variant, py=py)
            records.append({"task_id": task["id"], "variant": variant, "run": run, "score": score})
    write_outputs(records, run_dir)
    return 0


def cmd_score(args):
    """Re-score workspaces already present under a run directory."""
    py = resolve_py(args.py)
    tasks = {t["id"]: t for t in load_tasks(None)}
    run_dir = args.run_dir
    records = []
    for task_id in sorted(os.listdir(run_dir)):
        tdir = os.path.join(run_dir, task_id)
        if not os.path.isdir(tdir) or task_id not in tasks:
            continue
        for variant in sorted(os.listdir(tdir)):
            ws = os.path.join(tdir, variant, "workspace")
            if not os.path.isdir(ws):
                continue
            score = score_run(ws, tasks[task_id], variant, py=py)
            records.append({"task_id": task_id, "variant": variant,
                            "run": {"ran": True, "returncode": 0, "workspace": ws}, "score": score})
    if not records:
        print("No scorable workspaces found under run dir.", file=sys.stderr)
        return 1
    write_outputs(records, run_dir)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="bench", description="repo-harness workflow benchmark")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="run tasks via codex then score")
    pr.add_argument("--tasks", help="comma-separated task ids (default: all)")
    pr.add_argument("--run-dir", help="output dir (default: benchmark/runs/<ts>)")
    pr.add_argument("--timeout", type=int, default=600, help="per-run timeout seconds")
    pr.add_argument("--py", help="python with pytest+coverage for scoring (default: current)")
    pr.set_defaults(func=cmd_run)

    ps = sub.add_parser("score", help="re-score an existing run dir (no agent)")
    ps.add_argument("run_dir", help="a benchmark/runs/<ts> directory")
    ps.add_argument("--py", help="python with pytest+coverage for scoring")
    ps.set_defaults(func=cmd_score)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
