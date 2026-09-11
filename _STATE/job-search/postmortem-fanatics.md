# Post-mortem: Fanatics Collectibles (Chris Lamontagne / CJ Masopust), Jun 23 to Jul 17, 2026

> **Written:** 2026-09-11 (Thread 3 of the job-search fork). **Revised same day** after the Gmail
> connector came back and the full thread, the Jul 1 call transcript, and the surrounding sent mail
> were pulled live. **Status of the engagement:** CLOSED-WARM.
> **Why now:** this is the cleanest warm-path failure in the data. Warmth was real and verified; the
> outcome was still a no. It isolates a variable the fit-score does not model: **req_reality**.
> **Evidence discipline:** every dated claim cites a source. Anything not verifiable is listed under
> "Unconfirmed", not folded into the narrative.
> **Visual artifact (earned-fidelity render, internal, unrouted):** `_ARTIFACTS/postmortem-manufactured-role.html`.
> **Gate shipped:** `scripts/req_reality_gate.py` (pre-commit) + `opportunity.req_reality` in the war-room template.

## Sources

| Source | Where | What it carries |
|---|---|---|
| Gmail thread `19f5db040cf63cdc` "Fanatics Collect - Follow Up" | pulled live 2026-09-11, PLAIN_TEXT | CJ's Jul 13 note (full), Zach's fwd to Boardy, Boardy's read (full), Zach's Jul 15 reply, Zach's Jul 15 fwd to Chris, Mixmax no-reply ping Jul 17 |
| Gmail thread `19f5c4ac51e3babb` "Call Transcript w/ CJ" | pulled live 2026-09-11 | Granola transcript of the Jul 1 screen (Zach sent it to Hilary Jul 13 12:23 PM); Hilary's reply 12:56 PM |
| Gmail thread `19f018d834006f23` "The bubblegum problem" | pulled live | Zach's Jun 25 night email + deck; Chris's Jun 29 reply and CJ intro (full wording) |
| Gmail thread `19f237639ecb183e` "CJ was great // My read on it // Your take on Chase" | pulled live | Zach's Jul 2 note to Chris; Mixmax no-reply ping Jul 4 |
| Gmail search: all mail to/from Chris, CJ, Regina, Jun 23 to Sep 11 | pulled live | Proves what was NOT sent (no Jul 8 stop-loss, no Growth+1 invite by email) |
| Chris call recoil SSOT | `runtime/recoil/generated/2026-06-25-lamontagne.json` | Jun 25 call, scenarios, stop-loss |
| CJ screen recoil SSOT | `runtime/recoil/generated/2026-07-01-masopust.json` | Jul 1 screen as scored on the day |
| Pre-call go-bag | `src/ui-kit/recoil-report/fanatics-go-bag.html` | Pre-call prior "active req attached: 30%" |
| Archived target-facing pages | `_ARCHIVE/fanatics-pages/*.html` | The artifacts Zach shipped Jul 1 to 2 |
| The req Zach wrote | `JOB_REQ.md` | "This req was written by the person applying for it. That's intentional." |
| Git | `git log --grep=fanatics` | Jul 15 archive + 301 of the six subdomains |

## Timeline (what was said, when; all times ET)

