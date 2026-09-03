# What in the 141-tool catalog is worth showing, and to whom

Date: 2026-09-03. Source: `runtime/specs/tool-catalog.json` (141 tools after the family snap), AGENTS.md
operator census, live surfaces, and the Ahmed thread as the calibration case. Rule applied throughout:
a tool is showable only if a named persona can look at its output and know what to do Monday morning.
Everything else is engine room, and showing engine room is what produced "hard to follow" twice.

Honesty flags used below:
- **LIVE** = a real counterpart has received this output and the page or file is verifiable.
- **BUILT** = code exists and runs; no external counterpart has consumed the output yet.
- **DEMO** = the only run is on our own data (self-referential). Proves mechanism, not outcome.
- **NOT SEAWORTHY** = built, measured, and failed its own falsification test. Do not show.

---

## 0. The shape first: one loop, six personas standing at different points on it

The Receipt Loop is the carrier. Every persona below is someone who benefits from one stage of it
more than the others. That is the whole segmentation logic: not "who is the customer" but "which
stage of the loop hurts them most today."

| Stage | Hurts most for | Showable tool | Output they hold |
|---|---|---|---|
| Before | Anyone walking into a meeting they cannot afford to misread | `recoil-prep` / `precall-brief` | A one-page bet |
| After | Sales leaders, coaches, anyone with a transcript pile | `recoil-close` / `gen_receipt_close.py` | A scored bet: hits, misses, the turning line |
| Share | Advisors, agencies, recruiters who must hand a client something | `recoil-ship` / `forge` / page factories | A counterpart-safe page plus a hand-sent note |
| Compounds | Founders, execs, anyone tracking a relationship over quarters | the SSOT account record / `receipt_lookup.py` | A track record: where their judgment is reliable |
| One-way doors | Anyone at a decision they cannot undo | `/dashboard` compass + Y gate, BAR operator | A RED/YELLOW/GREEN read with the strongest counter-argument |

---

## 1. Persona: the sales leader at one of Ahmed's customers (the real end user)

**Situation.** Hundreds of recorded calls. Deals are lost and the post-mortem is a story told by the
rep who lost it. No pre-commitment, so every write-up is hindsight.

**Show:**

- **`recoil-close` on a deal's call series** (the Recoil Report proper). Input: the transcripts for
  one account, discovery to close or loss. Output: per deal, two or three belief lines over call
  time ("intends to renew", "will expand seats", "champion has budget"), each with the quoted
  line that moved it, and a red dot where a belief broke. Rolled up: a ranked list of deals by
  reversal risk. **Monday action:** pick the three deals to step into and know which line to
  address. **Why it matters:** the objection that keeps costing the team is invisible in any one
  call and obvious across twenty. Flag: **DEMO** on our own call (ahmed-ext), **LIVE** for
  advisors (Joe Kim bar, Robin, Yuri). No sales-pipeline customer has run it yet. Say so if asked.

- **`recoil-prep` before the next call on a live deal** (the pre-meeting receipt). Output: what the
  rep expects the buyer to say, the one ask, and the strongest argument against the rep's own
  read. **Monday action:** the rep walks in with a bet written where they cannot edit it later.
  **Why it matters:** this is what makes the post-call score honest. Without it the Recoil Report
  is just a nicer call summary. Flag: **LIVE** (every counterpart brief since July).

- **`listening_scan.py` / hedging flags** (inside the recoil pass). Output: the hedge phrases and
  their timestamps ("we'd have to see", "probably next quarter"). **Monday action:** coaching note
  per rep. Flag: **BUILT**; the NLP is pattern-based, not learned. Do not oversell as "AI detects
  intent."

**Do not show:** the Y gate, NCI, kinematic vocabulary, operators. The rep needs three lines and a
red dot.

**Ahmed's resale line, in his customer's words:** "You already record the calls. This reads them
against what your rep expected, and tells you which deals are quietly turning."

---

## 2. Persona: Ahmed himself, as channel partner

**Situation.** He does not need to understand ARCS. He needs to know what he can say to a customer
in one sentence, what he gets back to put his name on, and what it costs. Twice he has been handed
the mechanism instead.

**Show:**

- **The sponsored report** (`recoil-ship` output with his name on it). One page, one customer,
  existing export, no integration. **His action:** forward it. **Why it matters:** he designed this
  funnel himself on July 22 ("free once per company, then talk to Zach"). It is his idea; return it
  to him.

