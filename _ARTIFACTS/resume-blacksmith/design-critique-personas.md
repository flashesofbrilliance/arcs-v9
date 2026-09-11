# Persona-led design critique — the Blacksmith bundle

_Private. Would the three founders read this page as **sharp** or **generic**? Judged against the
live render (blacksmith.arcs.care + /forge), through each founder's actual taste, not a checklist.
Air-gapped: never served._

## JP Jayaprakash — CEO, ex-Faire (product + design + business taste)
Faire is a beautifully-crafted marketplace; JP has the highest design literacy of the three and
will read the page the way a product person reads a competitor.
- **Praises:** the frozen **ship-clock instrument** ("v0 in 1h 22m") — specific, on-brand for a CI
  company, not a vanity metric; the **domain-map** (his customers ↔ where you shipped) reads as
  homework, not spray; the **Forge** as a product artifact, not a brag.
- **Reads generic:** the **dark-cockpit palette** (cyan/green on near-black) is the default
  developer-tool aesthetic — he has seen it 100 times; the **three-equal-card rhythm** repeats down
  the whole page with no change of gear; the hero is strong but nothing after it surprises.
- **Verdict:** competent and clearly bespoke-to-them, but visually *safe*. One distinctive moment
  past the hero would move it from "good dev landing page" to "this person has a point of view."

## Aayush Shah — Co-CTO, ex-Cockroach (the skeptic; bluff-vs-dig)
Screens for polish-over-substance. Beauty matters less to him than whether the chrome earns itself.
- **Praises:** the **Forge** — evidence grades, the cut list, the **between-stage gates**, the CI
  named by workflow. This is the page's spine for him: the "instrument" framing is *backed*, so the
  aesthetic reads as earned, not theater. The **git-true frozen clock** (checkable) survives his
  sniff test where a live-counting timer would have invited "so it took longer, then?"
- **Reads generic / risk:** any element that is decorative-only. The pulse dot and gradient glows
  are on the right side of the line *because* the Forge backs them — but that is a thin margin. Add
  ornament and he flips to "theater."
- **Verdict:** passes, on the strength of the Forge. Do not add decoration; every visual must keep
  earning itself.

## Aditya Maru — Co-CTO, ex-Cockroach (the gate-builder; rigor + consistency)
Notices whether details hold up and whether anything contradicts.
- **Praises:** the **advancement gates** are literally his integrity-gate pattern rendered as UI — he
  will recognize it; the **air-gap-as-a-test** and CI gauntlet are his language.
- **Would catch:** cross-surface inconsistency. The **status-board false-zero bug** (0 shipped over a
  full board) is exactly the kind of contradiction he'd spot and dock you for — **now fixed**, and
  worth it, because it's on a page linked from the bundle.
- **Verdict:** strong with him, *provided* the bundle / forge / resume-viewer are token-identical and
  nothing contradicts across them.

## Synthesis — the refinements, ranked
1. **[JP, highest leverage] Give the page one distinctive moment past the hero.** The strongest
   candidate: turn the **domain-map** from a 3-column table into an actual *mapping* visual (their
   space ↔ your work, drawn as connections). It's the one section whose content is inherently a
   relationship, currently rendered as parallel columns. This is the single change that lifts it from
   category-generic to authored.
2. **[Aayush] Hold the line on ornament.** Do not add visual flourish to "look designed." The Forge is
   what earns the cockpit aesthetic; keep the decoration/substance ratio where it is.
3. **[Maru] Lock cross-surface consistency.** Verify blacksmith.html / observatory / resume-viewer
   share the exact token set; the status/build fix removed the one live contradiction.
4. **[all] Palette differentiation (optional, lower ROI).** The cyan/green-on-black is category-default.
   A restrained on-brand accent (a blacksmith-forge ember/steel note) would de-genericize it, but it's
   a bigger change with real risk; the speed-optimization call earlier deprioritized this deliberately.

## Bottom line
**Sharp where it counts, safe where it doesn't.** The load-bearing surfaces (hero instrument, Forge,
gates, honest grades) are genuinely differentiated and back their own claims — that is what the three
founders actually weight. The "generic" read is confined to the *connective* visual language (palette,
repeated card grid), which is low-stakes with this audience. If you touch one thing, make it #1.

_Seed: [[recruiter-recoil-report.md]] · personas: [[founder-gauntlet.md]] · recon: [[dyor-blacksmith-recon.md]]._