| Date | Event | Evidence |
|---|---|---|
| Jun 23 | Zach books "Growth Execs (Zach Harris)" via Chris's agentic hiring flow off his LinkedIn post ("Have your agent speak to my agent"). Regina Marshall (EA) on the invite. | booking confirmation |
| Jun 25, 3:00 PM | 15-min call with Chris (scheduled 15, ran ~30). Chris names Instant Rips early. Close: "send me something in writing, I'll use it to make relevant intros." | Lamontagne SSOT |
| Jun 25, 9:31 PM | Zach emails "The bubblegum problem": "Glad I saw the post – and got there first. Not a coincidence." Pitches the bookie/elephant's-memory layer, names it "Growth Intelligence, FDE, or something you haven't named yet", and closes: "Would love to chat with whoever's closest to this problem." 11:16 PM: follow-up with the Magic Patterns deck, "Something easy to socialize internally." | thread `19f018…` |
| Jun 29, 2:20 PM | **Chris replies:** "i loved what you built - would be keen to have the team dive in deeper. As an immediate next step, I'd like to introduce CJ, who leads Talent for us... I'd love to get into a bit more detail with him and **would also love Zach to meet with Chase to talk specifically about Instant Rips Growth (as a starting point).**" Zach forwards to Hilary: "See below. Told ya!" CJ sends a Calendly; Jul 1 booked. | thread `19f018…` |
| Jul 1, 12:30 PM | **30-min screen with CJ (Director, Recruiting).** See "What the transcript shows" below. Key exchange: Zach asks whether this is "a real thing or exploratory." CJ: "a little bit of both. We are going to have a need. Chris and I and his HR business partner are in the process of really defining what the job description can be. He just kind of wanted to see what type of response he would get." Later: "we are going to be having a leadership role open up... I'll just ask for your patience because I don't have it fully baked right now... it'll be somewhere at the top, managing and driving performance marketing, lifecycle marketing and all the data that pours into it." | transcript |
| Jul 1, same day | Recoil scores the screen **NCI 88, GREEN / HIGH / STABLE, SHARP**: "Screen passed. CJ is an advocate. Path to Chase is clear." Zach ships `cj-brief` (five candidate-written req variants + candidate-written interview probes), `chase-intro` (30/60/90 for Chase + booking link), `fanatics` chain-reaction page, `token`. | Masopust SSOT; archived pages |
| Jul 2, 11:32 AM | Zach to Chris: "CJ was great. Thanks for the intro. I put a short note together for you after the call. My read on where things landed and why Rips is the right starting point." + PS "cold start context for anybody else on your end." **No reply.** Mixmax no-reply reminder fires Jul 4. | thread `19f237…` |
| Jul 2 to Jul 12 | **Silence in both directions.** No mail to or from Chris, CJ, or Regina. The Chris SSOT stop-loss ("no Chase calendar by Jul 8 → reopen with Chris directly") was **not executed**. CJ's "early next week the latest" circle-back did not arrive. | Gmail search, all three addresses |
| Jul 13, 12:23 PM | Zach sends the Jul 1 transcript to Hilary. **12:56 PM Hilary replies:** "Seems like a great call. I wouldn't focus on other roles or rushing people in an Introduction - or pushing salary - let them come back and actually meet and have a meeting with would be boss. Maybe wait a day to see if they write you. What was your follow up?" | thread `19f5c4…` |
| Jul 13, 6:53 PM | **CJ to Zach:** "...you bring a unique perspective on AI and how it can be applied to solve meaningful business problems. The creativity and initiative you demonstrated stood out... After reflecting on where we are as a business today, we've decided not to move forward with next steps at this time. **This decision is much more about timing and the opportunities we have available than it is about your capabilities. While we don't have a role in mind that's the right fit today**, we would very much like to stay in touch as things evolve." | thread `19f5db…` msg 1 |
| Jul 13, 9:50 PM | Zach forwards to Boardy: "Unfortunately, seems like the timing / needs didn't work out for this one…" **Boardy, same minute:** "Read plainly, they liked the work but never found a concrete mandate that matched your shape. That makes this a role-design miss, not a signal that the interview process exposed a capability gap. I would treat the 'stay in touch' line as relationship preservation, not pipeline. **The useful takeaway is the same one we already had: you need an executive champion tied to a defined operating problem, not an exploratory growth-intelligence concept looking for a home.**" | msgs 2, 3 |
| Jul 15, 2:31 PM | Zach to CJ: "Totally understand it's a timing thing. Selfishly, I'd still love to swing by Growth+1 if the invite's still on the table... Happy to be a sounding board or just a familiar face." 2:34 PM: forwards to Chris, "Hope this isn't goodbye… but see you later." **No reply from either.** Mixmax no-reply reminder Jul 17. | msgs 4, 5, 6 |
| Jul 15, 3:22 PM | Zach archives all six Fanatics pages, removes the subdomain routing; 4:27 PM adds 301s "so anyone holding an old link (Chase, CJ, etc.) lands on arcs.care." | commits `ac7ad9ae`, `650b4e38` |
| Aug 16 | Resume harmonized: "retire Fanatics framing, reduce growth-intelligence voice." | commit `c8428c33` |
| Aug 28 | Status trued vs Gmail: CLOSED-WARM, no owed reply. | retired memory `fanatics-artifact-security-constraints` |
| Sep 8 | Champion shortlist: "Standing exclusion: Fanatics." | memory `champion-shortlist-v1-sourced` |

