#!/usr/bin/env python3
"""
generate_arcs_operator_data.py
Builds .hermes/data/arcs_operators.json + _ids.json + _brief.json
from the live operators/ library + arcs-operator-table SKILL.md.

Run from repo root:
  python scripts/generate_arcs_operator_data.py
"""

from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("/Users/zharris/arcs-v9")
OP_DIR = REPO / "operators"
SKILL_FILE = Path("/Users/zharris/.hermes/profiles/arcs/skills/arcs-operator-table/SKILL.md")
OUT_DIR = Path("/Users/zharris/.hermes/profiles/arcs/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── helpers ──────────────────────────────────────────────────────────────────

def wc_l(path: Path) -> int:
    try:
        out = subprocess.check_output(["wc", "-l", str(path)], text=True).strip()
        return int(out.split()[0])
    except Exception:
        return -1


def read_header(path: Path, lines: int = 60) -> str:
    try:
        txt = path.read_text(encoding="utf-8")
        return "\n".join(txt.splitlines()[:lines])
    except Exception:
        return ""


def parse_python_header(path: Path) -> Dict[str, Any]:
    """
    Pull the structured fields we want for a .py operator file:
      FILE, NAME, PHASE, PURPOSE (from Summary/role/how-to lines),
      STATUS, CLI, SOURCE, SOURCE_NAME.

    We deliberately keep this conservative: only extracted strings go in.
    """
    header = read_header(path, 70)
    result: Dict[str, Any] = {"source": path.name}

    # FILE — basename
    result["file"] = path.name

    # NAME — first non-trivial title line
    for line in header.splitlines():
        s = line.strip()
        if s and not s.startswith(("\"\"\"", "#", "from", "import", "=", "ARCS v9")):
            result["name"] = s
            break

    # PHASE — first 'Phase N: ...' match
    pm = re.search(r"Phase\s+(\d+|[A-Za-z0-9]+)\s*:\s*(.+)", header)
    if pm:
        result["phase"] = f"Phase {pm.group(1)}".strip()
        result["phase_detail"] = pm.group(2).strip()

    # PURPOSE — try Summary/role/usecase/canonical reference / description lines
    purpose_lines: List[str] = []
    for line in header.splitlines():
        s = line.strip()
        if not s:
            continue
        low = s.lower()
        if any(k in low for k in ["summary", "role in pipeline", "usecase", "canonical reference",
                                   "description", "purpose", "design", "semantics", "architecture",
                                   "design principle", "design invariant", "sprint status"]):
            # strip the field-name prefix for cleaner output
            m = re.match(r"^\s*(?:Summary|Role in pipeline|UseCase|Canonical reference|Description|Purpose|Architecture|Design principle|Design invariant|Sprint status)\s*[:\-]?\s*(.+)", s)
            if m:
                purpose_lines.append(m.group(1).strip())
            else:
                purpose_lines.append(s.lstrip(":- ").strip())
        elif low.startswith("notation rule") or low.startswith("critical:"):
            purpose_lines.append(s)
    if purpose_lines:
        result["purpose"] = " ".join(purpose_lines)
    else:
        # fallback: first non-boilerplate content line that looks like a sentence
        for line in header.splitlines():
            s = line.strip()
            if s and len(s.split()) >= 6 and not s.startswith(("from", "import", "def", "class", "@", "#", "\"\"\"")):
                result["purpose"] = s
                break

    # STATUS — explicit status line, or inferred from phase_word
    sm = re.search(r"(?:status|status[:\-]?\s*)(.+)", header, re.I)
    if sm:
        result["status"] = sm.group(1).strip()
    else:
        # infer from phase wording
        low = header.lower()
        if "phase 4: write-lock" in low or "write-lock" in low:
            result["status"] = "write-locked"
        elif "phase 3" in low:
            result["status"] = "read-write"
        elif "phase 2" in low:
            result["status"] = "write"
        elif "phase 7" in low or "lab/experimental" in low or "target" in low:
            result["status"] = "lab/experimental"
        elif "phase 5" in low:
            result["status"] = "phase-5"
        else:
            result["status"] = "uncategorized"

    # CLI — either explicit CLI block or our generic form
    cli_m = re.search(r"(?:cli entry|primary cli|cli demo|__main__|standalone cli|command-line|invocation)[:\s]*(.+)", header, re.I)
    if cli_m:
        result["cli"] = cli_m.group(1).strip()
    else:
        # default: python operators/<file>  (or __main__ block if present)
        result["cli"] = f"python operators/{path.name}  (python operators/cli_arcs_run.py for full pipeline)"

    # SOURCE — canon refs as a joined string
    refs: List[str] = []
    rm = re.search(r"(?:canon reference|canonical reference|spec|canon foundation)[:\s]*(.+)", header, re.I)
    if rm:
        refs.append(rm.group(1).strip().replace("\n", " "))
    rm2 = re.search(r"(?:canon references?)[:\s]*(.+)", header, re.I)
    if rm2:
        refs.append(rm2.group(1).strip().replace("\n", " "))
    if refs:
        result["source"] = " | ".join(dict.fromkeys(refs))[:400]

    # SOURCE_NAME — the document/standard this operator is derived from, if parseable
    sn_m = re.search(r"(?:ARCS-[A-Za-z0-9\-]+\.md|ARCS-[A-Za-z0-9\-]+|SPEC-v[0-9\.]+|Canon v[0-9\.]+|ARCS-[A-Z]+-?[A-Za-z]+)", header)
    if sn_m:
        result["source_name"] = sn_m.group(0).replace("ARCS-", "ARCS_").replace(".md", "_MD").upper()
    else:
        result["source_name"] = ""

    # LOC via wc -l
    result["loc"] = wc_l(path)

    return result


def parse_skill_markdown(path: Path) -> Dict[str, Any]:
    """
    Extract the canonical table info from SKILL.md so our JSON IDs map to
    the layer/category the skill itself uses.
    """
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception:
        return {}

    # Layer-to-category mapping from the skill's layer headers + operator table.
    # We parse the table rows under each layer heading.
    result: Dict[str, Any] = {"layers": {}, "canonical": [], "experimental": []}

    # Find layer sections
    layer_pat = re.compile(r"^##\s+Layer\s+(\d+)\s*[—-]\s*(.+)$", re.M)
    layers: Dict[str, Dict[str, Any]] = {}
    for m in layer_pat.finditer(txt):
        num = m.group(1)
        title = m.group(2).strip()
        layers[num] = {"title": title, "operators": []}

    # Parse table rows within each layer
    # Table format: | OPERATOR | File | LOC | Purpose | CLI/Invocation |
    table_rows = re.findall(
        r"^\|\s+\*\*(.+?)\*\*\s*\|\s*`([^`]+)`\s*\|\s*([\d.]+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$",
        txt,
        re.M,
    )
    # Assign to the most recent layer
    cur_layer: str | None = None
    for row in table_rows:
        op_name = row[0].strip()
        file_rel = row[1].strip()
        loc = row[2].strip()
        purpose = row[3].strip()
        invocation = row[4].strip()
        entry: Dict[str, str] = {
            "name": op_name,
            "file": file_rel,
            "loc": loc,
            "purpose": purpose,
            "invocation": invocation,
        }
        if cur_layer:
            layers[cur_layer]["operators"].append(entry)

    # Walk text line-by-line to assign table rows to the current layer heading
    lines = txt.splitlines()
    cur_layer = None
    layer_map: Dict[str, Dict[str, Any]] = {}
    for line in lines:
        m = layer_pat.match(line)
        if m:
            cur_layer = m.group(1)
            layer_map[cur_layer] = {"title": m.group(2).strip(), "operators": []}
        elif cur_layer:
            row = re.match(
                r"^\|\s+\*\*(.+?)\*\*\s*\|\s*`([^`]+)`\s*\|\s*([\d.]+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$",
                line,
            )
            if row:
                layer_map[cur_layer]["operators"].append({
                    "name": row.group(1).strip(),
                    "file": row.group(2).strip(),
                    "loc": row.group(3).strip(),
                    "purpose": row.group(4).strip(),
                    "invocation": row.group(5).strip(),
                })

    result["layers"] = layer_map

    # Separate canonical vs experimental from the skill's explicit section
    canon_section = False
    for line in lines:
        if "Operators NOT yet canonical" in line:
            canon_section = True
            continue
        if canon_section and line.strip().startswith("|"):
            row = re.match(r"^\|\s+\*\*(.+?)\*\*\s*\|\s*`([^`]+)`\s*\|\s*([^\s|]+)\s*\|\s*(.+)$", line)
            if row:
                result["experimental"].append({
                    "name": row.group(1).strip(),
                    "file": row.group(2).strip(),
                    "rc_id": row.group(3).strip(),
                    "promotion": row.group(4).strip(),
                })

    # Everything not in experimental section = canonical
    canonical_names = set()
    for layer in layer_map.values():
        for op in layer["operators"]:
            canonical_names.add(op["name"])
    for exp in result["experimental"]:
        canonical_names.discard(exp["name"])
    result["canonical"] = sorted(canonical_names)

    return result


# ── build operator objects ───────────────────────────────────────────────────

def build_operators() -> Dict[str, Dict[str, Any]]:
    """
    One entry per .py file in operators/ that looks like an operator or system.
    """
    ops: Dict[str, Dict[str, Any]] = {}

    # Core operator files (the ones we want in the harness index)
    operator_files = [
        "arcs_operators_sage.py",
        "arcs_operators_lab.py",
        "arcs_operators_bar.py",
        "arcs_operators_curator.py",
        "arcs_operator_kairos.py",
        "arcs_operator_contract.py",
        "arcs_operator20.py",
        "arcs_kintsugi.py",
        "arcs_primitives.py",
        "arcs_primitives_bridge.py",
        "arcs_receipt_core.py",
        "arcs_constitutional_court.py",
        "arcs_hc.py",
        "arcs_lte.py",
        "arcs_rom.py",
        "arcs_trace.py",
        "arcs_trace_loki.py",
        "arcs_cis.py",
        "arcs_diagnostic.py",
        "arcs_pipeline_v1.py",
        "arcs_runtime_service.py",
        "arcs_api.py",
        "arcs_store.py",
        "arcs_yoav_store.py",
        "arcs_dewy_log.py",
        "arcs_substrate.py",
        "arcs_seed_bar.py",
        "arcs_kinematics.py",
        "arcs_no_go_inventory.py",
        "arcs_init_bundles.py",
        "arcs_battery.py",
        "arcs_backup.py",
        "arcs_inchworm_echo.py",
        "cli_arcs_run.py",
        "arcs_operator21.py",
        "seed_test_receipts.py",
        "waveform_optimizer.py",
    ]

    for fname in operator_files:
        path = OP_DIR / fname
        if not path.exists():
            continue
        meta = parse_python_header(path)
        # id = basename without .py
        op_id = fname[:-3]
        meta["id"] = op_id
        ops[op_id] = meta

    return ops


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    print(f"Reading skill table: {SKILL_FILE}")
    skill = parse_skill_markdown(SKILL_FILE)

    print(f"Reading operators from {OP_DIR}")
    ops = build_operators()
    print(f"  → {len(ops)} operator objects")

    # Build IDs index: category → list of op ids
    # Categories align with the skill's layers; we map each op to the layer
    # its file appears in in the skill table, or infer from file name.
    layer_map: Dict[str, List[str]] = {
        "meta_operators": [],
        "primitives": [],
        "systems": [],
        "infrastructure": [],
        "harness_wrappers": [],
        "support": [],
        "experimental": [],
    }

    # Explicit per-file-layer assignment using the skill table as ground truth,
    # falling back to file-name heuristics.
    file_to_layer: Dict[str, str] = {}

    # From the skill's canonical operator table:
    canonical_table: Dict[str, str] = {
        "arcs_operators_sage": "meta_operators",
        "arcs_operators_lab": "meta_operators",
        "arcs_operators_bar": "meta_operators",
        "arcs_operators_curator": "meta_operators",
        "arcs_operator_kairos": "meta_operators",
        "arcs_operator_contract": "meta_operators",
        "arcs_operator20": "meta_operators",
        "arcs_kintsugi": "meta_operators",
        "arcs_primitives": "primitives",
        "arcs_primitives_bridge": "primitives",
        "arcs_receipt_core": "primitives",
        "arcs_constitutional_court": "systems",
        "arcs_hc": "systems",
        "arcs_lte": "systems",
        "arcs_rom": "systems",
        "arcs_trace": "systems",
        "arcs_trace_loki": "systems",
        "arcs_cis": "systems",
        "arcs_diagnostic": "systems",
        "arcs_pipeline_v1": "infrastructure",
        "arcs_runtime_service": "infrastructure",
        "arcs_api": "infrastructure",
        "arcs_store": "infrastructure",
        "arcs_yoav_store": "infrastructure",
        "arcs_dewy_log": "infrastructure",
        "arcs_substrate": "infrastructure",
        "cli_arcs_run": "infrastructure",
    }
    file_to_layer.update(canonical_table)

    # File-name heuristics for the rest
    name_to_layer_heuristic: Dict[str, str] = {
        "arcs_seed_bar": "support",
        "arcs_kinematics": "systems",
        "arcs_no_go_inventory": "support",
        "arcs_init_bundles": "support",
        "arcs_battery": "support",
        "arcs_backup": "support",
        "arcs_inchworm_echo": "experimental",
        "seed_test_receipts": "support",
        "waveform_optimizer": "support",
        "arcs_operator21": "meta_operators",  # Phase 3, new operator
    }
    for k, v in name_to_layer_heuristic.items():
        if k not in file_to_layer:
            file_to_layer[k] = v

    # Populate layer_map
    for op_id, meta in ops.items():
        fname = meta["file"][:-3]  # strip .py
        layer = file_to_layer.get(fname, "support")
        layer_map[layer].append(op_id)

    # Canonical/experimental split
    canonical_ids = set()
    experimental_ids = set()
    for op_id, meta in ops.items():
        fname = op_id
        if fname in file_to_layer and file_to_layer[fname] == "experimental":
            experimental_ids.add(op_id)
        else:
            canonical_ids.add(op_id)

    # ── arcs_operators.json ────────────────────────────────────────────────
    operators_json: Dict[str, Any] = {}
    for op_id, meta in ops.items():
        entry: Dict[str, Any] = {
            "id": op_id,
            "name": meta.get("name", op_id),
            "file": meta.get("file", ""),
            "loc": meta.get("loc", -1),
            "phase": meta.get("phase", ""),
            "phase_detail": meta.get("phase_detail", ""),
            "status": meta.get("status", ""),
            "purpose": meta.get("purpose", ""),
            "cli": meta.get("cli", ""),
            "source": meta.get("source", ""),
            "source_name": meta.get("source_name", ""),
            "category": file_to_layer.get(op_id, "support"),
            "canonicality": "seed" if op_id == "arcs_operator21" else (
                "lab/experimental" if op_id == "arcs_inchworm_echo" else "canonical"
            ),
        }
        operators_json[op_id] = entry

    out_ops = OUT_DIR / "arcs_operators.json"
    out_ops.write_text(json.dumps(operators_json, indent=2), encoding="utf-8")
    print(f"  → {out_ops} ({out_ops.stat().st_size} bytes, {len(operators_json)} operators)")

    # ── arcs_operators_ids.json ────────────────────────────────────────────
    ids: Dict[str, Any] = {}
    for cat, ids_list in layer_map.items():
        ids[cat] = sorted(ids_list)

    out_ids = OUT_DIR / "arcs_operators_ids.json"
    out_ids.write_text(json.dumps(ids, indent=2), encoding="utf-8")
    print(f"  → {out_ids} ({out_ids.stat().st_size} bytes, {len(ids)} categories)")

    # ── arcs_operators_brief.json ──────────────────────────────────────────
    # Build metadata from skill content
    summary: Dict[str, Any] = {
        "operators": len(canonical_ids | experimental_ids),
        "categories": len(ids),
        "total_loc": sum(m.get("loc", 0) for m in ops.values()),
        "canonical_count": len(canonical_ids),
        "experimental_count": len(experimental_ids),
        "builder": "generate_arcs_operator_data.py",
        "built_at": __import__("datetime").datetime.now().isoformat(),
    }

    # Featured operators — canonical meta_operators + key primitives
    featured: List[Dict[str, Any]] = []
    featured_ids = [
        "arcs_operators_sage",
        "arcs_operators_lab",
        "arcs_operators_bar",
        "arcs_operators_curator",
        "arcs_kintsugi",
        "arcs_operator21",
        "arcs_primitives",
        "arcs_hc",
        "arcs_lte",
        "arcs_pipeline_v1",
        "cli_arcs_run",
    ]
    for fid in featured_ids:
        meta = ops.get(fid)
        if not meta:
            continue
        featured.append({
            "id": fid,
            "name": meta.get("name", fid),
            "file": meta.get("file", ""),
            "loc": meta.get("loc", -1),
            "phase": meta.get("phase", ""),
            "status": meta.get("status", ""),
            "category": file_to_layer.get(fid, "support"),
            "purpose": meta.get("purpose", ""),
            "cli": meta.get("cli", ""),
            "source_name": meta.get("source_name", ""),
            "description": (
                meta.get("purpose", "")
                or f"ARCS operator: {fid} ({meta.get('loc', 0)} LOC, {meta.get('phase', '')})"
            )[:300],
        })

    brief: Dict[str, Any] = {
        "summary": summary,
        "featured": featured,
        "skills": {
            "table": "arcs-operator-table",
            "reading_sequence": "arcs-reading-sequence",
            "handoff": "arcs-handoff",
            "adr_review": "arcs-adr-review",
        },
        "layers": {
            name: {
                "title": info["title"],
                "count": len(info["operators"]),
            }
            for name, info in skill.get("layers", {}).items()
        },
        "experimental": [
            {
                "id": "arcs_inchworm_echo",
                "name": "INCHWORM+ECHO",
                "file": "operators/arcs_inchworm_echo.py",
                "rc_id": "RC-OPS-001",
                "status": "lab/experimental",
                "promotion": "Observatory period — findings logged and replayed through Observatory across multiple real sessions, with severity grading and named patterns confirmed accurate in hindsight, before promotion to full ROM.",
            },
            {
                "id": "arcs_operator21",
                "name": "OPERATOR21 (SplineInference)",
                "file": "operators/arcs_operator21.py",
                "rc_id": "RC-OPS-003",
                "status": "seed",
                "promotion": "Farm league graduation: SEED → LAB (survives one structured review pass) → PLAYGROUND (tested in wild) → GEMINATE_CANDIDACY (dual-instance convergence test) → canonical. Opt-in only.",
            },
        ],
        "notes": "Generated from live operators/ tree + arcs-operator-table SKILL.md. Canonicality reflects current on-disk state (operator21 = SEED, inchworm_echo = lab/experimental, rest = canonical).",
    }

    out_brief = OUT_DIR / "arcs_operators_brief.json"
    out_brief.write_text(json.dumps(brief, indent=2), encoding="utf-8")
    print(f"  → {out_brief} ({out_brief.stat().st_size} bytes)")

    print("\nDone. Three files written to", OUT_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
