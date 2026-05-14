# harness-lite

`harness-lite` is a small Codex project skeleton for role-based AI-assisted development. It keeps orchestration explicit through project state, run state, dispatch files, and four scoped lifecycle roles.

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
  project/state.yaml
  runs/template/run.yaml
  runs/template/dispatch/role.dispatch.template.md
  decisions/template/decisions.template.md
  test-matrix/template/domain.template.md

AGENTS.md
README.md
```

## Runtime expectation

Codex reads project-scoped custom agents from `.codex/agents/*.toml`. The Coordinator uses `AGENTS.md`, `.harness/project/state.yaml`, run state, and dispatch files to decide which role runs next.

## Starting a run

Create a new run directory from the templates:

```bash
mkdir -p .harness/runs/<RUN_ID>/dispatch
cp .harness/runs/template/run.yaml .harness/runs/<RUN_ID>/run.yaml
cp .harness/runs/template/dispatch/role.dispatch.template.md .harness/runs/<RUN_ID>/dispatch/harness-planner.dispatch.md
```

Then replace `<RUN_ID>`, `<ROLE>`, `<PHASE>`, and the dispatch-specific read/write paths. Update `.harness/project/state.yaml` so it points at the active run.

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
