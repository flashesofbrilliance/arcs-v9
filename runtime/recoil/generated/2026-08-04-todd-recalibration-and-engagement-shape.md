# PRL Chatbot — Recalibration + Engagement Shape (change-order vs hard-stop)
_2026-08-04 · honest reassessment before over-committing 1.2 to 1.5_
_Grounded in the sent-mail trail (Jul-20 → Aug-04) + the ROADMAP + punchlist._

## 0. The one structural lesson (read first)

**Phase 1.1's overrun was not build. It was coordination, vendor due diligence, and client-side
access/decision latency.** The build itself was always ~1 week and still is. What consumed 6 weeks:

- **Vendor due diligence that kept moving:** Tidio plan changes (Starter → Flows → Flows+Lyro),
  the webhook-tier discovery, the Lyro architecture call, the AI-conversation-cap question (51/mo
  hard-stop vs overage, still open). None of this existed in the original scope.
- **Client-side access latency:** WordPress login via Josh's shop, no staging at first, SugarCRM
  sandbox still pending, DNS for `info@` stuck on PRL IT.
- **Decision latency:** the same three decisions (phone / lead_source / test lead) have been open
  since Jul-20.
- **Net-new scope discovered, not scoped:** 74-case safety eval, SugarCRM config audit, territory
  routing nuances (Distribution states, NY/PA sub-region splits), the email/DNS problem, and now
  ZoomInfo + Mailgun.

**Why this matters for 1.2 to 1.5:** every remaining phase has the same shape (external gates +
vendor DD + access latency). Estimating them in "build days" will underestimate them the same way
1.1 was underestimated. The correct unit of pricing is **Zach's coordinated availability over
calendar time**, not deliverables-per-hour. This is the crux of the engagement-shape decision below.

---

## 1. Expected vs learned vs modified (per phase)

### 1.1
- **Expected:** 1 week build, route to SM, $1,500, live in ~3 weeks.
- **Learned:** the bot builds fast; the *system around it* (CRM required fields, delivery tier,
  access, decisions) is the work. Still not live at 6 weeks, blocked on sandbox + 3 decisions.
- **Modified:** Mailgun retires the DNS/IT block; flow-webhook works on current plan (no upgrade
  gate). Definition of done tightened. This is genuinely close, gated on client inputs not build.
- **Why more effort:** vendor DD + access latency, not code.

### 1.2 (delivery + enrichment + metric)
- **Expected:** wire webhook → Zapier → Sugar, done.
- **Learned:** the 4-hour metric assumes Sugar captures a fielding event (unverified); **$26.5M of
  closed-won has no lead source**, so the attribution blind spot is large and the baseline pull is
  itself a project; enrichment (ZoomInfo) and autoresponder (Mailgun) are net-new.
- **Modified:** add the **CRM Data Reality** session as a gate; measure first-touch by an
  auto-capturable proxy, never by asking reps to log calls.
- **Why more effort:** the metric is a data-archaeology + instrumentation job, not a wire-up.

### 1.3 (knowledge / recognition)
- **Expected:** get a competitor cross-ref DB from Todd, OCR the guide, build recognition.
- **Learned (big):** **Sugar already holds 231 opps tagged with the competitor grade replaced.** The
  ground-truth largely exists in their own CRM. This **de-risks 1.3** and gives a ready-made eval
  corpus.
- **Modified:** extract the cross-ref from the 231 tagged opps first; treat Todd's DB + the guide as
  supplements, not the spine. Still need the tacit-knowledge elicitation (substitutions outside
  Good/Better/Best) and the deterministic eval.
- **Why more/less effort:** less data-gathering risk, but real eval + tacit-capture + guardrail work.

### 1.4 (SEM onramp + persona-conditional AI)
- **Expected:** add flows to Unbounce landers.
- **Learned:** it is two projects (GSC/Ads-driven page redesign + persona-conditional AI logic), and
  the freed **$15K/yr lead-gen budget** reframes it as an ongoing SEM + account/campaign-management
  agent, not a one-time refresh.
- **Modified:** scope Part A (page/onramp) and Part B (persona AI) separately; the persona AI depends
  on Lyro being verified (the 1.5 handoff), so 1.4B and 1.5 are coupled.
