---
name: counterpart-forge
description: Forge the 4-surface counterpart artifact family (landing + recoil + codex + demo) for ANY counterpart from one recoil seed, via the deterministic partials x SSOT pipeline. Use to stand up a new counterpart universe end to end, or re-render an existing one after editing its forge SSOT. Command /forge <name>.
---

# counterpart-forge

The "mechanize instance #2" pipeline. Given a **recoil seed** (enriched-profile SSOT + call
transcript), produce the 4-surface family for a counterpart, parameterized by name:

| Surface | File | Domain | Job |
|---|---|---|---|
| A landing | `public/<name>.html` | `<name>.arcs.care` (ungated) | one door, sequences the other 3 |
| B recoil | `public/<name>-recoil.html` | `<name>-recoil.arcs.care` | the loop, run on their own call |
| C codex | `public/<name>-codex.html` | `<name>-codex.arcs.care` | one decision, five altitudes (+ present mode) |
| D demo | `public/<name>-demo.html` | `<name>-demo.arcs.care` | inference ledger, data-driven + JSON export |

Shared grammar lives in `partials/` (single source of truth). The generator is deterministic:
same forge SSOT in, same HTML out. Full design rationale: `_PATTERNS/counterpart-artifact-family-blueprint.md`.

## The chain: gather -> synthesize -> generate -> verify -> deploy -> poll

### 0. Preconditions
- `git worktree list` -- know where the **main** worktree is. **All deploys happen from main only**
  (cost discipline; each surface is one file + one build). Never deploy from a feature worktree.
- Confirm the two seeds exist for `<name>`: an enriched-profile JSON and a call transcript/recoil JSON
  in `runtime/recoil/generated/`.

### 1. Gather (reuse existing skills)
Run `recoil-prep` / `recoil-new` to assemble the seed if it is not already built. The enriched-profile
scan (`scripts/gen_profile_seed.py` per [[counterpart-codex-recoil-seed-pattern]]) is seed #1; the
Granola transcript is seed #2. **Attribution discipline: in the transcript Me=Zach, Them=counterpart.**
Never attribute Zach's framing to the counterpart.

### 2. Synthesize ONE forge SSOT
Merge the two seeds into `runtime/recoil/generated/<name>-forge.json`. Schema:
`scripts/forge_counterpart.py` -> `FORGE_SCHEMA_DOC`; worked example: `kleban-forge.json`. This is the
one record all four surfaces render from. Content rules (non-negotiable):
- **Zero em-dashes** anywhere. Plain language, short sentences ([[writing-avoid-emdashes-plain-language]]).
- **The fence** (`meta.fence`): show shape + value in full; withhold the transform. Dial `tight` for
  resourced counterparts who could rebuild what is shown (e.g. big tech); `standard`/`loose` otherwise.
- **Role-archetypes only** for real orgs; never fabricate interiority about a named person. Codex
  altitudes are seats ("office of the CEO", "operator"), not real individuals.
- **Attribution:** `said[].speaker` is `zach` (cyan) or `counterpart` (green, their own words).
- Every demo `read` carries a `clue` + `inference` (a labeled read, not an asserted fact). Reserved-band
  reads carry a `disclosure`. This is enforced by verify (H3).

Consider running `omakase-pipeline` first if this counterpart also needs the back-of-house SSOT +
coursed cellar; the forge family is the target-tuned front-of-house at essence.

### 3. Generate
```bash
python3 scripts/forge_counterpart.py --data runtime/recoil/generated/<name>-forge.json
```
Writes all 4 to `public/`. `--surface <one>` + `--stdout` to preview a single surface; `--out-dir` to
render to a scratch dir first (recommended if `<name>` could collide with a live file).

### 4. Verify (ALL hard checks must pass before deploy)
```bash
python3 scripts/forge_verify.py --data runtime/recoil/generated/<name>-forge.json
```
Runs: impeccable anti-pattern detector (`node ~/.claude/skills/impeccable/scripts/detect.mjs`),
0-em-dash scan, attribution + labeling checks, noindex + gate topology, password = first name.
Exit nonzero = deploy blocked. Also screenshot at least the landing + demo locally (serve `public/`
via the dev server or a scratch http server) -- [[deploy-antipattern-grep-verified-ui]]: one look beats a
gauntlet.

### 5. Deploy (from the MAIN worktree, one build per surface)
Add 4 host rewrites to `next.config.ts` `beforeFiles`, mirroring the existing `yuri-*` entries
(single wildcard rule each, the proven-reliable shape):
```ts
{ source: "/:path*", destination: "/<name>.html",        has: [{ type: "host", value: "<name>.arcs.care" }] },
{ source: "/:path*", destination: "/<name>-recoil.html", has: [{ type: "host", value: "<name>-recoil.arcs.care" }] },
{ source: "/:path*", destination: "/<name>-codex.html",  has: [{ type: "host", value: "<name>-codex.arcs.care" }] },
{ source: "/:path*", destination: "/<name>-demo.html",   has: [{ type: "host", value: "<name>-demo.arcs.care" }] },
```
Add each `<name>*.arcs.care` subdomain to the Vercel project (token at
`~/Library/Application Support/com.vercel.cli/auth.json`, project `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`) via
the REST API per [[vercel-config-via-cli-token-rest-api]] and [[subdomain-html-hosting-workflow]]. Commit
the 4 HTML files + the forge SSOT + the `next.config.ts` change together, push, let Vercel build once.

### 6. Poll live
After deploy, confirm each host serves **status Ready**, not just HTTP 200
([[vercel-ignored-build-step-was-inverted]]): `get_deployment(<name>.arcs.care)`. Verify the pw-gate
prompts and the first-name password admits.

## Command
`/forge <name>` -> run this chain for `<name>`. If no forge SSOT exists yet, start at step 1; if it
exists, start at step 3 (re-render) and re-verify before any redeploy.

## Anti-goals
- Do NOT hand-edit the generated `public/<name>*.html` files. Edit the SSOT or a partial and re-generate;
  hand edits break determinism and the JSON export ([[build-reusable-decomposable-interoperable-default]]).
- Do NOT deploy on a failing verify, and do NOT deploy from a feature worktree.
- Do NOT put internal scoring (NCI, conviction values, kinematics) on any forged surface; that stays in
  the war-room ([[internal-external-artifact-air-gap]]).
