# PRL Chatbot and Lead Capture: what we found, what to fix, and what we need from you
_For Todd. Plain and honest, so there are no surprises. Numbers below were double-checked against your CRM
directly (read-only, nothing changed)._
_2026-08-07_

## The one-line version
Your website is capturing good leads, but a chunk of them never reach your CRM, and your main lead form is
mostly spam right now. The chatbot fixes the capture-and-delivery leak going forward, and there is a batch of
real, unworked leads we can recover today. A few quick approvals from you unlock all of it.

## What we found (observations)
1. **The chatbot is built and capturing leads.** The one step left is turning on delivery into your CRM.
2. **Your main "Material Alternative" form is about 96 percent spam.** It has no working spam protection right
   now (the anti-spam honeypot is off and the CAPTCHA is present but not set up). The spam buries the real
   inquiries so nobody can find them.
3. **Underneath the spam are real, high-value inquiries.** Across the last three and a half years we found
   about 38 genuine ones, and after checking your CRM carefully, **about 29 of them never made it in.** They
   include a program inquiry tied to Tesla, a large international order (876 kg), and quote requests from names
   like Siemens, OtterBox, Momentive, Amphenol RF, and Ideal Industries, many asking for alternatives to
   competitor materials (Lexan, Valox, Makrolon, Lustran).
4. **Emails are not populating in the CRM because the automated paths do not send them.** The email field
   works fine when a value is supplied. A person entering a lead by hand includes it; the automated form path
   does not. The chatbot captures the email every time.
5. **The form-to-CRM delivery (via Zapier) is turned off.** That is a big reason the real leads orphaned.
6. **The ZoomInfo enrichment writeback into your CRM has an expired connection**, so that data is not currently
   flowing either.
7. **Your CRM already has strong tools** (enrichment, lead scoring, integrations) that look underused. Before
   adding anything new, it is worth making sure you are getting full value from what you already pay for.

## What it means (implications)
- **Real revenue is leaking.** Genuine buyers reached out and were never worked, simply because the leads got
  lost between the website and the CRM.
- **The chatbot is the permanent fix for that leak** - capture the email every time, and deliver reliably, so
  no future lead orphans the way these did.
- **Once delivery is on, we can finally measure** your four-hour response number and show what the chatbot adds
  versus before.

## Recommended fixes (in order)
1. **Clean up the form spam** (about a one-hour fix): turn on the honeypot, set up a proper bot check
   (reCAPTCHA or Cloudflare Turnstile), and block the known spam patterns. Real leads become visible again.
2. **Turn on chatbot lead delivery** into your CRM, with the email captured every time. Nothing touches your
   live system until it is tested on one labeled test lead.
3. **Recover the roughly 29 orphaned leads** - qualify them and hand the real ones to your sales team to work.
4. **Reconnect the ZoomInfo enrichment** so that data flows again.
5. **Small CRM housekeeping:** add a "Chatbot" lead source so we can measure this channel cleanly, and decide
   how to handle the required phone field.

## Next steps
- Secure a safe way to prove delivery: a sandbox copy, or one clearly labeled test lead we create and remove
  together. This is the single thing that unlocks go-live.
- Then, in order: clean the form spam (test on staging first), wire the chatbot delivery, recover the orphaned
  leads, and only then move on to the smarter phases.

## What we need from you (approvals)
1. **A safe way to test CRM delivery** - a sandbox, or your OK to create and delete one labeled test lead.
2. **OK to add spam protection to the forms** - we would apply it on the staging copy first, show you the
   before and after, then put it live with your go-ahead.
3. **Phone field:** require it on the chatbot form, or allow it to be optional with a stand-in value?
4. **OK to add a "Chatbot" lead source** to your CRM list.
5. **OK to recover and hand over the orphaned leads** to your sales team.
6. **Later:** OK to reconnect the ZoomInfo enrichment writeback.

Nothing here changes your live system without your go-ahead. The one move that unlocks the most at once is the
safe test path for delivery.
