# DRAFT — Todd recap email (post 2026-09-17 walkthrough) — NOT SENT

**To:** todd.hotes@prlresins.com (cc todd.hotes@gmail.com)
**From:** Zach
**Subject:** Chatbot // where we landed today + your test-drive while I'm out

**Status:** DRAFT for Zach's review and send. Air-gapped: no internal recoil / belief / scope-psychology language. Every claim below is either something Todd saw live on the 9-17 call or is on the linked runbook page. Sources: Granola transcript cd30a239 (2026-09-17 2:00pm), runbook at prl.arcs.care/status/runbook.

---

Todd,

Good walkthrough today. Quick recap of where we landed, what I'm cleaning up, and the couple of things that would help while I'm out for surgery Friday. Short version up top, detail below.

**Bottom line:** the pipe runs end to end and you saw it work today. We are not flipping it live yet, and I agree with that call. The next step is enriching the bot's knowledge so it answers the "what's an alternative to X resin" questions the way a customer actually needs, then we go live. Nothing here needs to happen on a clock.

## What we proved live today

- **Region routing works.** A Connecticut lead landed on Lynn; a Nebraska question correctly named Steve Fabricius and his territory. The right rep gets named from the visitor's location.
- **Enrichment works.** ZoomInfo filled in company, job title, and industry on the lead automatically, so it arrives more complete than a normal web form.
- **The full path is wired.** Chat to captured lead to your CRM sandbox, deduplicated, tagged "Chatbot," with follow-up reminders set. We walked the Tidio flow editor so you can see where the copy and questions live.
- **The baseline audit is done and it is the sleeper win.** 24 months, 942 leads, 4,238 opportunities, and roughly 40% have no recorded lead source today. That "before" picture alone is worth the phase, because it is how we prove what the chatbot adds later.

## What I'm cleaning up from what we saw (I'm on these)

You saw a few rough edges live. That is exactly what a test drive is for. None are hard problems, and I would rather you know the full list than discover them mid-cutover:

1. **New lead came in as status "dead" instead of "new."** Looks like a field-mapping or routing-rule quirk. I'm running it down.
2. **A second test lead lagged / did not show during the call.** Because Sugar has no live API, we ride Zapier's push timing, and ZoomInfo can hold a lead briefly while it enriches. I'm confirming which it is so delivery timing is predictable.
3. **The new-lead email notification did not reach you.** The 5-minute and 4-hour reminders are wired through Zapier; I need to point the notification at the right inbox and confirm it lands.
4. **info@prlresins.com can't receive a routed lead yet** because it has no user record in the CRM. Small setup item on the PRL side when we get there.

## The switch to your account

I'm swapping the sandbox notification and assignment over to your login so a test lead flows all the way through to you, and I'll set up the "Chatbot" lead source in the production CRM (setup only, not go-live). You mentioned you already added the lead-source field on your side, thank you, I'll confirm it maps cleanly.

## Going live, when we're ready (three steps, all reversible)

Everything above is proven in a sandbox copy. The live switch is three deliberate changes, and you can undo any of them:

- **A.** Point lead delivery at your live CRM instead of the sandbox copy.
- **B.** Add the "Chatbot" lead source in the live CRM (one-time).
- **C.** Install the chat plugin on the live site with the same credentials.

We prove it once with a single real test lead, then you pick the window. And you can always just disable the plugin.

Full end-to-end tour and these steps live here: **prl.arcs.care/status/runbook**

## What would help from you

- **Play with it in the test environment while you're assigned to it.** Run a few real personas through it: the electrician, the injection molder, the person who knows the resin and the person who only knows the application.
- **Send me a short Loom or a few notes** on what you expected versus what you saw, especially on the answers. That is the fastest way for me to tune it.
- **The knowledge piece is the real next step.** For the bot to answer "what's an alternative to Velox 357" well, it needs your product/alternative data behind it. That's the enrichment we do before go-live, and it's mostly your domain knowledge plus the data we feed it.

## Timing

Surgery is Friday, so I'll be offline from Friday through the weekend, likely back online early next week. Take your time in the test environment. When I'm back we'll work through any kinks and the final validation before we go live. No rush on your end, and safe travels to Wichita.

Talk soon,
Zach

---

### Reviewer checklist before send (Zach)
- [ ] Confirm info@ address spelling (transcript rendered it oddly; almost certainly info@prlresins.com).
- [ ] Confirm you're OK naming the reps (Lynn, Steve Fabricius) in writing to Todd — they came up on the call, but this is an email that could be forwarded.
- [ ] Decide whether to attach/mention the 1.2-A web-forms add-on ($2,070) or keep this recap clean and raise money separately. (Left OUT of this draft on purpose.)
- [ ] Em-dash sweep: 0 (done).
