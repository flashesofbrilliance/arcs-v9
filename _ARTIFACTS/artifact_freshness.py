#!/usr/bin/env python3
"""Artifact-freshness linter — the CI *sensor* of the reactive doc-graph.

For each derived surface in derivation.jsonl it measures TENSION:
  tension = 0  iff  surface == rebuild(ssot)  AND  redaction invariants hold.
Nonzero tension = a slack string (the frame moved, the surface didn't, or a
leak slipped in) -> a drift-receipt line + nonzero exit.

This is detection only (the CI half). The CD half (re-derive + re-publish +
re-verify = the Golden Inchworm's Needle) is a separate actuator.
See memory: seed-reactive-doc-graph-physics.

Usage:  python3 artifact_freshness.py            # human output, exit 1 on drift
        python3 artifact_freshness.py --receipts # also emit JSONL receipts to stdout
"""
import json, os, re, subprocess, sys, tempfile, pathlib

DIR = pathlib.Path(__file__).resolve().parent
MANIFEST = DIR / "derivation.jsonl"


def load_edges():
    edges = []
    for line in MANIFEST.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        edges.append(json.loads(line))
    return edges


def check(edge):
    """Return (list_of_receipts, tension_bool) for one edge."""
    receipts = []
    tension = False
    surface = DIR / edge["surface"]
    if not surface.exists():
        return [_r(edge, "MISSING", "derived surface absent")], True
    body = surface.read_text()

    # (1) staleness: rebuild the surface from its SSOT into a temp, compare bytes.
    if edge.get("build") and edge.get("ssot"):
        tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False).name
        try:
            proc = subprocess.run(
                edge["build"], shell=True, cwd=str(DIR),
                env={**os.environ, "OUT": tmp}, capture_output=True, text=True,
            )
            if proc.returncode != 0:
                receipts.append(_r(edge, "BUILD_FAIL", (proc.stderr or "").strip()[:200]))
                tension = True
            else:
                rebuilt = pathlib.Path(tmp).read_text()
                if rebuilt != body:
                    receipts.append(_r(edge, "DRIFT",
                        f"surface != rebuild({edge['ssot']}) — frame moved, string slack"))
                    tension = True
                else:
                    receipts.append(_r(edge, "IN_SYNC", f"= rebuild({edge['ssot']})"))
        finally:
            try: os.unlink(tmp)
            except OSError: pass

    # (2) redaction / dead-link invariants on the SHIPPED surface.
    for pat in edge.get("assert_absent", []):
        if re.search(pat, body):
            receipts.append(_r(edge, "LEAK", f"assert_absent matched /{pat}/"))
            tension = True
    for tok in edge.get("assert_present", []):
        if tok not in body:
            receipts.append(_r(edge, "MISSING_TOKEN", f"assert_present not found: {tok!r}"))
            tension = True
    return receipts, tension


def _r(edge, status, detail):
    return {"surface": edge["surface"], "ssot": edge.get("ssot"),
            "url": edge.get("url"), "status": status, "detail": detail}


def main():
    emit = "--receipts" in sys.argv
    any_tension = False
    all_receipts = []
    for edge in load_edges():
        receipts, tension = check(edge)
        any_tension = any_tension or tension
        all_receipts += receipts
        for rc in receipts:
            mark = "OK " if rc["status"] == "IN_SYNC" else "!! "
            print(f"{mark}{rc['status']:<13} {rc['surface']} — {rc['detail']}")
    print()
    if emit:
        for rc in all_receipts:
            print(json.dumps(rc))
        print()
    if any_tension:
        print("FRESHNESS: DRIFT — tension > 0. A string is slack: rebuild + re-publish the flagged surface(s).")
        sys.exit(1)
    print("FRESHNESS: all strings taut (zero tension).")
    sys.exit(0)


if __name__ == "__main__":
    main()
