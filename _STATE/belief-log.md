# ARCS — Belief-Change Log

> The corpus record of what we believed, the test that overturned it, and what replaced it.
> One field, one SSOT: **generated from `_STATE/falsification-ledger.jsonl`** by
> `scripts/belief_log_emit.py`. Do not hand-edit — append to the ledger and regenerate.

**48 beliefs overturned** · 20 promoted to canon · span 2026-06-03 → 2026-11-05

By scope: infra 12 · canon 11 · process 10 · gauntlet 5 · deploy 4 · surface 3 · security 2 · recoil 1

---

## This week — spotlight (2026-10-30 → 2026-11-05)

The reversals that went most against the grain this week:

### F48 · 2026-11-05 · `infra`
- **Held:** F47 (2026-11-04): 2 of the 5 outside users were never emailed although their check-in dates had passed.
- **Test:** Read-only prod query on 2026-11-05, per outside user: each receipt's reminderDate, debriefSentAt and the user's firstDebriefSentAt.
- **FALSIFIED →** Corrects F47. Of the two: one user's only check-in is 2026-12-31, not yet due, so no email is correct behavior. The other had debriefs scheduled for all 3 receipts on 2026-06-25, the day the receipts were made, but User.firstDebriefSentAt was never set, so 'ever emailed' read false. Debriefs were scheduled for 6 receipts across 4 users, and no user whose check-in came due was skipped. Whether the 6 were delivered is unrecorded, because debriefSentAt is stamped at scheduling (gauntlet G7). F47 read one flag as delivery and never checked the dates.
- **Now:** Treat 'emailed' as unknown until delivery is recorded; count by reminderDate, never by firstDebriefSentAt. The journey map gauntlet (G1, G2) and the interview script are corrected. Still open: why firstDebriefSentAt was not set for the June sends, and why one check-in fell on the day the receipt was made.
- _refs: src/app/api/compass/route.ts, src/app/api/cron/debrief/route.ts, prisma/schema.prisma, belief log F47 · confidence: high_

### F47 · 2026-11-04 · `infra`
- **Held:** The debrief email reaches every saved receipt's owner once its check-in date passes (the debrief cron and the compass-time send both exist).
- **Test:** Read-only prod query on 2026-11-04 over the 11 receipts from the 5 outside users: check-in dates passed, Receipt.debriefSentAt, User.firstDebriefSentAt, User.debriefOptIn.
- **FALSIFIED →** 10 of 11 check-ins have passed, but debrief emails were sent for 6 receipts, to 3 of the 5 people; 2 people were never emailed at all. 0 of 5 opted in to repeat reminders, so by design each person is asked about one receipt at most. None of the 6 emails produced an outcome. The cause of the 2 never-emailed people is open: the cron is declared in vercel.json, but its run logs were not checked.
- **Now:** Check the cron's runs and the two users' rows before the five-person test. The journey map now names the opt-in (step 07) and makes calling the five who already tried ARCS the first step of the build order. Found by the journey map gauntlet (G1, G2, G4).
- _refs: src/app/api/cron/debrief/route.ts, src/app/api/compass/route.ts, vercel.json, prisma/schema.prisma · confidence: medium_

### F46 · 2026-11-04 · `surface`
- **Held:** Striking an unsupported claim from canon removes it from every served page (the Oct 17 strike, PR 1518, covered every 87% accuracy, expert-comparison and network-effect claim).
- **Test:** For each eval row on public/status.html, open the paper section it cites and check whether the claim is still there (2026-11-04).
- **FALSIFIED →** Four of six eval rows cited sections struck on Oct 17 (YellowPaper §2.4 three times, §6.2 once) and still read NOT RUN, as if the claims were live and awaiting a test; three Archaeology chips repeated them. The strike changed the papers, not the pages that cite them. Separately, WhitePaper v2.1 §2.1 still claims 78% cascade prediction and +35% ROAS, the same class of unsupported number the strike removed elsewhere.
- **Now:** Rows relabeled STRUCK with the date and kept visible; the section intro says why; chips marked struck. The WhitePaper §2.1 claims are left for Zach to rule on (a canon change).
- _refs: public/status.html, _CANON/ARCS-YellowPaper.md, _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md, receipt 2026-10-17--strike-unsupported-canon-claims-pr1518--ZH · confidence: high_

