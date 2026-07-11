# ARCS Meta-Audit & Roadmap — v1.0.0

**Epoch:** 2026-07-10 · **Method:** Recoil Protocol (Reverse Listening + Deep Recall) over the full corpus · **Verified against code at** `e802ed7`
**Update law (Golden Inchworm):** every new handoff, ROM Candidate, or serializability epoch appends an entry to §8 and re-grades §4/§6. Owner of the loop: Drift Sentry daily routine (08:00 ET).
**Honesty gauge:** requested confidence was 100%; ARCS doctrine (honest NCI, never inflate) overrides. Gauges below are earned, not asserted.

---

## 1. True North (the audit's own receipt)

**Question:** Where is ARCS against its promised done-state, and what is the highest-conviction next move?
**Bearing:** The engine is real and live; the loop is open. Close the loop (ship → measure → debrief → truth-sync) before adding any new organ.
**Conviction:** 78 · **Coherence:** 82 · **Done-state (weighted, assessed):** ~42% toward WORLD.md's superionic end-state.
**Mode:** COURT · **Door:** TWO_WAY (everything ranked below is reversible except the Hard Fork).

## 2. Recoil passes

**Reverse Listening (end→start):** Read backward from today, the corpus landed somewhere it didn't announce: the de-facto product is the **artifact wedge** (call briefs, recoil reports, 13 personalized subdomains — where every recent NCI ships), while the canon still narrates the **compass** as the product. Second divergence: the promised engine (operators/, 17.4K LOC Python) exists but the actual engine is a Claude prompt; two implementations of the same physics, one wired. Third: the system that preaches receipts had no receipts about itself until `e802ed7` (funnel events) and this audit.

**Deep Recall (start→end, 1/100th speed):** The founding promise (WORLD.md/canon): navigable fog→clarity world · receipts as cartography · Observatory replay · accumulation into a personal atlas · Kairos timing · L0–L7 · multi-party court · superionic flow-state. Slow-read verdict: L0–L5 and the receipt/brief/replay chain are substantially real; the *accumulation* layer (outcomes → priors → atlas) is embryonic; timing (Kairos) and collective (L6–L7, shared court) are canon-only — and correctly so, they're gated, and the UI discloses this honestly (EyebrowToast §04).

## 3. Parity matrix (code-verified 2026-07-10)

| Capability | Backend | Frontend | Verdict |
|---|---|---|---|
| L0–L5 compass pipeline | ✅ Claude prompt, `api/compass` | ✅ dashboard | **PARITY** (single-model engine) |
| Y-gate 12D → render fidelity | ✅ `ygate.ts` | ✅ resolution mapping | **PARITY** |
| DEWY receipts + briefs | ✅ 15 Prisma models | ✅ receipt/brief/reflect | **PARITY** |
| ATG tributaries | ✅ EXACTLY-3 + migration | ✅ chips/stacks | **PARITY — canon STALE** (AGENTS.md says "not built") |
| Outcome loop | ✅ `api/receipts/[id]/outcome` | ✅ debrief page | **PARITY — canon STALE** (listed P1 backlog) |
| Prep calibration | ✅ PrepSession | ✅ /prep | **PARTIAL** — no prior-work/ruled-out field (Phase 2 specced) |
| Observatory replay | ✅ GitHub ingest | ✅ 1174-LOC page | **PARTIAL** — receipt substrate gated at 100 receipts (ADR-023/027) |
| Recoil reports | ✅ JSON pipeline | ✅ route + ui-kit | **PARITY** |
| Scan / Calibrate surface | ✅ ScanSignal/Feedback | ✅ /scan | **EMBRYO** |
| Sage operator service | 🟡 mounted `/svc/sage` (vercel.json) | ❌ zero TS callers | **ORPHAN** — deployed engine nobody calls; SageTrace written from TS instead |
| Operators library 17.4K LOC | ✅ 37 files | ❌ unwired | **CANON-IN-CODE** — needs eval before wiring |
| Kairos detection | ❌ | disclosed "Roadmap" | **GAP (honest)** |
| Drift sentinel (session nudge) | ❌ (drift fields only) | ❌ | **GAP** → becomes the 08:00 routine |
| Accumulation protocol (Book II·V) | cron scaffolding only | debrief embryo | **EMBRYO** |
| Shared court (Book II·VI) | ❌ | ❌ | **GATED — correctly empty** |
| L6–L7 / lattice | sim harness only | ❌ | **GATED (100 receipts)** |
| Billing (Stripe) | ❌ | ❌ | **MISSING — held behind Hard Fork** |
| Funnel instrumentation | ✅ 8 events | ✅ | **NEW at `e802ed7`** |

