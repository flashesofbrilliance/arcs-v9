# /recoil-report

> **Two things share this name.** This command is the single-session, cheap path (one
> transcript in, one report out). `.claude/workflows/recoil-report.mjs` is the multi-agent,
> ~350k-token version for a full pre-call dossier on a person; run it only on explicit opt-in.
> Inside the Receipt Loop (see `runtime/specs/tool-catalog.md`), prefer `/recoil-prep` and
> `/recoil-close`, which write to the counterpart's account record; this command is the
> standalone, no-SSOT variant.

> Generates an ARCS Recoil Report from a Granola call transcript, builds it into a deployed
> preview, smoke-tests it, and emails the link. Run manually right after a call, or on a
> recurring schedule via `/schedule` (Claude Code's own cron — see "Scheduling" below).
>
> **Real architecture note:** Granola and Gamma are reached through MCP connectors available
> in *this chat session*, not a public REST API the deployed Next.js app can call on its
> own. So this is a Claude-Code-session skill, not a Vercel serverless cron job — the
> recurring version runs this whole skill on an interval, it doesn't deploy a backend job
> that runs unattended forever.

## Governing spec

`runtime/specs/recoil-modes-v1.md` — defines Reverse Listening and Deep Recall passes, and
the segment-count cadence (`max(3, round(sqrt(duration_minutes)))` segments per pass).
DRAFT status — not canon-ratified. If Zach corrects the "1/(duration)" cadence reading,
update that spec first, this skill just implements whatever it currently says.

## Step 1 — Find the call + pull the transcript

1. `mcp__<calendar>__list_events` for events that ended in roughly the last 2 hours (or
   whatever window makes sense for how this was invoked — manual run vs. scheduled poll).
2. Match against Granola: `mcp__<granola>__list_meetings` (or `query_granola_meetings` if
   list doesn't surface it) for a meeting with the same approximate end time / attendees.
3. `mcp__<granola>__get_meeting_transcript(meeting_id)` for the verbatim transcript.
4. Compute `duration_minutes` from the calendar event's start/end. This drives Step 2's
   segment count.

**If no new ended call is found:** stop here, report "no new call to process," don't
fabricate a report. This is the most likely failure mode on a scheduled run — most polling
windows won't have a fresh call.

## Step 2 — Run both Recoil Protocol passes

Per `runtime/specs/recoil-modes-v1.md`:
- Segment the transcript into `max(3, round(sqrt(duration_minutes)))` chunks.
- **Reverse Listening pass**: read end-to-start. Extract the actual close, then work
  backward flagging divergence between what the call seemed to be building toward (read
  forward) and where it landed (read backward).
- **Deep Recall pass**: read start-to-end, scored against the pre-call expectation (pull
  the matching PrepSession via `prisma.prepSession` if one exists for this call, otherwise
  note "no pre-call expectation captured" rather than inventing one).
- Merge both passes' findings into the `RecoilReportData` shape (see
  `src/document/screens/RecoilReport.tsx` — `RecoilReportData` interface): cover,
  loadBearingQuote, callWalk, signalThreads, scenarios, riskFlags, protocol.

## Step 3 — Gamma wireframe (cheap, rough, blocking-and-tackling artifact)

Call `mcp__<gamma>__generate` (or `generate_from_template` if a recoil-shaped template
already exists in your Gamma workspace — check `get_themes`/folders first) with the Step 2
findings as input. This is a **rough pass**, not the final artifact — its job is to let you
eyeball the structure cheaply before the real document gets built in Step 4. Don't spend
more than one generation call on it; if it's wrong, fix it in Step 4's real component
instead of iterating on the Gamma draft.

## Step 4 — Render through the real design system

Write the merged `RecoilReportData` object to
`runtime/recoil/generated/<reportId>.json` (reportId = a short slug, e.g. the call date +
first attendee surname). This repo's `/recoil/[reportId]` route
(`src/app/recoil/[reportId]/page.tsx`) reads that file and renders it through
`RecoilReportFromData` — the same canonical atomic-design kit (`src/document/`,
`src/ui/tokens.ts`) every other document type in this app uses. **Do not use MUI or any
other component library** — this repo is inline-styles-only, no exceptions (see
CLAUDE.md/AGENTS.md). The "atomic elements" referred to in the original ask are this kit's
existing patterns (CoverBlock, Timeline, SidelineList, ScenarioStack, AsideBox,
ProcessSteps), not an imported library.

Commit the generated JSON (it's a real artifact, not a build output — keep it in git).

## Step 5 — `/debug` loop + Playwright smoke test

1. `npx next build` — must be clean before anything else.
2. Start a preview server (`preview_start` MCP tool, or `npm run dev`).
3. `npx playwright test` (config: `playwright.config.ts`, spec: `tests/smoke.spec.ts`).
   **Run this against a deployed preview URL** (`SMOKE_BASE_URL=https://...vercel.app`),
   not local dev — local dev is missing `DATABASE_URL`/`AUTH_SECRET` and will show false
   failures on `/`, `/dashboard`, `/history` unrelated to anything this skill touched. Add
   the new report's actual route (e.g. `/recoil/<reportId>`) to the `ROUTES` array in
   `tests/smoke.spec.ts` for this run, or pass it as a one-off check.
4. If smoke tests fail: read the actual error (don't guess), fix, rebuild, re-test. Loop
   until clean. Don't skip a failing test to "make progress" — this step exists specifically
   to catch what step 4 might have broken.

## Step 6 — Deploy + email

1. Commit everything (the generated JSON, any code changes from Step 4/5's fixes).
2. `vercel deploy` (preview, not `--prod`).
3. Confirm the deployment is `READY` and the new report route returns 200
   (`curl -s -o /dev/null -w "%{http_code}" <url>/recoil/<reportId>`).
4. Email the link via the `resend` MCP/skill (`send-email`) — to Zach, subject naming the
   call (e.g. "Recoil Report ready — <call title>"), body with the direct
   `<preview-url>/recoil/<reportId>` link. Use the same `from` address pattern already in
   this repo's other emails (`ARCS <noreply@arcs.care>`).

## Scheduling (optional — only if a recurring run is wanted)

Use the `/schedule` mechanism (Claude Code's own cron) to re-run this whole skill on an
interval — e.g. every 30 minutes during working hours. Be aware: scheduled jobs in this
harness auto-expire after 7 days and need re-creating; this is a session-level convenience,
not durable infrastructure. For anything more permanent, this would need to move to a real
backend service with its own Granola/Gamma API credentials — a different, larger project.
