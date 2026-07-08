# ARCS Drift Log — Append-Only

One entry per session. Format: date → RESOLVED / BELIEF_CHANGE / NEW / OPEN.
This is an audit trail of how understanding has evolved, not a task list.

---

## 2026-05-28

**Session scope:** Design system sprint (tokens + Badge + Button + Card), ADR authoring (009/010/011), ADR-002 closure, new slash commands (/dewy-stub, /receipt-book-curator), arcs.care button fix.

### RESOLVED
- Design system source of truth: new `src/ui/tokens.ts` matches arcs-v9's actual page palette (#020408, etc.) — not arcs-app's Le Woof palette. Both exist independently.
- arcs-app pre-stub-revert commit identified: `83374ed` — Register pattern Badge/Button/Card recovered from git history.
- arcs.care `hw-button-orange` button fixed: flat fill, `border-radius: 0`, explicit sizing — conforms to GCR design system. Committed `94a0ab8`.
- ADR-002 formally closed: P4 trigger fired, Supabase live, execution divergence logged.

### BELIEF_CHANGE
- **Was:** ADR numbering stopped at ADR-008. **Now:** ADR-009 (design system), ADR-010 (naming), ADR-011 (import strategy), ADR-012 (PLG Phase 1) all authored this session.
- **Was:** No shared component library in arcs-v9. **Now:** src/ui/ with tokens.ts + Badge + Button + Card committed and functional.

### NEW
- `/dewy-stub` command: lightweight ADR scaffolder (`~/.claude/commands/dewy-stub.md`)
- `/receipt-book-curator` command: decision book state audit (`~/.claude/commands/receipt-book-curator.md`)
- Design system ADR-011 revisit trigger: component count ≥8 fires barrel + optimizePackageImports ADR
- Second Vercel toolbar thread `YyvHp8_-4jXX` open — API investigation ("Is the API working? Busted? Missing deps?") — NOT yet resolved

### OPEN
- Second toolbar thread `YyvHp8_-4jXX` (API investigation) — unresolved
- ADR-009 Stability field: should be REVISIT not STABLE (ultrareview finding, cosmetic)
- Panel + Chip components — next in design system sprint
- P5: arcs-care PLG Phase 1 (compass model swap + Lab offer card) — specced in ADR-012, not yet built

---

## 2026-05-18

**Session scope:** Full ecosystem scan (local + GitHub), P0 arcs-v9 push, P2 perplexity-mcp scaffold, memory consolidation.

### RESOLVED
- `arcs-v9` (`/Users/zharris/arcs`) identified as canonical ARCS v9 app and pushed to `github.com/flashesofbrilliance/arcs-v9`. No longer at existential risk.
- `perplexity-mcp` scaffolded and pushed to GitHub. Blocked only on `PERPLEXITY_API_KEY`.

### BELIEF_CHANGE
- **Was:** canonical v9 dev surface = `arcs-decision-receipts`. **Now:** `arcs-decision-receipts` is stale/superseded. Real canonical = `/Users/zharris/arcs`.
- **Was:** True North = template string (`_extract_true_north_and_why` in arcs_api.py). **Now:** arcs-v9 uses real Claude Sonnet 4.6 call — True North is LLM-generated and specific per decision.
- **Was:** 3 repos claiming to be the monorepo. **Now:** 11+ GitHub repos discovered across `flashesofbrilliance` org; arcs-v9 is the new canonical.
- **Was:** FastAPI at port 8765 is the active backend. **Now:** arcs-v9 has no FastAPI dependency — all intelligence is inline Next.js route handlers calling Claude.
- **Was:** ATG (tributaries) is backlog. **Now:** Already implemented in arcs-v9 compass route — 3 follow-ups (meta/challenge/adjacent) per response.

### NEW
- `arcs-hq` (GitHub): full TypeScript skills runtime (SkillRegistry, Orchestrator, RAG, Notion sync). To be archived (P1).
- `arcs-canon` (GitHub): Dewey YAML knowledge library with CANON-FILE-STANDARD-v2.
- `arcs-immune-system` (GitHub): published Python pip package (`pip install arcs-immune-system`). 4-variable manipulation detection.
- `arcs-field-os` (GitHub): v8.5 spec/artifact archive.
- `arcs-memory-export` (GitHub): folksonomy/indexer — potential semantic compiler precursor.
- Y-gate (`ygate.ts`): 12D manifold computation in arcs-v9. States: GREEN/YELLOW/RED/FORK/MERGE/DRIFT/SCRATCH/PARADOX/DELTA.
- DEWY schema in Prisma (D·E·W·Y + lineage + kinematic fields).
- `mcp-handler` v1.1.0 = current package name for Vercel MCP adapter (supersedes `@vercel/mcp-adapter`).

