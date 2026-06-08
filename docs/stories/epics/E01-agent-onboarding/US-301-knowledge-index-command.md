# US-301 Knowledge Index command + Codex skill

## Status

done

## Lane

normal

## Product Contract

A repository using Harness can (re)generate a versioned **Knowledge Index**
(`docs/KNOWLEDGE_INDEX.md`) — the "Accessed knowledge" onboarding map an agent
reads before touching code. The deterministic parts (Top-Level Structure, Key
Technologies) are produced by `harness-cli`; the semantic parts (Purpose, Key
Concepts) are authored by agents/humans and preserved across regenerations. A
Codex skill (`/skills` → `knowledge-index`) drives the full procedure so it is
invokable like a slash command, and the layout is portable to other agents
(`.agents/skills/`).

## Relevant Product Docs

- `docs/KNOWLEDGE_INDEX.md` (artifact produced)
- `_harness/skills/generate-knowledge-index.md` (canonical procedure)
- `.agents/skills/knowledge-index/SKILL.md` (Codex entrypoint)

## Acceptance Criteria

- `harness-cli knowledge scaffold` creates `docs/KNOWLEDGE_INDEX.md` with the
  four sections (Purpose, Key Technologies, Top-Level Structure, Key Concepts).
- Re-running `scaffold` refreshes the deterministic sections to match the
  current filesystem while preserving authored Purpose / Key Concepts and any
  authored Top-Level Structure descriptions.
- `harness-cli knowledge check` exits non-zero with actionable messages when the
  index is missing, stale (structure drift), or still has unfilled `TODO`
  placeholders; exits zero when complete and current.
- The Codex skill and harness skill describe the run → fill → verify loop and
  point at `harness-cli knowledge` + `docs/GLOSSARY.md` instead of duplicating.

## Design Notes

- Commands: `harness-cli knowledge scaffold`, `harness-cli knowledge check`.
- Queries: none (filesystem only; no SQLite involvement).
- API: new `knowledge` subcommand surface on the CLI.
- Tables: none.
- Domain rules: technology detection from root signal files; parse/merge of
  preserved marker blocks; render of the index; check = required sections + no
  TODO + structure matches filesystem.
- UI surfaces: CLI + Codex `/skills`.

## Validation

`scripts/bin/harness-cli story update --id US-301 --unit 1 --integration 1 --e2e 0 --platform 1`.

| Layer       | Expected proof                                                            |
| ----------- | ------------------------------------------------------------------------- |
| Unit        | domain: tech detection, preserved-block parse/merge, render, check logic. |
| Integration | infra: scaffold writes/refreshes file; check on temp repo dirs.           |
| E2E         | n/a (no browser surface).                                                 |
| Platform    | CLI invoked end-to-end on this repo; binary rebuilt for `scripts/bin`.    |
| Release     |                                                                           |

## Harness Delta

- New CLI capability (`knowledge`), new harness skill + registry row, new Codex
  skill, decision `0007`, and the generated `docs/KNOWLEDGE_INDEX.md`.

## Evidence

- `cargo test --release` → 18 passed (domain: tech detect / parse-merge / render
  / check; application: scaffold→author→re-scaffold idempotent + check green).
- `cargo clippy --all-targets` clean; `cargo fmt --check` clean.
- `harness-cli knowledge scaffold` → `npx prettier --write` →
  `harness-cli knowledge check` exits `0` on this repo; round-trip is
  idempotent.
- Artifact committed: `docs/KNOWLEDGE_INDEX.md`.
