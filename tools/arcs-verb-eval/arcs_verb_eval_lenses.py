#!/usr/bin/env python3
"""
arcs_verb_eval_lenses.py - the MECHANICAL half of the five teardown lenses, stdlib only.

Wired into Evaluation by ARCS: a gauntlet at stakes:high (declared in the gauntlet JSON as
"stakes": "high", or set by config / --set evaluation.stakes=high) must carry all five lenses,
each lens must meet the output contract, and each lens's one cheap probe must pass. Any miss
is a failed gate, so the step exits 1 (fails closed). Below high stakes nothing here runs.

    BAR                 ruin / exposure      probe: locked stations refuse Auto (station-flags JSON)
    COURT               notomation / honesty probe: routes writing swipe/outcome/rubric require an
                                                    admin session, not the pipeline token
    KKL                 Kairos open windows  probe: a plan's slice windows vs open-loop deadlines
                                                    (the backlog review_by dates scripts/open_loops.py reads)
    FUN HOUSE           mirror / kryptonite  probe: stop-loss = slices shipped per send, computed
                                                    from ledgers; null with a reason when a ledger is absent
    ANTERIOR/POSTERIOR  op 21 belief update  probe: a prior file committed BEFORE the evidence step;
                                                    the posterior is diffed against it

What this module does NOT do: judge. Whether the ruin path is real, whether the dissent is a
straw man, whether a window is the right one: that stays the 0-2 rubric a person scores. A
regex that pretends to judge ruin is protection theater (seed-anti-protection-theater). Every
check below asks a question with one answer: does the file exist, does the line resolve, was
the prior committed first, does the number match the ledger.

Lens output contract (one object per lens in gauntlet["lenses"]):
    {"name": "BAR", "result": "pass|fail|dissent", "reason": "...",
     "verdict": "survives|survives_with_fix|fails",
     "evidence": ["path/to/file:42", ...],          >= 1, each resolves in the repo
     "forces":   ["doc.md#section", "src/x.ts"],    each names an existing file, or file#heading
     "confirmed": [...], "untested": [...]}         both lists present, no item in both
Probe inputs: gauntlet["probes"][<lens>] (paths relative to the repo root). See sample/high-stakes/.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import re
import subprocess
from pathlib import Path

LENS_VERDICTS = ("survives", "survives_with_fix", "fails")
REQUIRED = ("BAR", "COURT", "KKL", "FUN HOUSE", "ANTERIOR/POSTERIOR")
ALIASES = {"BAR": "BAR", "COURT": "COURT", "KKL": "KKL", "KAIROS": "KKL", "FUNHOUSE": "FUN HOUSE",
           "ANTERIORPOSTERIOR": "ANTERIOR/POSTERIOR", "OP21": "ANTERIOR/POSTERIOR"}
CITE_RE = re.compile(r"^(?P<path>[^:#\s]+):(?P<line>\d+)$")
WRITE_RE = re.compile(r"prisma\.(?P<model>[A-Za-z]+)\.(create|createMany|upsert|update|updateMany|delete|deleteMany)\b")
MUTATING_RE = re.compile(r"export\s+async\s+function\s+(POST|PUT|PATCH|DELETE)\b")
ADMIN_RE = re.compile(r"""caller\??\.kind\s*!==?\s*["']admin["']|\brequireAdmin(Session)?\(""")
DEFAULT_GUARDED_MODELS = r"swipe|outcome|rubric"
# src/lib/admin.ts doctrine: dev passes through outside production. The only carve-out sanctioned by default.
DEV_TERM_RE = re.compile(r"""^!\(\s*caller\??\.kind\s*===?\s*["']dev["']\s*&&\s*process\.env\.NODE_ENV\s*!==?\s*["']production["']\s*\)$""")


def canon(name: str) -> str | None:
    return ALIASES.get(re.sub(r"[^A-Z0-9]", "", (name or "").upper()))


def repo_root(repo=None) -> Path:
    if repo:
        return Path(repo).resolve()
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return Path.cwd()


def _slug(h: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")


# ---- 1. the output contract -----------------------------------------------------------
def cite_resolves(root: Path, cite: str) -> str | None:
    """None if path:line resolves, else the reason."""
    m = CITE_RE.match(str(cite).strip())
    if not m:
        return f"{cite!r} is not path:line"
    p = root / m["path"]
    if not p.is_file():
        return f"{m['path']} does not exist"
    n = len(p.read_text(errors="replace").splitlines())
    line = int(m["line"])
    return None if 1 <= line <= n else f"{cite} past end ({n} lines)"


def force_resolves(root: Path, item: str) -> str | None:
    """A forces item names an existing file, or file#heading where the heading exists."""
    path, _, anchor = str(item).strip().partition("#")
    path = path.split(":")[0]
    p = root / path
    if not path or not p.is_file():
        return f"{item!r} names no existing file"
    if anchor:
        heads = [re.sub(r"^#+\s*", "", l).strip() for l in p.read_text(errors="replace").splitlines() if l.startswith("#")]
        if _slug(anchor) not in {_slug(h) for h in heads}:
            return f"{item!r}: no heading {anchor!r} in {path}"
    return None


def contract(lens: dict, root: Path) -> list[str]:
    errs = []
    if lens.get("verdict") not in LENS_VERDICTS:
        errs.append(f"verdict {lens.get('verdict')!r} not in {'|'.join(LENS_VERDICTS)}")
    ev = lens.get("evidence") or []
    if not ev:
        errs.append("no evidence cite")
    errs += [e for e in (cite_resolves(root, c) for c in ev) if e]
    errs += [e for e in (force_resolves(root, f) for f in lens.get("forces") or []) if e]
    conf, unt = lens.get("confirmed"), lens.get("untested")
    if not isinstance(conf, list) or not isinstance(unt, list):
        errs.append("confirmed and untested must both be lists")
    else:
        both = set(map(str, conf)) & set(map(str, unt))
        if both:
            errs.append(f"in both confirmed and untested: {', '.join(sorted(both))}")
    return errs


def dissents(lens: dict) -> bool:
    return lens.get("verdict") in ("survives_with_fix", "fails") or lens.get("result") in ("fail", "dissent")


# ---- 2. one cheap probe per lens --------------------------------------------------------
def probe_bar(root: Path, cfg: dict) -> tuple[bool, str]:
    """Locked stations refuse Auto. Station-flags JSON: {"stations": [{"id", "locked", "auto"}]}."""
    p = root / str(cfg.get("stations", ""))
    if not cfg.get("stations") or not p.is_file():
        return False, f"station-flags config missing ({cfg.get('stations')!r}); fail closed"
    st = json.loads(p.read_text()).get("stations", [])
    if not st:
        return False, f"{cfg['stations']} lists no stations"
    bad = [s.get("id", "?") for s in st if s.get("locked") and (s.get("auto") or "auto" in (s.get("modes") or []))]
    locked = sum(bool(s.get("locked")) for s in st)
    return not bad, f"{locked}/{len(st)} stations locked" + (f"; locked but Auto allowed: {', '.join(bad)}" if bad else "; every locked station refuses Auto")


def _split_and(expr: str) -> list[str]:
    """Split an expression on top-level && (outside parens, brackets and strings)."""
    terms, depth, quote, cur, i = [], 0, None, "", 0
    while i < len(expr):
        c = expr[i]
        if quote:
            cur += c
            if c == "\\" and i + 1 < len(expr):
                cur, i = cur + expr[i + 1], i + 1
            elif c == quote:
                quote = None
        elif c in "\"'`":
            quote, cur = c, cur + c
        elif c in "([{":
            depth, cur = depth + 1, cur + c
        elif c in ")]}":
            depth, cur = depth - 1, cur + c
        elif expr.startswith("&&", i) and depth == 0:
            terms, cur, i = terms + [cur.strip()], "", i + 1
        else:
            cur += c
        i += 1
    return terms + [cur.strip()] if cur.strip() else terms


def admin_guards(src: str) -> list[tuple[str, list[str]]]:
    """For each `caller.kind !== "admin"` match: the full if (...) condition and its extra && terms (carve-outs)."""
    out = []
    for m in ADMIN_RE.finditer(src):
        if m.group(0).startswith("requireAdmin"):
            continue
        k = src.rfind("if", 0, m.start())
        op = src.find("(", k) if k >= 0 else -1
        if op < 0 or op > m.start():
            out.append((m.group(0), []))
            continue
        depth, end = 0, None
        for j in range(op, len(src)):
            depth += {"(": 1, ")": -1}.get(src[j], 0)
            if depth == 0:
                end = j
                break
        if end is None or end < m.end():
            out.append((m.group(0), []))
            continue
        cond = " ".join(src[op + 1:end].split())
        extra = [t for t in _split_and(cond) if not ADMIN_RE.search(t)]
        out.append((cond, extra))
    return out


def carve_name(term: str) -> str:
    t = term[1:].strip() if term.startswith("!") else term
    return t[1:-1].strip() if t.startswith("(") and t.endswith(")") else t


def probe_court(root: Path, cfg: dict) -> tuple[bool, str]:
    """Any route that writes a guarded model (swipe/outcome/rubric) must require an admin session.
    Every extra && term on the admin guard is a carve-out: the dev-outside-production term is sanctioned by
    default; any other must be declared in cfg["allowed_carveouts"] ({route, term, why}). The probe asks only
    whether a carve-out was declared, never whether it is acceptable."""
    base = root / str(cfg.get("routes", "src/app/api/jobs"))
    if not base.is_dir():
        return False, f"routes dir {base.relative_to(root) if base.is_relative_to(root) else base} missing; fail closed"
    guard = re.compile(cfg.get("guarded_models", DEFAULT_GUARDED_MODELS), re.I)
    declared = {(str(d.get("route", "")), str(d.get("term", ""))): str(d.get("why", ""))
                for d in cfg.get("allowed_carveouts", []) if isinstance(d, dict)}
    hits, bad, undeclared, noted = [], [], [], []
    for f in sorted(base.rglob("route.ts")):
        src = f.read_text(errors="replace")
        models = {m["model"] for m in WRITE_RE.finditer(src) if guard.search(m["model"])}
        if not models or not MUTATING_RE.search(src):
            continue
        rel = str(f.relative_to(root))
        hits.append(rel)
        if not ADMIN_RE.search(src):
            bad.append(f"{rel} ({', '.join(sorted(models))})")
            continue
        for _cond, extra in admin_guards(src):
            for t in extra:
                if DEV_TERM_RE.match(t):
                    continue
                name = carve_name(t)
                why = declared.get((rel, name))
                if why is None:
                    undeclared.append(f"{rel} term `{name}`")
                else:
                    noted.append(f"{rel} `{name}` declared: {why or 'no reason given'}")
    if not hits:
        return True, f"no route under {cfg.get('routes', 'src/app/api/jobs')} writes a guarded model"
    ev = f"{len(hits)} guarded-write routes"
    if bad:
        ev += f"; pipeline token or no admin check: {'; '.join(bad)}"
    if undeclared:
        ev += f"; undeclared carve-out on the admin guard (declare in probes.COURT.allowed_carveouts): {'; '.join(undeclared)}"
    if not bad and not undeclared:
        ev += "; all require an admin session"
    if noted:
        ev += f"; carve-outs: {'; '.join(noted)}"
    return not bad and not undeclared, ev


def _open_loops(root: Path):
    for d in (root, *Path(__file__).resolve().parents):
        p = d / "scripts" / "open_loops.py"
        if p.is_file():
            spec = importlib.util.spec_from_file_location("open_loops", p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None


def deadlines(root: Path, cfg: dict) -> tuple[list[tuple[str, dt.date]], str | None]:
    """Open-loop deadlines: backlog review_by dates, filtered exactly as scripts/open_loops.py does."""
    ol = _open_loops(root)
    if ol is None:
        return [], "scripts/open_loops.py not found"
    bl = root / str(cfg.get("backlog", "_QUEUE/induced-backlog.jsonl"))
    if not bl.is_file():
        return [], f"{bl.name} missing"
    out = []
    for r in ol._jsonl(bl):
        if "id" not in r or ol.DONE_RE.match(str(r.get("status_note") or r.get("status") or "open")) or ol.HELD_RE.search(str(r.get("status_note") or r.get("status") or "")):
            continue
        d = ol._date(r.get("review_by"))
        if d:
            out.append((r["id"], d))
    return out, None


def probe_kkl(root: Path, cfg: dict) -> tuple[bool, str]:
    """Every open-loop deadline that lands inside a slice window must be acknowledged by the plan."""
    p = root / str(cfg.get("plan", ""))
    if not cfg.get("plan") or not p.is_file():
        return False, f"plan missing ({cfg.get('plan')!r}); fail closed"
    plan = json.loads(p.read_text())
    slices = plan.get("slices", [])
    if not slices:
        return False, "plan has no slices"
    dl, why = deadlines(root, cfg)
    if why:
        return False, f"deadlines unreadable: {why}; fail closed"
    ack = set(plan.get("acknowledged", []))
    bad, collide = [], []
    for s in slices:
        try:
            a, b = dt.date.fromisoformat(s["start"]), dt.date.fromisoformat(s["end"])
        except (KeyError, ValueError):
            bad.append(f"{s.get('id', '?')} has no valid start/end")
            continue
        if a > b:
            bad.append(f"{s.get('id', '?')} starts after it ends")
        collide += [f"{rid} ({d}) inside {s.get('id', '?')}" for rid, d in dl if a <= d <= b and rid not in ack]
    issues = bad + collide
    return not issues, f"{len(slices)} slices vs {len(dl)} open deadlines" + (f"; unacknowledged: {'; '.join(issues)}" if issues else "; no unacknowledged collision")


def stop_loss(root: Path, cfg: dict, today: dt.date | None = None) -> dict:
    """slices shipped per send over a window. Null with a reason when a ledger is absent; never invented."""
    today = dt.date.fromisoformat(cfg["as_of"]) if cfg.get("as_of") else (today or dt.date.today())
    days = int(cfg.get("window_days", 7))
    lo = today - dt.timedelta(days=days)
    counts = {}
    for key in ("sends_ledger", "slices_ledger"):
        p = root / str(cfg.get(key, ""))
        if not cfg.get(key) or not p.is_file():
            return {"value": None, "reason": f"{key} absent ({cfg.get(key)!r})", "window_days": days}
        n = 0
        for line in p.read_text().splitlines():
            if line.strip():
                try:
                    d = dt.date.fromisoformat(str(json.loads(line).get("date", ""))[:10])
                except (ValueError, json.JSONDecodeError):
                    continue
                n += lo < d <= today
        counts[key] = n
    sends, slices = counts["sends_ledger"], counts["slices_ledger"]
    per_week = round(sends * 7 / days, 2)
    if sends == 0:
        return {"value": None, "reason": f"0 sends in {days}d (slices shipped {slices}); ratio undefined",
                "sends_per_week": per_week, "slices_shipped": slices, "window_days": days, "zero_sends": True}
    return {"value": round(slices / sends, 2), "sends_per_week": per_week, "slices_shipped": slices, "window_days": days}


def probe_funhouse(root: Path, cfg: dict, claimed=None) -> tuple[bool, str]:
    m = stop_loss(root, cfg)
    cap = cfg.get("max_slices_per_send")
    if claimed is not None and claimed != m["value"]:
        return False, f"lens claims stop_loss {claimed!r}, ledgers compute {m['value']!r} ({m.get('reason', 'computed')}); fabricated"
    if m["value"] is None:
        if m.get("zero_sends") and m["slices_shipped"] > 0 and cap is not None:
            return False, f"stop-loss tripped: {m['slices_shipped']} slices shipped, 0 sends in {m['window_days']}d"
        return True, f"stop_loss null: {m['reason']}"
    ok = cap is None or m["value"] <= cap
    return ok, (f"stop_loss {m['value']} slices/send ({m['sends_per_week']} sends/week, {m['slices_shipped']} slices, {m['window_days']}d)"
                + (f" > cap {cap}: building instead of sending" if not ok else ""))


def _commit_times(root: Path, rel: str) -> list[int]:
    out = subprocess.run(["git", "-C", str(root), "log", "--format=%ct", "--", rel], capture_output=True, text=True)
    return sorted(int(x) for x in out.stdout.split()) if out.returncode == 0 else []


def probe_posterior(root: Path, cfg: dict) -> tuple[bool, str]:
    """Prior committed (and never edited) before the evidence's first commit; posterior diffed against it."""
    for k in ("prior", "evidence", "posterior"):
        if not cfg.get(k) or not (root / cfg[k]).is_file():
            return False, f"{k} file missing ({cfg.get(k)!r}); fail closed"
    pt, et = _commit_times(root, cfg["prior"]), _commit_times(root, cfg["evidence"])
    if not pt:
        return False, f"prior {cfg['prior']} is not committed; no committed prior = fail"
    if not et:
        return False, f"evidence {cfg['evidence']} is not committed; order unprovable"
    if pt[-1] > et[0]:
        why = "committed after" if pt[0] > et[0] else "edited after"
        return False, f"prior {why} the evidence step (prior {pt[-1]} > evidence {et[0]}); post-hoc prior"
    prior = json.loads((root / cfg["prior"]).read_text()).get("beliefs", {})
    post = json.loads((root / cfg["posterior"]).read_text()).get("beliefs", {})
    new = sorted(set(post) - set(prior))
    if new:
        return False, f"posterior adds beliefs the prior never registered: {', '.join(new)}"
    moved = {k: (prior[k], post[k]) for k in post if post[k] != prior[k]}
    return True, f"{len(prior)} registered beliefs, {len(moved)} moved" + (": " + "; ".join(f"{k} {a}->{b}" for k, (a, b) in moved.items()) if moved else "")


PROBES = {"BAR": probe_bar, "COURT": probe_court, "KKL": probe_kkl, "ANTERIOR/POSTERIOR": probe_posterior}


# ---- 3. the gate set Evaluation runs at stakes:high -------------------------------------
def high_stakes(run, g: dict, repo=None) -> dict:
    """Adds the lens gates to an evaluation Run. Returns a summary carried into the print."""
    root = repo_root(repo)
    lenses = g.get("lenses", [])
    by = {}
    for l in lenses:
        c = canon(l.get("name", ""))
        if c:
            by[c] = l
    missing = [r for r in REQUIRED if r not in by]
    run.gate("lens-all-five", not missing, f"stakes:high needs {', '.join(REQUIRED)}" + (f"; missing: {', '.join(missing)}" if missing else "; all present"))
    errs = {n: contract(l, root) for n, l in by.items()}
    bad = {n: e for n, e in errs.items() if e}
    run.gate("lens-contract", not bad, f"{len(by) - len(bad)}/{len(by)} lenses meet the contract" + ("; " + " | ".join(f"{n}: {'; '.join(e)}" for n, e in bad.items()) if bad else ""))
    dis = [n for n, l in by.items() if dissents(l)]
    run.gate("lens-dissent", bool(dis), f"{len(dis)} lens(es) dissent: {', '.join(dis)}" if dis else "no lens verdict short of survives")
    probes = g.get("probes", {})
    pcfg = {canon(k): v for k, v in probes.items() if canon(k)}
    results = {}
    for name in REQUIRED:
        cfg = pcfg.get(name, {})
        if name == "FUN HOUSE":
            ok, ev = probe_funhouse(root, cfg, (by.get(name) or {}).get("stop_loss")) if cfg else (False, "no FUN HOUSE probe config; fail closed")
        else:
            ok, ev = PROBES[name](root, cfg)
        gid = "probe-" + re.sub(r"[^a-z]+", "-", name.lower()).strip("-")
        run.gate(gid, ok, ev)
        results[name] = {"ok": ok, "evidence": ev}
    return {"repo": str(root), "probes": results,
            "untested": {n: l.get("untested", []) for n, l in by.items()},
            "confirmed": {n: l.get("confirmed", []) for n, l in by.items()}}


# ---- self-test: every gate fails on its own bad fixture and passes on the good one -------
def _fixture() -> tuple[Path, dict]:
    import tempfile
    root = Path(tempfile.mkdtemp(prefix="arcs-lenses-"))
    git = lambda *a, **kw: subprocess.run(["git", "-C", str(root), *a], check=True, capture_output=True, env=kw.get("env"))
    import os
    git("init", "-q")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "self-test")
    files = {
        "spec.md": "# Job Factory\n\n## Stations\n\nForge, Send.\n\n## Stop loss\n\nOne slice per send.\n",
        "src/app/api/jobs/swipe/route.ts": 'export async function POST(req) {\n  const caller = await callerFor(req)\n  if (!caller || caller.kind !== "admin") return deny()\n  await prisma.jobSwipe.upsert({})\n}\n',
        "src/app/api/jobs/rubric/route.ts": 'export async function POST(req) {\n  const caller = await callerFor(req)\n  const evalRow = caller?.kind === "pipeline" && jobid.startsWith("eval-")\n  if (caller.kind !== "admin" && !(caller.kind === "dev" && process.env.NODE_ENV !== "production") && !evalRow) return deny()\n  await prisma.rubric.upsert({})\n}\n',
        "src/app/api/jobs/outcome/route.ts": 'export async function POST(req) {\n  const caller = await callerFor(req)\n  if (caller.kind !== "admin" && !(caller.kind === "dev" && process.env.NODE_ENV !== "production")) return deny()\n  await prisma.outcome.upsert({})\n}\n',
        "src/app/api/jobs/score/route.ts": "export async function POST(req) {\n  const caller = await callerFor(req)\n  await prisma.score.upsert({})\n}\n",
        "stations.json": json.dumps({"stations": [{"id": "send", "locked": True, "auto": False}, {"id": "scan", "locked": False, "auto": True}]}),
        "plan.json": json.dumps({"slices": [{"id": "s1", "start": "2026-10-06", "end": "2026-10-10"}], "acknowledged": ["lyndon"]}),
        "_QUEUE/induced-backlog.jsonl": json.dumps({"id": "lyndon", "status": "open", "review_by": "2026-10-08"}) + "\n" + json.dumps({"id": "old", "status": "DONE", "review_by": "2026-10-07"}) + "\n",
        "ledgers/sends.jsonl": "".join(json.dumps({"date": f"2026-10-0{d}"}) + "\n" for d in (1, 3)),
        "ledgers/slices.jsonl": "".join(json.dumps({"date": f"2026-10-0{d}"}) + "\n" for d in (1, 2, 4)),
        "beliefs/prior.json": json.dumps({"beliefs": {"p1": 0.6, "p2": 0.3}}),
    }
    for rel, body in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body)
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-10-01T10:00:00", "GIT_COMMITTER_DATE": "2026-10-01T10:00:00"}
    git("add", "-A")
    git("commit", "-qm", "prior + fixtures", env=env)
    (root / "beliefs/evidence.md").write_text("# Evidence\n\nThe call happened.\n")
    (root / "beliefs/posterior.json").write_text(json.dumps({"beliefs": {"p1": 0.8, "p2": 0.3}}))
    env2 = {**os.environ, "GIT_AUTHOR_DATE": "2026-10-03T10:00:00", "GIT_COMMITTER_DATE": "2026-10-03T10:00:00"}
    git("add", "-A")
    git("commit", "-qm", "evidence", env=env2)

    def lens(name, verdict="survives", **kw):
        return {"name": name, "result": "dissent" if verdict != "survives" else "pass", "reason": f"{name} read",
                "verdict": verdict, "evidence": ["spec.md:3"], "forces": ["spec.md#stations"],
                "confirmed": ["send station locked"], "untested": ["recruiter reply rate"], **kw}
    g = {"stakes": "high", "verdict": "conditional pass",
         "conditions": [{"id": "k1", "claim": "", "action": "degrade", "text": "add a stop-loss row"}],
         "lenses": [lens("BAR", "survives_with_fix"), lens("COURT"), lens("KKL"),
                    lens("FUN HOUSE", stop_loss=1.5), lens("ANTERIOR/POSTERIOR", "fails")],
         "probes": {"BAR": {"stations": "stations.json"},
                    "COURT": {"routes": "src/app/api/jobs", "allowed_carveouts": [
                        {"route": "src/app/api/jobs/rubric/route.ts", "term": "evalRow", "why": "eval-* rows driven by the trigger eval"}]},
                    "KKL": {"plan": "plan.json"},
                    "FUN HOUSE": {"sends_ledger": "ledgers/sends.jsonl", "slices_ledger": "ledgers/slices.jsonl",
                                  "as_of": "2026-10-05", "window_days": 7, "max_slices_per_send": 2},
                    "ANTERIOR/POSTERIOR": {"prior": "beliefs/prior.json", "evidence": "beliefs/evidence.md",
                                           "posterior": "beliefs/posterior.json"}}}
    return root, g


def _commit_late_prior(root: Path):
    import os
    (root / "beliefs/late.json").write_text(json.dumps({"beliefs": {"p1": 0.8}}))
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-10-04T10:00:00", "GIT_COMMITTER_DATE": "2026-10-04T10:00:00"}
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "late prior"], check=True, env=env, capture_output=True)


