# PRL Zap Kit

Build and edit sheets for the PRL Tidio to Sugar pipeline (sandbox: prlresinstest.sugarondemand.com, rest/v11). Production is off limits. All artifacts adversarially verified 2026-08-26.

## Artifact status

### task7-state-parser.js + task7-state-parser.test.js
Verdict: ship-with-notes. Drop-in replacement body for the Code step "Process State and Name Inputs" in Zap 376827315. Normalizes both full state names ("California") and 2-letter codes ("CA") seen in dirty historical data, keeps the existing output contract (state_code always valid 2-letter with CA fallback, state_parse_failed flag, raw passthrough keys unrenamed), and adds rep_email routing per the 2026-08-26 live 50-state sweep (12 states route to nobody and yield empty rep_email). Verified independently: author suite 39/39, expanded suite 55/55, exit 0. Runnable locally with node before pasting.

### task8-payload-hardening.md
Verdict: ship-with-notes. Edit sheet for Zap 376827315, both Paths A and B. Adds the empty-email Filter that prevents the Roger Lamarre class of false-match update, sanitizes payload fields in one Code-step extension (account_name >255 chars, blank names), and includes per-edit curl read-back verification against the sandbox. Critical fix applied during verification: defaults like "Unknown" are no longer baked into mapped fields, so an update path can never silently overwrite real historical data with placeholder text.

### task3-sla-nudge.md
Verdict: ship-with-notes. Build sheet to finish draft SLA Zap 376815688: hourly schedule, editable N=4 hour threshold in a config Code step, Sugar Find Records on status New, digest builder, count filter, email to zach.harris@gmail.com only for the pilot. Verification fixed a structural gap: the digest Code step (3b) that produces stale_count is now an explicit step in the Zap structure, so the sheet is executable as written.

### task4-rep-notification.md
Verdict: ship-with-notes. Edit sheet adding an Email by Zapier step after the Sugar step in each path of Zap 376827315. Verification caught a ruin-class scope miss: the notification now actually addresses the assigned rep (rep_email computed in the existing Code step from the verified routing table), with info@prlresins.com as recipient and reply-to and zach.harris@gmail.com copied. Unassigned states fall back to info@ plus Zach, never a guessed rep. Barracuda quarantine risk is noted; the allow-list fix is on PRL's side.

### task9-unassigned-sweep.md
Verdict: ship-with-notes. Build sheet for a new daily 7:00 AM Eastern read-only Zap that digests leads with no assigned rep to zach.harris@gmail.com and info@prlresins.com, covering the 12 states that route to nobody. Verification corrected the timezone claim (Schedule by Zapier uses the account profile timezone, not a per-trigger field) and the sheet now includes a fire-time verification test.

## Paste order for the Zapier co-pilot session

Each sheet is written to work as a co-pilot prompt. Paste in this order; do not start the next item until the previous one's verification checks pass.

1. task8-payload-hardening.md, Step 0 plus the empty-email Filter edit FIRST. This is the Task 1 filter verification: confirm the Filter (email non-empty before the dedup search; empty email routes to Path B create) exists or gets added, and prove it with the read-back checks. Nothing else ships before this, because every later edit assumes the Roger-class false match is closed.
2. Remainder of task8-payload-hardening.md (sanitize Code-step extension, length caps, verification curls).
3. task7-state-parser.js. Replace the body of "Process State and Name Inputs" with the verified parser (run task7-state-parser.test.js locally first: node task7-state-parser.test.js, expect 55/55). This lands state_code normalization plus the rep_email and company_display keys that tasks 4 depends on.
4. task4-rep-notification.md. Add the notification email steps to both paths. Depends on rep_email and company_display from step 3.
5. task3-sla-nudge.md. Finish draft Zap 376815688. Independent of the live Zap; safe to do after the pipeline edits.
6. task9-unassigned-sweep.md. Build the new daily sweep Zap. Read-only, fully independent, last.

## Open items that still need the browser or the co-pilot

- Roger Lamarre repair: clear the description suffix ("Updated via Chatbot") and reset title/industry from "Not specified" back to blank on lead ea77a7d2-1b0b-11ec. Manual sandbox edit or a one-off API call; not covered by any sheet.
- Test-lead cleanup: roughly 8+ synthetic and test leads (including 3x Zach) still in the sandbox.
- Debug WHY the empty-email payload got past Tidio flow validation in the first place. The Filter closes the blast radius; the root cause is in the Tidio flow and needs the Tidio browser UI.
- Confirm the Zapier account profile timezone is America/New_York before publishing the task9 sweep (Settings, Profile), and verify actual fire time in Zap History after go-live.
- Barracuda allow-list for noreply@zapiermail.com on PRL's side, otherwise rep notifications may quarantine. Needs Todd or PRL IT.
- Email by Zapier rate limit (about 10 per hour): fine for pilot; revisit provider choice if volume grows.
- Baseline pull follow-up: 2041 opps with blank lead_source ($43.7M unattributed) is measured; attribution work itself is future scope, not in this kit.
- Publish steps for all edited Zaps happen in the Zapier UI after verification; the sheets stop at verified-in-draft.
