---
name: lab-mint
description: Mint, refine, and deploy an ARCS Lab mini-app (a free PLG instrument on lab.arcs.care) from one spec, in the FieldOS grammar and the record→receipt→seed master pattern. Use when building or updating a lab surface, or standing up a counterpart briefing-space seed. The prepaid reflex that turns a 40-message hand-build into one invocation.
---

# lab-mint — the ARCS Lab factory

One governed pipeline: **mine → refine → instrument → orchestrate → choreograph.**
This skill is the *refinery + orchestration* — it turns a surface spec into a finished,
deployed, version-controlled mini-app without re-deriving the grammar or the deploy each time.

The lab surfaces are **cubic zirconium** — the instrument, not the real diamond (the customer's
actual decision). They exist to attract and filter toward the real engagement: free, no-login,
shareable PLG onramps ([[arcs-plg-onramp-mindset-filter]]).

## Governance invariants (never violate)

1. **Source of truth is git, not the scratchpad.** Every surface lives under `_ARTIFACTS/lab/`
   (ADR-041 durable artifacts, build-excluded — confirmed in `scripts/vercel-ignore-build.sh`
   `SAFE_PATTERN`). Editing/deploying from `/tmp` scratchpad is the data-loss anti-pattern that
   motivated this skill. Edit the `_ARTIFACTS/lab/` copy; deploy from it.
2. **Isolation.** Deploy ONLY to the `arcs-experiments` Vercel project (`prj_2hKOq2uqRXualTM4zsbbOXHpuAXm`,
   serves lab.arcs.care). NEVER touch arcs-v9 (`prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`) or arcs.care.
3. **Commit before / with deploy.** The flow is: edit `_ARTIFACTS/lab/…` → commit on a worktree
   branch (build-safe, `_ARTIFACTS/` is in `SAFE_PATTERN` so no arcs-v9 build fires) → deploy →
   `STATE.json` records the serializable result (git_head + deploy_id + per-surface sha). Never
   deploy uncommitted source — that reintroduces the drift this layer exists to kill.
4. **One deploy per batch.** All surfaces ship in one immutable snapshot (`deploy_lab.py` uploads
   the whole `_ARTIFACTS/lab/` tree), so a partial deploy can never 404 a sibling route.

## The build recipe (refinery)

1. **Grammar** — FieldOS dark-glass. Pull tokens JIT from DesignSync project
   `be620c0c-708c-4160-a4fa-24996d941507` (`get_file: colors_and_type.css`, `atoms.jsx`) only if
   you need to re-verify; the canonical tokens are baked into `scaffold.html`. Inter + JetBrains
   Mono, `#020408` void bg, recessed input wells, underlit-LED accents, glass/bevel cards.
   First line of every surface MUST be `<meta charset="utf-8">` (else em-dash/·  mojibake).

2. **The master pattern** — every surface is one self-similar loop, nested like Russian dolls:
   `Trigger → Action → Receipt(open) → Seed → (Trigger)` at every zoom (atom = a coord cell,
   molecule = a receipt, organism = the surface, meta = a seed opens the next doll).

3. **Sequencing law (do NOT invert)** — [[design-for-arriving-cognitive-state]]. The visitor
   arrives System-1, in-fire, ~8s. **Lead with the fire + one obvious action, not the mechanism.**
   Value leads as *experience* (the reward — their input transformed into a receipt), the System-2
   explainer is **pulled not pushed** (a collapsed `<details>` below). Never front-load how-it-works;
   never bury it in the footer either.

4. **Copy** — plain language, no em-dashes in deliverable prose per [[writing-avoid-emdashes-plain-language]].
   Fire in the headline, benefit in one line, the mechanism named only where the reward shows it.

Start from `scaffold.html` and fill the spec. Keep JS self-contained, local-first (localStorage),
no backend, no keys, no deps.

## Deploy + verify

```bash
python3 .claude/skills/lab-mint/deploy_lab.py --dry-run   # list routes
python3 .claude/skills/lab-mint/deploy_lab.py             # deploy + write STATE.json
```
Before deploy: `node --check` the extracted `<script>`; confirm `<meta charset>` present.
After deploy: curl each route for 200 + a content marker. Screenshot before calling it done
([[deploy-antipattern-grep-verified-ui]]).

## Seed-chain (choreography)

Surfaces hand off via URL-hash seeds (`#seed=` / `#bet=`, base64 of a small JSON, unicode-safe
`btoa(unescape(encodeURIComponent(...)))`). A Briefing receipt seeds a Conviction Ledger bet; a
minted IYKYK link seeds a counterpart's briefing space. **Nothing counterpart-specific is ever
deployed** — pseudonymized content rides inside the minted link only ([[counterpart-pseudonym-key-public-artifacts]]).

## Current surfaces
`index.html` (the Lab), `conviction-ledger/`, `briefing-record/`. See `_ARTIFACTS/lab/STATE.json`
for live routes, deploy id, and per-surface sha.