- **Why more effort:** it is a channel strategy, not a page edit.

### 1.5 (Lyro AI)
- **Expected:** turn on the AI.
- **Learned:** AI-level delivery needs Tidio+; the **51-conversation/month cap** cost behavior is
  unconfirmed (hard-stop vs overage); the handoff-to-Sugar path is unverified and load-bearing.
- **Modified:** keep OFF until the Tidio support review answers the cap + handoff questions; gate
  activation on a passing eval.
- **Why more effort:** it is a safety + cost + integration question, not a toggle.

---

## 2. The fork

### Option A — Hard stop at 1.1 done
Define 1.1 "done" crisply (it is, in today's email: complete lead into Sugar with Chatbot source,
routes to SM, 74 checks pass, live in a window Todd picks, time-to-first-touch on from day one),
ship it, close the $1,552 engagement clean. Todd has a working lead-capture bot he owns. Clean exit
if your focus needs to go to higher-opportunity work (Yuri/Google, etc.).
- **Use when:** you want optionality preserved and are not ready to commit 3 months of focus.
- **Risk:** leaves the high-value work (the $26.5M attribution blind spot, the SEM displacement of
  the $15K service) on the table, and re-opening later re-pays the coordination startup cost.

### Option B — 3-month change-work-order covering 1.1 to 1.5 (what you floated)
A time-boxed engagement priced to Zach's coordinated availability + buffer, not deliverables.
- **Use when:** the relationship + the $26.5M/$15K upside justify committing focus for a quarter.
- **This is the recommended shape** given (a) the upside just got bigger with today's discovery, and
  (b) the coordination overhead is only worth paying down once if you are staying through 1.5.

---

## 3. Pricing the 3-month engagement (recommendation)

**Instrument: monthly retainer, 3-month term, with a kill/pause at each month boundary.**
This is the resolution to the tension between "coordination is the real cost, so price availability"
and "Todd explicitly wants keep/kill optionality." A monthly with month-boundary offramps prices
your availability honestly while giving Todd a clean exit every 30 days. He floated 3 months, so the
term matches his own ask.

**Anchor: the freed $15K/yr lead-gen budget.** The cleanest, most honest frame Todd can take to the
owner: *"reallocate the $15K you already spend renting leads into a system you own, that also fixes
the $26.5M attribution blind spot."* That reframes the spend as a swap, not a new cost. It also sets
the floor: the engagement should not be priced below what they were already paying for less.

**Recommended number.** Price for buffer, because your stated risk is opportunity cost + focus, and
because 1.1 proved the effort runs well above the build estimate:
- **Recommended: $5,000/month × 3 = $15,000**, matching the freed budget dollar-for-dollar (easy yes,
  clean story, and roughly 3x the true effort-value of what 1.1 actually consumed).
- **Floor: $4,000/month** if Todd needs the number under the old line for internal comfort.
- **Stretch: $6,000/month** if he leans in and wants the SEM/account-management agent (1.4+) treated
  as an ongoing capability, not a project. This is defensible for a $100M company where the buyer has
  full discretion and values the relationship.
- **Do not** re-anchor on the $1,500 Phase-1 number. That priced a build-week and mispriced the job;
  repeating it would lock in the same underpricing across five phases.

**Vendor costs (Tidio, ZoomInfo, Mailgun) are PRL's, pass-through, not inside your fee.** State this
explicitly so your retainer is your time, and their tool spend is their line. Todd owns the accounts
(clean handoff), you configure them.

**What each month roughly buys** (deliverable-anchored inside the retainer, so Todd sees progress):
- **Month 1:** 1.1 live + 1.2 delivery/enrichment/metric + the CRM Data Reality baseline.
- **Month 2:** 1.3 recognition + eval (leveraging the 231 tagged opps) + 1.4A SEM onramp.
- **Month 3:** 1.4B persona AI + 1.5 Lyro (post Tidio-support review) + the attribution/ROI readout
  vs the $15K baseline.

**Scope guardrail:** new asks outside 1.1-1.5 (rep-facing voice notes, the resin recommendation
engine, IT triage) are Phase 2, quoted separately. Say so, so the retainer does not silently absorb
Phase-2 scope the way 1.1 absorbed the safety eval and config audit.

