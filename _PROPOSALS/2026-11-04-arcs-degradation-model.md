# ARCS degradation model: what still works as tending stops (2026-11-04)

Status: PROPOSED. Read-only analysis. Nothing was changed, scheduled, merged or published.
Source: Will Binns, *Mru: A Fault-Tolerant Operating System for Thousand-Year Autonomous Operation*, v1.1.1
(October 2026), and its companion simulation at https://dusk.mru.space/. Prior art: memory
`control-integrity-described-vs-wired` (a control that never runs is not a control).

## Bottom line

Mru's rule is to treat decline as the normal state and plan the descent, not defend the peak. dusk measures the
payoff: a fallback that runs itself adds **nothing (1.00x)** while a ground team is still there to do the same thing
by hand. The whole gain comes from the years after support ends.

Applied to ARCS, the result is uncomfortable. Almost all of its automation is a ground team in disguise: it
**reports** to Zach and waits. The session-start sentries, the pre-commit gates and the morning note all fire only
when Zach is in a session or reading. In the "no tending" phase they are worth about zero. Very little in ARCS
**acts** on its own, and the things that keep the product alive for a visitor (the deployed site, the debrief cron,
the paid model calls) carry decay clocks that nothing watches unattended.

So the work is not more gates. It is three things: name a small Layer 0 that must survive zero tending, put a date on
each of its decay clocks, and rate each automation by what it does when nobody reads its output.

## Decisions waiting on Zach

1. **Adopt the four phases below** as the planning frame for long-horizon work (or amend them).
2. **Confirm the Layer 0 list.** Anything not on it is allowed to rot when tending drops.
3. **Pick the first decay clock to date.** Recommended: model id retirement, because it breaks the compass with a 502
   and the one watch on it skipped this morning (`model-drift: no ANTHROPIC_API_KEY; skipped`).
4. **Kill rule for reporters.** An automation that only reports and has had no reader act on it in 60 days gets
   composted or turned into one that acts. Yes or no.

## The four phases (by Zach's attention, not by time)

Mru steps down by remaining power: Full Operations, Reduced Science, Core Operations, Survival, Beacon. ARCS's
declining resource is attention and budget (the weekly token cap and the shared Anthropic budget, per memory
`anthropic-api-budget-shared-cap-ci-drain`).

| Phase | Tending | What runs | What is allowed to decay |
|---|---|---|---|
| 1. Full | Daily sessions | Everything: hooks, sentries, pre-commit, molts, receipts, the backlog | Nothing on purpose |
| 2. Reduced | Weekly | Product surfaces, receipts on each merge, the weekly token routine | Handoff ceremony, dreaming passes, atlas and lattice regeneration, rotting loops |
| 3. Core | Monthly | Layer 0 only, plus one monthly check of the decay clocks | All operator tooling, artifacts, the induced backlog, memory growth |
| 4. Beacon | None | Whatever is still deployed and paid for: the live site says "I am still here" | Everything that needs a human or a running Mac |

The test for each phase: **what is the minimum useful output, and what has to be true for it to keep coming?**
Phase 4 is the honest one. Today it is "arcs.care stays up until a bill, a domain or a model id lapses", and nobody
knows which comes first.

## Layer 0: the part that must survive zero tending

Mru's Layer 0 is a verified interpreter of about 200 to 500 instructions, small enough to prove. ARCS has 556 wired
tools and no list of the few that must outlive the rest. Proposed Layer 0:

| Item | Why it is load-bearing | Already locked? |
|---|---|---|
| Git history on GitHub (`flashesofbrilliance/arcs-v9`) | The event record; everything else can be rebuilt from it | Yes: squash and rebase merges are refused by repo setting |
| `decision_receipt` ledger (Supabase `xbbpiryokswwvcrcutge`) | What was decided and believed, at the time | Yes: a trigger refuses UPDATE and DELETE (the closest thing to Mru's read-only constitution) |
| The ROM primitives (CLAUDE.md) | The constitution: what ARCS may never do | By convention only; any session can edit the file |
| The live site on Vercel (`arcs-v9` project) | The beacon: proof ARCS still exists | Depends on billing, domain and model ids (below) |
| Off-machine encrypted backups | Recovery if the Mac or an account is lost | Yes, two copies; passphrase in Passwords (memory `offmachine-encrypted-backups-location-and-restore`) |

Everything else (operators, scripts, skills, hooks, artifacts, memory) is Mru's "legislation": useful, changeable,
and allowed to fail without killing the system. The one gap worth closing is the third row: the constitution is
locked only by habit.

## Decay clocks (ARCS's equivalent of a power supply that only ever declines)

Mru's master constraint is a power source on a fixed half-life. ARCS has several clocks of the same kind. Each runs
whether or not anyone is watching.

| Clock | What breaks when it runs out | Who watches it today | Date known? |
|---|---|---|---|
| Pinned model ids in `src/lib/claude-models.ts` (e.g. `claude-haiku-4-5` for compass fast mode) | Compass and brief calls fail; the route returns 502 | `model_drift_check.py` at session start, which needs `ANTHROPIC_API_KEY` and **skipped on 2026-11-04** | No |
| Anthropic budget and key | Every paid route | Nobody unattended | No |
| `arcs.care` domain registration | Every surface on about 95 aliases | Nobody; `whois arcs.care` returned no expiry line from this machine | No |
| Vercel and Supabase billing (card on file, plan limits) | Site and ledger | Nobody unattended | No |
| Self-hosted Actions runners on this Mac (3 launchd agents) | All six scheduled workflows; they ran daily through 2026-11-01 only because the Mac was on | Nobody; a common-mode fault, like Mru's shared power rail | n/a |
| Memory index load cap (22,353 of 24,576 bytes, 91%) | New memories stop loading at session start | The global SessionStart hook (only when a session starts) | Roughly, at current growth |
| Next.js and Node support windows | Builds stop working | Nobody | Knowable |

Dating these is cheap and mechanical. It belongs in a script, not in judgment.

## Automations scored by what they do after tending stops

dusk's question, asked of each one: **does it act, or only report? And does it run without Zach in a session?**
This is a judgment rubric, not a measured ratio like dusk's; the categories are what matter.

| Automation | Host | Runs with no session? | Acts or reports | Value in phase 4 |
|---|---|---|---|---|
| SessionStart sentries, pulse, drift, gait, loops | Claude Code hook | No | Reports | None |
| PreToolUse canon write guard | Claude Code hook | No | Acts (blocks) | None (there are no writes to guard) |
| Pre-commit gates (`scripts/git-hooks/pre-commit`) | Local git | No, only on commit | Acts (blocks) | None (there are no commits) |
| Morning open-loops note | Claude scheduled task | Needs the desktop app and budget | Reports | None |
| Scheduled workflows: advisory gates, a11y nightly, no-squash, branch pin, governance, intent | Self-hosted runners on this Mac | Only while the Mac is on | Report (red checks) | None |
| `canon-propagation` (daily 21:00), `memory-timecapsule` (every 30 min), `gigi-stream` | launchd on this Mac | Only while the Mac is on | Act on local files | Low |
| `/api/cron/debrief` (daily 14:00 UTC) | Vercel cron | Yes | **Acts**: sends due debrief emails to users | **Real** |
| The deployed site and compass | Vercel | Yes | **Acts**: serves visitors | **Real, until a decay clock runs out** |

Two rows out of eight keep delivering when Zach is gone, and both live on Vercel. That is where the long-horizon
effort earns the most. This is dusk's finding again: the gain is in the years after support ends, and only things
that act on their own can collect it.

This does not mean the reporting tools are wrong. In phase 1 they are the self-check, and dusk shows self-check is
worth paying for: a lone processor that does not check itself produces a wrong result on 87% of missions, against
20% for one that does. The point is narrower: **reporting tools are phase-1 tools, and they should not be counted as
durability.**

## What this proposal does not claim

- The phases and scores are a planning frame, not a simulation. Nothing here was measured the way dusk measures.
- Domain expiry, billing renewal dates and the Supabase plan were not verified. They are listed as unknown on purpose.
- "Value in phase 4" assumes no human at all. Most real months sit in phases 1 to 3.
- The Mru parallel is structural for Layer 0, decay clocks and the act-or-report split. It is not a claim that ARCS
  is a spacecraft.

## Proposed next steps (each small, each with a stop rule)

1. **Decay clock script** (`scripts/decay_clocks.py`, read-only): print each clock with its date or `UNKNOWN`. Stop
   rule: if it takes more than one session, cut it to the three clocks that break the site.
2. **Move the model-retirement watch to a host that runs unattended.** It does not need a session; a Vercel cron or
   the health route could probe each `MODELS` id daily and alert by email. Stop rule: one probe, one alert, no dashboard.
3. **Write the beacon down.** One line on `/trust` or the health route that says what ARCS keeps doing with no one
   tending it, so phase 4 is a stated promise, not an accident.
4. **Run the kill rule once** over the reporting automations above (decision 4), and record the fates in one receipt.

## Loop stage

| Stage | State |
|---|---|
| Proposed | This file |
| Assayed | Not yet: needs decisions 1 to 4 |
| Scored | Not yet |
| Adopted or composted | Not yet |
