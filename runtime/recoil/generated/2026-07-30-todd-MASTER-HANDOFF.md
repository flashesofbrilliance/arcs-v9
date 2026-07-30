# PRL Resins Chatbot — MASTER HANDOFF & Document Index
_2026-07-30 · supersedes the earlier deploy-integration handoff as the top-level pickup point_

## 1. Executive summary
Phase-1 lead-capture chatbot for PRL Resins (Polymer Resources Ltd). Todd paid ($1,552.51, Jul 24)
and is a close friend + full-budget client. The bot is **built, branded, activated, and tested**
in Tidio, running on a local sandbox and (pending one login) the WP dev site. The one thing left
to make it deliver leads is **lead delivery (email + SugarCRM via Zapier)**, which is currently
**blocked on a Tidio plan upgrade** (webhooks are paid). Everything else is done or staged.

## 2. Current state
**DONE**
- Tidio flow "PRL Resins - Lead Capture" ACTIVE + tested end-to-end (real lead captured Jul 30).
  Greeting → "What brings you in?" (5 buttons: I know what I need / Help me choose / Have someone
  call me / Guides and resources / Something else) → Branch A/B/C + callback → shared contact
  capture. "Guides and resources" serves live prlresins.com links.
- Voice tuned to Todd + the website ("straight to the source, no phone trees, within a few hours").
- Branding: maroon #7A1F2B header, white text, gold #C9A227 accents. Welcome "Welcome to PRL
  Resins"; launcher "Chat with our team". Emojis removed (CSAT survey strings still have them).
- Lyro AI OFF; default subscribe/newsletter flow OFF.
- Local sandbox (Docker/OrbStack) at http://localhost:8080 + pixel-perfect homepage at
  /prl-home.html (pulls live theme assets). Manage: `cd ~/prl-resins-local && ~/.orbstack/bin/docker compose start`.
- Tidio plugin installed on the WP dev site (wfaprlredev26); Todd invited to Tidio (Chat Agent).
- Zapier: draft Zap "Send PRL website chatbot lead emails to Gmail" (Catch Hook + Gmail) built.

**BLOCKED / PENDING (owner)**
- **Tidio webhook action = PAID** → upgrade needed before Tidio can POST to Zapier. [Zach + rep]
- Connect Tidio plugin to the existing account on the dev site (log in, not create). [Zach]
- Gmail OAuth connect in the Zapier Zap + copy the Catch Hook webhook URL. [Zach]
- Wire the Tidio webhook node to the Zapier hook (post-upgrade). [Claude]
- SugarCRM Create-Lead step (copy the existing Unbounce→Sugar mapping). [Zach + Claude]

## 3. Key decisions (the "why")
- **Lead delivery = Zapier**, not Tidio's paid API tier for CRM logic, and not the auto "new
  contact" trigger (our fields are session variables). Webhook node → Catch Hook → Gmail + Sugar.
