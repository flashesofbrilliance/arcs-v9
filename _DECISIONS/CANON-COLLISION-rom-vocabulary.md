# CANON COLLISION — ROM Vocabulary (three coexisting axis-sets)

> **Status:** `RESOLVED — Option A (human ruling, 2026-08-28)` · **Raised:** 2026-08-27 by the
> forensic-recoil sweep, skeptic-verified.
>
> **RULING (Zach, 2026-08-28):** Option A — declare one authoritative axis and subordinate the
> others. The **7 ROM Primitives** (`.claude/arcs-canon.md`) are CANON. The **6 execution laws**
> (`runtime/specs/ARCS-v9-ROM.md`) are relabeled **ROM behavioral laws (derived)**. The **7 axioms**
> (`_CANON/book-ii/part-ii-rom-axioms.md`) are relabeled **epistemic foundations**. A single authority
> index was created at `runtime/specs/ROM-AXIS-INDEX.md`, and tier banners were added to all three
> source files pointing to it. The CLAUDE.md 5→7 truncation was already de-rotted 2026-08-27 (doc-rot,
> not part of the ruling). This unblocks the Norse ROM candidates' numbering (canon axis now declared).

## The finding

Multiple, *different* "ROM" vocabularies are live in arcs-v9 simultaneously. Two are the **same axis**
in conflict (a stale truncation — resolvable as doc-rot). The rest are **different axes** wearing the
same "ROM" label — a genuine collision that needs a ruling on which is authoritative and how they nest.

All counts/paths below are skeptic-verified against the live repo (2026-08-27). The original sweep
report mis-cited several of these; this doc supersedes those citations.

| Set | Live location | Count | Named items | Kind |
|---|---|---:|---|---|
| **7 PRIMITIVES** (authoritative) | `.claude/arcs-canon.md:65–75` | 7 | 1 NOTOMATION · 2 HYPERSPHERE · 3 HYPERSTITION · 4 GOLDEN INCHWORM · 5 ORTHOGONAL ECHO · **6 KINTSUGI** · **7 WRITE-LOCK** | constitutional primitives |
| **5 PRIMITIVES** (stale copy) | `CLAUDE.md:58–63` | 5 | drops KINTSUGI + WRITE-LOCK | **doc rot** — truncation of the 7-list |
| **6 EXECUTION LAWS** | `runtime/specs/ARCS-v9-ROM.md:14–29` | 6 | ROM-1 Clarity-before-Curvature · ROM-2 Agency-over-Automation · ROM-3 Min-Steps · ROM-4 Kairos · ROM-5 Drift-Sentinel · ROM-6 Stable-True-North | **different axis** — behavioral execution laws, "draft ROM starter" |
| **7 AXIOMS (I–VII)** | `_CANON/book-ii/part-ii-rom-axioms.md` | 7 | I Decisions-Are-Bets · II NOTOMATION · III Time-Quality-First-Class · IV Structure-Earned · V Repair-Visibly · VI History-is-Teacher · VII Irreversibility-Declared | **different axis** — epistemic axioms |

Note the partial mapping across axes (evidence they are *views* of one thing, not four unrelated lists):
Axiom II ↔ Primitive 1 (NOTOMATION); Axiom V (Repair Visibly) ↔ Primitive 6 (Kintsugi); Axiom VII
(Irreversibility Declared) ↔ Primitive 7 (Write-Lock); Axiom III (Time Quality) ↔ the
`time-quality-attribution-rom.json` spec. The 6 execution-laws do NOT cleanly map — they are a
behavioral layer, not a primitive/axiom layer.

## Two problems, separated

1. **Doc rot (resolvable, NOT the collision).** `CLAUDE.md`'s 5-list is a stale truncation of the
   authoritative 7-primitive table in `.claude/arcs-canon.md`. **De-rotted 2026-08-27**: KINTSUGI (#6)
   and WRITE-LOCK (#7) added back to `CLAUDE.md`. This was alignment to an existing authoritative
   in-repo source, not a ruling.
2. **The genuine collision (needs a ruling).** Three *different-axis* sets — 7 primitives / 6 execution
   laws / 7 epistemic axioms — all called "ROM," with no single doc declaring how they nest. A reader
   asking "what are the ROM primitives?" gets three different answers depending on which file they open.

## Verified-as-prose caveats (do not propagate as implemented fact)
- **WRITE-LOCK is prose-only.** No git hook enforces non-fast-forward; the "git-is-the-write-lock"
  framing is a metaphor, not a wired mechanism.
- Nothing mechanically reconciles the four files above — the CLAUDE.md truncation went uncaught until
  this sweep. A drift-lint that diffs the primitive lists across `.claude/arcs-canon.md`, `CLAUDE.md`,
  and `part-ii` would have caught it (candidate wiring, not built).

## Options for the ruling (pick one; do not auto-apply)
- **A. Declare one authoritative axis + subordinate the others.** e.g. the 7 primitives are canon;
  the 6 execution-laws become "ROM behavioral laws (derived)"; the 7 axioms become "epistemic
  foundations." Cross-link all three from one index.
- **B. Rename to end the label collision.** Keep all three but stop calling all of them "ROM" — e.g.
  PRIMITIVES / EXECUTION-LAWS / AXIOMS as distinct named tiers.
- **C. Merge the two 7-lists** (primitives ↔ axioms map cleanly on 3 of 7) into one table, keep the
  6 execution-laws as the separate behavioral layer.

## Do-not-do
- Do not silently edit `runtime/specs/ARCS-v9-ROM.md` or `part-ii` to "match" — that is resolving a
  collision under write-lock.
- Do not mint a new numbered primitive/axiom while this is open (blocks ratifying the Norse ROM
  candidates' numbering — see `runtime/specs/ROM-CANDIDATES-norse-witness.md`).
