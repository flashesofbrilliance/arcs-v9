# PRL Lyro Configuration Plan — 80% capability, lean + extensible
_2026-08-06 · Token-efficient, not overengineered, structured for reuse. Grounded in a sourced Tidio/Lyro
research pass (see §Research basis) + the PRL KB we already collected + the anti-fabrication design._

## The one design fact everything hangs on
Lyro is **answer-from-knowledge-only**: if the answer is not in your curated content, Lyro **auto-forwards
to a human** rather than inventing. That native behavior *is* the anti-hallucination guarantee. So the build
is mostly **curation + routing**, not custom guardrail engineering. This is why 80% of the value is cheap.

Corollary: **the knowledge base is the guardrail.** Keep unverified specs/certs/prices OUT of it. What is
not in the KB becomes a handoff, which is the correct, safe failure.

---

## The 5 config surfaces (this is the whole 80%)

### 1. Knowledge base (Knowledge → Data Sources)
- **Load, verified only:** Product Catalog PDF, Good/Better/Best matrix, Competitor cross-reference
  (Todd approved open/ungated), the market/application **sell sheets** (EE, Medical, Transportation,
  Building, Consumer, Sustainability, Structural Foam), the **UL 94/746 explainer** (`UL-Jun16.pdf` — good
  for "what does V-0 mean," NOT per-grade file numbers), and the site URL crawl (**caps at 60 pages** —
  point it at the product-capability pages).
- **Hold out until sourced:** per-grade UL yellow-card file numbers (not in any asset we have), live
  pricing, lead-time promises. These route to a human by design.
- **Grade tech sheets:** the 11 representative datasheet PDFs are Tidio-uploadable (direct PDFs). The full
  per-grade set (IDES `I=73811`) is the extensible-20% crawl, queued.
- Cadence: review the **Suggestions** report (unanswered questions) monthly; each unanswered question is a
  KB gap to close, never a reason to loosen the guardrail.

### 2. Guidance prompt (Behavior → Guidance)
Controls tone + the never-invent rule. Draft (drop-in, edit in-account):
> You are the assistant for Polymer Resources (PRL), a US specialty resin manufacturer. Audience: injection
> molders and OEM engineers. Be concise, plain, technical-but-friendly; no emoji. Answer **only** from PRL's
> knowledge base. **Never state a specific property value, UL/certification status, file number, price, or
> lead time unless it appears verbatim in the knowledge base.** If a question needs a value you do not have,
> or you are unsure, say so plainly and offer to connect them to a PRL specialist, then capture their contact.
> When someone names a competitor grade (e.g. "equivalent to Lexan"), give PRL's cross-reference family if it
> is in the knowledge base, and offer the specialist for a confirmed match.

### 3. Flows ↔ Lyro split
- **Enabling Lyro auto-disables your "Visitor says" Flows** — so the split must be deliberate, not accidental.
- **Deterministic Flow** owns: the lead-capture form (name, company, **phone `phone_work` is required in
  Sugar**, email, application/grade interest) and the **webhook → Zapier → SugarCRM**. Keep lead delivery
  in the Flow, not a Lyro Action — Lyro Actions are not rolled back on failure, so the irreversible CRM write
  stays in the tested deterministic path for MVP.
- **Lyro** owns: open-ended Q&A from the KB, competitor cross-reference lookups, "which family for my market."
- **Persona tag:** ask one early qualifying question ("Are you specifying a material, or sourcing one you
  already spec?") → branch/tag OEM vs molder. Do **not** rely on Lyro to auto-classify user type (it won't
  reliably). Tag now, use the tag for routing/attribution later.

### 4. Handoff / off-ramp (Configure → Conversation handoff)
- Set **online vs offline** behavior separately so off-hours leads still get captured (ticket + contact form).
- Triggers: (a) Lyro lacks the answer (automatic), (b) visitor asks for a human, (c) any specs/cert/price/
  lead-time question (route by policy). Capture email/phone **at the handoff point** so the lead lands even
  with no agent online. This is the "confidence off-ramp to a specialist" made concrete.

### 5. Analytics / baseline (the attribution wedge)
- Instrument from day one: **resolution rate, handoff rate, leads captured, Suggestions volume.** These are
  the baseline that later proves "net-new revenue attributable to the chatbot channel." Vendor case studies
  cite up to ~85% automation — treat as a ceiling, measure the real number.

---

## What is explicitly NOT in scope now (the extensible 20%, each its own later decision)
- **Lyro Actions** for live CRM/inventory lookups mid-chat (needs a safe tested integration; irreversible-write
  caution).
- **Audiences tab** per-persona knowledge/guidance scoping (start with one tag + one guidance; split only if
  the data shows OEM vs molder need genuinely different answers).
- **Per-grade cert answers** (blocked on the UL yellow-card source from Todd).
- **Full per-grade datasheet KB** via the IDES `I=73811` crawl.
- **SEM/Unbounce page-specific onramps** (Phase 1.4).

## Cost discipline (matches the pre-revenue rule)
- Lyro is billed **per conversation, not per message**, and quota-metered (Free/Starter = 50; overage
  ~$39/50). A public site can burn the quota fast → **route low-intent/non-qualified traffic to Flows**, spend
  Lyro conversations on real Q&A. Confirm the plan's quota + file-import tier **in-account** (already waiting
  on the Tidio support review).

## Config as a versioned artifact (why this is extensible, not click-only)
Keep the SSOT in the repo so config is reproducible and diff-able, not trapped in the Tidio UI:
```
runtime/recoil/generated/prl-lyro/
  guidance-prompt.md          # §2 verbatim, versioned
  kb-manifest.md              # what's loaded, what's held out + why (the guardrail ledger)
  qualifying-flow.md          # the OEM/molder branch + capture fields + webhook contract
  handoff-policy.md           # online/offline + escalation triggers
```
Adding a capability = add a file + a KB source, not a rebuild. That is the "extensible" test.

---

## Research basis (verify hard numbers in-account before quoting Todd)
Sourced pass over Tidio/Lyro docs (2025–2026). Ambiguous/unverified, flagged: exact language count (docs say
45/47/48), Guidance character limit (undocumented), per-plan Lyro quotas above Starter (undocumented),
file-import tier (cited as Plus). Native guardrail (answer-from-KB + auto-forward) is the well-sourced,
load-bearing fact. Full reference retained in session; key sources: help.tidio.com Data-sources / Lyro
Guidance / flows-Lyro-agents / Lyro Actions, tidio.com/blog/lyro-ai-training, chatimize Tidio review.
