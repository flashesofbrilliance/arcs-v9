# Agent Smith Analysis

**Project:** arcs-v9 (worktree `objective-mendeleev-471910`)
**Type:** Node.js (Next.js 16, Prisma 7) plus Python tooling (`scripts/`, `operators/`)
**Score:** 6.4/10 (first analysis)
**Date:** 2026-11-03
**Agent Smith:** v2.5.1

---

## Summary

The extension layer is strong: 26 agents with scoped tool lists, 25 skills that all carry frontmatter, 18 commands, path-scoped rules, and two guard hooks (canon write guard, cruise-control Bash guard). Every slash command the instruction files mention exists. The weak spots are security hygiene in the gitignored `settings.local.json` (a live-looking Resend API key and two passwords sit in plaintext allow rules, among 803 accreted one-off entries), no `Read` deny rules for secrets, a `gh pr merge *` allow that skips the repo's own `safe_merge.sh` rule, and about 12k tokens of always-loaded project instructions (CLAUDE.md plus its AGENTS.md and WORLD.md imports).

---

## Pillar Scores

| Pillar | Score | Notes |
|--------|:-----:|-------|
| Security Posture | 5/10 | Plaintext secrets in local allow rules; no secret-file deny rules; broad `Bash(node *)`, `Bash(python3)`; `gh pr merge *` allowed |
| Instruction Clarity | 6/10 | Dense, project-specific, well cross-referenced; but ~12k always-loaded tokens, ~60 hardcoded dates, stale model names |
| Configuration Quality | 7/10 | All JSON valid; duplicate and stale allow entries; local file holds 803 one-off rules |
| Context Efficiency | 6/10 | Rules are path-scoped (good); always-loaded budget ~19k tokens incl. memory index; MEMORY.md at 88% of its load cap |
| Command & Extension Design | 8/10 | Clean frontmatter everywhere, scoped tools; 17 agents omit `model`; 11 agents still `[CANDIDATE]` |
| Hook Safety | 7/10 | Good guard hooks, no prompt-injecting hooks; PreCompact and PostToolUse lack timeouts; PreCompact does network calls and writes files |
| MCP Integration | 6/10 | No `.mcp.json`, but `enableAllProjectMcpServers: true` would auto-trust any one added later |

Weighted: 5(0.20) + 6(0.20) + 7(0.15) + 6(0.15) + 8(0.15) + 7(0.10) + 6(0.05) = **6.35, shown as 6.4**.

---

## Findings

### Critical (breaks functionality or security risk)
- **Plaintext secrets in `.claude/settings.local.json`.** An allow rule embeds a full Resend API key in a `curl ... Authorization: Bearer re_T6zS…` command; a grep rule embeds the same key plus a password literal (`ArcsApp2026`); other rules embed `devtest123`. The file is gitignored (verified with `git check-ignore`), so this is not in git, but it sits on disk, in backups, and in every transcript that reads the file. **Fix:** rotate the Resend key (and the password if it was ever real), then delete those allow entries.
- **No `Read` deny rules for secret files** in `.claude/settings.json`. The deny list only covers `prisma db push`. `.env*`, `*.pem`, `*.key`, `credentials*` are all readable without a prompt. (Note: settings.local already shows `grep ... /Users/zharris/.env.local` was allowed.)

### Important (affects efficiency or maintainability)
- **`Bash(gh pr merge *)` in `settings.json` contradicts AGENTS.md gotcha 17** ("Merge with `scripts/safe_merge.sh` ... never `--squash`"). The repo setting blocks squash/rebase, but the allow lets a session merge with no head-SHA pin or check wait, without a prompt. Replace with `Bash(bash scripts/safe_merge.sh *)` and move `gh pr merge` to `ask`.
- **Broad interpreters allowed in `settings.local.json`:** `Bash(node *)`, `Bash(python3)`, `Bash(python3 -c ' *)`, `Bash(cat)`, `Bash(xxd)`. `node *` and `python3 -c` are arbitrary code execution with no prompt.
- **`settings.local.json` has 803 allow entries / 79 KB**, mostly one-off commands with baked-in preview URLs, `/Users/zharris/` paths and literal payloads. It is unreviewable, which is how the secrets above got in.
- **Always-loaded instructions are ~11.9k tokens** (CLAUDE.md ~4.5k, AGENTS.md ~5.6k, WORLD.md ~1.8k via `@` imports), over the 8k "critical" line. The 2026-07-19 trim and the 2026-10-17 move to path-scoped rules already helped; the next candidates are AGENTS.md's Receipts section (~1.2k tokens, only needed at merge/deploy time) and gotchas 9, 14a, 21 (narrow, area-specific).
- **Volatile content in always-loaded files:** 28 dates in CLAUDE.md, 25 in AGENTS.md, 9 in WORLD.md, plus the whole handoff block in CLAUDE.md (rewritten every molt). The handoff sits at the bottom, which is the right place; the dates inside durable rules (e.g. "(Zach, 2026-10-08)") are provenance and mostly fine, but each edit invalidates the cache prefix.
- **Stale model names:** AGENTS.md:77 says the compass runs "Claude Sonnet 4.6" and AGENTS.md:131 sets the commit trailer to `Co-Authored-By: Claude Sonnet 4.6`. The model map lives in `src/lib/claude-models.ts` (AGENTS.md says so itself), and current sessions run other models. Point to the file and make the trailer model-agnostic.
- **PreCompact hook** (`.claude/hooks/pre-compact.sh`) has no `timeout`, calls `gh pr list` over the network, and runs `lattice_drift_check.py --regenerate`, which can write files during compaction. The PostToolUse prisma hook also has no timeout.
- **Main checkout drift:** the session-start hook reports `/Users/zharris/arcs-v9` at `a6938dfa` vs origin/main `a0e6f606`; `.claude/commands/backlog-graph.md` differs, and project skills/commands load from the main checkout. Visible in this session: `echo-scan` exists in the worktree but is absent from the loaded skill list.

