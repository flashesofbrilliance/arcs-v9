#!/usr/bin/env python3
"""canon_propagation_check — a propagation sentinel for first-order sources of truth.

Canonical facts (the 7 ROM primitives, the ADR set, render-scale, Hermes constants)
live in ONE authoritative source each, but are COPIED into downstream files (CLAUDE.md,
WORLD.md, global ~/.claude config, global MEMORY.md, Hermes config). Copies rot by
neglect — e.g. CLAUDE.md carried a stale 5-primitive list while .claude/arcs-canon.md
had 7 (forensic-recoil sweep, 2026-08-27).

This does NOT author canon and NEVER picks a winner in a collision (NOTOMATION +
canon-collision-escalate). It classifies each declared sync-pair as one of:

  IN_SYNC     copy already matches its authoritative source. no-op.
  DEROT       copy is a strict SUBSET (truncation) of the authoritative source.
              MECHANICAL — safe to auto-apply (add the missing items). git-reversible.
  ESCALATE    copy CONFLICTS (has content the source lacks, or the two disagree) —
              a possible collision / net-new. NEVER auto-written. Becomes a
              stacked yes/no item in the approval queue for /canon-review.

  check        (default) classify all pairs; append a receipt to
               _INBOX/canon-propagation.jsonl; (re)write the approval queue
               _INBOX/canon-propagation-queue.json. Writes NO canon files.
  --regenerate additionally APPLY the DEROT (mechanical-mirror) class in place.
               Never touches ESCALATE items. Idempotent: writes a target only when
               it actually changed. The cron runs this ON A DEDICATED BRANCH.

Stdlib only. Exit 0 always (hook/cron-safe; drift is a receipt, not a failure).
"""
import json, glob, re, os, sys, datetime

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
HOME = os.path.expanduser("~")
INBOX = os.path.join(ROOT, "_INBOX")
RECEIPTS = os.path.join(INBOX, "canon-propagation.jsonl")
QUEUE = os.path.join(INBOX, "canon-propagation-queue.json")

# Global (cross-project) memory index for this repo's project.
GLOBAL_MEMORY = os.path.join(
    HOME, ".claude/projects/-Users-zharris-arcs-v9/memory/MEMORY.md")


# ── extractors: pull the normalized fact-set out of a file ───────────

def _read(path):
    try:
        return open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return None


def primitives_from_canon(text):
    """Authoritative 7-primitive table: rows like `| 6 | **KINTSUGI ...** | ...`."""
    out = []
    for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*\*\*([^*]+)\*\*", text, re.M):
        out.append((int(m.group(1)), m.group(2).strip().upper()))
    return [name for _, name in sorted(set(out))]


def primitives_from_list(text):
    """Downstream copy: numbered list `6. **KINTSUGI ...** — ...` under a ROM heading."""
    # scope to the ROM Primitives section if present, else whole file
    sec = re.search(r"##\s*ROM Primitives.*?(?=\n##\s|\Z)", text, re.S)
    scope = sec.group(0) if sec else text
    out = []
    for m in re.finditer(r"^\s*(\d+)\.\s*\*\*([^*]+)\*\*", scope, re.M):
        out.append((int(m.group(1)), m.group(2).strip().upper()))
    return [name for _, name in sorted(set(out))]


def classify_setpair(auth_items, copy_items):
    """Return (verdict, missing, extra). auth/copy are ordered name lists.

    DEROT (auto-applyable) fires ONLY on a non-empty STRICT SUBSET — a genuine
    partial mirror that lost items. An EMPTY copy means the file simply does not
    carry this fact; adding it would be AUTHORING, not de-rotting (NOTOMATION), so
    it is ABSENT (left alone), never auto-written.
    """
    a, c = set(auth_items), set(copy_items)
    missing = [x for x in auth_items if x not in c]   # in auth, not in copy
    extra = [x for x in copy_items if x not in a]     # in copy, not in auth (conflict)
    if extra:
        return "ESCALATE", missing, extra
    if not copy_items:
        return "ABSENT", missing, []      # file carries no such list — do not author one
    if missing:
        return "DEROT", missing, []        # non-empty partial mirror — safe to complete
    return "IN_SYNC", [], []


# ── sync-pair registry ───────────────────────────────────────────────
# Each pair: id, human title, authoritative path+extractor, copy path+extractor,
# and how DEROT is applied (an in-place patcher, or None => escalate-only).

