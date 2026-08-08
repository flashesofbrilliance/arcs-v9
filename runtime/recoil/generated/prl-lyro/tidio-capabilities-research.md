# Tidio Capabilities Research (Audiences, Qualification, Dual-Experience, A/B, Lyro Knowledge, Integrations, Plan Gating)

> Reference file grounding the PRL Resins chatbot architecture against Tidio's own documentation.
> No date is asserted here; check git history for when this was compiled. Every claim carries a
> source URL and a confidence tag: [confirmed] = stated in Tidio's own docs; [likely] = strongly
> implied by Tidio docs or corroborated across third-party reviews but not verbatim in a single doc;
> [unverified] = could not confirm in Tidio's own docs.
>
> Note on method: `help.tidio.com` returns HTTP 403 to direct fetches, so the doc content below was
> retrieved through search-engine summaries of those same doc pages plus Tidio's marketing/pricing
> pages. Where a settings path or number could not be read verbatim off the live page, it is tagged
> [likely] or [unverified] rather than stated as fact. Re-verify anything load-bearing directly in the
> account UI before making live changes.

---

## 1. Audiences / Segmentation

**Answer.** Tidio "Audiences" are named visitor segments defined by conditions, and they are the
primary mechanism for making Lyro behave differently for different visitor groups. Crucially,
Audiences plug into three distinct parts of Lyro: **data sources, handoff, and Guidance.** That means
all three of the sub-questions resolve to the same feature.

- **Create an audience:** `Lyro AI Agent > Knowledge > Audiences` tab. Two buttons top-right:
  **Manage knowledge** and **Add audience**. "Add audience" opens the audience creator: name it and
  set conditions. [likely - path assembled from doc summaries]
- **Audience conditions/parameters:** visitor country, email address, communication channel (live
  chat, Instagram, WhatsApp), and any **custom Contact Properties** already defined in the project.
  [confirmed]
- **Knowledge/data sources scoped per audience - YES.** The data-sources list has an **Audience**
  column; the default target audience is "everyone." You can "decide which portions of Lyro's
  knowledge will be used for particular target audiences," and also decide whether Lyro should
  immediately transfer a given audience to live agents. [confirmed]
- **Guidance per audience - YES, not strictly global.** Lyro Guidance (the persona + rules layer:
  communication style, handoff/escalation rules, custom directions) "can be targeted at different
  audiences." So Guidance is NOT strictly account-global; it can be audience-scoped. [confirmed]
- **Flows targeted by audience/attributes - via Conditions, not an "Audience" picker on the trigger.**
  Flows branch using **Condition** nodes and trigger conditions (chat status, browser, current page,
  visitor properties). Flows do not natively select a Lyro "Audience" object; instead you replicate
  segmentation inside the flow with Condition nodes reading Contact Properties/tags. [likely]

**Settings paths.**
- Audiences: `Lyro AI Agent > Knowledge > Audiences`.
- Data-source audience scoping: `Lyro AI Agent > Knowledge > Data Sources` (Audience column).
- Contact Properties (the raw material for audience conditions): `Settings > Tags and properties >
  Contact properties`. [confirmed]

**Sources.**
- Data sources - Lyro's knowledge base: https://help.tidio.com/hc/en-us/articles/14543666652316-Data-sources-Lyro-s-knowledge-base
- Lyro Guidance: https://help.tidio.com/hc/en-us/articles/20810956911004-Lyro-Guidance
- Lyro - the conversational AI agent: https://help.tidio.com/hc/en-us/articles/9003475527196-Lyro-the-conversational-AI-agent
- Contact Properties: https://help.tidio.com/hc/en-us/articles/5444927889052-Contact-Properties
- Flow editor: Conditions: https://help.tidio.com/hc/en-us/articles/5453789640476-Conditions

**Confidence:** [confirmed] that Audiences scope data sources, handoff, and Guidance; [likely] on the
exact tab path and on the Flow-side "no native audience picker, use Conditions" characterization.

