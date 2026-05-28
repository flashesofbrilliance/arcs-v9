---
id: ADR-010
title: Rename arcs-dewy Package Directory to Resolve Module Shadowing
status: DECIDED
date: 2026-05-27
deciders: [Zach Harris]
nci: 82
gate: GREEN
---

## D — The Decision

**Sharp question:** How do we resolve the Python naming collision where `arcs_dewy.py` (flat file at repo root) shadows `arcs-dewy/` (package directory), causing `_HAS_DEWY = False` in the bridge and killing all live ReceiptObject construction?

---

## E — Entity / System

- `arcs_dewy.py` — flat file at `/Users/zharris/A.R.C.S./arcs_dewy.py`
- `arcs-dewy/` — package directory at `/Users/zharris/A.R.C.S./arcs-dewy/` (hyphenated, not importable directly)
- `arcs_primitives_bridge.py` — imports `from arcs_dewy.schema.receipt import ReceiptObject`; currently falls back to dict (`_HAS_DEWY = False`) because flat file wins
- Any future code importing `ReceiptObject` or `OnPurposeLabel` from `arcs_dewy`

> **Cross-repo note:** This ADR is tracked in `arcs-v9/_DECISIONS/` but the change executes entirely in `/Users/zharris/A.R.C.S./`. No arcs-v9 files are modified.

---

## W — Window

**Horizon:** WEEK  
**Revisit trigger:** If `arcs-dewy` is extracted into a standalone installable package (pip/PyPI), re-evaluate whether the in-repo path is still needed at all.

---

## Context

Python's import system resolves `arcs_dewy` to the first match on `sys.path`. Because `arcs_dewy.py` (a flat module) exists at repo root and the hyphenated `arcs-dewy/` directory is not directly importable (hyphens are not valid in Python identifiers), the bridge sets `_HAS_DEWY = False` and returns dicts instead of live `ReceiptObject` instances.

This means:
1. Schema validation is bypassed on all bridge-produced receipts
2. `ReceiptObject`-typed function signatures silently receive dicts
3. Phase 7 receipt infrastructure can't progress until resolved

**Perplexity research summary:**
- The canonical Python fix is direct: rename the conflicting file/directory so there is no ambiguity
- A thin compatibility shim (`arcs_dewy_legacy.py`) can satisfy any code that still imports from the old flat file without forking the import tree
- `importlib.import_module` workarounds exist but add complexity with no benefit here — no external consumers of `arcs_dewy.py` exist yet
- The hyphen → underscore convention (`arcs-dewy` → `arcs_dewy_pkg`) is the community standard for packages with hyphenated distribution names

---

## Options Considered

### Option A — Rename `arcs-dewy/` → `arcs_dewy_pkg/`, update all imports
- Rename directory; update `arcs_primitives_bridge.py` import to `from arcs_dewy_pkg.schema.receipt import ReceiptObject`
- **Pros:** Clean, unambiguous, standard Python convention; `arcs_dewy.py` flat file is undisturbed if it's needed for something else
- **Cons:** All future imports use `arcs_dewy_pkg`, not `arcs_dewy`; requires audit of all import sites

### Option B — Delete `arcs_dewy.py` flat file, rename `arcs-dewy/` → `arcs_dewy/`
- Remove the collision entirely; directory becomes the canonical `arcs_dewy` package
- **Pros:** Final-state clean — `from arcs_dewy.schema.receipt import ReceiptObject` works with zero bridge changes; no `_pkg` suffix confusion
- **Cons:** `arcs_dewy.py` contents (if any are used) must be audited and migrated first

### Option C — `importlib` workaround in bridge, no rename
- Keep both files, use `importlib.import_module` with explicit path manipulation
- **Pros:** No file moves
- **Cons:** Fragile, non-obvious, adds complexity with no upside; violates "minimum steps to coherence"

---

## Decision

**Chosen:** Option B (with pre-execution finding)

**Rationale:** Option B produces the cleanest end state and the `from arcs_dewy.schema.receipt import ReceiptObject` import in the bridge works with zero changes. Option A uses `_pkg` suffix which leaks into all future code.

**Pre-execution audit result (2026-05-27):**
- `arcs_dewy.py` contains live `DEWYLog` / `DEWYEntry` dataclasses — Phase 6 crystallization log schema. Not a stub.
- Zero callers of `DEWYLog`/`DEWYEntry` outside the flat file itself (grep confirmed).
- Execution sequence: rename `arcs_dewy.py` → `arcs_dewy_log.py` first (preserving content), then rename `arcs-dewy/` → `arcs_dewy/`. No import sites break.

**Trade-offs accepted:** `DEWYLog`/`DEWYEntry` live at `arcs_dewy_log.py` (not inside the package) until a future DEWY consolidation pass.

---

## Y — Conviction

**Polarity:** GREEN  
**Conviction:** HIGH  
**Stability:** STABLE

**Loki test:** (Pre-execution risk, now mitigated) If `arcs_dewy.py` had callers outside the file, deleting it would break them silently — confirmed zero via grep. Residual risk: a future contributor importing `arcs_dewy` may expect `DEWYLog` (the old flat file) and get `ReceiptObject` instead. Mitigation: `arcs_dewy_log.py` header carries a rename notice; any new code importing `arcs_dewy` will correctly get the package.

---

## Consequences

- `_HAS_DEWY` in bridge becomes `True`; live `ReceiptObject` construction restored
- Schema validation is enforced on all bridge-produced receipts
- `arcs_primitives_bridge.py` needs no import changes (Option B)
- Phase 7 receipt-core work unblocked
- `arcs_dewy_log.py` has zero callers; may be promoted into `arcs_dewy/crystallization.py` in a future DEWY consolidation pass (no urgency — DEWYLog is not on the Phase 7 critical path)

**Implementation steps (audit complete — safe to execute):**
1. `mv arcs_dewy.py arcs_dewy_log.py` — rename flat file, preserve DEWYLog/DEWYEntry
2. `mv arcs-dewy arcs_dewy` — rename package directory
3. `python -c "from arcs_primitives_bridge import _HAS_DEWY; print(_HAS_DEWY)"` — verify True
4. Update bridge comment (lines 1–20) — collision resolved
5. `git add -A && git commit` with this ADR

**Implementation pointer:** `arcs_primitives_bridge.py` lines 1–20 (naming collision note), `arcs_dewy.py` (flat file to audit/delete)

---

## Linked receipts / ADRs

- ADR-007 — Prisma migration strategy (relates to: schema infrastructure discipline)
- `arcs_primitives_bridge.py` — bridge that exposed this collision