def _mut(g, fn):
    g = json.loads(json.dumps(g))
    fn(g)
    return g


def _lens(g, name):
    return next(l for l in g["lenses"] if canon(l["name"]) == name)


BAD = [
    ("lens-all-five", lambda g: g["lenses"].pop()),
    ("lens-contract", lambda g: _lens(g, "BAR").update(verdict="mostly fine")),
    ("lens-contract", lambda g: _lens(g, "COURT").update(evidence=[])),
    ("lens-contract", lambda g: _lens(g, "COURT").update(evidence=["spec.md:999"])),
    ("lens-contract", lambda g: _lens(g, "KKL").update(forces=["spec.md#no-such-section"])),
    ("lens-contract", lambda g: _lens(g, "KKL").update(forces=["vibes"])),
    ("lens-contract", lambda g: _lens(g, "BAR").update(untested=["send station locked"])),
    ("lens-contract", lambda g: _lens(g, "BAR").pop("untested")),
    ("lens-dissent", lambda g: [l.update(verdict="survives", result="pass") for l in g["lenses"]]),
    ("probe-bar", lambda g: g["probes"]["BAR"].update(stations="nope.json")),
    ("probe-court", lambda g: g["probes"]["COURT"].update(guarded_models="swipe|score")),
    ("probe-court", lambda g: g["probes"]["COURT"].pop("allowed_carveouts")),
    ("probe-court", lambda g: g["probes"]["COURT"].update(allowed_carveouts=[{"route": "src/app/api/jobs/swipe/route.ts", "term": "evalRow", "why": "wrong route"}])),
    ("probe-kkl", lambda g: g["probes"]["KKL"].update(plan="plan-unack.json")),
    ("probe-fun-house", lambda g: _lens(g, "FUN HOUSE").update(stop_loss=0.5)),
    ("probe-fun-house", lambda g: g["probes"]["FUN HOUSE"].update(max_slices_per_send=1)),
    ("probe-anterior-posterior", lambda g: g["probes"]["ANTERIOR/POSTERIOR"].update(prior="beliefs/uncommitted.json")),
    ("probe-anterior-posterior", lambda g: g["probes"]["ANTERIOR/POSTERIOR"].update(prior="beliefs/late.json")),
    ("probe-anterior-posterior", lambda g: g["probes"]["ANTERIOR/POSTERIOR"].update(posterior="beliefs/post-new.json")),
]


