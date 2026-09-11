# 4-hour SLA nudge — Zapier build brief (skips Sugar BPM entirely)

Part of Phase 1.2's committed "four-hour metric" line item. Cheapest path: a scheduled Zap,
not Sugar's Process Author (unintuitive, avoided by design).

## Build
1. **Trigger: Schedule by Zapier** — hourly.
2. **Action: SugarCRM Find Record** (reuse the proven sandbox connection, same one used for
   series_376761228) — search Leads where `status = New` and `date_entered` older than a
   configurable threshold (start at 4 hours; Todd confirmed this isn't a hard rule, so make it
   a plain filter value, not hardcoded logic).
3. **Action: send notification** (email or Slack, whichever's easiest to stand up) listing the
   stale leads found.

## Test
Create one test Lead in sandbox assigned to Zach, with `date_entered` old enough to trip the
filter (or just wait it out). Confirm the notification arrives with that lead listed. No Sugar
UI work needed beyond creating the one test record.

## Note
`date_entered` already exists on every Lead for free — no new field or schema change needed.
This only builds the check + notification, nothing else.
