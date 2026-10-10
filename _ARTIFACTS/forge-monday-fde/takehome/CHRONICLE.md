# monday FDE take-home: forensic chronicle, first prompt to now

> **WRITE-LOCKED 2026-10-10 ~15:00 ET.** Append-only. Corrections go in a dated `## Amendment` block at the end, never by
> editing a line above. SHA-256 of this file at lock time is recorded in `MANIFEST.json`.
> PRIVATE: contains pre-work and interview context (grade E items). Never copy into `~/ret-rfp-intelligence`.

**Sources (how each line was established):**
- your turns: both session transcripts (`33458036`, `43abdc60`), timestamps converted UTC to ET (UTC−4)
- the take-home repo's git log, `KINTSUGI.md` (K1-K41) and `DECISIONS.md`
- memory `project_monday_fde_strategic_deployments`
- `git log origin/main -- _ARTIFACTS/forge-monday-fde`

A time given as "~" is inferred from neighbouring events, not recorded. Grades: A client docs · B measured · C cited third-party · D inference · E recollection.

## Single sources of truth (who owns which truth)
| Truth | Owner | Not this |
|---|---|---|
| Build state, plan, rules, next action | `~/ret-rfp-intelligence/HANDOFF.md` + `python3 scripts/plan.py` | this file |
| Own mistakes, repairs, direction changes | `~/ret-rfp-intelligence/KINTSUGI.md` | chat |
| Decisions + rejected alternatives | `~/ret-rfp-intelligence/DECISIONS.md` | chat |
| Every shown number | `~/ret-rfp-intelligence/evidence/evidence.jsonl` (rendered by the one-source generator, K35) | slides, prose |
| Private history, pre-work, interview context | **this file** + memory `project_monday_fde_strategic_deployments` | the take-home repo (leak gate) |
| Visual map | `atlas.json` (arcs.atlas.v1) → Atlas Loader HUD at jobs.arcs.care/atlas | |
| Writer | ONE session ("Continue monday take-home from HANDOFF.md"); all others read-only | |

## Phase 0: Pre-work (before the brief)
- 10-05 → 10-06: the resume forge restyles and ATS-companions all tailored resumes, including the monday FDE cut (`_ARTIFACTS/forge-monday-fde/`: JD, tailor notes, red-team, hiring-manager file). Grade B (git).
- Red-team claim hygiene: arcs-v9 is private, and MCP is a private tool layer, so never imply a public repo or a production connector. Grade B (red-team.md).
- 10-07: recruiter screen. 10-08: hiring-manager call with Stefan (Head of Strategic FDE). He challenged builder credibility, and showing live public proof is what landed. He's building FDE from scratch (team of ~5) and is open to local models; Zach joked about running Qwen locally. Grade E (Zach's account).
- Comp band: lives in memory only, never in any repo.

## Phase 1: Kickoff (Sat 10-10, 10:04-10:31 ET)
- 10:04 `/handoff-pickup`. 10:06 Zach drops the brief PDF. 10:10 asks for an experiment wrapper ("blackbox flight recorder", belief before/after, rubric, unit economics).
- 10:11 repo scaffolded (flight recorder, rubrics, constraints gate). 10:15 "highest burden of proof"; recall the pre-work. 10:16 Qwen joke surfaces; 10:18 Qwen approved "after core passes".
- 10:19-10:24 disk full: caches A and B freed (4.5 to 19 GiB). 10:24 data: the RFP package, verbatim. 10:25 core pipeline go; TypeSafe skill install.
- **10:31 first working core: ingest, amendment resolver, cited answers, golden eval 18/18.** Built 10:11 to 10:31 by git time, ~20 min.

## Phase 2: Proving it's honest (10:31-11:00)
- 10:31 Zach: every time a test is wrong, document the seam and its repair as a core principle. Birth of KINTSUGI.
- 10:41 K9: fuzz shows 143/30,000 failures; the harness was wrong, not the system.
- 10:45 K10: estimated build time ran ~3x high vs git; time is measured from git from here on.
- 10:46-10:48 Comet browser: the assessment workspace, plus the full briefing video (the video names the four grading lenses: ambiguity, trade-offs, use of data, clarity).
- 10:53-10:57 unit economics. **K13: Zach asks "are you pulling these numbers out your ass", which creates the global rule that every number is measured, cited, client-provided, derived with inputs shown, or a placeholder.** K14: a price typed from memory is corrected to the cited $2/$10.
- 10:54 framing: "POC mashup ... global minimum water line" (lean, cheap, field-truth grounded).

## Phase 3: Landing in monday (11:00-12:10)
- 11:02-11:03 orchestration question; needs and approvals list; build status dashboard asked for (pinned artifact).
- 11:11 the artifact doubles as the monday wireframe. 11:18 dynamic inputs as parameterized e2e variables.
- 11:30 walkthrough + provenance; Zach emails the recruiter (Sam Turner) to ask for a higher tier. 11:32 `moves_metric` field added.
- 11:36-11:41 token: a one-shot CLI to write .env; a malformed second token line gives 401, so the client now refuses duplicate or malformed tokens. 11:39 the playground link; 11:42 API analytics (Enterprise-gated).
- **11:43 "go boards": live boards on assessment-lab-assignment.monday.com.** 11:48 anticipatory objections lead to wave-2 evals.