**A call with Chase never happened.** No booking, no thread, no SSOT. The pipeline the go-bag drew
(Chris → CJ → Chase → Loop → Offer) stopped at stage 2 of 5.

## What the transcript shows (Jul 1, primary source)

Read in order, the screen has five movements. Quotes are verbatim from the Granola transcript.

1. **CJ opens by asking what Chris and Zach discussed.** Zach delivers a long "headlines only"
   monologue (CoE vs vertical GMs, horizontal layer, strategic advisory + applied AI engineering +
   forward-deployed engineering, "growth intelligence" as "a big enough umbrella"), then asks
   whether Chris forwarded the deck. CJ: "I didn't see there was an attachment." Zach: "I know I've
   given you a lot to digest."
2. **Rapport is real.** Connecticut geography, Sacred Heart, CJ's own AI builds (talent-sourcing
   agent, Interview Architect GPT, Greenhouse/Okta scheduling pain). Zach riffs on MCPs, permission
   dashboards, Claude-in-Slack, "producer, composer, orchestrator." CJ: "No that's incredible."
3. **Zach asks the req-reality question directly:** "I didn't quite understand from my chat with
   Chris if this is like a real thing or if you guys were in exploratory stages." CJ answers at
   length and honestly: a little of both; a need is coming; JD being defined with Chris and the HR
   business partner; the LinkedIn post was Chris wanting "to see what type of response he would
   get"; the eventual role is a senior leader over **performance marketing, lifecycle marketing,
   and the data in between**, SD to VP, player-coach, small team, five days in West Village.
4. **Zach pushes process, leverage, and comp** in the final third: "since I'm chatting with some
   other folks", "late stages with a few and may have offers coming in after the fourth", asks if
   there is "a monopoly bypass, go collect 200", asks for the Chase intro "to get that in motion",
   hands over the pre-built brief and the Chase pass-along, asks for the targeted base band. CJ,
   each time: "I still have to click in with Chris on total process and scope... we're in very
   early stages... three to four weeks more realistically"; "I don't have a job description in
   front of our compensation team yet." Zach also asks about Fan Fest guest passes for his son;
   CJ: "I'm not in the in crowd that can give out guest passes."
5. **CJ closes six minutes into her next call**, promising to "circle back to Chris with regards to
   next steps... early next week the latest," and offers the Growth Plus One invite unprompted.

Two independent readers scored this transcript before or as the outcome landed. Hilary, six hours
before CJ's email, without knowing the outcome: don't focus on other roles, don't rush the intro,
don't push salary, let them come back and meet the would-be boss. Boardy, the same night: no
concrete mandate matched the shape; you need a champion tied to a defined operating problem. Both
reads survive contact with the primary source.

## The inflection: where it turned

Jul 13 is where it was announced. The turn is **Jul 1, movement 3**: the req-reality question was
asked, answered at "being defined, not fully baked, please be patient", and then **scored as
optionality instead of as absence.** Three readings of the same fact from Zach's own July artifacts:

1. The recoil SSOT logged it as a **MED** risk ("NO_JD_RISK") and a **gold DIRECTIONAL** signal
   ("Role Still Fluid: structural optionality, Zach has more influence over role definition").
2. The pre-call go-bag had already priced it: **"Active req attached to this process: 30%."**
3. The Chris SSOT's scenario tree gave **5%** to "Process stalls at Talent: CJ finds no open req to
   attach this to." That is the scenario that occurred, in CJ's own words: "we don't have a role in
   mind that's the right fit today."

