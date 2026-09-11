# Pickup — resume.PWA.theming (2026-08-28)

Paste as first message in fresh thread. Self-contained.

## What this is

Resume PWA theming branch. Two phases: PWA shell (done) + themed MUI polish (unstarted, spec only — see `docs/resume-tailor-theming-engine-spec.md`).

Tonight: PII strip + WIREFRAME removal + sticky-header removal, deployed to prod. Then a proxy.ts bug surfaced (SW file caught by wildcard rewrite → resume.arcs.care rendered black), fixed, deployed, then hit Vercel Security Checkpoint (dashboard action needed, not code).

## What landed (committed + deployed)

| Commit | What |
|---|---|
| `b2144d9e` | PWA install affordance wired into resume.html (HEAD at session start) |
| `ab7c73f8` | proxy.ts: static-assets allowlist so SW/manifest/icons bypass wildcard rewrite (`fix(resume): let subdomain static assets bypass wildcard rewrite`) |
| `976bfa50` | resume.html: restore render — add back `selectedNode`/`selectedClient` state to `Resume()` that PWA-install refactor dropped; swap React dev builds → `production.min.js` (`fix(resume): restore render`) |
| `bff8b050` | deploy guardrails: `scripts/deploy-smoke.mjs` (browser render gate — fails if page mounts blank/black) + `DEPLOY.md` (production = main only, no --prod from dirty/feature trees, run gate before promote, rollback recipe) (`chore(deploy): add render smoke-gate + DEPLOY.md guardrails`) |

All 4 on `feat/resume-pwa-theming`, pushed to origin (branch matches remote — nothing to push).

## What's on disk right now

- `public/resume.html` — 47,259 bytes, PII clean (grep WIREFRAME/BUILDING AT THE EDGE/Fairfield/203-/zach.harris@gmail.com/headerH/headerRef = 0 matches), only linkedin + github URLs in contact line, header not sticky (no position:fixed/zIndex:50/ResizeObserver/headerH/spacer)
- `public/manifest.json` — 25 lines, standalone display, maskable icons, `/?source=pwa` start URL
- `public/resume-sw.js` — 2,068 bytes, cache-first shell (HTML/fonts/icons), network-first for `/_vercel/*` analytics
- `public/resume-icon-192.png` — 1,759 bytes
- `public/resume-icon-512.png` — 5,823 bytes
- `src/proxy.ts` — proxy.ts patched with `staticAssets` allowlist (resume-sw.js, manifest.json, resume-icon-192/512.png)
- `scripts/deploy-smoke.mjs` — render smoke gate (new)
- `DEPLOY.md` — deploy guardrails doc (new, 60 lines)

## Production state

- `app.arcs.care/resume.html` — ✅ correct: PII stripped, WIREFRAME gone, header not sticky, title `Zach Harris — Resume`, SW serves as `application/javascript` (confirmed via 15 consecutive polls after deploy)
- `resume.arcs.care` — ⚠️ Vercel Security Checkpoint (spinner page, "We're verifying your browser") — triggered after proxy.ts deploy. This is a dashboard action (Website owner fix link or domain re-validation), NOT a code bug. The code fix is correct and deployed.

## Uncommitted (do NOT commit as-is — many are from other workstreams)

See `git status --short` for full list. The ones that matter for THIS branch:

