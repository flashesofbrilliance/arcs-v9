# ui-kit migration plan — ordered, per-surface, with coordination flags

Companion to ADR-082 and `src/ui-kit/README.md`. The gate is opt-in and ratcheted, so migration is
per-surface and reversible; nothing here is a mass rewrite. Each page: (1) inline `_tokens.css`
verbatim (or `<link>`), map its palette to canonical names, keep non-signal extras in a second
`:root{}`; (2) add `<!-- @arcs-template: <name> -->` (+ optional `@arcs-mode`); (3) add brand-profile
exemptions for that file via `impeccable ignores add-value <rule> "*" --file <path>`; (4) verify
token/component/wrap/slop gates + sweep 360–1440 + eyeball lede-vs-heading at ~1280.

**Ownership is live and drifts.** Re-check `git worktree list` + recent per-file history before
touching any page below; the flags are a 2026-09-26 snapshot. Do NOT migrate a page an active session
owns without coordinating — that is a clobber magnet (see memory `whole-file-overwrite-clobbers-...`).

## Wave 0 — DONE (this change, PoC)
- `_ARTIFACTS/profile-scan-hud.html` → template `scan-hud`. Closes half of backlog
  `scan-huds-migrate-to-tokens-css`.

## Wave 1 — unowned, backlog-blessed, low-risk (do next)
- `_ARTIFACTS/target-role-scan-hud.html` → `scan-hud`. Same `--palette-*` block; closes the other
  half of `scan-huds-migrate-to-tokens-css`. No active owner seen. **Best next PoC-follow.**
- The 6 recoil-report counterpart INSTANCES sitting inside the kit dir that ignore the sibling
  `_tokens.css` (`chase-intro`, `chris-lamontagne-recoil`, `cj-brief`, `cj-masopust-recoil`,
  `cj-pre-meeting-brief`, `fanatics-go-bag`) → `<link>` the tokens (they are beside the file) +
  template `recoil-report`. Low risk (stale engagement instances).

## Wave 2 — foreign-name re-authors (worst divergence: 27 files), by owner
The renamed-palette pages (`--nc`, `--vc`, `--acc`, `--ac/--qc`, `--bc/--cc/--ic`, `--cyanlt`). Migrate
only the unowned ones; the rest wait for their vertical's session.
- COORDINATE (actively-owned verticals — do NOT unilaterally migrate): `robin*.html`,
  `yuri-profile/-receipt`, `monstro-full.html`, `recruithaus.html`, `state-of-union.html`,
  `status.html`. Flag each to its owning session first.
- Likely unowned / stale (verify): `joe.html`, `lewoof.html`, `louisville-kernel.html`,
  `scott-profile.html`, `pf-moire`, `gauntlet`. Candidate-brief or recoil-report per shape.

## Wave 3 — verbatim-canonical-name copies (74 files)
These already use `--cyan/--gold/--green/--red` but do not inherit. Mechanically the cheapest
(replace the local `:root` palette lines with verbatim `_tokens.css` + marker), but the bulk are owned
candidate/counterpart verticals. Migrate in owner batches, one vertical per session.

## Wave 4 — actively-owned candidate/counterpart families — COORDINATION REQUIRED
Each of these is a vertical an active session owns; migration must be done BY or WITH that session:
- `public/resume-tailor.html` — **already migrated onto `_tokens.css` on an unmerged branch (commit
  `98b8013d`, a peer session).** Do NOT touch; let that branch land, then enroll a template marker.
- `public/squad*.html` (branch `claude/squad-applied-ai-engineer-d35898`) → `candidate-brief`.
- `public/success-academy*.html` (this worktree family) → `candidate-brief`.
- `public/vico*.html` (vico branch) → `candidate-brief`.
- `public/fun.html` (crypto/PMM session) → `candidate-brief`.
- `public/jack-rain*.html`, `runtime/warroom/jack-rain*.html` (already exempted in `.impeccable`;
  inspiring-gates/motion-spec lineage) → `recoil-report`.
- `public/schriner*.html`, `public/autopilot*.html` (Oxenham session) → `candidate-brief`.

## Wave 5 — NFTT family (34 posts) — needs a template + backlog coordination
`public/blog-nftt-*.html` have a SANCTIONED self-authored-under-canonical-names token path (the
`token_source_gate.py` `blog-nftt-*` exemption). Enrolling them in `nftt-essay` is a kit-wide change
that should be folded with backlog item `nftt-template-kintsugi-contrast-and-label-heuristics` (the
`--dim` AA-contrast debt + the label-vs-body detector heuristic). Do the template + detector fix once,
propagate to all 34; do not per-post patch. Decide whether to retire the token_source_gate NFTT
exemption in favor of enrollment (open question in ADR-082).

## Wave 6 — resume-print signatures
When the first resume enrolls (`public/vico-resume.html` or `squad-resume.html`), read its shared class
vocabulary and finalize `resume-print.signature_selectors` in `templates.json` (currently empty /
min_signatures 0 so it never false-fails). Resumes are often NOT-A-PALETTE light/paper surfaces; the
tokens+mode binding still applies.

## Not in scope (separate design systems — leave alone)
`prl-status-*` (PRL design system), `louisville-*` omakase-appendix, `observatory/`, `omakase/`,
forensics (`vishal-*`). These are deliberately separate visual worlds, not divergence.