### F45 · 2026-11-04 · `process`
- **Held:** Outcome rows are mostly synthetic plumbing probes, so no real outcome has ever been logged (said in this session, from a schema comment).
- **Test:** Same prod query as F43: Outcome rows split by the synthetic flag.
- **FALSIFIED →** 5 of 10 Outcome rows are real. The narrower true statement: no outside person has logged one. A schema comment described the flag, not the data; the claim was made without reading the rows.
- **Now:** Count rows before characterizing them. The session's recommendation stands on the narrower fact (0 outside outcomes).
- _refs: prisma/schema.prisma · confidence: high_

### F44 · 2026-11-04 · `infra`
- **Held:** The eight track() calls in the app (compass_run, receipt_save_*, brief_*) are live funnel events we can measure the journey with (journey map draft 2, this session).
- **Test:** Read the receipts and handoff that queried Vercel: count_events and aggregate_events on project arcs-v9 returned 404 'Web Analytics not found' on 2026-09-27, and the analytics query API returned the same 404 on 2026-10-27.
- **FALSIFIED →** The calls exist in code but Web Analytics is not enabled on arcs-v9, so every event is dropped. A track() call in the code proves an event is sent, not that it is recorded. The journey map's measurement plan already counted from the database first; its 'live' label for events was wrong.
- **Now:** Journey map relabels the eight events 'in code, not recorded' and makes enabling Web Analytics (and confirming one event lands) step zero of measurement. No new events until one existing event is seen in the dashboard.
- _refs: src/app/dashboard/page.tsx, src/app/receipt/[receiptId]/page.tsx, receipt 2026-09-28--receipt-save-nudge-v11-flag-merge--ZH, CLAUDE.md handoff v3.142.0 (Vercel 404) · confidence: medium_

### F43 · 2026-11-04 · `surface`
- **Held:** The evidence base the gated features wait for builds itself through normal use: every decision and its outcome accumulates calibration data automatically (status.arcs.care, Roadmap and Risk Register).
- **Test:** Read-only prod query on 2026-11-04 (Supabase ARCS_v9): count Outcome rows with synthetic = false and the distinct people behind them, against the outcome loop shipping on Day 98.
- **FALSIFIED →** About 110 days after the outcome loop shipped: 10 Outcome rows, 5 real, all 5 from one person, last logged 2026-10-25. 8 users, 6 with real receipts, 2 active in the last 30 days. The page's own counter reads 0 of 30 closed outcomes from outside users. Nothing built itself: the loop records outcomes only when someone is asked, and no outside person has answered.
- **Now:** Reword the two status lines from 'builds itself' to what is true (outcomes are logged only when a debrief is answered; 0 outside so far). Make the outcome loop the next build (receipt stub, check-in tracker, outcome on the receipt) and run the five-person test before any gated feature.
- _refs: public/status.html, prisma/schema.prisma (Outcome.synthetic), src/app/debrief/[receiptId]/page.tsx, receipt 2026-09-27--op19-accountant-bind-and-scoreboard-merge--ZH · confidence: high_

---

## Full ledger — newest first

