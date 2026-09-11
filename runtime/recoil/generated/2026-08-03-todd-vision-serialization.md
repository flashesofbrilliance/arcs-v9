# Todd, serialized: what I saw, what I heard, what we did, where to grow

**Date:** 2026-08-03
**Purpose:** an active-listening audit, not a plan summary. The test is whether the phased
approach still serves what Todd actually said, or has drifted toward what is interesting to us.

**Sources, and honesty about them:**
- Jul 20 call (Granola `20f5b815`) — read **verbatim**.
- Jul 31 11:05 (Granola `2387379e`) — read **verbatim**.
- Jul 31 2:30 with Daniel (Granola `d471f203`) — read **verbatim**.
- Jul 2 and Jul 9 — **from notes, not re-read.** Lower confidence, marked where used.

---

## WHAT I SAW

Behaviour, not words. What he did with his attention.

- **He took the Jul 20 call from a car on the way to the airport** and still walked the whole
  scope. He did not reschedule. Engagement is real and not calendar-dependent.
- **He never looked at the site during that call.** The artifact has to survive being *heard*,
  not read. Worth remembering every time we build another page.
- **He paid the same day the invoice went out** (Jul 24), and on Aug 3 executed a plan change
  within hours of Daniel's email. When he decides, he moves immediately. Slowness in this
  engagement has never come from Todd.
- **He volunteered a number once, unprompted:** four hours. He has never volunteered another.
- **He deflected exactly one suggestion:** the IT triage agent. Protected the person rather than
  the budget. That is a values signal, not a scope signal.
- **He pulled toward the recommendation engine twice**, both times unprompted, both times while
  still keeping Phase 1 intact.

## WHAT I HEARD

His words.

**On sequencing, which he chose himself:**
> "Let's start with this chatbot. And just keep it simple, routed to the sales manager. And then
> take it from there because, again, getting the rest of the team involved in the technology is
> going to be a huge pain in the ass."

**On what he actually wants, which is not the website:**
> "I could see some sort of agent to help them. As kind of like a personal assistant. Would be
> extremely beneficial for them."
> "Anything to help automate that would... Totally. Huge win. That'd be huge."

His reps: 55 to 60, "they have books, pens, they take appointments, they go in and see these
people." Sugar updates are "like pulling teeth." Changing them is "like turning a cruise ship."

**On capture depth:**
> "If we could have a chatbot that captures, obviously, the typical contact info, but then also
> take it one step further where it captures maybe the application... the resin they're currently
> using. That would be huge."

**On the metric:**
> Zach: "have you guys ever lost any deals because of that?"
> Todd: "For sure. We try to keep it to within, like, four hours."

**On the thing he said quietly, in the middle of a tangent:**
> "It's a very successful company, but it's very old school. And it's prime for a facelift."
> "It's a well-oiled machine, but that's not necessarily a good thing for the future of the
> company. But then again, I don't think we, as in the person that I work for, will own the
> company forever."

**On his people:**
> On the 18-year IT generalist: "I kind of leave him alone. Because he's got a family... some
> people are just kind of left alone."

## WHAT WE DID

| He asked for | We did | Verdict |
|---|---|---|
| Chatbot, simple, to the sales manager | Built, live on dev site | Followed |
| Capture application and current resin | Branch A/B plus QATF001 mapping | Followed |
| A light version of the product-dev form | Field mapping delivered | Followed |
| Recommend an offset for a competitor grade | Deferred, blocked on image tables | Followed, correctly slow |
| An assistant for the reps | Logged to Later, not built | Followed his sequencing |
| Voice or photo into Sugar | Logged, not built | Followed |
| Left the IT guy alone | Dropped after one mention | Followed |
| Four-hour callback | Nothing | **Missed** |
| Company prime for a facelift | Nothing | **Missed** |

Two things also happened that he did not ask for and should be checked: we ran a SugarCRM config
audit and a 74-case AI safety eval. Both are defensible, because both protect him from failures he
would carry. But neither came from his mouth, so both need to earn their place on the next call
rather than be presented as obviously necessary.

## WHERE THERE IS ROOM TO REFINE, GROW, ITERATE

### Refine: build the thing he actually measures.
Four hours is the only business number he has ever volunteered. Nothing we have built reports on
it. When lead delivery goes live, stamp the Sugar lead and show him time-to-first-touch against
close-won and close-lost, using data he already owns. Nearly free, and it is the number he would
repeat to his owner.

### Grow: the wedge is not the goal.
The chatbot is what he accepted **because it avoids the reps**. The reps are where he feels the
pain. Everything built this month serves the visitor. That is correct for Phase 1 and becomes
drift if Phase 2 is chosen by what is technically adjacent (more flows, more SEM pages) rather
than by what he called huge.

**The test before proposing Phase 2:** does it reduce work for a 58-year-old rep who does not want
to use technology? If not, it is our roadmap, not his.

### Iterate: the frame we have never said back to him.
"I don't think the person I work for will own the company forever" reframes the whole engagement.
Efficiency is the surface. Making the company **legible and instrumented to a future buyer** is the
deeper read, and Todd, as effective CMO and CFO in a family office, is exactly who would carry it.

Do not put this in a client artifact. It is his to raise. But it should shape how Phase 2 is
framed, because "instrumented demand capture" and "a chatbot" are different conversations, and the
first is the one that matches what he told us.

### Questions worth asking, in his language
1. "Once leads start landing, do you want to see how fast they get picked up? You mentioned four
   hours."
2. "Of the rep ideas, voice notes into Sugar or a photo of handwritten notes, which one would
   actually get used by the hardest guy on the team?"
3. "When you said the company is prime for a facelift, what does good look like a year out?"

---

## What would falsify this reading

Written down so it can be checked rather than believed:

- If Todd, unprompted, pushes for more website or SEM work before any rep-facing work, then the
  "wedge is not the goal" reading is wrong and he genuinely wants demand capture first.
- If he shrugs at time-to-first-touch when offered, then four hours was conversational, not a
  metric he manages to.
- If he never raises ownership or the future of the company again across two more calls, treat it
  as a passing remark rather than a frame.
