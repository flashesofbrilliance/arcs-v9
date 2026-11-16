# ARCS — Belief-Change Log

> The corpus record of what I believed, the test that overturned it, and what replaced it.
> One field, one SSOT: **generated from `_STATE/falsification-ledger.jsonl`** by
> `scripts/belief_log_emit.py`. Do not hand-edit — append to the ledger and regenerate.

**51 beliefs overturned** · 20 promoted to canon · span 2026-06-03 → 2026-11-16

By scope: infra 12 · canon 11 · process 11 · gauntlet 5 · surface 5 · deploy 4 · security 2 · recoil 1

---

## This week — spotlight (2026-11-10 → 2026-11-16)

The reversals that went most against the grain this week:

### F49 · 2026-11-16 · `surface`
- **Held:** The public counts stay current on every surface that shows them, because status.arcs.care stamps its floor from git.
- **Test:** On 2026-11-16, compared the commit and PR figures on status.arcs.care, zach.md, the proof ledger and the resume with app.arcs.care/api/pulse (commitsTotal 7,133) and the GitHub merged-PR count (1,993).
- **FALSIFIED →** Only the status floor has a stamping script. zach.md said 6,809 commits, the proof ledger 6,800+, the resume 6,300+ from Nov 9. The status page's own milestones stopped at Day 173 while its header read Day 217, and its "shows 13 milestones" line had drifted to 19.
- **Now:** PR 2312 brings every surface to 7,133 commits and 1,993 PRs as of 2026-11-16 and adds Days 194 to 218 to the milestones. Still open: one shared count source, or a check that fails when the surfaces disagree.
- _refs: PR 2312, scripts/status_floor_emit.py, _ARTIFACTS/status/explorer.js, app.arcs.care/api/pulse · confidence: high_

---

## Full ledger — newest first

| id | date | scope | canon | belief that broke → what replaced it |
|----|------|-------|-------|--------------------------------------|
| F49 | 2026-11-16 | surface | — | **The public counts stay current on every surface that shows them, because status.arcs.care stamps its floor from git** → PR 2312 brings every surface to 7,133 commits and 1,993 PRs as of 2026-11-16 and adds Days 194 to 218 to the milestones |
| F51 | 2026-11-09 | process | — | **A public repo the seedbank check flags as not catalogued can be catalogued by hand in one change** → None yet |
| F50 | 2026-11-09 | surface | — | **Every tool listed with the open MIT-licensed public goods carries an MIT license** → PR 2105 lists it apart from the MIT tools and says it has no license file |
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
_Regenerated by `scripts/belief_log_emit.py` · 51 entries · do not hand-edit — the ledger is the SSOT._
