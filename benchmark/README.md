# Workflow Benchmark

An automated, scorable benchmark for the Harness workflow (`_harness/`) — and in
particular for whether the `tdd-workflow` skill improves code tasks.

It answers two questions with numbers:

1. **Does an agent that follows the Harness produce correct durable records and
   artifacts?** (classification, traces, decisions, friction capture)
2. **Does the `tdd-workflow` skill help?** — by running the same code task with
   the skill available vs. stripped, and reporting the **skill delta**, isolated
   on the `skill_tdd` sub-score (the only dimension the skill targets).

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
| `skill_tdd`      | code task: tests pass (0.25) + **branch coverage ≥ 80%** (0.50) + interface present (0.10) + story proof (0.10) + trace notes `skill: tdd-workflow` (0.05) | files + DB |

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
./run.sh --repeat 3               # 3 runs per arm; mean +- spread (averages out
                                  #   run-to-run agent variance)
```

Live-agent runs vary from run to run. `--repeat N` runs each task+variant `N`
times and the report shows the **mean (± sample SD)** per arm, so a one-off flip
(e.g. the agent classifying a task differently on one run) doesn't masquerade as
a skill effect. Recommended: `--repeat 3` or more when you care about the delta.

Output goes to `benchmark/runs/<timestamp>/`:

- `report.md` — human-readable scorecards + headline + skill delta (also printed)
- `result.json` — machine-readable scores
- `<task>/<variant>/r<k>/workspace/` — exactly what the agent produced (one dir
  per repeat; inspectable)

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

Lean by design — each task targets a distinct rubric dimension; the four code
tasks run A/B (with vs. without the skill), so `./run.sh` performs twelve runs
across eight tasks (more with `--repeat`):

| Task                | Lane      | Targets                                               |
| ------------------- | --------- | ----------------------------------------------------- |
| `T1-tiny-doc`       | tiny      | classification + Minimal trace                        |
| `T2-feature-tdd`    | normal    | **TDD skill + coverage (A/B)** — `password_strength`  |
| `T3-highrisk-auth`  | high-risk | governance gate + Detailed trace                      |
| `T4-normal-change`  | normal    | classification + Standard trace                       |
| `T5-friction`       | normal    | friction capture (references a missing spec)          |
| `T6-validator-tdd`  | normal    | **TDD skill + coverage (A/B)** — `normalize_username` |
| `T7-parser-tdd`     | normal    | **TDD skill + coverage (A/B)** — `parse_duration`     |
| `T8-calculator-tdd` | normal    | **TDD skill + branch coverage (A/B)** — `evaluate` (branch-rich, hardest) |

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

- Live-agent runs are **non-deterministic**; use `--repeat N` and read the mean
  (± SD), not a single number. The *scorer* is deterministic given a workspace.
- The **skill delta is isolated on `skill_tdd`** (the only dimension the skill
  targets). The table also shows a *Compliance Δ (ref)*, but treat it as
  reference only: it includes dimensions like `classification` whose run-to-run
  variance is unrelated to the skill and can flip its sign on a single run.
- A capable agent often writes thorough tests and hits full branch coverage even
  without the skill; when that happens the measured delta collapses toward the
  `skill_noted` term (≈ 0.05). That is a real finding, not a bug — on easy,
  well-specified tasks the skill mainly affects *whether the agent records* using
  TDD, not code quality. To see a quality delta, use harder tasks and/or a weaker
  model (`BENCH_CODEX_MODEL`).
- `skill_tdd` grades mechanically verifiable outcomes, weighted toward results
  over process signals: tests pass (0.25) + **branch** coverage vs. threshold
  (0.50) + interface symbol present (0.10) + story proof recorded (0.10) +
  skill named in trace (0.05). Branch coverage (not just line coverage) is used
  so untested edge-case branches actually cost points — that is where a
  disciplined TDD pass tends to separate from an un-guided one. Strict
  RED-before-GREEN ordering is process, not provable post-hoc, so it is not
  scored directly.
