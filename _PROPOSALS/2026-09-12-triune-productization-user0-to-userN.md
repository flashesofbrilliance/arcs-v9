# Proposal: Triune Productization & Extensibility Architecture (User0 → UserN)
**Document ID:** `PROP-2026-09-12-USERN-EXTENSIBILITY-001`  
**Status:** DRAFT / FOR CONVERGENCE REVIEW  
**Parties:** Claude Code (Architect/Compiler) · Hermes Agent (Operator/Actuator) · Perplexity (Sensor/Scout) · Zach Harris (Principal/User0)  
**Parent Anchors:** `_STATE/convergence.json`, `_SPECS/self-serve-atlas-scan-v1.md`, `_STATE/handoff-2026-09-11-cross-harness-pickup.md`

---

## 1. Executive Summary & Core Motivation

We have established a working, high-throughput resume forge and career intelligence engine inside `arcs-v9`. However, this capability is currently **locked to $User_0$ (Zach Harris)**:
- Paths, seeds, and priors are hardcoded in local scratch trees.
- Capabilities are split across disjoint repos (`arcs-v9`, `resume-tailor-skill`, `arcs-skills`, `hermes-agent`).
- Multiple AI harnesses (Claude Code, Hermes, Perplexity) operate without a unified protocol for how an external user ($User_N$) drops in data and receives an honesty-graded product surface.

This proposal establishes a **decoupled, multi-tenant architecture** where:
1. **The Skill & Falsifier Engine (`flashesofbrilliance/resume-tailor-skill`)** becomes the portable, harness-agnostic core for any user ($User_N$).
2. **Hermes Agent (`flashesofbrilliance/hermes-agent`)** acts as the sovereign, air-gapped local runtime (extracting sensitive LinkedIn exports locally with zero PII cloud leakage).
3. **Claude Code** acts as the high-altitude architectural gatekeeper and code compiler.
4. **Perplexity** serves as the live sensory organ, harvesting untainted exterior hiring signals, JD ground truth, and company trajectory.
5. **ARCS Web (`resume-tailor.arcs.care` via `arcs-v9`)** serves as the standalone client presentation surface (MUI-driven PWA + interactive claim auditor + print-perfect PDF generator).

---