## Phase 4: Grading yourself, cutting, the deck (12:10-13:00)
- 12:10 line-by-line rubric (snapshots/T+2h.md). 12:11 commits shown but not linked. 12:12 bundle limits and hard constraints re-checked (E1-E8).
- 12:15-12:20 a recoil of the video ("what resonates with Stefan") leads to options A then A+B. 12:21 Kimi benchmark question.
- 12:31 an impeccable drift check against the brief. **12:35 D-600: testing a 600-page PJM document is NOT required; it becomes a Q&A point.** Correction of my own premise.
- 12:37 slides, a SAM.gov search, the deck started. 12:41 STAR / SARI framing, which becomes STAR-I. 12:42 status check + OSS borrow sweep.
- 12:54-12:56 pinned status artifact; the chips-not-hovering bug; two safety-classifier stops.
- 12:57 Pilot Scorecard board. 13:00 **Zach builds the native monday dashboard by hand.** 13:01 the monday Models API doc gives 403 insufficient_credits on the free tier (B).
- Fast path (exact key facts, no model call) and `./rfp` CLI land around 12:51-13:01 (git).

## Phase 5: Fold and handoff (13:07-13:20)
- 13:07-13:10 HANDOFF.md becomes the SSOT: execution plan by waves and clusters, the cold-start kit. 13:08-13:11 Zach asks for clustered JTBD, batchability, the explicit tool inventory, and the rubric, self-eval and pre-kickoff research passed along.
- **13:13 collision: two sessions in one working tree; my commit is blocked by the other's staged provider.py.** Zach: "focus on global serializability", which sets the **SINGLE-WRITER rule**; this session goes read-only.
- 13:14 K34 history rewrite approved. 13:15 K33 fixed (W10 deterministic). 13:21 K34: history scrubbed, 0 leak matches, force-pushed.

## Phase 6: Relay era (13:15-14:50)
This session read-only; the writer shipped. Relays sent ≈ 25; my own turns were mostly "check again".
- Writer shipped:
  - Evals tab, filters and rubric (13:41-13:46)
  - jobs-to-be-done map (13:53)
  - **K35: one-source generator, nothing shown is typed by hand, staleness fails the build** (13:57)
  - **K36: localhost server hardening, Host/Origin, 9 attack tests** (14:05)
  - brief-reread reflection + T+4h re-grade (14:11)
  - war game, 15/15 live (K38, 14:18-14:23)
  - Brier calibration log (14:26)
  - risk table (14:27)
  - D-SCOPE (14:32)
  - Vibe styling (14:36)
  - overflow gate (14:43)
  - pre-registered estimates (14:49)
- Writer pushed back: **D-LAYOUT rejected my "one column per area" relay** (one reading column, not five lanes). Relayed specs were corrected twice: "never silently overwrite" is not built, and Playback was cut.
- I ran a 4-persona gauntlet on the dashboards spec (~200k tokens; ~3x over the cheapest adequate tool; logged as a cost seam). Live finding: one persona read only the base RFP and quoted Nov 13 instead of Dec 4, the exact stale-fact failure the system prevents.

## Phase 7: Subtraction (14:49-15:00)
- **14:51 Zach confirms D-SCOPE was his call: "focus on rehearsal".** My seam: I relayed ~10 features without weighing them against the brief. Banked as memory `relay-scope-check-against-brief-before-forwarding`.
- 14:52 shavasana: load-bearing vs ornamental. **14:54 D-SUBTRACT lands** (teardown and extra scanners cut, Present mode deferred, three proposals folded into one line).
- 14:55 this chronicle; write lock requested. 14:56 visualize via the HUD explorer.

## Turning points (the vector changes)
| # | When (ET) | Twist | Heading after |
|---|---|---|---|
| 1 | 10:31 | Tests can be wrong | KINTSUGI as a first-class log (K1-K41) |
| 2 | ~10:55 | "Numbers out your ass" (K13) | Global provenance rule, lint-enforced |
| 3 | 12:35 | PJM not required (D-600) | Scope to the brief, not to imagination |
| 4 | 13:00 | Zach hand-builds the native dashboard | monday-native is the deliverable surface |
| 5 | 13:13 | Session collision | Single writer; relay by message |
| 6 | 13:21 | History leak (K34) | Gates scan everything that ships |
| 7 | 13:57 | Hand-typed figures drifted (K35) | One source renders everything |
| 8 | 14:05 | Localhost CSRF (K36) | Security proven by attack tests |
| 9 | 14:32 | Bar-raiser over-build estimate (D-SCOPE) | Modest build that proves you listened |
| 10 | 14:54 | D-SUBTRACT | Rehearsal, then submit |

## Where it stands at lock
- Repo `~/ret-rfp-intelligence`: 92 commits, CI green on the latest, K1-K41 logged, decisions D-600 … D-SUBTRACT.
- Next: **rehearsal ×2 from a clean database (Zach)**, then the D-SUBTRACT pass, the T+N snapshot, `scripts/package.py`, and the upload by Thu 10-15 17:00 ET.
- Open for Zach: rehearsal; the recruiter's tier reply; licence (none vs "All rights reserved").