- `docs/resume-tailor-theming-engine-spec.md` — MUI theme spec (SPECCED only, not implemented). Reference for next phase.
- `docs/frontend-theming-curated-bases.md` — curated color bases for theming.
- `docs/mui-theme-reference-memo.md` — MUI theme reference memo.
- `public/mui-smoke.html` — MUI smoke test page (unstarted the MUI embedding exploration).
- `docs/task4-grounded-recommendations.md` — modified (don't know scope).
- `docs/decision-memo-creative-tim-template-audit.md` — unrelated decision memo.
- `docs/audit-service-hosting-scope.md` — Python audit service hosting scoping doc (272 lines, options A-E). Separate thread — user hasn't chosen an option yet.
- `operators/audit_service/*` — audit service codebase (multiple modified + new files). Separate thread.
- `src/lib/audit-translator.ts` — modified (audit translator, separate thread).

The uncommitted audit files (audit_service/, audit-translator.ts, audit-service-hosting-scope.md) belong to a DIFFERENT workstream — don't fold them into resume.PWA.theming commits.

## Next session — first move

If continuing resume.PWA.theming:
1. `git status` — confirm state matches above.
2. Decide on `resume.arcs.care` checkpoint: clear it from Vercel dashboard, or wait it out. `app.arcs.care` is fine regardless.
3. Verify the page renders on both subdomains: curl title + SW content-type on `resume.arcs.care` (once checkpoint clears) and `app.arcs.care`.
4. Then the theming phase: read `docs/resume-tailor-theming-engine-spec.md` → MUI embedded via unpkg/esm into `public/resume.html` → three themes (formal/casual/neutral) + inference hook + ThemeProvider.

If switching to audit service hosting:
1. Read `docs/audit-service-hosting-scope.md` (272 lines, options A-E, cold-start numbers, recommendation draft).
2. Pick an option (A/B/D/E). That's a separate session/thread.

## Skills created this session

Two new skills under `~/.hermes/profiles/arcs/skills/`:

1. **`vercel-subdomain-wildcard-routing`** — proxy.ts pattern for subdomain→static HTML on Vercel (Next.js 16, NOT middleware.ts). Covers the wildcard rewrite, the service-worker trap (SW file rewritten to HTML → black page, no console errors, diagnose via curl content-type), the static-assets allowlist fix, clinic flow, and the real 2026-08-28 incident.
2. **`vercel-security-checkpoint-triage`** — Vercel Security Checkpoint page diagnosis: what it is (automated browser-verification gate, NOT a code bug), how to recognize it (title = "Vercel Security Checkpoint", Astro `data-astro-cid-` attrs, 17-language obfuscated JS), why it triggers (deploys, new subdomains, suspicious request patterns), the three clear paths (wait, dashboard fix link, domain re-validation), and what NOT to do (don't deploy again, don't curl-bypass, don't debug page code while checkpoint is active).

Both load with `skill_view(name='...')` before working on Vercel subdomain routing or checkpoint triage.

## File status

| File | Status | Notes |
|------|--------|-------|
| `public/resume.html` | ✅ committed (bff8b050) | PII stripped, WIREFRAME gone, header not sticky, render restored |
| `src/proxy.ts` | ✅ committed (ab7c73f8) | staticAssets allowlist added |
| `scripts/deploy-smoke.mjs` | ✅ committed (bff8b050) | render smoke gate |
| `DEPLOY.md` | ✅ committed (bff8b050) | deploy guardrails |
| `docs/resume-tailor-theming-engine-spec.md` | ❌ uncommitted | MUI theme spec, SPECCED only |
| `docs/audit-service-hosting-scope.md` | ❌ uncommitted | Python audit hosting scoping (separate thread) |
| `operators/audit_service/*` | ❌ uncommitted | audit service codebase (separate thread) |
| `src/lib/audit-translator.ts` | ❌ uncommitted | audit translator (separate thread) |
| `docs/frontend-theming-curated-bases.md` | ❌ uncommitted | theming color bases |
| `docs/mui-theme-reference-memo.md` | ❌ uncommitted | MUI reference memo |
| `public/mui-smoke.html` | ❌ uncommitted | MUI smoke test |
| `docs/task4-grounded-recommendations.md` | ❌ uncommitted | modified, scope unclear |
| `docs/decision-memo-creative-tim-template-audit.md` | ❌ uncommitted | unrelated decision memo |
| `_STATE/*.md`, `_PATTERNS/*.md`, `apply-scott-loop.sh`, `ship-scott-loop-v2.sh` | ❌ uncommitted | other workstream artifacts — do not fold into this branch |

## Reading sequence

1. **Substrate** — `CLAUDE.md` ROM primitives, trust contract, NOTOMATION. `WORLD.md` — if not read this session, any reference is inferential (verify before treating as canon).
2. **Structural map** — `AGENTS.md` operator table (lines 139–163), 34 files, 16.6K LOC, four-layer layering. ADR system count + canon vs provisional status.
3. **Components** — read in order: PWA spec (`docs/resume-tailor-theming-engine-spec.md`) → proxy.ts → resume.html → DEPLOY.md → deploy-smoke.mjs. Don't read all operators — read the ones relevant to the question.
4. **Synthesis** — what was built/discovered/corrected, what's still open, what inferences are still unverified (flag these, don't present as verified).

## Insights register

- *Inferential —* the proxy.ts wildcard rewrite catching the SW file is the most common cause of "subdomain page renders black with no errors." Curl the SW content-type first — that's the diagnostic.
- *Inferential —* Vercel Security Checkpoint on a subdomain is not a code bug. Title check distinguishes it from a real page failure. Dashboard action needed.
- *User-framing —* "PWA shell first, theming polish after" — confirmed sequencing from a prior session. Don't invert it.

## Caveats

- The 4 committed commits cross two model boundaries (`ab7c73f8` = Claude Sonnet 4.6, `976bfa50` + `bff8b050` = Claude Opus 4.8). The file contents are what matter; authorship metadata is secondary.
- `resume.arcs.care` checkpoint status is unknown at session start — verify via curl before assuming it cleared.
- The uncommitted audit files are a separate workstream. If the next session is about audit service hosting, start from `docs/audit-service-hosting-scope.md`, not resume.PWA.theming.

---

`docs/audit-service-hosting-scope.md`, `docs/resume-tailor-theming-engine-spec.md`, `DEPLOY.md`, `scripts/deploy-smoke.mjs`, skills `vercel-subdomain-wildcard-routing` + `vercel-security-checkpoint-triage` — all written to disk this session, exist for pickup.
