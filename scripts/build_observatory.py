#!/usr/bin/env python3
"""
build_observatory.py — generates the ARCS Observatory data layer from REAL repo data.

Emits a SWAPPABLE JSON payload (public/observatory/data.<name>.json) plus a switcher
manifest (datasets.json). The Observatory's static runtime.jsx fetches a payload and
hot-swaps it at runtime — no rebuild/redeploy to point the instrument at a new repo.
Each payload carries EVENTS / RISKS / LAYERS / span computed from:
  - git log              -> EVENTS  (build trajectory; classified by commit)
  - repo signals + ADRs  -> RISKS   (ruin-paths; OPEN items REDACTED for public view)
  - real file metrics    -> LAYERS  (5-altitude scored deck; prov cites real sources)

Exposure policy (ADR/decision 2026-06-05): PUBLIC, OPEN-RISKS REDACTED.
OPEN-status risks (standing live exposures) are computed but withheld from the public
payload; only AVERTED/MITIGATED are emitted, with a redactedCount banner for honesty.

Run:  python3 scripts/build_observatory.py                          # this repo
      python3 scripts/build_observatory.py --repo-path ../other \\
          --slug owner/other --attribution hide                    # another repo
"""
from __future__ import annotations
import json, os, re, subprocess
from datetime import date, datetime

REPO_SLUG = "flashesofbrilliance/arcs-v9"
REPO_PATH = "."  # where `git` runs; override with --repo-path to build a tailored instance
HIDE_ATTRIBUTION = False  # --attribution hide scrubs Co-Authored-By / tool trailers from desc


def sh(args: list[str]) -> str:
    return subprocess.run(args, capture_output=True, text=True, cwd=REPO_PATH).stdout


def rp(path: str) -> str:
    """Resolve a repo-relative path against the target repo, not the cwd."""
    return os.path.join(REPO_PATH, path)


def commits() -> list[dict]:
    raw = sh(["git", "log", "--reverse", "--date=short",
              "--format=%H%x1f%h%x1f%ad%x1f%s%x1f%b%x1e"])
    out = []
    for rec in raw.split("\x1e"):
        rec = rec.strip()
        if not rec:
            continue
        parts = rec.split("\x1f")
        if len(parts) < 4:
            continue
        out.append({"full": parts[0], "sha": parts[1], "date": parts[2],
                    "subject": parts[3], "body": parts[4] if len(parts) > 4 else ""})
    return out


def loc(path: str) -> int:
    try:
        with open(rp(path), encoding="utf-8") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def clean(subject: str) -> str:
    return re.sub(r"\s*\[NCI:[^\]]*\]\s*$", "", subject).strip()


def desc_of(c: dict) -> str:
    # --attribution hide strips desc to the commit subject line; the body (where
    # Co-Authored-By / tool trailers / noise live) is dropped. Flag gates VISIBILITY
    # only — the body is recoverable by regenerating with show.
    base = clean(c["subject"])
    if HIDE_ATTRIBUTION:
        return base
    body = c["body"].strip()
    first = body.split(chr(10))[0].strip() if body else ""
    return base + ((" — " + first) if first else "")


# ── EVENTS — classify each commit into the kit's type/altitude grammar ───────────
TYPE_KEEP = {"genesis", "canon", "kairos", "milestone", "feat", "security"}