### Suggestions (improvements, not problems)
- **Duplicate allow entries** in `settings.json`: `Bash(git check-ignore *)` and `Bash(git merge-base *)` each appear twice; `Bash(git fetch *)` makes the four narrower `git fetch` rules redundant; `Bash(python3 scripts/backlog_status_check.py *)` subsumes its two narrower variants.
- **Stale MCP permission names** in `settings.json`: `mcp__Claude_Preview__preview_screenshot`, `mcp__Claude_Preview__preview_start`, `mcp__Claude_in_Chrome__navigate` don't match any current tool (now `mcp__Claude_Browser__*` and `mcp__claude-in-chrome__*`).
- **17 of 26 agents omit `model`.** They inherit the parent model, which is valid, but the read-only seats (`chief-*`, `idea-*`, `scenario-runner`, `recoil-*`, review agents) would run on Opus. Your own memory `model-tier-routing-locked-principle` argues for pinning `haiku`/`sonnet` here.
- **`.claude/arcs-session-state.md` is stale** (v3.104.0, 2026-10-06; current handoff is v3.142.0) yet 17 files cite it. Either regenerate it from the handoff or retire it.
- **`.claudeignore` does not exist.** Honest note: `.claudeignore` is not a documented Claude Code feature, so creating one may do nothing. The documented route is `permissions.deny` `Read(...)` rules (see Critical #2) plus `.gitignore`, which already covers `node_modules/`, `.next/`.
- **`enableAllProjectMcpServers: true`** in settings.local with no `.mcp.json`; set it to `false` and keep the explicit `enabledMcpjsonServers: ["supabase"]`.
- **MEMORY.md index is 21,659 B of the 24,576 B load cap** (88%). The memory file itself tracks this; a consolidation pass is due soon.

---

## Action Plan

### Option A: Quick Wins (Low Effort)

| # | Action |
|---|--------|
| A1 | Delete the 3 secret-bearing allow entries (Resend key, `ArcsApp2026`, `devtest123`) from `settings.local.json`; you rotate the Resend key in its dashboard |
| A2 | Add `Read` deny rules for `.env*`, `*.pem`, `*.key`, `credentials*`, `secrets/` to `settings.json` |
| A3 | Replace `Bash(gh pr merge *)` with `Bash(bash scripts/safe_merge.sh *)`; move `gh pr merge` to `ask` |
| A4 | Remove duplicate and stale (`Claude_Preview`, `Claude_in_Chrome`) allow entries from `settings.json` |
| A5 | Add `timeout` to the PreCompact (30s) and PostToolUse (10s) hooks |

### Option B: Recommended (Medium Effort)

| # | Action |
|---|--------|
| B1 | Prune `settings.local.json`: drop one-off `curl`/preview-URL/literal-payload entries and the broad `node *`, `python3`, `python3 -c`, `cat`, `xxd`; set `enableAllProjectMcpServers` to `false` (back up first) |
| B2 | Fix AGENTS.md stale model refs (line 77 → "model from `src/lib/claude-models.ts`"; line 131 → trailer per harness) |
| B3 | Pin `model:` on the read-only agents (`haiku` for chief/idea/scenario seats, `sonnet` for review agents) |
| B4 | Regenerate or retire `.claude/arcs-session-state.md` |

### Option C: Advanced (High Effort)

| # | Action |
|---|--------|
| C1 | Move AGENTS.md's Receipts section and narrow gotchas (9, 14a, 21) into path-scoped `.claude/rules/` files, targeting <8k always-loaded tokens |
| C2 | Make the PreCompact hook read-only (drop `--regenerate`, move the write to the session-start or `/handoff` path) |

---

## .claudeignore Status

| Check | Status |
|-------|:------:|
| File exists | ✗ |
| `.git/` included | N/A |
| Covers .gitignore patterns | N/A |
| Large binaries excluded | N/A |

`.claudeignore` is not part of Claude Code's documented config. Protect secrets with `permissions.deny` `Read(...)` rules instead (A2).

---

## Hooks Status

| Hook Event | Command | Safe? |
|------------|---------|:-----:|
| SessionStart | `.claude/hooks/session-start.sh` (timeout 30) | ✓ |
| PreCompact | `.claude/hooks/pre-compact.sh` (no timeout; `gh` network call; `--regenerate` writes) | ⚠ |
| PreToolUse `Edit\|Write\|MultiEdit` | `canon-write-guard.py` (timeout 10) | ✓ |
| PostToolUse `Write\|Edit` | inline prisma-schema reminder (no timeout) | ⚠ |
| Agent-scoped PreToolUse (cruise-control) | `cruise-control-bash-guard.py` | ✓ |

No hook injects dynamic content on `UserPromptSubmit`/`PreToolUse`, and none rewrites CLAUDE.md. All referenced scripts exist.

---

## MCP Status

| Server | Command | Scope |
|--------|---------|-------|
| (none in repo) | `.mcp.json` absent; `.mcp.json.example` only | `enabledMcpjsonServers: ["supabase"]` + `enableAllProjectMcpServers: true` in settings.local |

Many MCP servers are connected at user/app level (Vercel, Supabase, Gmail, Granola, monday, etc.); those are outside this repo's config and weren't scored.

---

## Wiring Status

| Check | Status | Details |
|-------|:------:|---------|
| Cross-references valid | ✓ | `/fold`, `/handoff`, `/handoff-pickup`, `/loops`, `/witness`, `/prior-art`, `/catalog` all resolve; all hook scripts exist |
| No stale references | ⚠ | 17 files cite stale `.claude/arcs-session-state.md`; stale MCP tool names in allow list |
| No orphaned extensions | ⚠ | 11 `[CANDIDATE]` agents; session-start flags `scenario-runner` at 0 uses after 16 days |
| No context conflicts | N/A | No `.claude/contexts/` |
| Bidirectional consistency | ⚠ | Worktree has `echo-scan` skill; main checkout (where skills load from) is behind origin/main |

---

## Memory Status

| Check | Status | Details |
|-------|:------:|---------|
| Memory directory found | ✓ | `~/.claude/projects/-Users-zharris-arcs-v9/memory/` |
| Memory files count | — | 363 files; index 21,659 B / 24,576 B cap |
| Conflicts with config | ⚠ | 1: AGENTS.md commit trailer "Claude Sonnet 4.6" vs memory `model-tier-routing-locked-principle` / harness attribution |
| Stale references | ⚠ | Global CLAUDE.md says the Supabase MCP "was disconnected"; memory `supabase-mcp-wrong-org-use-cli` says both Supabase MCPs reach prod since 2026-11-02 |

> Memory files are personal (not committed). These are suggestions to keep local memory aligned with the repo config.

---

## Content Overview

### Totals

| Category | Files | Est. Tokens | Loaded |
|----------|------:|------------:|--------|
| CLAUDE.md + AGENTS.md + WORLD.md | 3 | ~11,900 | Always |
| Global `~/.claude/CLAUDE.md` | 1 | ~1,500 | Always |
| MEMORY.md index | 1 | ~5,400 | Always |
| Rules (path-scoped) | 4 | ~5,400 | On path match |
| Commands | 18 | ~20,600 | On demand |
| Agents | 26 | ~19,400 | On demand (descriptions always) |
| Skills | 25 | ~39,400 | On demand (descriptions always) |
| Loose `.claude/arcs-*.md` | 5 | ~5,500 | Only when read |

**Potential savings:** ~3-4k always-loaded tokens (C1).

---

## Cache Efficiency

| File | Est. Tokens | Volatile markers | Verdict |
|------|------------:|:----------------:|---------|
| CLAUDE.md | ~4,500 | 28 dates; handoff block at bottom | Order is right; handoff churn is by design |
| AGENTS.md | ~5,600 | 25 dates, 1 TODO-class marker | Move narrow sections to rules |
| WORLD.md | ~1,800 | 9 dates | Clean enough |

CLAUDE.md alone is in the 5k "good" band; with imports the always-loaded set is ~11.9k (critical band).

---

## Instruction Quality Detail

| File | Clarity | Structure | Completeness | Efficiency | Usefulness | Overall |
|------|:-------:|:---------:|:------------:|:----------:|:----------:|:-------:|
| CLAUDE.md | 8 | 8 | 9 | 6 | 9 | 8/10 |
| AGENTS.md | 7 | 7 | 9 | 5 | 9 | 7/10 |
| WORLD.md | 8 | 8 | 7 | 8 | 7 | 8/10 |
| `.claude/rules/*` | 8 | 9 | 8 | 9 | 8 | 8/10 |

---

## Progress History

First analysis. Run again after making changes to track progress.

---

## Limitations

This analysis covers user-configurable components only. Claude Code's system prompt, built-in tool schemas, and runtime behavior are outside this scope. Token counts use ~4 characters per token.

---

*Report generated by [Agent Smith](https://github.com/maxencemeloni/claude-code-agent-smith)*
