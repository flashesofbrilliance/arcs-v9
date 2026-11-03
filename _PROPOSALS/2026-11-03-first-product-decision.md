# First product to sell: decision page (2026-11-03)

Status: PROPOSED, waiting on Zach's yes or no. Nothing was built, sent or published to make this page.

Prior art: `_PATTERNS/2026-07-13-frontend-monetization-queue.md` (July ranking), backlog rows `agent-receipts-audit-offer` (DONE) and
`agent-receipts-audit-first-conversion` (HOLDING, its one dependency is now DONE), memories on free-to-hold / metered-to-fire,
refusal to overclaim, and cut not add.

## The ask

**Yes or no: spend today putting the Agent Receipts Audit in front of 10 named buyers.** It is already built and live. The work
today is outreach drafts, not product.

## What runs today (checked 2026-11-03)

| Thing | Proof it runs | Ever paid? |
|---|---|---|
| Agent Receipts Audit offer, good.arcs.care/audit | 200 live. Two fixed scopes, sample report at /audit/sample, two worked cases | No. Prices hidden ("quoted after a scope call") |
| Free repo check, good.arcs.care/audit/check | Ran it today on anthropics/claude-code: scored 30 commits, 27% explain themselves. Runs in the browser, result has its own shareable link (`?repo=owner/name`) | Free by design |
| Lead capture, arcs.care/advisory | `/api/lead` stores a Lead, emails the admin, returns a booking link (Google Calendar) | Prod `Lead` table: **1 advisory lead ever (2026-06-29)**, 9 waitlist (last 2026-10-04) |
| PRL chatbot to CRM build (client work) | Sandbox lead delivery and rep routing worked (2026-09-01 live demo). Prod go-live not proven: empty-email guard failed 2026-10-09 | **Yes, about $6,200 to date.** Todd funds no more phases until it helps his team |
| README to video (RET, Dioptra, monday panel cut) | Three videos shipped. Gates 1 and 3 exist (`scripts/readme_video_check.py`); stages 1 to 3 are hand work | No |
| OSS family (germinate, rosetta-shell, resume-tailor-skill, rfp-engine, arcs-field-scan, 10+ more) | 23 public repos, 0 to 1 star each; landing pages live | No, and they should not be (free to hold) |

Plain read: the only money so far came from hands-on client work (PRL). Inbound does not convert by itself: one advisory lead in
four months. So whatever ships first needs outbound, by Zach, to named people.

## Four candidate products

**1. Agent Receipts Audit (service, fixed price).**
Buyer: an engineering lead or CTO at a 5 to 50 person team that ships with coding agents. Job: "When an agent says it is done,
show me the record proves it, and show me where it does not." Proof: the live page, free check, sample report, the published cold
reconstruction of our own incident. Smallest sale this week: the "Audit" scope, one repo and one window, two weeks, async.

**2. Small-business AI ops sprint (service, the PRL model).**
Buyer: an owner-operator whose website leads die between the chat widget and the CRM. Job: "Every lead reaches the right rep, and I can
see it." Proof: PRL paid, routing worked in sandbox. Weak spot: the reference client is not live in prod, so the case cannot be told as
finished. Smallest sale: a fixed-price phase 1 with a working slice inside about five weeks (box the discovery; sign audit and phase 1
together).

**3. Proof-of-work walkthrough video (done for you).**
Buyer: a technical candidate with a take-home, or a maintainer with a launch. Job: "Turn my checked README into a 2 minute video that
claims nothing the README does not." Proof: three shipped videos and two gate scripts. Weak spot: most stages are hand work and the voice
step costs credits, so margin per video is thin and the buyer is price-sensitive.

**4. The open tool family as a catalog.** Not a product. Keep it free and MIT. Its job is to be the proof and the funnel that points at
1 to 3. Charging here adds the friction the model says never to add.

## Recommendation: ship #1 first

Why this one:
- **Zero build.** Page, free check, sample report, lead route and booking link all run today. The July queue's blocker for this kind of
  work (no front door) is gone.
- **The free check is the opener.** Run it on a prospect's public repo, send them their own score link. That is a personal, true,
  two-minute first touch that needs no deck.
- **It is the brand promise, sold.** It measures what the record can prove and labels the rest "not verified". It refuses to
  overclaim by design.
- **It fits the job search.** Pitch it as a craft practice, not a pivot. A hiring manager who sees it sees FDE work done in the open.

What could sink it (said up front):
- The buyer and the price are unvalidated. One advisory lead ever, and no audit has been sold.
- The only case is our own incident, and the person running the audit is the operator in it. The page already says this.
- An eng lead may hear "audit" as compliance. The page says it is not a certification; the first call has to land that.

### Price hypothesis

| Scope | List (benchmark guess, from the backlog row) | Founding offer, first 3 buyers |
|---|---|---|
| Audit: one repo, one window, 2 weeks async | $3,500 | **$2,500**, in exchange for written permission to publish a redacted case |
| Audit + gate: plus receipt schema, CI check, second cold run | $6,500 | $5,000 |

Keep prices off the page (current decision) and quote on the scope call. The guess is validated or killed by 3 buyer conversations,
which is the gate the backlog row already sets. Invoice first; no Stripe build.

### One-day plan (about 4 hours of Zach's time)

1. **Pick 10 named prospects (1 hour).** Eng leads Zach already knows or is one hop from, at small teams with a public repo that shows
   agent commits (an AI credit line in commit messages). Warm first, cold second.
2. **Score each repo with the free check (20 minutes).** Save each `?repo=` link. Drop any repo that scores high and has nothing to find.
3. **Draft 10 short notes (Claude drafts, 1 hour).** First person singular. One line on what the score shows, the link, one question:
   "Which week would you least like to explain from memory?" Link to /audit, ask for a 20 minute scope. No price in the first note.
4. **Ex-ante receipt before any send (10 minutes).** One `decision_receipt` row (ADR-068): what we expect (2 or more replies, 1 scope
   call within 10 business days) and what would prove us wrong.
5. **Zach reviews and sends (1 hour).** Zach sends, not Claude.
6. **Close the loop.** On any reply, log it against the same receipt; book through the existing calendar link.

Kill rule: if 10 targeted sends get 0 scope calls in 10 business days, park #1 and move the same day of effort to #2 (warm SMB intros,
starting with fixing PRL's prod go-live so the case is true).

## Not in this page

No new page, pricing table, Stripe, catalog site or landing copy. Each of those waits until one buyer says yes.
