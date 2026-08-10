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
- **Applied in staging (`wfaprlredev26`), 2026-08-10:**
  - Honeypot ON — Contact Us (id 7) + Material Alternative (id 6).
  - Submission speed check ON, 2000ms / Normal — both forms.
  - **Akismet integration ON** (Forms &rarr; Settings) — site-wide across all Gravity Forms; the Akismet
    plugin was already installed + active. This is the no-code, no-PHP spam filter. Chosen over the generated
    `gform_entry_is_spam` snippet because the site has no Code Snippets / WPCode host and editing Divi's
    functions.php on a client site carries white-screen risk. The `prl-gf-spam-filter.php` snippet stays in
    the repo as the fallback if a safe PHP host is added later.
- **Applied 2026-08-10 (round 2):**
  - Honeypot + submission speed check ON, Apply Now (id 4).
  - **Form-factor clarifier field ADDED** to Contact Us (id 7, field input_7) + Material Alternative (id 6,
    field input_9). Optional dropdown, label "What form do you need the material in?", placeholder "Select one
    (optional)" so there is no biased default; choices: Pellets / compound (what we make) &middot; Sheet, rod,
    or film &middot; Not sure. Verified on the live GF preview for both forms (options read from the rendered
    DOM match exactly).
- **FINDING (not ours to fix in staging):** the forms already carry a Google reCAPTCHA, but on the staging
  domain it renders `ERROR for site owner: Invalid domain for site key` &mdash; the site key is domain-locked to
  the production host, so reCAPTCHA does not validate on `wfaprlredev26`. Expected on staging; on production it
  should work IF the key lists `prlresins.com`. Worth a one-line confirm with the site owner that the prod key
  is valid. This is exactly why we layered honeypot + speed check + Akismet as the real, domain-independent
  protection.
- **CLIENT DECISION for Todd (terse, give him both, rec = A):** reCAPTCHA works on prod, no-op on staging
  (key domain-locked to prod). NOT CLI-creatable for the classic v2/v3 key GF uses (console-only; Enterprise
  keys are `gcloud`-creatable but wrong product, need GCP billing, and GF's native field won't accept them).
  - **Option A (RECOMMENDED): leave as-is.** reCAPTCHA stays live on prod; honeypot + speed check + Akismet do
    the real, domain-independent work. No action.
  - **Option B: extend key to staging.** Add `wfaprlredev26.wpenginepowered.com` to the key's allowed-domains
    in Google reCAPTCHA admin (30 sec, additive/reversible, zero prod risk) to test reCAPTCHA pre-go-live.
- Waiting on Todd: his negative-keyword / anti-ICP list to extend `todd_provided`. When it lands, the chatbot
  picks it up automatically; the GF blocklist regenerates via `python3 exclusions.py`.