### OPEN
- P2: perplexity-mcp needs `PERPLEXITY_API_KEY` → deploy → wire to `~/.claude/settings.json`. Reminder: 2026-05-19 09:00.
- P1: arcs-hq archive + extract `SkillDefinition`/`SkillRegistry` types to arcs-v9.
- P3: Home dir `.git` audit — 51 commits ahead of origin. **Hard gate: audit before removing `.git`.**
- P4: arcs-v9 SQLite → Supabase. TEXT→jsonb optimization deferred.
- GIGI seam: `_extract_true_north_and_why` in arcs_api.py = arcs-care path ✅ SWAPPED. arcs-v9 seam = `src/app/api/compass/route.ts` — not yet wired.
- arcs-v9 not yet deployed to Vercel (on GitHub, not live).
- Dual data store unresolved: arcs-v9 (SQLite) vs arcs-care (Supabase).
- GitHub issues #40–#43 still open — close manually.
- gigi PR #1 still open — merge manually (docs-only, no CI gate).
- gigi-stream autostart: not configured as launchd plist — substrate goes dark on reboot (degrades gracefully to L5).

---

## 2026-05-18 (session 2 — cranky-hoover substrate build)

**Session scope:** P2/P3/P4 substrate build track. GIGI interface discovered, macOS compile fix, 12 BAR templates seeded, seam swapped, backup verified.

### RESOLVED
- GIGI interface is REST (`/v1/bundles/*`). GQL `CREATE BUNDLE` syntax exists but had parse errors — REST is the reliable path.
- `malloc_trim` is glibc-only, not macOS. Fixed `#[cfg(unix)]` → `#[cfg(target_os = "linux")]` in `gigi_stream.rs` (2 locations) to compile on M1.
- arcs-care seam is `A.R.C.S/arcs_api.py:_extract_true_north_and_why()` — swapped. L1/L2/L5 routing now live. Every receipt response includes `substrate: {routing_path, holonomy_distance, confidence, template_id, provenance}`.
- AES-256-GCM backup to iCloud Drive confirmed working: `arcs-gigi.enc` (8.7KB) decrypts to `{reason, bundles: {arcs_templates: 12, arcs_gap_log: 1}}`.
- Battery mode reading confirmed: `pmset -g batt` → `FULL` (AC Power, 100%).

### BELIEF_CHANGE
- **Was:** GIGI interface shape unknown until P2 read. **Now:** Confirmed REST API. GQL is secondary.
- **Was:** arcs-v9 seam TBD between arcs_api.py and compass/route.ts. **Now:** arcs-care path (arcs_api.py) swapped first. arcs-v9 path (compass/route.ts) still future.

### NEW
- `arcs_substrate.py` — fiber coordinate distance metric: L2 norm over ordinal stakes/horizon/mode dimensions, normalized to [0,1] (max ≈ 4.3).
- `arcs_battery.py` — fails open (returns FULL on any pmset error).
- `arcs_backup.py` — semantic triggers (receipt_written, template_promoted, session_closed); atomic write via tmp + os.replace.
- Commit `dcfb4ff` in A.R.C.S main: all 6 substrate files landed clean, ruff passes.
- P5 gate: need ~20 validated templates with real deltas before RAM→ROM arc weld work starts.

### OPEN
- GitHub issues #40–#43: complete but not closed. Manual action needed.
- gigi PR #1: docs-only, ready to merge. Manual action needed.
- gigi-stream launchd plist: not set up — process dies on reboot (graceful L5 degradation).
- arcs-v9 GIGI seam: `src/app/api/compass/route.ts` — not yet wired. Future P3-equivalent for arcs-v9.
- P0 (ADP + FileVault + Keychain): status unknown — never verified in session.
- `arcs-decision-receipts` issues #40–43 were written for the FastAPI/arcs-care path. Need to reconcile with arcs-v9 reality before executing P1–P4 GIGI track.

---

## 2026-05-26 (session 3 — Vercel deploy + housekeeping)

**Session scope:** Thread summary, memory consolidation, orienting on arcs-v9 Vercel deploy path.

