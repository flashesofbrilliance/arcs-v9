# PRL go-live blockers and admin to-dos (2026-10-09)

Internal. For the Mon 2026-10-12 10:00 ET "Wrapping up Phase 1.2" call. Checklist Todd sees: prl.arcs.care/go-live.

## What the sandbox shows (read-only, Zapier MCP GET against prlresinstest, 2026-10-09)

| Sep 17 rough edge | Finding | Status |
|---|---|---|
| Lead came in "dead" | No new lead was created. At 2026-09-17 14:41 ET "Chatbot Integration" UPDATED Roger A Lamarre (2021 lead, id `ea77a7d2-1b0b-11ec-83a4-06ab610ac1b0`, status Dead, location "Rhode Island"), description now "— Updated via Chatbot". Same empty-email false match as Aug 18 (repaired Aug 27). | **NOT FIXED. Blank-email safeguard was not effective in the published zap on Sep 17; no record changes since.** |
| Second lead lagged | No lead created in the sandbox since 2026-09-10. Only Chatbot-sourced lead is the Sep 1 test (CT, Lynn Winston, description "Chatbot Lead"). Consistent with the 14:40 run held by the Zapier task limit (held until Nov 12). | **NOT FIXED** (plan limit) |
| New-lead email did not reach Todd | Not verifiable from Sugar; nothing has fired since Sep 1. | **UNKNOWN** |

## Technical blockers (Zach, before go-live)

1. **Empty-email guard in the published dedup zap (376827315).** Route by Path rules: if `email_clean` is empty, skip Find Record and go straight to Create (never a top-level Filter, which drops the lead). Guard on `email_clean`, not the raw Tidio email. Build sheet: `_ARTIFACTS/prl-zap-kit/task8-payload-hardening.md`. The older spec `empty-email-filter-spec.md` is NOT on main (only in preserve commit `0b6e3781`).
2. **Repair Roger Lamarre** (sandbox write, show fields first): clear `description`, check `title`, `hint_account_industry`, `account_description` (the 4 fields Path A writes).
3. **Prove it:** one sandbox chat with no email must CREATE a new lead, never update. Then one repeat chat with a real email must update the same lead.
4. **Alert email:** point the new-lead alert at the assigned rep (+ Todd, info@) and watch one land.

## Admin creates / account updates (Todd or PRL)

| Item | Who | Why |
|---|---|---|
| Add "Chatbot" to Lead Source dropdown in live Sugar | Todd (Sugar admin) | Prod lacks the value; leads won't filter by source without it |
| Create a local (non-SSO) Sugar user for the automation, Leads-only role, PRL-owned email | Todd / Bill | Microsoft SSO logins cannot authorize Zapier; sandbox user is over-privileged admin |
| Confirm each rep's Sugar user email is current | Todd / Bill | Alert goes to the assigned user's email |
| WordPress admin access on prlresins.com | Todd / Josh (websitesforanything) | Install the Tidio plugin |
| Allow-list the alert sender in Barracuda; fix info@ | PRL IT (Jorge) | First-time sender likely quarantined |
| Check no SugarBPM process / web logic hook touches Lead create | Bill or Sugar admin | Residual from the custom-code review; never run |

## Business blockers (decisions or purchases only PRL can make)

1. **Zapier plan upgrade (purchase).** Current plan holds runs until Nov 12. Go-live on the current plan means leads can sit for weeks. Real-time needs the upgrade; Claude cannot buy it.
2. **Territory list reconcile with Bill.** 12 states route to no rep; Todd's interim decision is "unmatched go to Bill". Fine for a trial, needs an owner.
3. **Go-live is gated on the empty-email fix.** If it cannot be fixed and proven before Monday, the call becomes a working session to fix it, and the live switch waits. Do not point the zap at production Sugar until the no-email test creates, not updates.