## 2. Decoupled Topological Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. SENSORY INTAKE & MARKET TRUTH (Perplexity)                              │
│    - Scrapes raw JD text, decodes hiring manager signals, team pain points. │
│    - Delivers structured research dossiers into `_INBOX/evidence/`.         │
│    - Validates company viability (avoids ghost jobs & hollow reqs).         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Raw Opportunity Vector (JD + Context)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. CANONICAL FALSIFIER & COMPETENCY SSOT (`resume-tailor-skill`)            │
│    - Inputs: User's portable LinkedIn ZIP (`Positions.csv`, etc.) + JD.     │
│    - Stage 1: Build `competency-model.json` (Hard/Soft/Tacit taxonomy).      │
│    - Stage 2: Adversarial Falsifier pass (refuse what evidence can't defend).│
│    - Stage 3: Lead-with-strengths projection & depth-ladder ordering.        │
│    - Dual packaging: Claude Code plugin + Hermes native skill.              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Honesty-Graded Competency Payload
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. AIR-GAPPED LOCAL RUNTIME (Hermes Agent & Local OT)                       │
│    - Sandboxed extraction of user exports; sensitive PII never leaves host. │
│    - Executes headless Chrome PDF compilation (`--print-to-pdf`).           │
│    - Runs automated QC checks: seed-identity leak sweep, wrap-lint, ATS txt.│
│    - Stamps proof-of-life to `_STATE/pulse.json`.                           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Rendered Artifacts & Decision Receipt
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. PRESENTATION & TENANT ATLAS (`arcs-v9` / `resume-tailor.arcs.care`)      │
│    - Standalone PWA shell (`public/resume-tailor-pwa.html`).                 │
│    - Heuristic Three-Theme Engine (Formal / Neutral / Casual).               │
│    - Interactive evidence auditor: click any claim to view verified source.  │
│    - Supabase RLS row-scoped persistence (UserN data isolation).            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Harness Roles & Responsibilities

| Harness | Primary Domain | Sovereign Actions | Boundaries / Invariants |
|---|---|---|---|
| **Perplexity** | Sensory / Exterior | Market reconnaissance, live posting retrieval, company trajectory analysis, decider identification. | Writes to `_INBOX/evidence/` only. Never modifies repo code or ADRs. |
| **Claude Code** | Cognitive / Interior | System architecture, schema contracts, PR creation, ADR resolution, worktree & collision pruning. | Operates on git branches. Never writes ungrounded claims or skips receipt logging. |
| **Hermes Agent** | Physical / Actuator | Local file extraction (ZIP/CSV), headless rendering, terminal script execution, desktop inspection, pulse/oracle beat keeping. | Local-first. Never leaks raw PII outside localhost sandbox. |

---

## 4. Workstreams & Concrete Implementation Milestones

### Phase 1: Engine Portability & Packaging (`resume-tailor-skill`)
- [ ] Audit `flashesofbrilliance/resume-tailor-skill` to ensure **zero $User_0$ hardcoded strings** in template files.
- [ ] Add dual-manifest support: keep `.claude-plugin/plugin.json` and add Hermes `skill.yaml` / `SKILL.md` frontmatter metadata.
- [ ] Symlink/register the skill into Hermes profile (`~/.hermes/profiles/arcs/skills/resume-tailor`).
- [ ] Verify both CLIs can invoke the same skill:
  - Claude: `/plugin install resume-tailor@arcs`
  - Hermes: native skill view / invocation.

### Phase 2: Presentation & Surface Promotion (`arcs-v9`)
- [ ] Run the local smoke test on `public/resume-tailor-pwa.html` (`feat/resume-pwa-theming`) per `resume-tailor-pwa-next-session` skill.
- [ ] Strip legacy PWA service-worker hooks from static `public/resume.html` so personal resume remains clean and decoupled.
- [ ] Promote `resume-tailor.arcs.care` via Vercel domain routing to serve the general-purpose PWA shell.

### Phase 3: Triune Feedback & Receipt Grounding
- [ ] Standardize the Perplexity input schema (`_INBOX/evidence/role-dossier-schema.json`) to feed directly into `target-role-scan.json` and `resume-tailor-skill`.
- [ ] Ensure all resume builds log a standardized `decision_receipt` on Supabase verifying what claims were confirmed vs. unconfirmed.

---

## 5. Review Prompts for Parallel Sessions

To present this proposal to Claude Code and Perplexity without context loss, use the review prompts below.

### Prompt for Claude Code (Architect Session)
```markdown
# ARCHITECT REVIEW: Triune Productization & Extensibility Proposal (User0 -> UserN)

Hermes has drafted an architectural proposal to decouple ARCS resume-tailoring and career intelligence from User0 (Zach Harris) into a portable, multi-tenant instrument (UserN):
- Proposal doc: `_PROPOSALS/2026-09-12-triune-productization-user0-to-userN.md`
- Shared convergence anchor: `_STATE/convergence.json`

Please review this proposal from an architectural, type-contract, and repo-organization perspective:
1. Does the boundary between `flashesofbrilliance/resume-tailor-skill` (canonical skill core), `flashesofbrilliance/hermes-agent` (local execution engine), and `arcs-v9` (presentation/PWA) respect our atomic design principles and avoid CANON_COLLISION?
2. Does the job-search lane (PR #393 / `bridge-scan.json`) cleanly integrate as the intake pipeline for this decoupled model?
3. What failure modes, security boundaries (PII air-gapping), or contract gaps need to be hardened before we merge and promote `resume-tailor.arcs.care`?

Please record your verdict and feedback into `_STATE/convergence.json` or your session handoff.
```

### Prompt for Perplexity (Scout Session)
```markdown
# SCOUT REVIEW: Market Reconnaissance & Evidence Pipeline (Triune Productization)

ARCS is establishing a formal intake pipeline between Perplexity (Scout), Hermes (Local Actuator), and Claude Code (Architect):
- Proposal doc: `_PROPOSALS/2026-09-12-triune-productization-user0-to-userN.md`

We are standardizing how external market intelligence lands in `_INBOX/evidence/` to feed the honesty-graded `resume-tailor` engine:
1. What are the highest-fidelity data fields an external reconnaissance pass can provide for a target job posting (e.g. unlisted tech stack, hiring manager public commentary, recent team departures, funding runway, verified salary bands)?
2. How should an external scout packet format company risk/ruin signals so the ARCS adversarial gauntlet (Loki/BAR) can evaluate whether an opportunity is attainable vs. a trap?
3. Review the proposed `_INBOX/evidence/` intake role to ensure it aligns with optimal Perplexity MCP querying and synthesis capabilities.
```