---

## 2. Qualification In-Session

**Answer.** Yes, a chat can score/segment a visitor mid-conversation, primarily inside **Flows**:

- **Set data mid-conversation:** the **Update Contact Property** action writes/updates a contact
  property; **Add a tag** action attaches a customer tag; both take effect within the running flow.
  Multiple properties can be set in one action via **+ Update another Contact Property**. [confirmed]
- **Branch on it:** **Condition** nodes read visitor criteria (properties, page, browser, chat
  status) and route the flow down different paths. So the pattern "ask questions -> set a property/tag
  -> Condition-branch on it" is natively supported. [confirmed]
- **Lyro reading those attributes:** this is the key limit. Contact Properties/tags set by a flow do
  feed **Audiences**, and Audiences drive Lyro's data sources, Guidance, and handoff. So Lyro "acts
  on" the segmentation **indirectly, at the audience level** (which knowledge/persona/handoff applies)
  rather than by reading an arbitrary attribute inside a single generated reply. There is no
  documented mechanism for Lyro to consume a specific property value as a runtime variable in its
  answer. [likely]
- **Handoff conditions:** Lyro handoff behavior (when it lacks knowledge, or the visitor asks for a
  human) is configurable separately for online vs offline hours, and can be set per audience.
  [confirmed]

**Settings paths.** Flow actions: `Flows > (your flow) > Actions` (Update Contact Property, Add a
tag, Remove a tag). Conditions: within the same flow editor. Lyro handoff: `Lyro AI Agent`
handoff/Guidance settings, audience-scoped.

**Sources.**
- Flow editor: Actions: https://help.tidio.com/hc/en-us/articles/5453966368412-Actions
- Flow editor: Conditions: https://help.tidio.com/hc/en-us/articles/5453789640476-Conditions
- Data sources - Lyro's knowledge base (audience -> data sources/handoff): https://help.tidio.com/hc/en-us/articles/14543666652316-Data-sources-Lyro-s-knowledge-base
- Lyro Guidance: https://help.tidio.com/hc/en-us/articles/20810956911004-Lyro-Guidance

**Confidence:** [confirmed] flows can set property/tag and branch; [likely] on the precise ceiling of
what Lyro itself can read (audience-level yes, arbitrary per-reply variable not documented).

---

## 3. Concurrent Dual-Experience (qualified -> specialist vs unqualified -> AI self-serve)

**Answer.** Partially, and the cleanest supported form routes at the **Audience + handoff** layer,
not by running two independent Lyro "brains."

- Lyro's knowledge, Guidance, and handoff are all audience-scopable (Q1), so you CAN make one Tidio
  account behave as two experiences: define a "qualified" audience whose handoff = "immediately
  transfer to live agents / specialist," and an "unqualified/default" audience that stays on Lyro
  self-serve with the general knowledge set. [confirmed that the audience-level levers exist]
