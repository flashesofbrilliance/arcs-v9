# Front-End Design Queue — Monetization-Ready Backends v1.0.0

**Epoch:** 2026-07-13 · **Evidence:** meta-audit parity matrix (code-verified), Granola revenue record, Surface Map service decomposition, fire-test census.
**Ranking law:** backend readiness × proven demand ÷ design lift. NOTOMATION note: this ranks; the Hard Fork receipt (audit #06) still decides where design investment concentrates.

## The queue

| # | Product | Backend state (verified) | Front end needed | Why this rank |
|---|---|---|---|---|
| **1** | **Artifact Publisher** — the call-brief / recoil-report factory | Revenue-proven wedge: 13 live subdomains, `runtime/recoil/generated/*.json` → `/recoil/[id]` pipeline, 13 ui-kit atoms, parameterized template, password gates, Lead model + `/admin/leads` | (a) Operator console: transcript/params in → live preview (existing atoms) → publish to `<name>.arcs.care`; (b) thin client portal (a client's artifact index) | The only asset with **paying demand today** ($5–20K sprints; briefs compound testimony). Every sale currently costs hours of hand-assembly in a Claude session — the front end converts a consultancy into a product. Chi-aligned; KKL window OPEN. = Surface Map S3/A3+A5. |
| **2** | **Decision/Profile Scan storefront** | Scanner suite READY since May (stdlib Python, 750 real events tested: calendar/reader/listening/network/forensic/archetype) + `ScanSignal`/`ScanFeedback` models + `/scan` page embryo + **`ProfileScan` screen already in the document kit** | Upload/consent flow → scan run → **fidelity-earned reveal** of the ProfileScan document → share/export | Cleanest self-serve wedge ($99–499 one-time): backend tested, renderer exists, missing only the front door. Fits BOTH fork branches (sprint pre-work artifact-led; self-serve product-led). Payment rail: invoice-first pilot until Stripe unblocks. |
| **3** | **Debrief / Atlas** — the retention surface | Outcome route live (`api/receipts/[id]/outcome`), debrief page embryo, T+N cron scaffolding, ADR-026 reminder plumbing | Polished debrief moment + **Atlas view** (`/history` as terrain, not list — the missing organism from the Surface Map) + outcome nudge surfaces | This is what makes $300/seat *recurring*: outcomes → calibration over time is the moat. Monetizes audit move #03; unlocks F8 (ax4 finally testable). No new backend needed. |
| **4** | **Corpus Audit as a service** (the meta-audit, white-labeled) | Methodology proven end-to-end this week on ARCS itself; deliverables = the five explorers (`_ARTIFACTS/`, self-contained); recoil + gauntlet + lattice scripts in repo | Parameterization (render-svc A3): client corpus in → branded lattice/orbital/roadmap out; engagement one-pager | Enterprise/consulting price point with artifacts as proof-of-craft. Needs the cross-compiler before it scales — rank 4 because design lift is real. |

## Explicitly NOT ready (do not design front ends yet)

- **Operators / sage service** — 17.4K LOC, mounted, zero callers, **no eval harness**. You cannot sell what you haven't benchmarked (audit #04 gates this; LAB's strongest objection stands).
- **Observatory** — substrate gated at 100 receipts; demo-class until then.
- **Compass paywall / Stripe rails** — held RED until the Hard Fork receipt (#06). Note ranks 1 and 4 monetize via invoices (services) and do not violate the hold; rank 2 pilots invoice-first.

## Fork honesty

Ranks 1+4 are artifact-led; ranks 2+3 are product-led. This queue deliberately gives each fork branch its best candidate — it does not resolve the fork. File the receipt (#06) before concentrating design spend past rank 1.

## Sequencing

Rank 1 can start immediately (all parts exist; the design is assembly). Rank 2 needs one consent/privacy pass (scanners touch personal data — sovereignty L2 export ships with it). Rank 3 rides audit move #03. Rank 4 waits on A1–A3 (tokens.json → manifests → render-svc).