def classify(c: dict, first: bool) -> dict | None:
    subj = c["subject"].lower()
    s = subj  # subject-driven: the body carries co-author/handoff noise, ignore it
    m = re.match(r"^([a-z]+)(?:\(([^)]+)\))?", subj)
    prefix = m.group(1) if m else ""
    scope = (m.group(2) or "") if m else ""

    # drop pure housekeeping + CI/deploy-trigger noise — never a build milestone
    if re.search(r"handoff|snapshot|pickup|gitignore|housekeep|\bstate\)"
                 r"|trigger|pick ?up|redeploy|validated|chore\(deploy", subj):
        if not first:
            return None

    if first:
        # history was rewritten by filter-repo; the true scaffold commit was purged.
        return {"id": f"ev-{c['sha']}", "date": c["date"], "alt": "L3", "type": "genesis", "peak": True,
                "label": "Earliest commit in current history (filter-repo rewrite)", "sha": c["sha"],
                "desc": "Git history was rewritten to purge committed secrets; SHAs before this were rewritten. "
                        "Earliest visible commit: " + clean(c["subject"]) + ".", "conf": 80}
    elif "canon" in s or "book ii" in s:
        typ = "canon"
    elif prefix == "feat" and ("security" in scope or re.search(r"\brls\b|deny-all|secret|\bauth\b|credential", s)):
        typ = "security"
    elif re.search(r"\bsecret|filter-repo|purge|\brls\b|deny-all", s):
        typ = "security"
    elif re.search(r"deploy|vercel|\bp4\b|\bready\b", s):
        typ = "milestone"
    elif re.search(r"kairos|anonymous compass|receipt.?claim|funnel", s):
        typ = "kairos"
    elif scope in ("adr", "spec") or re.search(r"\badr-\d+\b", s):
        typ = "milestone"
    elif prefix == "feat":
        typ = "feat"
    elif prefix == "fix" and re.search(r"unblock|deploy|adapter|prisma|critical|\bauth\b|brief", s):
        typ = "fix"
    else:
        return None  # drop chore/docs/debug/refactor noise

    # altitude = audience zoom (L5 exec governance → L1 surgical)
    if re.search(r"adr|govern|funnel|kairos|strategy|plg|model", s):
        alt = "L5"
    elif typ in ("security", "canon") or re.search(r"auth|rls|architecture|schema", s):
        alt = "L4"
    elif typ == "milestone" or re.search(r"deploy|migrat|infra|pipeline|ci", s):
        alt = "L3"
    elif typ == "feat" or re.search(r"ui|design|component|badge|card|compass|page", s):
        alt = "L2"
    else:
        alt = "L1"

    peak = first or typ in ("milestone", "kairos", "canon") or bool(re.search(r"deploy|ready|secret|filter-repo", s))
    conf = 90 if prefix in ("feat", "fix", "docs", "chore", "refactor") else 82
    if typ in ("genesis", "milestone", "security"):
        conf += 4
    conf = min(conf, 96)
    return {"id": f"ev-{c['sha']}", "date": c["date"], "alt": alt, "type": typ,
            **({"peak": True} if peak else {}),
            "label": clean(c["subject"]), "sha": c["sha"],
            "desc": desc_of(c),
            "conf": conf}


def build_events(cs: list[dict]) -> list[dict]:
    evs = []
    seen_adr: set[str] = set()
    for i, c in enumerate(cs):
        e = classify(c, i == 0)
        if not e:
            continue
        # dedupe by ADR number — keep the first commit that introduces each ADR
        nums = set(re.findall(r"adr-(\d+)", e["label"].lower()))
        if nums and nums <= seen_adr:
            continue
        seen_adr |= nums
        evs.append(e)
    # de-cluster: at most 2 events per (date, alt) — keep peaks + highest conf
    seen: dict[tuple, int] = {}
    keep = []
    for e in evs:
        k = (e["date"], e["alt"])
        seen[k] = seen.get(k, 0)
        if seen[k] < 2 or e.get("peak"):
            keep.append(e); seen[k] += 1
    return keep


