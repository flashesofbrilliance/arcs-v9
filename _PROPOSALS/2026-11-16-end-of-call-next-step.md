# End-of-call next step (sketch, not built)

**Status:** PROPOSED, waiting on Zach. Nothing is built.
**Replaces:** the live floor light (`tools/floor-light/`), parked after the projection-map pilot found no
in-call signal (P5 null, p 0.74 on 998 turns).
**Evidence it rests on:** the pilot's one lean is per call: calls that went nowhere had more long, dense
turns (p about 0.05). The ledger lists "naming a next step before hanging up changes outcomes" as a
CANDIDATE (the Room Playbook experiment), untested. So this is an experiment, not a fix.

## The move

In the last minutes of a call, Zach names one next step out loud, with three parts:

| Part | What it is | Example |
|---|---|---|
| Action | one concrete thing, not "stay in touch" | "send the two case studies" |
| Owner | a named person | "me" or "you" |
| Date | a day, not "soon" | "by Thursday" |

Line to say: *"Before we go, can we name one next step? I'll send X by Thursday, and you'll Y by Monday."*
If they will not name one, that is the answer; log it, do not push.

## The precondition: verify before you advance

The next step serves whoever asked for it. In the Bitfury impersonation call, the "next step" (a
same-day CV, a quick second meeting) was the attacker's ask. So the move is gated on the trust tier the
pre-call page already computes (T0 self-asserted up to T4 company-confirmed):

- **T2 or above (verdict `go`):** name a next step as above.
- **Below T2 (verdict `hold` or `stop`):** the only next step is verification, owned by them:
  *"Happy to keep going. Could you send the next step from your company address, so I can put it on my calendar?"*
  Never accept their ask (a CV, a file, an install, a move to another channel) as the next step.
  The three standard tripwires still apply.

## Where it lives (no new app)

1. **Pre-call page** (`precall-page` skill, the precall-brief template): add a `close` section to the
   cockpit after `ask`, filled from the brief: the trust tier, the one next step Zach wants (written
   before the call, as a prediction), and the verification line when the tier is below T2. Optional:
   the section highlights 5 minutes before the calendar end time. Page-side only; no audio, no network.
2. **Post-call close** (`/recoil-close`): one new field, *next step named?* (yes, no, verification-only),
   read from the last 3 minutes of the transcript: an action, an owner and a date expression. It also
   records whether the named step matches the one predicted on the pre-call page.

## How we would know it works (pre-register before the first use)

1. **Baseline first, from existing transcripts:** how often does Zach already name a dated next step
   in the last 3 minutes? If it is already most calls, the prompt adds little; stop there.
2. **Then the experiment:** use the `close` section on every verified call for a fixed window (say 15
   calls). Outcome: the call advanced, counted only for verified counterparts (an unverified
   counterpart's follow-up never counts, per the ledger's Bitfury spark).
3. **Kill rule, written now:** if calls with a named next step advance no more often than baseline calls,
   remove the section.

The baseline and the detector belong with the projection-map pilot's data (branch
`claude/voice-branded-mini-app-1ne11t`), not in this repo's main line.

## Open for Zach

1. Go or no-go on the experiment.
2. The 5-minute highlight: on the page, or no timer at all?
3. Window size: 15 verified calls, or a fixed number of weeks?
