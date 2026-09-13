#!/usr/bin/env python3
"""
Patch _handoff.json: remove FM-E3.3 (disproven — _alignments dispatches correctly)
and reframe FM-E3.1 (root cause is empty llmOutput on disk, not ReadPath gap).
Updates consolidated.integrity_bugs, session_context.md, session_context.json,
memory_wiki.md, memory_wiki.json in one pass.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HP = Path("/Users/zharris/arcs-v9/_handoff.json")
raw = HP.read_text()
h = json.loads(raw)
tl = h["land_the_plane"]

# ── 1. consolidated.integrity_bugs (JSON array) ────────────────────────────
new_bugs = [
    {
        "id": "FM-E3.1",
        "title": "8/9 pairs show 'no' LLM reference — root cause is empty llmOutput on disk",
        "detail": "SONIC_REFERENCE_KEY/LLM_REFERENCE_PROPAGATED written on WritePath but not propagated to ReadPath was a working hypothesis. Ground truth check (2026-08-29): 8/9 pairs have empty llmOutput={} on disk because the store was never populated with real compass output. The 8/9 'no' count reflects missing data, not a ReadPath gap. No separate ReadPath propagation bug confirmed.",
        "fix_direction": "Drive real compass POSTs (needs ANTHROPIC_API_KEY) to populate llmOutput on 8/9 pairs, then re-check. If real llmOutput populated and ReadPath still shows 'no', then investigate propagation."
    }
]
tl["consolidated"]["what_landed"]["integrity_bugs"] = new_bugs

# ── 2. session_context.md ──────────────────────────────────────────────────
md = tl["session_context"]["md"]

# Replace the known-bugs section
old_block = """## Known integrity bugs (persistence.py)

1. **FM-E3.1** — LlmReference ReadPath not propagated. 8/9 pairs show "no" LLM reference.
2. **FM-E3.3** — `_alignments` always uses `_SAGE_SUBTASKS` regardless of operator.

Both distort the sound: all operators sound like SAGE, almost all pairs look like no LLM reference. User approved repairing both."""
new_block = """## Known issue (persistence.py)

**FM-E3.1 (investigated, root cause reframed 2026-08-29)** — 8/9 pairs show "no" LLM reference. Earlier hypothesis was a ReadPath propagation gap (SONIC_REFERENCE_KEY/LLM_REFERENCE_PROPAGATED not propagated from WritePath to ReadPath). Ground truth check: 8/9 pairs have empty `llmOutput={}` on disk because the store was never populated with real compass output. The count reflects missing data, not a ReadPath bug. No separate ReadPath propagation bug confirmed. Fix: drive real compass POSTs (needs ANTHROPIC_API_KEY) to populate llmOutput, then re-check.

