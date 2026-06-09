# US-302 Consume the Knowledge Index in the workflow

## Status

in_progress

## Lane

normal

## Product Contract

`docs/KNOWLEDGE_INDEX.md` is wired into the agent workflow as a **read/consume**
step, not only as a generated artifact. Every task starts by reading the index
as an Orient **router** (Purpose, Structure, Tech, Concepts) that points into
the existing source-of-truth Hierarchy; on conflict the Hierarchy wins. The
index is **trust-if-fresh**: when `harness-cli knowledge check` reports drift,
the agent treats the index as stale and refreshes it via the existing
`generate-knowledge-index` skill before relying on it. This closes the consume ↔
produce loop with **no code change** (docs/policy only).

## Relevant Product Docs

- `_harness/00-AGENTS.md` (source-of-truth Hierarchy + Orient layer)
- `_harness/01-WORKFLOW.md` (Context Budget / ĐỊNH MỨC TOKEN + GĐ1 Intake)
- `docs/CONTEXT_RULES.md` (Read Shape + Retrieval Triggers)
- `docs/KNOWLEDGE_INDEX.md` (artifact consumed)
- `docs/decisions/0008-consume-knowledge-index.md`

## Acceptance Criteria

- `_harness/00-AGENTS.md` defines an "Orient" layer instructing the agent to
  read `docs/KNOWLEDGE_INDEX.md` first as a router (not a source of truth), with
  the trust-if-fresh rule pointing at `harness-cli knowledge check`.
- `_harness/01-WORKFLOW.md` lists `docs/KNOWLEDGE_INDEX.md` as a base read for
  every lane in the Context Budget (including Tiny) and adds an Orient step at
  the start of GĐ1 Intake.
- `docs/CONTEXT_RULES.md` lists `docs/KNOWLEDGE_INDEX.md` as a Read Shape entry
  and adds a Retrieval Trigger for "start of any task / onboarding".
- The index remains a router only: no content is duplicated, and the documented
  precedence on conflict is Hierarchy > index.
- No `harness-cli` code changes; existing `knowledge check` is reused as the
  freshness gate.

## Design Notes

- Commands: none new (reuse `harness-cli knowledge scaffold` /
  `knowledge check`).
- Queries: none.
- API: none (docs/policy only).
- Tables: none.
- Domain rules: index = Orient router; Hierarchy wins on conflict;
  trust-if-fresh via `knowledge check`; consume ↔ produce loop linked to
  `generate-knowledge-index` (GĐ2/GĐ6).
- UI surfaces: agent-facing harness docs.

## Validation

`scripts/bin/harness-cli story update --id US-302 --unit 0 --integration 0 --e2e 0 --platform 1`.

| Layer       | Expected proof                                                                |
| ----------- | ----------------------------------------------------------------------------- |
| Unit        | n/a (no code changed).                                                        |
| Integration | n/a (no code changed).                                                        |
| E2E         | n/a (no browser surface).                                                     |
| Platform    | `harness-cli knowledge check` exit 0 + `prettier --check .` + `cargo clippy`. |
| Release     |                                                                               |

## Harness Delta

- Wire `docs/KNOWLEDGE_INDEX.md` into the read path across `00-AGENTS.md`,
  `01-WORKFLOW.md`, and `docs/CONTEXT_RULES.md`; add decision `0008`. Governance
  gate (source-of-truth hierarchy + workflow) — approved by human.

## Evidence

Add commands, reports, or links after validation exists.
