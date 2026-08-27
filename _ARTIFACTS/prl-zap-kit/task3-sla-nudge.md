# Task 3: SLA Nudge Build Sheet

Finish draft Zap **376815688** so it emails Zach when leads sit in status New for more than N hours.

- Sandbox: `prlresinstest.sugarondemand.com` (rest/v11). Production is off limits and not connected.
- Draft Zap: **376815688** (the SLA draft). Do not touch live pipeline Zap 376827315.
- Recipient for pilot: **zach.harris@gmail.com** only. Rep and info@ routing comes later, after the pilot proves clean.
- Threshold: **N = 4 hours**, stored as an editable value at the top of the Zap (see Step 2).

## Zap structure (6 steps)

```
1.  Schedule by Zapier  (every hour)
2.  Code by Zapier      (config + cutoff computation)   <- the editable N lives here
3.  Sugar Find Records  (status = New)
3b. Code by Zapier      (digest builder: age filter + stale_count + stale_lines)
4.  Filter by Zapier    (only continue if stale_count > 0)
5.  Email               (digest to zach.harris@gmail.com)
```

Step 3b is the Plan B digest builder described under Step 3. It is part of the Zap in both plans (Plan A still needs it to build `stale_count` and `stale_lines`), so build it unconditionally.

### Step 1: Schedule by Zapier

- App: Schedule by Zapier
- Event: Every Hour
- Trigger on weekends: Yes (leads arrive on weekends too; a Saturday lead should not wait until Monday to alert)

### Step 2: Code by Zapier (config + cutoff)

This step is the "editable top-of-zap value." Zapier has no native constants feature, so the convention is: a Code step near the top of the Zap whose **Input Data** fields act as the Zap's settings panel. Anyone editing the Zap opens this step, changes one visible field, and republishes. No code reading required.

How to make it editable, exactly:

1. Add step: Code by Zapier, event **Run Javascript**.
2. Rename the step to `CONFIG: SLA threshold hours` so it is self-describing in the Zap editor.
3. In **Input Data**, add one row: key `threshold_hours`, value `4` (typed literally into the value box, not mapped from a prior step). This input box is the editable setting.
4. Paste the code below. It reads `threshold_hours` from the input and computes the cutoff timestamp.

```javascript
// CONFIG: edit threshold_hours in the Input Data box above, not in this code.
const hours = Number(inputData.threshold_hours);
if (isNaN(hours) || inputData.threshold_hours === "" || hours < 0) {
  throw new Error("threshold_hours input must be a non-negative number, got: " + inputData.threshold_hours);
}
const cutoffMs = Date.now() - hours * 60 * 60 * 1000;
const cutoffIso = new Date(cutoffMs).toISOString().replace(/\.\d{3}Z$/, "+00:00");
output = [{
  threshold_hours: hours,
  cutoff_iso: cutoffIso,   // e.g. 2026-08-26T14:00:00+00:00
  now_iso: new Date().toISOString()
}];
```

To change the SLA later: open this step, change `4` to the new number in Input Data, Publish. That is the entire edit.

### Step 3: Sugar Find Records (stale New leads)

- App: SugarCRM (the sandbox connection already used by Zap 376827315)
- Event: Find Record(s) on module **Leads**
- Filter: `status` equals `New` AND `date_entered` older than the cutoff from Step 2.

**Relative-date caveat (plan A vs plan B).** The Zapier Sugar integration's Find step may only support equals/contains style matching on fields, with no "older than X hours ago" relative operator.

- **Plan A (try first):** if the Find step exposes a raw filter or supports operator syntax, filter on `status = New` and `date_entered < {{cutoff_iso from Step 2}}`. Sugar's REST filter form for this is:

  ```json
  {"filter":[{"status":{"$equals":"New"}},{"date_entered":{"$lt":"2026-08-26T14:00:00+00:00"}}]}
  ```

  Map Step 2's `cutoff_iso` into the date value. Test it: it must return known-old sandbox leads and exclude a lead created minutes ago.

- **Plan B (fallback, expected):** if the Find step cannot express `$lt` on a date, fetch by `status = New` only and do the age comparison in the Step 3b Code step placed between Find and Filter:

  ```javascript
  // Step 3b. Input Data fields, each mapped from the Find step's line-item
  // outputs: lead_ids, lead_names, lead_accounts, lead_reps, lead_dates.
  // Plus cutoff_iso mapped from the CONFIG step (Step 2).
  const cutoff = new Date(inputData.cutoff_iso).getTime();
  if (isNaN(cutoff)) {
    throw new Error("cutoff_iso did not parse as a date: " + inputData.cutoff_iso);
  }
  const ids = (inputData.lead_ids || "").split(",");
  const names = (inputData.lead_names || "").split(",");
  const companies = (inputData.lead_accounts || "").split(",");
  const reps = (inputData.lead_reps || "").split(",");
  const dates = (inputData.lead_dates || "").split(",");

  // Alignment guard: comma-joined arrays must be the same length, or names,
  // companies, and reps can attach to the WRONG lead (silent-wrong-data class,
  // same family as the Roger Lamarre incident). If lengths disagree, say so in
  // the email instead of guessing.
  const misaligned = (names.length !== ids.length) ||
    (companies.length !== ids.length) ||
    (reps.length !== ids.length) ||
    (dates.length !== ids.length);

  const stale = [];
  for (let i = 0; i < ids.length; i++) {
    const entered = new Date(dates[i]).getTime();
    if (!ids[i] || isNaN(entered) || entered >= cutoff) continue;
    const ageHours = Math.round((Date.now() - entered) / 3600000 * 10) / 10;
    stale.push(
      (misaligned ? "(details unverified) " : "") +
      (names[i] || "Unknown name") + " / " +
      (companies[i] || "No company") + " / " +
      (reps[i] || "Unassigned") + " / " +
      ageHours + "h old / " +
      "https://prlresinstest.sugarondemand.com/#Leads/" + ids[i]
    );
  }
  const warning = misaligned
    ? "WARNING: field arrays came back misaligned (a name or company likely contains a comma). Lead IDs and links are trustworthy; names, companies, and reps on each line may be shifted. Verify in Sugar before acting.\n\n"
    : "";
  output = [{ stale_count: stale.length, stale_lines: warning + stale.join("\n") }];
  ```

  Map the Find step's line-item outputs into the comma-joined Input Data fields (Zapier joins line items with commas automatically when mapped into a single input). Note: if any name or company itself contains a comma, alignment can shift. The code above detects the mismatch and marks the email with a warning instead of silently attaching the wrong name or rep to a lead. If the warning fires regularly, switch the inputs to the Find step's raw JSON output and `JSON.parse` instead (account names over 255 characters have appeared in test data, so long or messy values are a real possibility, not a hypothetical).

  Sugar timezone note: `date_entered` comes back in UTC from the REST API. The code compares in UTC on both sides, so no offset math is needed. Verify once during testing that a lead created "now" shows ~0h age.

