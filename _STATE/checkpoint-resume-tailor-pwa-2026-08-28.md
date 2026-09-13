# Checkpoint — resume-tailor PWA surface (2026-08-28)

## What landed this session

### Files written (on `feat/resume-pwa-theming` branch)
| File | Size | Purpose |
|---|---|---|
| `public/resume-tailor-landing.html` | 12,166 B | Surface A — standalone landing page (React-free, hand-rolled subset) |
| `public/resume-tailor-pwa.html` | 25,528 B | Surface B — standalone PWA: MUI via CDN, three-theme engine, interactive skill content |
| `public/resume-tailor-manifest.json` | 762 B | PWA manifest, branded RT-diamond, theme colors |
| `public/resume-tailor-sw.js` | 1,589 B | Service worker: cache-first shell, network-first job URLs |
| `public/resume-tailor-icon-192.png` | 1,642 B | 192×192 PWA icon, diamond glyph + RT mark |
| `public/resume-tailor-icon-512.png` | 6,660 B | 512×512 PWA icon, same glyph |
| `scripts/gen_tailor_icons.py` | 933 B | Icon generator (Pillow) — can regenerate if mark changes |

### Build
- `npx next build` — exit 0, "Compiled successfully", "Generating static pages using 7 workers (23/23)".
- `resume-tailor-pwa.html` is a static file — no TS transpilation, so the build's only job is to confirm `next.config.ts` is valid and the rewrites resolve.

### `next.config.ts` routing
Already has by-singular rewrites (from a prior session), nothing added this session:
```
resume-tailor.arcs.care  /           → public/resume-tailor.html
resume-tailor.arcs.care  /pwa        → public/resume-tailor-pwa.html
```
Other existing rewrites: `resume.arcs.care` → `resume.html`, plus vishal/kelly/cj-brief/chase/chris/growth/todd/labella/peter/julia/fanatics/daniel/token/jeben/louisville/lewoof. All untouched.

## Architecture

### Surface A — `resume-tailor-landing.html` (React-free)
- Static hand-rolled subset: hero, summary, role-breaking (3 bullets), how-it-works (6-step pipe table), why-it-matters (mosquito claim), artifact proof (3 graded claims from the PDF), install, footer.
- Uses `@import` Google Fonts (Inter + JetBrains Mono) — no render-blocking `<link>`.
- Self-contained; no JS bundle; no theme switching (dev-only static frame).
- Distinct from `resume.arcs.care` → `resume.html` (personal resume). No PII overlap in `resume-tailor-landing.html`.

### Surface B — `resume-tailor-pwa.html` (MUI + React via CDN)
- **CDN loading pattern (proven):** `<script type="importmap">` → `<script type="module">` loads 6 esm.sh modules (react, react-dom, @mui/material, @mui/material/styles, @emotion/react, @emotion/styled) → populates `window.MUI_*` globals → writes `window.__MUI_BOM` (diagnostic).
- **Babel transpilation:** `<script type="text/babel">` (Babel standalone from CDN) transpiles inline JSX → runs at parse time.
- **Deferred mount (bug fixed this session):** The babel script no longer assumes MUI globals exist. At mount time (bottom of babel script), checks `window.MUI_ThemeProvider` + `window.ReactDOM/ReactDOMClient`. If missing, polls every 120ms and falls back to a "Loading MUI from CDN…" loading state in `#root`. This fixes the race condition where the babel script executes synchronously during parsing but the module script is deferred.
- **Three-theme engine:** `THEMES.formal` (cyan+gold, regulated/finance/legal/enterprise), `THEMES.casual` (green+purple, early-stage/consumer/creative), `THEMES.neutral` (slate+cyan secondary, ambiguous). Picked from `docs/resume-tailor-theming-engine-spec.md`.
- **Inference hook:** `inferTheme(jobUrlOrText)` — regex soft signal → theme key. Default `neutral` when empty or ambiguous. User can also set via the "Auto-theme from job posting" input field (default `neutral`, switchable by clicking the chip).
- **Interactive skill content (6 tabs):**
  1. The one rule — moat thesis ("defensibly true over impressive")
  2. Every claim is graded — documented/self-reported/unverifiable card grid
  3. What it actually produces — artifact proof: 3 graded claims lifted from the PDF (`Zach Harris Resume 2026.pdf`), with evidence column + color badge
  4. The method — 6-step pipe (GATHER → GRADED SSOT → FALSIFY → PROJECT → RENDER → GAUNTLET), lifted from `public/resume-tailor.html`
  5. Install & use — two-column: plugin install + per-role use, Claude Code commands
- **PWA shell:** manifest link, SW reg (`<script defer src="/resume-tailor-sw.js">`), apple-touch-icon, `theme-color`, `beforeinstallprompt` handler, "Add to Home Screen" button (disappears on `appinstalled`).
- **No backend, no build step, no npm install.** Single file, run by serving `public/` via Next.js rewrites (dev) or any static host.