So the instrument saw it, the candidate asked it, and the render did not honor it. A screen with a
30% prior on req existence, confirmed on the call as "JD being defined, no comp sign-off, process
undefined, Chase not yet in the loop", was rendered **SHARP at NCI 88** with the headline "Path to
Chase is clear." By ARCS's own render scale that is fog (YELLOW, DEGRADED at best), and the honest
headline was "Advocate confirmed. Req unconfirmed (level 1). Path to Chase owned by Chris, not CJ."

The second inflection is movement 4 plus what followed it. The final third of the call converted a
warm screen into a negotiation with a recruiter who had nothing to negotiate yet, and the follow-up
converted the "send me something forwardable" signal into six subdomains and a self-authored req.
Then the record goes silent for eleven days: no Chris reply, no CJ circle-back, no Jul 8 stop-loss.

## Root cause, separated

### A. Req reality (primary; largely out of Zach's control)

- There was no req. Chris's LinkedIn post was, per CJ, a probe to "see what type of response he
  would get." The JD was being defined by Chris and HR at the time of the screen. CJ's no, twelve
  days later, says it plainly: "we don't have a role in mind that's the right fit today."
- The role that was forming (senior leader over performance marketing, lifecycle, and growth data)
  is a **growth-operator exec**. The role Zach pitched (Growth Intelligence / FDE / horizontal
  receipt layer) is a **new function**, by his own req: "A new function that doesn't exist yet."
  Boardy's line names the gap exactly: "an exploratory growth-intelligence concept looking for a
  home." A recruiter can route a person into a forming mandate; she cannot mint a VP-level function
  on a candidate's behalf. That decision lived with Chris, and Chris went silent after the handoff.
- Chris DID say he wanted Zach to meet Chase (Jun 29, in writing). That never happened either. The
  block was upstream of CJ: the person who could open the req or the Chase door stopped replying
  after Jul 2.
- **Verdict on A:** sufficient on its own. No execution change turns "JD being defined" into a hire
  inside a Talent screen. `req_reality` on Jul 1 = **1** (verbal shape, no JD, no budget).

### B. Execution and register ("cards hot"; in Zach's control)

Zach's own description holds up against the transcript: "played my cards hot, demonstrated
technical competency and Applied-AI / FDE vibes for a role that didn't yet exist." Specifically:

- **Wrong register for the room.** CJ described a growth-exec search; Zach pitched an applied-AI
  systems builder. CJ conceded the AI axis in movement 2 ("that's incredible"), so every further
  demonstration on that axis bought nothing. The axis not conceded was the mandate.
- **Negotiating before there was a counterparty.** Competing offers, "monopoly bypass", base band,
  Fan Fest passes. Hilary named all three (rushing the intro, pushing salary, other roles) from the
  transcript alone. Each push got the same honest answer: nothing is baked yet. Pressure on a
  recruiter with no req cannot accelerate; it can only raise the cost of saying yes.
- **Self-authoring the req and the rubric.** Five JD variants and "suggested interview probes" sent
  to the person whose job is to write those. "This req was written by the person applying for it.
  That's intentional." It reads as bespoke headcount, the hardest possible ask.
- **Maximal ask, no scoped fallback.** Every artifact asked for a new VP function. The scoped
  alternative was already in Zach's own material: the Day-60 deliverable ("first pre-drop brief, a
  real tool Chase's team uses before the next drop") is a 60-day pilot that needs no headcount, no
  band, no JD. It was written as a consequence of being hired, not offered as the entry.
- **Stop-loss not executed.** The Jul 8 trigger was written on Jun 25 and never fired. The only
  outbound after Jul 2 was the Jul 13 forward to Hilary and the Jul 15 close.
- **Warmth mis-scored as fit.** Growth Plus One was offered unprompted and is real goodwill; it was
  also lifted into the GREEN/HIGH read. Room-reading trigger 7.

