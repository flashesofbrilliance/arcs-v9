# Tasks for the site maintainer (Josh) and IT: step by step
_For Todd, to route to the right people. Based on what we observed this week (read-only, on the staging copy).
None of it is done yet. Do everything on the staging copy first, then production. Plain language, no personal
data. Exact menu labels can vary slightly by plugin version._
_2026-08-07_

## For the website maintainer (Josh): Gravity Forms spam protection and fields
Goal: stop the automated spam that is burying real leads on the main form.

**1. Turn on the honeypot (free, one toggle).**
   - WP Admin > Forms > open "Material Alternative" > Settings > Form Settings.
   - Scroll to "Anti-spam honeypot" and turn it ON. Save.
   - Repeat for the "Contact Us" form.

**2. Turn on a real bot check (reCAPTCHA v3 or Cloudflare Turnstile).**
   - WP Admin > Forms > Settings > reCAPTCHA.
   - Enter the Site Key and Secret Key (create them free in the Google reCAPTCHA admin, v3 recommended). Save.
   - Then open each form, click the CAPTCHA field, and confirm its type is set to reCAPTCHA. Save.
   - (The CAPTCHA field already exists on the form; it just has no keys, so today it does nothing.)

**3. Add keyword / blacklist filtering.**
   - The older "PDF Form" already has the blacklist plugin rules configured. Copy the same rules onto
     "Material Alternative" and "Contact Us".
   - Block obvious spam terms (for example "eric", "xrumer") and reject any link or URL in the material field.

**4. Tighten the material field.**
   - Edit the "Which material alternative are you looking for?" field: make it required, set a minimum length,
     and reject links / HTML.

**5. Confirm the chatbot widget fires on production** when we go live (it is live on the staging copy now).

Test each change on staging, then push to production. Highest value item is the bot check plus honeypot in
steps 1 and 2.

## For IT: email deliverability and DNS
**1. Email authentication (so form and chatbot emails do not go to spam).**
   - Add or confirm SPF, DKIM, and DMARC DNS records for prlresins.com.

**2. Finish the changes that did not take.**
   - A Microsoft 365 email forwarding rule and a domain / DNS change were attempted but have not applied yet.
     Please confirm and complete them.

**3. info@prlresins.com routing.**
   - Confirm this inbox is monitored, and decide where chatbot and form notifications should land so real leads
     are seen quickly.

## How this fits
None of this blocks our chatbot work, and we can do most of it alongside you. It is flagged here so the right
owner handles each piece, on staging first, then production when we roll everything live.
