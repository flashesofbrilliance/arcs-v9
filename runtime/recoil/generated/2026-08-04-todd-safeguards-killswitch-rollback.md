# PRL Go-Live — Safeguards, Kill Switches, Rollback (in-flight DR)
_2026-08-04 · the 0%-margin contingency layer. A client's LIVE production CRM = free-solo topology._
_Governing rule: **sandbox-first for everything that touches production. No blind writes to live.**_

## The one rule
Nothing touches the **live** prlresins.com site or the **live production** SugarCRM until it is proven
in a **lower / copy-down sandbox**. This includes the "Chatbot" lead_source value, the Create-Lead
mapping, the widget, and any test lead. Todd confirmed he can add the Chatbot value; we add + verify it
in the sandbox FIRST, then replicate to production only after it works clean.

## Per-surface: sandbox → kill switch → rollback → blindspot monitor

### 1. SugarCRM (production writes — highest stakes)
- **Sandbox-first:** add the "Chatbot" picklist value + run the Create-Lead flow in the copy-down
  instance. Replicate to prod only after a clean end-to-end test.
- **Kill switch:** turn OFF the Zapier Zap (Create-Lead step) → all Sugar writes stop instantly. One toggle.
- **Rollback:** test leads are labelled + deletable; the Chatbot picklist value is **additive** (safe
  to remove, doesn't break existing records); no destructive schema changes, ever.
- **Blindspot monitor:** a silent Zap failure = leads vanish and nobody notices. Watch Zapier task
  history; run a periodic canary test lead to confirm the pipe is live.

### 2. Tidio bot
- **Kill switch:** deactivate the flow / set the widget offline → the bot stops instantly.
- **Rollback:** flows are versioned through the git-tracked generator (`prl_tidio_flow_gen.py`); revert =
  reimport the prior JSON. Nothing is hand-edited-only.
- **Sandbox:** the WP dev site (wfaprlredev26) is the copy-down; never publish via prod GTM to test.

### 3. Live WordPress site
- **Never edit live directly** — staging/dev only. **Kill switch:** remove the Tidio snippet / GTM tag.
- **Watch:** GTM go-live hits the **shared prod container** (GTM-WLP9C76) — it is the single controlled
  go-live switch, not a dev tool. Never flip it on dev.

### 4. Mailgun (notifications + autoresponder)
- **Sandbox:** test sends to internal addresses first. **Kill switch:** pause the sending domain / disable
  the notify step. **Rollback:** dedicated subdomain, zero impact on live prlresins.com mail.

### 5. ZoomInfo (enrichment)
- **Spend cap** on enrichment volume to prevent runaway per-lookup cost. **Kill switch:** disable the
  enrichment step; leads still create, just without enrichment.

## Blindspot safeguards (the things that bite silently)
- **Silent Zap failure** → no leads land. Monitor: task history + canary lead.
- **Duplicate leads** (bot + Unbounce both fire). Add a dedup check before Create-Lead.
- **location_c format mismatch** (abbreviation vs full name, incl. Canadian provinces) → lead fails to
  create. Verify against a real record before go-live.
- **Tidio 51-conv cap** (only if Lyro on) → hard-stop or overage. Confirm behavior before enabling. Lyro
  stays OFF for 1.1.
- **Cost bubble** → the change-work-order trigger + vendor spend caps.

## Rollback contingency (if something breaks in production)
1. **Immediate:** hit the relevant kill switch (Zap off / flow off / snippet off).
2. **Assess:** Zapier task history + Tidio inbox + Sugar audit log.
3. **Revert:** reimport prior flow JSON / delete test leads / remove the picklist value if needed.
4. **Communicate:** if a real lead was affected, tell Todd **immediately**. No silent failures — a hidden
   break is worse than a visible one, and trust is the apex objective.

## Where this lives in the system
This is the **in-flight / disaster-recovery** layer of the flight-operations loop
(`flight-operations-system.md` §1B). Each pre-mortem failure mode maps to a kill switch + a rollback here.
Sandbox-first is the pre-flight gate; these are the in-flight procedures for when a surprise hits.
