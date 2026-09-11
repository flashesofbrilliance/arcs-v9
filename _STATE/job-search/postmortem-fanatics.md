# Post-mortem: Fanatics Collectibles (Chris Lamontagne / CJ Masopust), Jun 24 to Jul 15, 2026

> **Written:** 2026-09-11 (Thread 3 of the job-search fork). **Status of the engagement:** CLOSED-WARM.
> **Why now:** this is the cleanest warm-path failure in the data. Warmth was real and verified; the
> outcome was still a no. It isolates a variable the fit-score does not model: **req_reality**.
> **Evidence discipline:** every dated claim below cites a local artifact. Anything not locally
> verifiable is listed under "Unconfirmed", not folded into the narrative.

## Sources (what this is grounded on)

| Source | Path | What it carries |
|---|---|---|
| Chris call recoil SSOT | `runtime/recoil/generated/2026-06-25-lamontagne.json` | Jun 25 call, 5 segments, scenarios, stop-loss |
| CJ screen recoil SSOT | `runtime/recoil/generated/2026-07-01-masopust.json` | Jul 1 screen, Granola notes, scenarios, risk flags |
| Pre-call go-bag | `src/ui-kit/recoil-report/fanatics-go-bag.html` | Pipeline stages, pre-call probabilities incl. "active req attached: 30%" |
| Archived target-facing pages | `_ARCHIVE/fanatics-pages/{fanatics,cj-brief,chase-intro,chris-intro}.html` | The artifacts Zach shipped, dated beats Jun 24 to Jul 7 |
| The req Zach wrote | `JOB_REQ.md` | "This req was written by the person applying for it. That's intentional." |
| Gmail thread `19f5db040cf63cdc` "Fanatics Collect - Follow Up" | recovered from a prior session's Gmail pull (2026-08-28), message headers + snippets | CJ's Jul 13 note, Zach's Jul 14 fwd to Boardy, Boardy's read, Zach's Jul 15 reply, Zach's Jul 15 fwd to Chris |
| Memories | `feedback_room_reading_trigger_checklist`, `feedback_interview_pivot_to_self_promotion`, `writing-style-email` | Post-call transcript reads made in July |
| Git | `git log --grep=fanatics` | Jul 15 archive + 301 of the six subdomains |

The Gmail MCP was not connected in this session. The thread was NOT re-pulled live; the message
headers and snippets above come from a verified pull on 2026-08-28. CJ's full Jul 13 body (19.6 KB)
was never captured locally; only its first sentence is on record.

## Timeline (what was said, when)