**FM-E3.3 DISPROVEN (2026-08-29)** — earlier hypothesis that `_alignments` always uses `_SAGE_SUBTASKS` regardless of operator. Verified false: `_alignments` dispatches correctly to per-operator subtask maps (SAGE→5 SAGE subtasks, LAB→5 LAB subtasks, BAR→5 BAR subtasks, KINTSUGI→5 KINTSUGI subtasks with different keys). Removed from the bug list."""

if old_block in md:
    md = md.replace(old_block, new_block)
    print("session_context.md: replaced known-bugs block")
else:
    print("session_context.md: old block not found verbatim — attempting regex fallback")
    # Fallback: replace the two bullet points
    md = re.sub(
        r"1\. \*\*FM-E3\.1\*\* — LlmReference ReadPath not propagated\. 8/9 pairs show .no. LLM reference\.",
        "**FM-E3.1 (investigated, root cause reframed 2026-08-29)** — 8/9 pairs show \"no\" LLM reference. Earlier hypothesis was a ReadPath propagation gap (SONIC_REFERENCE_KEY/LLM_REFERENCE_PROPAGATED not propagated from WritePath to ReadPath). Ground truth check: 8/9 pairs have empty `llmOutput={}` on disk because the store was never populated with real compass output. The count reflects missing data, not a ReadPath bug. No separate ReadPath propagation bug confirmed. Fix: drive real compass POSTs (needs ANTHROPIC_API_KEY) to populate llmOutput, then re-check.",
        md,
    )
    md = re.sub(
        r"2\. \*\*FM-E3\.3\*\* — `_alignments` always uses `_SAGE_SUBTASKS` regardless of operator\.",
        "**FM-E3.3 DISPROVEN (2026-08-29)** — earlier hypothesis that `_alignments` always uses `_SAGE_SUBTASKS` regardless of operator. Verified false: `_alignments` dispatches correctly to per-operator subtask maps (SAGE→5 SAGE subtasks, LAB→5 LAB subtasks, BAR→5 BAR subtasks, KINTSUGI→5 KINTSUGI subtasks with different keys). Removed from the bug list.",
        md,
    )
    print("session_context.md: regex fallback applied")

# Remove the "Both distort the sound" sentence if present (no longer accurate)
md = md.replace(
    "\nBoth distort the sound: all operators sound like SAGE, almost all pairs look like no LLM reference. User approved repairing both.",
    ""
)

# Also update the "What's NOT yet done" section — remove FM-E3.3 from the repair item
md = md.replace(
    "- Repair FM-E3.1 + FM-E3.3 in persistence.py",
    "- Repair FM-E3.1 (drive real compass POSTs to populate llmOutput, then re-check ReadPath if still showing 'no') in persistence.py — FM-E3.3 disproven 2026-08-29"
)

tl["session_context"]["md"] = md

# ── 3. session_context.json ────────────────────────────────────────────────
j = tl["session_context"]["json"]
old_json_bugs = [
    "FM-E3.1: LlmReference ReadPath not propagated — 8/9 pairs show 'no' LLM reference",
    "FM-E3.3: _alignments always uses _SAGE_SUBTASKS — LAB/BAR/KINTSUGI get 0 alignment on all 5 subtasks"
]
new_json_bugs = [
    "FM-E3.1 (investigated, root cause reframed 2026-08-29): 8/9 pairs show 'no' LLM reference — root cause is empty llmOutput={} on disk (store never populated with real compass output), not a ReadPath gap. Fix: drive real compass POSTs to populate llmOutput, then re-check."
]
# Only replace if the old list matches exactly
if j.get("integrity_bugs") == old_json_bugs:
    j["integrity_bugs"] = new_json_bugs
    print("session_context.json: replaced integrity_bugs list")
else:
    print(f"session_context.json: unexpected integrity_bugs = {j.get('integrity_bugs')}")

# Update next_moves: remove "Repair FM-E3.1 + FM-E3.3" and replace
nm = j.get("next_moves", [])
if "Repair FM-E3.1 + FM-E3.3 in persistence.py" in nm:
    idx = nm.index("Repair FM-E3.1 + FM-E3.3 in persistence.py")
    nm[idx] = "Repair FM-E3.1 (drive real compass POSTs to populate llmOutput, then re-check ReadPath if still showing 'no') in persistence.py — FM-E3.3 disproven 2026-08-29"
    j["next_moves"] = nm
    print("session_context.json: updated next_moves")

tl["session_context"]["json"] = j

# ── 4. memory_wiki.md ──────────────────────────────────────────────────────
wmd = tl["memory_wiki"]["md"]
wmd_old_bugs = """### Known issues

1. **FM-E3.1** — LlmReference ReadPath not propagated. 8/9 pairs show "no" LLM reference.
2. **FM-E3.3** — `_alignments` always uses `_SAGE_SUBTASKS` regardless of operator. Non-SAGE operators get 0 alignment on all 5 subtasks.

Both distort the sound: all operators sound like SAGE, almost all pairs look like no LLM reference. User approved repairing both."""
wmd_new_bugs = """### Known issue (investigated, root cause reframed 2026-08-29)

**FM-E3.1** — 8/9 pairs show "no" LLM reference. Earlier hypothesis: ReadPath propagation gap (SONIC_REFERENCE_KEY/LLM_REFERENCE_PROPAGATED not propagated from WritePath to ReadPath). Ground truth check: 8/9 pairs have empty `llmOutput={}` on disk because the store was never populated with real compass output. The count reflects missing data, not a ReadPath bug. No separate propagation bug confirmed. Fix: drive real compass POSTs (needs ANTHROPIC_API_KEY) to populate llmOutput, then re-check.

