# Pickup task — pitch-us bundle polish pass (Ahmed-legibility + altitude reorder + wrap + honesty)

> Captured 2026-09-09 near the weekly wall. Everything below is spec'd to execute clean in one pass.
> The two pitch pages (public/sentilink.html, public/mercury.html) are LIVE at sentilink.arcs.care /
> mercury.arcs.care (noindex). Both are wing-chassis surfaces that PROJECT their _ARTIFACTS memos.

## 1. THE CENTERPIECE — reorder each pitch as an altitude descent (wuwei)

**Why:** Ahmed's data-driven-storytelling bar = takeaway-first + legibility. Zach sharpened it twice:
(a) **fail-fast for the reader** — the current order buries the ask/why-me at the end, so a "right
premise, wrong guy" reader must pay the full read before they can disqualify on the person; leading
with ask+operator lets them run their own stop-loss cheaply on EITHER axis (premise OR person).
(b) **the descent IS the demo** — the counterpart already knows their own unfair advantage; what they
are buying is someone who can go **exec → strategic → operational → tactical → surgical in one breath**.
The page should DEMONSTRATE that fluency by descending altitudes top-down, each step effortless (wuwei),
never making the reader climb.

**New order (both pages), mapped to altitude:**
| Altitude | Block (SentiLink §# was) | 
|---|---|
| EXEC | The Ask + the 90-day proof (§10) + Why Me / the operator (§10) — lead here |
| STRATEGIC | The Opportunity (§1) · Why Now (§3 kairos) · Why SentiLink/right-to-win (§9) |
| OPERATIONAL | What I'd build (§5) + the instrument-panel gauges (§2) |
| TACTICAL | The phased plan + go/no-go gates (§8's plan half / §6) |
| SURGICAL | The rigor tail: evidence base (§6 ms-list) · objection map (§7) · pre-mortem (§8) |

(Mercury: identical treatment, its own section numbers — same altitude mapping.)

**What to change per page:**
- Physically reorder the `.section` blocks into the descent above; renumber the `.section-n` labels 01..N.
- Re-sequence the PRESENT `SLIDES` array to match (OPENING = the ask; ACTs descend; final horizon slide
  can be the surgical "give me the pilot" close, or keep the ask as bookend — author's call).
- Keep the collapsed `.sec-tldr` one-liners; make each the takeaway (the number + the so-what) so the
  collapsed read alone descends the arch.
- Preserve the SSOT rule: the page projects the memo. Reconcile the memos (`_ARTIFACTS/*-pitch/pitch-memo.md`)
  to the new order so page and SSOT do not drift (they already drifted slightly from the gauntlet edits).
- **Wuwei seams**: each section's opening line should hand off from the prior altitude, not restart cold.

## 2. Ahmed-legibility polish (same pass)
- Lead each section with its hardest number + so-what (data-led, not thesis-led). SentiLink leans on one
  hearing + a GAO range; front-load the strongest figure. Mercury leans narrative; lead with the $ figures.
- Tighten the expanded prose to scannable (the wing register is dense; that is the "delivery mechanism"
  Ahmed dinged). Shorter sentences, more structure, less literary in the deep sections.

## 3. Wrap spot-check (the impeccable pass Zach asked for)
- Cover letter tagline orphans "MCP" ("... AI ON CLAUDE +\nMCP") — fix the mono tagline wrap in
  `_ARTIFACTS/forge-mercury-open-call/cover-*.html` and the sentilink cover.
- Sweep the forge/monstro site + all four pitch surfaces for the wrap-regression class at 375/790/1024/1280.
- Run `scripts/artifact_wrap_lint.py` on every touched html; the gate now also covers `_ARTIFACTS/*.html`.

## 4. Honesty confirms (need Zach's yes/no, do not guess)
- **Resume**: it added "RAG" to the skills line and re-labeled ARCS's outcome-capture loop as "evals."
  DROP "RAG" unless ARCS has a real retrieval-augmented component; confirm "evals" framing is fair.
  File: `_ARTIFACTS/forge-mercury-open-call/resume-mercury-open-call.html` (+ ats.txt + pdf; re-render via its render.sh after edits).
- **Covers**: the Axon line is included; confirm it is on Zach's record before send (both covers footer-flagged it).

## 5. Parked gauntlet items (from the low-lift counterpart-gauntlet, both FIX-FIRST)
- SentiLink: add one line of eCBSV permitted-use diligence for the government beachhead (Flag 3).
- Mercury: re-rank the three pillars around spend-timing (the one clean-greenfield wedge), demote
  pricing/runway to fast-follows (Flag 1). Both should get a full `counterpart-gauntlet` ladder before an
  ACTUAL send (only the low-lift pass has run).

## State at capture (all live)
- Deployed: sentilink.arcs.care (/, /operator), mercury.arcs.care (/, /operator) — noindex, per-company
  favicons (shield / coin); NFTT No.11 at good.arcs.care/blog/nftt/schematic-scaffolds; monstro.arcs.care
  five-systems now a 1-1 mapping table.
- Scheduled: `monstro-postcall-recoil-ship` fires 2026-09-09 14:00 EDT → builds monstro.arcs.care/debrief
  from the 1pm call transcript (draft-first, honesty-guarded).
- Application assets (local, not deployed): SentiLink resume (existing) + cover (new); Mercury resume (new)
  + cover (new).
- Ledger: `_ARTIFACTS/pitch-portfolio-ledger.md`. Seed: `seed-arch-pitch-us-bundle-ziggurat`.
