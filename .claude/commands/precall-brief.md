# /precall-brief

> Pre-meeting trigger companion to `/teardown`. Where `/teardown` needs a website URL and a
> bio PDF handed to it, `/precall-brief` finds those inputs itself by reading the calendar,
> the person's correspondence history, and any prior Granola meetings — then infers the
> **register** (friend vs. cold intro) and the **intent behind the meeting** from that context
> instead of asking cold, and hands a fully-briefed context package into `/teardown`'s Step 0
> onward. Run manually before a specific meeting, or on a recurring poll via `/schedule` (see
> bottom).

**Usage:** `/precall-brief` (polls calendar for the next unbrief­ed external meeting) or
`/precall-brief <attendee name or email>` (target one specific upcoming meeting directly).

## Step 1 — Find the meeting

1. `mcp__<calendar>__list_events` for events in the lookahead window (default: next 24
   hours; widen if nothing found and this is a manual invocation, not a scheduled poll).
2. Filter to events with at least one external attendee (email domain not matching Zach's
   own) and a real 1:1 or small-group shape — skip large internal syncs, recurring standups,
   anything without a named external counterpart.
3. **If none found:** stop here, report "no upcoming external meeting needs a brief," don't
   fabricate one. Same guardrail as `/recoil-report` Step 1 — this is the most common outcome
   on a scheduled poll and that's fine.
4. If multiple qualify, brief the soonest one first; note the others so nothing gets silently
   skipped on a scheduled run.

## Step 2 — Gather situational context (this is the "losslessly tuned" part)

For the identified attendee, pull every available signal before inferring anything:

1. **Calendar event itself** — title, description, and location/link. This is usually the
   single strongest intent signal: "Boardy Intro" or similar connector-platform language
   almost always means cold register (see `daniel.html`/`labella.html` precedent — both were
   literally labeled that way in the calendar). "Catch up," a first-name-only title, or a
   recurring/personal-sounding title leans friend register (see `danny.html` precedent).
   If the description names a specific ask ("discuss X," "re: Y opportunity"), that's the
   meeting's intent — thread it through to which teardown sections get emphasis in Step 4.
2. **Email history** — `mcp__<gmail>__search_threads` for the attendee's email address.
   Thread count, tone, and date range are the register signal when the calendar title is
   ambiguous: months of casual back-and-forth reads differently than a single connector-
   platform intro email from last week. Pull the most recent thread's content if it exists —
   it may directly state the meeting's purpose, which is better than inferring it.
3. **Prior Granola meetings** — `mcp__<granola>__list_meetings` /
   `query_granola_meetings` for past meetings with this attendee. If any exist, pull the
   transcript(s) — this is the highest-quality signal available: real prior quotes,
   confirmed relationship history, and (if a `/recoil-report` was run on a prior call) an
   existing Recoil Report to build on rather than start cold. **If a prior report exists,
   don't redo work it already did — extend it.**
4. **Bio source** — if no PDF was handed to this run, check the calendar event and recent
   email threads for a LinkedIn URL or attached profile. If genuinely nothing is available,
   proceed with whatever's inferable from the attendee's own company website (About/Team
   page) and flag the bio section's confidence as lower than usual — don't block the whole
   brief on a missing PDF, but don't silently upgrade a thin bio to full confidence either.
5. **Website** — if not stated explicitly, infer from the attendee's email domain (strip to
   the apex domain, verify it resolves and is the actual company site, not a redirect or a
   generic ESP domain like a Gmail/personal address with no company site — if personal email
   only, ask rather than guess a website).

## Step 3 — Decide register + intent (explicit, not silent)

Synthesize Step 2's signals into two explicit calls, stated in your own output before
building anything (this is Court-lens discipline — don't let an inferred judgment call hide
inside the artifact unstated):

- **Register**: friend / warm-existing-relationship / cold-intro / unknown. If the signals
  conflict (e.g., a "Boardy Intro" calendar title but six months of warm email history since),
  say so and pick the more recent, higher-fidelity signal — real correspondence beats a
  calendar label. If genuinely unclear, this is the one place to still ask rather than guess,
  same as `/teardown` Step 0.
- **Intent**: what does this specific meeting appear to be for? (e.g., "revisiting a
  dormant lead ahead of a stated fundraise close," "pure catch-up with a friend's new
  venture," "sales-oriented intro via a mutual connector"). This determines which of
  `/teardown`'s section 04 hypotheses (or section 03 quick-wins) get foregrounded — an
  artifact for a fundraise-adjacent catch-up should lead differently than one for a cold
  sales intro, even if the underlying site teardown is identical.

## Step 4 — Hand off to `/teardown`, pre-loaded

Invoke `/teardown <website> <bio-source>` but skip its Step 0 (register is already decided)
and Step 1 (bio is already gathered) — carry this step's findings directly into its Step 2
onward. Additionally thread the **intent** finding from Step 3 into artifact drafting:

- If intent is relationship-maintenance (friend catch-up, no clear ask): keep section 04
  genuinely speculative and light — don't manufacture urgency that isn't there.
- If intent is a specific stated ask (fundraise timing, a hiring problem, a named decision):
  make sure section 04's hypotheses and section 05's next-steps directly address that ask,
  not a generic version of "where might our work interlock."
- If a prior Granola transcript exists (Step 2.3): section 04 can use real attributed quotes
  the way `daniel.html` does, instead of `kiko.html`'s hedged "no conversation yet" framing.

## Step 5 — Everything downstream is `/teardown`'s job

Gauntlet (BAR/LAB/KKL/COURT/Funhouse), style rules, deploy mechanics, domain verification —
all inherited unchanged from `/teardown` Steps 2 onward. This skill's entire value-add is
Steps 1-4 above: turning "here's a URL and a PDF" into "here's who this is, why we're
meeting, and how warm the relationship actually is" without the user having to hand-assemble
that context every time.

## Scheduling

Same shape as `/recoil-report`'s scheduling section: wire via `/schedule` (Claude Code's own
cron) on a recurring poll — e.g. every morning, or every few hours during working hours.
Scheduled jobs in this harness auto-expire after 7 days and need re-creating. Suggested
cadence: once daily is enough for most calendars; tighter polling only helps if meetings get
added same-day with little lead time.

**Idempotency guard for scheduled runs:** before drafting anything, check whether a brief for
this attendee/meeting already exists (e.g., a `public/<name>.html` committed in the last few
days, or a subdomain already wired in `next.config.ts`) — don't regenerate and redeploy a
brief that was already produced for the same upcoming meeting.
