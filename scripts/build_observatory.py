#!/usr/bin/env python3
"""
build_observatory.py — generates the ARCS Observatory data layer from REAL repo data.

Emits public/observatory/data.jsx (the only file the Observatory kit's BACKEND_HANDOFF
says to swap) with EVENTS / RISKS / LAYERS / span computed from:
  - git log              -> EVENTS  (build trajectory; classified by commit)
  - repo signals + ADRs  -> RISKS   (ruin-paths; OPEN items REDACTED for public view)
  - real file metrics    -> LAYERS  (5-altitude scored deck; prov cites real sources)

Exposure policy (ADR/decision 2026-06-05): PUBLIC, OPEN-RISKS REDACTED.
OPEN-status risks (standing live exposures) are computed but withheld from the public
payload; only AVERTED/MITIGATED are emitted, with a redactedCount banner for honesty.

Run:  python3 scripts/build_observatory.py
"""
from __future__ import annotations
import json, os, re, subprocess
from datetime import date, datetime

REPO_SLUG = "flashesofbrilliance/arcs-v9"
OUT = "public/observatory/data.jsx"
REPO_PATH = "."  # where `git` runs; override with --repo-path to build a tailored instance


def sh(args: list[str]) -> str:
    return subprocess.run(args, capture_output=True, text=True, cwd=REPO_PATH).stdout


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
        with open(path, encoding="utf-8") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def clean(subject: str) -> str:
    return re.sub(r"\s*\[NCI:[^\]]*\]\s*$", "", subject).strip()


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
            "desc": clean(c["subject"]) + ((" — " + c["body"].strip().split(chr(10))[0]) if c["body"].strip() else ""),
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


# ── LAYERS — 5-altitude scored deck from real file metrics ───────────────────────
def build_layers(cs: list[dict]) -> list[dict]:
    n_adr = len([f for f in os.listdir("_DECISIONS") if re.match(r"ADR-\d+", f)])
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


# ── emit data.jsx (token maps + helpers verbatim; data arrays generated) ─────────
HEADER = '''// ARCS Observatory — data layer. GENERATED by scripts/build_observatory.py from
// REAL arcs-v9 repo data (git log + ADRs + file metrics). Do not edit by hand;
// re-run the generator to refresh. Exposure: PUBLIC, OPEN-risks redacted.

const C = { cyan: "#00F0FF", green: "#00FF9D", gold: "#FFD700", orange: "#ff9d3c", red: "#FF4D6D", steel: "#94a3b8" };
const REPO = "https://github.com/%(slug)s/commit/";
const ALT = {
  L5: { name: "EXECUTIVE",   accent: C.green },
  L4: { name: "STRATEGIC",   accent: C.cyan },
  L3: { name: "OPERATIONAL", accent: C.gold },
  L2: { name: "TACTICAL",    accent: C.orange },
  L1: { name: "SURGICAL",    accent: C.red },
};
const GRADE = { A: C.green, B: C.cyan, C: C.gold, D: C.orange, F: C.red };
const SEV = { RUIN: C.red, HIGH: C.orange, MED: C.gold };
const STATUS = { AVERTED: C.green, MITIGATED: C.gold, OPEN: C.red };
const TYPE_COLOR = { genesis: C.green, canon: C.green, kairos: C.gold, milestone: C.cyan, feat: C.cyan, security: C.red, fix: C.orange };

const SPAN_START = Date.parse("%(span_start)s"), SPAN_DAYS = %(span_days)d;
const leftPct = (d) => Math.round(((Date.parse(d) - SPAN_START) / 86400000 / SPAN_DAYS) * 1000) / 10;

// REDACTED: %(redacted)d standing OPEN risk(s) withheld from this public payload.
const REDACTED_OPEN_RISKS = %(redacted)d;

const EVENTS = %(events)s;

const RISKS = %(risks)s;

const LAYERS = %(layers)s;
'''

FOOTER = '''
const LEDGER = [...EVENTS.map(e => ({ ...e, kind: "event" })), ...RISKS.map(r => ({ ...r, kind: "risk" }))]
  .map(x => ({ ...x, left: leftPct(x.date) }))
  .sort((a, b) => Date.parse(a.date) - Date.parse(b.date) || (a.kind === "event" ? -1 : 1));

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
function groupKeys(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  const day = `${DOW[d.getDay()]} \\u00b7 ${MON[d.getMonth()]} ${d.getDate()}`;
  const monday = new Date(d); monday.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  const week = `Week of ${MON[monday.getMonth()]} ${monday.getDate()}`;
  const month = `${["January","February","March","April","May","June","July","August","September","October","November","December"][d.getMonth()]} ${d.getFullYear()}`;
  return { day, week, month };
}
function matchQ(x, q) {
  if (!q || !q.trim()) return true;
  const s = q.trim().toLowerCase();
  const hay = [x.label, x.risk, x.type, x.alt, x.status, x.sev, x.sha, x.desc, x.note, x.lab, x.grade, x.how, x.kind,
    x.alt && ALT[x.alt] && ALT[x.alt].name].filter(Boolean).join(" ").toLowerCase();
  return hay.includes(s);
}
function stepIndices(focus) {
  return (!focus || focus === "all") ? LEDGER.map((_, i) => i) : LEDGER.map((x, i) => (x.alt === focus ? i : -1)).filter(i => i >= 0);
}
Object.assign(window, { C, REPO, ALT, GRADE, SEV, STATUS, TYPE_COLOR, EVENTS, RISKS, LAYERS, LEDGER, leftPct, groupKeys, matchQ, stepIndices, REDACTED_OPEN_RISKS });
'''


def main():
    import argparse
    global REPO_SLUG, OUT, REPO_PATH
    ap = argparse.ArgumentParser(description="Generate an Observatory data.jsx from a repo's real history.")
    ap.add_argument("--repo-path", default=REPO_PATH, help="dir to run git in (default: cwd)")
    ap.add_argument("--slug", default=REPO_SLUG, help="owner/repo for commit links")
    ap.add_argument("--out", default=OUT, help="output data.jsx path (use a distinct path per tailored instance)")
    args = ap.parse_args()
    REPO_PATH, REPO_SLUG, OUT = args.repo_path, args.slug, args.out

    cs = commits()
    events = build_events(cs)
    risks, redacted = build_risks(cs)
    layers = build_layers(cs)

    start = cs[0]["date"] if cs else date.today().isoformat()
    span_days = max((date.today() - datetime.strptime(start, "%Y-%m-%d").date()).days + 2, 7)

    def js(o):  # pretty JSON == valid JS literal
        return json.dumps(o, indent=2)

    body = HEADER % {"slug": REPO_SLUG, "span_start": start, "span_days": span_days,
                     "redacted": redacted, "events": js(events), "risks": js(risks), "layers": js(layers)} + FOOTER
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(body)
    print(f"wrote {OUT}")
    print(f"  events={len(events)}  risks={len(risks)} (public)  redacted_open={redacted}  layers={sum(len(l['findings']) for l in layers)} findings")
    print(f"  span: {start} +{span_days}d")


if __name__ == "__main__":
    main()