- What you cannot do: nest a Lyro node inside a Flow, or run two genuinely separate Lyro
  configurations simultaneously as isolated bots. The order is always **Flows -> Lyro -> Human**,
  sequential, never nested (confirmed by Tidio support in prior handoff; consistent with the "how
  flows, Lyro, and live agents work together" doc). Lyro's "brain" is one engine; you shape it per
  audience, you do not fork it. [confirmed / prior support confirmation]

**Cleanest supported implementation:**
1. A qualification Flow (button/attribute-triggered so it coexists with Lyro) sets a Contact
   Property/tag, e.g. `qualified = true`.
2. That property is the condition for a "Qualified prospects" Audience.
3. For that Audience, set handoff to route immediately to a specialist (live agent), and/or scope a
   different Guidance persona and knowledge subset.
4. The default audience ("everyone") keeps Lyro self-serve.

This is "two experiences by segment on one account," but realized as **one Lyro configured per
audience + a routing flow**, not two concurrent isolated bots. [likely - this is the supported
approximation, assembled from the audience docs]

**Sources.**
- Data sources - Lyro's knowledge base: https://help.tidio.com/hc/en-us/articles/14543666652316-Data-sources-Lyro-s-knowledge-base
- Lyro Guidance: https://help.tidio.com/hc/en-us/articles/20810956911004-Lyro-Guidance
- How do flows, Lyro, and live agents work together?: https://help.tidio.com/hc/en-us/articles/14667264947356-How-do-flows-Lyro-and-live-agents-work-together (page returns 403 to fetch; title/existence confirmed via search index)

**Confidence:** [confirmed] the audience-level levers exist and Flows/Lyro/Human are sequential;
[likely] that the audience+handoff pattern is the intended "closest supported" way to run dual
experiences.

---

## 4. A/B Testing

**Answer.** No clearly documented **native A/B test / traffic-split node for Flows or Lyro configs**
was found in Tidio's own help docs. Third-party reviews assert Tidio "supports A/B testing," but the
concrete, doc-backed capability is limited to A/B testing of **proactive messages**, plus the ability
to preview/test a flow before publishing. There is no found doc describing a percentage traffic
splitter that sends 50/50 of visitors down variant A vs B of a flow.

- **Supported workaround:** approximate a split using **Condition** nodes on a pseudo-random or
  rotating attribute, or split by an existing segment dimension (page, source, audience) and compare
  flow completion analytics. Tidio does expose per-flow completion/drop-off analytics to compare
  variants. [likely for the workaround; the analytics are confirmed]
- **Limits:** no native random bucketing, no built-in statistical significance, and separating
  variant traffic cleanly requires you to engineer the split condition yourself.

**Sources.**
- (Third-party, NOT Tidio docs) FlowHunt "Which AI Chatbot Platforms Support A/B Testing": https://www.flowhunt.io/faq/ai-chatbot-platforms-ab-testing/
- (Tidio blog, general) Chatbot testing guide: https://www.tidio.com/blog/chatbot-testing/
- Native A/B flow/Lyro traffic-split doc: **not found in docs.**

**Confidence:** [unverified] for native flow/Lyro A/B splitting (not found in official docs);
[likely] for the Condition-node workaround.

---

## 5. Lyro Knowledge Control (disable vs delete, Lyro vs Copilot scope, answer-vs-handoff)

**Answer.**

- **Disable vs delete:** you can **deactivate** an individual Q&A/data source without deleting it by
  toggling off the blue toggle next to the **Used by** column. Deleting is a separate, permanent
  removal. Toggling off is the reversible option. [confirmed]
- **Immediate effect:** docs describe the toggle as the live on/off control for whether Lyro/Copilot
  may use that knowledge; treated as effective for subsequent conversations. Exact propagation
  latency is not stated verbatim. [likely]
- **Scope a source to human agents (Copilot) only, not customer-facing Lyro:** YES. The **Used by**
  column shows **Lyro** and **Copilot** tags per Q&A pair. You can toggle a source on for Copilot
  while leaving it off for Lyro (and vice versa), so a source can be human-agent-only. [confirmed]
- **Answer-from-knowledge vs handoff:** Lyro answers from its data sources when it has the knowledge;
  when it **lacks the required knowledge** or the **visitor requests a live agent**, it enters
  handoff. Handoff behavior is configurable separately for **online vs offline** hours, and per
  audience. Docs frame this as a knowledge/confidence gate ("lacks the required knowledge to
  respond") rather than exposing a numeric confidence threshold to the admin. [confirmed for the
  trigger conditions; the internal confidence number is not admin-exposed]
- **Improvisation control:** AI improvisations can be disabled in `Lyro AI Agent > Configure` (Copilot
  tab, "Sources of suggestions"). [likely]

**Settings paths.** `Lyro AI Agent > Knowledge > Data Sources` (Used by column + toggle);
`Lyro AI Agent > Configure` for improvisation/handoff behavior.

**Sources.**
- Data sources - Lyro's knowledge base: https://help.tidio.com/hc/en-us/articles/14543666652316-Data-sources-Lyro-s-knowledge-base
- Copilot: https://help.tidio.com/hc/en-us/articles/15126324714012-Copilot
- Lyro - the conversational AI agent: https://help.tidio.com/hc/en-us/articles/9003475527196-Lyro-the-conversational-AI-agent

**Confidence:** [confirmed] disable-via-toggle, Lyro/Copilot per-source scoping, and the two handoff
triggers; [likely] on immediate-propagation and the exact Configure path.

---

## 6. Integrations + Limits

### 6a. Tidio -> Zapier / external webhook
- **Send to Zapier action:** a Flow **Action** node "Send to Zapier" pushes collected data to Zapier.
  [confirmed]
- **Zapier trigger side:** Zapier exposes a Tidio trigger such as **"Contact Sent From Bot"**, which
  can drive a "Custom Request" in Webhooks by Zapier. [confirmed]
- **Native HTTP POST / API call node:** Flows also have a dedicated **"Making an API call (HTTP
  request)"** action that can send data to (and receive data from) external systems mid-flow. This is
  the more general native way to POST JSON to a Zapier Catch Hook without the Zapier-branded action.
  [confirmed the node exists]
