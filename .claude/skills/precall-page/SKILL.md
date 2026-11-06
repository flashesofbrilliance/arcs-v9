---
name: precall-page
description: Build the private pre-call prep page for one upcoming call (interview, intro, sales call) from the precall-brief template. Gathers calendar, Gmail, Granola and the JD, fills the brief JSON (identity checks, tripwires, go/stop rule, lines to say, labeled predictions), builds, gates and publishes it as a private Artifact. Use before any call where the counterpart's identity or the stakes warrant a cockpit page.
---

# /precall-page: gather, fill, build, gate, publish

The page is the Bitfury round-one brief (2026-11-06, v19) turned into a template. Parts:

| Part | Path |
|---|---|
| Template (renderer + page layer, no counterpart content) | `src/ui-kit/precall-brief/page.tpl` |
| Data schema | `src/ui-kit/precall-brief/brief.schema.json` |
| Fictional example (copy this to start) | `_ARTIFACTS/precall-brief/example.json` |
| Build + validate + gate | `scripts/precall_brief_build.py` |
| Real briefs (gitignored, never committed) | `_ARTIFACTS/precall-brief/private/` |

Related: `/recoil-prep` fills the war-room SSOT and its ex-ante receipt; `/precall-brief` routes founder meetings into
`/teardown`; `/recoil-close` scores the call afterwards. This skill makes the page you hold open during the call. If a
recoil SSOT already exists for the counterpart, read it first and carry its ex-ante predictions over; don't restart.

## Step 1: gather (breadth, then depth, in parallel)
- **Calendar**: the event, time, link, attendees. Note the link's real host (it must match the platform it claims).
- **Gmail**: `search_threads` on the recruiter and company, `get_thread` on the substantive ones. What was promised,
  what went unanswered, which address each person writes from.
- **Granola**: prior calls (`query_granola_meetings`, `get_meeting_transcript`). Pull what you said, verbatim, so the
  "What the intro notes say you said" card can correct it.
- **JD and documents**: the posting, any PDF, the company's own pages.
- **Identity evidence**: profile pages, company domain, who first named the company and who confirmed it. Keep
  what someone *said* separate from what you *checked*.

## Step 2: fill the JSON
Copy the example to `_ARTIFACTS/precall-brief/private/<yyyy-mm-dd>-<counterpart>.json` and replace every value.

**The verification layer is standard, not optional.** The schema requires all four cockpit sections in stop-loss order:
1. `trip` Tripwires: keep the three standard ones (install or fix anything; personal data or money; a move to another
   channel or code to open) and add any the case adds.
2. `ask` Ask first: the identity check in the first minutes. One question whose specific, checkable answer is a pass,
   plus the strongest proof available (a company-domain email address).
3. `rule` Decide: a go rule and a stop rule with a minute deadline, and what to do on stop (finish politely, send nothing).
4. `say` Say: the opener and the lines for the likely probes, used only once the person checks out.

The Before lane carries the evidence behind that layer: Status (what you sent, what came back, when to re-check),
who the interviewer is per the public record, the recruiter for and against, Odds with error bars and what moves them,
and Checks you can still run.

Rules for every field:
- **Chips are evidence only**: `stated` (someone said or wrote it), `judgment` (no data behind it), `unverified`
  (claimed, not checked). Never use a chip for importance.
- **Every probability is labeled** (memory `label-every-probability-with-its-basis`): the `basis` starts with
  `Stated:`, `Measured:` or `Judgment.` and then the reason. The schema rejects anything else.
- **Predictions are falsifiable**: each resolves Hit or Miss after the call. Put your last Brier score in `after`.
- **Cockpit items**: headline two to four words, one-line lede readable mid-call, bullets for depth, `link` set to the
  exact title of the card that holds the detail.
- **Quotes are faithful to the source** (memory `fact-check-final-pass-vs-transcript`). No em-dashes anywhere.
- `start`/`end` carry the timezone offset; the page uses them to open the current lane and run the countdown.
- When prep is done, set `pinned` (the freeze note: time frozen, and the one or two things left to do). Past the
  freeze, more polishing is soothing, not preparing.

## Step 3: build and gate
```bash
python3 scripts/precall_brief_build.py _ARTIFACTS/precall-brief/private/<file>.json --gate
```
It validates the data (schema, section and lane order, every Details link resolves, no em-dashes), writes the page next
to the data as a full document (doctype, lang, charset, viewport), then runs `scripts/artifact_wrap_lint.py` and
`scripts/page_gate.py --matrix full` on it. Fix the data until it passes; the google-fonts warning is expected.

## Step 4: publish
Publish the built `.html` with the Artifact tool, `icon: "checklist"`. It starts private; it
names real people, so never share it with the counterpart and never commit it. To update, edit the JSON, rebuild, and
republish the same file path so the URL stays. Hand Zach the link.

## Step 5: after the call
Mark each prediction Hit or Miss on the page (the Brier score updates), then run `/recoil-close` for the transcript,
belief updates and the decision receipt.

## Changing the template
Edit `page.tpl` or the schema, rebuild the example
(`python3 scripts/precall_brief_build.py _ARTIFACTS/precall-brief/example.json`), and run `--check` and `--self-test`.
Pre-commit runs `--check`. Tokens inherit from `src/ui-kit/recoil-report/_tokens.css` verbatim; the light palette
re-declares the kit's own names only, never new ones.