---

## 3b. Preferred instrument: committed hours bucket (best / base / worst) with tier-up

Better than a flat retainer, because the real variable in this engagement is *hours* (coordination
overhead), and a flat fee either underprices the worst case or overcharges the best. A committed-hours
bucket prices the variance directly, caps your downside (worst-case coordination drag is pre-funded,
not eaten), and answers the opportunity-cost problem: metered hours mean PRL cannot silently consume
unlimited focus. It also turns the burn-down report into the progress artifact Todd sees, which is
the same data that made the 1.1 recalibration legible ("here is where the hours went").

**Hour estimate per phase (Zach's time, coordination included):**
| Phase | Best | Base | Worst |
|---|---|---|---|
| 1.1 finish → live | 6 | 10 | 16 |
| 1.2 delivery + enrichment + metric + CRM Data Reality | 12 | 20 | 30 |
| 1.3 recognition + eval (de-risked by the 231 tagged opps) + tacit capture | 10 | 18 | 28 |
| 1.4 SEM onramp (A) + persona AI (B) | 16 | 26 | 40 |
| 1.5 Lyro + handoff verify + safety/cap review | 8 | 14 | 22 |
| **Total** | **~52** | **~88** | **~136** |

**The three buckets (sized to land on shippable phase boundaries, never mid-phase):**
| Bucket | Hours | Rate | Price | Covers (a done-state) |
|---|---|---|---|---|
| **Lean / Best** | 40 | $200/hr | **$8,000** | 1.1 live + 1.2 delivery/metric |
| **Base** (recommended) | 80 | $185/hr | **$14,800** | through 1.3 + 1.4A onramp. ≈ the freed $15K budget |
| **Full / Worst-buffer** | 120 | $170/hr | **$20,400** | all of 1.1–1.5 with coordination buffer |

**Tier-up / pro-rate mechanic (matches your ask):** the rate is set by the bucket committed, applied
to all hours in it. Moving up a tier **re-rates the whole commitment retroactively**, so you pay only
the difference to the new tier's total. Example: on the 40h bucket, jumping to the 80h tier tops up
40 hours and re-rates the first 40 to $185, so the top-up is (80 × $185) − $8,000 = **$6,800**. The
higher the commitment, the lower the blended rate ($200 → $185 → $170), so volume is rewarded exactly
as you described.

**Why the buckets end on phase boundaries:** so a bucket running out always leaves Todd at a
shippable state (1.2 done, 1.3 done), never a half-built phase. This is the safety valve that makes
keep/kill real without stranding either side.

**Honest caveats to hold:**
- **Value-capture risk.** Your value is the $26.5M blind spot fixed, not your hours. Pure hourly can
  under-monetize the strategy work. Mitigation: the rate is set so the Base bucket still lands at the
  $15K value anchor, and the high-leverage pieces (attribution readout, SEM strategy) are named as
  outcomes inside the bucket, not treated as commodity build hours.
- **Friend-relationship risk.** A visible meter can feel transactional with a friend-client. Size the
  buckets generously (the worst-case buffer exists so neither of you counts minutes); the meter is for
  transparency, not for billing disputes.
- **Vendor tool costs (Tidio/ZoomInfo/Mailgun) are still PRL's, outside the hours.**

**Recommendation:** offer the **Base 80h bucket ($14,800)** as the default (clean swap for the freed
$15K, covers the highest-value work through 1.3 + the SEM onramp), with the Full bucket named as the
tier-up path if he leans in, and the Lean bucket as the floor if he wants to stay closest to
optionality. This is the same $15K anchor as §3, expressed in the instrument you prefer.

## 4. The honest sentence to Todd (if Option B)

"Phase 1 taught us the build is the easy part; the value and the effort are in the system around it,
the CRM data, the attribution, the SEM channel. You're already spending $15K a year renting leads and
cutting it. I'd put that same budget into three months of building you a system you own, that fixes
the $26.5M of revenue with no source on it, and hands your SEM channel real attribution. Same money,
you own the asset, and you can stop at any month if it isn't landing."
