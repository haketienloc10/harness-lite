"""Deterministic scorer.

Given a finished run workspace (a copy of the repo where an agent worked,
containing `harness.db` plus any files it produced) and the task's expected
rubric, compute a per-dimension scorecard. No LLM involved: scoring the same
workspace twice yields identical numbers.

Dimensions (only those the task marks as expected are counted):
  - classification : intake input_type + risk_lane match expectation
  - artifacts      : story / decision records exist as expected
  - trace_quality  : trace tier (TRACE_SPEC) reaches the lane minimum
  - friction       : harness_friction captured when the task has friction
  - governance     : high-risk work has a durable decision + ADR file
  - skill_tdd      : code task followed tdd-workflow (tests pass, coverage,
                     interface present, proof recorded, trace notes the skill)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass, field
from typing import Any, Optional

from . import trace_tier

# Default weight per dimension. A task only spends weight on dimensions it
# declares in `expect`; the task score is the weighted average over the
# applicable ones, so absent dimensions never penalise a task.
DEFAULT_WEIGHTS = {
    "classification": 1.0,
    "artifacts": 1.0,
    "trace_quality": 1.0,
    "friction": 1.0,
    "governance": 1.0,
    "skill_tdd": 2.0,
}

LANE_ALIASES = {
    "high-risk": "high_risk",
    "highrisk": "high_risk",
    "high_risk": "high_risk",
    "normal": "normal",
    "tiny": "tiny",
}


def norm_lane(lane: Optional[str]) -> str:
    return LANE_ALIASES.get((lane or "").strip().lower(), (lane or "").strip().lower())


@dataclass
class DimScore:
    name: str
    score: float  # 0..1
    weight: float
    detail: str = ""
    applicable: bool = True


@dataclass
class TaskScore:
    task_id: str
    variant: str
    dims: list[DimScore] = field(default_factory=list)
    lane_correct: Optional[bool] = None
    trace_tier: Optional[int] = None
    notes: list[str] = field(default_factory=list)

    @property
    def applicable(self) -> list[DimScore]:
        return [d for d in self.dims if d.applicable]

    @property
    def compliance(self) -> float:
        dims = self.applicable
        wsum = sum(d.weight for d in dims)
        if wsum == 0:
            return 0.0
        return 100.0 * sum(d.score * d.weight for d in dims) / wsum

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "variant": self.variant,
            "compliance": round(self.compliance, 1),
            "lane_correct": self.lane_correct,
            "trace_tier": self.trace_tier,
            "dimensions": [
                {
                    "name": d.name,
                    "score": round(d.score, 3),
                    "weight": d.weight,
                    "applicable": d.applicable,
                    "detail": d.detail,
                }
                for d in self.dims
            ],
            "notes": self.notes,
        }


# --------------------------------------------------------------------------
# DB access
# --------------------------------------------------------------------------
def _rows(db_path: str, query: str) -> list[dict[str, Any]]:
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute(query)
        except sqlite3.Error:
            return []
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


# --------------------------------------------------------------------------
# Coverage measurement (real, mechanical)
# --------------------------------------------------------------------------
def measure_coverage(
    workspace: str, src_dir: str, tests_dir: str, py: str
) -> dict[str, Any]:
    """Run the candidate's tests under coverage. Returns:
    {tests_pass: bool, coverage: float|None, error: str|None}.

    `py` is a python interpreter that has pytest + coverage installed
    (the benchmark venv). Falls back gracefully when paths are missing.
    """
    workspace = os.path.abspath(workspace)
    src = os.path.join(workspace, src_dir)
    tests = os.path.join(workspace, tests_dir)
    if not os.path.isdir(tests):
        return {"tests_pass": False, "coverage": None, "error": f"no tests dir: {tests_dir}"}
    cov_file = os.path.join(workspace, ".bench_coverage.json")
    env = dict(os.environ)
    # Make `src/` importable both as `import x` and `from src import x`.
    env["PYTHONPATH"] = os.pathsep.join(
        [src, workspace, env.get("PYTHONPATH", "")]
    )
    cov_target = src if os.path.isdir(src) else workspace
    run = subprocess.run(
        [py, "-m", "coverage", "run", "--branch", f"--source={cov_target}",
         "-m", "pytest", tests, "-q"],
        cwd=workspace,
        env=env,
        capture_output=True,
        text=True,
    )
    tests_pass = run.returncode == 0
    coverage = None
    err = None if tests_pass else (run.stdout + run.stderr)[-800:]
    jr = subprocess.run(
        [py, "-m", "coverage", "json", "-o", cov_file],
        cwd=workspace,
        env=env,
        capture_output=True,
        text=True,
    )
    if jr.returncode == 0 and os.path.exists(cov_file):
        try:
            with open(cov_file) as fh:
                data = json.load(fh)
            coverage = float(data["totals"]["percent_covered"])
        except (ValueError, KeyError, OSError):
            coverage = None
    return {"tests_pass": tests_pass, "coverage": coverage, "error": err}


# --------------------------------------------------------------------------
# Dimension scorers
# --------------------------------------------------------------------------
def _score_classification(db: str, task: dict, w: float) -> DimScore:
    intakes = _rows(db, "SELECT input_type, risk_lane, risk_flags FROM intake ORDER BY id")
    if not intakes:
        return DimScore("classification", 0.0, w, "no intake recorded")
    row = intakes[-1]
    exp_type = task.get("type")
    exp_types = exp_type if isinstance(exp_type, list) else ([exp_type] if exp_type else [])
    exp_lane = norm_lane(task.get("lane"))
    got_type = (row.get("input_type") or "").strip().lower()
    got_lane = norm_lane(row.get("risk_lane"))
    parts: list[float] = []
    detail: list[str] = []
    if exp_types:
        ok = got_type in [t.strip().lower() for t in exp_types]
        parts.append(1.0 if ok else 0.0)
        detail.append(f"type={got_type}{'' if ok else f' (want {exp_types})'}")
    if exp_lane:
        ok = got_lane == exp_lane
        parts.append(1.0 if ok else 0.0)
        detail.append(f"lane={got_lane}{'' if ok else f' (want {exp_lane})'}")
    score = sum(parts) / len(parts) if parts else 1.0
    return DimScore("classification", score, w, "; ".join(detail))


def _score_artifacts(db: str, ws: str, task: dict, w: float) -> DimScore:
    expect = task.get("expect", {})
    checks: list[tuple[str, bool]] = []
    if expect.get("story"):
        stories = _rows(db, "SELECT id, status, unit_proof, integration_proof, e2e_proof, evidence FROM story")
        has = len(stories) > 0
        checks.append(("story_row", has))
        if expect.get("story_implemented"):
            impl = any(
                (s.get("status") in ("implemented", "changed"))
                and ((s.get("unit_proof") or 0) + (s.get("integration_proof") or 0) + (s.get("e2e_proof") or 0) >= 1)
                for s in stories
            )
            checks.append(("story_implemented+proof", impl))
    if not checks:
        return DimScore("artifacts", 1.0, w, "no artifact expectation", applicable=False)
    score = sum(1.0 for _, ok in checks if ok) / len(checks)
    detail = ", ".join(f"{n}={'ok' if ok else 'MISS'}" for n, ok in checks)
    return DimScore("artifacts", score, w, detail)


def _score_trace(db: str, task: dict, w: float, ts: TaskScore) -> DimScore:
    traces = _rows(
        db,
        "SELECT task_summary, intake_id, story_id, agent, actions_taken, files_read, "
        "files_changed, decisions_made, errors, outcome, duration_seconds, "
        "token_estimate, harness_friction, notes FROM trace ORDER BY id",
    )
    if not traces:
        ts.trace_tier = 0
        return DimScore("trace_quality", 0.0, w, "no trace recorded")
    # Best trace counts (an agent may write several).
    scored = [trace_tier.score_trace(t) for t in traces]
    best = max(scored, key=lambda s: s["tier"])
    ts.trace_tier = best["tier"]
    exp_lane = norm_lane(task.get("lane"))
    want = task.get("expect", {}).get("trace_min_tier") or trace_tier.expected_tier_for_lane(exp_lane)
    score = min(1.0, best["tier"] / want) if want else 1.0
    miss = best["missing"]
    detail = f"tier={best['tier']}/{want}"
    if best["tier"] < want:
        gap = miss["detailed"] if want >= 3 else miss["standard"]
        if gap:
            detail += f" missing={gap}"
    return DimScore("trace_quality", score, w, detail)


def _score_friction(db: str, task: dict, w: float) -> DimScore:
    if not task.get("expect", {}).get("friction"):
        return DimScore("friction", 1.0, w, "no friction expected", applicable=False)
    traces = _rows(db, "SELECT harness_friction FROM trace")
    backlog = _rows(db, "SELECT id FROM backlog")
    captured = any(
        (t.get("harness_friction") or "").strip().lower() not in ("", "none")
        for t in traces
    )
    score = 1.0 if captured else 0.0
    detail = f"friction_captured={captured}, backlog_items={len(backlog)}"
    if captured and backlog:
        detail += " (+backlog)"
    return DimScore("friction", score, w, detail)


def _score_governance(db: str, ws: str, task: dict, w: float) -> DimScore:
    if not task.get("expect", {}).get("decision_record"):
        return DimScore("governance", 1.0, w, "no decision expected", applicable=False)
    rows = _rows(db, "SELECT id, doc_path FROM decision")
    has_row = len(rows) > 0
    # An ADR markdown file under docs/decisions/ that is NOT one of the
    # repo's seed decisions (0001-0006 ship with the repo).
    adr_dir = os.path.join(ws, "docs", "decisions")
    new_adr = False
    if os.path.isdir(adr_dir):
        for fn in os.listdir(adr_dir):
            m = re.match(r"^(\d{4})", fn)
            if m and int(m.group(1)) >= 7 and fn.endswith(".md"):
                new_adr = True
    score = (0.5 if has_row else 0.0) + (0.5 if new_adr else 0.0)
    return DimScore(
        "governance", score, w,
        f"decision_row={has_row}, new_adr_file={new_adr}",
    )


def _score_skill_tdd(db: str, ws: str, task: dict, w: float, py: str) -> DimScore:
    if not task.get("expect", {}).get("skill_tdd"):
        return DimScore("skill_tdd", 1.0, w, "not a TDD task", applicable=False)
    code = task.get("code", {})
    src_dir = code.get("src_dir", "src")
    tests_dir = code.get("tests_dir", "tests")
    min_cov = float(code.get("min_coverage", 80))
    sub: list[tuple[str, float, float]] = []  # (name, score, weight)

    # Weights emphasise verifiable *outcomes* (tests pass + real branch
    # coverage) over the weak "did the agent name the skill" proxy. Coverage is
    # measured with branch tracking, so untested edge-case branches lower it.
    cov = measure_coverage(ws, src_dir, tests_dir, py)
    sub.append(("tests_pass", 1.0 if cov["tests_pass"] else 0.0, 0.25))
    if cov["coverage"] is None:
        cov_score = 0.0
        cov_detail = "coverage=n/a"
    else:
        cov_score = min(1.0, cov["coverage"] / min_cov)
        cov_detail = f"coverage={cov['coverage']:.0f}%/{min_cov:.0f}% (branch)"
    sub.append(("coverage", cov_score, 0.50))

    # Interface present: the required symbol exists in src.
    symbol = code.get("symbol")
    iface_ok = True
    if symbol:
        iface_ok = False
        src_path = os.path.join(ws, src_dir)
        for root, _d, files in os.walk(src_path):
            for fn in files:
                if fn.endswith(".py"):
                    try:
                        with open(os.path.join(root, fn)) as fh:
                            if re.search(rf"\b(def|class)\s+{re.escape(symbol)}\b", fh.read()):
                                iface_ok = True
                    except OSError:
                        pass
    sub.append(("interface", 1.0 if iface_ok else 0.0, 0.10))

    # Proof recorded on the story.
    stories = _rows(db, "SELECT unit_proof, evidence FROM story")
    proof_ok = any((s.get("unit_proof") or 0) >= 1 and (s.get("evidence") or "").strip() for s in stories)
    sub.append(("story_proof", 1.0 if proof_ok else 0.0, 0.10))

    # Trace names the skill.
    traces = _rows(db, "SELECT notes, actions_taken FROM trace")
    skill_named = any(
        "tdd-workflow" in ((t.get("notes") or "") + (t.get("actions_taken") or "")).lower()
        for t in traces
    )
    sub.append(("skill_noted", 1.0 if skill_named else 0.0, 0.05))

    total = sum(s * wt for _n, s, wt in sub)
    detail = cov_detail + "; " + ", ".join(
        f"{n}={'ok' if s >= 1 else ('%.2f' % s)}" for n, s, wt in sub if n != "coverage"
    )
    ds = DimScore("skill_tdd", total, w, detail)
    ds.extra = {"coverage": cov["coverage"], "tests_pass": cov["tests_pass"]}  # type: ignore[attr-defined]
    return ds


# --------------------------------------------------------------------------
# Top-level
# --------------------------------------------------------------------------
def score_run(workspace: str, task: dict, variant: str = "default", py: str = "python3") -> TaskScore:
    db = os.path.join(workspace, "harness.db")
    weights = {**DEFAULT_WEIGHTS, **task.get("weights", {})}
    ts = TaskScore(task_id=task["id"], variant=variant)

    ts.dims.append(_score_classification(db, task, weights["classification"]))
    ts.dims.append(_score_artifacts(db, workspace, task, weights["artifacts"]))
    ts.dims.append(_score_trace(db, task, weights["trace_quality"], ts))
    ts.dims.append(_score_friction(db, task, weights["friction"]))
    ts.dims.append(_score_governance(db, workspace, task, weights["governance"]))
    ts.dims.append(_score_skill_tdd(db, workspace, task, weights["skill_tdd"], py))

    # Lane accuracy (separate headline metric).
    intakes = _rows(db, "SELECT risk_lane FROM intake ORDER BY id")
    if intakes and task.get("lane"):
        ts.lane_correct = norm_lane(intakes[-1].get("risk_lane")) == norm_lane(task["lane"])

    if not os.path.exists(db):
        ts.notes.append("harness.db not found — agent never initialised the durable layer")
    return ts