### RESOLVED
- GitHub issues #40–#43 closed (2026-05-19).
- gigi-stream launchd plist live: `~/Library/LaunchAgents/com.arcs.gigi-stream.plist`. Wrapper `~/gigi/start.sh` auto-reseeds 12 BAR templates after every restart. Process survives reboots.
- Question Compass standalone (A.R.C.S. FastAPI) was a POC to prove NCI + ARCS API — confirmed legacy. arcs-v9 is the canonical product surface.
- arcs-v9 build passes clean. Vercel project already linked (`prj_KjhmInzgwA6Pdh7tg8Yx7W8JzEtt`). 6/9 env vars set on all three environments.
- Prisma schema change: `provider = "sqlite"` → `"postgresql"` with `DATABASE_URL` + `DIRECT_URL` (uncommitted local change).

### BELIEF_CHANGE
- **Was:** arcs-v9 uses SQLite only. **Now:** Schema already changed to postgresql locally (uncommitted). Deploy is unblocked once DATABASE_URL + DIRECT_URL + SUPABASE_SERVICE_ROLE_KEY are set.
- **Was:** GIGI substrate work lives on arcs-decision-receipts. **Now:** All issues closed, that repo is retired. GIGI substrate is a separate local-first system under A.R.C.S.; arcs-v9 is the product.
- **Was:** Zoetrope = potentially useful legacy code. **Now:** Confirmed legacy hypercube 5x5x5x5x5 viz — archived on remote branch, local worktree deleted.

### NEW
- arcs-field-os repo has substantial spec activity: `orient-prd.md` (Kairos Lock active), `jtbd-master-map.md`, `dewy-receipt-schema-v1.json` in arcs-v9.
- Open sprint #2–#5 in arcs-v9: DEWY schema wire-in → Time ROM → Compass→DEWY flow doc → Book II Canon.
- Vercel CLI 53.1.0 bug: `vercel env add NAME preview --value X --yes` always errors with `git_branch_required` even when omitting branch. Workaround: Vercel REST API directly via Python urllib.
- Supabase project ref: `owdiiyvphyifukygvxhg`. All other env vars set; just need DB connection strings.

### OPEN
- arcs-v9 Vercel deploy: need `DATABASE_URL` (Supabase pooler, port 6543) + `DIRECT_URL` (port 5432) + `SUPABASE_SERVICE_ROLE_KEY` from Supabase dashboard → set on Vercel → `prisma db push` → `vercel deploy`
- Prisma schema postgresql change is uncommitted — needs to be committed before deploy
- gigi PR #1: still open (docs-only, safe to merge)
- P0 (ADP + FileVault + Keychain): still unverified
- Open sprint #2–#5 in arcs-v9: not started

---

## 2026-05-26 (session 4 — context pre-loading + deploy prep)

**Session scope:** Global CLAUDE.md creation, deploy path investigation, Supabase DB connection string handoff.

### NEW
- `~/.claude/CLAUDE.md` created — global session context file. Loads every session regardless of working directory. Contains: canonical repo map, active P-track status (with gates), DRIFT_LOG pointer, cross-project rules.
- arcs-v9 Vercel project confirmed: `prj_KjhmInzgwA6Pdh7tg8Yx7W8JzEtt` (team `team_narCbxUgS4eiieJKRv1QMfff`), linked to `flashesofbrilliance/arcs-v9`. No deployments yet.
- Supabase DB password still needed to complete deploy. Both URLs known: pooler (port 6543) = DATABASE_URL, direct (port 5432) = DIRECT_URL. User connecting Supabase integration to Vercel project didn't inject vars automatically — manual paste required.

### OPEN
- DB password → wire DATABASE_URL + DIRECT_URL → `prisma db push` → `vercel deploy --prod`
- Commit Prisma schema change (sqlite → postgresql) before deploy

---

## 2026-05-27 (session 5 — ARCS Data Science Suite + Calendar MCP restructure)

**Session scope:** Completed ARCS Personal Data Science Suite (Phases 0–3), ran real calendar gauntlet via MCP, restructured Google Calendar with 5 recurring anchor blocks.

### RESOLVED
- ARCS Data Science Suite complete: `arcs_core.py` (kernel, DEWY, Folksonomist), `calendar_scan.py`, `listening_scan.py`, `reader_scan.py`, `arcs_cli.py` — all committed and pushed to arcs-v9.
- Calendar gauntlet run on 750 real events via Calendar MCP. Key findings: 2.3% revenue/external, 0% recurring, peak maker window 06:00–09:00 ET.
- `DomainConfig.strand_a_fn` hook resolves NCI semantic drift (P5) — each scanner injects its own scoring logic; kernel is domain-agnostic.
- Versioned output tree live: `exports/{domain}/YYYY-MM-DD/`.

