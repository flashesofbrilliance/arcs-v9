# Handoff — Zero-Trust & Orchestration session — 2026-07-19

> Standalone handoff (NOT appended to CLAUDE.md this time — a concurrent session was
> restructuring the handoff chain; writing to the hot shared file would clobber it, which
> is the exact J5/serializability pathogen this session hardened against). Fold into
> CLAUDE.md as `## Handoff — v3.8.0` once that refactor settles.

## What shipped (all committed + pushed to main, deployed READY)

### Public surfaces
- **`/state-of-union.html`** (app.arcs.care) — roadmap zones → patent pressure-test →
  evals/falsifiability + funding → L0–L7 archaeology cross-section. + Vercel analytics.
- **`status.arcs.care`** — same four movements folded in as sections 08–11 (su- namespaced),
  plus a **Live Pulse** (commit/deploy/PRs/count) and full analytics.
- **`chan.arcs.care`** — Live Pulse only, **sanitized** (J1: shows telemetry shape, never
  raw commit/PR text — no internal roadmap on a prospect page). Patent/eval sections
  deliberately excluded (sensitive).
- **`GET /api/pulse`** — cached (ISR, `revalidate=300`), CORS-open GitHub telemetry.
  Verified `x-vercel-cache: HIT` — GitHub hit ~once/5min regardless of traffic. Set
  `GITHUB_TOKEN` in Vercel to drop to 60s.

### Correction (important)
- The Yellow/White papers are **internal drafts, NOT published** — the in-doc "Public
  Release / CC BY 4.0" header is aspirational. Both live pages' patent alarms were
  reframed: no publication occurred, but the papers sit in a **public repo** → a §102
  public-accessibility question for counsel, not a settled deadline.

### Orchestration + doctrine
- **`_PATTERNS/jtbd-orchestration-map.md`** — model-delegation policy (Haiku/Sonnet/Opus by
  effort × **trust-of-input** × blast-radius, risk-calibrated), per-job dependency graphs,
  budgets, least-privilege rule, OSS verdict, and the J-backlog.
- **`.claude/workflows/recoil-report.mjs`** — the recoil-report as a real fan-out, hardened:
  risk-calibrated models, scoped gather agents, untrusted-data wrapping, **Skeptic Sentinel**
  (pre + post, 3 modes incl. false-premise/wolf), J7 verify cap, J10 preflight.
- **`.claude/agents/`** — `recoil-reason` (`tools: Read` — J8; NOTE: `tools: []` was found to mean
  *inherit all tools*, so it's scoped to Read, not empty. True zero-tools is a residual), `recoil-gather-git` (shell, no net),
  `recoil-gather-web` (fetch one URL, no shell).
- **OSS vetting** → keep `/ultrareview` + `/dual-bar-raiser` bespoke; adopted
  `anthropics/claude-code-security-review` as a CI scan (`.github/workflows/security.yml`,
  fork-guarded, needs `ANTHROPIC_API_KEY` in GH Secrets).

### ADRs / patterns
- **ADR-032 — Zero-Trust Posture (GOVERNING).** 10 principles + conformance checklist every
  ADR must pass. Key: never-trust/always-verify; least-privilege; egress-is-a-control
  (read-only ≠ exfil-proof); trust-of-input drives tier (risk-calibrated, not blanket);
  verify provenance not just plausibility; **crypto/ZK proves identity/provenance, never
  intent** (P10); anti-fragile immune ledger. Operational patterns: Skeptic Sentinel,
  Dual-Control Handshake, step-up auth roadmap (**decided: magic-link primary, TOTP optional,
  WebAuthn/passkey/YubiKey/Face-Touch-ID endgame**).
- **ADR-031 — Secrets inventory + rotation** (5 secrets, 2 stores; overdue: Supabase pw, Resend key).
- **`_PATTERNS/public-repo-exposure-audit.md`** (J2) — ~18 named-person dossiers + papers in a
  public repo; options A(private repo)/B(split)/C(scrub); **remediation is a human call.**
- **`_PATTERNS/workflow-cost-ledger.md`** (J4) — seeded + recoil-report run outcome recorded.

## Recoil-report validation run (`wf_31635888-3f6`) — watchdog-stopped
Ran ~60 min on the **pre-tightening broad-permission** script; stopped mid-verify by the
stop-rule watchdog. Salvage: gather 5/5 (only **2 productive** — granola+git) → profile ✓ →
4 lenses (31 claims) → verify **48/93**, **refuted 43** (~90% — skeptic working exactly as
designed on thin input) → synthesis **never reached**. Three lessons became J7/J8/J10 (done).
> ⚠ PROVENANCE (claims-skeptic, 2026-07-19): these run numbers are **journal-sourced and NOT
> independently reproducible** — the raw run journal (`wf_31635888-3f6`) lived in a transient path,
> not the repo. They survive only across this handoff + snapshot + ledger, which *mutually cite each
> other* — document agreement is not proof. Treat as unconfirmed until a journal is produced.
Data-bleed finding: on the broad script the CURATOR lens read *other people's* dossiers into
Chan's report — the exact risk the tightening now closes.

## Backlog (see jtbd-orchestration-map §8c)
- Done this session: J1, J2(audit), J4, J6, J7, J8, J10.
- **Open:** J3 (falsifiability harness, gated 100 receipts), J5→J14 (serializability/yoav),
  J11 (`/ultrareview` enforces ADR-032 checklist), J12 (Sentinel→pathogen_log), J13
  (dual-control in code), J15 (Sonnet-first-pass verify), J16 (per-subject consented input
  allowlist for multi-artifact recoil).

## Human actions pending (no session can do these)
1. **J2 decision** — make the repo private, or split sensitive out (named dossiers + papers). Sharpest edge: the forensic dossiers.
2. `GITHUB_TOKEN` → Vercel env (tightens /api/pulse to 60s).
3. `ANTHROPIC_API_KEY` → GitHub Actions Secrets (so security.yml runs) + "require approval for outside collaborators."
4. Rotate the overdue Supabase DB password + stale Resend MCP key (ADR-031).
5. Branch-protection on `main` (the trigger half of J14 serializability).

## Post-handoff commits (continued past the first handoff — see J17, this is the drift it fixes)
- `fdcdf31` J7/J8/J10 hardening + this handoff · `0f2e3c8` init-state-sync + **J17 Fork Lineage**
  (rebrand snapshot → provenance record; make sync a mandatory `/handoff` step 0) ·
  `30c7e4f` pulse foot shows honest **"data as of"** generation time, not the client clock.
- Live-pulse recency: status/chan are ISR-cached ~5 min (rate-limit safety without a token);
  the foot now exposes that. Drop `revalidate` 300→60 once `GITHUB_TOKEN` is set (pending action #2).

## Key commits
`30c7e4f` pulse-timestamp · `0f2e3c8` state-sync + J17 · `fdcdf31` J7/J8/J10 · `e44fe02` ledger ·
`7abac40` ADR-032 + hardened workflow · `392ca41` least-privilege · `f9290a0` ATG J1/J2/J4/J6 ·
`2038fa4` papers-correction + pulse + analytics · `936e1dc`/`1f4b548` /api/pulse.

## Next session starts at
Pick from J11 (self-enforcing doctrine), J13 (dual-control), or J14 (serializability — read
`arcs_yoav_store.py` first). Re-run recoil-report ONLY after confirming MCP connectivity
(J10). NOTE (J8 resolved): `tools: []` was found to mean *inherit all tools*; `recoil-reason` is
now `tools: Read` (an explicit list is honored). True zero-tools remains a residual.
