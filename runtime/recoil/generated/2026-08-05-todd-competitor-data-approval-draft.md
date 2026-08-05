# Draft to Todd — competitor cross-reference: approval + how to handle it (DRAFT ONLY, not sent)
_2026-08-05 · 🤝 client-facing · plain register, no em-dashes. Default assumption: gate behind lead capture._

**Subject:** Your competitor cross-reference in the chatbot: one call to make

Hi Todd -

Quick one that is worth getting right before it goes live, because it touches your most valuable data.

The chatbot can answer the question your buyers care about most: "what is your equivalent to Lexan, Ultem,
Valox, Noryl, or Zytel." I have your grade-by-grade competitor cross-reference ready to power that. It is
the strongest thing the bot can do, and it is also competitively sensitive, so I do not want to put it out
in the open without your say-so.

Two things to confirm:
1. Is any of this cross-reference something you would consider a trade secret, or that should not be freely
   visible to anyone on your website (including a competitor)?
2. How do you want the bot to hand it out?

Three ways to run it, easiest to most protected:
- **Open.** The bot answers the equivalent to anyone who asks. Most helpful, but a competitor could fish it
  anonymously and see your positioning against SABIC, Covestro, and the rest.
- **Gated behind contact capture (my recommendation).** The visitor gives their name, company, and email
  first, then the bot gives the equivalent. This turns your most valuable answer into a lead magnet, screens
  out anonymous competitor fishing, and means every competitor-match question becomes a qualified lead in
  your CRM. It fits the whole point of the bot.
- **Recognize but defer.** The bot knows the competitor grade is a real buying signal and routes them to a
  specialist, without stating the equivalent itself. Most conservative, but you lose the instant-answer edge.

My default, unless you tell me otherwise, is the middle option: gate the competitor match behind a quick
contact capture. You get the lead, the visitor gets the answer, and your cross-reference is not sitting in
the open for anyone to scrape.

Let me know if that works, or if any of this data should stay off the bot entirely.

With gratitude,
Zach

---
## Internal note (not for Todd)
- Default (pending Todd): **gate the competitor cross-reference behind lead capture** (contact-first, then answer).
  This doubles as a qualifier (anonymous competitor fishing is screened; a real buyer self-identifies) and
  aligns with the QATF001 "Match Needed / Offset Incumbent" sub-type + the ICP-as-state read.
- Until Todd confirms: **do NOT upload `PRL-Competitor-Cross-Reference.pdf` to Tidio as an open KB source.**
  The catalog + G/B/B PDFs are fine to upload (public product data). The competitor file waits on this yes,
  and ideally on the gating mechanism, not an open upload.
- Build implication: "gated behind capture" means the competitor match lives behind the flow's contact-capture
  step (or a Lyro handoff to the capture flow), not as an always-open KB doc. Scope with the 1.3/persona build.
