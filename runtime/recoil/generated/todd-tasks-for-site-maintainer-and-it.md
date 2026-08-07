# Tasks for the site maintainer (Josh) and IT
_For Todd, to route to the right people. Everything below is based on what we observed this week (read-only, on
the staging copy). None of it is done yet; it is flagged so the person who owns each area can action it, on
staging first and then production. Plain language, no personal data._
_2026-08-07_

## For the website maintainer (Josh): site, forms, plugins
1. **Turn on spam protection for the Gravity Forms (the priority).** The main "Material Alternative" form has
   no working protection today: the built-in anti-spam honeypot is off, and the CAPTCHA field is present but
   has no keys set, so it does nothing. Steps:
   - Enable the Gravity Forms honeypot (one toggle).
   - Add real reCAPTCHA v3 or Cloudflare Turnstile keys to the existing CAPTCHA field (invisible, no user cost).
   - Apply the same keyword/blacklist rules that already exist on the older "PDF Form" to the "Material
     Alternative" and "Contact Us" forms.
2. **Tighten the form fields.** Make the free-text material field reject links and HTML and require a minimum
   length, so bots that paste pitches and URLs are rejected.
3. **Confirm the chatbot widget is correctly installed on production.** It is live on the staging copy; confirm
   the tag fires on the real site when we go live.
4. **Check form notifications and delivery.** Confirm form submissions notify a monitored inbox, and note that
   nothing currently writes form leads into the CRM automatically (the old connector is off). We will design
   the delivery; Josh confirms the site side.
5. **Plugin and security hygiene.** Keep the active plugins current, and confirm the site security plugin is
   running. Coordinate the staging-to-production push when we roll the chatbot and the fixes live.

## For IT: email, DNS, and Microsoft 365
1. **Email deliverability.** Set up or confirm SPF, DKIM, and DMARC for the domain so form confirmations and
   the chatbot autoresponder do not get spam-filtered.
2. **The forwarding rule and DNS that did not take.** A Microsoft 365 email forwarding rule and a domain/DNS
   change were attempted but do not appear to have applied yet. Please confirm and finish those.
3. **info@prlresins.com routing.** Confirm this inbox is monitored, and decide where chatbot and form
   notifications should land so real leads are seen quickly.

## How this fits
None of this blocks our chatbot work, and we can do most of it with you. Flagging it here so the right owner
handles each piece, on staging first, then production when we roll everything live. The single highest-value
item is the form spam protection, since it is currently burying real leads.
