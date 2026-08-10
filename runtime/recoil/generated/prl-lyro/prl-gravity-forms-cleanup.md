# Gravity Forms cleanup — spam + anti-ICP filter (staging first, then live)

_2026-08-10 · Todd approved on the Aug 10 call (Zach applies: staging → review → live; Josh only hosts). The
site form has **no working spam protection today** (anti-spam off, no bot check), and ~96% of submissions were
spam. This layers a fix and wires it to the ONE extensible exclusion source so the chatbot and the form stay
in sync._

## The fix — layered, cheapest-and-broadest first

1. **Honeypot (free, invisible).** Gravity Forms → Form Settings → **Enable anti-spam honeypot.** Kills most
   naive bots, zero user friction. First and cheapest.
2. **Bot check.** Add a real bot gate: **Cloudflare Turnstile** (free, near-invisible, best UX) via the GF
   Turnstile add-on, or reCAPTCHA v3 (score-based). Recommend Turnstile. This catches the automated bulk.
3. **Keyword blocklist (the extensible backstop).** Paste the generated list into GF's **Keyword Blocklist**
   (or a per-field validation). Generate it any time with `python3 normalization/exclusions.py` →
   `gravity_forms_blocklist()` (29 terms today: seo/backlink/loan/crypto/etc + any `block`-tagged anti-ICP).
   Hard-spam that slips past the bot check is rejected here.
4. **Form-factor clarifier field.** Add a required select — *"What form do you need the material in?"* →
   **Pellets / compound (what we make)** · Sheet, rod, or film · Not sure. "Sheet/rod/film" triggers the soft
   prequal + a low-intent tag. This encodes Todd's pellets-not-sheets distinction at the point of entry.
5. **Anti-ICP soft filter (never lose a real lead).** For a real person who is a wrong fit (the "sheet" seekers
   Todd flagged) and passes the blocklist, use `exclusion_check()`'s **prequal** message ("we make pellets, not
   sheet, are you after a moldable grade?") — a clarifying step, not a hard block. Real leads are never dropped.

## Extensibility — the whole point (Todd's list drops in with no code change)

Every rule lives in **one file**: `normalization/exclusions.json` (chatbot + form share it via
`exclusions.py`). When Todd sends his negative keywords / garbage-lead examples:
- Drop each into `todd_provided.entries` (`prequal`) or `hard_spam_signals.keywords` (`block`).
- The **chatbot picks them up automatically** (`exclusion_check`).
- **Regenerate the GF blocklist** (`python3 exclusions.py`) and paste — no rebuild, no code change.

So the form-factor cleanup and the chatbot filter are the same brain; Todd's future list improves both at once.

## Apply order + verify
1. **Staging** (`wfaprlredev26`): honeypot on → Turnstile → blocklist → form-factor field. Test three inputs:
   a spam string (blocked), a "sheet of polycarbonate" string (soft prequal, not dropped), a real resin lead
   (passes clean). These mirror the `exclusions.py` self-test (8/8).
2. **Review with Todd.**
3. **Live site** (`prlresins.com`), same config.

## Status
- Engine built + tested: `normalization/exclusions.json` + `exclusions.py` (self-test 8/8), seeded with Todd's
  "sheet" signal + common form spam.
- WordPress application (honeypot/Turnstile/blocklist/field) is the next click-step, on staging first.
- Waiting on Todd: his negative-keyword / anti-ICP list to extend `todd_provided`.
