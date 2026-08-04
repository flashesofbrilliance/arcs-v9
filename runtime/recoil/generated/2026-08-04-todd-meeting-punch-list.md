# PRL Resins Chatbot — Meeting Punch List (Aug 4 AM)

_For Zach + Todd. Goal of the meeting: get the 3 decisions, confirm the one blocker, agree the path to first live lead._

---

## 1. Where it stands (show this first — it's real progress)
- Bot **built, branded, activated, tested** in Tidio. A **real lead was captured Jul 30**.
- **Live on the WordPress dev site**, branded to the PRL theme (maroon/gold), greets on load.
- Flow: greeting → "What brings you in?" (5 buttons incl. Guides & resources) → route to Sales Manager.
- Lead-to-CRM step is now **fully mapped against your live SugarCRM** and ready to wire.

## 2. Decisions I need from Todd (the real agenda — 3 quick calls)
These come straight from your live Sugar "Leads" setup, which **requires** 6 fields on every new lead.

1. **Phone.** Sugar requires a phone on every lead, but the bot asks for it as optional. Do we
   **make phone required in the chat**, or **drop in a placeholder** when someone won't give one?
   (Required = cleaner data; placeholder = never lose a lead. My rec: make it required, it's a B2B buyer.)
2. **Lead source.** Sugar has no "Chatbot" option in its Lead Source list. Do you want me to have you
   **add a "Chatbot" value** (so you can measure the bot's ROI), or **tag them "Web Site"** for now?
   (My rec: add "Chatbot" — it's the whole point, you'll want to see what it produces.)
3. **First test lead.** To prove it end-to-end I need to send **one real lead into your Sugar**,
   clearly labelled as a test. OK to do that against production, or do you want a sandbox first?
   (Note: all your leads sit on team "Global," so a test one will be visible — we'd just label + delete it.)

Bonus quick one: the bot should also **require Company and State** (Sugar needs both). Any objection?

## 3. The one thing blocking go-live (needs a yes + a card)
- **Tidio's webhook feature is a paid upgrade.** Until we upgrade, Tidio can't hand the lead to
  Zapier → Sugar. This is the single gate between "bot works" and "leads land in your CRM."
  **Ask:** approve the Tidio plan upgrade today so I can wire and test this week.

## 4. Done / staged on my side (no action needed from Todd)
- Zapier → SugarCRM "Create Lead" mapping complete, against your live schema (assign to **Bill Galla**,
  status **New**, team **Global** — matches how your leads already flow).
- Name-splitting, field handling, and a Gmail "new lead" email notification all specced/drafted.

## 5. Small manual steps still open (mostly mine, one is Todd's)
- **Todd:** accept the Tidio invite (you're added as a Chat Agent).
- Zach: upload the hexagon logo in the widget; reimport the 5-button flow; connect Gmail in Zapier.

## 6. After the meeting → path to first live lead
1. Todd approves Tidio upgrade → I wire Tidio → Zapier Catch Hook → SugarCRM Create Lead.
2. Send **one labelled test lead** end-to-end; confirm it lands (Bill Galla, status New).
3. Flip on for real. Go-live to the public site happens via GTM (covers WordPress + Unbounce at once).

---
_Decisions to leave with: phone (required/placeholder) · lead source (Chatbot/Web Site) · test-lead OK · Tidio upgrade approved._