### PWA assets
- `resume-tailor-manifest.json`: `name: "resume-tailor"`, `start_url: "/pwa"`, `display: "standalone"`, `theme_color: "#020408"`, `background_color: "#020408"`, icons 192/512.
- `resume-tailor-sw.js`: install event listener (skip prompt, update `window.__TAILOR_SW_INSTALLED`), cache-first for shell file + icon + manifest, network-first for JS chunks, fetch listener adds `stale-while-revalidate` for other assets. Keep-alive via `setInterval` every 30s (so inactive PWA doesn't get evicted from the SW cache).
- Icons: diamond glyph + "RT" letterform mark, distinct from the personal-resume diamond (which is plain).

## Source material consumed
- PDF: `~/Zach Harris Resume 2026.pdf` — extracted via `pdftotext`. Used the 3 graded-claim artifact in Surface B (the doc/self/unv sample), not the full resume text (PII concern — the personal resume stays on `resume.arcs.care`).
- `public/resume-tailor.html` — existing skill landing page from a prior session. Read the full content (12,788 chars). Used the how-it-works 6-step structure, the role-breaking bullets, the why-it-matters mosquito framing ("a resume that sounds true but isn't").
- `docs/resume-tailor-theming-engine-spec.md` — read by prior session, not this one. Referenced as the three-theme spec.
- `docs/decision-memo-creative-tim-template-audit.md` — Material Kit 2 React chosen as base. Not re-read this session.
- `public/mui-smoke.html` — proven MUI CDN reference. Not re-read this session.
- `public/resume.html` — the existing personal-resume PWA page. Not touched (constraint: `resume.arcs.care` stays clean/static).

## Decisions made this session

### 1. Surface B is a standalone HTML file, not a Next.js route
User said "from an html file." Confirmed: `resume-tailor-pwa.html` is self-contained, no app router, no server component. Served via the `next.config.ts` by-singular rewrite `resume-tailor.arcs.care /pwa → public/resume-tailor-pwa.html`. Same pattern as `mui-smoke.html` and the existing `resume.html`.

### 2. Theme inference is heuristic, not LLM
`inferTheme()` is regex over keywords (finance/legal/enterprise → formal; startup/consumer/creative → casual). No Claude call, no API key needed. The user can override by clicking the three theme chips. This matches the spec's "soft signal" language.

### 3. The PDF artifact is sampled, not reproduced verbatim
Took 3 representative graded claims from the PDF (the doc/self/unv sample) for the artifact proof in Surface B tab 3. The full resume text is not embedded in any HTML file. PII stays on `resume.arcs.care` / `resume.html`.

### 4. Deferred mount with retry loop
Fixed the real race condition where the babel script runs during parsing (sync) but MUI modules load asynchronously (deferred module script). Solution: gate the mount on `MUI_ThemeProvider` + `ReactDOM` existing, poll every 120ms, show a loading state in the meantime. No user action needed.

### 5. `react-dom/client` vs `ReactDOM.render` — both supported
The mount block tries `ReactDOM.render` first (React 18 legacy), falls back to `ReactDOMClient.createRoot` (React 18 concurrent). esm.sh exports both. The conditional handles whichever the CDN version exposes.

## Open items / next sessions

### Not done, by design (dev-only scope, user said "lets do this on dev for now")
- Vercel deploy of `resume-tailor.arcs.care` — not done. The branch preview exists but was never promoted, and the user explicitly said not to deploy to `resume.arcs.care`.
- The `resume.arcs.care` subdomain stays clean: `resume.html` there has PWA wiring (`manifest.json` ref, SW reg, install button) that the user may want stripped to match "static personal resume" intent — not done this session.
- Production main still serves `resume-sw.js` as `text/html` (the "SW trap" — the file + `proxy.ts` staticAssets allowlist don't exist on main). Not fixed (by design — don't deploy to `resume.arcs.care`).

### Next-session first moves
1. **Dev smoke-test Surface B locally** — serve `public/` via `npx next dev` (or a static server), hit `http://localhost:3000/resume-tailor-pwa.html` directly (bypass the rewrite for a direct file check), open DevTools console, verify: `__MUI_BOM` shows all 6 modules loaded, no "MUI CDN load failed" fallback, tabs render, theme chips switch, inference field changes "current" label. The rewrite path (`resume-tailor.arcs.care/pwa`) can only be tested against the Vercel preview, not local dev (no local subdomain).
2. **Verify `resume-tailor-landing.html` standalone** — serve and eyeball; it's React-free so should render with no console errors.
3. **Strip PWA wiring from `resume.html`** — remove the manifest link, SW reg script, install button, and `beforeinstallprompt` handler so `resume.arcs.care` is a clean static personal resume. Low-risk one-file edit.
4. **Re-read the resume-tailor skill SKILL.md** — the user said "if you try running the actual resume skill from the repo it prints pdfs like this" (the Context Warnings path-outside-workspace message). That suggests the skill throws when run against the PDF attachment. The pwa.html content is the *product* (what it renders), not the skill source. Next session should load `skill_view(name='claude-code')` (was `[SKILL_PRUNED]` earlier) and re-read `resume-tailor.html` to confirm the pwa's "Install & use" tab matches the actual skill instructions.
5. **Promotion queue (separate, later)** — `feat/resume-pwa-theming` → main → Vercel promote → add `resume-tailor.arcs.care` + `resume-tailor.arcs.care/pwa` domains in Vercel project settings → re-validate DNS. Each step gated; don't bundle.

### Coordination note
- A sibling subagent (`20260828_161625_3dd30e`) apparently touched `resume-tailor-pwa.html` during this session (the `write_file` warning). Verified on disk: the file content matches what was written, no conflict. The sibling's `deleg_e5ae564863` batch (E1/E2/E3 gauntlet) has no surviving artifacts — no task dir, no completed transcripts, no file references. If that batch's results matter, re-dispatch needed; not blocking PWA.

## Credentials note
No API keys, tokens, or passwords touched in this session. The Vercel dashboard, domain DNS, and delegation cache paths are operations references only. If a future turn surfaces any, replace with `[REDACTED]`.

## Skill to save
If the user wants: a `resume-tailor-pwa-checkpoint` skill capturing (file inventory, build command, smoke-test steps, strip-resume-pwa-wiring steps, promotion queue). Not created yet — ask first.

## Memory
Nothing durable beyond what's already in MEMORY.md (PWA sequencing: shell before theming; embed MUI into standalone CDN page, not Next.js app-router migration; subdomain-split decision). No new durable fact this session that warrants a memory write.