def _patch_primitive_list(copy_path, missing, auth_names):
    """Append the missing numbered primitives to the copy's ROM list. Mechanical."""
    text = _read(copy_path)
    if text is None:
        return False
    # Insert after the highest existing `N. **...**` line in the ROM section.
    sec = re.search(r"(##\s*ROM Primitives.*?)(?=\n##\s|\Z)", text, re.S)
    if not sec:
        return False
    block = sec.group(1)
    rows = list(re.finditer(r"^\s*(\d+)\.\s*\*\*[^*]+\*\*.*$", block, re.M))
    if not rows:
        return False
    # Canonical rule/desc for the two known primitives; generic fallback otherwise.
    DESC = {
        "KINTSUGI IMMUNE SYSTEM": "repair seams visibly; no silent patching of integrity failures; show the break and the gold",
        "WRITE-LOCK": "one-way-door decisions require explicit write-lock declaration before commit; irreversibility is declared, not assumed",
    }
    start_n = int(rows[-1].group(1))
    add_lines = []
    for i, name in enumerate(missing, start=1):
        desc = DESC.get(name, "(propagated from .claude/arcs-canon.md — verify wording)")
        add_lines.append(f"{start_n + i}. **{name}** — {desc}")
    insert_at = rows[-1].end()
    new_block = block[:insert_at] + "\n" + "\n".join(add_lines) + block[insert_at:]
    new_text = text[:sec.start(1)] + new_block + text[sec.end(1):]
    if new_text != text:
        open(copy_path, "w", encoding="utf-8").write(new_text)
        return True
    return False


PAIRS = [
    {
        "id": "rom-primitives-claudemd",
        "title": "ROM primitives: .claude/arcs-canon.md → CLAUDE.md",
        "auth": (os.path.join(ROOT, ".claude/arcs-canon.md"), primitives_from_canon),
        "copy": (os.path.join(ROOT, "CLAUDE.md"), primitives_from_list),
        "patch": _patch_primitive_list,
    },
    {
        "id": "rom-primitives-global-claudemd",
        "title": "ROM primitives: .claude/arcs-canon.md → ~/.claude/CLAUDE.md",
        "auth": (os.path.join(ROOT, ".claude/arcs-canon.md"), primitives_from_canon),
        "copy": (os.path.join(HOME, ".claude/CLAUDE.md"), primitives_from_list),
        "patch": _patch_primitive_list,
    },
]


# ── ADR-067 identity check (escalate-only; no auto-fix across global memory) ──

def adr067_identity_finding():
    repo = glob.glob(os.path.join(ROOT, "_DECISIONS/ADR-067-*.md"))
    repo_slug = os.path.basename(repo[0])[len("ADR-067-"):-3] if repo else None
    gm = _read(GLOBAL_MEMORY)
    mem_line = None
    if gm:
        for line in gm.splitlines():
            if "ADR-067" in line:
                mem_line = line.strip()
                break
    if not repo_slug or not mem_line:
        return None
    # tokens of the repo slug that should appear in the memory line
    toks = [t for t in re.split(r"[-_]", repo_slug) if len(t) > 3]
    hit = sum(1 for t in toks if t.lower() in mem_line.lower())
    mismatch = (len(toks) > 0 and hit == 0)
    return {
        "id": "adr-067-identity",
        "title": "ADR-067 identity: repo _DECISIONS vs global MEMORY.md",
        "verdict": "ESCALATE" if mismatch else "IN_SYNC",
        "repo": f"ADR-067-{repo_slug}",
        "global_memory": mem_line,
        "detail": ("global MEMORY.md describes ADR-067 differently from the repo file "
                   "— human must reconcile which ADR-067 is authoritative"),
    } if mismatch else None


# ── cross-harness invariant sync (Hermes USER.md <-> Claude AGENTS.md) ──
# These operating files are PROSE, not extractable lists, so this is a presence
# check, not a list-completion: a shared invariant present in one harness's file
# but missing from the other's = drift -> ESCALATE (never auto-written).

HERMES_USER = os.path.join(HOME, ".hermes/memories/USER.md")
# Claude's operating surface is the THREE always-loaded files, not AGENTS.md alone
# (NOTOMATION etc. live in WORLD.md / CLAUDE.md). Compare against their union.
CLAUDE_SURFACE = [os.path.join(ROOT, f) for f in ("AGENTS.md", "WORLD.md", "CLAUDE.md")]
SHARED_INVARIANTS = {
    "NOTOMATION": ["notomation"],
    "oracle-first numbering": ["oracle"],
    "non-sycophantic / bear-case-first": ["sycophan", "bear case", "bear-case"],
    "audit-before-acting": ["audit before", "audit first", "check git log", "audit adr"],
}