- **`forge` as the "how it scales" story, one sentence only.** "Every customer gets the same
  family of pages, stamped from their own data." Do not open the blueprint. Flag: **BUILT**, run on
  Blacksmith, Robin, Yuri, Ahmed. The parameterized factory is real.

- **`teardown` / `precall-brief` for his new sales rep's ICP.** Input: the rep's stated hypothesis
  about who buys and why, plus the target's site and bio. Output: a falsifiable pressure test of the
  ICP and the prep questions the rep should ask. **His action:** hand it to the rep before outreach
  begins. Flag: **LIVE** (wing.arcs.care, Saul, Starpilot prep). This is the thing to offer if the
  sales-pipeline pilot stalls: cheaper, faster, and he raised it himself.

**Do not show:** pricing model theory. One story: first report free, then a fixed per-customer fee
named the day you pick who.

---

## 3. Persona: the founder or exec at a one-way door (Robert's world, the coaching wedge)

**Situation.** A hire, a raise, a pivot, a termination. Irreversible or nearly so. Magical thinking
is the failure mode; the room agrees too fast.

**Show:**

- **The compass (`/dashboard`, `POST /api/compass`) with the PrepSession.** Input: the question
  plus five prep fields (stakes, window, what you are protecting, how sure you already are, the
  strongest argument against your instinct). Output: a bearing, three tributaries (the deeper
  question, the uncomfortable truth, the cross-domain reframe), and a Y gate colour. **Action:**
  GREEN, move. YELLOW, one more probe. RED, "you are free-soloing this; add protection or change the
  climb." **Why it matters:** the RED state is the only piece of software that will tell an
  overconfident founder to stop. Flag: **LIVE** on app.arcs.care; the Claude L0–L5 pipeline is
  the production path.

- **BAR operator (`arcs_operators_bar.py`, and the 12 BAR templates in `arcs_seed_bar.py`).**
  Belief-Action-Rationale with ruin bounds. Output: the boundary condition where the plan dies.
  **Action:** redesign the decision so a single mistake is survivable. Flag: **BUILT**, not wired
  into the compass route; runs as the Python alternative path. Show the output, not the code.

- **LAB operator (`arcs_operators_lab.py`): Loki / Advisors / Bayesian.** Three adversarial
  lenses on one decision. Output: the strongest case against, from three directions, before you
  commit. **Action:** the pre-mortem Ahmed mentioned on July 22 for hiring. Flag: **BUILT**, same
  caveat as BAR.

- **The receipt track record over time (`receipt_lookup.py`, the Detective query).** Output:
  across N receipts, where this person's calibration is good and where it is systematically off.
  **Why it matters:** this is the decision-ROI conversation with Robert. It is the one output that
  compounds and cannot be faked after the fact. Flag: **BUILT** on the internal ledger; the
  cross-receipt view has been shown to no external counterpart. Be honest that N is small.

**Do not show:** the L0–L7 stack, ROM primitives, the Court. They are why it works, not what it does.

---

## 4. Persona: the recruiter or hiring manager (RecruitHaus / Blacksmith pattern)

**Situation.** A recruiter must sell a candidate to a founder who will object in predictable ways.
A hiring manager must not repeat the last bad hire.

**Show:**

- **Two-tier tear sheet (recruithaus.arcs.care open pitch + gated ammo).** Output: role pills, the
  "two hires in one" positioning, and behind a passcode the battle cards with first, second and
  third-order objection handling, plus comp logic. **Action:** the recruiter walks into the founder
  call with the objections pre-answered. Flag: **LIVE**, air-gap verified.

- **The Forge with CI gates (blacksmith.arcs.care).** For an engineering audience only: the
  candidate's build record, with the real gates between stages. **Why it matters to a CTO:** it
  proves craft without a take-home. Flag: **LIVE**.

- **`sbom-payload-scan` for anyone receiving a take-home repo.** Input: an untrusted repo. Output:
  a pass/fail on install-time and open-time triggers (the Contagious Interview class). **Action:**
  do not open it, or open it. Flag: **BUILT** and used on a real lure. This is the one security tool
  with a general audience: every job seeker who gets a "coding assignment."

**Hiring-side use, not yet built as a surface:** the pre-mortem on a hire is LAB + BAR pointed at a
candidate. It is the July 22 "hiring decisions" use case. Say "designed, not stamped as a page."

---

## 5. Persona: the advisor, consultant or agency with an engagement corpus

**Situation.** Months of calls, notes, emails, decks. The client asks "so where are we." The
answer lives in twelve places.

**Show:**