What B did and did not cause:
- It did **not** cause the no. CJ ("not about your capabilities"), Boardy ("liked the work"), and
  the transcript (CJ's enthusiasm is unforced) agree.
- It **raised the price of a yes** and **spent the goodwill budget on the wrong axis**, at the
  moment when the only thing a recruiter could green-light without a mandate was a scoped pilot.
- The lesson was **available on Jul 13 and not banked for 60 days.** Boardy: "the useful takeaway
  is the same one we already had." It reached the ledger only now.

## In vs out of control

| In Zach's control | Out of Zach's control |
|---|---|
| Honoring the answer to the req-reality question he asked (level 1) by rendering the screen YELLOW and gating artifact spend | Whether Chris and HR ever cut the JD |
| Sizing the ask to the req that existed: a scoped pilot at Rips instead of a VP function | Whether Chris replied after Jul 2, or opened the Chase door he said he wanted |
| Not negotiating comp or process, and not stacking competing offers, with a recruiter who had said "not fully baked" | Fanatics' twelve-day internal clock |
| Not authoring the req and the interview rubric for the counterpart | CJ's warmth (real, kept) |
| Executing the Jul 8 stop-loss as a mandate check with Chris | |
| Banking Boardy's Jul 13 rule the day it was written | |

## The transferable rule

**Warmth routes you; only a req hires you. Ask req_reality on the first screen, honor the answer
in the render, and size the ask to the req that exists; when none does, offer a pilot, not a
headcount.**

Operationally, for the bridge rubric (Thread 2) and the ledger (H3'):

- `req_reality` is a **gate**, not a weighted dim. Score it 0 to 3:
  0 = no JD, no owner met;
  1 = verbal shape, no JD or budget (**Fanatics on Jul 1**);
  2 = JD posted or cut, budget implied;
  3 = JD + budget + you have met the decision-owner.
- `warm_path` multiplies conversion only at `req_reality >= 2`. At 0 or 1, warmth predicts
  goodwill, invites, and referrals, not offers. Log it as a relationship asset, not a shot.
- At `req_reality <= 1` the correct move is to **convert the ask**: propose the smallest scoped
  deliverable the champion can say yes to without creating a req. The 90-day plan is the offer.
- At `req_reality <= 1`, **no negotiation moves**: no competing-offer leverage, no band questions,
  no process-shortcut asks. There is no counterparty yet. Hilary's rule: let them come back and
  meet the would-be boss.
- Render fidelity follows the gate. A screen at `req_reality <= 1` cannot be SHARP/GREEN
  regardless of rapport. Recoil headlines must carry the gate state.
- **Bank the rule the day it is stated.** A post-mortem that arrives 60 days after the outside read
  is reconstruction, not witness.

## Isomorphism: HypeLab (Joe Kim), Oct 2025 to Jul 2026

Added 2026-09-11 after Zach flagged the resemblance. Sources: `runtime/recoil/generated/2026-07-20-joe-kim-hypelab-serialization.json`,
`runtime/recoil/generated/2026-07-22-kim-multicall.json` (both anchored to Granola transcripts), the
Oct 19 "HypeLab Strategic Survey" and Oct 22 "Follow-up: Thoughts on Next Steps" sent mail (both
with Mixmax no-reply pings), the Jul 20 pre-call note pointing Joe at joe.arcs.care.

The same kinematic skeleton, step for step:

| Step | Fanatics | HypeLab |
|---|---|---|
| Warm entry via a founder | Chris, off the LinkedIn stunt: "i loved what you built." | Joe (CEO), via LinkedIn plus Brian Wong: "we could talk for hours." |
| Req never funded | CJ: JD "being defined... not fully baked." | Joe, Oct 21: "a purely opportunistic role, not something that I've pitched I needed... I need to make a case for why I need it." |
| Disqualifying signal heard live | Level 1, soft: "please be patient." | Level 0, explicit: Oct 21 Joe says they already hired a GTM person; Ed reconfirms Oct 29. |
| Candidate manufactures the req | Five JD variants, interview probes, 30/60/90, self-authored `JOB_REQ.md`. | 30-card board-facing Gamma "hypelab-gtm-system" with tripwires, a Tally strategic survey, the Oct 22 Day-1 self-pitch ("I'd pay for my salary within 6–12 months"), sent the day after the role-filled disclosure. The multicall SSOT's own line: "Behavior went UP as the signal went DOWN." |
| Negotiating with no counterparty | Competing offers, "monopoly bypass," base band. | "Q1/Q2 budget windows... each week that passes," a target above Joe's stated ceiling, survey homework before the call. |
| Gate owner never clears it | Chris silent after Jul 2; Chase never reached. | Ed: "I'll talk to Joe." Routed back to Joe. Never cleared. |
| Resolution | Polite no in 12 days. | Nine months of silence. |
| What survived | CJ "stay in touch," Growth+1. | Joe's "shoot the shit"; Jul 22 as peer and advisor. |
| Scoped pilot available, unused as entry | Day-60 pre-drop brief written as a consequence of hiring. | Advisory → fractional → FTE ladder floated Oct 21; deck's "$45–60K retained value even if it doesn't convert"; hard numbers left as $X/$Y/$Z "pending a terms conversation that never happened." |

**Where they differ, and why it strengthens the rule:**

- **Register was right at HypeLab.** An ad-tech revenue operator pitched to an ad-network CEO who
  prized the ads + crypto combination. No self-promotion pivot, no wrong room. It still went to
  zero. HypeLab is therefore the control that isolates `req_reality` from execution: with register
  fixed, `req_reality <= 1` alone produced the outcome.
- **Gatekeeper type did not matter.** HypeLab was founder-direct, Fanatics went through Talent.
  Same result. A missing req is not rescued by skipping the recruiter.
- **Price was not the common factor.** HypeLab priced under target, Fanatics in range.
- **Time-to-resolution depends on gatekeeper.** A recruiter with no req sends a polite no in two
  weeks; a founder with no req goes silent. Treat a warm founder thread at `req_reality <= 1` as
  resolved after a few weeks of silence, not as open.

**The rule was stated three times in eight days and never reached the ledger:** Boardy, Jul 13
("champion tied to a defined operating problem"); Hilary, Jul 13 ("let them come back and meet
the would-be boss"); Zach's own HypeLab recoil, Jul 20 ("A persuasion artifact cannot create
internal sponsorship that doesn't exist... gate heavy spec work on a confirmed, open req"). The
Jul 20 recoil is the sharpest statement of H3' in the corpus, written one week after Fanatics
closed. It reached the ledger on Sep 11.

**The contrast that sharpens the rule.** The Jul 20 joe.arcs.care page was a third pre-call
artifact push, same reflex. It worked: Joe's Jul 22 response was "would you be interested in
commercializing this" plus raise-or-bootstrap advice, and the multicall SSOT's next step is an ARV
sprint on Joe's investor-buyout decision. Same behavior, different frame: product to a peer, not a
candidacy into a non-req. The lesson is not "stop building artifacts." It is "never point them at a
role that does not exist." At `req_reality <= 1` the artifact has to be the pilot or the product,
never the JD.

**Mechanical detector for Thread 2:** count artifacts sent after a `req_reality <= 1` signal.
Fanatics: four (cj-brief, chase-intro, fanatics chain page, Jul 2 note). HypeLab: three (survey,
deck, Day-1 self-pitch). Any count above zero after the signal is the pattern firing.

**Booking:** HypeLab enters the ledger as `warm_path=1 · req_reality=1 (effectively 0 after
Oct 21) · laneStatus=ghosted · resolved ~2026-01 (the FTE date lapsing)`, manufactured-role arm.
That arm is now n=2, 0 conversions.

## Reconciling with "Fanatics excluded"

The champion-shortlist exclusion (2026-09-08) and the CLOSED-WARM status (2026-08-28) are
consistent with this post-mortem: Fanatics is excluded as a **target** because there is no req to
target, and the door is **warm** because the people liked the work. Revive triggers: an inbound
from CJ or Chris, a Growth Plus One invite (none has arrived by email as of Sep 11), or a posted
req at `req_reality >= 2` in the growth-exec shape CJ described. Do not re-pitch the bespoke
function into the same Talent door.

## Unconfirmed (do not cite as fact)

- Whether the Growth Plus One invite or Fan Fest passes ever reached Zach by a channel other than
  email (no email exists).
- Whether Chris read the Jul 2 note or the Jul 15 forward (no reply; Mixmax pings confirm no reply,
  not non-receipt).
- Whether Chris and HR ever cut the growth-leader JD after Jul 13.