def invariant_sync_findings():
    h = _read(HERMES_USER)
    parts = [_read(p) or "" for p in CLAUDE_SURFACE]
    c = "\n".join(parts)
    if h is None or not c:
        return []
    hl, cl = h.lower(), c.lower()
    out = []
    for name, markers in SHARED_INVARIANTS.items():
        in_h = any(m in hl for m in markers)
        in_c = any(m in cl for m in markers)
        if in_h != in_c:
            claude_label = "Claude always-loaded files (AGENTS/WORLD/CLAUDE.md)"
            missing = "Hermes USER.md" if not in_h else claude_label
            out.append({
                "id": f"invariant-{name.split()[0].lower()}",
                "title": f"cross-harness invariant drift: '{name}'",
                "verdict": "ESCALATE",
                "detail": (f"shared operating invariant '{name}' is present in "
                           f"{claude_label if in_c else 'Hermes USER.md'} but MISSING from "
                           f"{missing} — the two harnesses will behave differently on the monorepo"),
            })
    return out


# ── main ─────────────────────────────────────────────────────────────

def main():
    regen = "--regenerate" in sys.argv
    os.makedirs(INBOX, exist_ok=True)
    findings, queue, applied = [], [], []

    for p in PAIRS:
        auth_text = _read(p["auth"][0])
        copy_text = _read(p["copy"][0])
        if auth_text is None or copy_text is None:
            findings.append({"id": p["id"], "verdict": "SKIP",
                             "reason": "auth or copy path missing"})
            continue
        auth_items = p["auth"][1](auth_text)
        copy_items = p["copy"][1](copy_text)
        verdict, missing, extra = classify_setpair(auth_items, copy_items)
        f = {"id": p["id"], "title": p["title"], "verdict": verdict,
             "missing": missing, "conflict": extra}
        findings.append(f)
        if verdict == "DEROT":
            if regen and p.get("patch"):
                if p["patch"](p["copy"][0], missing, auth_items):
                    applied.append(f"{p['id']}: +{', '.join(missing)}")
            else:
                queue.append({"id": p["id"], "kind": "mechanical", "default": "yes",
                              "title": p["title"],
                              "proposal": f"add {', '.join(missing)} to {os.path.relpath(p['copy'][0], ROOT) if p['copy'][0].startswith(ROOT) else p['copy'][0]}"})
        elif verdict == "ESCALATE":
            queue.append({"id": p["id"], "kind": "judgment", "default": "no",
                          "title": p["title"],
                          "proposal": f"CONFLICT: copy has {extra} not in authoritative source — human ruling required"})

    adr = adr067_identity_finding()
    if adr:
        findings.append(adr)
        queue.append({"id": adr["id"], "kind": "judgment", "default": "no",
                      "title": adr["title"], "proposal": adr["detail"]})

    for inv in invariant_sync_findings():
        findings.append(inv)
        queue.append({"id": inv["id"], "kind": "judgment", "default": "no",
                      "title": inv["title"], "proposal": inv["detail"]})

    drifted = [f for f in findings if f.get("verdict") in ("DEROT", "ESCALATE")]
    verdict = "DRIFT" if drifted else "OK"
    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    receipt = {"ts": ts, "type": "canon-propagation-receipt", "verdict": verdict,
               "findings": findings, "applied": applied}
    with open(RECEIPTS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(receipt, ensure_ascii=False) + "\n")
    json.dump({"ts": ts, "verdict": verdict, "items": queue},
              open(QUEUE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"canon-propagation: {verdict} · {len(drifted)} drifted pair(s) · "
          f"{sum(1 for q in queue if q['kind']=='mechanical')} mechanical / "
          f"{sum(1 for q in queue if q['kind']=='judgment')} judgment · "
          f"queue -> _INBOX/canon-propagation-queue.json")
    if regen:
        print(f"canon-propagation: --regenerate applied {len(applied)} mechanical de-rot(s)"
              + (f" -> {'; '.join(applied)}" if applied else " (none; mirrors already fresh)")
              + " · judgment items stay in the queue")
    else:
        print("canon-propagation: receipt-only (mechanical de-rots staged in queue; "
              "run --regenerate to apply them; judgment items are human-owned)")


if __name__ == "__main__":
    main()
