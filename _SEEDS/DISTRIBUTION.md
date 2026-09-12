# _SEEDS/DISTRIBUTION — the citable install registry

**Status:** LIVE · opened 2026-08-15 · SSOT is [`distribution.jsonl`](./distribution.jsonl)
**Anchors:** ADR-044 (temporal chain-of-custody / no overclaim) · [[oss-family-seedbank-two-tier-conformance]]

> Makes the resume claim "invented **& published** open-source public goods" true at the
> **distribution** level, not just source. One row per public repo, tracking each channel's real,
> verified `live` status. `distribution.jsonl` is the machine SSOT; this file is the human view.

## The gate (read before citing anything on the resume)

**The resume / any outward SSOT may cite an install command ONLY for a channel whose registry row is
`live: true` AND carries a `verified_at` + `verify` note.** npm/PyPI channels start `live:false` and
flip only after: (1) the repo secret is added, (2) a version tag is pushed, (3) CI publishes, (4) the
install is actually run and verified here. Until then the resume cites GitHub source only. This is the
ADR-044 discipline: no NOW-claim without a receipt.

## Live now — verified 2026-08-15 (safe to cite)

| Tool | Channel | Install command | Verified |
|---|---|---|---|
| rosetta-shell | npm | `npx @flashesofbrilliance/rosetta-shell` | ✅ ran, printed version+locale |
| rosetta-shell | Homebrew | `brew install flashesofbrilliance/tap/rosetta-shell` | ✅ installed + `rosetta version` |
| germinate | npm | `npm i -g germinate` | ✅ `npx germinate@0.1.0` ran |
| germinate | Homebrew | `brew install flashesofbrilliance/tap/germinate` | ✅ installed + `germinate version`=0.1.0 (macOS) |

Homebrew users first run `brew tap flashesofbrilliance/tap` (or use the fully-qualified name above).
germinate on Homebrew is **macOS-only** for v0.1.0; Linux users use `npm i -g germinate`.

## Ready, NOT live — machinery built + dry-run-verified, publish is token-gated (do NOT cite yet)

| Tool | Channel | Would-be command | Blocker to go live |
|---|---|---|---|
| arcs-claude-project-scaffold | npm | `npx @flashesofbrilliance/arcs-claude-project-scaffold <dir>` | add `NPM_TOKEN` secret → push `v0.1.0` tag → verify |
| linkedin-connections-toolkit | PyPI | `pipx install linkedin-connections-toolkit` | add `PYPI_TOKEN` secret → push `v0.1.0` tag → verify |
| blindsat | PyPI | `pip install blindsat` | add `PYPI_TOKEN` secret → push `v0.1.0` tag → verify |

## GitHub-only by design (correct terminal state — not registry packages)

`arcs-field-scan` (Next.js web app) · `token-savings-bank` · `state-sync-skill` · `rca-skill` ·
`fix-toolbar-comments-skill` (Claude Code skills). Distribution channel = git clone / skill install.

## Finishing the token-gated channels (the two-step handoff)

1. **Add secrets** (once per repo):
   - npm: `gh secret set NPM_TOKEN -R flashesofbrilliance/arcs-claude-project-scaffold`
   - PyPI: `gh secret set PYPI_TOKEN -R flashesofbrilliance/blindsat` (and `…/linkedin-connections-toolkit`)
   (Or add them in each repo's Settings → Secrets. germinate's npm uses OIDC Trusted Publishing — no token.)
2. **Tag to publish:** `git tag v0.1.0 && git push origin v0.1.0` → the `release.yml` workflow publishes.
3. **Verify + flip:** run the install command; on success set that channel's `live:true` + `verified_at`
   in `distribution.jsonl`, then the resume may cite it.

## Namespace

npm scope `@flashesofbrilliance/*` is the family default (rosetta-shell, scaffold). **germinate is the
one intentional unscoped exception** — it holds the premium bare name `germinate` on npm (published
2026-08-14). PyPI has no scopes → repo-matching names. Homebrew → `flashesofbrilliance/homebrew-tap`.
