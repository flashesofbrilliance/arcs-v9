# PRL Chatbot — SEM Triggers + Product Picker v1

Two build additions: (1) URL-scoped triggers so PPC landing pages open with the right greeting,
and (2) a Branch A product picker built from PRL's own /products/ taxonomy.

## Part 1 — SEM / Unbounce URL-scoped triggers

**Prerequisite:** the Tidio JS snippet must be added in Unbounce (Script Manager → add to the
landing pages), because Unbounce is not covered by the WordPress plugin.

### How Tidio does URL targeting
A Flow trigger fires on page view; a **Condition** node checks the page URL. Pattern per page:
`Trigger: Visitor views a page` → `Condition: Page URL contains "<slug>"` → `Bot message: <page
greeting>` → drop into the matching branch with the product/competitor pre-filled.

### Page → greeting map

| URL contains | Opening line (voice-tuned) | Then |
|---|---|---|
| `sabic-alternatives` | "Looking to move off a SABIC grade? Tell me which one, Lexan, Ultem, Noryl, or Valox, and I'll match it to a PRL equivalent and get you to a specialist fast." | Branch A · pre-tag `competitor: SABIC` |
| `lexan` / `makrolon` / `calibre` | "Need a Lexan-class polycarbonate? We compound PC grades to match. Which grade or spec are you running?" | Branch A · family PC |
| `ultem` | "Looking for an Ultem-class PEI? Tell me the grade or the spec you need." | Branch A · family PEI |
| `noryl` | "Need a Noryl-class PPE? Let's match it. What grade or spec?" | Branch A · family PPX |
| `valox` | "Replacing a Valox PBT? Tell me the grade or the requirement." | Branch A · family PBT |
| any `gad_source` present (fallback) | "Thanks for coming in. Tell me the resin, spec, or the material you're replacing and I'll get you to the right person fast." | greeting + branch buttons |

Build the specific-competitor triggers first (highest intent), then the generic `gad_source`
fallback so every paid-search visitor gets a fast, relevant open. Each SEM open should still keep
the "Just have someone call me" option (no phone trees).

## Part 2 — Branch A product picker (from /products/)

Instead of only free text, offer PRL's actual product menu as quick replies. It matches the site,
reduces typos, and lets the bot deep-link the exact product page and tag the family cleanly.

### PRL product taxonomy (from the /products/ index)
Base resins: **PC** (Polycarbonate) · **ABS** · **ASA** · **PEI** (Ultem-class) · **PPX**
(Noryl-class PPE) · **Nylon 6** · **Nylon 66** · **PBT**
Blends: **PC/ABS** · **PC/ASA** · **PC/PBT**
Processes / capabilities: **Structural Foam** · **Profile Extrusion**

### Picker flow (Branch A step 1, replacing the open free-text ask)
Bot: "Great. Pick the family you need, or just type it."
Decision buttons (Tidio caps buttons per node, so group):
- **Polycarbonate (PC)** → set `desired_resin_or_spec=PC`, link `/pc-resin`
- **PC blend (ABS / ASA / PBT)** → sub-decision: PC/ABS · PC/ASA · PC/PBT
- **ABS or ASA** → sub-decision: ABS · ASA
- **Nylon (6 or 66)** → sub-decision: Nylon 6 · Nylon 66
- **PBT** → `/pbt-resin`
- **PEI (Ultem-class)** → `/pei-resin`
- **PPX (Noryl-class)** → `/ppx-resin`
- **Not sure, help me choose** → jump to Branch B
- **Type it instead** → free text → `desired_resin_or_spec`

After a pick: "Good choice. Here's the page on that grade family: [link]. Are you replacing a
resin you run now?" → continue Branch A (current_resin, application, requirements) → capture.

### Product page links (confirm live permalinks before shipping)
Sandbox slugs (parent = products): `pc-resin`, `abs-resin-by-polymer-resources`, `pc-abs-resin`,
`pc-asa-resin`, `pcpolyester-resin` (PC/PBT), `nylon-6-resin-...`, `nylon-66-resin-...`,
`pbt-resin`, `pei-resin`, `ppx-resin`, `structural-foam`, `profile-extrusion`.
Verify the live URL shape (`/products/<slug>/` vs `/<slug>/`) on prlresins.com before wiring the
deep links, since the picker sends visitors to real pages.

## Attributes to add for these
`competitor` (SABIC / Lexan / Ultem / etc.) · `product_family` (PC / ABS / Nylon / ...) — both
optional, both help the rep triage. Keep the existing set from the build sheet.

_Version: v1 · 2026-07-30 · sources: /products/ index taxonomy + Product Selection Guide
competitor cross-reference + branch-logic map v1.3. Pairs with the voice script v1._
