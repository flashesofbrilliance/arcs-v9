<!--
session: claude-monday-prep-handoff
branch: claude/monday-prep-handoff
head: 874f14e4
created_at: 2026-10-28T00:15:02Z
-->
> Monday guide follow-up session (2026-10-27, part 2): nav click tracking shipped on the guide; analytics and email-open signals read.

## What changed
- PR 1825 merged (head 0866ac1a, merge 445a46b8): public/monday-guide.html fires a Vercel custom event `nav_click` {label, href} on nav link clicks. Live behind the passcode (verified with an unlock cookie).
- Merged over a fe-smoke check stuck pending with 0s run time (Actions limit), on Zach's explicit "merge it anyway". Receipt 2026-10-27--monday-guide-nav-events-pr1825--ZH records that.
- Trap order T1, T2, T5, T3, T4 kept as submitted (golden.json order), per Zach.

## State
- Vercel analytics query API returns 404 "Web Analytics not found" for arcs-v9 (by name and by ids); /_vercel/insights/script.js serves 200. Custom events need the Pro plan; unconfirmed whether nav_click records.
- Mixmax shows bulk opens and clicks at 5:20pm and 5:40pm from Virginia: read as Safe Links style scanners, not reader interest.

## Decisions
- Zach: keep trap order as submitted; merge PR 1825 over the pending check.

## Open
1. Zach: check Vercel dashboard (arcs-v9, Analytics, Events) for nav_click; it is the only human-only signal on the guide.
2. Optional: relabel the guide's one-answer bullet to "What one finished answer looks like (traced):".
3. Branch claude/monday-prep-handoff (fragment 874f14e4 plus this one) is unpushed.

## Next action
Wait for a reply from Sam or the panel; read nav_click in the Vercel dashboard.

## Cold-start recipe
- Read _ARTIFACTS/forge-monday-fde/walkthrough/2026-10-26-recoil-close.md and memory project_monday_fde_strategic_deployments.