**FM-E3.3 DISPROVEN (2026-08-29)** — earlier hypothesis that `_alignments` always uses `_SAGE_SUBTASKS`. Verified false: dispatches correctly to per-operator subtask maps. Removed from the bug list."""

if wmd_old_bugs in wmd:
    wmd = wmd.replace(wmd_old_bugs, wmd_new_bugs)
    print("memory_wiki.md: replaced known-issues block")
else:
    print("memory_wiki.md: old block not found verbatim — attempting regex fallback")
    wmd = re.sub(
        r"1\. \*\*FM-E3\.1\*\* — LlmReference ReadPath not propagated\. 8/9 pairs show .no. LLM reference\.",
        "**FM-E3.1 (investigated, root cause reframed 2026-08-29)** — 8/9 pairs show \"no\" LLM reference. Earlier hypothesis: ReadPath propagation gap (SONIC_REFERENCE_KEY/LLM_REFERENCE_PROPAGATED not propagated from WritePath to ReadPath). Ground truth check: 8/9 pairs have empty `llmOutput={}` on disk because the store was never populated with real compass output. The count reflects missing data, not a ReadPath bug. No separate propagation bug confirmed. Fix: drive real compass POSTs (needs ANTHROPIC_API_KEY) to populate llmOutput, then re-check.",
        wmd,
    )
    wmd = re.sub(
        r"2\. \*\*FM-E3\.3\*\* — `_alignments` always uses `_SAGE_SUBTASKS` regardless of operator\. Non-SAGE operators get 0 alignment on all 5 subtasks\.",
        "**FM-E3.3 DISPROVEN (2026-08-29)** — earlier hypothesis that `_alignments` always uses `_SAGE_SUBTASKS`. Verified false: dispatches correctly to per-operator subtask maps. Removed from the bug list.",
        wmd,
    )
    wmd = wmd.replace(
        "\nBoth distort the sound: all operators sound like SAGE, almost all pairs look like no LLM reference. User approved repairing both.",
        ""
    )
    print("memory_wiki.md: regex fallback applied")

# Update next_session_first_move in memory_wiki.md
wmd = wmd.replace(
    "- Repair FM-E3.1 + FM-E3.3 in persistence.py",
    "- Repair FM-E3.1 (drive real compass POSTs to populate llmOutput, then re-check ReadPath if still showing 'no') in persistence.py — FM-E3.3 disproven 2026-08-29"
)

tl["memory_wiki"]["md"] = wmd

# ── 5. memory_wiki.json ────────────────────────────────────────────────────
wj = tl["memory_wiki"]["json"]
wj_old = [
    "FM-E3.1: LlmReference ReadPath not propagated (8/9 pairs show 'no')",
    "FM-E3.3: _alignments always uses _SAGE_SUBTASKS (non-SAGE get 0 alignment)"
]
wj_new = [
    "FM-E3.1 (investigated, root cause reframed 2026-08-29): 8/9 pairs show 'no' LLM reference — root cause is empty llmOutput={} on disk (store never populated with real compass output), not a ReadPath gap. Fix: drive real compass POSTs to populate llmOutput, then re-check."
]
if wj.get("integrity_bugs") == wj_old:
    wj["integrity_bugs"] = wj_new
    print("memory_wiki.json: replaced integrity_bugs list")
else:
    print(f"memory_wiki.json: unexpected integrity_bugs = {wj.get('integrity_bugs')}")

# Update next_session_first_move in memory_wiki.json
wjnfm = wj.get("next_session_first_move", [])
if "Repair FM-E3.1 + FM-E3.3 in persistence.py" in wjnfm:
    idx = wjnfm.index("Repair FM-E3.1 + FM-E3.3 in persistence.py")
    wjnfm[idx] = "Repair FM-E3.1 (drive real compass POSTs to populate llmOutput, then re-check ReadPath if still showing 'no') in persistence.py — FM-E3.3 disproven 2026-08-29"
    wj["next_session_first_move"] = wjnfm
    print("memory_wiki.json: updated next_session_first_move")

tl["memory_wiki"]["json"] = wj

# ── Write back ─────────────────────────────────────────────────────────────
out = json.dumps(h, indent=2, ensure_ascii=False) + "\n"
HP.write_text(out)
print(f"\nWrote {HP} ({len(out)} bytes)")

# ── Verify ──────────────────────────────────────────────────────────────────
h2 = json.loads(HP.read_text())
bugs = h2["land_the_plane"]["consolidated"]["what_landed"]["integrity_bugs"]
print(f"\nVerification — consolidated.integrity_bugs: {len(bugs)} items")
for b in bugs:
    print(f"  {b['id']}: {b['title'][:80]}...")
print()
print("session_context.md integrity_bugs section present:", "FM-E3.3 DISPROVEN" in h2["land_the_plane"]["session_context"]["md"])
print("memory_wiki.md integrity_bugs section present:", "FM-E3.3 DISPROVEN" in h2["land_the_plane"]["memory_wiki"]["md"])
print("FM-E3.3 absent from all bug lists:", all(
    "FM-E3.3" not in b.get("id", "") and "FM-E3.3" not in b.get("title", "")
    for b in bugs
))
