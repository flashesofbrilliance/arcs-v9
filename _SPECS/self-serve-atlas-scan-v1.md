---
name: self-serve-atlas-scan
version: v1 (DRAFT / YELLOW — reasoned, not built; shaped in the 2026-09-08 session)
status: DRAFT — pending build. Serialized here so a fresh session can build from a clean baseline.
author: Zach Harris + Claude (ARCS-on-ARCS)
date: 2026-09-08
---

# Self-Serve Atlas Scan — candidate geometry → best-fit role mold, per-tenant, with a pulse

> **Thesis.** ARCS' personal job-search instrument, run *inverse* and *for anyone*: a user drops in
> portable files, ARCS abduces the directionally-accurate role mold their geometry points to, and each
> run compounds into a per-tenant atlas whose fidelity grows with the evidence. The working system IS
> the AI-native competency proof (show, don't tell) and the growth onramp. **This entire design is a
> reconciliation-before-leap artifact; nothing here is built yet, and the honest-state labels below are
> load-bearing.**

## The one product sentence
Drop in Resume + LinkedIn Profile PDF + LinkedIn Data Export → get a HUD scan of your candidate
geometry and the role mold it best fits (e.g. "these dimensions point to Applied AI Engineer") → the
atlas sharpens each time you add a receipt or an outcome.

## Architecture (the circulatory system)

```
INPUT LANES
  A. Zach SSOT lane   : resume.arcs.care + Connections.csv + calendar/reader/listening   [BUILT, ad-hoc]
  B. User1 self-serve : Resume + LinkedIn Profile PDF + LinkedIn Data Export             [GAP — the productization]
        │  (portable, universal; no ARCS-insider setup)
        ▼
FIRST ORDER — deductive geometry (fit against the known)
  scanner suite → classify_archetype + RESONANCE_MATRIX + compute_nci (arcs_core.py)     [BUILT, deterministic]
  op20 54-dim seed                                                                        [BUILT]
        ▼
SECOND ORDER — abductive discovery (what shape best explains this geometry?)
  Folksonomist (arcs_core.py:708–1014) + op20 DBSCAN over ROLE space                      [ENGINE BUILT, NOT WIRED inverse]
  → directionally-accurate role mold + market title(s) + confidence
  → VALIDATE mold against live postings (jobs loop) — mold must be real, not flattering   [GAP — the overfit gate]
        ▼
PER-TENANT ATLAS  (Ziggurat on the L0–L7 stack)
  Supabase RLS tenant per User1; corpus/canon/receipts/outcomes row-scoped               [PARTLY SCAFFOLDED: Supabase prod, rls-policies.sql, User model]
  Null State = outer fog / GRAIN → densifies along the earned-fidelity ladder as evidence compounds
        ▼
OUTPUT — one artifact, three onramps
  HUD scan (like target-role-scan-hud) rendered at EARNED fidelity
    · product-led : self-serve, try-the-instrument
    · media-led   : shareable derivative content
    · founder-led : demonstrates AI-native competency by working (zachharris.xyz secondary)
    · MCP-led     : read-only MCP over the corpus (ADR-076)                               [BACKLOG]

HEARTBEAT (monitors freshness of every organ above)
  pulse ⇄ oracle mutual attestation, git-anchored; status.arcs.care = external witness   [GAP — build first]
```

## The heartbeat (pulse ⇄ oracle) — build this FIRST (the plié)
- The **oracle** is already a logical clock backed by git (`scripts/oracle.py`, non-fast-forward = the lock).
- **Pulse** = its wall-clock twin: `_STATE/pulse.json` holding the current beat + each subsystem's
  `last_beat` + allowed `max_beats`. Every drift/staleness check reports **freshness in beats-since**,
  replacing the ~20 scattered private `STALE_DAYS`/`STALE_THRESHOLD` constants.
- **Mutual check (each is the other's second strand — neither self-certifies):**
  - pulse → oracle: counter monotonic, advancing, no off-oracle mints (already caught ADR-076).
  - oracle → pulse: each allocation stamps `last_beat`; the guard alarms on flatline.
- **Proof-of-life lives in the OT layer, not the IT layer.** Liveness is derived from the *operational*
  layer being observably active — crons that actually fired, workers that actually ran, commits that
  actually landed (the **git commit timestamp** as the tamper-evident beat) — NOT from the data/IT layer
  self-reporting "I'm fresh." The OT layer is the canary: when the operations go quiet, that is the
  flatline, and it cannot be faked the way a self-report can (this session's whole theme; cf. "wired
  beats written"). No standing service, no watcher-of-the-watcher regress.
- status.arcs.care = the external witness: renders "last beat: N ago · FRESH/STALE" by reading the
  committed pulse / OT-canary (build-time or a tiny Vercel serverless read). **A standing FastAPI is
  deferred** — new infra + new dep + it needs its own proof-of-life; only take it if sub-minute live
  pinging is ever required.
- Consequence: `drift-sentry` (stale 5d), `precall`/`postcall` (disabled since July) become subsystems
  that beat against the pulse and would have alarmed on day 2 instead of rotting silently.

### Immune response — arterial buildup → KINTSUGI / pathogen detection
The pulse does not just alarm on flatline; it is the afferent nerve of an immune system. **Arterial
buildup** = accumulated drift / staleness / integrity-decay / anomaly clogging the flow (stale-sentry,
disabled pollers, off-oracle mints, unreconciled built-but-unwired seams). When the OT-canary detects
buildup past threshold it **auto-triggers** the appropriate response — the machinery already exists:
- **benign seam-decay → KINTSUGI** (`operators/arcs_kintsugi.py`, ROM primitive #6): repair the seam
  *visibly*, show the break and the gold; never silent-patch.
- **foreign / counterfeit → pathogen detection** (`operators/arcs_constitutional_court.py` + the
  gauntlet + the ventriloquy speaker-provenance lambda, ADR-033): quarantine + flag provenance.
- **both** when a seam is simultaneously broken and compromised.
- **triage split** (per the metabolic router, mechanical vs judgment): buildup *detection* is mechanical
  (threshold cross on the canary); the benign-vs-foreign *classification* is mostly judgment and must not
  be smuggled into a "mechanical" gate. `[KINTSUGI + court BUILT; the auto-trigger wiring is the GAP.]`

### Time-signature alignment (local ⇄ global) — the carrier normalization
Each tenant has a **different clock rate**: careers, corpora, and receipt/outcome accretion run at
different cadences. The global pulse is ARCS's reference beat; each tenant carries a **local time
signature** (their own accretion rhythm). To process a candidate's carrier signal, ARCS must
**phase-align local to global** — normalize each tenant's local clock to the global pulse — so that:
- **"stale" is relative, not absolute:** a fast-moving candidate's atlas goes stale in fewer wall-clock
  days than a slow one's; freshness is measured in the tenant's *normalized* beats, not raw days.
- **fidelity gain is comparable across tenants:** progression up the earned-fidelity ladder is scored in
  normalized time, so two atlases at "SHARP" mean the same evidentiary density regardless of pace.
- **implementation seed:** `pulse.json` carries `global_beat`; each tenant row carries `local_beat` +
  an alignment factor (resample / phase-lock local→global). The canary check runs in normalized time.

## Local-first / air-gapped-after-sync (first-class extensibility constraint)
The architecture must be **extensible to run fully local and air-gapped after a network sync** — nothing
in v1 may foreclose that. It mostly validates choices already made:
- **Organs are already substrate-agnostic + offline-capable:** the scanners, `classify_archetype`,
  Folksonomist, op20, KINTSUGI are stdlib Python, zero-LLM for the deterministic core → they run
  air-gapped natively. Second-order abduction can run on the local deterministic + Folksonomist path; any
  LLM call needs a declared local fallback or is deferred to sync-time.
- **Dual store (already the dev/prod shape):** local SQLite / **GIGI** (the local-first fiber-bundle DB,
  seam at `compass/route.ts`) is the air-gapped store; Supabase RLS is the **network-sync layer**. The
  tenant's atlas lives locally and re-converges with Supabase on reconnect (git-style merge / CRDT-like).
- **Git-anchored pulse was already the right call:** git is local-first and syncs on push/pull, so the
  heartbeat + OT-canary work air-gapped; a standing FastAPI would have broken this (another reason to
  defer it).
- **Two-mode proof-of-life:** the **local OT-canary** (local git/pulse) is the air-gapped witness;
  **status.arcs.care** is the sync-time network witness. Neither is required for the other to function.
- **Time-signature alignment** runs on the local clock air-gapped and re-aligns to the global pulse on
  reconnect.
- **PII becomes a feature, not a cost:** an air-gapped local scan of the LinkedIn export means the data
  *never leaves the device* — the strongest privacy posture, and itself a competency/trust signal.
- `[GIGI is a connected-system seam, TBD/not wired. The dual-store dev(SQLite)/prod(Supabase) pattern
  partly exists. The sync/reconciliation layer is a GAP.]`

## Non-negotiable gates (this session's whole theme is why)
1. **RLS isolation airtight** — cross-tenant leak on LinkedIn-export PII is catastrophic. Security-review
   gate; per `supabase-rls-hides-rows` scar. Every atlas query row-scoped and tested for leakage.
2. **Earned fidelity, never inflated** — atlas resolution tracks actual evidence density; it may never
   render sharper than the data supports. Null State renders as fog (GRAIN) by construction. An
   overclaimed atlas is the counterfeit-System-2 / false-proof-of-life pattern.
3. **Directional-mold overfit gate** — the abduced role mold must survive field-contact (real postings
   exist for that shape) before it is shown. Validate against the live jobs loop; a flattering label with
   no market is a deceipt.
4. **PII-local scan** — the LinkedIn Data Export is scanned privacy-preserving; never exfiltrated. This is
   itself a trust/competency signal for a consulting audience.

## Phased build (plié → élevé → leap)
- **Phase 0 (plié): the pulse.** `pulse.json` + mutual-check guard (cron + SessionStart hook) +
  status.arcs.care freshness read. Load-bearing for every freshness label; fixes stale-sentry now.
- **Phase 1:** generate `profile-scan-hud` from a real scan (stop hand-authoring it) → a committed
  geometry object (the reusable first-order artifact that today does not exist).
- **Phase 2:** `role_abduce` — Folksonomist/annealing over role-space → mold + title + confidence, gated
  by validation against live postings.
- **Phase 3:** self-serve portable input lane (Resume + LI PDF + LI export) + RLS tenant per User1.
- **Phase 4:** progressive fidelity — atlas resolution rises along the earned-fidelity ladder as
  receipts/outcomes compound. Wire the recoil-close → recalibrate feedback so the loop actually closes.

## Open decisions
- FastAPI standing service vs Vercel-serverless/build-time read for status.arcs.care (recommend the latter).
- Where `role_abduce` validation runs (reuse the deployed jobs worker vs a new step).
- The fidelity metric (evidence-density → render-resolution mapping; WORLD.md render-scale is the spec).

## Falsifiers (what would prove this wrong)
- If a self-serve run on a stranger's export produces a mold no real postings match → the abduction
  overfits; the second order is not directionally accurate. 
- If tenants can see each other's rows → RLS model is unsound; halt.
- If the null-state atlas is useless (not just coarse) → the cold-start onramp fails the
  met-at-your-level bar.
```
