# Task 9: Daily Unassigned-Lead Sweep (Build Sheet)

**What this is:** a new Zap that runs every day at 7:00 AM Eastern, looks for leads in Sugar with no assigned rep, and emails a digest of them to zach.harris@gmail.com and info@prlresins.com. If there are zero unassigned leads, it sends nothing.

**Why it exists:** the live 50-state routing sweep on 2026-08-26 proved that exactly 12 states route to nobody: AK, DE, HI, ID, LA, MS, MT, NM, SD, UT, WV, WY. Any lead from those states (and any lead where routing fails for another reason) lands in Sugar with no owner and no rep notification. This digest is the promised safety net so those leads are seen within 24 hours instead of never.

**Environment:** Sugar sandbox only (prlresinstest.sugarondemand.com, rest/v11). Production is off-limits and not connected. This Zap is separate from the live pipeline Zap 376827315 and the draft SLA Zap 376815688; it reads and emails only, it never writes to Sugar.

---

## Zap structure

| Step | App / Action | Purpose |
|---|---|---|
| 1 | Schedule by Zapier: Every Day | Fire at 7:00 AM, timezone America/New_York |
| 2 | Code by Zapier (Python or JS) or Sugar "API Request": search Leads for empty assigned_user_id | Pull the unassigned list |
| 3 | Filter by Zapier: only continue if count > 0 | Zero results = send nothing, no email |
| 4 | Code by Zapier: format digest body | Build the table of leads with links |
| 5 | Email by Zapier (or Gmail): send digest | To zach.harris@gmail.com and info@prlresins.com |

Notes on step choices:
- Schedule by Zapier's Every Day trigger has a Time of Day field but no timezone field of its own; it uses the timezone in the Zapier account profile settings. Before publishing, open Zapier Settings > Profile and confirm the timezone is Eastern (America/New_York). If the account must stay on another timezone, adjust Time of Day to compensate, and either way verify the actual fire time in Zap History after go-live (test 5 below).
- Step 2 and step 4 can be one Code step if the search is done via fetch/requests inside Code. That saves a task per run. Recommended: one Code step that authenticates, searches, and returns both `count` and a prebuilt `digest_html` string, then Filter on `count > 0`, then Email.

---

## Step 2: expressing "assigned_user is empty" in the Sugar search

