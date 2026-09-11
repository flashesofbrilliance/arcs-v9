# Lyro handoff + measurement policy — PRL Resins (SSOT)
_2026-08-07 · The non-CRM half of the handoff. The lead-delivery webhook → Zapier → SugarCRM is 1.1/1.2 and is
blocked on the Sugar sandbox; this file covers only what needs no Sugar: when Lyro escalates, how it captures
the contact, and the rep-anonymous measurement rule (the gauntlet's friend-not-foe fix)._

## Architecture (confirmed by Tidio support 2026-08-07) — build to this
Order is **Flows -> Lyro -> Human**, run sequentially, never nested. There is **no Lyro node inside a Flow.**
Only **"Visitor Says" (input-based) flows** conflict with Lyro and get disabled; **button/attribute-triggered
flows still run.** So: build the lead-capture as a **Flow with a non-input trigger** (it runs first and always),
and let **Lyro be the free-text fallback** that recognizes intent, then hands off/captures per the rules below.
"Simple Actions" (Lyro AI Agent -> Behavior -> Actions) is the only in-Lyro logic path (legacy, plan-gated,
successor "Smart Actions" pending) — confirm on Todd's plan before relying on it. See the config plan's
"Confirmed Tidio architecture" section.

## When Lyro hands off to a person
Escalate and capture contact on any of:
- A request for a specific property, spec, test value, UL/cert status, price, lead time, or a firm material
  recommendation. (These never come from the bot — routed by policy, reinforced by the KB firewall.)
- A "which grade exactly" question, or a competitor-grade comparison wanting a confirmed match.
- Any visitor who asks to talk to a person.
- Any answer Lyro is not confident is in its knowledge (Lyro's native auto-forward covers this; keep it on).

## Capture at the point of handoff
Collect **name, company, email** (phone optional in the after-hours/AI path until the `phone_work` decision is
made for the CRM write — see the blocked-until in the main plan). Capture must work even when no agent is
online — offline path creates the contact/ticket so the lead is never lost after hours.

## Hand to a **named rep**, not an anonymous queue
The friend-not-foe rule: frame every handoff as "a PRL specialist will follow up," and route to the sales
manager / territory owner (auto-routing by territory is wired in 1.1/switched on later). The bot is the
after-hours catcher that *feeds* the reps, visibly. It never says or implies it resolved something instead of
a rep.

## Online vs offline
Set handoff behavior separately for staffed hours vs after-hours, so:
- **Online:** offer to connect to the team now + capture contact as backup.
- **Offline:** capture contact + set expectation ("the team follows up next business day"), never leave a dead
  end.

## Measurement — channel-level, rep-anonymous (hard rule)
Track only: resolution rate, handoff rate, conversations, **leads captured** — **at the channel level**. Never
per-rep, never "the bot did what a rep didn't." This is the second friend-not-foe guardrail: attribution
measures *what the after-hours channel adds vs nothing*, so it reads as new ground gained, not a scoreboard on
people. (The before/after baseline + the 4-hour number are a **1.2** deliverable; this file just fixes the
rule so 1.5's analytics can never drift into rep-monitoring.)
