# CANON COLLISION — the Tao has two books (disjoint SSOTs)

> **Status:** `RAISED — awaiting human ruling` · **Raised:** 2026-09-27 by the tao-257 mint
> (session arcs-production-harness-arch-f4f38e). Same class as
> `CANON-COLLISION-rom-vocabulary.md`: two live stores wearing one label. Per
> [[canon-collision-escalate-never-resolve-under-write-lock]] this doc RAISES; it does not resolve.

## The finding (skeptic-verified 2026-09-27, `python3` set-diff over ids)

| Store | Rows | Id scheme | Numbering authority | Read by |
|---|---:|---|---|---|
| `_CANON/tao-proverbs.jsonl` | 256 | `tao-NNN` | **the oracle** (`_SEEDS/_oracle.json` ns `tao`) | nothing mechanical found (`grep -rl` over scripts/, skills/, artifacts/) |
| `runtime/tao/proverbs.json` | 242 | `<source>-<aspect>-<verb>` (ADR-041 grid) | the `/tao-mint` skill (no oracle) | `gen_tao_corpus.py`, `gen_tao_views.py`, `gen_tao_alchemist.py` → the front-of-house Tao pages |

**Overlap of ids: 0.** Both claim to be "the Tao SSOT". The oracle-governed book is not rendered; the
rendered book is not oracle-governed. The `/tao-mint` skill says "append to `runtime/tao/proverbs.json`";
the last canon row (`tao-256`) says it was "minted through the oracle". Both are true and they point at
different files.

## What the tao-257 mint did (additive, reversible)

Minted ONCE through the oracle (`tao` 256→257) and appended the same proverb to BOTH books under the
shared id `tao-257`, with the runtime row carrying `canon_ref` back to the canon row. This is a
cross-reference, not a merge: neither book was rewritten, no id was renumbered. It is the first row the
two books share.

## Options for the ruling (not ranked; the ruling is yours)

- **A.** Declare `_CANON/tao-proverbs.jsonl` canon (oracle-numbered, append-only) and make
  `runtime/tao/proverbs.json` a **derived projection** (ADR-065: corpus = SSOT, derived = cache) that a
  generator rebuilds from canon, carrying grid custody as fields. The renderers keep reading runtime.
- **B.** Declare `runtime/tao/proverbs.json` canon (it is what renders) and back-number its 242 rows
  through the oracle; retire the `_CANON` jsonl to `_ARCHIVE` as the molted shell.
- **C.** Keep two books deliberately (oral tradition vs grid-distilled) and give each its own oracle
  namespace and its own label, so neither is called "the Tao SSOT".

Whichever: the `/tao-mint` skill text and `_CANON/index.md` must be updated to name ONE write path,
and future mints must go through the oracle (the 255→256 drift on 2026-09-24 was this same gap).
