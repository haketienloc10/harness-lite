# 0009 Deepen the Knowledge Index generator

Date: 2026-06-09

## Status

Accepted

## Context

Decision `0007` added `harness-cli knowledge` and shipped the index as a mix of
deterministic sections (Top-Level Structure, Key Technologies) and authored
sections (Purpose, Key Concepts). A review of the `generate-knowledge-index`
skill against arbitrary code repositories found the **deterministic output too
shallow and too narrow** to be a genuinely useful onboarding map outside this
repo:

- **Technology detection is a small hardcoded allowlist** (`detect_technologies`
  in `domain::knowledge`): Rust/Cargo/SQLite/Node/TS/Python/Go plus a few config
  tools. It misses Java, C/C++, C#/.NET, Ruby, PHP, Kotlin, Swift, Terraform; it
  never reports frameworks (React/Next/Vue/Angular/Django/Flask/FastAPI/Rails)
  or the package manager in use, because it only looks at file **names** and
  extensions, never manifest **contents**. Many real repos render a thin or
  empty list (`- TODO: no technologies detected.`).
- **Structure is repo-root only.** `gather` lists only the top-level entries, so
  the map never reaches the nested directories (`src/`, `apps/`, `packages/`,
  `crates/<name>`, `docs/<area>`) where code actually lives.
- **No run/build/test commands.** The map says nothing about how to build, test,
  or run the project — high-value onboarding context that is mechanically
  derivable from manifests.

This decision deepens the deterministic generator so a green, freshly scaffolded
index is more useful on any repo, while keeping the deterministic/authored split
and the mechanical `check` gate from `0007`.

## Decision

Extend `harness-cli knowledge` (deterministic sections only; the authored
Purpose / Key Concepts contract is unchanged):

1. **Broader technology detection.** Recognize more ecosystems by name/extension
   (Java via `pom.xml` / `build.gradle*` / `ext:java`, Kotlin, Swift via
   `Package.swift` / `ext:swift`, Ruby via `Gemfile` / `ext:rb`, PHP via
   `composer.json` / `ext:php`, C/C++ via `ext:c|cpp|cc|h|hpp` /
   `CMakeLists.txt` / `Makefile`, C#/.NET via `ext:cs|csproj|sln`, Terraform via
   `ext:tf`), the Node package manager (`pnpm-lock.yaml` → pnpm, `yarn.lock` →
   Yarn, `package-lock.json` → npm), and **frameworks read from manifest
   contents** (`collect_signals` already reads `Cargo.toml`; extend it to scan
   `package.json`, `requirements.txt`, `pyproject.toml`, `Gemfile`) emitting
   `dep:*` signals mapped to labels (React, Next.js, Vue, Angular, Svelte,
   Express, NestJS, Django, Flask, FastAPI, Ruby on Rails).

2. **Nested structure — new `## Key Subdirectories` section (additive).** Keep
   `## Top-Level Structure` exactly as-is (non-breaking) and add a new
   deterministic section listing the **immediate subdirectories of each
   top-level directory** (one level deeper), by relative path (e.g.
   `crates/harness-cli/`, `docs/decisions/`), skipping hidden/ignored dirs.
   Descriptions are authored and preserved per path, like Top-Level Structure
   entries.

3. **New `## How to Run` section (deterministic).** Derive build/test/run
   commands from manifests: `Cargo.toml` → `cargo build` / `cargo test`;
   `package.json` scripts (`build`/`test`/`dev`/`start`/`lint`) → `npm run <s>`;
   `Makefile` targets (`build`/`test`/`run`/`lint`) → `make <t>`; `go.mod` →
   `go build ./...` / `go test ./...`; `pytest` referenced → `pytest`. This
   section never emits a `TODO`; when nothing is detected it renders a neutral
   "No standard build/test commands detected." line so `check` stays green.

The new `## Key Subdirectories` and `## How to Run` headings are added to the
required-heading set in `check_index`, so an index produced by an older binary
is flagged as stale and refreshed via the `generate-knowledge-index` skill — the
same drift contract as `0007`. Authored content is preserved across the upgrade
because preservation is keyed by section markers and per-entry path.

## Alternatives Considered

1. **Rename `Top-Level Structure` and nest entries inside it.** Rejected:
   renaming the heading would drop authored descriptions in already-installed
   repos (preservation is anchored on the heading) and force edits to historical
   decisions/stories. An additive section is non-breaking.
2. **Add `serde_json` to parse `package.json`.** Rejected for now: the crate
   deliberately keeps a tiny dependency set (`clap`, `rusqlite`, `thiserror`). A
   small hand-rolled scan of the `scripts` block matches the existing
   `Cargo.toml` content-scan style and avoids a new dependency.
3. **Recurse arbitrarily deep for structure.** Rejected: explodes the list and
   makes `check` noisy. One extra level (immediate subdirectories) captures the
   useful layout without per-file churn.

## Consequences

Positive:

- A freshly scaffolded index is meaningfully richer on arbitrary repos: real
  language/framework/package-manager list, a two-level directory map, and
  copy-pasteable build/test/run commands.
- Detection reads manifest contents, so frameworks and package managers surface
  instead of only raw file types.
- No new runtime dependency; deterministic/authored split and the `check` gate
  are preserved.

Tradeoffs:

- The generated index contract grows (two new sections); indexes from older
  binaries are reported stale until rescaffolded. Authored content is preserved.
- Detection is still heuristic (substring scans, fixed command set) and will
  need occasional tuning; friction is logged and tuned in the generator, not by
  hand-editing the index.
- `scripts/bin/harness-cli` must be rebuilt and committed (per `0005`).

## Follow-Up

- Tighten `knowledge check` so a green check is a stronger freshness signal
  (recursive structure signature, technology-drift detection) — closes the
  asymmetry documented in `0008` (backlog).
- Detect CI (`.github/workflows`) once the signal walk can opt into specific
  hidden directories.
