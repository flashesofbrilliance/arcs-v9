#!/usr/bin/env python3
"""
github_ingest.py — plug-and-play GitHub → ARCS Observatory dataset builder.

Point it at ANY GitHub repo, apply a (user-editable) event ruleset, and emit a
data.<name>.json payload + datasets.json entry that drops straight into the
Observatory switcher. No code change, no rebuild of the UI.

Two input modes (the engine is identical for both):
  LIVE   python3 scripts/github_ingest.py --repo owner/name --token $GITHUB_TOKEN
  OFFLINE python3 scripts/github_ingest.py --repo owner/name --from-json commits.json
         (commits.json = a GitHub `GET /repos/:o/:r/commits` response array, or a
          {"commits":[...], "releases":[...]} bundle. Lets you ingest in CI or behind
          a proxy by fetching separately, and makes the whole path testable offline.)

Custom events:   edit scripts/event-rules.json (see scripts/event_rules.py docstring).
Output schema:   identical to scripts/build_observatory.py — runtime.jsx hydrates it.
Deps:            stdlib only (urllib/json/argparse). No new dependencies.
"""
from __future__ import annotations
import argparse, json, os, sys, urllib.request, urllib.error
from datetime import date, datetime

import event_rules as ER
from build_observatory import slug_to_name, update_manifest  # reuse the manifest writer

API = "https://api.github.com"


# ── GitHub REST (stdlib) ─────────────────────────────────────────────────────────
def _get(url: str, token: str | None):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "arcs-observatory-ingest",
        **({"Authorization": f"Bearer {token}"} if token else {}),
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r), r.headers


def fetch_commits(repo: str, token: str | None, max_pages: int = 5) -> list[dict]:
    out, page = [], 1
    while page <= max_pages:
        data, _ = _get(f"{API}/repos/{repo}/commits?per_page=100&page={page}", token)
        if not data:
            break
        out.extend(data)
        if len(data) < 100:
            break
        page += 1
    return out


def fetch_releases(repo: str, token: str | None) -> list[dict]:
    try:
        data, _ = _get(f"{API}/repos/{repo}/releases?per_page=100", token)
        return data
    except urllib.error.HTTPError:
        return []


# ── normalize GitHub objects → the engine's common signal shape ──────────────────
def norm_commit(c: dict) -> dict:
    msg = (c.get("commit", {}).get("message", "") or "")
    subject = msg.splitlines()[0] if msg else ""
    body = "\n".join(msg.splitlines()[1:]).strip()
    iso = c.get("commit", {}).get("author", {}).get("date", "") or c.get("commit", {}).get("committer", {}).get("date", "")
    day = iso[:10] if iso else date.today().isoformat()
    author = (c.get("author") or {}).get("login") or c.get("commit", {}).get("author", {}).get("name", "")
    return {"kind": "commit", "sha": c.get("sha", ""), "date": day, "subject": subject, "body": body, "author": author, "labels": []}


def norm_release(r: dict) -> dict:
    iso = r.get("published_at") or r.get("created_at") or ""
    day = iso[:10] if iso else date.today().isoformat()
    name = r.get("name") or r.get("tag_name") or "release"
    return {"kind": "release", "sha": (r.get("tag_name") or "")[:12], "date": day,
            "subject": f"release: {name}", "body": (r.get("body") or "").strip(), "author": (r.get("author") or {}).get("login", ""), "labels": []}


# ── auto-derive the altitude deck (LAYERS) from classified events ────────────────
def grade_of(conf: int) -> str:
    return "A" if conf >= 90 else "B" if conf >= 86 else "C" if conf >= 82 else "D" if conf >= 75 else "F"


def build_layers(events: list[dict], slug: str, per_alt: int = 6) -> list[dict]:
    layers = []
    for alt in ("L5", "L4", "L3", "L2", "L1"):
        evs = [e for e in events if e.get("alt") == alt]
        if not evs:
            continue
        evs = sorted(evs, key=lambda e: e.get("conf", 0), reverse=True)[:per_alt]
        findings = []
        for e in evs:
            findings.append({
                "id": f"s-{e['sha']}", "lab": e["label"][:64], "grade": grade_of(e.get("conf", 82)),
                "conf": e.get("conf", 82), "risk": "LOW", "kind": e.get("type", "event").upper(),
                "date": e.get("date"),
                "desc": e.get("desc", "")[:240],
                "prov": [[e["label"][:48], e["sha"], "commit", "—"]],
            })
        layers.append({"id": alt, "findings": findings})
    return layers