# ── RISKS — computed from real repo signals; OPEN items redacted for public ──────
def build_risks(cs: list[dict]) -> tuple[list[dict], int]:
    text = " ".join((c["subject"] + " " + c["body"]).lower() for c in cs)
    def find_sha(pat):
        for c in cs:
            if re.search(pat, (c["subject"] + " " + c["body"]).lower()):
                return c["sha"]
        return None
    n_human = len({l.split("\t")[1] for l in sh(["git", "shortlog", "-sne"]).splitlines() if "noreply@anthropic" not in l and "\t" in l})
    has_tests = bool(sh(["bash", "-c", "find . -path ./node_modules -prune -o \\( -name '*.test.*' -o -name '*_test.py' \\) -print 2>/dev/null | grep -v node_modules | head -1"]).strip())

    full = []
    if re.search(r"secret|filter-repo|purge", text):
        full.append({"id": "risk-secrets", "date": "2026-06-04", "risk": "Credentials committed to git history",
                     "sev": "RUIN", "status": "AVERTED", "sha": find_sha(r"secret|filter-repo|purge"),
                     "how": "history rewrite + secret rotation",
                     "note": "API keys reached git history; purged before exploitation. Ruin-class — single exposure is unrecoverable."})
    if re.search(r"rls|deny-all", text):
        full.append({"id": "risk-rls", "date": "2026-05-27", "risk": "Unauthenticated data access (no RLS)",
                     "sev": "HIGH", "status": "AVERTED", "sha": find_sha(r"rls|deny-all"),
                     "how": "RLS deny-all on all 9 tables", "note": "Tables briefly readable without auth; closed by deny-all RLS."})
    if re.search(r"anonymous|receipt.?claim|adr-016", text):
        full.append({"id": "risk-xuser", "date": "2026-06-03", "risk": "Cross-user data leakage",
                     "sev": "HIGH", "status": "MITIGATED", "sha": find_sha(r"anonymous|receipt.?claim|adr-016"),
                     "how": "anonymous + scoped receipt-claim", "note": "Receipt-claim flow scoped per session to prevent cross-user reads."})
    if re.search(r"prisma.*adapter|p1012|prismapg", text):
        full.append({"id": "risk-prisma", "date": "2026-05-28", "risk": "Prisma 7 P1012 — deploy blocked",
                     "sev": "MED", "status": "AVERTED", "sha": find_sha(r"prisma.*adapter|prismapg"),
                     "how": "PrismaPg adapter fix", "note": "Schema/engine mismatch blocked deploy; resolved by adapter swap."})
    if n_human <= 1:
        full.append({"id": "risk-solo", "date": "2026-06-04", "risk": "Free-solo decision (zero reversibility)",
                     "sev": "RUIN", "status": "MITIGATED", "sha": None, "how": "ADR governance + reversibility gate",
                     "note": "Solo author, no review surface. Mitigated by ADR discipline; structurally standing."})
    # ── OPEN / standing exposures (REDACTED from public payload) ──
    if not has_tests:
        full.append({"id": "risk-ygate", "date": "2026-06-04", "risk": "computeYGate unaudited logic",
                     "sev": "MED", "status": "OPEN", "sha": None, "how": "needs unit coverage + audit",
                     "note": "Core gate logic ships without test coverage."})
    full.append({"id": "risk-dburl", "date": "2026-05-28", "risk": "DATABASE_URL silent rotation",
                 "sev": "HIGH", "status": "OPEN", "sha": None, "how": "needs alerting + pinned secret",
                 "note": "Provider can rotate the URL silently; no alert wired yet."})

    public = [r for r in full if r["status"] != "OPEN"]
    redacted = len(full) - len(public)
    public.sort(key=lambda r: r["date"])
    return public, redacted


