# Workflow Benchmark

An automated, scorable benchmark for the Harness workflow (`_harness/`) — and in
particular for whether the `tdd-workflow` skill improves code tasks.

It answers two questions with numbers:

1. **Does an agent that follows the Harness produce correct durable records and
   artifacts?** (classification, traces, decisions, friction capture)
2. **Does the `tdd-workflow` skill help?** — by running the same code task with
   the skill available vs. stripped, and reporting the **skill delta**.

This directory is standalone tooling. It does **not** modify `_harness/`,
`docs/`, the `harness-cli` binary, or `harness.db`.

## How it works

Three layers:

- **Runner** (`bench/runner.py`) — for each task it builds a clean workspace (a
  copy of the Harness), optionally strips the `tdd-workflow` skill (the A/B
  "noskill" arm), runs `harness-cli init`/`migrate`, then lets `codex exec`
  perform the task inside that workspace.
- **Scorer** (`bench/score.py`, `bench/trace_tier.py`) — **deterministic**.
  Reads the resulting `harness.db` + produced files and grades six dimensions.
  No LLM is involved in scoring, so re-scoring a workspace always gives the same
  numbers. Trace quality implements the tier rules in `docs/TRACE_SPEC.md`
  (the real binary has no `score-trace` command, so we compute tiers here).
- **Report** (`bench/report.py`) — aggregates into the headline metrics the repo
  already names in `docs/HARNESS_MATURITY.md` (Harness compliance %, Lane
  accuracy, Trace quality /3, Friction captured) plus the skill A/B delta.

### Scored dimensions

| Dimension        | What it checks                                                        | Source             |
| ---------------- | --------------------------------------------------------------------- | ------------------ |
| `classification` | intake `input_type` + `risk_lane` match the task's expectation        | `intake` table     |
| `artifacts`      | story (and implemented + proof) created when expected                 | `story` table      |
| `trace_quality`  | best trace reaches the lane's minimum tier (Minimal/Standard/Detailed)| `trace` + TRACE_SPEC |
| `friction`       | `harness_friction` captured when the task contains friction           | `trace`/`backlog`  |
| `governance`     | high-risk work has a durable `decision` row **and** a new ADR file     | `decision` + files |
| `skill_tdd`      | code task: tests pass, **coverage ≥ 80%**, interface present, story proof recorded, trace notes `skill: tdd-workflow` | files + DB |

A task only spends weight on dimensions it declares in `expect`, so unrelated
dimensions never penalize it. Per-task **compliance %** is the weighted average
of its applicable dimensions.

## Requirements

- Python 3.10+ (`run.sh` creates a local `.venv` and installs `pytest` +
  `coverage` for the real coverage measurement).
- [`codex`](https://github.com/openai/codex) CLI, logged in:

  ```bash
  npm install -g @openai/codex
  codex login            # or: codex login --device-auth  (headless)
  ```

## Run it

```bash
cd benchmark
./run.sh                          # all tasks, live agent, then score + report
./run.sh --tasks T2-feature-tdd   # just the TDD A/B centerpiece
./run.sh --timeout 900            # longer per-task budget (default 600s)
```

Output goes to `benchmark/runs/<timestamp>/`:

- `report.md` — human-readable scorecards + headline + skill delta (also printed)
- `result.json` — machine-readable scores
- `<task>/<variant>/workspace/` — exactly what the agent produced (inspectable)

### Re-score without re-running the agent (deterministic)

```bash
python3 -m bench score runs/<timestamp>
```

Useful for regression checks and for verifying the scorer is stable: scoring the
same workspaces twice yields identical numbers.

### Codex sandbox / model overrides

The runner calls `codex exec --cd <ws> -s workspace-write --json`. Override via
env vars:

- `BENCH_CODEX_SANDBOX` — `read-only` | `workspace-write` | `danger-full-access`
- `BENCH_CODEX_MODEL` — model name passed to `-m`
- `BENCH_CODEX_ARGS` — extra args appended to `codex exec`

## Task suite

Lean by design — five tasks, each targeting a distinct rubric dimension; the
centerpiece runs A/B:

| Task               | Lane      | Targets                                   |
| ------------------ | --------- | ----------------------------------------- |
| `T1-tiny-doc`      | tiny      | classification + Minimal trace            |
| `T2-feature-tdd`   | normal    | **TDD skill + coverage (A/B)**, artifacts |
| `T3-highrisk-auth` | high-risk | governance gate + Detailed trace          |
| `T4-normal-change` | normal    | classification + Standard trace           |
| `T5-friction`      | normal    | friction capture (references a missing spec) |

Each task is a directory with `task.json` (expected rubric) + `prompt.md` (the
request given to the agent). The prompts are realistic task requests; the
Harness (`AGENTS.md` → `_harness/`) is what should drive correct behavior — the
prompts deliberately do **not** spell out the workflow steps.

### Adding a task

Create `tasks/<id>/task.json` + `tasks/<id>/prompt.md`. Set `expect` to the
dimensions that matter; add a `code` block (`src_dir`, `tests_dir`, `symbol`,
`min_coverage`) for code tasks; set `variants` to `["withskill","noskill"]` to
get an A/B skill delta.

## Caveats

- Live-agent runs are **non-deterministic**; run a few times and read trends, not
  a single number. The *scorer* is deterministic given a workspace.
- `skill_tdd` grades mechanically verifiable outcomes (tests pass, coverage,
  interface symbol present, proof recorded, skill noted in trace). Strict
  RED-before-GREEN ordering is process, not easily provable post-hoc, so it is
  not scored directly.