- **Plan gating for the HTTP/API-call node:** not confirmed in docs which plan/add-on unlocks it.
  Advanced flow nodes are commonly gated above Starter; treat as **[unverified]** and confirm in the
  live builder for the PRO account.

Sources:
- Flow editor: Actions (Send to Zapier): https://help.tidio.com/hc/en-us/articles/5453966368412-Actions
- Flows: Making an API call (HTTP request): https://help.tidio.com/hc/en-us/articles/16747427756188-Flows-Making-an-API-call-HTTP-request
- Tidio Webhooks (structure): https://developers.tidio.com/docs/webhooks-structure

### 6b. Tidio -> SugarCRM
- **No native Tidio<->SugarCRM integration found.** The supported path is **via Zapier** (Tidio
  action/trigger -> Zapier -> SugarCRM). This matches the account plan (Zapier in the middle for
  retry + task history). [confirmed no native integration found; Zapier path confirmed]

Sources:
- Zapier Tidio + SugarCRM listings: https://zapier.com/apps/gravity-forms/integrations/sugarcrm7/463/send-new-gravity-forms-leads-to-sugarcrm and https://zapier.com/apps/tidio (Tidio app on Zapier)
- Native Tidio-SugarCRM connector: **not found in docs.**

### 6c. ZoomInfo
- **No native Tidio<->ZoomInfo integration found.** As expected, any ZoomInfo tie-in would run
  through Zapier or a CRM writeback, not a Tidio-native connector. [confirmed absence; nothing found]

### 6d. WordPress / Gravity Forms
- **Tidio WP plugin** (`tidio-live-chat`) primarily installs the widget on WordPress. No documented
  form-to-Tidio or identity bridge beyond widget install was found; Gravity Forms -> Tidio is done
  **via Zapier**, not the plugin. Note Gravity Forms can also talk to SugarCRM directly through
  dedicated third-party GF<->Sugar plugins (separate from Tidio). [confirmed for widget-install scope;
  no extra plugin capability found]

Sources:
- Tidio WordPress plugin: https://wordpress.org/plugins/tidio-live-chat/
- Tidio + Gravity Forms via Zapier: https://zapier.com/apps/tidio/integrations/gravity-forms

### 6e. Lyro cost model
- **What counts as a Lyro conversation:** any time a customer interacts with Lyro and gets **at least
  one AI-generated reply**. Returning to the same chat later, or Lyro sending multiple replies, still
  counts as **one** conversation. [confirmed]
- **Separate quotas:** Lyro conversations, human "billable" conversations, and Flow triggers are three
  **separate** quotas billed in parallel. [confirmed]
