# Scope: target-role scan as data (execute after 19:00 ET 2026-09-04)

Status: SCOPED, not started. Owner: this session's forge watcher. No agents until the spend limit clears; all three steps are deterministic and run in the main session.

## Why
`_ARTIFACTS/target-role-scan-hud.html` already holds the mapping layer between a JD and Zach: four archetypes with proof points, four differentiators (A AI-native builder, B forward-deployed operator, C product x GTM breadth, D regulated fluency), the screen-in / screen-out filter, the eight-dimension rubric with gates and bands, and the wired loop. Today that content is copied in three places (the HUD, the scorer prompt in the scheduled task, the board's embedded DIMS table) and two facts on the HUD are stale (ingest "unwired"; pursue band 0.70 vs the board's 0.58 with three tiers). Make the scan the single source and let the forge, the resume tailor, and the cover letter read it.

## Step 1: extract the scan to JSON (30 min, no LLM)
Write `runtime/specs/target-role-scan.json`:
```
{ "version": "1.1", "source": "_ARTIFACTS/target-role-scan-hud.html",
  "archetypes": [ {id, title, rail, lead_proof: {company, claim, evidence_grade}, titles: []} x4 ],
  "quads":      [ {id: "A"|"B"|"C"|"D", label, headline, proof: {company, claim}, dims: [rubric dims that load on it]} x4 ],
  "fit":        { "screen_in": [...6], "screen_out": [...6] },
  "rubric":     { "dims": [ {key, label, weight, anchor0, anchor3} x8 ], "max": 72,
                  "gates": [...4], "bands": {pursue: 0.70, consider: 0.50}, "board_cutoff": 0.58,
                  "tiers": {t1: 0.80, t2: 0.70, t3: 0.58} } }
```
Quad-to-dimension loading (the mapping the forge page uses): A <- ai_native; B <- role_shape, scope_authority; C <- comp_level (level), strength_leverage (breadth); D <- strength_leverage (regulated), culture. Record it in the file, not in code.
Then: the board's `DIMS` array and `anatomy()` read this file (embed at publish time, one copy), and the scheduled task's Step 3 cites it instead of restating the rubric.

## Step 2: scorer emits `jd_hits` (small change to the scoring prompt)
For each scored row add `jd_hits: { A: [quoted JD sentence], B: [...], C: [...], D: [...] }` with only sentences actually present in the JD (empty list is allowed and honest). This is the evidence the forge page and cover letter quote. Backfill for the 13 board rows on the next scoring pass; the four parked forges get it from their saved JD text (`jd-full.txt`, `jd-ashby-fde.txt`, etc.).

## Step 3: consumers
- Forge page "why this role": the two or three quads with the highest weighted contribution for that row, each as the scan's thread-rail block: quad headline, the JD sentence it answers (from jd_hits), the proof point. Public version carries NO scores, bands, or rubric words (air-gap). Base grammar stays blacksmith.html.
- Resume cut lead rule: the archetype the row was surfaced under (alert_query -> archetype id) decides which proof point leads. Replaces the per-agent judgment Trinity's tailor notes made by hand.
- Cover letter: top two quads by contribution, one paragraph each from the proof point, close on the archetype line. Voice tuned from Zach's own LinkedIn export (Shares / Comments / Recommendations) per the resume-tailor voice memory; needs the export ZIP dropped at `_INBOX/linkedin-export.zip` (parser: `operators/linkedin_pipeline/linkedin_export.py`). Until it exists, cover letters use the general register and say so in TAILOR-NOTES.
- Fix the HUD's two stale facts (ingest status light; band copy) from the JSON, not by hand.

## Not in scope
Hosting the scan as a public subpage (it is the internal instrument; if ever served, behind the recoil passcode gate). Re-weighting the rubric (a separate, human-judged change).

## Done when
`target-role-scan.json` exists and is cited by board, scheduled task, and forge prompts; 13 rows carry jd_hits; the four forge pages render "why this role" from it; HUD stale facts fixed; one docs-only PR.