### NEW
- Google Calendar restructured via MCP — 5 recurring anchor blocks created starting 2026-06-01:
  - 🔴 Deep Work: Mon–Fri 06:00–09:00 (Tomato)
  - 🟢 Morning Stack: Daily 05:30–06:00 (Sage)
  - 🟠 Revenue Block: Tue+Thu 10:00–12:00 (Tangerine)
  - 🟡 Weekly Review: Fri 16:00–17:00 (Banana)
  - 🔴 Shutdown Ritual: Mon–Fri 17:30–17:45 (Tomato)
- Listening scan has only synthetic fixture data. Real Spotify data requires Privacy Export from spotify.com/account/privacy (request extended streaming history — up to 30 days).
- `_CANON/book-ii/part-iv-sessions-api.md` exists as DRAFT (DO NOT COMMIT per frontmatter).

### OPEN
- DB password → wire DATABASE_URL + DIRECT_URL → `prisma db push` → `vercel deploy --prod`
- Commit Prisma schema change (sqlite → postgresql) before deploy
- Spotify extended history export: user must request at spotify.com/account/privacy
- Kindle `My Clippings.txt`: needs USB connect or Kindle Mac app check
- Calendar Phase 2: find/rename existing morning routine event to avoid duplicate with 🟢 Morning Stack

---

## 2026-05-27 (session 6 — Human Connection Physics / Pronoia Spark Plug)

**Session scope:** Designed, built, and deployed `/helpful` instrument to arcs.care. Resolved arcs-care-local consolidation and credits/engine-offline wall.

### RESOLVED
- `/helpful` (Human Connection Physics — Pronoia Spark Plug) live at `arcs.care/helpful`.
- `helpful_receipts` Supabase migration applied to `owdiiyvphyifukygvxhg` (ARCS project).
- API credits restored. Compass ungated (`feat(compass): ungate Question Compass`).
- `arcs-care-local` Vercel project deleted — consolidated into canonical `arcs-care` (`prj_cVMjIW1ElkddeqdyowuQi34P7KIs`). Local repo at `~/arcs-care-local` still exists; `.vercel/project.json` updated to point at arcs-care.
- "Engine Offline" error root-caused: ANTHROPIC_API_KEY was missing from `arcs-care-local` project (not credits). Added key; credits were separately restored by user.

### BELIEF_CHANGE
- **Was:** arcs-care-local and arcs-care are separate Vercel projects. **Now:** Single Vercel project `arcs-care`. arcs-care-local was a duplicate that got cleaned up.
- **Was:** Compass gated (no credits). **Now:** Compass live, credits restored, model confirmed as `claude-haiku-4-5-20251001`.

### NEW
- `/helpful` instrument: POST /api/helpful → Claude Haiku → JSON receipt with `offer`, `pronoia_spark`, `off_ramp_phrase`, `tier`, `failure_mode`, `failure_mode_rationale`, `opportunity_cost_rating`, `stop_loss_triggered`, `next_action`.
- Human Connection Physics canon block (from Perplexity doc): Pronoia Spark Plug + Opportunity-Cost Guardrail + Stated vs. Revealed Classifier + Stop-Loss Rule. Plan file at `~/.claude/plans/users-zharris-downloads-i-feel-alone-a-floating-mitten.md`.
- Pressure tests run on 4 live cases (Harry, Jeben, Ben Allen, FDE onboarding). Cross-case pattern: offer must remove friction, not add context.
- arcs.care design system shifted to GCR dark hardware aesthetic (black/orange) with LED scroll strip, DigitalCounter, NeonBackground.
- SPEC.md added to arcs-care repo (`62e3eef`).

### OPEN
- arcs-v9 Vercel deploy still blocked: need DATABASE_URL + DIRECT_URL + SUPABASE_SERVICE_ROLE_KEY
- `_CANON/book-ii/part-iv-sessions-api.md` untracked in arcs-v9 — check frontmatter before committing (was marked DO NOT COMMIT in prior session)
- `exports/` dir in arcs-v9 — Apollo data + arcs_score scripts, likely needs .gitignore entry
- P3: Home dir `.git` audit (51 commits ahead of origin) — still hard-gated