- **Free allowance:** every project gets a **non-renewable 50** Lyro conversations free; when
  exhausted, Lyro stops and that free quota does not reset. [confirmed]
- **Paid Lyro add-on:** quota **resets monthly** on the purchase date; add-on tiers commonly cited
  around **$39/mo for 100** Lyro conversations, scaling up (e.g. 500-1,000 chats ~ $79-$149/mo).
  Exact current tier prices [likely - third-party pricing pages, verify on Tidio pricing].
- **Overage behavior / capping:** Tidio's mechanism is **auto-upgrade to a higher tier at ~95% of
  quota** (in-app banner, no email warning) rather than per-unit overage. If **auto-upgrade is
  disabled**, service **stops at 100%** until reset or manual upgrade. So the way to CAP spend is to
  **disable auto-upgrade** and accept a hard stop, not to set a spend ceiling. [likely - corroborated
  across multiple third-party pricing reviews; confirm the exact auto-upgrade toggle in the account]

Sources:
- The Lyro AI agent limit: https://help.tidio.com/hc/en-us/articles/13924459295900-The-Lyro-AI-agent-limit
- The monthly conversations limit: https://help.tidio.com/hc/en-us/articles/11874534946460-The-monthly-conversations-limit
- Tidio pricing: https://www.tidio.com/pricing/
- (Third-party) myAskAI Tidio limits 2026: https://myaskai.com/blog/tidio-ai-complete-guide-2026
- (Third-party) auto-upgrade/overage behavior: https://chatarmin.com/en/blog/tidio-pricing and https://www.quantumdesk.com/blog/tidio-pricing

**Confidence:** [confirmed] Lyro-conversation definition, separate quotas, free-50; [likely] on exact
add-on prices and the auto-upgrade/no-overage capping mechanism (third-party corroborated).

---

## 7. Plan Gating Summary

Tidio's current plan lineup (2026): **Free, Starter (~$29/mo), Growth (~$59/mo), Plus (~$749/mo)**,
plus a separately purchased **Lyro AI add-on** and Flows. The mapping below is best-effort from docs +
pricing pages; treat plan cells as [likely] unless marked otherwise, and confirm against the account's
own plan screen (the account shows a **PRO** badge, which maps to a paid tier but the exact modern
tier name should be verified in-app).

| Capability | Plan / add-on (best read) | Confidence |
|---|---|---|
| Live chat widget + basic Flows | Free / Starter+ | [likely] |
| Flows: Conditions, Update Contact Property, Add/Remove tag | Included where Flows are available (Starter+/Growth) | [likely] |
| Flows: **API call (HTTP request) node** | Higher tier / advanced flows (not confirmed) | [unverified] |
| Flows: **Send to Zapier** action | Where Flows available | [likely] |
| **Lyro AI agent** (answering, knowledge, handoff) | Lyro AI add-on (50 free, then paid tiers) | [confirmed add-on model] |
| **Audiences** (scoping data sources / Guidance / handoff) | Part of Lyro AI agent | [likely] |
| **Lyro Guidance** (persona/rules, audience-targeted) | Part of Lyro AI agent | [likely] |
| **Copilot** (agent-assist, per-source scoping) | Lyro/Copilot feature set | [likely] |
| **Simple Actions** (in-Lyro logic) | Legacy, plan-gated (per prior support confirmation) | [confirmed legacy/gated] |
| Native A/B traffic split | Not offered natively | [unverified / not found] |
| Zapier connection (Catch Hook, SugarCRM actions) | Zapier-side, not Tidio-plan-gated | [confirmed] |

**Sources.** Tidio pricing: https://www.tidio.com/pricing/ ; Tidio features: https://www.tidio.com/features/ ; Lyro AI agent limit: https://help.tidio.com/hc/en-us/articles/13924459295900-The-Lyro-AI-agent-limit ; Lyro Simple Actions: https://help.tidio.com/hc/en-us/articles/12642003268764-Lyro-Simple-Actions

---

## Design implications for PRL

