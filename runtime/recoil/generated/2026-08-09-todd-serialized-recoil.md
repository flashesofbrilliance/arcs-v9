# Serialized Recoil — Todd Hotes / PRL (last 4 calls + Jul 9/Jul 2 context)

_2026-08-09 · Internal. A serialized recoil across Todd's call arc, run to get a field-level read on his
**ambition** and lock the Kairos windows, so we propose the right thing given current platform constraints.
Grounded in the Aug 6 verbatim transcript + a cross-call extraction (Jul 2 → Aug 6). Reverse-Listening +
Deep-Recall passes per `runtime/specs/recoil-modes-v1.md`. Not deployed; analysis only._

Calls serialized (newest first): **Aug 6** (lunch, 1-1) · **Aug 5** (1-1) · **Jul 31** (1-1, + the 2:30 Tidio/Daniel
call same day) · **Jul 20** (1-1). Context anchors: **Jul 9**, **Jul 2**.

---

## 1. Reverse Listening — where each call LANDED vs. where it seemed headed

Read end→start, per call, then the cross-call drift.

- **Aug 6** — *Seemed* to be a working session on CRM field-mapping and data sources. *Landed* on two things that
  aren't chatbot-technical at all: (a) Todd's elevation to **CEO of the family office** ("the point guy for
  everything… estate, foundation, take care of their kids… their grandchild"), and (b) a quiet reset of the
  build to **"get the email figured out. And the sandbox. If we can get those tomorrow."** The real close: every
  data-source thread (IDES, FTP, product-dev forms) resolved to *"let me talk to our technical team"* — i.e.
  Todd has **no direct access** to the canonical data, and the build is gated on people he has to go ask.
- **Aug 5** — Opened on play (AR avatars) and **landed on launch theater**: *"the full launch should be the
  close… that's how we should launch this."* Todd is staging a single reveal moment, not an incremental rollout.
- **Jul 31** — Landed on Todd **doing the plumbing himself** (created the Outlook forwarding rule, paid the Tidio
  annual by card) and wanting it **kept separate** ("I want to keep it separate if I can"). He executes the small
  mechanical unblocks personally rather than delegating them.
- **Jul 20** — Landed on **"keep it simple, routed to the sales manager… getting the rest of the team involved in
  the technology is going to be a huge pain in the ass."** The constraint that governs everything downstream.

**Cross-call drift (the tell):** every call *forward* reads as "we're scoping a smarter chatbot," but every call
*backward* lands on the same floor — **simple, safe, single fielding inbox, no team change-management, gated on
data Todd doesn't personally hold.** The ambition is not in the feature depth. It's in the *frame around* the win.

---

## 2. Deep Recall — scored against the expectation each call set

- The recurring pre-call expectation ("this call we lock the CRM/data path and move to build") **misses every
  time on the same axis**: the blocker is never technical, it's **access + other people** (Bill traveling; Sugar
  pro-services Kim/Becca; the Rochester tech guy; the FTP "black box"; IDES bulk-export unknown). Todd is
  reliable on *decisions* and unreliable on *access he has to source from others* — not from unwillingness, but
  because he sits above the systems ("honestly, I don't really interact with our CRM… I've never been to that area").