def main():
    ap = argparse.ArgumentParser(description="Build an Observatory dataset from a GitHub repo via a custom event ruleset.")
    ap.add_argument("--repo", required=True, help="owner/name")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    ap.add_argument("--rules", default=ER.DEFAULT_RULES_PATH, help="event ruleset (default: scripts/event-rules.json)")
    ap.add_argument("--from-json", dest="from_json", default=None, help="ingest a pre-fetched commits array / {commits,releases} bundle instead of calling the API")
    ap.add_argument("--out-dir", default="public/observatory")
    ap.add_argument("--name", default=None, help="dataset name → filename data.<name>.json + switcher label key (default: repo name)")
    ap.add_argument("--label", default=None)
    ap.add_argument("--include-releases", action="store_true", help="also fetch + classify GitHub releases")
    ap.add_argument("--max-pages", type=int, default=5, help="commit pages to fetch (100/page)")
    args = ap.parse_args()

    rules = ER.load_rules(args.rules)

    raw_commits, raw_releases = [], []
    if args.from_json:
        blob = json.load(open(args.from_json))
        if isinstance(blob, list):
            raw_commits = blob
        else:
            raw_commits = blob.get("commits", [])
            raw_releases = blob.get("releases", [])
    else:
        try:
            raw_commits = fetch_commits(args.repo, args.token, args.max_pages)
            if args.include_releases:
                raw_releases = fetch_releases(args.repo, args.token)
        except urllib.error.HTTPError as e:
            sys.exit(f"GitHub API error {e.code}: {e.reason} — set --token / GITHUB_TOKEN, or use --from-json")

    # normalize → signals (newest-first from API; reverse to chronological so `first` = genesis)
    sigs = [norm_commit(c) for c in raw_commits] + [norm_release(r) for r in raw_releases]
    sigs = [s for s in sigs if s.get("date")]
    sigs.sort(key=lambda s: s["date"])  # oldest first

    events, risks = [], []
    for i, s in enumerate(sigs):
        e = ER.classify_event(s, rules, first=(i == 0))
        if e:
            events.append(e)
        r = ER.classify_risk(s, rules)
        if r:
            risks.append(r)

    # dedupe risks by distinct risk text — keep first (earliest) occurrence,
    # so each exposure surfaces once on the register rather than once per commit.
    seen, deduped = set(), []
    for r in risks:
        key = r.get("risk") or r.get("note") or r.get("id")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    risks = deduped

    if not events:
        sys.exit("No events produced — check the repo has commits and the ruleset matches them.")

    layers = build_layers(events, args.repo)
    start = min(e["date"] for e in events)
    span_days = max((date.today() - datetime.strptime(start, "%Y-%m-%d").date()).days + 2, 7)
    name = args.name or slug_to_name(args.repo)
    label = args.label or f"{name} — GitHub events"

    payload = {
        "repo": args.repo, "label": label,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "head_sha": (sigs[-1]["sha"][:7] if sigs else ""),
        "attribution": "shown", "span_start": start, "span_days": span_days,
        "redacted_open_risks": 0,
        "events": events, "risks": risks, "layers": layers,
    }

    os.makedirs(args.out_dir, exist_ok=True)
    file_name = f"data.{name}.json"
    out_path = os.path.join(args.out_dir, file_name)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    manifest_path = update_manifest(args.out_dir, args.repo, name, label, file_name)

    print(f"wrote {out_path}")
    print(f"updated {manifest_path}")
    print(f"  signals={len(sigs)}  events={len(events)}  risks={len(risks)}  layers={sum(len(l['findings']) for l in layers)} findings")
    print(f"  span: {start} +{span_days}d")


if __name__ == "__main__":
    main()
