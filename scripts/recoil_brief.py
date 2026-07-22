#!/usr/bin/env python3
"""
recoil_brief.py -- single-source-of-truth generator for a recoil brief.

Reads one canonical engagement JSON and projects an AUDIENCE view:
  internal  = full (beliefs, next-steps, kinematic derivatives, opportunity NCI)
  external  = redacted (only audience:"both" fields survive)

The redaction is mechanical, not a manual discipline: any field/row tagged
audience:"internal" is dropped for the external projection. Kinematics are
COMPUTED (via operators/arcs_kinematics.py), never hand-typed, so the numbers
are reproducible from source.

Usage:
  python scripts/recoil_brief.py --data runtime/recoil/generated/<id>.json \
      --audience internal|external [--format md|json] [--set key=value ...]

Pass-through:
  --set meta.foo=bar   override any dotted meta key at generation time
"""
import argparse, json, os, sys

OPERATORS = os.path.join(os.path.dirname(__file__), "..", "operators")


def load(path):
    with open(path) as f:
        return json.load(f)


def apply_overrides(data, sets):
    """Pass-through --set key.path=value overrides (best-effort, meta scope)."""
    for kv in sets or []:
        if "=" not in kv:
            continue
        path, val = kv.split("=", 1)
        node = data
        keys = path.split(".")
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = val
    return data


def visible(item, audience):
    """A field/row is visible if audience is internal, or it is tagged 'both'."""
    if audience == "internal":
        return True
    return item.get("audience") == "both"


def compute_kinematics(series_block):
    """Compute D1-D3 per series via the canonical engine. Reproducible."""
    sys.path.insert(0, os.path.abspath(OPERATORS))
    import numpy as np
    from arcs_kinematics import KinematicManifold
    dt = series_block.get("dt", 1.0)
    out = []
    for s in series_block["series"]:
        pts = np.array(s["points"], dtype=float)
        km = KinematicManifold(pts, dt=dt)
        v, a, j = km.velocity(), km.acceleration(), km.jerk()
        out.append({
            "key": s["key"], "label": s["label"], "audience": s.get("audience", "both"),
            "points": s["points"],
            "D1_velocity": {"peak": round(float(np.max(np.abs(v))), 3), "terminal": round(float(v[-1]), 3)},
            "D2_acceleration": {"terminal": round(float(a[-1]), 3)},
            "D3_jerk": {"terminal": round(float(j[-1]), 3)},
        })
    n = len(series_block["series"][0]["points"]) if series_block["series"] else 0
    note = (f"n={n} points -> D1-D2 valid, D3 marginal, D4+ undersampled. "
            "D5-D12 = coherence-operator zone (noise past ~D4 per arcs_kinematics.py "
            "header); NOT reported as derivatives.")
    return out, note


def project(data, audience):
    """Mechanically drop internal-only content for the requested audience."""
    dropped = []
    out = {"meta": data["meta"], "audience": audience}

    # beliefs
    keep_b = [b for b in data.get("beliefs", []) if visible(b, audience)]
    dropped += [f"belief:{b['id']}" for b in data.get("beliefs", []) if not visible(b, audience)]
    if keep_b:
        out["beliefs"] = keep_b

    # opportunity
    if visible(data.get("opportunity", {}), audience):
        out["opportunity"] = data.get("opportunity")
    elif "opportunity" in data:
        dropped.append("opportunity.nci")

    # next steps
    keep_n = [s for s in data.get("next_steps", []) if visible(s, audience)]
    dropped += [f"next_step:{s['owner']}" for s in data.get("next_steps", []) if not visible(s, audience)]
    if keep_n:
        out["next_steps"] = keep_n

    # kinematics: trajectories always cross; derivatives are internal-only
    kin, note = compute_kinematics(data["kinematic_series"])
    if audience == "internal":
        out["kinematics"] = {"series": kin, "note": note}
    else:
        out["kinematics"] = {"series": [{"key": s["key"], "label": s["label"], "points": s["points"]}
                                        for s in kin if s["audience"] == "both"]}
        dropped.append("kinematic derivatives (D1-D3)")

    out["_redaction_report"] = {"audience": audience, "dropped_count": len(dropped), "dropped": dropped}
    return out


def render_md(p):
    L = [f"# Recoil Brief -- {p['meta']['counterpart']} ({p['audience']})", ""]
    if "beliefs" in p:
        L += ["## Belief Log (confidence x conviction)", "",
              "| id | claim | inf | conf | conviction | verdict |",
              "|----|-------|-----|------|------------|---------|"]
        for b in p["beliefs"]:
            c = b["confidence"]
            cs = f"{c[0] if c[0] is not None else '--'}->{c[1]}"
            L.append(f"| {b['id']} | {b['claim']} | {b['inference']} | {cs} | {b['conviction']} | {b['verdict']} |")
        L.append("")
    if "opportunity" in p:
        o = p["opportunity"]
        L += [f"**Opportunity NCI:** {o['nci_prior']} -> {o['nci_post']}  "
              f"({o['y_state']}/{o['topology']})", ""]
    L += ["## Kinematics (measured)", ""]
    for s in p["kinematics"]["series"]:
        if "D1_velocity" in s:
            L.append(f"- **{s['label']}**: D1 peak {s['D1_velocity']['peak']} / "
                     f"term {s['D1_velocity']['terminal']} | D2 term {s['D2_acceleration']['terminal']} | "
                     f"D3 term {s['D3_jerk']['terminal']}")
        else:
            L.append(f"- **{s['label']}**: trajectory {s['points']} (derivatives redacted)")
    if "note" in p["kinematics"]:
        L += ["", f"> {p['kinematics']['note']}"]
    if "next_steps" in p:
        L += ["", "## Next Steps"]
        for s in p["next_steps"]:
            L.append(f"- [{s['owner']}] {s['text']}")
    r = p["_redaction_report"]
    L += ["", f"---", f"_Redaction: {r['dropped_count']} field(s) dropped for '{r['audience']}' -> "
          f"{', '.join(r['dropped']) or 'none'}_"]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Single-source recoil brief generator.")
    ap.add_argument("--data", required=True)
    ap.add_argument("--audience", choices=["internal", "external"], default="internal")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--set", action="append", default=[], help="pass-through override key.path=value")
    a = ap.parse_args()

    data = apply_overrides(load(a.data), a.set)
    proj = project(data, a.audience)
    print(render_md(proj) if a.format == "md" else json.dumps(proj, indent=2))


if __name__ == "__main__":
    main()