# ── LAYERS — 5-altitude scored deck ──────────────────────────────────────────────
def generic_layers(cs: list[dict]) -> list[dict]:
    """Scaffold deck for a non-arcs repo. L1/L2 carry real generic signals;
    L3–L5 are author-me placeholders — the altitude assessment is editorial, not
    auto-derivable from an arbitrary tree. Hand-author per instance."""
    n_commits = len(cs)
    n_human = len({l.split("\t")[1] for l in sh(["git", "shortlog", "-sne"]).splitlines() if "\t" in l})
    has_tests = bool(sh(["bash", "-c", "find . -path ./node_modules -prune -o \\( -name '*.test.*' -o -name '*_test.py' -o -name '*.spec.*' \\) -print 2>/dev/null | grep -v node_modules | head -1"]).strip())
    F = lambda i, lab, g, c, rk, k, d, p: {"id": i, "lab": lab, "grade": g, "conf": c, "risk": rk, "kind": k, "desc": d, "prov": p}
    SC = "scaffold — author per instance"
    return [
        {"id": "L5", "findings": [F("g-L5-0", "Product thesis", "B", 60, "MED", "CLASS", "Author the one-line product thesis for this instance.", [["author me", "—", SC, "P00"]])]},
        {"id": "L4", "findings": [F("g-L4-0", "Governance posture", "B", 60, "MED", "INSTANCE", "Author the architecture / governance posture.", [["author me", "—", SC, "P00"]])]},
        {"id": "L3", "findings": [F("g-L3-0", "Core request path", "B", 60, "MED", "CLASS", "Author the core request / data path.", [["author me", "—", SC, "P00"]])]},
        {"id": "L2", "findings": [F("g-L2-0", "%d commits" % n_commits, "A", 90, "LOW", "INSTANCE", "%d commits by %d author(s) over the tracked span." % (n_commits, n_human), [["git history", "git shortlog -sne", "%d commits" % n_commits, "P04"]])]},
        {"id": "L1", "findings": [F("g-L1-0", "Tests %s" % ("present" if has_tests else "absent"), "A" if has_tests else "C", 90 if has_tests else 55, "LOW" if has_tests else "MED", "INSTANCE", "Automated tests %s in tree." % ("found" if has_tests else "not found"), [["test scan", "find", "tests" if has_tests else "none", "P28"]])]},
    ]