def self_test() -> int:
    import arcs_verb_eval as core
    root, good = _fixture()
    (root / "plan-unack.json").write_text(json.dumps({"slices": [{"id": "s1", "start": "2026-10-06", "end": "2026-10-10"}]}))
    (root / "beliefs/uncommitted.json").write_text(json.dumps({"beliefs": {"p1": 0.6}}))
    (root / "beliefs/post-new.json").write_text(json.dumps({"beliefs": {"p1": 0.8, "p9": 0.9}}))
    _commit_late_prior(root)
    passed = failed = 0

    def check(cond, msg):
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")

    run = lambda g, **kw: core.evaluate("evaluation", json.dumps(g), repo=root, **kw)
    rep = run(good)
    check(rep["ok"], "high-stakes good gauntlet passes every lens gate" + ("" if rep["ok"] else f"  failed: {rep['failed']}"))
    check(rep.get("lenses", {}).get("probes", {}).get("FUN HOUSE", {}).get("evidence", "").startswith("stop_loss 1.5"),
          "FUN HOUSE: stop_loss computed from ledgers (3 slices / 2 sends = 1.5)")
    for gate, fn in BAD:
        r = run(_mut(good, fn))
        check(gate in r["failed"] and not r["ok"], f"{gate:<26} fires" + ("" if gate in r["failed"] else f"  (failed: {r['failed']})"))
    court = rep.get("lenses", {}).get("probes", {}).get("COURT", {}).get("evidence", "")
    check("`evalRow` declared: eval-* rows" in court and "outcome" not in court.split("carve-outs:")[-1],
          "COURT: declared carve-out named in evidence; dev-outside-production term sanctioned silently")
    r = run(_mut(good, lambda g: g["probes"]["COURT"].pop("allowed_carveouts")))
    check("rubric/route.ts term `evalRow`" in r["lenses"]["probes"]["COURT"]["evidence"], "COURT: undeclared carve-out names route and term")
    # stop-loss honesty: a missing ledger yields null with a reason, and a lens claiming a number fails
    nul = _mut(good, lambda g: (g["probes"]["FUN HOUSE"].pop("sends_ledger"), _lens(g, "FUN HOUSE").update(stop_loss=None)))
    r = run(nul)
    ev = r["lenses"]["probes"]["FUN HOUSE"]["evidence"]
    check(r["ok"] and "null" in ev and "sends_ledger absent" in ev, "FUN HOUSE: ledger absent -> null with reason, not a number")
    fab = _mut(nul, lambda g: _lens(g, "FUN HOUSE").update(stop_loss=1.5))
    check("probe-fun-house" in run(fab)["failed"], "FUN HOUSE: a number claimed over an absent ledger fails as fabricated")
    # stakes switch: config can raise to high; below high no lens gate runs
    low = _mut(good, lambda g: (g.pop("stakes"), g.pop("probes")))
    r = run(low)
    check(r["ok"] and not any(x["id"] in ("lens-all-five", "lens-contract", "lens-dissent") or x["id"].startswith("probe-") for x in r["gates"]), "stakes absent -> lens gates do not run")
    r = run(low, stakes="high")
    check(not r["ok"] and "probe-bar" in r["failed"], "config stakes=high on a probe-less gauntlet fails closed")
    r = run(_mut(good, lambda g: g.update(stakes="high")), stakes="low")
    check("lens-all-five" in [x["id"] for x in r["gates"]], "config cannot lower a gauntlet that declares stakes:high")
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(self_test())
