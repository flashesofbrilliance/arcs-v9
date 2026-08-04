# PRL Resins Chatbot — Project Knowledge Base
_Shared with: Zach + Todd. Kept current. Last updated 2026-08-04._
_Plain-language single source of truth for where the project stands and where it is headed._

> This is the Todd-safe knowledge base (no internal handling notes). The technical detail lives in the
> code repository; this page is the non-technical view.

## Where things stand
The lead-capture chatbot is built, branded, and tested on a private copy of the site. It captures a
visitor's details and their resin need and hands a clean lead to your sales team. The one thing left
before it goes live on the real site is turning on lead delivery, which needs a few short confirmations
from your side (below).

## What is already done
- The chatbot is built and running on a private copy of your site, branded in PRL colors.
- It greets visitors, sorts them, and captures contact plus the resin they use now and the one they
  need, the application, and the spec.
- It routes each lead to your sales manager, and can auto-route by territory once switched on (your
  rep-to-state map is already in).
- Safety checks are in place so the bot never states a spec, certification, or price. It hands those to
  a person.

## What is needed to go live (the pre-flight checklist, in order)
1. Three quick answers: require a phone number on every chat or allow a placeholder; add a "Chatbot"
   option to your Lead Source list; approval to create one clearly marked test lead.
2. A sandbox login for SugarCRM, or a yes to that single test lead.
3. A 30-minute session with your sales manager and whoever runs your reports.
4. Who owns the chatbot day to day once it is live.
5. Unbounce and Google access, later, only for the landing-page step.

## The roadmap ahead (scope, in sequence)
- **Now: go live.** Finish and prove the chatbot on the real site.
- **Next: reliable delivery and the four-hour number.** Every lead lands complete and fast, with an
  instant acknowledgment to the prospect, and we start showing time-to-first-touch.
- **Then: complete lead records.** Fill in the business email and company details that are missing on
  most leads today, using tools you already have.
- **Then: your paid landing pages.** Give each campaign page its own chatbot opening, wired to your CRM.
- **Later: a smarter assistant.** Let the bot handle open-ended "help me choose" conversations, once its
  handoff to your CRM is proven.

The guiding idea through all of it: make the tools you already own work together and cost less, and keep
it invisible to your reps so a better lead just shows up where they already look.

## What the project surfaced about the business
Building the chatbot meant following a lead through your systems. A few things worth knowing:
- About $26.5M of closed-won revenue has no lead source recorded, so it is hard to see which channels
  make you money. Tagging every lead starts to close that.
- Your CRM already holds 231 deals tagged with the competitor grade the customer was replacing, which
  is a ready-made picture of who you win against.
- Almost none of your current leads carry an email, which slows follow-up.
- The four-hour callback window you aim for is not on any report yet.

## Tools involved
Tidio (the chat tool) · SugarCRM (your CRM) · Zapier (the connector) · ZoomInfo, Mailgun, Unbounce
(for enrichment, delivery, and landing pages). The goal is for PRL to own all of these for a clean
handoff.

## Where the detail lives
The live status page is at prl.arcs.care. The full technical build spec is a separate link Zach can
share on request.
