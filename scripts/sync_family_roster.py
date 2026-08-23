#!/usr/bin/env python3
"""
sync_family_roster.py — one seed bank (_SEEDS), four family surfaces, kept honest.

The arcs.care family shows the same catalog through four windows:

  good.arcs.care        published goods            _SEEDS/distribution.jsonl (live channels)
  build.arcs.care       the flywheel: goods+play+lab   all three stages, one page
  lab.arcs.care         experiments ripening      _SEEDS/index.jsonl  lab_candidate ∈ {ripe,maybe,poc}
  playground.arcs.care  live performing artifacts  _SEEDS/index.jsonl  seed_type=performer
                                                    (cross-checked vs next.config.ts routing enum)

germinate — itself one of the goods — is the seed-bank format all four ride on, so the bank
is the single source and each surface is a render of it. This tripwire is what makes "single
source" true rather than aspirational: it fails (exit 1) the moment a surface disagrees with
the bank, with the bank, or with the live routing table. It does NOT re-author the pages —
they're hand-designed and curation is human-owned (same stance as seedbank_drift_check.py).
It emits runtime/family-roster.json, the machine-readable roster the surfaces are checked against.

Usage:
  python3 scripts/sync_family_roster.py            # human report (exit 1 on drift)
  python3 scripts/sync_family_roster.py --check     # CI: quiet on clean, exit 1 on drift
  python3 scripts/sync_family_roster.py --write-json # (re)write runtime/family-roster.json only
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS = os.path.join(ROOT, "_SEEDS")
DIST = os.path.join(SEEDS, "distribution.jsonl")
INDEX = os.path.join(SEEDS, "index.jsonl")
DECISIONS = os.path.join(ROOT, "_DECISIONS")
NEXTCFG = os.path.join(ROOT, "next.config.ts")
GOOD = os.path.join(ROOT, "public", "good.html")
BUILD = os.path.join(ROOT, "public", "build.html")
PLAY = os.path.join(ROOT, "public", "playground.html")
ROSTER_JSON = os.path.join(ROOT, "runtime", "family-roster.json")

# repos that are family surfaces / hubs, not catalog repos — allowed as page links.
NON_CATALOG_LINKS = {"arcs-skills", "homebrew-tap"}
LAB_STATES = {"ripe", "maybe", "proven-poc", "poc"}


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def adr_count():
    return len([f for f in os.listdir(DECISIONS) if re.match(r"ADR-\d+", f) and f.endswith(".md")])


def html(path):
    return open(path, encoding="utf-8").read()


def repos_referenced(text):
    return set(re.findall(r"github\.com/flashesofbrilliance/([a-z0-9][a-z0-9-]+)", text))


def tokens(s):
    return {t for t in re.split(r"[^a-z0-9]+", s.lower()) if len(t) > 2 and t not in
            ("the", "web", "app", "mini", "surface", "interactive", "toolkit")}


def build_roster():
    """goods (live-channel repos), lab candidates, and playground performers — the
    three renderable classes, all sourced from the one bank."""
    goods = []
    for row in load_jsonl(DIST):
        live_ch = [c for c in row.get("channels", []) if c.get("live")]
        conn = row.get("connector") or {}
        goods.append({
            "repo": row["repo"].split("/")[-1],
            "url": "https://" + row["url"],
            "live": bool(live_ch) or bool(conn.get("live")),
            "channels": [c["channel"] for c in live_ch],
            "connector": conn.get("url") if conn.get("live") else None,
        })
    idx = load_jsonl(INDEX)
    lab = [{"alias": r["alias"].split(" ")[0], "status": r["lab_candidate"]["status"]}
           for r in idx if r.get("lab_candidate", {}).get("status") in LAB_STATES]
    performers = [{"alias": r["alias"], "title": r.get("title", r["alias"]), "url": r["url"]}
                  for r in idx if r.get("seed_type") == "performer"]
    return {"goods": goods, "lab": lab, "playground": performers}


def playground_enum():
    """The routing truth: the :seg(...) group on the playground.arcs.care host rewrite."""
    m = re.search(r":seg\(([^)]+)\)[^\n]*playground\.arcs\.care", html(NEXTCFG))
    return set(m.group(1).split("|")) if m else set()


def audit():
    r = build_roster()
    live_goods = {g["repo"] for g in r["goods"] if g["live"]}
    all_goods = {g["repo"] for g in r["goods"]}
    lab_aliases = {x["alias"] for x in r["lab"]}
    perf_aliases = {p["alias"] for p in r["playground"]}
    good_refs, build_refs = repos_referenced(html(GOOD)), repos_referenced(html(BUILD))
    bhtml, phtml = html(BUILD), html(PLAY)
    problems = []

    # --- GOODS: good.html + build.html agree, no phantoms, every live good surfaced ---
    for page, refs in (("good.html", good_refs), ("build.html", build_refs)):
        for phantom in sorted(refs - all_goods - NON_CATALOG_LINKS):
            problems.append(f"[goods] {page} links repo not in _SEEDS: {phantom}")
    for missing in sorted(live_goods - (good_refs | build_refs)):
        problems.append(f"[goods] live good surfaced nowhere: {missing}")
    for only in sorted((good_refs & live_goods) - build_refs):
        problems.append(f"[goods] on good.html but missing from build.html rail: {only}")
    for only in sorted((build_refs & live_goods) - good_refs):
        problems.append(f"[goods] on build.html but missing from good.html: {only}")

    # --- LAB: every experiment build.html shows must be a real lab_candidate (no invented work) ---
    lab_sec = re.search(r"stage s-lab.*?</section>", bhtml, re.S)
    lab_labels = re.findall(r'card"><span class="t">([^<]+)', lab_sec.group(0)) if lab_sec else []
    for label in lab_labels:
        lt = tokens(label)
        if not any(lt & tokens(a) for a in lab_aliases):
            problems.append(f"[lab] build.html shows '{label.strip()}' — no matching lab_candidate in _SEEDS")

    # --- PLAYGROUND: bank performers == routing enum == what both pages link ---
    enum = playground_enum()
    if perf_aliases != enum:
        problems.append(f"[playground] bank performers {sorted(perf_aliases)} != routing enum {sorted(enum)}")
    for p in sorted(perf_aliases):
        if f"playground.arcs.care/{p}" not in bhtml:
            problems.append(f"[playground] performer '{p}' in bank but not linked on build.html")
    for p in r["playground"]:
        stem = p["title"].split(" ")[0].replace("é", "")
        if stem not in phtml.replace("é", ""):
            problems.append(f"[playground] performer '{p['title']}' in bank but not on playground.html")

    # --- COUNTS: build.html stats must match ground truth ---
    m = re.search(r'id="sv-adrs">(\d+)<', bhtml)
    if m and int(m.group(1)) != adr_count():
        problems.append(f"[count] build.html ADR stat {m.group(1)} != {adr_count()} in _DECISIONS/")
    m = re.search(r"(\d+) goods live", bhtml)
    rail = re.search(r"stage s-goods.*?</section>", bhtml, re.S)
    rail_n = len(re.findall(r'class="card"', rail.group(0))) if rail else 0
    if m and rail_n and int(m.group(1)) != rail_n:
        problems.append(f"[count] build.html 'goods live' {m.group(1)} != {rail_n} rail cards")
    m = re.search(r"(\d+) in the lab", bhtml)
    if m and lab_labels and int(m.group(1)) != len(lab_labels):
        problems.append(f"[count] build.html 'in the lab' {m.group(1)} != {len(lab_labels)} lab cards")

    return r, problems


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    roster, problems = audit()
    if mode != "--check":
        with open(ROSTER_JSON, "w", encoding="utf-8") as fh:
            json.dump({"generated_by": "scripts/sync_family_roster.py", **roster}, fh, indent=2)
            fh.write("\n")
    if mode == "--write-json":
        print(f"wrote {os.path.relpath(ROSTER_JSON, ROOT)}")
        return 0
    if problems:
        print("DRIFT — a family surface disagrees with the _SEEDS bank:", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        return 1
    if mode != "--check":
        g = [x["repo"] for x in roster["goods"] if x["live"]]
        print(f"clean · {len(g)} live goods · {len(roster['lab'])} lab candidates · "
              f"{len(roster['playground'])} performers · ADRs={adr_count()}")
        print(f"  goods: {', '.join(g)}")
        print(f"  playground: {', '.join(p['alias'] for p in roster['playground'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
