# 4-hour metric — decision paragraph (REVISED 2026-08-26: mechanical close, ack is nice-to-have)

> Zach's ruling: the written ack is NOT a gate. The line closes on the mechanical facts below;
> Todd's sign-off is a nice-to-have for the record, folded into the close-loop call as an FYI.

**The 4-hour metric is implemented mechanically from timestamps the chatbot pipeline already
creates.** Every chatbot lead carries a creation timestamp and an assignment timestamp, and the
Zap rule nudges once the elapsed period passes the threshold (4 hours by default, editable in
one config step): (1) the per-lead reminder email, live; (2) the hourly stale-lead sweep (Zap
376815688), built and staged as a nice-to-have layer on top. No lead can age silently, which is
the business intent of the soft rule Todd described. A true recorded time-to-first-TOUCH (rep
action, not assignment) remains a future upgrade if a first-touch event ever lands in Sugar;
until then elapsed-since-creation/assignment is the measure. Written sign-off from Todd:
nice-to-have, not blocking; mention on the close-loop call.
