# Dispatch: <ROLE>

run_id: `<RUN_ID>`
role: `<ROLE>`
current_phase: `<PHASE>`

## Required Input Artifacts

- `.harness/project/state.yaml`
- `.harness/runs/<RUN_ID>/run.yaml`
- `<dispatch-specific input artifact>`

## Allowed Read Paths

- `.harness/project/state.yaml`
- `.harness/runs/<RUN_ID>/run.yaml`
- `.harness/runs/<RUN_ID>/dispatch/<ROLE>.dispatch.md`
- `<path>`

## Allowed Write Paths

- `<path>`

## Completion Criteria

- Read only paths listed in `Allowed Read Paths`.
- Write only paths listed in `Allowed Write Paths`.
- Produce the role artifact listed for this dispatch.
- Final response includes `status`, `decision`, `role`, artifacts/files, evidence checked, next recommended role, and blockers if any.

## Blocked Conditions

- Required input artifact is missing.
- Dispatch conflicts with project state or run state.
- Allowed read/write scope is unclear or insufficient.
- Completion criteria cannot be verified from available evidence.