- **`omakase-pipeline` (jeben → omakase → louisville).** Input: one engagement corpus. Output: the
  three-surface family: a gated back-of-house record, a coursed narrative, and a client-facing suite
  tuned to their register. **Action:** send the front-of-house link; keep the record. Flag: **LIVE**
  for Jeben and Louisville.

- **`prl-page-factory` (prl.arcs.care).** Client-facing status page in a pilot-checklist register,
  BLUF first, plain language. **Why it matters:** this is a real paying-shaped engagement (Todd,
  PRL) and the design system is proven to land with a non-technical operator. Flag: **LIVE**, 1.2
  closed 8/27.

- **`teardown-page-factory` (wing.arcs.care).** Claim-versus-record teardown of a founder's essay
  or pitch, readable at any depth. Flag: **LIVE**.

- **`gauntlet_report.py` and `counterpart-gauntlet`.** The pre-send adversarial pass: simulate the
  counterpart across N facets, verify, fix. Output: the scar log, what the gauntlet changed before
  the client saw it. **Why it matters to an agency:** it is QA for judgment, and it is the reason
  the pages above land. Flag: **BUILT**, run on every recent ship.

**Do not show:** canon, seed bank, ADR machinery. The agency wants the pages and the QA gate.

---

## 6. Persona: the CTO or engineering lead (the one place the engine room is the product)

**Situation.** Wants to know whether any of this is real code or a deck.

**Show, in this order and no further:**

- `operators/` census: 43 modules, ~21.9k LOC, stdlib Python, the ARCS Law
  `C = αA − β(S − S_min)² + γW` in `arcs_primitives.py`. Flag: **BUILT**; not wired into the
  production compass route, which is Claude-driven. Say that plainly.
- `operator21` anterior/posterior spline inference: P1 determinism PASS 2026-08-28. One sentence.
- `echo_detector_dogfood.py`: the falsifiable seaworthiness test that the Orthogonal Echo Detector
  **failed** (adversarial false-positive 1.0 at default). **Why show a failure:** because a CTO
  trusts the shop that publishes its own failing test. Flag: **NOT SEAWORTHY**, and that is the
  point of showing it.
- `oracle.py` and the pre-commit hook: distributed numbering across parallel sessions with git
  non-fast-forward as the lock. **Why it matters:** concurrency discipline for multi-agent work,
  a real problem everyone building with agents hits in month two.

**Do not show anyone else:** any of the above.

---

## 7. Offstage, always (Zach-only operations)

`handoff`, `handoff-pickup`, `night-moves`, `fold`, `cruft-sweep`, `meta-audit`, `drift-check`,
`canon-review`, `nci-commit`, `nci-scoring`, `witness` (the ritual is showable, the command is not),
`memory_*`, `lattice_*`, `seedbank_*`, `sync_*`, `ship_docs`, `deploy-prod`, `vercel-*`,
`watchdog`, `tripwire`, `leak_check`, `oracle` (except to a CTO), every `arcs_*` operator not named
above, `doll_*`, `corpus_adapter_*`, `sugar_bulk` (PRL-specific), the Observatory scripts.

These are how the shop stays coherent while running twenty worktrees. They are the reason the
external pages are honest. They are not the product and every minute spent showing them costs a
minute of the persona's attention that the loop needed.

---

## 8. What this says about the two Ahmed strikeouts

Both demos sat at **stage After** (a scored bet) with the **wrong persona in the subject slot**.
The report was about Ahmed's beliefs on a call where nothing was at stake for him. The persona who
benefits from stage After is the sales leader with a pipeline. Ahmed is persona 2, the channel, and
persona 2 benefits from stage **Share**: a thing with his name on it he can forward.

So the fix is not a fourth rebuild of the page. It is a stage change: hand him a Share-stage
artifact for one of his customers (or, faster, a `teardown` on his new rep's ICP, which he raised
himself) and let the After-stage report be the thing his customer sees, not him.

The general lesson for the catalog: **a tool is legible to the persona standing at its stage of
the loop, and illegible one stage away.** Persona-tool fit is stage fit.

---

## 9. Falsifiers (so this document can be wrong in a checkable way)

- If Ahmed engages with a Share-stage artifact for one of his customers within 10 business days of
  receiving it, section 8 holds. If he says "still lost," the stage thesis is wrong and the gap is
  the offer itself, not its stage.
- If a sales leader who receives a Recoil Report on their own pipeline cannot name the three deals
  to act on in under five minutes, section 1's "Monday action" claim is falsified.
- If Robert (decision ROI) asks for the cross-receipt calibration view and finds N too small to
  trust, section 3's fourth bullet is premature; downgrade to DEMO.
