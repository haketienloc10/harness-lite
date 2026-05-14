# harness-lite

## Install into another repo

From the target repo directory:

```bash
curl -fsSL https://raw.githubusercontent.com/haketienloc10/harness-lite/main/install.sh | sh
```

The installer downloads the GitHub archive and copies only:

```txt
.harness
.codex
AGENTS.md
```

It refuses to overwrite existing paths. To overwrite:

```bash
curl -fsSL https://raw.githubusercontent.com/haketienloc10/harness-lite/main/install.sh | FORCE=1 sh
```

`harness-lite` is a small Codex project skeleton for role-based AI-assisted development. It keeps orchestration explicit through run state, dispatch files, and four scoped lifecycle roles.

## When to use

Use this skeleton when a task should move through a controlled lifecycle instead of letting one agent plan, implement, and approve its own work.

The default lifecycle is:

```txt
Planner -> Contract Reviewer -> Generator -> Evaluator
```

## Layout

```txt
.codex/agents/
  harness-planner.toml
  harness-contract-reviewer.toml
  harness-generator.toml
  harness-evaluator.toml

.harness/
  runs/template/run.yaml
  runs/template/dispatch/role.dispatch.template.md
  decisions/template/decisions.template.md
  test-matrix/template/domain.template.md

AGENTS.md
README.md
```

## Runtime expectation

Codex reads project-scoped custom agents from `.codex/agents/*.toml`. The Coordinator uses `AGENTS.md`, run state, and dispatch files to decide which role runs next.

## Starting a run

Create a new run directory from the templates:

```bash
mkdir -p .harness/runs/{RUN-YYYYMMDD-NNN-task-slug}/dispatch
cp .harness/runs/template/run.yaml .harness/runs/{RUN-YYYYMMDD-NNN-task-slug}/run.yaml
cp .harness/runs/template/dispatch/role.dispatch.template.md .harness/runs/{RUN-YYYYMMDD-NNN-task-slug}/dispatch/harness-planner.dispatch.md
```

Then replace `{RUN-YYYYMMDD-NNN-task-slug}`, `<ROLE>`, `<PHASE>`, and the dispatch-specific read/write paths. The run's lifecycle state lives in `.harness/runs/{RUN-YYYYMMDD-NNN-task-slug}/run.yaml`.

Use `AGENTS.md` as the canonical artifact layout reference for a run. Files under `.harness/**/template/` are examples only, not active run artifacts.

## Status contract

Role final responses use a stable top-level status:

```txt
PASS | FAIL | BLOCKED | DONE
```

Role-specific outcomes go in `decision`, for example `approved`, `rejected_requires_revision`, `implemented`, `pass`, `fail`, or `blocked_insufficient_evidence`.

## Known limitations

- This repo is a skeleton; it does not include a validator script yet.
- Coordinator setup still requires manual run and dispatch creation from templates.
- Dispatch files are the source of truth for subagent scope, so incomplete dispatch files should block the role.
