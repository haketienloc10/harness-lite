# US-303 Deepen the Knowledge Index generator

## Status

implemented

## Lane

normal

## Product Contract

`harness-cli knowledge scaffold` must produce an onboarding map that is useful
on arbitrary code repositories, not only this one. Concretely the deterministic
sections must:

- Detect a broad set of languages, frameworks, and the package manager in use by
  reading manifest contents, not just file names.
- Show repository layout two levels deep (top-level entries plus the immediate
  subdirectories of each top-level directory).
- List how to build/test/run the project, derived from manifests.

The authored contract (Purpose, Key Concepts, preserved descriptions) and the
`knowledge check` gate from decision `0007` are unchanged. See decision `0009`.

## Relevant Product Docs

- `docs/decisions/0009-deepen-knowledge-generator.md`
- `docs/decisions/0007-knowledge-index-command.md`
- `_harness/skills/generate-knowledge-index.md`

## Acceptance Criteria

- `detect_technologies` recognizes Java, Kotlin, Swift, Ruby, PHP, C, C++,
  C#/.NET, Go, Terraform, the Node package manager (npm/Yarn/pnpm), and common
  frameworks (React, Next.js, Vue, Angular, Svelte, Express, NestJS, Django,
  Flask, FastAPI, Rails) from manifest contents.
- The index gains a `## Key Subdirectories` section listing immediate
  subdirectories of each top-level directory by path, with preserved authored
  descriptions; `Top-Level Structure` is unchanged.
- The index gains a deterministic `## How to Run` section with build/test/run
  commands derived from `Cargo.toml`, `package.json`, `Makefile`, `go.mod`, and
  Python manifests; it never emits a `TODO`.
- `knowledge check` requires the two new headings and detects drift in the new
  subdirectory list, with no false `TODO` from `## How to Run`.
- Existing authored content is preserved across an upgrade scaffold.

## Design Notes

- Commands: `harness-cli knowledge scaffold|check` (no new subcommands).
- Queries: none.
- API: `domain::knowledge` — extend `detect_technologies`, `render_index`,
  `check_index`, parsing; add `RunCommand` and subdirectory entries to
  `KnowledgeInputs`. `infrastructure::KnowledgeWorkspace` — extend `gather` /
  `collect_signals` to read manifest contents, collect depth-2 directories, and
  derive run commands. Pure rendering stays in `domain`; filesystem stays in
  `infrastructure`.
- Tables: none.
- Domain rules: deterministic sections regenerated; authored sections and
  per-path descriptions preserved between markers.
- UI surfaces: the rendered `docs/KNOWLEDGE_INDEX.md`.

## Validation

| Layer       | Expected proof                                                  |
| ----------- | --------------------------------------------------------------- |
| Unit        | `cargo test -p harness-cli` (domain detection / render / check) |
| Integration | `KnowledgeService` scaffold→author→check→rescaffold round-trip  |
| E2E         | n/a (CLI library; covered by integration)                       |
| Platform    | rebuilt `scripts/bin/harness-cli`; `knowledge check` green here |
| Release     | n/a                                                             |

## Harness Delta

- Decision `0009` records the contract change. The `generate-knowledge-index`
  skill and `03-CLI_REFERENCE.md` are updated to describe the new sections.
- `scripts/bin/harness-cli` rebuilt (decision `0005`).

## Evidence

Added after validation: `cargo test`, `cargo clippy`, `cargo fmt --check`,
`scaffold` + `check` + `prettier --check` on this repo's regenerated index.
