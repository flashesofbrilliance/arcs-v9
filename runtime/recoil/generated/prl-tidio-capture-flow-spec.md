# PRL Tidio capture-flow spec (1.1): configure now, no Sugar needed
_2026-08-07 · The lead-capture flow to build/refine in Tidio right now. Everything here is configurable with
current Tidio access; the ONLY Sugar-gated step is the final Create Record write (build up to it, test the
webhook payload against a Zapier Catch Hook, leave the live write off until Todd approves). Persona-generic for
MVP (audiences = 1.4). Anti-fabrication holds: the flow captures + routes, it never states a spec/price/cert._

## Flow shape (actions / triggers / conditions)
```
TRIGGER: visitor opens chat / clicks a conversation starter
  → GREETING (plain, on-brand): "Hi, I can help you find the right resin or the right person at PRL."
  → CONDITION: what does the visitor want?
       • "I know what I need / send me to sales"  → SHORT PATH (capture → handoff)
       • "Help me choose / a question"            → Q&A then capture
       • competitor/grade mention                 → acknowledge, capture, route to specialist
  → CAPTURE FORM (fields below)
  → ACTION: Webhook → Zapier Catch Hook (payload below)
  → CONFIRMATION: "Thanks [name], a PRL specialist will follow up. Anything else?"
  → OPTIONAL: live handoff if an agent is online
```

## Capture form: fields (the contract)
| Field | Required? | Notes |
|---|---|---|
| First name | yes | |
| Last name | yes | |
| Company | yes | maps to `account_name` |
| **Phone** | **decision** | Sugar expects `phone_work`; require it OR use a placeholder (Todd's call) |
| **Email** | yes | THE differentiator: capture every time; maps to `email1` (the fix) |
| Application / grade interest | yes | free text → `description`; run the recognizer later (1.3) |
| Market (optional dropdown) | no | EE / Medical / Transportation / Building / Consumer / Sustainability |

Validation: basic email format check; phone per the decision above. Do NOT block submission on a missing
optional field.

## Webhook action → Zapier Catch Hook (test end-to-end NOW)
POST a JSON payload to a Zapier Catch Hook. Build the Zap up to (but not including) the live Sugar write; the
Catch Hook receiving the payload proves capture works. Payload:
```json
{
  "first_name": "...", "last_name": "...", "account_name": "...",
  "phone_work": "...", "email1": "...",
  "description": "...", "lead_source": "Chatbot",
  "status": "New", "market": "...", "source_url": "...", "captured_at": "..."
}
```
When Todd approves: the Zap's final step = Sugar **Create Record (Leads)** mapping these fields (see
`prl-kb/sugar-schema/leads-integration-design.md`; email → `email1`). Add retry + an email-the-lead fallback so
a write error never drops a lead silently (1.2).

## Triggers / conditions checklist
- [ ] Entry trigger on the widget + on conversation starters.
- [ ] Condition branch: know-what-I-need vs help-me-choose vs competitor/grade mention.
- [ ] Capture form gated so bots/low-intent don't spam (helps Lyro cost later too).
- [ ] Handoff-to-human condition (agent online → offer live; offline → capture + "next business day").
- [ ] Webhook action after successful capture.
- [ ] Confirmation message.

## What's Sugar-gated (do NOT block on it)
Only the live **Create Record write** + the **labelled test lead**. Build + test the whole flow and the webhook
payload now; finish the last Zap step when Todd approves.

## Parked (not this flow)
Persona branching (1.4 / `audiences.md`), the Lyro AI answers (1.5), competitor recognition surfacing (1.3).
MVP flow is capture + route.
