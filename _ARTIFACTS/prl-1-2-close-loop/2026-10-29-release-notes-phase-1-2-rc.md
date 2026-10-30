# PRL phase 1.2 release candidate: release notes (2026-10-29)

Scope: the chatbot lead pipeline, Tidio (staging site) to Zapier to SugarCRM.
Everything below ran against the **sandbox** (prlresinstest). Nothing touched production Sugar.

## Release status

| Item | Status |
|---|---|
| Release candidate | Zap 376827315 **v9**, Tidio flow 7752845 (active) |
| Automated check | 32 of 32 pass (`prl_uat_harness.py` on `prl-rc-e2e-fixtures.json` + `rc-actuals-2026-10-29.json`) |
| Zach's approvals (this session) | Tidio call-me questions added; repeat-visitor test run; fixes for the state warning and the reminder recipient |
| Todd's sign-off (UAT) | **Not yet given.** This RC is ready for his review |

## What changed

| Version | Change | Why |
|---|---|---|
| Tidio flow 7752845 | Call-me branch now asks company and state (after name, phone, email) | Sugar needs both fields to route the lead |
| Zap v8 | Job title and industry extraction rewritten | ZoomInfo data arrives as flattened text, so every lead had been saved as "Not specified" |
| Zap v9 | If the visitor's state isn't recognized, the lead's Lead Source Description now reads "State not recognized: '<what they typed>' (routed to CA by default, please confirm)" | Before this, a non-US region was routed to the CA rep with no flag |
| Zap v9 | The new-lead 5-minute reminder now goes to chatbot@prlresins.com, the same as the repeat-visitor reminder | The two paths sent reminders to different inboxes |

## What was tested (live chats through the staging site)

| # | Test | Result |
|---|---|---|
| 1 | Call-me chat, new visitor (Ohio) | Lead created: names split, OH, source Chatbot, phone and company present |
| 2 | Same visitor chats again | Existing lead updated, no duplicate |
| 3 | Know-what chat, 2-letter state (TX) | Lead created, TX, routed to the TX rep |
| 4 | A phone number typed into the email question | Rejected by the email check, re-asked |
| 5 | Non-US region ("Ontario") on v9 | Lead created, routed to CA **and flagged** in Lead Source Description |
| 6 | Real ZoomInfo person (Todd) on v8 | Lead created with title "Lead Captain" |
| 7 | Todd's email again (existing lead) | Updated, not duplicated |
| 8 | 5-minute reminder emails | Arrived on schedule (before the v9 recipient change) |

## Known limits (not fixed in this RC)

- **Repeat visitors don't get a title.** Updates never overwrite fields, per the Oct 10 design.
- **Industry isn't confirmed in Sugar.** The Zap extracts it, but no industry field came back when Sugar was read.
- **4-hour reminders weren't observed.**
- **The chat transcript note isn't checked.**
- **v9 reminder emails weren't observed after the recipient change.** The new recipient is set in the Zap, but no email to it was seen.
- **v9 wasn't rerun for a valid state.** The warning stays blank when the state parses, so nothing should change for those leads.
- **The rep-facing alert and the business-email check are still open decisions.**

## Cleanup (done 2026-10-29, on Zach's go)

Deleted from sandbox Sugar, each confirmed gone by a re-query: Claude Testlead, Kim Testbuyer, Pat Canuck, Pat Ontario, Todd Hotes (Oct 29), and the Sept 1 "sales rep / test" lead.
Kept: an older Todd Hotes lead from 2023-09-05 (0574990c). It predates this testing, so it is not ours to delete.

Decision receipts logged: Tidio flow activation, Zap v8, Zap v9, and this cleanup (receipt ids 2026-10-29--prl-*--ZH).

## Running log (newest last)

Append one dated line per test session or observation. Keep earlier lines as they are.

- 2026-10-29: 8 live chats on staging; v8 then v9 published; check 32 of 32; release candidate ready for Todd's review.
- 2026-10-29: Ontario lead flagged as expected on v9. In Sugar Leads, the flag goes in Lead Source Description because Leads has no plain Description field.
- 2026-10-29: test leads cleaned up and receipts logged.
