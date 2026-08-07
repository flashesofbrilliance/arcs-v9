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

**Kicking off 1.2, pending a few quick approvals**
The one thing that unlocks the most is a safe way to prove delivery into your CRM: a sandbox copy, or one
clearly labeled test lead we create and delete together. Alongside that, a short list: your OK to clean up the
form spam (we would test on the staging copy first), a quick call on the phone field, adding a "Chatbot" lead
source, recovering those orphaned leads, and reconnecting the enrichment feed.

Give me the green light on the test path and 1.1 goes live within days, with 1.2 right behind it.

With gratitude,
Zach

PS – The roadmap at prl.arcs.care now shows the logic and the findings behind each stage, so you can see
exactly why the build order is what it is.
