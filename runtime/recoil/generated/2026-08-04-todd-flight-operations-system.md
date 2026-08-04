# PRL Engagement — Flight Operations System (the engagement OS)
_2026-08-04 · aviation-grade operating layer: pre-flight → in-flight → post-flight, compounding._
_Not net-new: this is the ARCS recoil loop + Golden Inchworm + BAR/ruin dogfooded on a live engagement._

## Why this exists
Todd flies a $30M plane where imprecision means death, and he wants boring/predictable/low-variance in
every context. So the engagement runs like a flight: mandatory checklists, contingency procedures for
every case, and a debrief that makes the next flight even more boring. The dashboard is the instrument
panel. Kaizen is the compounding: each loop banks a pattern and retires a variance source.

---

## 1. The flight loop (repeats per phase: 1.1, 1.2, 1.3, 1.4, 1.5)

### A. PRE-FLIGHT (pre-mortem + checklist) — before a phase starts
- The **pre-mortem** (already built): most-likely failure modes ranked by likelihood × impact, each
  with a de-risk baked in. This is the turbulence forecast.
- The **pre-flight checklist**: the single front-loaded client-input batch, serial, one action at a
  time, defaults-on-no-response. Nothing takes off until the checklist is clear (or defaults engage).

### B. IN-FLIGHT (procedural: best / base / worst + disaster recovery) — during the phase
Every phase carries three flight plans and a DR procedure, so a surprise is a procedure, not a crisis:
- **Best case:** low friction path, lean hours, early completion.
- **Base case:** expected path (the plan of record).
- **Worst case:** high-friction path + the specific DR move for each pre-mortem failure mode (e.g.
  client-input stalls → defaults engage; Tidio cap is a hard-stop → Lyro stays off, flow-only ships;
  CRM has no first-touch → go-forward proxy). Pre-written, so mid-flight there is no improvisation.

### C. POST-FLIGHT (post-mortem / kaizen debrief) — after the phase
Structured debrief, every phase, banked to memory + the registry:
- What went well · what didn't · what went off the rails · what to improve / automate / close-loop ·
  **patterns to bank** · **anti-patterns to flag**.
- Output feeds the NEXT pre-flight (the inchworm: each pass tightens the next). This is the compounding
  step, and the reason the engagement gets more boring, not less, over time.

---

## 2. The instrument panel (compounding dashboard)
One row per gauge. Each has a computed value + a green/amber/red read + why it matters. 🔒 = internal
gauge (gate from any Todd-facing view); 🤝 = safe to show Todd.

| Gauge | Measures | Computed from | Green / Amber / Red | Aud |
|---|---|---|---|---|
| **Risk reduction** | pre-mortem burn-down | severity-weighted (FMs closed ÷ total) | ≥80% / 50-80% / <50% | 🤝 |
| **Revenue acceleration** | attributable pipeline vs baseline | tagged leads → pipeline vs the $15K/$26.5M/4hr baseline | trending up / flat / down | 🤝 |
| **Project completion** | deliverables done | done ÷ scoped, per phase | on-plan / slipping / stalled | 🤝 |
| **Blocker resolution** | open blockers + age | count × days-open × owner | 0 aging / 1-2 / 3+ or >7d | 🤝 |
| **Time to value** | days to first live lead, then first attributed $ | today − kickoff | ≤target / near / over | 🤝 |
| **Project pacing** | ahead / on-track / behind vs the score's tempo | actual vs Gantt beat | on-tempo / half-beat off / behind | 🤝 |
| **Scope tracking** | creep + budget burn + change-order flags | logged asks outside phase; hours/$ vs cap | in-scope, <80% budget / approaching / needs CWO | 🔒 |
| **Budget / hours burn** | spend vs cap | fixed-phase price or hours drawn | <80% / 80-100% / over | 🔒 |

**Change-work-order trigger (explicit, so cost never bubbles):** the Scope gauge goes red when an ask
lands outside the current phase OR budget crosses 100%. Red = a one-line CWO naming *what* and *why*,
approved before any work. This is the mechanical answer to "costs bubbling after the first crack."

---

