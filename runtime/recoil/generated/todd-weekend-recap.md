# Weekend recap for Todd (draft, Zach's voice)
_2026-08-07 · Client-safe. Plain language, no em-dashes, business-level (no personal contact data). Ready to
send as an email or paste as a message. PS points to prl.arcs.care._

---

**Subject:** Weekend recap // where the chatbot stands and what is next

Hi Todd –

Quick weekend recap so you have the full picture going into next week, and so nothing lands as a surprise.

**What we set out to do this week**
Get the chatbot ready to go live (Phase 1.1), and dig into your CRM, your website forms, and the data behind
them, so we scope the next phases on facts rather than guesses.

**Where we hit walls**
A few things were not immediately available: a safe way to test lead delivery into your live CRM, direct access
to the data sheet files on the site, competitor spec numbers (those sit behind a paid service), and a couple of
connectors that had expired or were switched off.

**How we kept moving anyway (the workarounds)**
Rather than wait, we routed around each one. We gathered your data sheets and tech sheets from public sources
instead of needing FTP access. We learned your CRM structure from public documentation and read-only access, so
no sandbox was needed just to understand it. And we pulled your website form data by export and checked it
against the CRM safely, without changing anything.

**What we found and got done**
- The chatbot is already capturing leads. We traced why emails were not landing in your CRM (the automated
  paths were not sending them) and fixed the capture so it grabs the email on every lead.
- The bigger find: your main website lead form is mostly automated spam right now, with no protection, and
  underneath it are about 29 real, high-value inquiries from the last few years that never made it into your
  CRM. That includes a program tied to Tesla and quote requests from names like Siemens and OtterBox. Those are
  recoverable.
- We pinned down the exact, quick fixes to clean up the form spam.
- We built the knowledge and guardrails the smarter phases will use, and updated your roadmap at prl.arcs.care
  with the business case and what we learned at each stage.

**Calls we need you to make (and our recommendation)**
A couple of these are genuinely yours to decide, so here they are plainly, with what we would recommend.

1. Should the chatbot answer detailed specs and certification ratings, or connect people to a specialist for
   those? Right now it is quoting exact property values and UL ratings straight from your catalog. That looks
   impressive, but if any value is out of date it becomes a customer-facing error, and stating certification
   ratings carries the most risk for a manufacturer.
   - Option A: keep it answering specs, and we verify the data is current, add a safety note on certifications,
     and clean up the formatting.
   - Option B, our recommendation: the bot recognizes what someone is asking about and helps, but points the
     detailed specs and certifications to your specialist and the official data sheet, and captures the lead.
     Safer for you, and it still gets the right person involved fast.

2. A quick handoff fix, and our recommendation is yes. Right now, when no one is available to chat, a visitor
   who asks to talk to a person hits a dead end and the conversation simply ends, so that lead is lost. We
   recommend switching it to collect their details and follow up, so no after-hours lead slips away.

**The go-ahead items from before, whenever you are ready**
A safe way to prove delivery into your CRM (a sandbox copy, or one clearly labeled test lead we create and
delete together, which is the big unlock), cleaning up the form spam (we would test on the staging copy first),
a quick call on the phone field, adding a "Chatbot" lead source, recovering those orphaned leads, and
reconnecting the enrichment feed.

Give me the green light on the test path and the two calls above, and 1.1 goes live within days, with 1.2 right
behind it.

With gratitude,
Zach

PS – The roadmap at prl.arcs.care now shows the logic and the findings behind each stage, so you can see
exactly why the build order is what it is.