Sugar stores the owner in `assigned_user_id`. "Unassigned" can appear as either an empty string or a null depending on how the record was created, so there are two candidate filters. Run the probe below once to determine which one the sandbox actually needs, then build the Zap with the winning filter (or both, OR'd together, which is the safe default).

**Candidate A: empty string**

```
GET /rest/v11/Leads?filter[0][assigned_user_id]=&fields=id,first_name,last_name,account_name,location_c,lead_source,date_entered&max_num=100
```

**Candidate B: null**

```
GET /rest/v11/Leads?filter[0][assigned_user_id][$is_null]=&fields=id,first_name,last_name,account_name,location_c,lead_source,date_entered&max_num=100
```

**Safe default: both, OR'd**

```
GET /rest/v11/Leads?filter[0][$or][0][assigned_user_id]=&filter[0][$or][1][assigned_user_id][$is_null]=&fields=id,first_name,last_name,account_name,location_c,lead_source,date_entered&max_num=100
```

### API probe to determine which works

Run these against the sandbox before building (same OAuth token flow the live pipeline uses):

1. Create a known-unassigned lead (see test protocol below) so there is at least one true positive.
2. Call Candidate A. Note whether the test lead comes back.
3. Call Candidate B. Note whether the test lead comes back.
4. Whichever returns the test lead is the filter to use. If both return it, use the OR form so historical records created either way are all caught. If neither returns it, inspect the raw record (`GET /rest/v11/Leads/[id]?fields=assigned_user_id`) to see what value Sugar actually stored and adjust.

Record the probe result in this file when done: [PROBE RESULT: pending]

Pagination guard: if `next_offset` in the response is not -1, there are more than 100 unassigned leads. Loop with `offset` until `next_offset` is -1. In practice the digest should never be that long; if it is, that itself is a red flag worth seeing in the email.

---

## Step 3: Filter (zero results = silent)

Filter by Zapier, condition: `count` (from step 2 output) is a number, greater than 0. If the filter does not pass, the Zap halts and no email is sent. This is deliberate: a daily "nothing to report" email trains everyone to ignore the digest.

---

## Step 4: digest body format

One row per unassigned lead. Fields, in order:

| Column | Source field | Notes |
|---|---|---|
| Name | first_name + last_name | Fall back to "(no name)" if both blank |
| Company | account_name | Truncate display to 80 chars; account_name over 255 chars has occurred in test data, so never assume it is short |
| State | location_c | Show raw value as stored. Historical data is dirty (both "California" and "CA" exist), so do not normalize here; showing the raw value helps diagnose why routing missed it |
| Source | lead_source | Blank is common (2,041 opps have blank lead_source); show "(blank)" |
| Age | date_entered | Render as days since created, e.g. "3d" |
| Link | id | `https://prlresinstest.sugarondemand.com/#Leads/[id]` (modern SPA format, works in email clients) |

Subject line: `Unassigned leads in Sugar: [count] waiting (daily 7 AM sweep)`

Body header, plain language: "These leads have no assigned rep. Most likely cause: the lead's state is one of the 12 with no rep coverage (AK, DE, HI, ID, LA, MS, MT, NM, SD, UT, WV, WY), or the state could not be read. Each link opens the lead in Sugar. Assign an owner or the lead sits unworked."

Recipients: To: zach.harris@gmail.com, info@prlresins.com. Reply-to: info@prlresins.com. PRL runs Barracuda, so the info@ copy may quarantine at first; the allow-list fix is on PRL's side (same precedent as the rep-notification emails).

---

## Test protocol

Run end to end in the sandbox before calling this done. Every claimed behavior below is testable.

1. **Create one unassigned test lead via API:**
   ```
   POST /rest/v11/Leads
   { "first_name": "Digest", "last_name": "Test", "account_name": "DIGEST-TEST", "location_c": "WY", "lead_source": "Chatbot", "assigned_user_id": "" }
   ```
   Set assigned_user_id explicitly to empty string. Sugar can default the owner to the authenticated API user on create, so omitting the field risks a test lead that is silently assigned, which would make the probe wrongly conclude both filters are broken. After creating, GET the record with `?fields=assigned_user_id` and confirm the stored value really is empty before running the probe. WY is one of the 12 uncovered states, so this mirrors the real failure case. Capture the returned id. Note: the real leads this sweep must catch are created by pipeline Zap 376827315's Path B, which may store emptiness differently than a hand-made API create; once one real uncovered-state lead exists in the sandbox, confirm the chosen filter returns it too.
2. **Verify the digest fires:** a Schedule-triggered Zap has no manual "run now" button for a first run, so either use the editor's step-by-step Test on each step (this actually executes the Code search and the Email send), or publish with Time of Day set a few minutes ahead and let it fire once, then set it back to 7:00 AM. (Zap History's Replay only works on runs that already happened.) Confirm one email arrives at both addresses, the DIGEST-TEST row is present, and its link opens `https://prlresinstest.sugarondemand.com/#Leads/[id]` to the right record.
3. **Delete the test lead:**
   ```
   DELETE /rest/v11/Leads/[id]
   ```
   Confirm with a GET that it returns 404.
4. **Verify silence:** trigger one more run (schedule-ahead method) with the test lead deleted. Confirm the Filter step halts the run (Zap History shows the run stopped at the filter) and no email is sent. If other unassigned leads exist in the sandbox at test time, the digest will still fire; that is correct behavior, so either assign them first or verify silence by checking the DIGEST-TEST row is absent and the filter logic on a count of 0 in the Code step's test output.
5. **Timezone check:** after go-live, confirm the first real run stamps in Zap history at 7:00 AM Eastern, not UTC.

Cleanup rule: the test lead must be deleted in the same session it is created. The Roger Lamarre incident came from test artifacts touching real records; this test only ever creates and deletes its own record, identified by account_name=DIGEST-TEST, and never updates anything.

---

## Cost and quota

Zapier bills tasks only for action steps that run; the Schedule trigger and a Filter step that halts do not count. With the recommended single Code step: a silent day costs 1 task (Code), a day with leads costs 2 (Code + Email); with separate search and format Code steps, add 1 to each. No ZoomInfo credits, no Tidio quota, no Sugar writes. Negligible against current usage.

## Out of scope for this Zap

- Auto-assigning the leads (that is a routing-table decision for Todd: who covers the 12 empty states).
- Fixing dirty location_c history.
- Production. This entire sheet targets the sandbox; a production version waits for the gated cutover.
