# 4-hour metric proxy — written decision paragraph (DRAFT for Todd's ack)

Per the 1.2 plan's own allowance ("the chosen proxy documented"), and Todd's confirmation that
the 4-hour rule is a soft rule:

**The 4-hour first-touch metric is implemented as a documented proxy, not a recorded
timestamp.** Sugar does not stamp a first-touch event today, and we will not ask reps to log
calls to create one (change-management cost exceeds metric value at pilot volume). The proxy is:
(1) a per-lead reminder email that fires 4 hours after lead creation regardless of rep action,
and (2) an hourly scheduled sweep (Zap 376815688, staged) that digests any lead still in status
New past the threshold (default 4 hours, editable). Together these guarantee no lead can age
silently, which is the business intent of the rule. A true recorded time-to-first-touch becomes
possible if/when a first-touch event is captured in Sugar (candidate: status-change timestamp),
and the criterion upgrades then. This paragraph plus Todd's written "works" closes the 1.2
"four-hour metric" acceptance line.
