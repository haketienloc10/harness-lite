"""Aggregate scorecards into a human report (markdown) + machine result (json).

Headline metrics mirror the names the repo already uses in
docs/HARNESS_MATURITY.md: Harness compliance %, Lane accuracy, Trace quality
/3, Friction captured. Plus the A/B "skill delta" for tdd-workflow.
"""

from __future__ import annotations

import json
from typing import Any

from .score import TaskScore


def _primary_variant(variants: list[str]) -> str:
    if "withskill" in variants:
        return "withskill"
    if "default" in variants:
        return "default"
    return variants[0]


def aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    """records: [{task_id, variant, score: TaskScore, run: dict}]."""
    by_task: dict[str, dict[str, dict[str, Any]]] = {}
    for r in records:
        by_task.setdefault(r["task_id"], {})[r["variant"]] = r

    primaries: list[dict[str, Any]] = []
    for task_id, variants in by_task.items():
        prim = _primary_variant(list(variants.keys()))
        primaries.append(variants[prim])

    compliances = [r["score"].compliance for r in primaries]
    lane_judged = [r["score"] for r in primaries if r["score"].lane_correct is not None]
    lane_correct = sum(1 for s in lane_judged if s.lane_correct)
    tiers = [r["score"].trace_tier for r in primaries if r["score"].trace_tier is not None]

    friction_tasks = [r for r in primaries if _dim(r["score"], "friction").applicable]
    friction_ok = sum(1 for r in friction_tasks if _dim(r["score"], "friction").score >= 1.0)

    # Skill A/B deltas.
    deltas = []
    for task_id, variants in by_task.items():
        if "withskill" in variants and "noskill" in variants:
            a = variants["withskill"]["score"]
            b = variants["noskill"]["score"]
            deltas.append({
                "task_id": task_id,
                "compliance_with": round(a.compliance, 1),
                "compliance_without": round(b.compliance, 1),
                "compliance_delta": round(a.compliance - b.compliance, 1),
                "skill_tdd_with": round(_dim(a, "skill_tdd").score, 3),
                "skill_tdd_without": round(_dim(b, "skill_tdd").score, 3),
                "skill_tdd_delta": round(_dim(a, "skill_tdd").score - _dim(b, "skill_tdd").score, 3),
                "coverage_with": _coverage(a),
                "coverage_without": _coverage(b),
            })

    return {
        "overall_compliance": round(sum(compliances) / len(compliances), 1) if compliances else 0.0,
        "lane_accuracy": f"{lane_correct}/{len(lane_judged)}" if lane_judged else "n/a",
        "mean_trace_tier": round(sum(tiers) / len(tiers), 2) if tiers else 0.0,
        "friction_captured": f"{friction_ok}/{len(friction_tasks)}" if friction_tasks else "n/a",
        "skill_deltas": deltas,
        "n_tasks": len(by_task),
        "n_runs": len(records),
    }


def _dim(score: TaskScore, name: str):
    for d in score.dims:
        if d.name == name:
            return d
    # Should not happen; return a non-applicable stub.
    from .score import DimScore
    return DimScore(name, 0.0, 0.0, "missing", applicable=False)


def _coverage(score: TaskScore):
    d = _dim(score, "skill_tdd")
    extra = getattr(d, "extra", None)
    if extra and extra.get("coverage") is not None:
        return round(extra["coverage"], 1)
    return None


def to_json(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "summary": aggregate(records),
        "runs": [
            {**r["score"].to_dict(), "run": {k: v for k, v in r["run"].items() if k != "workspace"},
             "workspace": r["run"].get("workspace")}
            for r in records
        ],
    }


def to_markdown(records: list[dict[str, Any]]) -> str:
    agg = aggregate(records)
    out: list[str] = []
    out.append("# Workflow Benchmark Report\n")
    out.append("## Headline\n")
    out.append(f"- **Harness compliance (mean):** {agg['overall_compliance']}%")
    out.append(f"- **Lane accuracy:** {agg['lane_accuracy']}")
    out.append(f"- **Trace quality (mean tier):** {agg['mean_trace_tier']}/3")
    out.append(f"- **Friction captured:** {agg['friction_captured']}")
    out.append(f"- **Tasks / runs:** {agg['n_tasks']} / {agg['n_runs']}\n")

    if agg["skill_deltas"]:
        out.append("## Skill A/B delta — `tdd-workflow`\n")
        out.append("Compliance and TDD sub-score for the same task, run with the "
                   "skill available vs. with it stripped from the Harness.\n")
        out.append("| Task | Compliance (with) | Compliance (without) | Δ | "
                   "TDD (with) | TDD (without) | Δ | Coverage with/without |")
        out.append("| ---- | ----------------- | -------------------- | -- | "
                   "---------- | ------------- | -- | --------------------- |")
        for d in agg["skill_deltas"]:
            cov = f"{d['coverage_with']}% / {d['coverage_without']}%"
            out.append(
                f"| {d['task_id']} | {d['compliance_with']}% | {d['compliance_without']}% | "
                f"{d['compliance_delta']:+} | {d['skill_tdd_with']} | {d['skill_tdd_without']} | "
                f"{d['skill_tdd_delta']:+} | {cov} |"
            )
        out.append("")

    out.append("## Per-run scorecards\n")
    for r in records:
        s: TaskScore = r["score"]
        run = r["run"]
        out.append(f"### {s.task_id} — `{s.variant}` — {round(s.compliance, 1)}%")
        status = "ran" if run.get("ran") else "DID NOT RUN"
        extra = f" (exit {run.get('returncode')}, {run.get('duration', '?')}s)" if run.get("ran") else ""
        out.append(f"- agent: {status}{extra}")
        if run.get("error"):
            out.append(f"- error: `{str(run['error']).splitlines()[-1][:160] if run['error'] else ''}`")
        for d in s.dims:
            if not d.applicable:
                out.append(f"  - _{d.name}: n/a ({d.detail})_")
            else:
                out.append(f"  - **{d.name}**: {round(d.score * 100)}% — {d.detail}")
        for n in s.notes:
            out.append(f"  - note: {n}")
        out.append("")
    return "\n".join(out)
