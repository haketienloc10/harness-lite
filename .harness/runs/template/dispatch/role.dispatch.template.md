---
run_id: <RUN_ID>
role: <ROLE>
current_phase: <PHASE>
required_input_artifacts:
  - .harness/runs/<RUN_ID>/run.yaml
  - <dispatch-specific input artifact>
allowed_read_paths:
  - .harness/runs/<RUN_ID>/run.yaml
  - .harness/runs/<RUN_ID>/dispatch/<ROLE>.dispatch.md
  - <path>
allowed_write_paths:
  - <path>
completion_criteria:
  - Read only paths listed in allowed_read_paths.
  - Write only paths listed in allowed_write_paths.
  - Produce the role artifact listed for this dispatch.
  - Final response includes status, decision, role, artifacts/files, evidence checked, next recommended role, and blockers if any.
blocked_conditions:
  - Required input artifact is missing.
  - Dispatch conflicts with run state.
  - Allowed read/write scope is unclear or insufficient.
  - Completion criteria cannot be verified from available evidence.
---

# Dispatch: <ROLE>

## Required Input Artifacts

- `.harness/runs/<RUN_ID>/run.yaml`
- `<dispatch-specific input artifact>`

## Allowed Read Paths

- `.harness/runs/<RUN_ID>/run.yaml`
- `.harness/runs/<RUN_ID>/dispatch/<ROLE>.dispatch.md`
- `<path>`

## Allowed Write Paths

- `<path>`

If an edit target is not listed under `allowed_write_paths`, do not edit it even if workspace sandbox permits it.

## Completion Criteria

- Read only paths listed in `Allowed Read Paths`.
- Write only paths listed in `Allowed Write Paths`.
- Produce the role artifact listed for this dispatch.
- Final response includes `status`, `decision`, `role`, artifacts/files, evidence checked, next recommended role, and blockers if any.

## Blocked Conditions

- Required input artifact is missing.
- Dispatch conflicts with run state.
- Allowed read/write scope is unclear or insufficient.
- Completion criteria cannot be verified from available evidence.
