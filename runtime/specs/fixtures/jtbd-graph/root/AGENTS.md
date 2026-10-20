<!-- intent:begin -->
## Intent
- **Why:** The canonical ARCS monorepo (Zach, 2026-10-03): the product (compass, DEWY receipts, Y-gate), every arcs.care surface, the operator suite, the session/handoff machinery, and the private content folded in from dormant repos (`runtime/specs/field-os/`, `runtime/memory-export/`, each with an IMPORTED-FROM.md).
- **Done looks like:** See WORLD.md and the backlog in `_QUEUE/induced-backlog.jsonl`; this repo has no single done-state.
- **Not this:** Not one repo for everything: distributable packages with their own registry or marketplace identity (germinate, rosetta-shell, arcs-skills and its plugins) keep their own public repos. Handoff state lives in CLAUDE.md; intent lives here.
- **Status:** live (serves arcs.care, app.arcs.care and ~95 other aliases)
- **Last verified:** 2026-10-03 (Vercel `get_deployment("arcs.care")` returned project `arcs-v9`, READY at `165855f`)
- **Spec:** none at root (engineering specs live in `runtime/specs/`)
<!-- intent:end -->

<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

Loaded together with CLAUDE.md and WORLD.md (CLAUDE.md imports this file; no back-import, to avoid a cycle).

---

# ARCS v9 — Agent & DevOps Handbook

> Read WORLD.md first. It is not documentation — it is the physics of the world you're building in.

---

## What this repo is

**`github.com/flashesofbrilliance/arcs-v9`** — canonical ARCS v9 decision intelligence app.
Stack: Next.js 16 · Prisma 7 + SQLite (dev) / Supabase (prod) · Auth.js v5 · Anthropic SDK.
No Tailwind (removed 2026-07-11; it was an unused Day-1 scaffold remnant). Inline styles only in components (per WORLD.md); the sole stylesheet is `src/app/globals.css` (reset + keyframes + font tokens — things inline styles cannot express).

---

## Environment variables

| Var | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API for compass, jobs and other routes. Model per job lives ONLY in `src/lib/claude-models.ts` (`MODELS.<role>`; Python reads it via `scripts/arcs_models.py`). `model_id_gate.py` (pre-commit) blocks hardcoded ids; `model_drift_check.py` flags newer models at session start |
| `AUTH_SECRET` | Auth.js v5 session signing |
| `AUTH_RESEND_KEY` | Magic link emails via Resend |
| `DATABASE_URL` | Postgres/Supabase (prod only; SQLite used automatically in dev) |
| `RECOIL_PASSWORD` | **Retired.** Was a shared cookie gate for `/recoil*`; removed (it sat disclosed in git history). `/recoil` is now gated per-route by Auth.js session + `ADMIN_EMAILS` (`src/lib/admin.ts`), fail-closed. No code reads this var. |
| `ADMIN_EMAILS` | Comma-separated admin allowlist — interim RBAC for the internal `/recoil` index + reports (`src/lib/admin.ts`). Prod fail-closed if unset; dev passes through |
| `RECRUITHAUS_AMMO_PASSWORD` | Shared passcode for the gated recruiter ammo tier at `recruithaus.arcs.care/ammo` (`src/lib/ammo-gate.ts` + `src/proxy.ts` + `/api/recruithaus/unlock`). Fail-closed if unset; cookie holds a SHA-256 token, never the passcode |

---

## Routes & handlers

| Route | File | Purpose |
|---|---|---|
| `POST /api/compass` | `src/app/api/compass/route.ts` | **Core.** L0–L5 Claude pipeline → DEWY receipt + Y-gate |
| `POST /api/prep` | `src/app/api/prep/route.ts` | Create PrepSession (stakes/horizon/protecting/confidence) |
| `GET /api/brief/[id]` | `src/app/api/brief/[receiptId]/route.ts` | Cartography brief generation |
| `GET /api/guide/[id]` | `src/app/api/guide/[receiptId]/route.ts` | Step-by-step guide surface |
| `GET /api/history` | `src/app/api/history/route.ts` | Receipt history for user |
| Auth | `src/app/api/auth/[...nextauth]/route.ts` | Auth.js v5 magic link |

---
