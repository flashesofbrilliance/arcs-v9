---
name: fold
description: Reverse-ATG session decomposition. When a session has grown dense with threads from more than one domain, sweep its residue, sort by domain gravity, and re-serialize each cluster into a self-contained composed session (spawn_task chip) whose context is only the load-bearing edges. Use at natural density points ("lets stack X into one consolidated new session"), before a handoff on a sprawling session, or whenever open threads from 2+ domains are interleaving. The folding half of the induced-backlog doctrine.
---

# /fold — decompose the session, re-serialize at load-bearing edges

> Forward-ATG grows tributaries out of one question. /fold runs it in REVERSE: collect the
> tributaries a dense session threw off, sort them by domain gravity, and compose each cluster
> into a fresh session that boots on clean priors. Proven by hand 2026-08-26 (PRL close-out,
> Ahmed 60-second read, Yuri Sep-14 prep - all executed/queued as composed sessions while the
> trunk stayed clean). Doctrine: [[seed-pattern-induced-backlog]] + fork-when-dense memory.

## Step 1 — sweep the residue
Enumerate this session's open threads: unfinished work items, decisions taken but not executed,
sends owed, obligations logged. Sources: the conversation itself, `_QUEUE/induced-backlog.jsonl`,
any register built this session. EXCLUDE threads already owned by a running composed session -
check pending/running chips and `/tasks` first; never duplicate a live session's scope.

## Step 2 — sort by domain gravity
Cluster by counterpart/engagement/product-area, not by task type. A cluster earns its own
session when it has 2+ items sharing SSOTs, or one item too heavy for trunk residue. Singleton
light items stay on the trunk or go to the induced backlog as items, not sessions.

## Step 3 — compose each session at the load-bearing edges
Each chip prompt (spawn_task; title = imperative verb phrase) must be SELF-CONTAINED:
1. **Ground truth as-of block** — facts VERIFIED this session, with dates ("guard v5 live,
   verified 2026-08-26"), so the new session never re-derives or re-trusts stale memory.
2. **SSOT paths** — the files that ARE the state (backlog items, kit READMEs, memory shards,
   recoil JSONs). Point, never inline what a file already holds.
3. **Verified routes** — which tool reaches which surface, with quirks (auth ids, classifier
   limits, bulk endpoints). Routes drift; date them.
4. **Gates** — ADR-068 blocking prints (ex-ante-before-send, gauntlets, payment gates) AND
   consent gates. Consent gates ride INTO the prompt; a composed session inherits the rule,
   never the authorization. Draft-first for anything outward.
5. **Corrections** — any stale-memory fixes discovered this session that the cluster touches
   (the pulse-check class), so the new session doesn't reimport dead claims.
6. **Timing guard** if the session runs better later ("best run Sep 10-12 because X; if
   earlier, say so and ask").
7. **Close protocol** — receipts for everything closed, backlog status updates, handoff per
   CLAUDE.md policy.

## Step 4 — fold back to the trunk
After spawning: update `_QUEUE/induced-backlog.jsonl` item statuses/ownership, note the spawned
sessions in the handoff, and keep the trunk clean for cross-domain work. When a composed
session completes (task notification), fold its receipts back: memory updates, backlog closes,
drift fixes. The trunk is the integral; composed sessions are the derivatives.

## Guardrails
- NOTOMATION: /fold induces execution, never consent - a chip is a suggestion the human starts.
- One domain per chip. A chip needing two SSOers from unrelated domains is two chips.
- Ground truth in prompts comes from THIS session's verification, never from memory alone.
- Concurrent-writer awareness: composed sessions may write memory/PRs in parallel - trunk
  merges additively (append/extend), never clobbers (see the 2026-08-27 footer-merge precedent).
