# Scope — Rendered Connector Fleet (ADR-056) · 2026-08-16

> Fork pickup brief. Mechanize `<tool>.arcs.care` connectors as a **rendered family** from SSOT.
> `resume-tailor.arcs.care` is the hand-built REFERENCE; `forge.arcs.care` is the pattern origin.
> Governing law: **ADR-056** (connector = per-tool public front-door; subdomain mirrors tool name;
> "a rendered family, not N hand-built pages"). Memory: [[arcs-tie-in-connector-per-public-good]].

## Goal
One invariant page shape, many surfaces — each live public good gets a `<tool>.arcs.care` connector,
generated from `_SEEDS/distribution.jsonl` (now carries a `connector:` field on the resume-tailor row
as the schema model). Do NOT hand-author each page.

## SSOT
`_SEEDS/distribution.jsonl` — each row: `repo`, `url`, `channels[]` (channel/pkg/install/live/verify),
optional `connector{url,live,verified_at,verify}`, `notes`. Extend rows with the fields the template
needs (one-liner, what-it-does bullets, tie-in) rather than inventing a second SSOT.

## Template
Extract the invariant shape from `public/resume-tailor.html` into a data-driven renderer
(pattern: `scripts/milestone_render.py` + `_ARTIFACTS/milestones/_template.html`, per
[[milestone-artifact-engine]] — freeze layout, vary only the data block). Sections per page:
hero (tool name + one-line what) · install block (real channels only) · what-it-does · ARCS tie-in ·
footer. House style: **no em-dashes** (use `…` or restructure), honest tagline, ellipsis-human voice.

## Fleet scope — LIVE public goods only
INCLUDE (registry `live:true`): `rosetta-shell`, `germinate` (both npm+brew — strongest install
stories, do these first), `rca-skill`, `state-sync-skill`, `token-savings-bank`,
`fix-toolbar-comments-skill`, `arcs-field-scan`.
EXCLUDE until published (registry `live:false`): `arcs-claude-project-scaffold`,
`linkedin-connections-toolkit`, `blindsat`. **No connector may claim an install path that isn't live.**

## Honesty guardrails (hard)
- Cite ONLY `live:true` channels; each page's install story must match that row's `verify` string.
- Air-gap: PUBLIC/ungated only — no private `_SEEDS` registry, rosetta, or ripeness priors on a connector.
- Subdomain = tool/repo name (ADR-056): `rosetta-shell.arcs.care`, `germinate.arcs.care`, etc.

## Output & STOP line
Produce, in a worktree branch: `public/<tool>.html` per tool + the renderer + `next.config.ts` rewrite
entries + a Vercel domain-attach checklist (one `POST /v10/projects/{id}/domains` per subdomain).
**STOP before any outward deploy / subdomain attach** — return the branch + checklist for owner approval.
Build + local pixel-verify only (headless render + LOOK, per [[deploy-antipattern-grep-verified-ui]]).

## Cost note
N live tools → 1 renderer + N data blocks + 1 batched deploy, not N hand-built pages and N debug pushes.
Iterate locally; one deploy at the end after approval.