- **All capture fields are session variables** (answer_to_variable=false). Contact-property binding
  broke activation (system props enforce validation types; non-system names don't exist). Session
  vars ride the webhook payload. Add Update-contact-property nodes later if wanted on the record.
- **Dev deployment = Tidio WP plugin, NOT GTM.** The dev site loads the PROD GTM container
  (GTM-WLP9C76, agency-managed by 9rooftops) with GA4 G-WMRP7ELVRV. Publishing a Tidio tag there
  would hit LIVE. GTM is the eventual go-live switch (covers WP + Unbounce in one), not a dev tool.
- **Names redacted → titles only** (bot persona "Customer Service Manager, Global"; routing by role).
- **Hosting is two-platform**: WordPress (main) + Unbounce (SEM landing pages, e.g. /sabic-alternatives).
- **Generate-and-import** is the flow workflow: edit `prl_tidio_flow_gen.py` → regenerate JSON →
  Tidio Import (the Browse/file-select is a manual step Zach does).

## 4. Document index
**Specs & build (git: runtime/recoil/generated/)**
- `2026-07-30-todd-MASTER-HANDOFF.md` — this file (top-level pickup).
- `2026-07-20-todd-chatbot-branch-logic-v1.md` — v1.4 conversation design + field mapping +
  material matrix + hosting/webhook architecture. THE spec.
- `prl_tidio_flow_gen.py` — generates the importable Tidio flow JSON. Source of truth for the flow.
- `2026-07-30-todd-tidio-build-sheet-v1.md` — click-by-click Tidio build (v1.1).
- `2026-07-30-todd-tidio-voice-script-v1.md` — every bot line, voice-tuned.
- `2026-07-30-todd-tidio-triggers-and-picker-v1.md` — SEM URL triggers + product picker.
- `2026-07-30-todd-personas-routing-persona-v1.md` — market personas, territory map (titles),
  bot persona, policies-as-FAQ.
- `2026-07-30-todd-tidio-deploy-integration-handoff.md` — deploy + integration steps (subsumed here).
- `prl-chatbot-NEW-PROJECT-CLAUDE.md` — cold-start if spun into its own repo/folder.
- `precall-todd-hotes-2026-07-20.json`, `pilot-court-todd-hotes-2026-07-13.json` — earlier call artifacts.

**Client-facing surfaces**
- Status SSOT: https://todd-call.arcs.care (public/todd-call.html) — updated as work lands.
- Build spec artifact: https://claude.ai/code/artifact/e459357f-af02-4c0a-b58d-e9d1b4d7fe13
- Project hub (internal): https://claude.ai/code/artifact/d9492ec7-5378-4437-ae07-634e84fef7b3
- Other todd pages: public/todd-logictree.html, public/todd-teardown.html.

**Source docs from PRL (staged: scratchpad/prl-chatbot-handoff/sm-source-docs/)**
- QATF001 New Opportunity Form v1.1 (the SM's intake form → field mapping).
- Engineering Thermoplastics Material Selection Matrix (Good/Better/Best → Branch B recommender).
- Product Selection Guide 2025 PDF (competitor cross-ref tables are page-IMAGES → OCR fast-follow).

**Memory (machine-local: ~/.claude/projects/-Users-zharris-arcs-v9/memory/)**
- `project_todd_hotes_prl_resins.md` — running tracker, all status blocks + gotchas + this session.

## 5. Environment & access facts
- Tidio public key: `nemtpdglmxzbcpmqlqh1gnj3wmgqsxeu`. Account owner: zach.harris@gmail.com
  (account named "PRL Resins"). Todd = Chat Agent (invite pending).
- WP dev: wfaprlredev26.wpenginepowered.com (WP Engine). Theme = Divi Child. Plugins incl. HFCM
  (header/footer code), Unbounce Pages, Tidio Chat, Divi. Live GTM container GTM-WLP9C76 loads on
  dev (shared with prod → do NOT publish there for dev).
- Zapier: Todd's account (avatar TH). Existing live Unbounce→SugarCRM zaps (Sabic/Covestro/
  Ventilator) = SugarCRM already connected + Create-Lead mapping to copy. Paid plan (Webhooks OK).
- GTM account "Polymer" (ID 6002602763), managed by 9rooftops.com; Zach accepted the invite.
- Browser automation runs through Google Chrome (claude-in-chrome extension); NOT Comet. File
  uploads + OAuth + native dialogs are manual (Zach). Deploys from main worktree frosty-kepler-b69f51.

## 6. Next steps (prioritized)
1. **Pick the Tidio tier** that includes: webhook/API action, remove-branding, operator seats/roles.
2. After upgrade: **wire Tidio webhook node** → Zapier Catch Hook URL; **connect Gmail** in the Zap.
3. Test a lead end-to-end → confirm email arrives.
4. Add **SugarCRM Create-Lead** step in the Zap (copy the Unbounce→Sugar mapping).
5. Finish **dev-site plugin connect**; verify widget on dev in Incognito.
6. **Keyword links / resin recognition (B)** + **SEM onramp flows** for Unbounce pages.
7. **Go-live** via prod GTM (GTM-WLP9C76) once approved on dev.
8. Optional: change Tidio agent Name field to a title; strip CSAT emojis; offline pixel-perfect site.

## 7. Constraints (standing)
No em-dashes in Todd-facing copy; short plain language. Never enter credentials/OAuth (Zach does).
Don't touch live prlresins.com until dev-approved. PRL should eventually OWN its Tidio + Zapier +
GitHub (transfer ownership, not just admin) for a clean client handoff.
