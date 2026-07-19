# Token & Budget Efficiency Audit — ARCS
**Date:** 2026-07-19 · **Scope:** arcs-v9 repo + the two prior audit artifacts
(`sentinelrebuild.md`, `claudeusagepunchlist.md`) · **Register:** opinionated, ranked by measured leverage.

---

## TL;DR — the ranking is wrong, and I can prove it

The prior punchlist calls **stripping 13 connectors off the Drift Sentinel** the "single cheapest win" (#1).
That fix is correct and you should do it. But it is **not** your highest-leverage lever, and ranking it #1
misdirects effort.

Here is the thing the punchlist *couldn't* see — it explicitly says "I can't read your conversations, only
the config footprint." I can read the actual repo, and the biggest leak lives there:

| Cost | Paid when | Measured size | Growth |
|---|---|---|---|
| **Sentinel connector payload** | 1× per day (one scheduled fire) | ~13 tool-def blocks | flat |
| **Auto-loaded context tax** (CLAUDE.md `@`-imports AGENTS.md + WORLD.md) | **every message of every session** | **~24,600 tokens** | **unbounded by policy** |
| **Orientation-chain read** (agents told to read MEMORY.md first) | most sessions | **+14,750 tokens** | **unbounded by policy** |

**~39,000 tokens are consumed before a single line of work happens, on essentially every interactive
session in this repo.** The Sentinel wastes its connector payload ~365×/year into *fresh, isolated*
sessions. The context tax is paid on *every turn of every human session, forever, and it grows every time
anyone runs `/handoff`.* That is the #1 lever. The Sentinel fix is real but an order of magnitude smaller.

**Root cause:** the governance policy in CLAUDE.md — *"CLAUDE.md — append new sections only; never overwrite
prior"* and *"MEMORY.md — append-only; never delete prior versions."* These are append-forever machines
bolted to the two files that load on every session. They cannot do anything but grow, and they have:
**28 handoff sections** (v0.1.0 → v3.7.0) now live in the file every session reads first.

---

## The measured footprint (arcs-v9, today)

```
CLAUDE.md    1568 lines   79,352 bytes   ~19,838 tok   (28 handoff sections)
AGENTS.md     185 lines    9,718 bytes    ~2,429 tok   (@-imported by CLAUDE.md)
WORLD.md      188 lines    9,252 bytes    ~2,313 tok   (@-imported by CLAUDE.md)
MEMORY.md     815 lines   59,008 bytes   ~14,752 tok   (orientation-chain read #1)
------------------------------------------------------------------
Auto-loaded system prompt (CLAUDE+AGENTS+WORLD):        ~24,580 tok  / EVERY session
+ orientation chain if followed (MEMORY.md):            ~39,332 tok  / EVERY session
```

Of CLAUDE.md's 28 handoff sections, **~26 are dead history** — v0.1.0 through v3.4.0 describe work that
shipped months ago. No live session needs the story of the v0.5.0 Book II Part V draft. It is pure ballast
riding in the highest-traffic file in the repo.

---

## Findings, re-ranked by real leverage

### 🔴 P0 — The append-forever context tax (punchlist rated this 🟡 1.4, buried)
**Fix:** stop loading dead history on every session. Keep CLAUDE.md to durable facts only
(Project Map, ROM primitives, token-saving rules, current sprint, **latest 1–2 handoffs**). Move
v0.1.0→v3.4.0 handoffs to `_ARCHIVE/handoffs.md`, which is **not** `@`-imported. Same for MEMORY.md.

This is *relocation, not deletion* — history stays in git and in a reachable file, so it honors "never delete
prior versions" while ending the per-session tax. Estimated CLAUDE.md reduction: **~19,800 → ~4,000 tokens**
(~80%). Across every session in the repo, this is the dominant saving.

**Governance contradiction to resolve first:** the append-only handoff policy directly contradicts the
punchlist's own advice ("cap CLAUDE.md at ~150 lines, prune stale sections") *and* the repo's existing
`# Token-saving rules` section. Two rules in the same file tell you to both never-prune and keep-lean. Pick
one. My call: **CLAUDE.md is a working file, not an archive** — lean wins; archival preserves history
elsewhere. This needs a one-line policy amendment, not a silent edit.

### 🔴 P0 — Strip Sentinel connectors + downgrade to Haiku (punchlist #1/#2.1 — agreed, correct)
The 13-connector payload on a `Bash/Read/Write/Edit/Glob/Grep`-only task is dead weight, and mechanical
git-log parsing is Haiku work, not Sonnet. Both correct. Note the ownership rule from `sentinelrebuild.md`:
the task was created via API in the arcs-decision-receipts environment, so it must be recreated/deleted from
there — a chat session can't modify it. **This is genuinely cheap and worth doing — it's just not #1.**

### 🟡 P1 — The orientation-chain instruction is the multiplier
CLAUDE.md and the handoffs repeatedly instruct every agent to *"read MEMORY.md → SKILL.md → WORLD.md →
AGENTS.md in order"* before starting. This is what converts a big file into a *guaranteed* per-session cost —
it actively tells the model to spend ~40k tokens orienting before touching the task. Once P0 archival lands,
rewrite the orientation chain to: "read the Project Map; read a specific handoff only if resuming that
thread." Don't mandate a 40k-token read for a one-line change.

### 🟡 P1 — Subagents for exploration (punchlist 1.3 — agreed, high value here)
On a repo this size with `operators/` at 16.6K LOC, "use a subagent / the Explore agent to find X" keeps the
file-dump noise out of your main context. This is the #1 *interactive* habit. Correct as stated.

### 🟡 P2 — Custom skills + commands (punchlist §3/§4 — agreed, good)
`nci-scoring` skill and `/nci-commit`, `/drift-check`, `/ship-preview` commands are sound: they replace
re-explaining the rubric (tokens) and reduce missing-NCI commits. Real, but this is *consistency* leverage
more than *token* leverage — rank it below the two P0s.

### 🟢 P3 — Stale `_STATE` / handoff sprawl (punchlist missed this)
`_STATE/` holds `meta-audit-roadmap-v1.md` (23,790 bytes), `cold-start-v3.1.0.md`,
`compass-kit-phase2-handoff.md`, plus per-branch state files. Several are stale by their own version stamps.
These aren't auto-loaded, but agents get pointed at them and burn tokens reading. Prune or date-archive.

### 🟢 P3 — Permission-list rot (punchlist missed this)
`.claude/settings.json` `allow` has 60+ entries including opaque MCP UUID tools
(`mcp__b00f7942-…__get_deployment`). Not a big token cost, but it's config debt that makes the real
allowlist unreadable. Collapse the UUIDs to named servers when you next touch it.

### 🟢 P3 — `git fetch origin main` on every SessionStart (punchlist missed this)
The session-start hook does a network `git fetch` every boot to refresh snapshot sync state. Not tokens —
latency and a network round-trip on every session. Fine to keep; flagging it as a non-token cost the
punchlist's config-only view couldn't see.

---

## Where I disagree with the prior punchlist

1. **Leverage order.** Their #1 (Sentinel connectors) is a once-a-day fresh-session cost. The real #1 is the
   every-session, unbounded-growth context tax their own 1.4 flagged but rated 🟡 and buried. Reordering
   matters because effort follows the #1 label.
2. **"Your sentinel already updates CLAUDE.md in place — good pattern."** In *this* repo the governing policy
   is the opposite (append-only, never overwrite), and it has produced a 28-section, 19.8k-token file. The
   "good pattern" they praise is contradicted by the policy actually in force. That contradiction is the bug.
3. **They couldn't measure — I did.** Every number above is from the working tree, not inferred from a config
   footprint. The single highest-leverage fix was invisible to a config-only audit.

## Suggested order of attack (revised)

| # | Item | Where | Effort | Payoff |
|---|------|-------|--------|--------|
| 1 | Archive dead handoffs out of CLAUDE.md + MEMORY.md; amend the append-only policy | Claude Code / arcs-v9 | 20 min | **~80% cut to per-session base cost, forever** |
| 2 | Rewrite the orientation-chain instruction to stop mandating a 40k-token read | Claude Code / arcs-v9 | 10 min | removes the multiplier on #1 |
| 3 | Strip Sentinel connectors + downgrade to Haiku | arcs env (API) | 5 min | daily fresh-session saving |
| 4 | Subagent-for-exploration habit | Claude Code | 0 (habit) | every large search cheaper |
| 5 | `nci-scoring` skill + `/nci-commit` `/drift-check` `/ship-preview` | Claude Code | 45 min | consistency, fewer missing NCI tags |
| 6 | Prune `_STATE` sprawl + permission-list rot | arcs-v9 | 15 min | config legibility |

**Bottom line:** do the Sentinel fix — it's cheap and right. But if you only do one thing, cut the
append-forever context tax in CLAUDE.md/MEMORY.md. It's the largest, it compounds on every session, and it's
the only item on the list that gets *worse every day you don't fix it.*
