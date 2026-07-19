# Out-of-Band Actions — what this cloud session cannot do
**Date:** 2026-07-19 · **Companion to:** `_PATTERNS/2026-07-19-token-efficiency-audit.md`

Everything the token audit surfaced that **cannot be executed from a Claude Code cloud session scoped to
`arcs-v9`**, grouped by where it *must* be done and why it's blocked here. Ordered by leverage/urgency.
Items already handled in-repo (fix #1 context split, fix #2 orientation rewrite, patterns ledger) are NOT
listed — those are done and pushed on `claude/token-efficiency-audit-ip3l3x`.

Legend: 🔴 do-now leverage · 🟡 worth doing · 🟢 optional/hygiene

---

## A. arcs-decision-receipts environment — the Drift Sentinel (fix #3) 🔴
**Why blocked here:** the scheduled task was created via the API from the `arcs-decision-receipts`
environment. Ownership rule — a session in a *different* repo (this one) cannot read or modify it. Must be
recreated/deleted from that environment (or the API that made it).

**Cutover steps (from `sentinelrebuild.md`):**
1. Create a NEW scheduled task from the arcs-decision-receipts environment with:
   - **Name:** `ARCS Daily Drift Sentinel`
   - **Cron:** `0 4 * * *` (daily 04:00 UTC) — or `0 4 * * 1-5` weekdays-only (a solo project mostly reports
     IDLE on weekends).
   - **Model:** current **Haiku** (`claude-haiku-4-5` or newer). The job is mechanical git-log parsing —
     Sonnet is ~10× the cost for zero quality gain. Note: the old task was pinned to `claude-sonnet-4-6`;
     pinned models silently age, so pin to a current Haiku and revisit on model releases.
   - **Allowed tools:** `Bash, Read, Write, Edit, Glob, Grep` **only**.
   - **MCP connectors:** **NONE.** The old task carried all 13 (Supabase, Uber, Spotify, Canva, Gmail…) it
     could never use — every 4 AM fire paid to load their tool definitions for nothing, 365×/year.
   - **Source:** `github.com/flashesofbrilliance/arcs-decision-receipts`
   - **Notifications:** push **on** (so ⚠️/🔴 verdicts reach the phone).
   - **Prompt:** the one in `sentinelrebuild.md` (unchanged audit logic).
2. **Fire it once manually**; confirm the run output looks like a normal audit.
3. **Delete/pause the old task** `trig_01Wm372cvQHX9pvm1E8m62Vo` — from the same environment/API that made it.
4. Done: same audit, ~10× cheaper per run, zero connector dead weight.

> ⚠️ Governance note the punchlist missed: the new prompt's task 4 tells the sentinel to "keep CLAUDE.md
> under ~150 lines, prune stale sections." That is correct for the *arcs-decision-receipts* `CLAUDE.md`, but
> it directly contradicted the old append-only policy — the exact disease we just cured in *this* repo (fix
> #1). Make sure the sentinel prunes, not appends.

## B. claude.ai chat — connector hygiene (punchlist 1.2) 🟡
**Why blocked here:** MCP connectors are toggled in the claude.ai account/conversation settings, not from any
repo or from a Claude Code session.
- Disconnect the 4 connectors sitting in "unknown" auth state (**Google Drive, Spotify, Stripe, Uber**) —
  stale logins that inject tool definitions for nothing.
- Adopt **per-conversation** connector toggling: a coding chat needs Vercel + Supabase + Linear, not Canva +
  Gamma + Granola. Every enabled-but-unused connector is a standing per-message tax.

## C. Vercel dashboard — env + redeploys 🔴/🟡
**Why blocked here:** requires the Vercel dashboard UI (some of these hit a CLI bug); this session isn't
authenticated to mutate project env.
- 🟡 **Preview `DATABASE_URL`** — add via **dashboard** (Settings → Env Vars → `DATABASE_URL` → Preview →
  All branches). `vercel env add` cannot target "all preview branches" (CLI v53 bug). Tracked as ADR-006.
- 🟡 **Flip `NEXT_PUBLIC_CASE_STUDY_APPROVED=true`** (Production only) → redeploy → closes ADR-015 / issue
  #7. **Gated on the human decision in §F.**

## D. Supabase — CLI-only project + secret rotation 🔴
**Why blocked here:** (1) project `xbbpiryokswwvcrcutge` is **invisible to the Supabase MCP** (wrong org) —
its DDL/RLS needs the `supabase` **CLI**, which means a shell with that project's credentials (a *local*
Claude Code session could do it; this cloud session's MCP cannot). (2) Password rotation is a human dashboard
action.
- 🔴 **`SageTrace` RLS** — RLS is currently **disabled** on it (per live advisory); apply the ADR-008
  deny-all policy via the CLI. This is a security gap, not a token item, but it's on the same blocked path.
- 🔴 **`DATABASE_URL` rotation** — it was set manually (`vercel env add`), not integration-managed, so it
  won't auto-rotate (ADR-005 amendment). Rotate the Supabase DB password on a schedule and re-sync the env.
  **Set a calendar reminder** — there is no watchdog for this.

## E. Third-party dashboards — Resend + DNS 🟡/🟢
**Why blocked here:** external service dashboards / DNS, no repo surface.
- 🟡 **Resend MCP API key** is stale (`plugin:resend:resend` returns 400 "API key invalid") — rotate in the
  Resend dashboard and update the MCP plugin config. Blocks automated email from Claude sessions.
- 🟢 **DMARC `p=reject`** — `_dmarc.arcs.care` is at `p=quarantine`; upgrading to `p=reject` is optional
  deliverability hardening (worst case — monitor-only spam — is already resolved).

## F. Human decisions (no environment can unblock these) 🟡
- **Dan Pascone case-study approval** (ADR-015) — confirm OK to publish (even anonymized). Yes → do §C flip.
  No → skip it. This has gated ADR-013 item 1 since v1.9.0; it is a person-decision, not a build task.

---

## What I *can* still do from here (say the word)
These are in-repo and fully doable from this cloud session — listed so the local/out-of-band split is clear:
- `/nci-commit`, `/drift-check`, `/ship-preview` slash commands (`.claude/commands/*.md`) — punchlist §4.
- An `nci-scoring` skill and a reviewer subagent (`.claude/agents/reviewer.md`) — punchlist §3/§6.
- The one honest loose thread from the archive scan: verify the NCI<40 / W-field **HOLD gate** in
  `src/app/api/compass/route.ts` (PENDING.md, 2026-07-19 entry).
