# Counterpart Artifact Family — Blueprint SSOT (floor plan + component sequencing)

_2026-08-05. The reusable pattern behind the Yuri build (recoil reset → codex → meta-cognitive demo),
generalized from Ahmed + Louisville/Jeben. Refer here before standing up the next counterpart universe.
This is the "componentize + mechanize on instance #2" artifact ([[build-reusable-decomposable-interoperable-default]])._

## 0. Two seed inputs, always
1. **Enriched profile SSOT** (public profile scan) — `runtime/recoil/generated/<date>-<name>-enriched-profile.json`.
   Carries `resolution` (level + caveat + `dial_up_inputs`) as first-class fields: it says out loud "this is
   public-only, more sources sharpen it, with consent."
2. **Call transcript** (Granola) — the ground truth. **Attribution discipline: in the transcript `Me`=Zach,
   `Them`=counterpart.** Never attribute Zach's framing to the counterpart (caught on Yuri; would be false + insulting).
Light chats (LinkedIn DMs) are context, not a third seed.

## 1. The surfaces, in sequence (the floor plan)
| Order | Surface | Job (visitor mode) | Lives at |
|---|---|---|---|
| A | Enriched profile SSOT | seed input of record | `runtime/recoil/generated/*.json` |
| B | **Recoil** ("how it works") | show the loop on THEIR own call | `<name>-recoil.arcs.care` |
| C | **Codex** ("how it scales") | one decision at N altitudes, org-scale | `<name>-codex.arcs.care` |
| D | **Meta-cognitive demo** ("run on you") | interactive inference ledger + regrade | `<name>-demo.arcs.care` |
| E | Internal war-room (gated) | Zach's back-of-house | `<name>-war.arcs.care` → `/warroom/*` admin-auth |

## 2. Shared component grammar (the atoms/molecules — reuse verbatim)
- **Tokens:** ARCS dark cockpit (`--bg #020408`, surface `#0d1117`, border `#1e293b`, text `#e2e8f0`,
  cyan `#00F0FF`, green `#00FF9D`, gold `#FFD700`, red `#FF4D6D`). Mono for labels, sans for body. Inline styles only.
- **Progressive disclosure:** section = `headline (.shl) + lede + <details class="deeper">go deeper</details>`, default collapsed. Beats wall-of-text (TL;DR/TL;DV).
- **Onramp card** ("what this is / who / how to read / how you'd use it") — kills the "too abstract" complaint.
- **Felt-value card** ("what this changes for you") — pillars tied to concrete stakes, not generic benefits.
- **`.said` quote callout** — tinted block (NOT border-left >1px; detector flags it). Color by speaker: cyan=Zach's framing, green=counterpart's own words.
- **Sub-nav + IntersectionObserver scroll-spy**; **Presentation mode** (headline/lede slides, keyboard nav, G=go deeper).
- **Confidence meter** (honest bar + number, color by value) + **conviction chip** (stable/shifting/flat).
- **Two-band inference ledger** (public-projected vs reserved-inferred) with clue→inference→conclusion chains + per-row disclosure.
- **Belief-evolution timeline** (serialized: how a belief moved, with confidence at each t).
- **pw-gate** (first name), **noindex**, **no em-dashes**, data-driven render + **JSON export** (SSOT→render).

## 3. The narrative spine (every surface)
orient (onramp) → the mechanism (show, don't tell) → how you'd use it (their world) → the offer (ONE receipt) → the studio → the seed. Land one plane; don't present a menu.

## 4. The air-gap / fence (front vs back)
Show **shape + value in full**; withhold **the transform** (semantic/NLP parse, scoring, data model). Frame it
craftsman-to-craftsman. **Dial the fence tighter for resourced counterparts** (e.g. Google) who could rebuild what's shown.
Internal scoring (NCI, conviction values, kinematics) stays in the war-room. **Role-archetypes only** for real orgs —
never fabricate interiority about named people ([[internal-external-artifact-air-gap]]).

## 5. Decision log (ADR-candidates for `_DECISIONS/`)
- **D1 Two-seed grounding + attribution discipline** (whose words is whose).
- **D2 Fence calibration by counterpart resource** — show more/less mechanism based on rebuild risk.
- **D3 Real-org fabrication guardrail** — public roles + labelled inference only.
- **D4 Atomic-confidence calibration** — determinism buys confidence in the *transform/structure* (invariance,
  round-trip, provenance); *semantic* confidence comes from convergence of independent atoms; *vibes* floored + human-checked. Refuse atomic-vibe overclaim.
- **D5 Progressive disclosure default** — headline+lede+go-deeper.
- **D6 Data-driven render + JSON export now; stateful RLS air-gapped tenant deferred to engagement-live.**
- **D7 Cost discipline** — local iteration, batch deploys, cheapest tier per task; each surface is one file + one build.

## 6. To reuse (next counterpart)
1. Write the enriched-profile SSOT from the public scan (+ caveat + dial-up inputs).
2. Run the call; build Recoil (B) on their own transcript.
3. If org-scale matters, build Codex (C) grounded in their org.
4. If they want to feel it, build the meta-cognitive demo (D).
5. Sequence per §3, grammar per §2, fence per §4. Deploy once per surface.

## 7. Forge pipeline — expanded scope (queued into task_56561b51)
Land each first-shot, no overengineering. The forge pipeline (`/forge`) should carry these:
- **The page IS the end-to-end loop mechanism.** Parameterize / componentize / templatize / atomize the
  robin one-door (the current platinum master, `public/robin.html` + `robin-profile.html`) as the internal
  decision loop: **seed -> canon -> forge -> gauntlet -> closed receipt.** That chain is the templating spine;
  every counterpart page is that loop instantiated on one SSOT.
- **Interactive receipt builder, per-tenant.** Wire a **robin tenant of the louisville receipt builder** —
  the API-backed interactive receipt-close tool. Refs: `src/app/api/louisville/receipts/route.ts`,
  `scripts/gen_receipt_close.py`, `scripts/receipt_lookup.py`, `public/robin-receipt.html` (forensic close).
  Goal: file/close a receipt interactively (bet -> score -> JSON), not a hand-authored card. Keep receipts
  portable JSON (interoperable), stateful RLS air-gapped tenant deferred to engagement-live (D6).
- **Gauntlet-hardened visual cleanup pass.** Before shipping any generated surface, run the gauntlet
  (BAR / COURT / LAB / Funhouse) + the mechanical verify (impeccable detector, 0 em-dashes,
  fabrication/air-gap scan, attribution check). Ref: `_ARCHIVE/handoffs.md` "gauntlet-hardened". This is
  the automated quality floor for the assembly line, not a manual afterthought.
- **Efficiency note:** run the fresh forge session model-efficiently (cheaper tier for mechanical stages,
  higher only for synthesis/verify). Quality floor is non-negotiable; overengineering is the anti-goal.
