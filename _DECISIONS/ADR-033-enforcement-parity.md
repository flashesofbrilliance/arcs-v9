# ADR-033 — Enforcement Parity: Internal Invariants Get the Same Gates as Client Artifacts

> **Status:** DECIDED
> **Date:** 2026-07-16
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Should an audit finding be considered closed when it is documented, or only when a mechanism (test / CI rule / runtime guard) or a dated waiver exists — and should CI enforce that distinction?

---

## E — Entity / System

The governance loop itself: `_PATTERNS/` audits, `_DECISIONS/` ADRs, `_CANON/trust-contract.md` claims, and the CI pipeline. Secondarily every future contributor (human or agent), whose "done" definition this changes.

---

## W — Window

**Horizon:** YEARS
**Revisit trigger:** The ledger gate produces sustained false-pressure (findings waived repeatedly because SLAs are unrealistic), or the repo gains a real issue tracker that subsumes the ledger.

---

## Context

The 2026-07-16 meta-cognitive review confirmed a pattern the corpus had already caught twice (prose-rule enforcement audit 2026-06-23; RECOIL-PROTOCOL): audits produce beautifully documented findings that terminate in `_PATTERNS/` files with no enforcement mechanism. Exhibit A: "inline styles only" was violated at `layout.tsx` from the first commit; found 2026-06-23; fixed 2026-07-11; still has no lint rule preventing recurrence. Meanwhile client-facing artifacts get hard gates (Fanatics redaction scans, bar-raiser review). Stated preference (rigor, receipts, honest confidence) and revealed preference (prose without teeth internally) diverge at exactly this seam — the cobbler's-kids problem, named.

The blindspot is structural, not motivational: the end state of an audit was defined as "a document exists." Nothing aged open findings, so lack of domain expertise ("I didn't know deletion paths are table stakes") became invisible.

---

## Options Considered

### Option A — Keep discipline-based closure (status quo)
- Findings tracked in prose, closed by attention and memory.
- Pros: zero overhead.
- Cons: demonstrated failure mode, three separate times.

### Option B — Ledger + CI delinquency gate + scheduled heartbeat
- `_PATTERNS/ledger.json`: every finding exits via `test | ci | guard | waiver`; `open` entries age against severity SLAs (high 30d / medium 60d / low 90d); waivers require reason + expiry. `scripts/ledger_check.py` is a hard CI gate; a monthly scheduled workflow re-runs it and opens a GitHub issue, so quiet months can't silently age findings.
- Pros: closes the loop mechanically; makes unknown-unknowns someone-must-act items the moment they're filed; waivers keep it honest without blocking legitimate deferrals.
- Cons: one more file to maintain; SLA pressure could incentivize cosmetic waivers.

### Option C — Full external issue tracker (GitHub Issues/Projects as sole system)
- Pros: standard tooling.
- Cons: prior Projects board went stale within weeks; issues lack a machine-checkable "mechanism or waiver" field; nothing gates CI.

---

## Decision

**Chosen:** Option B.

**Rationale:** The repeated failure is documentation-terminates-the-loop. Only a machine that fails the build restores parity between internal invariants and client-artifact gates. The ledger is deliberately boring — JSON + stdlib Python + one CI step — because the reinvented-wheel audit finding applies to governance machinery too.

**Trade-offs accepted:** Waiver abuse is possible; the monthly governance issue makes waiver churn visible rather than preventing it. SLAs are initial guesses, tunable in `ledger.json` without touching code.

Companion role definitions ship with this ADR: `.claude/agents/{ciso-review, privacy-review, sre-review, claims-skeptic}.md` — specialized reviewers whose charters require citing evidence and routing out-of-scope findings **into the ledger**, so subagent reviews feed the same loop instead of generating new unenforced prose.

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Strongest case against: this is governance machinery for a solo project — process theater that a disciplined TODO list would match, and the SLAs will just generate waiver noise. Response: the disciplined-list approach is the tested-and-failed status quo (three documented instances); the gate costs one JSON file and ~80 lines of Python, and if it degenerates into waiver noise, that noise is itself the signal the revisit trigger fires on.

---

## Consequences

- "Done" for any audit finding now means: mechanism or dated waiver, in the ledger.
- Seeded with 12 findings from the 2026-07-16 review; RL-001 (compass rate limit), DEL-003 (deletion endpoint), DEP-008 (Dependabot) closed with mechanisms in the same commit; TC-004, YG-005, LINT-006, OBS-007, GW-002, BK-010, PL-011 open with SLAs running; ROT-009, ORPH-012 waived to 2026-08-15 (blocked on Zach).
- New decisions created: choose the durable rate-limit layer (GW-002 — Vercel AI Gateway evaluation), pick the exception tracker (OBS-007).

**Implementation pointer:** `_PATTERNS/ledger.json`, `scripts/ledger_check.py`, `.github/workflows/ci.yml` (Ledger delinquency check step), `.github/workflows/governance.yml`, `.claude/agents/*.md`.

---

## Linked receipts / ADRs

- ADR-032 — anonymous receipt remediation (the disclosed defect TC-004 exists to prevent recurring)
- ADR-014 — arcs-care CI/CD governance (same circuit-breaker philosophy, applied here to governance itself)
- `_PATTERNS/2026-06-23-prose-rule-enforcement-audit.md` (the evidence base)