### (i) Qualified-vs-unqualified routing to two experiences
Implement as **one Lyro configured per Audience + a qualification Flow**, not two bots:
1. Build a **button/attribute-triggered** qualification Flow (button-triggered so it coexists with
   Lyro; a "Visitor Says" input-triggered flow would conflict). Ask 2-3 qualifying questions.
2. Use **Update Contact Property** / **Add a tag** to stamp the outcome (e.g. `qualified=true`,
   `segment=specialist`).
3. Define a **"Qualified" Audience** conditioned on that property. For that Audience: set **handoff =
   transfer to live agent/specialist** (optionally a tighter Guidance persona + a narrower knowledge
   subset).
4. Leave the **default ("everyone") Audience** on Lyro self-serve.
This yields concurrent segment-routed experiences on one account within the confirmed
Flows -> Lyro -> Human, audience-scoped model. It is NOT two isolated Lyro brains.

### (ii) Never-state-a-spec Lyro
Lyro cannot be given a hard "never output a numeric spec" guarantee purely via prompt, so combine:
- **Knowledge control:** keep any spec/datasheet PDFs **off Lyro** (toggle their **Used by** to
  Copilot-only, or exclude from Lyro data sources), so human agents can reference specs via Copilot
  but Lyro has no spec numbers to quote. This is the strongest lever (source-level, confirmed).
- **Guidance rules:** add audience-scoped Guidance directions instructing Lyro to route spec requests
  to a human / capture the request rather than answer, and set **handoff** to trigger on spec-type
  questions where possible.
- Treat this as **defense in depth (knowledge exclusion + Guidance + handoff)**, not a single toggle.
  A residual risk remains that Lyro paraphrases spec-adjacent text from allowed sources; keep
  spec-bearing documents out of Lyro entirely to minimize it.

### (iii) Flow -> Zapier -> Sugar delivery
- Use the Flow **"Send to Zapier"** action **or** the native **API call (HTTP request)** node to POST
  the captured lead JSON to a **Zapier Catch Hook**; Zapier -> SugarCRM **Create Record** (Leads,
  full state names, status "New", assign Bill Galla, details into `description`, email into email1).
- Keep **Zapier in the middle** (retry + visible task history); confirmed there is no native
  Tidio<->Sugar path and Sugar cloud REST is OAuth2-only, so a bare flow node cannot authenticate to
  Sugar directly.
- **Before building:** verify in the PRO account whether the **API call (HTTP request)** node is
  available on the current plan (plan gating [unverified]); if not, fall back to the **Send to
  Zapier** action.
- Recall the account constraint from the config audit: `phone_work` is **required** in Sugar Leads, so
  the Zap or the flow must supply a phone value (or a placeholder) or Create Record will fail.

---

## Gaps / could not verify
1. **Plan gating of the Flows "API call (HTTP request)" node** - which Tidio plan/add-on unlocks it.
   Not found in docs. Verify in the live PRO builder. [unverified]
2. **Native A/B / traffic-split for flows or Lyro** - no official Tidio doc found describing a
   random-bucketing splitter; third-party claims exist but are not doc-backed. [unverified]
3. **Exact modern plan names/prices** mapped to the account's **"PRO"** badge - Tidio's public tiers
   read as Free/Starter/Growth/Plus; "PRO" may be a legacy label. Confirm on the account's plan page.
4. **Immediate propagation latency** of toggling a data source off - docs imply live effect but do not
   state timing. [likely, not confirmed]
5. **Whether Lyro can read a specific Contact Property value as a runtime variable** inside a single
   generated reply (beyond audience-level scoping). Not documented; assume audience-level only. [likely]
6. **Exact Audiences tab navigation path** and the Configure/improvisation path - assembled from doc
   summaries because `help.tidio.com` blocked direct fetch (403). Confirm labels in-app.
7. **Copilot Chrome extension vs in-app Copilot** scope differences - not fully explored; not needed
   for the routing/spec/delivery decisions above.