## 4. Gauntlet verdicts

- **BAR (ruin):** No fatal exposure. Live risks: DATABASE_URL rotation (ADR-005, open), key-man singularity, canon-drift as trust-ruin for a system-of-record product. RLS incident (SageTrace) caught+fixed — the immune system worked once.
- **COURT:** NOTOMATION **PASS** (compass never decides). Honesty **PASS** (gaps disclosed in-product). Consistency **TENSION** — stale canon claims (§3) violate "the map must not lie about the terrain." Remedy = truth-sync commit.
- **LAB (Loki):** Strongest objection: *two engines, no benchmark* — you can't justify the operators' existence or wire them without an eval harness. Second: the 100-receipt gates may never fire at organic traffic; distribution is the binding constraint, not features. Third: roadmap currently steered by n=1 (Vic).
- **KKL (timing):** Kairos window is OPEN on the artifact wedge (live interview loops, Fanatics/Tribe, Tallin) — it pays and compounds testimony. Window on enterprise/SOC2 is CLOSED — do not force.
- **FUN HOUSE (mirror):** ARCS's biggest unnamed fork is about itself: **product-led compass vs. artifact-led consultancy.** The corpus orbits this fork without filing a receipt on it. Kryptonite: writing canon faster than closing loops — complexity as comfort. Fate if unaddressed: a beautiful atlas of a territory nobody walks.

## 5. Chi · Ma · Wuwei

- **Chi (energy lives):** the artifact wedge + the just-instrumented funnel. Feed it.
- **Ma (deliberate emptiness):** L6–L7, shared court, 100-receipt gates, unwired operators. Correctly empty — do not fill early.
- **Wuwei (do not force):** operator/prompt unification, enterprise posture, monetization rails. Let the sentry + events accumulate evidence; per ADR-023's own physics, watch edge-weights and let the superordinate goal precipitate.

## 6. Stack-ranked next moves

| # | Move | Size | Y-gate | Why now |
|---|------|------|--------|---------|
| 1 | Merge branch → deploy from main → verify 8 events in prod | S | GREEN/HIGH | Everything downstream needs live data |
| 2 | **Canon truth-sync**: fix stale claims (ATG, outcome loop, sage orphan) in CLAUDE.md/AGENTS.md/snapshot | S | GREEN/HIGH | Consistency TENSION remedy; this doc is the diff list |
| 3 | Close the debrief loop for first users (T+N outcome nudge via existing cron) | M | YELLOW/MED | Accumulation embryo → organ |
| 4 | Eval harness: prompt-engine vs operators on ~20 canned decisions | M | YELLOW/MED | Gate for ever wiring `/svc/sage`; kills or crowns the orphan |
| 5 | Kairos v0 as breadcrumbs on receipts (not an engine) | S | YELLOW/MED | Honest roadmap promise, cheap |
| 6 | **HARD FORK (file the receipt):** product-led vs artifact-led — run ARCS on ARCS, prep + court mode, log it | S effort, L consequence | FORK | The unnamed fork taxing every other decision |
| 7 | Stripe/monetization rail | M | RED until #6 | Rail depends on fork outcome |

## 7. Scheduled loop

**Drift Sentry** — daily 08:00 ET routine: check new commits/handoffs/memory since last epoch → append §8 inchworm entry → re-grade parity table if code changed → flag drift (work without receipts, receipts without outcomes, canon claims contradicted by code) → surface top-1 next move. Batched into one daily run (the economy is the batching itself — scheduled runs carry no special token discount).

## 8. Golden Inchworm log (append-only, newest first)

- **2026-07-10 · v1.0.0 · epoch `e802ed7`** — Audit created. Funnel instrumentation shipped (NCI:88). Stale-canon findings filed (ATG, outcome loop, sage orphan). Fork receipt (#6) not yet filed.