| Date (ET) | Event | Evidence |
|---|---|---|
| ~Jun 24 | Chris Lamontagne (President, Strategy & Growth) posts on LinkedIn: "looking for a few exceptional & high-agency operators... Have your agent speak to my agent." Zach is first comment, first to book. | `fanatics.html` beat 01 |
| Jun 25, 3:00 PM | 30-min call with Chris (Regina Marshall, EA, on the invite). Chris names Instant Rips in segment 2. Load-bearing quote: **"Roles are fluid given pace of growth, looking for people with distinct ideas about what they want to do next."** Close: "send me something in writing, I'll use it to make relevant intros." | Lamontagne SSOT, segments 2 and 5 |
| Jun 25, same night | Zach sends "The Bubblegum Problem" email + a Magic Patterns deck. Last page re-cuts Chris's own hiring site as a prompt-injection scenario. | `fanatics.html` beat 02; `writing-style-email` |
| Jun 29 | Chris replies: "i loved what you built, would be keen to have the team dive in deeper. As an immediate next step, I'd like to introduce CJ, who leads Talent..." CJ sends a Calendly within 2 hours. | `fanatics.html` beat 03 |
| Jul 1, 12:30 PM | 30-min screen with CJ Masopust (Talent Lead). She describes the shape: SD to VP reporting to Chris, over performance marketing, lifecycle, data/analytics across Tops.com, Fanatics Live, Collect, VA. Player-coach, ~5 to 6 reports, 5 days in West Village. Comp ballpark verbal. **No JD. No comp sign-off. "3 to 4 weeks realistically."** Close is on community (Growth Plus One, Fan Fest), not process. Zach asks to be put in front of Chase; CJ's reply is a scope-and-process hedge. | Masopust SSOT segments 1 to 5; room-reading memory trigger 6 |
| Jul 1, same day | Zach ships `cj-brief.arcs.care` (post-call brief with **five candidate-written job-req variants** and **candidate-written interview probes**), `chase-intro.arcs.care` (30/60/90 for Chase + booking link), `fanatics.arcs.care` (chain-reaction provenance page), `token.arcs.care`. Recoil scores the screen **NCI 88, GREEN / HIGH / STABLE, render SHARP**: "Screen passed. CJ is an advocate. Path to Chase is clear." | archived pages; Masopust SSOT cover |
| Jul 2 | Zach emails Chris: subject "CJ was great // My read on it // Your take on Chase", with the `chris-intro` loop-close page and the Chase brief link. | `chris-intro.html`; `writing-style-email` |
| Jul 7 to 9 | Calendar reminders Zach set for himself: Jul 7 "reach out to Chase", Jul 9 "circle back with CJ on JD + process". Stop-loss in the Chris SSOT: "No Chase intro calendar by Jul 8, reopen with Chris directly." | `cj-brief.html` calendar block; Lamontagne SSOT protocol |
| Jul 13, 6:54 PM | **CJ to Zach, "Fanatics Collect - Follow Up":** "Hi Zach, I wanted to personally thank you again for the time, thought, and energy you invested throughout our process. We genuinely enjoyed getting to know you, and I especially appreciated the..." (rest of body not on local record). | Gmail thread, msg 1 |
| Jul 13, 9:50 PM | Zach forwards to Boardy: "Unfortunately, seems like the timing / needs didn't work out for this one..." | Gmail thread, msg 2 |
| Jul 13, 9:50 PM | Boardy replies: "Read plainly, they liked the work but never found a concrete mandate that matched your shape. That makes this a role-design miss, not a signal that the interview process exposed a..." | Gmail thread, msg 3 |
| Jul 15, 2:31 PM | Zach to CJ: "Hi CJ – Really appreciate you taking the time to write that. Totally understand it's a timing thing. Selfishly, I'd still love to swing by Growth+1 if the invite's still on the table..." | Gmail thread, msg 4 |
| Jul 15, 2:34 PM | Zach forwards the exchange to Chris: "Hope this isn't goodbye… but see you later." | Gmail thread, msg 5 |
| Jul 15, 3:22 PM | Zach archives all six Fanatics pages and removes the subdomain routing; 4:27 PM adds 301s "so anyone holding an old link (Chase, CJ, etc.) lands on arcs.care." | commits `ac7ad9ae`, `650b4e38` |
| Aug 16 | Resume harmonized: "retire Fanatics framing, reduce growth-intelligence voice." | commit `c8428c33` |
| Aug 28 | Engagement status trued against Gmail: CLOSED-WARM, no owed reply, revive on inbound or the Growth+1 invite. | retired memory `fanatics-artifact-security-constraints` (text recovered from transcript) |
| Sep 8 | Champion shortlist: "Standing exclusion: Fanatics." | memory `champion-shortlist-v1-sourced` |

**A call with Chase never happened.** There is no Chase SSOT in `runtime/recoil/generated/`, no
booking, no reply on record. The pipeline the go-bag drew (Chris → CJ → Chase → Loop → Offer)
stopped at stage 2 of 5.

## The inflection: where it turned

The turn is not Jul 13. Jul 13 is where it was announced. The turn is **Jul 1, inside the CJ screen,
segment 3**: "No formal JD with comp team yet." Everything after that was decided by a fact that was
already on the table and got scored as optionality instead of as absence.

Three readings of the same fact, all from Zach's own July artifacts:

1. The recoil SSOT logged it as a **MED** risk ("NO_JD_RISK: band could shift when formalized") and
   as a **gold DIRECTIONAL** signal ("Role Still Fluid: structural optionality, Zach has more
   influence over role definition than a standard search").
2. The pre-call go-bag had already priced it: **"Active req attached to this process: 30%."**
3. The Chris SSOT's scenario tree gave **5%** to "Process stalls at Talent: CJ screens and finds no
   open req to attach this to." That is the scenario that occurred.

So the instrument saw it. The render did not honor it. A screen with a 30% prior on req existence,
confirmed on the call as "no JD, no comp sign-off, Chase not yet in the loop," was rendered **SHARP
at NCI 88** with the headline "Path to Chase is clear." By ARCS's own render scale that state is
fog (YELLOW at best, GRAIN), and the honest headline was "Advocate confirmed. Req unconfirmed. Path
to Chase is unowned."

The secondary inflection is also Jul 1: **Zach asked for Chase; CJ hedged.** Room-reading trigger 6
(written on Jul 13 from the transcript) records that the next step came from Zach, not from CJ, and
that CJ's actual answer was a scope-and-process hedge. A talent lead who cannot volunteer the
hiring manager is telling you the hiring manager does not yet own a req.

## Root cause, separated

### A. Req reality (primary; largely out of Zach's control)

- There was no req. Chris's "roles are fluid" was read as *architectural permission* to manifest a
  role. The plainer reading, which Boardy gave in one line on Jul 13, is that fluid means
  *unfunded and undefined*: "never found a concrete mandate that matched your shape."
- The shape CJ actually described (SD to VP over performance marketing, lifecycle, analytics, with
  5 to 6 reports) is a growth-operator exec. The shape Zach pitched (Head of Growth Intelligence,
  a horizontal receipt/decision-instrument function, FDE-flavored) is a **new function**, by his own
  req: "A new function that doesn't exist yet." A talent lead can route a person into an existing
  mandate. She cannot create a VP-level function, a comp band, and a budget line on a candidate's
  behalf. That decision lived with Chris and Chase, and the process never reached Chase.
- Timing compounded it: CJ said 3 to 4 weeks; the no came in 12 days. Nothing in the record shows
  a JD ever being cut. "Timing / needs" in both Zach's and CJ's language is the polite name for
  "there was nothing to attach you to."
- **Verdict on A:** this alone was sufficient for the outcome. No execution change flips a
  non-existent req into a hire within a Talent screen.

### B. Execution and register ("cards hot"; in Zach's control)

Zach's own description: "played my cards hot, tried to demonstrate technical competency and
Applied-AI / FDE vibes for a role that didn't yet exist." The record supports the description and
also bounds what it caused.

What "hot" looked like in the artifacts:
- Same-night deck after the first 30-min call, with a prompt-injection "red pill" as the closer.
- Within hours of the Talent screen: a post-call brief containing **five versions of the job req,
  written by the candidate**, plus **the interview questions CJ should ask**, plus a 30/60/90 for a
  GM who had not been contacted, plus a public booking link for that GM, plus a provenance page of
  the whole chain, across six subdomains. The pitch document literally says "This req was written by
  the person applying for it. That's intentional."
- Register mismatch: a Talent screen for a growth-exec shape got an Applied-AI systems-builder
  pitch. The pivot memory (Tribe AI, Jul 8, one week later) names the same reflex: direct,
  scoped questions answered with the ARCS framework instead of the named example. CJ's screen did
  not have that specific failure signature (she was already a practitioner-builder and the AI angle
  "landed without needing to be sold"), which is exactly why over-demonstration bought nothing here:
  **the axis being demonstrated was already conceded.** What was not conceded was the mandate.
- Warmth was mis-scored as fit. The Growth Plus One and Fan Fest invites were logged as
  "durable goodwill regardless of outcome" (correct) and also lifted the overall GREEN/HIGH read
  (incorrect; room-reading trigger 7).

What B did and did not cause:
- It did **not** cause the no. Both Zach's read and Boardy's say Fanatics liked the work.
- It **raised the price of a yes.** Every artifact made the ask maximal: a new function, VP level,
  a self-authored req, a $350 to 400K band, a direct line to a GM. That is the hardest possible
  thing for a talent lead to say yes to when there is no req. The scoped alternative was already in
  Zach's own material: the Day-60 deliverable ("first pre-drop brief, a real tool Chase's team uses
  before the next drop") is a 60-day pilot that needs no headcount, no band, and no JD. It was
  written as a *consequence* of being hired rather than offered as the *entry*.
- It **consumed the stop-loss.** The Chris SSOT said: no Chase calendar by Jul 8, reopen with Chris
  directly. Whether that reopen happened is not on record (see Unconfirmed). What is on record is
  that the Jul 2 note to Chris was another artifact push ("my read on it"), not a req-reality check
  ("is there a mandate and who owns it?").
- The "cards hot" pattern is also what produced the evidence: the same artifact volume that
  overspent the ask is why this post-mortem can be dated to the hour. That is not nothing. It is
  just not conversion.

## In vs out of control

| In Zach's control | Out of Zach's control |
|---|---|
| Asking the req-reality question directly on Jul 1 (the go-bag even scripted it: "Does this land in an existing function, or is this bespoke and still being architected?") and gating artifact spend on the answer | Whether Chris had a funded mandate |
| Sizing the ask to the req that existed (pilot / contract / scoped 60-day) instead of VP headcount | Whether Chase was ever reachable through Talent |
| Rendering the Jul 1 screen at earned fidelity (YELLOW, not GREEN) so the next moves were "confirm mandate" rather than "prep Chase" | Fanatics' 12-day internal timeline |
| Not authoring the req and the interview rubric for the counterpart | CJ's warmth (real, and kept) |
| Executing the Jul 8 stop-loss as a mandate check with Chris | |

## The transferable rule

**Warmth routes you; only a req hires you. Confirm req_reality (defined, funded, decision-owner met)
before spending on a warm path, and size the ask to whatever req actually exists; when none does,
offer a pilot, not a headcount.**

Operationally, for the bridge rubric (Thread 2) and the ledger (H3):

- `req_reality` is a **gate**, not a weighted dim. Score it 0 to 3:
  0 = no JD, no owner met (Fanatics on Jul 1);
  1 = verbal shape, no JD or budget;
  2 = JD posted or cut, budget implied;
  3 = JD + budget + you have met the decision-owner.
- `warm_path` multiplies conversion only at `req_reality >= 2`. At 0 or 1, warmth predicts
  goodwill, invites, and referrals, not offers. Log it as a relationship asset, not a shot.
- At `req_reality <= 1` the correct move is to **convert the ask**: propose the smallest scoped
  deliverable the champion can say yes to without creating a req (pilot, audit brief, contract).
  The 90-day plan is the offer, not the reward.
- Render fidelity follows the gate. A screen at `req_reality <= 1` cannot be SHARP/GREEN
  regardless of rapport. Recoil headlines must carry the gate state ("Advocate confirmed, req
  unconfirmed").

## Reconciling with "Fanatics excluded"

The champion-shortlist exclusion (2026-09-08) and the CLOSED-WARM status (2026-08-28) are
consistent with this post-mortem, not in tension with it: Fanatics is excluded as a **target**
because there is no req to target, and the door is **warm** because the people liked the work.
Revive triggers stay as recorded: an inbound from CJ or Chris, the Growth+1 invite, or a posted
req at `req_reality >= 2`. Do not re-pitch the bespoke function into the same Talent door.

## Unconfirmed (do not cite as fact)

- CJ's full Jul 13 body. Only the first sentence is on record; the stated reason beyond "timing /
  needs" (Zach's paraphrase, same night) is not locally verifiable. Re-pull thread
  `19f5db040cf63cdc` when the Gmail connector is available and attach the body here.
- Whether Chris replied to the Jul 2 "CJ was great" note or the Jul 15 forward.
- Whether CJ's promised week-of-Jul-7 circle-back with Chris on JD and process happened.
- Whether Zach executed the Jul 8 stop-loss (reopen with Chris directly). No sent mail in the
  recovered headers between Jul 2 and Jul 13.
- Whether Zach attended Growth+1.
