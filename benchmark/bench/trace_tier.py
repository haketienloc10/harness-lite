"""Trace quality tiers, implementing docs/TRACE_SPEC.md.

Pure functions: given a trace row (dict of column -> value) decide its quality
tier (1=Minimal, 2=Standard, 3=Detailed) and explain why. The real
`harness-cli` binary does NOT ship a `score-trace` command, so the benchmark
computes tiers itself from the rule set in TRACE_SPEC.md.
"""

from __future__ import annotations

import json
from typing import Any, Optional

TIER_NAMES = {0: "none", 1: "minimal", 2: "standard", 3: "detailed"}


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def _json_list_nonempty(value: Any) -> bool:
    """True when value is JSON array text holding at least one item.

    The CLI stores list fields as JSON array text (e.g. '["a","b"]').
    """
    if not _is_filled(value):
        return False
    if isinstance(value, (list, tuple)):
        return len(value) > 0
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        # Not JSON: treat any non-empty, non-"none" string as present.
        return str(value).strip().lower() not in ("", "none", "[]")
    if isinstance(parsed, list):
        return len(parsed) > 0
    return _is_filled(parsed)


def _present_or_none(value: Any) -> bool:
    """Detailed traces may use the literal 'none' as explicit evidence."""
    if _json_list_nonempty(value):
        return True
    return _is_filled(value) and str(value).strip().lower() == "none"


def score_trace(row: dict[str, Any]) -> dict[str, Any]:
    """Return {'tier': int, 'name': str, 'missing': {tier: [reasons]}}."""
    missing: dict[str, list[str]] = {"standard": [], "detailed": []}

    # ---- Minimal (1) ---------------------------------------------------
    summary = row.get("task_summary")
    minimal_ok = _is_filled(summary) and len(str(summary).strip()) >= 10
    outcome_ok = _is_filled(row.get("outcome"))
    minimal = minimal_ok and outcome_ok

    # ---- Standard (2) --------------------------------------------------
    std_checks = {
        "agent": _is_filled(row.get("agent")),
        "actions_taken": _json_list_nonempty(row.get("actions_taken")),
        "files_read": _json_list_nonempty(row.get("files_read")),
        "files_changed": _json_list_nonempty(row.get("files_changed")),
        "errors_or_friction": (
            _present_or_none(row.get("errors"))
            or _is_filled(row.get("harness_friction"))
        ),
    }
    for name, ok in std_checks.items():
        if not ok:
            missing["standard"].append(name)
    standard = minimal and not missing["standard"]

    # ---- Detailed (3) --------------------------------------------------
    det_checks = {
        "decisions_made": _json_list_nonempty(row.get("decisions_made")),
        "errors": _present_or_none(row.get("errors")),
        "harness_friction": _is_filled(row.get("harness_friction")),
        "duration_or_note": (
            _is_filled(row.get("duration_seconds"))
            or _is_filled(row.get("notes"))
        ),
        "token_or_note": (
            _is_filled(row.get("token_estimate"))
            or _is_filled(row.get("notes"))
        ),
    }
    for name, ok in det_checks.items():
        if not ok:
            missing["detailed"].append(name)
    detailed = standard and not missing["detailed"]

    if detailed:
        tier = 3
    elif standard:
        tier = 2
    elif minimal:
        tier = 1
    else:
        tier = 0
        if not minimal_ok:
            missing["standard"].insert(0, "task_summary(>=10 chars)")
        if not outcome_ok:
            missing["standard"].insert(0, "outcome")

    return {"tier": tier, "name": TIER_NAMES[tier], "missing": missing}


# Lane -> minimum acceptable tier (TRACE_SPEC "Lane Mapping").
LANE_MIN_TIER = {"tiny": 1, "normal": 2, "high_risk": 3}


def expected_tier_for_lane(lane: Optional[str]) -> int:
    return LANE_MIN_TIER.get((lane or "").strip().lower(), 2)