## 3. Where this plugs into existing ARCS machinery (activate, don't reinvent)
- **recoil** (`runtime/recoil/generated/`, `scripts/recoil_brief.py`): T-minus (pre-flight) / T-zero
  (in-flight) / T-plus (post-flight) already IS this loop. The engagement is a recoil instance.
- **Golden Inchworm** (Red→Golden→Needle, 3-pass): the kaizen compounding.
- **BAR / ruin + free-solo edge** (WORLD.md): the 0%-margin discipline; DR procedures = "add protection
  or change the climb."
- **Observatory / replay**: the dashboard is the instrument panel of that theater.
This is [[recoil-as-second-product-surface]] made concrete: the engagement-OS is likely a product.

---

## 4. Generalization blueprint — "Engagement Flight Operations" skill family (PARKED)

PRL is instance #1. The reusable asset is a **composable, parameterized skill/command family**, but it
is **parked behind a real trigger** (a 2nd engagement, or PRL's first post-flight debrief), per
[[plan-generalize-omakase-site]]: structure for reuse on #1, build the abstraction on #2. Do NOT build
the framework now — capture the decomposition, keep PRL's components extractable, wait for the trigger.

**Component decomposition (what reuses vs what's net-new):**
| Component | Reuses (exists) | Net-new | Parameterized by |
|---|---|---|---|
| Pre-flight: pre-mortem/FMEA + client checklist | `recoil-prep` (T-minus gather) | FMEA + batched-checklist generator | phase scope, dependency map, client roster |
| In-flight: best/base/worst + DR procedure | — | contingency-procedure generator | hour estimates, failure modes |
| Post-flight: kaizen debrief → bank patterns | `recoil-close` (T-zero), `meta-audit` (Inchworm log) | debrief template + pattern/anti-pattern bank | phase outcomes |
| Instrument panel (dashboard) | ui-kit atoms | gauge-schema → renderer (audience-gated) | which gauges, thresholds |
| Registry / PKM index | snapshot.json `ui_artifacts` | registry generator + Drive mirror | artifact list |
| Change-work-order | — | scope-creep → CWO trigger + template | budget cap, phase boundary |

**Orchestration:** a per-phase loop (pre→in→post → update panel → bank → next pre-flight), all reading
one **engagement SSOT JSON** (same shape as `runtime/recoil/generated/<id>.json`). Dependency map: panel
← SSOT; CWO ← scope+budget gauges; next pre-flight ← last post-flight.

**Delivery form (decide on #2) — TWO surfaces:**
1. **Skill/command family** (`/preflight`, `/inflight`, `/debrief`, `/panel`) composing existing
   `recoil-*` skills, OR one `/flightops` orchestrator. Adds to [[project-open-source-skills-queue]].
2. **Interactive HUD** (the front-end): a live engagement cockpit spanning the FULL lifecycle —
   onboarding → intake → discovery → scoping → planning → tracking — as one interactive SSOT. This is
   the generalization of what **todd-call.arcs.care already is, hand-built** (status SSOT + discovery
   answers + "where things stand" + checklist). **todd-call = instance #1 of the HUD**, assembled by
   hand; the extraction seam is "structure what's already there," not invent. Reuses the ARCS FieldOS
   design system ([[arcs-fieldos-design-system]]: glass/underlit cockpit grammar, @arcs/kit atoms —
   do NOT re-derive the visual language). Ties to [[recoil-as-second-product-surface]] +
   [[arcs-hedged-parallel-path-b2c-b2b]] (a B2B product surface).

Gauge definitions in §2 are the SSOT both surfaces read.

**Trigger to un-park:** engagement #2 signs, OR PRL 1.1 ships and runs its first real debrief (which
produces the first genuine kaizen bank and proves the loop end-to-end). Kairos re-check, not a date.

## 5. Rendering (next step, on request)
Head-first: render a STATIC instrument-panel prototype (WYSIWYG) from the gauge schema before wiring
any live data. Internal vs Todd-facing split enforced (🔒 gauges gated). A Todd-facing instrument
panel is itself the ultimate proof of the "boring flight" promise — showing him the cockpit IS the
pitch. Keep budget/scope gauges internal.
