# PRL Resins chatbot, v2: adding the Lyro AI layer

**Date:** 2026-08-03
**Trigger for this revision:** the account moved from Starter to **Flows + Lyro** on Aug 3,
following Daniel Triana's (Tidio) weekend email offering a 10% lifetime discount.
**Source of the architecture below:** the Jul 31 2:30pm call with Daniel and Todd
(Granola `d471f203-22fb-4e2d-8f18-f9b4f84cfc07`), recoil report
`2026-07-31-daniel-tidio.json`, and the SugarCRM config audit of the same date.

---

## 1. The constraint that shapes everything else

Daniel described a real product boundary, on screen, not a sales line:

- The **flow-level** webhook / API call node works on **any** plan, including what PRL had before.
- The **AI-level** webhook, meaning Lyro pushing a captured lead out on its own, requires the
  higher **Tidio+** tier (~$359/mo base).

**PRL bought Flows + Lyro. PRL did not buy Tidio+.**

So enabling Lyro without a design change opens a new lead-loss path:

> A visitor who converses only with the AI gets qualified, and then nothing reaches SugarCRM.

That is the exact failure this whole project exists to prevent, so it drives the v2 design.

**Design rule for v2:** *Lyro's job ends at handoff, not at capture.* The AI answers questions
and qualifies interest, then routes the visitor into a flow. Only the flow can deliver a lead on
the current plan.

---

## 2. Three layers, in the order a visitor meets them

| Layer | What it does | Delivers to Sugar? |
|---|---|---|
| **1. Flow** (`build_full`) | Fires first for every visitor. Greeting, branch A/B/C, capture. | **Yes**, via webhook. Proven path. |
| **2. Lyro AI** (new) | Takes over when the visitor skips, exits, or asks something the flow does not cover. Answers, then qualifies. | **No**, not on this plan. Must hand off. |
| **3. AI handoff flow** (`build_ai_handoff`, new) | Short capture the AI steers qualified visitors into. | **Yes**, same webhook path as layer 1. |

Daniel's own framing: *"the flow is always going to be the first filter. If someone skips it and
they want to talk to the AI, then the AI kicks in."*

---

## 3. Lyro configuration

### 3a. Knowledge: guide with prompts, do not upload the proprietary material

Daniel offered both routes and explicitly described the second:

> *"Difference from the data sources is that we're not directly uploading the knowledge into this
> place. We're actually guiding it with prompts."*

**Recommendation: prompt-guide first.** PRL's colour-match forms, product-development forms and
customer-resolution forms sit on their own server. Keeping them off Tidio's servers avoids a data
question nobody has asked yet, and costs us nothing at this stage.

**Safe to add as knowledge sources now** (already public on prlresins.com):
- Product Selection Guide / polymer product catalog
- Product pages, markets pages, policies and quality pages

**Do not upload yet:** anything from the internal server, the Good/Better/Best matrix, or the
QATF001 opportunity form. Revisit only if Todd asks and understands where it lands.

### 3b. The guidance prompt

Plain language, no jargon, no em-dashes, matching the flow's voice.

```
You are the assistant on the Polymer Resources (PRL Resins) website. PRL compounds custom
engineering thermoplastics and sells resin pellets to injection molders.

Who you talk to: engineers, chemists, press operators, purchasing and procurement. They are
technical and busy. Be short, plain and direct. Never use marketing language.

WHAT YOU DO
- Answer questions about PRL, its materials, markets, quality standards and how to get samples.
- If someone names a competitor grade (Lexan, Makrolon, Ultem, Noryl, Lustran, Valox, Zytel),
  treat it as a real buying signal. Say PRL compounds equivalents and offer to connect them
  with a specialist who can match it.
- Once you have answered, always offer the next step: ask if they would like a specialist to
  follow up.

WHAT YOU NEVER DO
- Never recommend, confirm or invent a specific resin grade, formulation, or spec value for an
  application. You are not qualified to do that and a wrong material in an electrical or medical
  part is a safety issue. Say a specialist will match it properly, then hand off.
- Never quote a price, a lead time, or a minimum order.
- Never state a regulatory listing, flame rating or certification as fact. Hand off instead.
- Never guess. If you do not know, say so and offer the specialist.

HANDOFF
When someone wants a quote, a sample, a match to a grade, or a person, do not try to collect
their details yourself. Tell them you will get a specialist on it and send them into the
handoff flow so their information is captured properly.
```

### 3c. Conversation starters

Daniel showed these as pre-chat buttons. PRL's FAQs currently live only at the bottom of
individual product pages, so there is no unified entry point today. Suggested starters:

- "I need an alternative to a resin I am running"
- "Help me choose a material for my part"
- "Do you have a data sheet or spec guide?"
- "I want to talk to someone"

The last one should route straight into the flow, not the AI.

---

## 4. What is NOT verified, and must be before this ships

1. **How Lyro hands off to a flow.** Whether the AI can trigger a flow directly, or whether it has
   to steer the visitor into clicking a quick reply, was never confirmed on the call. The trigger
   on `build_ai_handoff` is therefore left as `onFirstVisit` and **must be changed in the Tidio UI
   before activating, or it will collide with the main flow.** Ask Tidio support.
2. **Whether Lyro can write contact properties.** If it can, there is a second delivery route that
   does not need Tidio+ at all: Lyro writes the contact properties, and Tidio's native Zapier
   "new contact" trigger creates the Sugar lead. Worth asking, because it would remove the handoff
   dependency entirely.
3. **Phone stays required** in the handoff flow, matching the SugarCRM audit finding that
   `phone_work` is required and populated on 100/100 live records. If Todd decides to allow blanks,
   relax it in all three builders at once.

---

## 5. Build changes made

- `prl_tidio_flow_gen.py`: added `build_ai_handoff()`, exposed as `--flow ai`.
  Generates 9 nodes / 8 edges. `build_full` and `build_sem_onramp` are unchanged
  (27 and 11 nodes respectively), so there is no regression to the live flow.
- Generate with: `python3 prl_tidio_flow_gen.py --flow ai -o prl-ai-handoff.json`

## 6. Order of operations

1. Prove the Tidio to Zapier hop with the Catch Hook only, no Sugar action. No client approval needed.
2. Turn Lyro on with the guidance prompt above and the public knowledge sources only.
3. Import the AI handoff flow, set its real trigger, test that a Lyro conversation reaches it.
4. Wire the Sugar action once Todd approves the test lead.