def build_layers(cs: list[dict]) -> list[dict]:
    # The curated deck below is editorial arcs-v9 content; a foreign repo gets a
    # scaffold (real generic signals + author-me slots), never arcs-v9 prose.
    if not os.path.exists(rp("WORLD.md")):
        return generic_layers(cs)
    try:
        n_adr = len([f for f in os.listdir(rp("_DECISIONS")) if re.match(r"ADR-\d+", f)])
    except OSError:
        n_adr = 0
    loc_compass = loc("src/app/api/compass/route.ts")
    loc_ygate = loc("src/lib/ygate.ts")
    loc_sim = loc("scripts/lattice_sim.py")
    has_tests = bool(sh(["bash", "-c", "find . -path ./node_modules -prune -o \\( -name '*.test.*' -o -name '*_test.py' \\) -print 2>/dev/null | grep -v node_modules | head -1"]).strip())
    n_human = len({l.split("\t")[1] for l in sh(["git", "shortlog", "-sne"]).splitlines() if "noreply@anthropic" not in l and "\t" in l})

    def F(id, lab, grade, conf, risk, kind, desc, prov):
        return {"id": id, "lab": lab, "grade": grade, "conf": conf, "risk": risk, "kind": kind, "desc": desc, "prov": prov}

    return [
        {"id": "L5", "findings": [
            F("s-L5-0", "Compass → Receipt", "A", 96, "LOW", "CLASS",
              "The product: a posed decision runs a Claude pipeline and returns one bearing + a graded receipt.",
              [["Product = compass pipeline", "src/app/api/compass/route.ts:1-%d" % loc_compass, "POST handler → receipt", "P09"]]),
            F("s-L5-1", "Solo · pre-revenue", "A" if n_human <= 1 else "B", 95, "LOW", "INSTANCE",
              "%d human author; no external contributors; ADR-governed." % n_human,
              [["Contributor count", "git shortlog -sne", "%d human" % n_human, "P04"]]),
            F("s-L5-2", "Spec-first world", "A", 92, "LOW", "CLASS",
              "Canon is the substrate; running code is the thinnest executable slice of a written world.",
              [["Canon precedes code", "WORLD.md + _CANON/", "Book II v1.0.0", "P02"]]),
            F("s-L5-3", "Observability layer", "B", 84, "MED", "CLASS",
              "ADR-023 goal lattice + load-tested Conductor sim; not yet wired to live receipts (gated).",
              [["Lattice spec + sim", "scripts/lattice_sim.py:1-%d" % loc_sim, "GREEN load test", "P30"]]),
        ]},
        {"id": "L4", "findings": [
            F("s-L4-0", "Dev/prod DB split", "A", 94, "LOW", "INSTANCE", "Separate dev and prod databases, externalized.",
              [["Split confirmed", "prisma + supabase config", "2 projects", "P11"]]),
            F("s-L4-1", "ADR governance", "A", 90, "LOW", "CLASS", "%d ADRs recorded; reversibility explicit." % n_adr,
              [["ADRs present", "_DECISIONS/", "ADR-001…%03d" % n_adr, "P15"]]),
            F("s-L4-2", "App-layer auth", "C", 85, "MED", "INSTANCE", "Auth enforced at the app layer (ADR-001) rather than the data layer alone.",
              [["Soft-guard routes", "src/app/api/**", "ADR-001", "P17"]]),
            F("s-L4-3", "RLS deny-all", "A", 92, "LOW", "INSTANCE", "Row-level security deny-all across all Supabase tables.",
              [["RLS deny-all", "scripts/rls-policies.sql", "9 tables", "P16"]]),
        ]},
        {"id": "L3", "findings": [
            F("s-L3-0", "Compass request path", "A", 95, "LOW", "CLASS", "Full request path from compass POST to rendered receipt.",
              [["Request path", "src/app/api/compass/route.ts", "POST→receipt", "P09"]]),
            F("s-L3-1", "Y-gate → render", "A", 92, "LOW", "INSTANCE", "Y-gate state drives render resolution (earned fidelity).",
              [["Y-gate→render", "src/lib/ygate.ts:1-%d" % loc_ygate, "state→resolution", "P10"]]),
            F("s-L3-2", "Manual env / rotation", "C", 82, "MED", "INSTANCE", "Env + secret rotation is manual; no automated alerting.",
              [["Manual rotation", "ops runbook", "no automation", "P19"]]),
        ]},
        {"id": "L2", "findings": [
            F("s-L2-0", "compass route %d" % loc_compass, "A", 98, "LOW", "INSTANCE", "The compass route is %d lines — the heaviest single handler." % loc_compass,
              [["%d lines" % loc_compass, "src/app/api/compass/route.ts", "L1-%d" % loc_compass, "P09"]]),
            F("s-L2-1", "ygate.ts %d" % loc_ygate, "B", 88, "MED", "INSTANCE", "ygate.ts is %d lines and carries the core gate logic." % loc_ygate,
              [["%d lines" % loc_ygate, "src/lib/ygate.ts", "L1-%d" % loc_ygate, "P10"]]),
            F("s-L2-2", "lattice_sim %d" % loc_sim, "B", 86, "LOW", "INSTANCE", "Observability load-test harness, %d lines, deterministic." % loc_sim,
              [["%d lines" % loc_sim, "scripts/lattice_sim.py", "L1-%d" % loc_sim, "P30"]]),
        ]},
        {"id": "L1", "findings": [
            F("s-L1-0", "L0–L5 prose prompt", "A", 98, "LOW", "CLASS", "The pipeline is a single L0–L5 prose prompt, not orchestrated agents.",
              [["Prose prompt", "src/app/api/compass/route.ts", "1 prompt", "P25"]]),
            F("s-L1-1", "arrays → TEXT", "A", 95, "LOW", "INSTANCE", "Structured arrays serialized to TEXT columns (SQLite-compat).",
              [["arrays→TEXT", "prisma/schema.prisma", "TEXT cols", "P27"]]),
            F("s-L1-2", "computeYGate %s" % ("tested" if has_tests else "unaudited"), "A" if has_tests else "C",
              95 if has_tests else 60, "LOW" if has_tests else "MED", "INSTANCE",
              "computeYGate %s." % ("has unit coverage" if has_tests else "ships without unit coverage"),
              [["%s" % ("tests present" if has_tests else "0 specs"), "src/lib/ygate.ts", "tests" if has_tests else "no tests", "P28"]]),
        ]},
    ]