| id | date | scope | canon | belief that broke → what replaced it |
|----|------|-------|-------|--------------------------------------|
| F48 | 2026-11-05 | infra | — | **F47 (2026-11-04): 2 of the 5 outside users were never emailed although their check-in dates had passed** → Treat 'emailed' as unknown until delivery is recorded; count by reminderDate, never by firstDebriefSentAt |
| F47 | 2026-11-04 | infra | — | **The debrief email reaches every saved receipt's owner once its check-in date passes (the debrief cron and the compass-time send both exist)** → Check the cron's runs and the two users' rows before the five-person test |
| F46 | 2026-11-04 | surface | — | **Striking an unsupported claim from canon removes it from every served page (the Oct 17 strike, PR 1518, covered every 87% accuracy, expert-comparison and…** → Rows relabeled STRUCK with the date and kept visible; the section intro says why; chips marked struck |
| F45 | 2026-11-04 | process | — | **Outcome rows are mostly synthetic plumbing probes, so no real outcome has ever been logged (said in this session, from a schema comment)** → Count rows before characterizing them |
| F44 | 2026-11-04 | infra | — | **The eight track() calls in the app (compass_run, receipt_save_*, brief_*) are live funnel events we can measure the journey with (journey map draft 2, this…** → Journey map relabels the eight events 'in code, not recorded' and makes enabling Web Analytics (and confirming one event lands) step zero of measurement |
| F43 | 2026-11-04 | surface | — | **The evidence base the gated features wait for builds itself through normal use: every decision and its outcome accumulates calibration data automatically…** → Reword the two status lines from 'builds itself' to what is true (outcomes are logged only when a debrief is answered; 0 outside so far) |
| F42 | 2026-09-29 | surface | — | **status.arcs.care/beliefs serves the public belief log, so the audit page's belief-log link works (verified by HTTP 200 before linking, #591)** → Catch-all lookahead widened to belief\|gauntlet (#650) |
| F40 | 2026-09-27 | canon | ✓ | **External audit (Perplexity, 'Job to Be Done.md'): Operators 1-19 mapped to repo files with 'Full Production' / 'Production Code' status, e.g** → Numbering LOCKED to the periodic table (AGENTS.md gotcha 16); registry generated and grep-verified; altitude canary + integrity gate pair for this class… |
| F39 | 2026-09-27 | infra | — | **Operator 21 (Librarian) binds to ARCSStore.query as its entrypoint** → operators/OPERATOR-REGISTRY.json generated only from grep-verified bindings; --check on pre-commit |
| F38 | 2026-09-27 | process | — | **'Live evidence this session shows the memory index clipped': the auto-loaded MEMORY.md ending at the consolidation stamp proved the harness truncates at ~24KB** → Corrected in-thread within one turn; memory [[memory-index-load-cap-observed]] carries the measured number; MEM_BUDGET guidance set to 24576 |
| F41 | 2026-09-26 | canon | ✓ | **F34's 'Now' fix is scoped but unbuilt, so the Orthogonal Echo Detector (ROM Primitive #5) remains architecturally blind on its stub matcher and keeps failing…** → signature_fn + orthogonality_fn made real and injectable with honest deterministic offline fixtures (make_llm_signature_fn / make_embedding_orthogonality_fn)… |
| F34 | 2026-08-29 | canon | ✓ | **The Orthogonal Echo Detector (ROM Primitive #5) works — it reliably surfaces true cross-domain kinematic isomorphisms and can be trusted as the immune guard…** → Replace stub with injectable LLM signature_fn + embedding orthogonality_fn; RC-OPS-001 graduation HELD on measured precision failure (target adv-FP<=0.10 @… |
| F37 | 2026-08-28 | process | ✓ | **The ADR-number collisions (033/067 each doubled) are caused by worktree sprawl / branches borrowing each other's numbers** → Oracle-first numbering as a git-backed logical clock (git non-fast-forward reject = the atomic lock); pre-commit hook rejects any duplicate ADR number… |
| F36 | 2026-08-28 | infra | — | **Operator-20 (folksonomy cultivator) has an import bug and is starved of real receipts — it is gated vaporware** → operators/prod_receipt_to_op20_seed.py adapter landed (never fabricates somatic/axiom fields) |
| F35 | 2026-08-27 | canon | ✓ | **The legacy / pre-v9 repos hold high-value net-new ROM primitives waiting to be recovered into arcs-v9 canon — mine them for lost wisdom** → Reframe the work from discovery to canonization hygiene: number the de-facto axioms, consolidate divergent schema copies, escalate the 3 colliding… |
| F33 | 2026-08-16 | process | — | **The single-mind kintsugi repair (gate=witnessed-provenance, rank=impact) had hardened the milestone-ranking plan to anti-fragile** → invert — promote external-corroboration from sort-key to GATE (renderer refuses to publish any milestone lacking a reviewer-clickable proof the author does not… |
| F4 | 2026-08-15 | gauntlet | ✓ | **The 0.50 flip rate is surrogate interpolation NOISE — a denser mesh will lower it** → it's a MODEL-TIER recall/precision gap (Haiku hot vs Sonnet strict), not noise; tau-calibration now splits flips by direction (up=recall hole -> act… |
| F32 | 2026-08-14 | process | ✓ | **A counterpart-gauntlet reliably identifies real defects in the artifact it audits** → ADR-061: verify every flag vs the full primary source before applying; reject + LOG over-flags; never blind-apply a prescribed fix; deterministic… |
| F9 | 2026-08-13 | canon | ✓ | **The hypercube's 5 axes are orthogonal, supporting a clean 3,125-cell count** → flagged MED as the cheapest real next falsifier (check axes against WORLD.md's render table); not yet resolved |
| F8 | 2026-08-13 | canon | ✓ | **The EM/physics frame (penteract, field dynamics) is literally true of the mechanism** → standing correction: not citable as evidence until it yields one surprising checkable prediction |
| F7 | 2026-08-13 | canon | ✓ | **'Float, not drift' is a safe self-applied exemption for the H-ladder — no boundary needed** → §1.5 rewritten with a mechanical boundary: float is legit only along an ex-ante-declared ladder; auditor flags regardless |
| F6 | 2026-08-13 | canon | ✓ | **The Hypercube Gauntlet ADR (055/060) is GREEN.HIGH.STABLE — verified doctrine** → Y downgraded; a self-audit receipt attached; prior GREEN rested on confirmation signals the ADR's own rule demotes |
| F5 | 2026-08-13 | gauntlet | ✓ | **A single-agent graded pass reads faults on an absolute 0-3 severity scale** → switched to top-K / relative selection; validated the ~10x-cheaper coarse->fine division of labor |
| F3 | 2026-08-13 | gauntlet | ✓ | **The empirical cost model is complete** → each spawn RE-READS the subject; added CostModel.subject_read_tokens (the prompt-caching lever) |
| F2 | 2026-08-13 | gauntlet | ✓ | **An absolute value-of-information threshold (uncertainty x stakes > tau) routes coarse -> fine** → escalation set = union of two BOUNDED top-Ks (severity + VoI) + irreversible + eps; 380 -> 24 |
| F12 | 2026-08-13 | canon | ✓ | **ADR numbers are unique, stable identifiers referenced unambiguously across the corpus** → per-collision human ratification; movers draw from scripts/oracle.py (the git-backed number authority); nothing auto-applied |
| F1 | 2026-08-13 | gauntlet | — | **Tight prompts + small inputs = cheap; gauntlet cost scales with data size** → the ~54K/subagent FLOOR dominates; agent-COUNT, not prompt size, is the cost driver; dropped binary refute-by-default for graded severity |
| F25 | 2026-08-01 | process | — | **Content probes (grep/curl) are sufficient to claim a UI is polished and verified** → screenshot locally before any push with visual effect; state the verification method rather than claiming 'polished' unqualified |
| F21 | 2026-08-01 | deploy | ✓ | **The dashboard ignored-build-step field is a stable, reviewable cost guardrail** → moved to a checked-in scripts/vercel-ignore-build.sh (ADR-039), versioned, dry-run-verified, `.claude/` excluded |
| F18 | 2026-08-01 | infra | — | **A new Postgres role with GRANT SELECT ON ALL TABLES can see the data it was granted** → verify new roles against the bypass-RLS app role on a table with known data; re-verify writes stay blocked separately |
| F20 | 2026-07-25 | deploy | ✓ | **The arcs-v9 Vercel Ignored Build Step correctly skips docs-only commits and builds real code** → removed the `!`; later moved the whole guard into a checked-in, dry-run-verified script (ADR-039); verify Ready vs Canceled after every push |
| F26 | 2026-07-24 | process | — | **`gh pr checks --watch && gh pr merge` is a sufficient merge gate** → assert every check's conclusion (json state,conclusion; fail on any 'failure') between watch and merge — this discipline IS the only gate on free-tier private… |
| F19 | 2026-07-24 | infra | — | **A Vercel MCP get_web_analytics 404 means Web Analytics is not enabled** → never conclude 'not enabled' from an MCP 404; check the dashboard directly |
| F24 | 2026-07-22 | process | — | **A control described in canon (Drift Sentinel, claims-skeptic) is an active safeguard** → treat canon-described-but-unwired controls as advisory; the fix is a wired hook or human trigger, not a self-applied rule |
| F30 | 2026-07-19 | security | — | **A scheduled Sentinel task with all 13 MCP connectors costs little because it runs on a schedule** → strip to core file tools, no MCP, Haiku for git-log parsing, report-only (no Write/Edit) |
| F29 | 2026-07-19 | security | — | **Password-gated subdomains keep their sensitive HTML confidential** → treat gated pages as not confidential while the repo is public; move sensitive dossiers to a private repo |
| F27 | 2026-07-19 | process | — | **CLAUDE.md's append-only handoff policy keeps context cheap and history preserved** → relocate dead handoffs to _ARCHIVE (not delete); keep the latest 1-2 live; policy amended to 'working file, kept lean' |
| F17 | 2026-07-19 | infra | — | **CLAUDE.md's project table accurately reflects which repo serves a live domain** → always run get_deployment(domain) (+ get_project live flag) before stating which repo serves a domain |
| F22 | 2026-07-17 | deploy | — | **preview_start renders the branch/edits of the current session's worktree** → confirm server cwd (lsof) before trusting browser verification; use a launch config that cds into the correct worktree |
| F31 | 2026-07-13 | recoil | — | **The Todd Hotes pilot-court receipt's premise (11 days of cold silence) was accurate** → premise marked FALSIFIED with evidence; write-lock MOOT; receipt voided, no discount/decision-window ask |
| F28 | 2026-06-24 | process | — | **Confident time-framing ('it's late, wind down') tracks the real current time** → run `date` and ground any time-dependent framing before asserting urgency or hour |
| F10 | 2026-06-23 | canon | ✓ | **BAR and KKL are single unambiguous canonical terms shared across ADR-020 and arcs-canon** → ADR-020 enum relabeled 'risk tier'; timing triad renamed KKL->KLC; collision resolved CONDITIONAL CLEAR |
| F23 | 2026-06-22 | deploy | ✓ | **The debrief-delivery gap was a missing in-app fallback surface (ADR-059 framing)** → ADR-059 amended same-day; split into ADR-026 as a delivery-timing fix; timezone bug corrected |
| F11 | 2026-06-20 | canon | ✓ | **ADR-011's Turbopack tree-shaking claim was confirmed — mark it GREEN** → Y corrected down to MEDIUM/REVISIT |
| F13 | 2026-06-19 | infra | — | **A synchronous Haiku-calls-Opus advisor tool in the compass route is real-time-safe** → reverted the advisor; restored MODEL_MAP routing; kept the prompt-caching beta (~90% cost cut) as the surviving win |
| F16 | 2026-06-03 | infra | — | **`vercel deploy --prod` from a local tree is equivalent to a normal deploy** → never `vercel deploy` from a local tree; git push and verify the log says 'Cloning' |
| F15 | 2026-06-03 | infra | — | **The SQLite dev schema and the Postgres prod schema are equivalent** → on a silent Auth.js failure, check Postgres logs immediately for a PrismaAdapter column gap |
| F14 | 2026-06-03 | infra | — | **A green Next.js production build means the database layer works** → explicit Pool + PrismaPg with SSL; run a real query against prod before calling the DB layer 'working' |

---
_Regenerated by `scripts/belief_log_emit.py` · 48 entries · do not hand-edit — the ledger is the SSOT._
