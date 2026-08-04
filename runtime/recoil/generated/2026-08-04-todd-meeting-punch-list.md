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

## 7. Demo plan (how to actually show it)
**Reality check:** Tidio runs **one active flow at a time** — the versions below are separate
configs, NOT one unified chat. You can't show all three live in one widget. Two clean ways:
- **Hero (full realism):** publish your best version as the active flow, show it on the **local
  sandbox** `http://localhost:8080/prl-home.html` (pixel-perfect PRL homepage). Todd experiences it
  as a real visitor on his own site. This is the money shot.
- **Compare the rest:** use **Tidio's flow-editor Preview/Test mode** to step through the other
  versions without publishing. Do NOT hot-swap the active flow live — clunky.

**Three versions on the table** (`~/Downloads/`):
- `prl-chatbot-flow-v1.json` — original 4-button (superseded)
- `prl-chatbot-flow.json` — 5-button + Guides & Resources (fullest)
- `prl-chatbot-flow-ai-forward.json` — newest (Aug 3), AI-forward angle
→ **Pick the hero before the meeting** and publish it so sandbox + dev site both show it.

**Pre-demo setup (before Todd arrives):**
- [ ] Start the sandbox (it's currently DOWN): `cd ~/prl-resins-local && ~/.orbstack/bin/docker compose start`
- [ ] Confirm `localhost:8080/prl-home.html` loads and the widget greets.
- [ ] Publish the hero flow in Tidio; open the other two in the editor for preview.
- [ ] Have the WP dev site tab ready as the "and here it is on your real site" proof.

## 8. Scope — Now / Next / Later (the "this is the scope for now" message)
Land this explicitly so Phase 1 stays bounded and future work is sized on its own.
- **Now (this engagement, Phase 1):** the lead-capture chatbot — branded, routes to the Sales
  Manager, delivers to SugarCRM + email. Goal: ship it, land the first real live lead. **Close this out.**
- **Next (near-term, scoped + priced separately):** pick + polish the winning flow version;
  GA4/GTM cleanup (analytics are currently dark); measure chatbot-sourced leads; extend to the
  Unbounce landing pages.
- **Later (Phase 4/5 — its own project, pricing, and NDA):** the AI agent trained on
  product-development data to recommend resin formulations by application. Big, separate, NDA-gated.

**The line to say:** "Phase 1 is this scope — let's ship it and get you live leads. Next and Later
are real, and we'll scope each as its own step." (Bounds now; opens appropriately-sized future phases.)

---
_Decisions to leave with: hero flow version · phone (required/placeholder) · lead source (Chatbot/Web Site) · test-lead OK · Tidio upgrade approved · agree Now/Next/Later scope._
