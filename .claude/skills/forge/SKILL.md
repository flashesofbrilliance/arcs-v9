---
name: forge
description: Forge a counterpart's clean surface family (recoil / codex / receipt-close) from their SSOTs, to Robin's crispness bar, via the deterministic forge_counterpart.py generator. Use to stand up or level a counterpart artifact universe end to end — gather, synthesize, generate, verify, deploy. Robin is the platinum master; Yuri is the acceptance test.
---

# /forge <name> — the parameterized counterpart forge

Deterministic SSOT -> template -> page. One token source (canonical ARCS
dark-cockpit, `src/ui-kit/recoil-report/_tokens.css`, ADR-009/031). Crispness
rules are generation constraints, not hand-discipline. Run model-efficiently:
cheap tier for the mechanical stages, higher tier only for synthesis + verify.
Overengineering is the anti-goal; the quality floor is non-negotiable.

**Read before deriving anything:** `_PATTERNS/counterpart-artifact-family-blueprint.md`
(sec 1-11) is the SSOT floor plan. This skill executes it; it does not re-derive it.

## The surfaces (blueprint sec 1, sec 9) — the 3-read triad
| Surface | Job | Generator | Lives at |
|---|---|---|---|
| **recoil** | show the loop on THEIR own call (before/after) | `recoil_brief.py --format html` | `<name>-recoil.arcs.care` |
| **codex** | how the read is made (dual: Read + Instrument) | (hand template until extracted) | `<name>-codex.arcs.care` |
| **receipt** | the crispest proof: bet-filed-before -> scored-after | `forge_counterpart.py --surface receipt` | `<name>-receipt.arcs.care` |

Robin's 4 live surfaces are the platinum master. Do NOT hand-fix a counterpart
to the bar — generate to it. The receipt surface is fully mechanized in
`scripts/forge_counterpart.py`; recoil is mechanized in `scripts/recoil_brief.py`.

## Pipeline: gather -> synth -> generate -> verify -> deploy

### 1. gather (cheap tier) — reuse the recoil skills
- New relationship: `/recoil-new` scaffolds `runtime/recoil/generated/<date>-<name>.json`.
- Before a call: `/recoil-prep` fills Pre-Call + Ex-Ante (this is the **bet, filed before**).
- After the call: `/recoil-close` pulls the transcript, scores ex-ante vs reality, fills the recoil.
- Two seed inputs always (blueprint sec 0): enriched-profile SSOT (public scan + `resolution` caveat)
  and the **call transcript** (ground truth). Attribution: `Me`=Zach, `Them`=counterpart.

### 2. synth (higher tier) — assemble the receipt SSOT
- Scaffold: `python3 scripts/gen_receipt_close.py --recoil <recoil.json> --ex-ante <warroom.json> --out <name>-receipt.json`.
  It seeds `close.scorecard` from the recoil belief-update table (every row grounded in a verbatim
  line the counterpart said) and stubs the narrative fields as TODO.
- Enrich the TODO fields (waveform points, reverse-listening beats, kairos-lock, posterior, confidences).
  **Crispness constraints (blueprint sec 9, encode as you write):**
  - Lead with the real-call STORY and verbatim quotes, not an abstract diagram.
  - The receipt-close is first-class: predicted-before vs actual-after, honestly scored (HIT/MISS/PARTIAL).
  - Single-call counterparts render single-call — no multi-call arc (that is Robin-only).
  - **Honesty gate (sec 11):** if public signal is insufficient, add a `resolution_gaps` entry
    (`{what, inputs}`) rendered as a visible `additional enrichment source inputs required` flag.
    Never fabricate and never import a claim from the master to fill a gap.

### 3. generate (mechanical)
```bash
python3 scripts/forge_counterpart.py --surface receipt --data runtime/recoil/generated/<name>-receipt.json --out public/<name>-receipt.html
python3 scripts/recoil_brief.py --data runtime/recoil/generated/<name>-recoil.json --audience external --format html > public/<name>-recoil.html
```

### 4. verify (the automated quality floor — blueprint sec 4 + sec 10)
The generator runs the gates inline and **refuses to write on any FAIL**. It enforces:
- impeccable voice (0 em-dashes, no buzzword tells),
- **no side-tab** (colored `border-left/right` >1px on a callout — the top AI tell; craft-floor rule),
- canonical tokens only (fails on any omakase `#0B0B0C`/`#C9A227`/`#5C8A4E`/`#E34F1C`/Helvetica),
- honesty + attribution (every scorecard row has an observed outcome; every net-new signal a verbatim quote).

Then run the real detector + a browser look (screenshots are not enough — verify the render):
```bash
node ~/.claude/skills/impeccable/scripts/detect.mjs public/<name>-receipt.html   # want: 0 anti-patterns
python3 scripts/forge_counterpart.py --verify-only --file public/<name>-receipt.html
```
For a heavier pass, run `/impeccable audit` or the gauntlet (BAR/COURT/LAB/Funhouse) before ship.

### 5. deploy (main worktree ONLY)
- `git worktree list` first; edit `public/` here, but the live subdomains serve from **main**.
- Add the rewrite to `next.config.ts` `beforeFiles`, mirroring the existing `robin-receipt` entry:
  `{ source: "/:path*", destination: "/<name>-receipt.html", has: [{ type: "host", value: "<name>-receipt.arcs.care" }] }`.
- Add the subdomain: `vercel domains add <name>-receipt.arcs.care` (project `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`;
  the Vercel CLI auto-refreshes its token). Deploy is a docs/public change on main -> one build.

## Acceptance test (proves the pipeline)
Regenerate Yuri to Robin's bar: `public/yuri-receipt.html` from
`runtime/recoil/generated/2026-07-23-kleban-receipt.json` (ex-ante `kleban.json` scored against
`kleban-recoil.json`), single-call, leading with the belief-flip story. If it matches Robin's
crispness and passes every gate + the detector, the forge is sound.