# ── emit: swappable JSON payload + datasets manifest ─────────────────────────────
# The Observatory now loads a STATIC runtime (public/observatory/runtime.jsx) and
# hot-swaps these payloads at runtime. The generator NO LONGER writes JS — it writes
# data.<name>.json (the swappable payload) and updates datasets.json (the switcher
# manifest). The token maps + helpers that used to live here are now in runtime.jsx.

def slug_to_name(slug):
    return (slug or "").rstrip("/").split("/")[-1] or "dataset"


def update_manifest(out_dir, slug, name, label, file_name):
    """Idempotently add/replace this dataset's row in datasets.json (the switcher list)."""
    path = os.path.join(out_dir, "datasets.json")
    try:
        with open(path) as f:
            manifest = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        manifest = {"datasets": []}
    rows = [d for d in manifest.get("datasets", []) if d.get("slug") != slug]
    rows.append({"slug": slug, "name": name, "label": label, "file": file_name})
    rows.sort(key=lambda d: d.get("name", ""))
    manifest["datasets"] = rows
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    return path


def main():
    import argparse
    global REPO_SLUG, REPO_PATH, HIDE_ATTRIBUTION
    ap = argparse.ArgumentParser(description="Generate a swappable Observatory data payload (data.<name>.json) from a repo's real history.")
    ap.add_argument("--repo-path", default=REPO_PATH, help="dir to run git in (default: cwd)")
    ap.add_argument("--slug", default=REPO_SLUG, help="owner/repo for commit links")
    ap.add_argument("--out-dir", default="public/observatory", help="dir for data.<name>.json + datasets.json")
    ap.add_argument("--label", default=None, help="human label for the dataset switcher (default: derived from slug)")
    ap.add_argument("--attribution", choices=["show", "hide"], default="show",
                    help="show (default) keeps Co-Authored-By/tool trailers in event desc; hide scrubs them")
    args = ap.parse_args()
    REPO_PATH, REPO_SLUG = args.repo_path, args.slug
    HIDE_ATTRIBUTION = args.attribution == "hide"

    cs = commits()
    events = build_events(cs)
    risks, redacted = build_risks(cs)
    layers = build_layers(cs)

    start = cs[0]["date"] if cs else date.today().isoformat()
    span_days = max((date.today() - datetime.strptime(start, "%Y-%m-%d").date()).days + 2, 7)

    name = slug_to_name(REPO_SLUG)
    label = args.label or f"{name} — forensic git history"
    try:
        head = subprocess.check_output(["git", "-C", REPO_PATH, "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        head = ""

    payload = {
        "repo": REPO_SLUG,
        "label": label,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "head_sha": head,
        "attribution": "hidden" if HIDE_ATTRIBUTION else "shown",
        "span_start": start,
        "span_days": span_days,
        "redacted_open_risks": redacted,
        "events": events,
        "risks": risks,
        "layers": layers,
    }

    os.makedirs(args.out_dir, exist_ok=True)
    file_name = f"data.{name}.json"
    out_path = os.path.join(args.out_dir, file_name)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    manifest_path = update_manifest(args.out_dir, REPO_SLUG, name, label, file_name)

    print(f"wrote {out_path}")
    print(f"updated {manifest_path}")
    print(f"  events={len(events)}  risks={len(risks)} (public)  redacted_open={redacted}  layers={sum(len(l['findings']) for l in layers)} findings")
    print(f"  span: {start} +{span_days}d  head={head}")


if __name__ == "__main__":
    main()
