---
name: deepwiki
description: >-
  Generate or refresh a DeepWiki-style Markdown wiki for the repo under
  docs/wiki/ (overview + per-area pages with architecture diagrams, summaries,
  and links to sources). Use when onboarding a repo, when the structure or tech
  stack changed, or when wiki pages drift from the current tree.
---

# DeepWiki

Thin entrypoint. The canonical, verifiable procedure lives in the Harness skill
**`_harness/skills/generate-deepwiki.md`** — read and follow it. This file only
adapts that procedure for an agent's "skill" surface (e.g. Codex `/skills`).

DeepWiki is a _consumer_ of `docs/KNOWLEDGE_INDEX.md` (the Orient map) and the
source-of-truth Hierarchy: it reads them as a frame, then expands each Area into
its own page with an architecture diagram, a summary, and links to the real
source paths. Do **not** duplicate the index or glossary — link to them.

## Steps

1. **Orient** — fix the page list. If `.devin/wiki.json` has `pages`, create
   exactly those; otherwise cluster the `KNOWLEDGE_INDEX.md` Top-Level Structure
   into Areas (one page each). Every page must map to a real path.

2. **Author** the wiki:
   - `docs/wiki/README.md` — Purpose (matches the index), a `mermaid`
     architecture diagram, a table linking every page, and a "Sources" list.
   - `docs/wiki/<area>.md` — summary, key files (links to real paths),
     flow/interactions (mermaid when useful), related concepts (link
     `docs/GLOSSARY.md`), and a `[← Wiki](./README.md)` back-link.

3. **Format** (repo uses Prettier `proseWrap: always`):

   ```bash
   npx prettier --write "docs/wiki/**/*.md"
   ```

4. **Verify** — the mechanical gate. Each must pass:

   ```bash
   test -f docs/wiki/README.md
   npx prettier --check "docs/wiki/**/*.md"
   ! grep -rIn -e 'TODO' -e '<area>' -e 'TBD' docs/wiki
   ```

## Done when

`docs/wiki/README.md` plus every Area page exist, the index links to all pages
and every page links back, no placeholders or broken intra-wiki `.md` links
remain, and Prettier is clean.

<!--
Extensibility: this is the Codex-facing wrapper. To support another agent, add a
sibling thin entrypoint that points back at the same canonical Harness skill
(`_harness/skills/generate-deepwiki.md`) instead of duplicating it:
  - Claude Code: `.claude/commands/deepwiki.md`
  - Cursor:      `.cursor/commands/deepwiki.md`
-->
