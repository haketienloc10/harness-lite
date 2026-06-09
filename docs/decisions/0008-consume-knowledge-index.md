# 0008 Consume the Knowledge Index in the workflow

Date: 2026-06-09

## Status

Accepted

## Context

`docs/KNOWLEDGE_INDEX.md` was introduced by decision `0007` as a versioned,
in-repo "Accessed knowledge" onboarding map. However, every reference to it is
on the **produce** side — the `generate-knowledge-index` skill, the
`harness-cli knowledge scaffold/check` commands, decision `0007`, story
`US-301`, and the generator code. No step in the operating workflow tells the
agent to **read** it: it is absent from the source-of-truth Hierarchy in
`_harness/00-AGENTS.md`, from the Context Budget (ĐỊNH MỨC TOKEN) and GĐ1 Intake
in `_harness/01-WORKFLOW.md`, and from the Read Shape / Retrieval Triggers
tables in `docs/CONTEXT_RULES.md`. The index is therefore write-only: generated
and committed but never entering the agent's context loop — despite its own
header claiming it is "the onboarding map agents read before changing code".

This change touches the source-of-truth hierarchy and the workflow, which are
governance gates per `01-WORKFLOW.md` GĐ7; it was explicitly approved by the
human (Option A).

## Decision

Wire the Knowledge Index into the **read/consume** path, docs/policy only (no
code change), framing it as an **Orient router**, not a new source of truth:

- `_harness/00-AGENTS.md` §1: add an "Orient" layer — read
  `docs/KNOWLEDGE_INDEX.md` first to orient and route into the existing
  Hierarchy. On conflict, the Hierarchy wins (index never overrides durable
  sources). This keeps the index a router and avoids it becoming a monolithic
  spec (which the harness forbids).
- `_harness/01-WORKFLOW.md`: list `docs/KNOWLEDGE_INDEX.md` as a base read for
  **every lane** in the Context Budget (including Tiny), and add an Orient step
  at the start of GĐ1 Intake before Type/Lane classification.
- `docs/CONTEXT_RULES.md`: add `docs/KNOWLEDGE_INDEX.md` to the Read Shape table
  and add a Retrieval Trigger for "start of any task / onboarding".
- **Trust-if-fresh (asymmetric, gate is COARSE):** reuse the existing mechanical
  gate `harness-cli knowledge check`. Verified against the implementation
  (`domain::knowledge::check_index` + `infrastructure::gather`), the gate only
  catches: missing file/sections, remaining `TODO` placeholders, and added/
  removed **repo-root** entries (compared by name against `fs::read_dir` of the
  root). It does NOT catch: changes inside subdirectories (the bulk of real
  changes), stale Purpose / Key Concepts / Top-Level descriptions (semantic), or
  an outdated Key Technologies list (only flagged when empty). Therefore the
  rule is asymmetric: **check red ⇒ definitely stale** → refresh via the
  `generate-knowledge-index` skill (registered for GĐ2/GĐ6) before relying on
  it; **check green ⇒ NOT proof of freshness** → treat the index as an
  orientation router only, keep the Hierarchy authoritative, and proactively
  refresh (`scaffold` + re-author semantics) at GĐ2/GĐ6 whenever structure/tech
  changes. This links the consume side back to the produce side, but does not
  over-rely on the gate.

## Alternatives Considered

1. Add a CLI signal (`harness-cli knowledge show` / `status`) to print the index
   and its freshness. Rejected for now: requires a code change and binary
   rebuild (higher risk) for a need already covered by reading the file plus
   `knowledge check`.
2. Add a dedicated "GĐ0 Orientation" stage to the 7-stage workflow. Rejected:
   restructuring the workflow itself is heavier than necessary; an Orient step
   inside GĐ1 plus a Context-Budget base read achieves the same outcome.
3. Promote the index into the source-of-truth Hierarchy as an authoritative
   layer. Rejected: it would compete with durable sources and risk becoming a
   monolithic spec. The index stays a router; Hierarchy wins on conflict.

## Consequences

Positive:

- The index finally enters the agent's context loop — read first, cheaply,
  before crawling `docs/`.
- Consume ↔ produce loop is linked: a coarsely-stale index (root structure /
  sections / TODO) is detected by `knowledge check` and refreshed via
  `generate-knowledge-index` instead of silently trusted.
- No code change, low risk; respects token-budget philosophy and anti-
  duplication rules.

Tradeoffs:

- `knowledge check` is a COARSE gate, not a freshness oracle: a green check does
  not prove the index is current (it misses subdir changes and semantic drift in
  Purpose / Key Concepts / descriptions). Real freshness still depends on agents
  proactively regenerating at GĐ2/GĐ6 when structure/tech changes. Tightening
  the gate (e.g. recursive structure hashing or detecting tech drift) is
  deferred to a future CLI change (see Alternative 1 / Follow-Up).
- Adds a small base read to every lane (mitigated by the index being compact and
  cheaper than ad-hoc exploration).

## Follow-Up

- Optionally add `harness-cli knowledge show/status` (Alternative 1) if a single
  command proves more ergonomic than file read + `check`.
- Optionally wire `knowledge check` into CI for installed repos (carried over
  from decision `0007`).
- Optionally deepen `knowledge check` (e.g. recursive structure signature, tech-
  drift detection) so a green check is a stronger freshness signal.
