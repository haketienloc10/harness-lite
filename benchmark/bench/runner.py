"""Live-agent runner.

For each task+variant: build a clean workspace (a copy of the Harness),
optionally strip the `tdd-workflow` skill (the A/B "noskill" arm), initialise
the durable layer, then let `codex exec` perform the task. The resulting
workspace (with `harness.db` + produced files) is what score.py grades.

The runner shells out to the Codex CLI. It does not need an API key when the
user has logged in with `codex login`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from typing import Any, Optional

# Harness files copied into each fresh workspace. `scripts/` is required
# because `harness-cli init` reads scripts/schema/*.sql relative to cwd.
HARNESS_COPY = ["_harness", "scripts", "docs", "AGENTS.md", "README.md"]

PROMPT_PREAMBLE = (
    "You are working inside a repository that uses the Harness operating "
    "framework. Before doing anything, read `AGENTS.md` and follow it "
    "(`_harness/00-AGENTS.md` and the workflow it points to). Use the durable "
    "CLI at `./scripts/bin/harness-cli` to record intake, story, decision, and "
    "trace data as the workflow requires. Work only inside this directory. "
    "When finished, make sure the durable layer reflects what you did.\n\n"
    "=== TASK ===\n"
)


def strip_tdd_skill(workspace: str) -> None:
    """Remove every trace of the tdd-workflow skill (A/B 'noskill' arm)."""
    skill_file = os.path.join(workspace, "_harness", "skills", "tdd-workflow.md")
    if os.path.exists(skill_file):
        os.remove(skill_file)

    # Registry row in 04-SKILLS.md.
    reg = os.path.join(workspace, "_harness", "04-SKILLS.md")
    _drop_lines(reg, lambda ln: "tdd-workflow.md" in ln)

    # GĐ3 skill pointer bullet in 01-WORKFLOW.md (a 3-physical-line bullet).
    wf = os.path.join(workspace, "_harness", "01-WORKFLOW.md")
    _drop_skill_bullet(wf)


def _drop_lines(path: str, pred) -> None:
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    with open(path, "w", encoding="utf-8") as fh:
        fh.writelines(ln for ln in lines if not pred(ln))


def _drop_skill_bullet(path: str) -> None:
    """Remove the `- **Skill:** ... tdd-workflow ...` bullet (multi-line)."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("- **Skill:**"):
            # Skip this bullet and its continuation lines (indented, not a new
            # bullet / heading), until the next top-level bullet or blank gap.
            i += 1
            while i < len(lines):
                nxt = lines[i]
                stripped = nxt.lstrip()
                if stripped.startswith("- ") or stripped.startswith("#") or nxt.strip() == "":
                    break
                i += 1
            continue
        out.append(ln)
        i += 1
    with open(path, "w", encoding="utf-8") as fh:
        fh.writelines(out)


def build_workspace(repo_root: str, dest: str, variant: str) -> None:
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for name in HARNESS_COPY:
        src = os.path.join(repo_root, name)
        if not os.path.exists(src):
            continue
        target = os.path.join(dest, name)
        if os.path.isdir(src):
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)
    os.makedirs(os.path.join(dest, ".bench"), exist_ok=True)
    if variant == "noskill":
        strip_tdd_skill(dest)


def init_durable_layer(workspace: str) -> tuple[bool, str]:
    cli = os.path.join(workspace, "scripts", "bin", "harness-cli")
    if not os.path.exists(cli):
        return False, "harness-cli binary missing in workspace"
    logs = []
    for args in (["init"], ["migrate"]):
        r = subprocess.run([cli, *args], cwd=workspace, capture_output=True, text=True)
        logs.append(f"$ harness-cli {' '.join(args)}\n{r.stdout}{r.stderr}")
        if r.returncode != 0 and args == ["init"]:
            return False, "\n".join(logs)
    return True, "\n".join(logs)


def codex_available() -> Optional[str]:
    return shutil.which("codex")


def run_codex(workspace: str, prompt: str, timeout: int) -> dict[str, Any]:
    codex = codex_available()
    if not codex:
        return {"ran": False, "error": "codex CLI not found in PATH", "returncode": None}

    sandbox = os.environ.get("BENCH_CODEX_SANDBOX", "workspace-write")
    model = os.environ.get("BENCH_CODEX_MODEL")
    extra = os.environ.get("BENCH_CODEX_ARGS", "").split()
    last_msg = os.path.join(workspace, ".bench", "last_message.txt")
    cmd = [codex, "exec", "--cd", workspace, "-s", sandbox, "--skip-git-repo-check",
           "--json", "-o", last_msg]
    if model:
        cmd += ["-m", model]
    cmd += extra + [prompt]

    start = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ran": True, "error": f"timeout after {timeout}s", "returncode": None,
                "duration": timeout}
    dur = round(time.time() - start, 1)
    with open(os.path.join(workspace, ".bench", "events.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(r.stdout)
    with open(os.path.join(workspace, ".bench", "stderr.txt"), "w", encoding="utf-8") as fh:
        fh.write(r.stderr)
    return {
        "ran": True,
        "returncode": r.returncode,
        "duration": dur,
        "error": None if r.returncode == 0 else (r.stderr[-600:] or "non-zero exit"),
    }


def run_task_variant(
    repo_root: str, task: dict, variant: str, run_dir: str, timeout: int, rep: int = 1
) -> dict[str, Any]:
    workspace = os.path.join(run_dir, task["id"], variant, f"r{rep}", "workspace")
    build_workspace(repo_root, workspace, variant)
    ok, init_log = init_durable_layer(workspace)
    with open(os.path.join(workspace, ".bench", "init.log"), "w", encoding="utf-8") as fh:
        fh.write(init_log)
    if not ok:
        return {"workspace": workspace, "ran": False, "error": "durable init failed"}

    prompt = PROMPT_PREAMBLE + task["prompt"]
    result = run_codex(workspace, prompt, timeout)
    result["workspace"] = workspace
    return result
