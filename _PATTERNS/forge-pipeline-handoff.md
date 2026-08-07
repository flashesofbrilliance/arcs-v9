# Forge pipeline — fresh-session pickup (run the CLI parameterized version)

_2026-08-07. Start here for the fresh session that builds and runs the parameterized/componentized
counterpart forge with args / depts / runtime configs._

## Read first (the full spec)
`_PATTERNS/counterpart-artifact-family-blueprint.md` — §1-11. It carries the floor plan, component
grammar, decision log, roadmap suite, the Robin platinum-master extraction, the UI-kit truing, and the
generation honesty gate. Do not re-derive; that file is the SSOT.

## Goal
A re-runnable CLI (`/forge <name>`) that generates a counterpart's clean surface family from their SSOTs,
to Robin's crispness bar. Deterministic SSOT -> render, one token source, honest about resolution.

## The order of work
1. **True up the UI kit FIRST (§10).** Canonical tokens = `src/ui-kit/recoil-report/_tokens.css`
   (== `src/document/tokens.ts`), standard ARCS dark-cockpit. Extract the §2 grammar into partials that
   import it; no per-page `:root`. Make the `#tip` data-vis hover/tap tooltip a canonical kit component.
   Regenerate `public/robin-receipt.html` off its omakase drift back onto canon (omakase house style stays
   scoped to the omakase/louisville family only).
2. **Extract Robin's 4 surfaces as parameterized templates (§9):** `robin.html` (one-door, leads with the
   real-call STORY not a diagram), `robin-profile` (the read), `robin-codex` (dual Read + Instrument),
   `robin-receipt` (forensic close: bet-filed-before -> scored-after). Crispness rules = generation constraints.
3. **Build the generator + skill:** `scripts/forge_counterpart.py` (SSOT -> templates -> pages, follow
   `recoil_brief.py` / `gen_recoil_artifact.py` / `receipt_lookup.py` + add `gen_receipt_close.py`), the
   `/forge` skill orchestrating gather->synth->generate->verify->deploy, reusing recoil-new/prep/close/ship.
4. **Verify gate:** impeccable detector, 0 em-dashes, fabrication/air-gap scan (role-archetypes only),
   attribution check (Me=Zach / Them=counterpart), and the **honesty gate (§11):** insufficient signal ->
   flag `additional enrichment source inputs required`, never fabricate or import-to-fill.
5. **Acceptance test = regenerate Yuri to Robin's bar (§9):** profile already regrounded; add a `yuri-receipt`
   (ex-ante `kleban.json` scored against `kleban-recoil.json`); restructure `yuri.html` to lead with the real
   belief-flip story; re-tier codex+demo as the deeper how-it-scales layer. Single-call (no multi-call arc).

## Runtime / deploy notes
- Deploy from the **main worktree only** (`git worktree list` first). Vercel CLI auto-refreshes its token
  (`vercel whoami` works even when the raw auth.json token is expired); add subdomains with
  `vercel domains add <domain>` from the linked project dir (project `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`),
  and mirror the `next.config.ts` `beforeFiles` rewrites off the existing `yuri-*` / `robin-*` entries.
- Model-efficient: cheap tier for mechanical stages, higher only for synthesis/verify. Quality floor
  non-negotiable; overengineering is the anti-goal.
- The earlier forge task (`task_56561b51`) started before blueprint §7-11 existed — restart it or have it
  re-read the blueprint so it runs against the complete spec.
