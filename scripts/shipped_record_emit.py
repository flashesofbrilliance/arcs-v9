#!/usr/bin/env python3
"""shipped_record_emit: one evidence-backed event table for "what shipped this year".

Reads only real sources and writes runtime/specs/shipped-record.json:
  milestones  public/status.html MILESTONES (date, title, rank, commit shas; each sha checked with git)
  beliefs     _STATE/falsification-ledger.jsonl (public shape only: id, date, scope, gold seam;
              claim text stays internal, the same rule status.arcs.care/beliefs follows)
  inventions  _DECISIONS/ADR-*.md cited by a belief (dated by the file's first commit)
  tao         _CANON/tao-proverbs.jsonl, grouped by (mint date, source)
  nftt        public/blog-nftt-*.html (dated by first commit), titles from <title>
  services    a short list of live product surfaces, each dated by its page's first commit
  tempo       weekly commits on origin/main (git) and weekly decision receipts (snapshot file), each with its as-of date

Every link carries a `cite` naming the file and key it was read from. A link that cannot be
cited is never emitted; known-but-uncited candidates go to `unconfirmed`.

Usage:
  python3 scripts/shipped_record_emit.py            # write
  python3 scripts/shipped_record_emit.py --check    # fail if the written file is stale
  python3 scripts/shipped_record_emit.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runtime" / "specs" / "shipped-record.json"
RECEIPTS = ROOT / "runtime" / "specs" / "shipped-record-receipts.json"
DAY0 = dt.date(2026, 4, 9)  # status.html: "DAY 0 · APR 9", sha 471d573
YEAR = "2026"

# Live product surfaces: (id, label, url, page whose first commit dates it).
SERVICES = [
    ("svc-app", "ARCS compass, live in production", "https://app.arcs.care", "ms:5"),
    ("svc-status", "Live build status", "https://status.arcs.care", "public/status.html"),
    ("svc-beliefs", "Belief-change log", "https://status.arcs.care/beliefs", "public/belief-log.html"),
    ("svc-nftt", "Notes from the Trenches", "https://good.arcs.care/blog/nftt", "public/blog-nftt-index.html"),
    ("svc-audit", "Agent-receipts audit", "https://good.arcs.care/audit", "public/good-agent-receipts-audit.html"),
    ("svc-phosphor", "Phosphor", "https://dj.arcs.care", "public/dj.html"),
    ("svc-check", "Free repo check", "https://good.arcs.care/audit/check", "public/good-audit-check.html"),
    ("svc-rfp", "RFP-O-Matic", "https://good.arcs.care/rfp-engine", "public/good-rfp-engine.html"),
]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def first_commit_date(path: str) -> str | None:
    out = git("log", "--diff-filter=A", "--no-renames", "--format=%as", "--", path)
    return out.splitlines()[-1] if out else None


def sha_exists(sha: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=ROOT,
                          capture_output=True).returncode == 0


def day_to_date(label: str) -> str:
    m = re.match(r"DAY (\d+)", label)
    return (DAY0 + dt.timedelta(days=int(m.group(1)))).isoformat() if m else ""


def read_milestones() -> list[dict]:
    s = (ROOT / "public/status.html").read_text()
    script = re.findall(r"<script[^>]*>(.*?)</script>", s, re.S)[0]
    body = script[script.find("var MILESTONES"):]
    hits = list(re.finditer(r'date:\s*"([^"]+)",\s*title:\s*"([^"]+)",\s*rank:\s*(\d)', body))
    rows = []
    for i, m in enumerate(hits):
        seg = body[m.end(): hits[i + 1].start() if i + 1 < len(hits) else len(body)]
        shas = [x for x in re.findall(r'sha:\s*"(\w+)"', seg) if sha_exists(x)]
        nftt = sorted(set(re.findall(r"nftt/([a-z0-9-]+)", seg)))
        rows.append({
            "id": "ms-%02d" % (i + 1), "lane": "milestone", "date": day_to_date(m.group(1)),
            "label": m.group(2), "rank": int(m.group(3)), "day_label": m.group(1),
            "shas": shas, "nftt": nftt, "cite": "public/status.html#MILESTONES[%d]" % i,
        })
    return rows


def read_beliefs() -> list[dict]:
    rows = []
    for line in (ROOT / "_STATE/falsification-ledger.jsonl").read_text().splitlines():
        d = json.loads(line)
        rows.append({
            "id": d["id"], "lane": "belief", "date": d["ts"], "scope": d["scope"],
            "gold": bool(d.get("canon")), "verdict": d.get("verdict"),
            "label": "%s · %s reversal%s" % (d["id"], d["scope"], " · gold seam" if d.get("canon") else ""),
            "refs": d.get("refs", []), "cite": "_STATE/falsification-ledger.jsonl#%s" % d["id"],
        })
    return rows


def adr_file(num: str) -> str | None:
    hits = sorted((ROOT / "_DECISIONS").glob("ADR-%s-*.md" % num))
    return str(hits[0].relative_to(ROOT)) if hits else None


def read_tao() -> tuple[list[dict], dict]:
    groups: dict = defaultdict(list)
    by_id = {}
    backfill: set = set()
    for line in (ROOT / "_CANON/tao-proverbs.jsonl").read_text().splitlines():
        d = json.loads(line)
        date = (d.get("minted") or "")[:10]
        if not date:
            continue
        src = d.get("source_adr") or ""
        groups[(date, src)].append(d["id"])
        if str(d.get("provenance", "")).startswith("extracted from artifact"):
            backfill.add((date, src))
        by_id[d["id"]] = (date, src)
    rows = []
    for (date, src), ids in sorted(groups.items()):
        rows.append({
            "id": "tao-%s-%s" % (date, re.sub(r"[^a-z0-9]+", "-", src.lower()).strip("-")[:40] or "x"),
            "lane": "tao", "date": date, "count": len(ids), "source": src, "tao_ids": ids,
            "backfill": (date, src) in backfill,
            "label": "%d Tao proverb%s from %s" % (len(ids), "" if len(ids) == 1 else "s", src or "unnamed source"),
            "cite": "_CANON/tao-proverbs.jsonl (minted=%s, source_adr=%s)" % (date, src),
        })
    return rows, by_id


def read_nftt() -> list[dict]:
    rows = []
    for p in sorted((ROOT / "public").glob("blog-nftt-*.html")):
        slug = p.stem[len("blog-nftt-"):]
        if slug in ("index", "loop-hud") or slug.startswith("recon-report") or slug.endswith(("-research", "-dossier")):
            continue
        date = first_commit_date(str(p.relative_to(ROOT)))
        t = re.search(r"<title>([^<]+)</title>", p.read_text(errors="ignore"))
        title = re.split(r"\s+[·|]\s+", t.group(1).strip())[0] if t else slug
        rows.append({"id": "nftt-" + slug, "lane": "nftt", "date": date, "slug": slug, "label": title,
                     "url": "https://good.arcs.care/blog/nftt/" + slug,
                     "cite": "%s (first commit %s)" % (p.relative_to(ROOT), date)})
    return [r for r in rows if r["date"]]


def read_services(ms: list[dict]) -> list[dict]:
    rows = []
    for sid, label, url, page in SERVICES:
        if page.startswith("ms:"):  # dated by the milestone that says it went live
            i = int(page[3:]) - 1
            date, cite = ms[i]["date"], ms[i]["cite"]
        else:
            date = first_commit_date(page)
            cite = "%s (first commit %s)" % (page, date)
        if date:
            rows.append({"id": sid, "lane": "service", "date": date, "label": label, "url": url, "cite": cite})
    return rows


def weekly_commits() -> list[dict]:
    dates = git("log", "origin/main", "--since=%s-01-01" % YEAR, "--format=%as").splitlines()
    c: Counter = Counter()
    for d in dates:
        day = dt.date.fromisoformat(d)
        c[(day - dt.timedelta(days=day.weekday())).isoformat()] += 1
    return [{"week": w, "n": n} for w, n in sorted(c.items())]


def build() -> dict:
    ms, bel, (tao, tao_by_id), nftt, svc = read_milestones(), read_beliefs(), read_tao(), read_nftt(), None
    svc = read_services(ms)
    nftt_ids = {r["slug"]: r["id"] for r in nftt}
    events = ms + bel + tao + nftt + svc
    links, unconfirmed = [], []
    inventions = {}

    for b in bel:
        for ref in b["refs"]:
            m = re.fullmatch(r"ADR-(\d+)", ref)
            if m:
                f = adr_file(m.group(1))
                if not f:
                    unconfirmed.append({"from": b["id"], "to": ref, "why": "ADR file not found in _DECISIONS"})
                    continue
                iid = "adr-" + m.group(1)
                if iid not in inventions:
                    inventions[iid] = {"id": iid, "lane": "invention", "date": first_commit_date(f),
                                       "label": ref, "cite": "%s (first commit)" % f}
                links.append({"from": b["id"], "to": iid, "kind": "led-to",
                              "cite": "_STATE/falsification-ledger.jsonl#%s refs %s" % (b["id"], ref)})
            m = re.fullmatch(r"tao-(\d+)", ref)
            if m and ref in tao_by_id:
                date, src = tao_by_id[ref]
                tgt = next(t["id"] for t in tao if t["date"] == date and t["source"] == src)
                links.append({"from": b["id"], "to": tgt, "kind": "minted",
                              "cite": "_STATE/falsification-ledger.jsonl#%s refs %s" % (b["id"], ref)})
            m = re.fullmatch(r"(closes-loop|supersedes-assumption):(F\d+)", ref)
            if m:
                links.append({"from": m.group(2), "to": b["id"], "kind": "repaired-by",
                              "cite": "_STATE/falsification-ledger.jsonl#%s refs %s" % (b["id"], ref)})
            if ref.startswith("belief log F"):
                links.append({"from": ref.split()[-1], "to": b["id"], "kind": "repaired-by",
                              "cite": "_STATE/falsification-ledger.jsonl#%s refs '%s'" % (b["id"], ref)})

    for t in tao:
        m = re.fullmatch(r"ADR-(\d+)", t["source"])
        if m and "adr-" + m.group(1) in inventions:
            links.append({"from": "adr-" + m.group(1), "to": t["id"], "kind": "minted", "cite": t["cite"]})
        m = re.fullmatch(r"nftt/([a-z0-9-]+)", t["source"])
        if m:
            if m.group(1) in nftt_ids:
                links.append({"from": nftt_ids[m.group(1)], "to": t["id"], "kind": "minted", "cite": t["cite"]})
            else:
                unconfirmed.append({"from": t["source"], "to": t["id"], "why": "NFTT slug has no page in public/"})

    for m in ms:
        for slug in m["nftt"]:
            if slug in nftt_ids:
                links.append({"from": m["id"], "to": nftt_ids[slug], "kind": "written-up",
                              "cite": "%s names nftt/%s" % (m["cite"], slug)})

    # Candidates a reader would expect but no source states; kept out of links on purpose.
    for a, b, why in [
        ("ms-11", "nftt-the-loop-closes", "same theme and title, but status.html does not cite the post"),
        ("ms-16", "nftt-assets-and-liabilities", "same date and theme, but status.html does not cite the post"),
        ("ms-21", "svc-audit", "the audit offer milestone names a page, not the svc row; date match only"),
    ]:
        unconfirmed.append({"from": a, "to": b, "why": why})

    events += [i for i in inventions.values() if i["date"]]
    events = [e for e in events if e.get("date", "").startswith(YEAR)]
    ids = {e["id"] for e in events}
    links = [l for l in links if l["from"] in ids and l["to"] in ids]
    events.sort(key=lambda e: (e["date"], e["lane"], e["id"]))

    receipts = json.loads(RECEIPTS.read_text()) if RECEIPTS.exists() else {"weeks": []}
    return {
        "schema": "shipped-record/v1",
        "as_of_commit": git("rev-parse", "--short", "origin/main"),
        "lanes": ["service", "milestone", "belief", "invention", "nftt", "tao"],
        "events": events,
        "links": links,
        "unconfirmed": unconfirmed,
        "tempo": {"commits": weekly_commits(), "commits_cite": "git log origin/main --since=%s-01-01, by ISO week" % YEAR,
                  "commits_as_of": git("log", "-1", "--format=%as", "origin/main"),
                  "receipts": receipts.get("weeks", []), "receipts_cite": receipts.get("cite", "missing"),
                  # Weeks after the snapshot date were never counted; a reader must not see them as zero.
                  "receipts_as_of": receipts.get("as_of")},
        "counts": dict(Counter(e["lane"] for e in events)),
    }


def self_test() -> int:
    d = build()
    ids = {e["id"] for e in d["events"]}
    assert all(l["from"] in ids and l["to"] in ids and l["cite"] for l in d["links"]), "dangling or uncited link"
    assert all(e.get("cite") for e in d["events"]), "uncited event"
    assert all(e["date"].startswith(YEAR) for e in d["events"])
    assert not any("claim" in e for e in d["events"]), "belief claim text leaked"
    assert d["tempo"]["commits_as_of"] and d["tempo"]["receipts_as_of"], "tempo without its as-of dates"
    assert day_to_date("DAY 98 · JUL 16") == "2026-07-16", "day arithmetic off"
    # Rename-following once dated a November post by an older sibling template (2026-11-13).
    nf = {e["slug"]: e["date"] for e in d["events"] if e["lane"] == "nftt"}
    assert nf.get("the-posted-rate") == "2026-11-11", "nftt date picked up a sibling's history"
    print("shipped_record_emit self-test: OK (%d events, %d links, %d unconfirmed)"
          % (len(d["events"]), len(d["links"]), len(d["unconfirmed"])))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    d = build()
    text = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
    if a.check:
        old = json.loads(OUT.read_text()) if OUT.exists() else {}
        old.pop("as_of_commit", None); d.pop("as_of_commit", None)
        if old != d:
            print("✖ shipped-record.json is stale. fix: python3 scripts/shipped_record_emit.py", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text)
    print("wrote %s: %s, %d links, %d unconfirmed" % (OUT.relative_to(ROOT), d["counts"], len(d["links"]), len(d["unconfirmed"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
