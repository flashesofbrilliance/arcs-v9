---
name: engagement-flightops
description: Run a client engagement as an aviation-grade flight loop — pre-flight (pre-mortem + one batched client checklist), in-flight (best/base/worst plans + disaster-recovery per failure mode), post-flight (kaizen debrief that banks patterns and feeds the next pre-flight), all reading one engagement SSOT and reported on a compounding instrument panel with a change-work-order trigger. Use to scope, price, sequence, de-risk, and track a multi-phase engagement so cost/timing/scope variance stay low. Composes the recoil-* skills (T-minus/zero/plus). Origin instance: PRL Resins chatbot 2026-08-04.
user-invocable: true
---

# /engagement-flightops — run an engagement as a boring, instrumented flight

> **SSOT:** one `runtime/recoil/generated/<date>-<name>.json` per engagement (same file the
> recoil-* skills use — this skill is interoperable with them, not a replacement).
> **Origin:** `runtime/recoil/generated/2026-08-04-todd-flight-operations-system.md` (the PRL
> instance-#1 spec). **HUD design handoff:** `reference/hud-designsync-brief.md` (this dir).

## What this is
A repeating three-phase loop per engagement phase, plus a compounding dashboard. It does not
invent process — it composes the recoil loop and adds the pieces recoil doesn't have:
pre-mortem, the batched client checklist, best/base/worst + DR, and the instrument panel + CWO.
The goal is **low variance**: predictable cost, steady cadence, no surprises, more boring each loop.

## The flight loop (run per phase: 1.1, 1.2, ...)
1. **PRE-FLIGHT** — pre-mortem (FMEA ranked by likelihood × impact, each with a baked-in de-risk)
   + ONE front-loaded client-input checklist (serial, one action at a time, defaults-on-no-response).
   Nothing takes off until the checklist clears or defaults engage. (Reuse `recoil-prep` for the gather.)
2. **IN-FLIGHT** — carry three plans (best / base / worst) + a written DR move for each pre-mortem
   failure mode, so a surprise is a procedure, not a crisis. No mid-flight improvisation.
3. **POST-FLIGHT** — kaizen debrief: what went well / didn't / off-rails / to automate / patterns to
   bank / anti-patterns to flag. Feeds the NEXT pre-flight (the compounding step). (Reuse `recoil-close`.)

## The instrument panel (gauges → the SSOT a renderer/HUD reads)
Risk reduction · Revenue acceleration (split LEADING vs LAGGING when revenue is recognized on a delay) ·
Project completion · Blocker resolution · Time to value · Project pacing (ahead/on-track/behind) ·
Scope tracking 🔒 · Budget/hours burn 🔒. Each has value + green/amber/red + audience tag.
**Change-work-order trigger:** Scope gauge goes red when an ask lands outside the current phase OR
budget crosses 100% → a one-line CWO naming what + why, approved before any work. (Mechanical answer
to "cost bubbling after the first crack.")

## Pricing (fixed-per-de-risked-phase, phase-gated)
Estimate best/base/worst hours per phase; price fixed with the pre-mortem buffer included; gate each
phase (stop-anytime). Open hours bubble; a de-risked fixed price is the cap. Vendor/tool costs are the
client's, pass-through, outside the fee. Sequence highest-value + lowest-client-dependency first.

## Non-negotiables (learned the hard way)
- **The never-share line is counterpart-profiling, not strategy.** The psychographic model of the
  counterpart (how they're read/handled) is 🧠 machine-local memory only — never in a shared/Drive/
  emailed/hosted surface. Business candor ≠ profiling-the-person. Scrub profiling before any client copy.
- **Channel is access control.** 🔒 internal = shown in person only, never sent. Only 🤝 client-facing
  gets a forwardable copy.
- **Credit routes to the client; the operator stays backstage.** The win narrative belongs to the
  counterpart, not to the operator's ingenuity.
- **Client inputs are batched into ONE serial checklist with defaults.** Client-input latency is the
  #1 variance source; front-loading it is the whole de-risk. Match the client's own cadence/register.
- **No overclaim.** Never present a lead as revenue; pipeline until the cycle closes. Baseline before ROI.

## Park discipline (instance #1 vs #2)
Structure for reuse on instance #1; **build the framework/HUD on instance #2** (or when a real trigger
lands). This SKILL.md and the design brief are the captured blueprint (cheap, durable) — not a mandate
to build the live HUD now. See `reference/hud-designsync-brief.md` for the design handoff when the
trigger fires. The PRL engagement's `todd-call.arcs.care` is the hand-built instance #1 of the HUD.

## Composition map
recoil-new (scaffold SSOT) → engagement-flightops pre-flight (pre-mortem + checklist) → recoil-prep
(gather) → in-flight → recoil-close (score/debrief) → post-flight kaizen bank → recoil-ship (externalize
a client-safe surface) → panel update → next pre-flight.
