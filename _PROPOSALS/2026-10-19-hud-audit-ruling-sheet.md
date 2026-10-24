# HUD audit: ruling sheet (D1 to D5, plus one confirmation)

For Zach. One answer here releases the backlog row `hud-proposals-ruling` (BLOCKED) and, through it, 9 downstream HUD rows by the backlog graph (the control tower's queue says 11; I count 9 through `depends_on` and `unblocks`). Source: `_PROPOSALS/2026-10-15-hud-moire-audit.json` and `_PROPOSALS/2026-10-15-hud-widget-lockups-spec.md`.

**How to answer:** reply "all as recommended", or give only the ones you change, for example "D1 hold, D3 revise". Nothing below is built on an unanswered line.

## C0. Confirm first: what are "widgets 1 to 5"?
- **Assumed:** the five gauges (fidelity, conviction, clarity, coherence, consonance).
- **Alternatives:** controls C1 to C5 of the audit, or decisions D1 to D5.
- **If you confirm:** the widget spec and the registry row go ahead as written. **If not:** only the widget table in the spec changes.

## The five decisions

| # | The question | Recommended | Status today | Releases | If you say no |
|---|---|---|---|---|---|
| D1 | Build the echo overlap strip, admin-only first? | **Approve admin-only.** Build-time JSON from the existing detector, shown in the HUD side panel behind the ziggurat loader's admin check. Public only after one real echo survives the template control. | Not built. The last measured run (2026-09-27) found 0 real echoes, so the strip would show flat lines and "0 real echoes". | `hud-echo-overlap-strip-admin` | Hold: no moire from echo data; the HUD keeps its decorative ripples only. |
| D2 | Label the waypoint ripples as illustrative? | **Yes.** One line: "Ripples mark roadmap waypoints, not data." | Not built. | `hud-ripples-illustrative-label` (then `hud-failcloser-gate`) | Leave as is: the ripples keep reading as measurement. |
| D3 | Merge clarity and coherence at the question level, and redefine consonance? | **Yes.** Keep the clarity lens, retire `coherence_pct` as a separate gauge, keep the HUD's coherence as a lattice property under its own name, define consonance as the gap between stated confidence and closed outcomes at n of 30 or more. | **Partly done:** the HUD rows already read "Clarity · lattice", "Coherence · lattice", "Consonance · invariants" (PR 1473). The merge and the new consonance definition are not built. | `hud-conviction-consonance-readings` | Keep five gauges: two names keep meaning two different quantities. |
| D4 | Drive per-node grain from evidence counts? | **Yes, as a second step.** Node uncertainty is 1 minus min(1, evidence / 10), with evidence = mapped files plus commits in the last 28 days, both already in `universe-field.json`. | Not built; no backlog row yet (I would add one on approval). The epic `hud-high-signal-field` also says "grain", but that is the grain of each gauge's reading, not D4's per-lattice-node grain. | Zoom shows less certainty where little is known | Hold: fog stays a user dial, not evidence. |
| D5 | Fix the L3 label drift (canon says cascade; the compass prompt runs the Kintsugi immune check)? | **Fix the doc, not the prompt.** | **Done:** CLAUDE.md now says so (PR 1473). Only the option "also rename the prompt layer" remains, and I recommend no. | Nothing waits on it | Reopen: say which side should change. |

## What your answers cost and gate
- **Cost of the recommended set:** D2 and D3 are label and definition work; D1 and D4 need the widget registry and views first (they sit behind `hud-widget-registry-tier0` and `hud-widget-views-admin-mount`). Nothing here touches the compass pipeline.
- **Order the rows then run:** registry (Tier 0, no model) then views and admin mount, then the echo strip, flow gauges, conviction and consonance readings, the fail-closer gate, and the cold-read acceptance test. The ruling is the only thing blocking the first three.
- **Pre-registered tests stay fixed:** the echo strip's known-bad (scrambled controls and the shared-template fixture render amplitude 0) and known-good (a synthetic planted pair) are in the audit; they are not renegotiated by a ruling.

## What I did not verify
- The 9-versus-11 count: I did not find the two rows the tower counts that the graph does not.
- Whether the HUD's public page should get the D2 label before any other work: that is your call, and it is the cheapest of the five.
- The echo detector's current result: the "0 real echoes" figure is from the 2026-09-27 run and was not refreshed.