### Step 4: Filter by Zapier

- Only continue if `stale_count` (from Step 3b) is greater than `0`.
- This condition works under both plans, because Step 3b runs in both. Plan A just makes the Find step tighter so Step 3b has less to filter.

This filter is what keeps the hourly schedule silent when nothing is stale. No stale leads, no email, zero noise.

### Step 5: Email

- App: Email by Zapier (or the Gmail connection if preferred; Email by Zapier is zero-setup and fine for a self-notification pilot)
- To: `zach.harris@gmail.com`
- Subject: `SLA Alert: {{stale_count}} stale leads (>4h)`
  - If you want the subject to track the editable threshold instead of hardcoding 4, use `SLA Alert: {{stale_count}} stale leads (>{{threshold_hours}}h)` mapped from Step 2. Recommended, so the subject never lies after a threshold change.
- Body (plain text), one line per lead in the format name / company / assigned rep / age, each with its record link:

```
{{stale_count}} leads have been in status New for more than {{threshold_hours}} hours.

{{stale_lines}}

Checked at {{now_iso}} (UTC). Sandbox: prlresinstest.sugarondemand.com
```

Each line in `stale_lines` already ends with the modern SPA record link `https://prlresinstest.sugarondemand.com/#Leads/[id]`, so every lead in the digest is one click from its Sugar record.

Later (not this task): add `info@prlresins.com` as a recipient with reply-to `info@prlresins.com` and keep the zach.harris@gmail.com copy, per the rep-notification spec. PRL runs Barracuda, so expect possible quarantine on their side; the allow-list fix is theirs. None of that gates this pilot, which emails Zach only.

## Test protocol

The sandbox already contains leads in status New that are far older than any sane threshold, so the cheapest full-path test is to drop the threshold to 0 and let real data trip the alert.

1. In Step 2 (CONFIG), set `threshold_hours` Input Data value to `0`.
2. In the Zap editor, run **Test** on each step in order:
   - Step 2 outputs `cutoff_iso` equal to roughly now. Sanity-check the timestamp.
   - Step 3 returns the existing sandbox New leads. Note how many records it returns versus how many New leads actually exist in the sandbox (see the result-cap edge below); record the observed cap in the test log.
   - Step 3b outputs `stale_count` > 0 and readable `stale_lines` with no misalignment warning.
   - Step 4 filter passes.
   - Step 5 test-send fires.
3. Verify delivery: the email arrives at zach.harris@gmail.com, subject shows the correct count, body has one line per lead in name / company / rep / age order.
4. Click **one** link in the body and confirm it opens the correct lead record in the sandbox (`#Leads/[id]` resolves in the Sugar SPA). One link is the acceptance bar; spot-check more if anything looks off.
5. Restore Step 2's `threshold_hours` to `4`.
6. Re-test Step 2 once to confirm the cutoff is now 4 hours back.
7. **Publish** the Zap and confirm it shows On.
8. Optional soak check: after the next top of the hour, look at Zap History. Expect one of three correct outcomes: a real alert, a run that stopped at the Filter (New leads exist but none stale), or a run that stopped at the Find step marked as "no results" or "halted" (zero leads in status New at all; Zapier search steps end the run quietly when they find nothing). All three are fine. An errored run is not; investigate any run marked Error.

## Known edges

- Every hourly run consumes Zapier tasks even when filtered (trigger + find + code steps still count). At 24 runs/day this is modest but nonzero; if task budget gets tight, drop the schedule to every 2 hours. The threshold and the schedule are independent knobs.
- The digest repeats a stale lead every hour until someone changes its status. That repetition is the nudge working as designed for the pilot; dedup/escalation logic is a later phase decision.
- Empty or malformed `date_entered` values are skipped by the Step 3b code (NaN guard) rather than crashing the run. Known trade: a lead with a broken date can never alert, silently. Sugar sets `date_entered` itself on create, so a broken value should not occur through normal use; if the count ever looks low, check for it directly in Sugar.
- Find Records steps in Zapier typically cap returned results (often 3 to 10 records depending on integration settings). Check the Sugar step's returned count during testing; if the sandbox has more stale New leads than the step returns, the email undercounts. For the pilot that is acceptable, but note the observed cap in the test log. If a true count matters later, replace the Find step with a raw REST call (Webhooks by Zapier GET to `rest/v11/Leads` with the filter JSON above and `max_num` raised).