---
## Live-doc verification (2026-08-08, via the built-in browser)

IMPORTANT ACCESS NOTE: help.tidio.com is readable ONLY via the built-in Browser pane
(mcp__Claude_Browser__ + preview_start). It 403s WebFetch and is ExtensionsSettings-policy-blocked for the
claude-in-chrome extension. Use the built-in browser pane to read Tidio docs.

CONFIRMED against the live Lyro - AI Agent section (help.tidio.com/hc/en-us/sections/12154776323612):
- **Audience-scoped data sources is a real, documented feature.** The "Data sources - Lyro's knowledge base"
  article (/articles/14543666652316) has a dedicated section: **"How to use custom audiences for data
  sources."** This is the master lever for the qualified-vs-unqualified dual experience. [CONFIRMED]
- Data-source management lives under **Lyro AI Agent > Knowledge > Data sources**; add via Website URL / Add
  manually / CSV-PDF import / Zendesk / webstore sync; three-dot menu deletes a Q&A pair or website. [CONFIRMED]
- Bulk data-source upload/export via **OpenAPI requires the Plus package**. [CONFIRMED]
- The Lyro section documents these design-relevant articles (verify specifics in-app before live changes):
  Lyro Guidance, Lyro Actions, **Lyro Simple Actions (legacy)**, Lyro Proactive roles, The Lyro AI agent limit,
  Data sources, Copilot. URLs: guidance/actions/limit are under /hc/en-us/articles/ in that section.
- Key article URLs: Data sources /articles/14543666652316 ; AI agent limit /articles/13924459295900 ;
  conversational agent /articles/9003475527196.

STILL TO VERIFY IN-APP (labels/plan-gating): the per-source "Used by" Copilot-only toggle exact control; whether
Guidance is audience-targetable in THIS account's UI; the Flow "API call (HTTP request)" node availability on
this plan; the "PRO" badge -> current tier mapping.

## Lyro Tasks + quota model (CONFIRMED via The-Lyro-AI-agent-limit article, 2026-08-08)

**Lyro Tasks = flows built INSIDE Lyro's config** that "never interrupt Lyro's current conversation - they
become a part of it." They do everything regular flows do. This is the current, non-legacy way to put
flow-logic inside Lyro (the "Simple Actions (legacy)" article now redirects to the help home - deprecated, as
support implied; successor is Tasks/Smart-Actions). [CONFIRMED]

**Quota - the big levers:**
- 1 Lyro conversation = the FIRST time Lyro responds in a new thread. Multiple replies in one thread = still 1.
  A thread closes after 15 min inactivity; a new visitor message then starts a new (counted) thread. [CONFIRMED]
- **Immediate handoff costs ZERO quota** - "nothing will be deducted if Lyro immediately performs handoff
  (e.g. transfers to a live agent)." So the qualified -> route-to-specialist path is quota-free. [CONFIRMED]
- **Lyro Tasks use NEITHER the flows quota NOR the Lyro quota.** Quota-free structured behavior inside Lyro.
  [CONFIRMED]
- Free Lyro = 50 non-renewable conversations. Paid packages 50 to 1,000/mo; more via Plus/custom. [CONFIRMED]

**Design implications (big):**
- The **unqualified/answer** experience can do its lead-capture + qualification as a **Lyro Task** (quota-free)
  INSIDE the Lyro conversation - one coherent thread, no jarring flow<->Lyro switch, and it does not burn the
  Lyro conversation quota beyond the single conversation count. This is a cleaner "consistent experience" than
  a separate flow handing to Lyro.
- The **qualified/route** experience should **hand off immediately** -> zero quota cost, hot lead to a human.
- Net: cost exposure is much lower than feared. The expensive case is only a genuine multi-turn Lyro Q&A that
  does not hand off; capture-as-Task and route-as-handoff are both effectively free.
- Revisit "Lyro Tasks" as the primary capture mechanism for the Lyro-led experience (vs the onFirstVisit flow).
