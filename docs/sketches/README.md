# Cross-Harness Idea & Sketch Ledger (Claude Code / Hermes / ARCS v9)
**Created:** September 13, 2026
**Security/Quarantine:** Internal R&D / Staging Ledger

## Purpose
A persistent staging ledger inside `arcs-v9` for raw architectural sketches, cross-harness handoffs (Claude Code, Hermes, Cursor), and design specs before committing to production runtime.

---

## 1. Codebase Ground Truth
- **Architecture:** Single Next.js 16 App Router application at root (`src/app/`, `src/lib/`, `src/proxy.ts`).
- **Policy:** Zero new dependencies without explicit approval; no monorepo/pnpm wrapping.
- **Routing:** Subdomain proxying for `good.arcs.care` and `*.arcs.care` lives in `src/proxy.ts`.

---

## 2. Zero-Telemetry Public Good & Token-Diff Architecture
- **Concept:** Client-side Consonance-Burstiness-Symmetry (CBS) evaluation running at `good.arcs.care/tools/anti-slop`.
- **Constraint:** Zero outbound telemetry sockets. In-memory execution in browser RAM.
- **Enterprise Shadow:** Commercial API key route (`/api/v1/scan`) checking quotas via `src/lib/ammo-gate.ts`.
- **Token Efficiency:** Multi-agent choreography passing JSON delta-patches rather than full documents, avoiding O(N^2) context explosion.

---

## 3. Inbound Signal: The Respark Engine (`pollinate`)
- **Origin:** NFTT #2 ("The week my own memory tried to make me lie to a friend").
- **Core Loop:** Returning counterparts' authentic, timestamped lines with zero-ask provenance.
- **Surface Target:** `src/app/tools/pollinate/page.tsx` routed via `src/proxy.ts`.

---

## 4. Harness Handoff Protocol
When picking up tasks from this ledger in Claude Code or Hermes:
1. Verify target repository topology against `package.json` before proposing tooling changes.
2. Respect the "no new dependencies without asking" standing rule.
3. Keep public utility tools client-side; keep stateful/monetized audits in `src/lib/`.
