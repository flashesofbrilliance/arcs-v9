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

## Root cause found (2026-10-10, read-only, Zapier editor + Sep 17 run history)

The Sep 17 Lamarre update was NOT an empty-email false match. Evidence from run `0067cd35-6112-a043-9604-e7ca68d6a754` (Zap v5):

- Trigger email was `todd.hotes@prlresins.com` (Todd's test chat), not empty.
- Step 5 search by email1 = that address found the RIGHT lead: `db056406-a634-11f1-a2ed-02309379545d` ("sales rep", created by Chatbot Integration 2026-09-01).
- Step 8 "Update Lead Record with ZoomInfo Data" then wrote to `ea77a7d2-1b0b-11ec-83a4-06ab610ac1b0` (Roger A Lamarre).
- Published step 8 config: the **Lead** field is a static dropdown pick, "Roger A Lamarre", not mapped from step 5's ID. Every Path A run updates Roger, whatever the search found. Likely left over from the Aug 18 test.

Corrections to the sections above:
- Blocker 1 (empty-email guard) is not the cause. Path A's rule is already "step 5 found = true AND 1. Email exists". Hardening it to `email_clean` (task8 sheet) is still worth doing, but it would not have stopped Sep 17.
- "Second lead lagged / held until Nov 12": the only held run in the last 30 days belongs to a different Zap ("Covestro Unbounce -> GHL", disconnected app). This Zap's Sep 17 run was Successful (7 tasks). The plan-limit theory is unconfirmed for this Zap.

Second defect, same step: Notes maps `1. Description` + "— Updated via Chatbot" and Account Description maps `1. Description` + "– Updated via Chatbot". The trigger's Description field shows a missing-field warning, so the update REPLACES Roger's description with just the suffix. An update should append or skip, never overwrite with a blank.

Fix (needs Zach's yes before publishing; the Zap is live in Todd's account):
1. Step 8 Lead field -> custom value mapped from step 5 `ID`.
2. Step 8 Notes / Account Description: drop the missing `1. Description` token; write nothing on update, or append only.
3. Then repair Roger (blocker 2) and run the proof (blocker 3): one repeat chat with a real email must update the matched lead and leave Roger untouched.

## Draft staged (2026-10-10, NOT published)

An unpublished draft of Zap 376827315 holds the fix. Published v5 is unchanged and still on. In the draft, step 8 "Update Lead Record with ZoomInfo Data":
- Lead: mapped to `5. ID` (was the static pick "Roger A Lamarre").
- Account Description, Notes, Title, Industry: emptied (were blank description + "Updated via Chatbot" suffixes and ZoomInfo "Not specified").
- "Retest step" was NOT run (it would replay the Aug 18 sample against Roger).

Before publishing (Mon call, with Todd):
1. Confirm whether the SugarAI update action SKIPS or CLEARS fields left empty. If it clears, the four emptied fields would wipe existing values on every update; then remove them instead, or append only.
2. Publish, repair Roger, run the repeat-chat proof (matched lead updated, Roger untouched).
