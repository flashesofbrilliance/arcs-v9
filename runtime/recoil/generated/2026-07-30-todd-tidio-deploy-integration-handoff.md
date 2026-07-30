# PRL Chatbot — Deploy + Integration Handoff (2026-07-30)

The bot is BUILT, ACTIVATED, and BRANDED in Tidio. This handoff covers what's left: connecting
it to the dev site, delivering leads (email + SugarCRM via Zapier), Home quick-links, and the
eventual go-live. Steps marked **[you]** need your credentials/decisions; **[Claude]** I can drive.

## Current state (done)
- Tidio flow "PRL Resins - Lead Capture" ACTIVE: greeting -> "What brings you in?" (4 buttons:
  I know what I need / Help me choose / Have someone call me / Something else) -> Branch A/B/C +
  callback -> shared contact capture. Tested end-to-end on the sandbox.
- All capture fields are SESSION VARIABLES (not contact properties) -> they ride the webhook/
  email node, but NOT Tidio's auto "new contact" Zapier trigger. Use a node to pass them.
- Branding: maroon #7A1F2B header, white text, gold #C9A227 accents. Welcome header "Welcome to
  PRL Resins"; subtext "Looking for a resin or a spec? We'll get you to the right specialist
  fast."; launcher "Chat with our team". Emojis removed (CSAT survey strings still have them).
- Lyro OFF; default subscribe flow OFF.
- Tidio public key: `nemtpdglmxzbcpmqlqh1gnj3wmgqsxeu`
- Flow generator (source of truth for the flow): `runtime/recoil/generated/prl_tidio_flow_gen.py`
  -> `python3 prl_tidio_flow_gen.py -o prl-chatbot-flow.json`, then Tidio Import (Browse = manual).

## Environment facts
- Dev WP: `wfaprlredev26.wpenginepowered.com` (WP Engine). Theme = **Divi Child**. Installed
  plugins incl. **HFCM** (Header Footer Code Manager), **Unbounce Pages**, Tidio Chat (just added).
- Live GTM container = **GTM-WLP9C76** ("prlresins.com", account "Polymer", managed by
  9rooftops.com). This is PRODUCTION -> do NOT publish the bot here until go-live.
- SEM/PPC landing pages = **Unbounce** (e.g. /sabic-alternatives), separate from WP.

## 1. Connect the bot to the DEV site  [you]  (in progress)
WP admin -> Tidio Chat -> "Already have an account? Log In" -> sign in with the EXISTING Tidio
account (NOT create new). This deploys the widget to the dev site only. Verify: open the dev
front-end in Incognito -> the maroon "Chat with our team" bubble appears; opening it shows
"Welcome to PRL Resins" + the greeting + 4 buttons.
- The plugin only affects this dev WP install. Live untouched.

## 2. Lead delivery — Zapier (email + SugarCRM in one)  [you + Claude]
Decision made: webhook/Zapier node, not the auto-trigger (because fields are session variables).
1. **[you]** In Zapier (logged into the same Chrome), create a Zap:
   - Trigger: **Webhooks by Zapier -> Catch Hook**. Copy the hook URL.
   - Action A: **Gmail/Email by Zapier -> Send email** to zach.harris@gmail.com (test), body =
     the mapped fields. (Swap to the sales manager / VP National Sales once verified.)
   - Action B: **SugarCRM -> Create Lead**, mapping fields -> QATF001-aligned lead fields
     (Customer Contact=name, Email, Phone, Customer Name=company, Current Grade=current_resin,
     Application/Problem=application, Special Tests=requirements, + desired_resin_or_spec,
     territory, branch). Connecting SugarCRM = your OAuth **[you]**.
2. **[Claude]** In the Tidio flow, add a node at the end of capture (and callback) that POSTs all
   session variables to the Zapier hook URL: use the flow's **API call** node (or "Send to
   Zapier" if present). Map every variable. Then re-activate.
   - NOTE: needs one Tidio flow edit + (if regenerated) a manual Import Browse **[you]**.
3. **[you]** Turn the Zap on; run one test lead from the dev widget; confirm email + SugarCRM lead.

## 3. Home quick-links + broaden triggers  [Claude]
- Tidio Home "quick actions" = **conversation starters** (prompts, not URL links). To make them
  functional (not dead-end), pair with broadening the flow trigger beyond "First visit" to also
  fire on **chat open** (and optionally returning visitor). That single change also fixes the
  "returning visitor sees old session" testing annoyance.
- Add starters mapped to paths: "Find an alternative to my resin", "Help me choose a resin",
  "Talk to a specialist". Wire via a trigger so they route into the flow.

## 4. GO-LIVE (later, after dev approval)  [you decide]
Two clean options to put the bot on live prlresins.com + Unbounce:
- **GTM** (covers WP + Unbounce): add a Custom HTML tag (Tidio snippet) in GTM-WLP9C76, All Pages
  trigger, Submit/Publish. This is the single switch for both platforms. Only do this at go-live.
- **Or** HFCM/Tidio plugin on live WP + Tidio snippet in Unbounce Script Manager separately.
- SEM onramp flows: URL-scoped greetings for /sabic-alternatives etc. (see triggers-and-picker doc).

## 5. Open decisions
- **Remove "Powered by Tidio"** = Tidio **Plus plan** (paid). Add to the pricing-tier quote you're
  getting from the rep.
- Tidio agent **Name** field still "Todd Hotes" -> change to a title (e.g., "Customer Service")
  per the redact-names preference.
- CSAT survey strings still have emojis (only appear if surveys run) -> strip if desired.
- Territory auto-routing draft exists (from /our-team/) but MVP routes to one fielding inbox.

_Companion docs (all in runtime/recoil/generated/): branch-logic-map v1.4, voice-script v1,
triggers-and-picker v1, personas-routing-persona v1, tidio-build-sheet v1.1, prl_tidio_flow_gen.py._
