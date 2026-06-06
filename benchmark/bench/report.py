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


def _mean(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def _stdev(xs: list[float]) -> float:
    """Sample standard deviation; 0 for fewer than two points."""
    if len(xs) < 2:
        return 0.0
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def _group(records: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    g: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in records:
        g.setdefault((r["task_id"], r["variant"]), []).append(r)
    return g


def aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    """records: [{task_id, variant, rep, score: TaskScore, run: dict}].

    Each (task, variant) cell may hold several repeated runs; we collapse them
    to a mean (+ spread) so run-to-run agent variance does not masquerade as a
    skill effect.
    """
    groups = _group(records)
    task_ids = sorted({tid for tid, _ in groups})
    variants_of = {tid: [v for (t, v) in groups if t == tid] for tid in task_ids}

    # Headline metrics use each task's primary variant, averaged over its reps.
    compliances, tiers = [], []
    lane_judged = lane_correct = 0
    friction_tasks = friction_ok = 0
    for tid in task_ids:
        prim = _primary_variant(variants_of[tid])
        reps = [r["score"] for r in groups[(tid, prim)]]
        compliances.append(_mean([s.compliance for s in reps]))
        rep_tiers = [s.trace_tier for s in reps if s.trace_tier is not None]
        if rep_tiers:
            tiers.append(_mean(rep_tiers))
        lanes = [s.lane_correct for s in reps if s.lane_correct is not None]
        if lanes:
            lane_judged += 1
            lane_correct += 1 if _mean([1.0 if x else 0.0 for x in lanes]) >= 0.5 else 0
        fr = [_dim(s, "friction") for s in reps if _dim(s, "friction").applicable]
        if fr:
            friction_tasks += 1
            friction_ok += 1 if _mean([d.score for d in fr]) >= 1.0 else 0

    # Skill A/B deltas, isolated on the skill_tdd sub-score (the only dimension
    # the skill actually targets). Compliance delta is kept as a *reference*
    # only: it folds in dimensions like classification whose run-to-run agent
    # variance is unrelated to the skill and can even flip the sign.
    deltas = []
    for tid in task_ids:
        vs = variants_of[tid]
        if "withskill" not in vs or "noskill" not in vs:
            continue
        a = [r["score"] for r in groups[(tid, "withskill")]]
        b = [r["score"] for r in groups[(tid, "noskill")]]
        tdd_a = [_dim(s, "skill_tdd").score for s in a if _dim(s, "skill_tdd").applicable]
        tdd_b = [_dim(s, "skill_tdd").score for s in b if _dim(s, "skill_tdd").applicable]
        comp_a = [s.compliance for s in a]
        comp_b = [s.compliance for s in b]
        cov_a = [c for c in (_coverage(s) for s in a) if c is not None]
        cov_b = [c for c in (_coverage(s) for s in b) if c is not None]
        deltas.append({
            "task_id": tid,
            "n_with": len(a),
            "n_without": len(b),
            "skill_tdd_with": _round(_mean(tdd_a), 3),
            "skill_tdd_without": _round(_mean(tdd_b), 3),
            "skill_tdd_with_sd": round(_stdev(tdd_a), 3),
            "skill_tdd_without_sd": round(_stdev(tdd_b), 3),
            "skill_tdd_delta": _round((_mean(tdd_a) or 0) - (_mean(tdd_b) or 0), 3),
            "compliance_delta": _round((_mean(comp_a) or 0) - (_mean(comp_b) or 0), 1),
            "coverage_with": _round(_mean(cov_a), 1),
            "coverage_without": _round(_mean(cov_b), 1),
        })

    tdd_deltas = [d["skill_tdd_delta"] for d in deltas if d["skill_tdd_delta"] is not None]
    return {
        "overall_compliance": round(_mean(compliances), 1) if compliances else 0.0,
        "lane_accuracy": f"{lane_correct}/{lane_judged}" if lane_judged else "n/a",
        "mean_trace_tier": round(_mean(tiers), 2) if tiers else 0.0,
        "friction_captured": f"{friction_ok}/{friction_tasks}" if friction_tasks else "n/a",
        "skill_deltas": deltas,
        "mean_skill_tdd_delta": round(_mean(tdd_deltas), 3) if tdd_deltas else None,
        "n_skill_tasks": len(deltas),
        "n_tasks": len(task_ids),
        "n_runs": len(records),
    }


def _round(x, n):
    return round(x, n) if x is not None else None


def _cell(mean, sd):
    if mean is None:
        return "n/a"
    return f"{mean} ± {sd}" if sd else f"{mean}"


def _multi_rep(records, task_id, variant) -> bool:
    return sum(1 for r in records if r["task_id"] == task_id and r["variant"] == variant) > 1


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
            {**r["score"].to_dict(), "rep": r.get("rep", 1),
             "run": {k: v for k, v in r["run"].items() if k != "workspace"},
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
        msd = agg["mean_skill_tdd_delta"]
        out.append("## Skill A/B delta — `tdd-workflow`\n")
        if msd is not None:
            out.append(f"- **Skill effect (mean Δ `skill_tdd`):** {msd:+} "
                       f"across {agg['n_skill_tasks']} code task(s)\n")
        out.append("Isolated on the **`skill_tdd`** sub-score — the only dimension the "
                   "skill targets — averaged over `n` repeats per arm (± sample SD). "
                   "Compliance Δ is a reference only: it folds in dimensions like "
                   "classification whose run-to-run agent variance is unrelated to the "
                   "skill and can flip the sign.\n")
        out.append("| Task | n | TDD with | TDD without | **Δ TDD** | "
                   "Coverage with/without | Compliance Δ (ref) |")
        out.append("| ---- | - | -------- | ----------- | --------- | "
                   "--------------------- | ------------------ |")
        for d in agg["skill_deltas"]:
            n = d["n_with"] if d["n_with"] == d["n_without"] else f"{d['n_with']}/{d['n_without']}"
            with_s = _cell(d["skill_tdd_with"], d["skill_tdd_with_sd"])
            without_s = _cell(d["skill_tdd_without"], d["skill_tdd_without_sd"])
            cov = f"{d['coverage_with']}% / {d['coverage_without']}%"
            out.append(
                f"| {d['task_id']} | {n} | {with_s} | {without_s} | "
                f"{d['skill_tdd_delta']:+} | {cov} | {d['compliance_delta']:+} |"
            )
        out.append("")

    out.append("## Per-run scorecards\n")
    for r in records:
        s: TaskScore = r["score"]
        run = r["run"]
        rep = f" r{r['rep']}" if r.get("rep") and _multi_rep(records, s.task_id, s.variant) else ""
        out.append(f"### {s.task_id} — `{s.variant}{rep}` — {round(s.compliance, 1)}%")
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
