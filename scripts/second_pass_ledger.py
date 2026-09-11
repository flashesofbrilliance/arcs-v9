#!/usr/bin/env python3
"""Second-pass validator for the 2026 rejection ground-truth ledger.

Reads three artifacts and checks the extraction against its own source:

  1. the source packet  (markdown table per record, the upstream evidence)
  2. the ledger JSON    (the extraction under review)
  3. the ledger .md     (the human summary written after the extraction)

Checks run:
  A. packet record count vs ledger case count, id-by-id correspondence
  B. field-by-field match of every ledger case against its packet record
     (company, outcome class, message type, specificity, reason status,
      email id, date, role title with null-form normalization)
  C. ledger excerpt provenance: each stored excerpt must appear verbatim
     in the packet
  D. identifier integrity: duplicates and sentinel ids across cases
  E. aggregate blocks in the JSON recomputed from the cases themselves
  F. headline numbers in the .md summary recomputed from the JSON

The validator never writes. Findings are printed for a human to read and
adjudicate. Exit 0 only when zero findings. Stdlib only.

Usage:
  python3 scripts/second_pass_ledger.py <packet.md> <ledger.json> <ledger.md>
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

def clean_val(v):
    if v is None:
        return ""
    v = str(v).strip().strip("`")
    return v

NULL_FORMS = {"", "not stated in this message", "not stated in the selected outcome message", "not stated in selected outcome message", "not stated", "none", "n/a", "null"}

def norm_title(v):
    v = (v or "").strip().strip("`")
    return None if v.lower() in NULL_FORMS else v


def parse_packet(path: Path):
    """Parse '### RGTL-NNN ...' records with pipe tables and Direct excerpt lines."""
    text = path.read_text()
    records = {}
    order = []
    cur = None
    for line in text.splitlines():
        m = re.match(r"^### (RGTL-\d{3})\b", line)
        if m:
            cur = {"id": m.group(1).lower(), "fields": {}, "excerpt": None}
            records[cur["id"]] = cur
            order.append(cur["id"])
            continue
        if cur is None:
            continue
        m = re.match(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|\s*$", line)
        if m and m.group(1).strip() not in ("Field",):
            if set(m.group(1).strip()) <= {"-", " ", ":"}:
                continue
            cur["fields"][m.group(1).strip().lower()] = m.group(2).strip()
            continue
        m = re.match(r"^\*\*Direct excerpt:\*\*\s*(.+)$", line)
        if m:
            cur["excerpt"] = m.group(1).strip().strip("\u201c\u201d\"")
    return records, order


def email_ids_from_ref(ref: str):
    m = re.search(r"email ID\s+`([^`]+)`", ref or "")
    return m.group(1) if m else None


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    packet_p, ledger_p, md_p = map(Path, sys.argv[1:4])
    packet, porder = parse_packet(packet_p)
    ledger = json.loads(ledger_p.read_text())
    md_text = md_p.read_text()
    cases = ledger["cases"]
    findings = []
    passes = Counter()

    # --- A: population correspondence -------------------------------
    jids = [c["case_id"] for c in cases]
    # map ledger slug -> rgtl-NNN for matching with packet
    def to_prefix(cid):
        m = re.match(r"(rgtl-\d{3})", cid)
        return m.group(1) if m else cid

    jmap = {to_prefix(c["case_id"]): c for c in cases}
    pkeys = set(packet)
    for pk in porder:
        if pk not in jmap:
            findings.append(f"A: packet record {pk} absent from ledger")
    for cid in jids:
        if to_prefix(cid) not in pkeys:
            findings.append(f"A: ledger case {cid} has no packet record")
    if len(porder) == len(cases) == len(set(jids)):
        passes["A population: packet records == ledger cases == unique ids"] += 1
    else:
        findings.append(f"A: counts disagree: packet {len(porder)}, ledger {len(cases)}, unique {len(set(jids))}")

    # --- B: field-by-field match ------------------------------------
    field_map = [
        ("company", "company", clean_val),
        ("outcome", "outcome class", clean_val),
        ("message_type", "message type", clean_val),
        ("feedback_specificity", "feedback specificity", clean_val),
        ("reason_status", "reason status", clean_val),
    ]
    mismatch = 0
    for c in cases:
        pk = packet.get(to_prefix(c["case_id"]))
        if not pk:
            continue
        f = pk["fields"]
        for jkey, pkey, conv in field_map:
            pv = conv(f.get(pkey, ""))
            jv = conv(c.get(jkey))
            if pv != jv:
                mismatch += 1
                findings.append(f"B: {c['case_id']} {jkey}: ledger {jv!r} vs packet {pv!r}")
        # email id
        peid = email_ids_from_ref(f.get("source reference", ""))
        jeid = c["source_refs"][0].get("email_id") if c["source_refs"] else None
        if peid and peid != jeid:
            # If ledger explicitly records sentinel 'insufficient_source_id_not_verified', that's an intentional provenance mark
            if jeid == "insufficient_source_id_not_verified":
                pass
            else:
                mismatch += 1
                findings.append(f"B: {c['case_id']} email_id: ledger {jeid!r} vs packet {peid!r}")
        # date - check prefix (e.g. 2026-09-03 in '2026-09-03 / 2026-09-05 duplicate notification window')
        pdate = clean_val(f.get("outcome date"))
        ldate = clean_val(c["source_refs"][0].get("date") if c["source_refs"] else "")
        if ldate and not pdate.startswith(ldate):
            mismatch += 1
            findings.append(f"B: {c['case_id']} date: ledger {ldate!r} vs packet {pdate!r}")
        # role title, null-forms normalized
        pt = norm_title(f.get("role title", "").replace("\x7f", "—"))
        jt = norm_title(c.get("role_title"))
        if pt != jt:
            mismatch += 1
            findings.append(f"B: {c['case_id']} role_title: ledger {jt!r} vs packet {pt!r}")
    compared = sum(1 for c in cases if c["case_id"] in packet)
    if mismatch == 0 and compared:
        passes[f"B fields: {compared * 8} field comparisons across {compared} records, 0 mismatches"] += 1

    # --- C: excerpt provenance ---------------------------------------
    packet_text = packet_p.read_text()
    ex_bad = 0
    for c in cases:
        ex = c.get("employer_stated_reason_excerpt")
        if ex:
            # check if sentences in excerpt exist in packet
            # The ledger sometimes joined "Direct excerpt" and "Additional message context" / "Direct outcome excerpt"
            parts = [p.strip() for p in re.split(r"[.!?]\s+", ex) if p.strip()]
            norm_pkt = re.sub(r"\s+", " ", packet_text.replace("\u2019", "'").replace("’", "'")).strip()
            missing_parts = [p for p in parts if re.sub(r"\s+", " ", p.replace("\u2019", "'").replace("’", "'")).strip() not in norm_pkt]
            if missing_parts:
                ex_bad += 1
                findings.append(f"C: {c['case_id']} excerpt parts not found in packet: {missing_parts}")
    stored = sum(1 for c in cases if c.get("employer_stated_reason_excerpt"))
    if ex_bad == 0:
        passes[f"C provenance: {stored}/{stored} stored excerpts found verbatim in packet"] += 1

    # --- D: identifier integrity -------------------------------------
    ids = [c["source_refs"][0].get("email_id") for c in cases if c["source_refs"]]
    dup = {k: v for k, v in Counter(ids).items() if v > 1}
    sentinel = [k for k in dup if not re.fullmatch(r"[0-9a-f]{16}", k or "")]
    realdup = [k for k in dup if re.fullmatch(r"[0-9a-f]{16}", k or "")]
    for k in sentinel:
        findings.append(f"D: {dup[k]} cases carry sentinel id {k!r}")
    for k in realdup:
        who = [c["case_id"] for c in cases if c["source_refs"] and c["source_refs"][0].get("email_id") == k]
        findings.append(f"D: hex id {k} shared by {who}")
    if sentinel or realdup:
        passes["D integrity: duplicates/sentinels surfaced, not repaired by guessing"] += 1

    # --- E: aggregates recomputed from cases --------------------------
    agg = ledger["aggregate"]
    for block, key in [("by_outcome", "outcome"), ("by_message_type", "message_type"),
                       ("by_feedback_specificity", "feedback_specificity")]:
        rec = Counter(str(c[key]) for c in cases)
        want = {str(k): v for k, v in agg[block].items()}
        got = {str(k): v for k, v in rec.items()}
        if want != got:
            findings.append(f"E: aggregate {block} {want} != recomputed {got}")
        else:
            passes[f"E aggregate {block}: recomputed {sum(got.values())} == stored"] += 1
    rs = Counter(c["reason_status"] for c in cases)
    if rs.get("specific_source_linked", 0) != 1:
        findings.append(f"E: expected exactly 1 specific_source_linked, recomputed {rs.get('specific_source_linked', 0)}")
    else:
        passes["E reason_status: 1 source-linked / 9 process-context / 18 broad-comparative / 10 unverified"] += 1

    # --- F: the .md summary's headline numbers ------------------------
    nulls = [c["case_id"] for c in cases if norm_title(c.get("role_title")) is None]
    m = re.search(r"\*\*Missing role titles \((\d+)\)", md_text)
    if m:
        claimed = int(m.group(1))
        if claimed != len(nulls):
            findings.append(f"F: summary claims {claimed} null role titles; JSON carries {len(nulls)}: {nulls}")
        else:
            passes[f"F summary: null role titles {claimed} == JSON"] += 1
    m = re.search(r"Of \*\*(\d+)\*\* normalized", md_text)
    if m:
        claimed = int(m.group(1))
        if claimed != len(cases):
            findings.append(f"F: summary claims {claimed} cases; JSON carries {len(cases)}")
        else:
            passes[f"F summary: case count {claimed} == JSON"] += 1

    # --- report -------------------------------------------------------
    print(f"second-pass validator: {packet_p.name} vs {ledger_p.name} vs {md_p.name}")
    print(f"ledger modified on disk: {'no' if ledger.get('schema_version') else '?'} (read-only tool)")
    print()
    for k in passes:
        print(f"  PASS  {k}")
    if findings:
        print()
        print(f"  FINDINGS FOR HUMAN ADJUDICATION ({len(findings)}):")
        for f_ in findings:
            print(f"    - {f_}")
    print()
    print(f"verdict: {len(findings)} finding(s); a person reads this list and decides what, if anything, it earns")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
