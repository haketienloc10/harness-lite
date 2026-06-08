# 0007 Knowledge Index command and Codex skill

Date: 2026-06-08

## Status

Accepted

## Context

Agents need repository onboarding context ("where to start, what the product
contract says") before changing code. Today that context is sometimes produced
as an auto-generated index that lives _outside_ the repository (e.g. an external
agent's knowledge note). External indexes drift from the codebase, have no
single source of truth, are not reviewable in PRs, and are not reproducible.

We want a first-class, in-repo "Accessed knowledge" map that any Harness-enabled
repo can regenerate on demand, invokable like a slash command, starting with
Codex.

## Decision

Add a `knowledge` subcommand to `harness-cli` and ship an agent skill that
drives it:

- `harness-cli knowledge scaffold` writes/refreshes `docs/KNOWLEDGE_INDEX.md`.
  - **Deterministic, regenerated every run:** Top-Level Structure (non-hidden
    repo-root entries) and Key Technologies (detected from root signal files
    such as `Cargo.toml`, `package.json`, `.prettierrc`).
  - **Authored, preserved every run:** Purpose and Key Concepts, kept between
    HTML-comment markers; Top-Level Structure descriptions preserved per entry.
- `harness-cli knowledge check` is the mechanical VERIFY gate: fails on missing
  file, structure drift, or remaining `TODO` placeholders.
- The canonical procedure lives in `_harness/skills/generate-knowledge-index.md`
  (registered in `_harness/04-SKILLS.md`). The Codex entrypoint is a thin skill
  at `.agents/skills/knowledge-index/SKILL.md`, invokable via `/skills`.

The artifact path is `docs/KNOWLEDGE_INDEX.md`.

## Alternatives Considered

1. Prompt-only slash command (LLM writes the whole index). Rejected: output
   drifts each run, no mechanical gate, not "real project" grade.
2. Keep generating the index outside the repo. Rejected: not version-controlled,
   not reviewable, drifts from the codebase.
3. Codex custom prompt under `.codex/prompts/`. Rejected: custom prompts are
   being deprecated in favor of skills, and `.agents/skills/` is the portable,
   repo-scoped, multi-agent standard.

## Consequences

Positive:

- A reviewable, reproducible onboarding map checked into the repo.
- Deterministic facts (structure, stack) cannot silently drift; `check` gates.
- Portable across agents via `.agents/skills/`; Codex works today.

Tradeoffs:

- Technology detection is heuristic (signal-file based) and may need tuning.
- `scripts/bin/harness-cli` must be rebuilt when the CLI surface changes.

## Follow-Up

- Add `.agents/skills/` entrypoints for Claude Code / Cursor when needed.
- Optionally wire `knowledge check` into CI for installed repos.