- Where Todd is FAST: money ("budget's never been a limitation"; "it's not that I need approval, I just need to
  get it out there"), and small mechanical acts he can do alone (the forwarding rule, the card payment).
- Where Todd is SLOW: anything requiring him to extract data or coordinate a specialist. This is the true
  critical path, and it will not compress by pushing him — only by us routing around it (which is exactly what
  the Friday recap already did: public sources instead of FTP, read-only instead of sandbox).

---

## 3. Kairos lock recall — the timing windows Todd keeps returning to

Deep recall on *when* Todd wants things, not just what. Four locks, ranked by pull:

1. **"The full launch is the close" (Aug 5).** The strongest lock. Todd is timing a **single internal reveal** to
   his team — not a soft rollout. He'll "show bits and pieces along the way," but the moment that matters is one
   clean launch. → Everything we build should be sequenced to *converge on one demoable reveal*, not dribble out.
2. **Family-office succession (Aug 6).** The horizon lock above all others. Todd is stepping into **CEO of the
   family office**; his PRL/plastics involvement becomes *conditional* ("if you still have the company, I'll be
   involved… if it sells, I don't know"). → His attention is migrating upward. The chatbot's value to Todd is
   partly as a **clean, narratable win he can point to** during that transition, not as an end in itself.
3. **Year-end lead-gen displacement.** The ~$15K/yr lead-gen service is being **cut at year-end** (Aug 4 intel).
   That's the natural attribution benchmark and the budget-reallocation window. → The "number to beat" and the
   moment the ROI story writes itself.
4. **"Tomorrow" (recurring).** Todd sets tight near-term locks ("if we can get those tomorrow") that reality
   keeps sliding a day. → Read these as *intent signals, not commitments*; plan to the week, not the day.

---

## 4. Field-level read on Todd's AMBITION (the payload)

Todd's ambition, decomposed. This is **not** "a great chatbot." It is:

| Field | What Todd is actually optimizing for | Evidence |
|---|---|---|
| **Arena** | Moving *up and out* of plastics into the **family-office CEO** seat. PRL is becoming one proof-point, not the mission. | Aug 6 succession disclosure; "conditional" plastics involvement. |
| **The win he wants** | A **clean, defensible modernization** he can narrate upward to Bill/the owner in one sentence. Justifiability > affordability. | "budget's never a limitation"; "they'll just want to know the number." |
| **Drama tolerance** | **Near-zero.** No team change-management, no herding 55–60 tech-resistant reps. Simple, single fielding inbox. | Jul 20 "keep it simple… huge pain in the ass." |
| **Reveal** | One **launch-as-close** moment that feels like a real leap, not a beta. | Aug 5 "the full launch should be the close." |
| **Signature feature** | The **data-sheet / reverse-lookup** capability — he lights up here ("that feature would be used… pretty powerful"). It's the piece he's *proud* of. | Aug 6, repeatedly. |
| **Self-image** | A **capital steward** who moves decisively but never wastefully; does the small plumbing himself; keeps things separate/clean. | Jul 31 forwarding rule + card; "keep it separate." |

**The tension to manage:** Todd wants the *impressive* feature (data-sheet/spec capability) **at launch**.
Correction (Zach, 2026-08-09): "never state a spec/cert" was **Zach's own conservative design default**, not a
platform law and not a Todd requirement. Todd would likely be OK with the bot answering specs/certs **provided it
never surfaces the wrong or stale value and our evals prove it.** So the real constraint is **correctness, not
silence** — which changes the recommendation (see §5).

---

## 5. What to propose, given current platform constraints (corrected)

The real constraint is **correctness, not silence** (§4 correction). Three states for spec/cert answering:

- **(a) Ungoverned answering — LIVE TODAY, and the actual danger.** Lyro states "UL94 V-0 / 295°F" straight from
  150 auto-generated Q&As with no freshness guarantee and no eval. This is the state to kill first.
- **(b) Silent / route.** Zach's conservative default. Safe, but discards the capability Todd is proud of. Correct
  only as an **interim** while (c) is built — never the destination.
- **(c) Governed answering — the target that serves Todd's ambition.** Verified ground-truth source + a
  **deterministic eval that proves each value is current** + an **abstain-and-route** fallback when coverage or
  confidence is missing. "It only states a number it can prove is current, and connects you to a rep otherwise" is
  a *stronger* capital-steward sentence than "it never answers." The impressive launch feature AND the defensibility.

**Convergence — and a correction (Zach, 2026-08-09):** the ground truth for (c) is **IDES**, the source Todd lit up
about (Aug 6). BUT the IDES crawl + reverse-lookup were **already built in the Aug 7 session** and are not a Todd
dependency: `prl-kb/ides-datasheets/` (28 per-grade IDES datasheets scraped, every family) + `prl-lyro/
normalization/normalize.py` (deterministic competitor→PRL reverse-lookup, 895 keys, self-test 10/10 verified
2026-08-09: Lexan 141→PC-GP2-D, Ultem 1000→PEI-GP1). Built from the 150-grade internal catalog already in repo.
The recognition backbone is DONE. Todd's IDES bulk-export is a **completeness/freshness upgrade** (JS-gated
per-family variants need browser-render; his export = authoritative *current* set vs our public scrape), **NOT a
launch blocker.** This was already surfaced to Todd in the shared Drive SSOT ("231 deals tagged with competitor
grade") + the 1.3 roadmap. So (c) is much closer than "gated on Todd" — see corrected recs.

Recommendations:

1. **Reframe the launch around GOVERNED spec + data-sheet delivery, not spec-silence.** The bot answers a spec/cert
   only when the eval proves it against IDES ground truth (with the official data sheet attached), and routes +
   captures the lead otherwise. Lead the reveal with this (Kairos lock #1).
2. **Interim safety, not permanent posture:** take the 5 ungoverned PDFs **off customer Lyro now** (state (a) is
   live and unsafe) — but frame it to Todd as "we're swapping guesswork for a verified source," NOT "the bot won't
   answer specs." The destination is (c).
3. **The eval + ground truth are BUILT, not to-build** (anti-amnesia — see ADR-PRL-001). Ground truth =
   150-grade catalog, specs 100% verified vs source (delivered by Todd). Eval = `prl_lyro_eval.py`, 74 cases.
   Remaining to convert (b)→(c): collect live Lyro responses (≥3×/case), score, flip green categories. This is
   the ARCS-brand move: answer when provable, abstain when not.
4. **Competitor cross-reference → gate behind lead capture** (the banked Aug-5 decision, not "route"): recognize
   pre-capture, deliver the eval-verified equivalence *after* contact. Lead magnet + screens anonymous fishing.
   Pending Todd's approval (`2026-08-05-todd-competitor-data-approval-draft.md`).
5. **Sequence to his locks:** email/Sugar first (stated priority + true critical path) → collect+score the eval →
   converge on **one launch reveal** of governed spec-answering + data-sheet delivery → time it to the year-end
   lead-gen displacement ROI story. Plan to the week, treat "tomorrow" as intent.
6. **Route around Todd's access gaps, but IDES export is NOT the gate** (corrected). Ground truth already exists;
   IDES bulk export is a freshness/completeness upgrade. The real Todd-sourced gap is the **UL yellow-card data**
   (the ~$30K/6mo differentiator, in no file we hold) — until sourced, cert questions HARD-route. Keep routing
   around access the Friday way (public sources, read-only, staged copies).

**One-line recommendation (corrected):** Don't silence the bot on specs — **govern it.** Build the launch around
**eval-verified spec/cert answering grounded in IDES + official data-sheet delivery + abstain-and-route when
unproven**, take the ungoverned PDFs off Lyro as an interim, keep lead capture single-inbox simple, and time the
reveal to the year-end lead-gen cut — because Todd's ambition is a clean, *provably-correct*, narratable win he can
carry upward, and "provably correct" is a bigger feature than "safely silent."
