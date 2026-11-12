#!/usr/bin/env python3
"""compounding_fit: run the pre-registered compounding fit. Stdlib, read-only, no model calls.

Rules live in _PATTERNS/2026-11-11-compounding-preregistration.md (merged PR 2156, ef4d20f3). This script reads them,
it never sets them; a change to a threshold here without an amendment there is a bug.

Inputs (all local, all read-only):
  - _QUEUE/induced-backlog.jsonl                         rows, state DONE
  - _STATE/job-search/universe/sources/decision-receipts.json   (refresh: scripts/universe_receipts_adapter.py --export)
  - gh pr list (merged PRs: number, head branch, additions, deletions)
  - ~/.claude/projects/*/*.jsonl                          session transcripts, joined to rows by gitBranch
  - git log --diff-filter=A                               first-add date of every file, for the reuse share

  python3 scripts/compounding_fit.py [--until YYYY-MM-DD] [--fit-hit] [--json]
  python3 scripts/compounding_fit.py --self-test

--fit-hit computes measure 7 (first-rank hit rate) by running each row's own-date copy of scripts/prior_art.py in a
temporary detached worktree. Slow (one checkout per row); off by default, and the report says "not computed" without it.
Exit: 0 report printed · 1 missing input.
"""
import argparse, collections, datetime as dt, glob, json, math, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKLOG = os.path.join(ROOT, "_QUEUE", "induced-backlog.jsonl")
RECEIPTS = os.path.join(ROOT, "_STATE", "job-search", "universe", "sources", "decision-receipts.json")
START = dt.date(2026, 10, 20)
READ_DATE = dt.date(2026, 12, 15)
FLOOR = 30          # pre-registered sample floor
AIC_MARGIN = 4.0    # pre-registered
Z90 = 1.645         # normal approximation for the 90% interval (stated, not tuned)
UPKEEP_WORDS = ("fix", "repair", "drift", "stale", "gate", "hygiene", "refresh", "regen", "reconcile")

# USD per million tokens: (input, output, cache read). Cache writes: 1.25x input (5 min TTL), 2x input (1 h TTL).
# Source: bundled claude-api skill, shared/models.md and shared/prompt-caching.md (read 2026-11-11). List prices;
# the plan is flat, so every figure is a shadow cost.
# Keyed by family-and-version substring of the transcript's model string (not a model choice, so not MODELS.<role>);
# first match wins, so a longer version sits before its prefix.
RATES = [
    ("fable-5-1", (10, 50, 0.25)), ("fable-5", (10, 50, 1.0)), ("mythos-5", (10, 50, 1.0)),
    ("opus-5-5", (4, 20, 0.20)), ("opus-5", (5, 25, 0.50)),
    ("sonnet-5-5", (2, 10, 0.20)), ("haiku-5-5", (0.10, 0.50, 0.01)),  # haiku cache read assumed 0.1x input
]
FALLBACK = "opus-5-5"
TOP_TIER = ("fable", "mythos", "opus")
TOOL_RE = re.compile(r"(?:\./)?(scripts/[\w./-]+\.(?:py|sh|mjs)|operators/[\w./-]+\.py)")
PR_RE = re.compile(r"/pull/(\d+)")


# ---------- small stats (stdlib) ----------
def solve(A, b):
    n = len(A); M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            return None
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def inverse(A):
    n = len(A); cols = []
    for j in range(n):
        e = [1.0 if i == j else 0.0 for i in range(n)]
        x = solve(A, e)
        if x is None:
            return None
        cols.append(x)
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def ols(X, y):
    """X rows include the intercept column. Returns beta, se, aic, n, p (or None if singular / too few)."""
    n, p = len(X), len(X[0])
    if n <= p + 1:
        return None
    XtX = [[sum(X[k][i] * X[k][j] for k in range(n)) for j in range(p)] for i in range(p)]
    Xty = [sum(X[k][i] * y[k] for k in range(n)) for i in range(p)]
    inv = inverse(XtX)
    if inv is None:
        return None
    beta = [sum(inv[i][j] * Xty[j] for j in range(p)) for i in range(p)]
    rss = sum((y[k] - sum(beta[i] * X[k][i] for i in range(p))) ** 2 for k in range(n))
    s2 = rss / (n - p)
    se = [math.sqrt(max(inv[i][i] * s2, 0.0)) for i in range(p)]
    aic = n * math.log(max(rss, 1e-300) / n) + 2 * p
    return {"beta": beta, "se": se, "aic": aic, "n": n, "p": p}


def logistic(X, y, iters=50):
    p = len(X[0]); b = [0.0] * p
    for _ in range(iters):
        mu = [1 / (1 + math.exp(-max(min(sum(b[i] * x[i] for i in range(p)), 30), -30))) for x in X]
        g = [sum((y[k] - mu[k]) * X[k][i] for k in range(len(X))) for i in range(p)]
        H = [[sum(mu[k] * (1 - mu[k]) * X[k][i] * X[k][j] for k in range(len(X))) for j in range(p)] for i in range(p)]
        step = solve(H, g)
        if step is None:
            return None
        b = [bi + si for bi, si in zip(b, step)]
        if max(abs(s) for s in step) < 1e-8:
            break
    inv = inverse(H)
    if inv is None:
        return None
    return {"beta": b, "se": [math.sqrt(max(inv[i][i], 0.0)) for i in range(p)], "n": len(X)}


def ci(fit, i):
    return (fit["beta"][i] - Z90 * fit["se"][i], fit["beta"][i] + Z90 * fit["se"][i])


# ---------- data ----------
def load_rows():
    rows = {}
    for line in open(BACKLOG):
        line = line.strip()
        if line:
            r = json.loads(line); rows[r["id"]] = r
    return rows


def as_list(v):
    if isinstance(v, list):
        return v
    if isinstance(v, str) and v.startswith("["):
        try:
            import ast
            return ast.literal_eval(v)
        except Exception:
            return [v]
    return [v] if v else []


def load_receipts():
    if not os.path.exists(RECEIPTS):
        return None
    d = json.load(open(RECEIPTS))
    return d if isinstance(d, list) else next(v for v in d.values() if isinstance(v, list))


def parse_ts(s):
    s = str(s).replace(" ", "T")
    s = re.sub(r"\+00$", "+00:00", s).replace("Z", "+00:00")
    s = re.sub(r"\.(\d+)", lambda m: "." + (m.group(1) + "000000")[:6], s)  # py3.9 wants 6 fraction digits
    return dt.datetime.fromisoformat(s)


def merged_prs():
    out = subprocess.run(["gh", "pr", "list", "--state", "merged", "--limit", "3000",
                          "--json", "number,headRefName,additions,deletions"],
                         capture_output=True, text=True, cwd=ROOT)
    if out.returncode:
        sys.exit("gh pr list failed: " + out.stderr.strip())
    return {p["number"]: p for p in json.loads(out.stdout)}


def first_add_dates():
    out = subprocess.run(["git", "log", "--diff-filter=A", "--name-only", "--format=@%as", "--reverse"],
                         capture_output=True, text=True, cwd=ROOT).stdout
    first, day = {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            day = line[1:]
        elif line and line not in first:
            first[line] = day
    return first


def scan_transcripts(branches):
    """Per branch: shadow cost, user turns, top-tier output share, tools run. Replies deduplicated by message id."""
    agg = {b: {"cost": 0.0, "turns": 0, "out": 0, "top_out": 0, "tools": set(), "unpriced_models": set()}
           for b in branches}
    seen = set()
    for path in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")) + \
            glob.glob(os.path.expanduser("~/.claude/projects/*/*/subagents/*.jsonl")):
        try:
            fh = open(path, errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if '"gitBranch"' not in line:
                    continue
                m = re.search(r'"gitBranch":"([^"]+)"', line)
                if not m or m.group(1) not in agg:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                a = agg[d["gitBranch"]]
                msg = d.get("message") or {}
                if d.get("type") == "user" and isinstance(msg.get("content"), str):
                    a["turns"] += 1
                if d.get("type") != "assistant":
                    continue
                for c in msg.get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        inp = c.get("input") or {}
                        if c.get("name") == "Bash":
                            a["tools"].update(TOOL_RE.findall(inp.get("command", "")))
                        elif c.get("name") == "Skill" and inp.get("skill"):
                            a["tools"].add(".claude/skills/%s/SKILL.md" % inp["skill"].split(":")[-1])
                mid, u = msg.get("id"), msg.get("usage")
                if not u or mid in seen:
                    continue
                seen.add(mid)
                model = msg.get("model") or FALLBACK
                rate = next((r for k, r in RATES if k in model), None)
                if rate is None:
                    a["unpriced_models"].add(model); rate = dict(RATES)[FALLBACK]
                rin, rout, rread = rate
                cc = u.get("cache_creation") or {}
                w1h = cc.get("ephemeral_1h_input_tokens", 0)
                w5m = cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) - w1h)
                a["cost"] += (u.get("input_tokens", 0) * rin + u.get("output_tokens", 0) * rout
                              + u.get("cache_read_input_tokens", 0) * rread
                              + w5m * rin * 1.25 + w1h * rin * 2.0) / 1e6
                a["out"] += u.get("output_tokens", 0)
                if any(t in model for t in TOP_TIER):
                    a["top_out"] += u.get("output_tokens", 0)
    return agg


def fit_hit(row, tools_run):
    """Measure 7: does the row's own-date prior_art rank first a tool the row ran? 1/0, or None if it cannot run."""
    rev = subprocess.run(["git", "rev-list", "-1", "--before=%sT23:59:59" % row["added"], "origin/main"],
                         capture_output=True, text=True, cwd=ROOT).stdout.strip()
    if not rev:
        return None
    d = tempfile.mkdtemp(prefix="fit-hit-")
    try:
        subprocess.run(["git", "worktree", "add", "--detach", "-q", d, rev], cwd=ROOT, check=True,
                       capture_output=True)
        if not os.path.exists(os.path.join(d, "scripts", "prior_art.py")):
            return None
        out = subprocess.run([sys.executable, "scripts/prior_art.py", row.get("jtbd", row["id"])],
                             capture_output=True, text=True, cwd=d, timeout=120).stdout
        m = re.search(r"best \[[^\]]*\] tool:\w+:(\S+)", out)
        if not m:
            return None
        name = m.group(1)
        return 1 if any(t.endswith(name) or name in t for t in tools_run) else 0
    except (subprocess.SubprocessError, OSError):
        return None
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", d], cwd=ROOT, capture_output=True)


# ---------- assembly ----------
def build(until, want_hit):
    rows = load_rows()
    rec = load_receipts()
    if rec is None:
        sys.exit("no receipt export; run: python3 scripts/universe_receipts_adapter.py --export")
    by_job = collections.defaultdict(list)
    for r in rec:
        j = r.get("job_id") or ""
        if j.startswith("job:backlog:"):
            by_job[j[len("job:backlog:"):]].append(r)
    done = []
    for rid, row in rows.items():
        rs = by_job.get(rid)
        if row.get("state") != "DONE" or not rs:
            continue
        closed = max(parse_ts(r["event_at"]) for r in rs)
        prs = {int(n) for r in rs for ref in as_list(r.get("refs")) for n in PR_RE.findall(str(ref))}
        done.append({"id": rid, "row": row, "closed": closed, "prs": prs})
    done.sort(key=lambda x: x["closed"])
    for i, d in enumerate(done):
        d["X"] = i + 1  # cumulative closed rows, this one included (ln X defined at the first row)
    window = [d for d in done if START <= d["closed"].date() <= until]
    pr = merged_prs()
    for d in window:
        d["branches"] = {pr[n]["headRefName"] for n in d["prs"] if n in pr}
        d["size"] = sum(pr[n]["additions"] + pr[n]["deletions"] for n in d["prs"] if n in pr)
    agg = scan_transcripts({b for d in window for b in d["branches"]})
    first = first_add_dates()
    out = []
    for d in window:
        parts = [agg[b] for b in d["branches"]]
        cost = sum(p["cost"] for p in parts)
        tools = set().union(*[p["tools"] for p in parts]) if parts else set()
        added = str(d["row"].get("added", ""))[:10]
        pre = {t for t in tools if first.get(t) and first[t] <= added}
        o_all = sum(p["out"] for p in parts)
        rec_ = {
            "id": d["id"], "closed": d["closed"].date().isoformat(), "X": d["X"],
            "t": (d["closed"].date() - START).days, "cost": cost, "turns": sum(p["turns"] for p in parts),
            "r": (len(pre) / len(tools)) if tools else None, "k": len(pre),
            "top_share": (sum(p["top_out"] for p in parts) / o_all) if o_all else 0.0,
            "size": d["size"], "prio": {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(d["row"].get("priority"), 2),
            "upkeep": int(any(w in (d["id"] + " " + d["row"].get("jtbd", "")).lower() for w in UPKEEP_WORDS)),
            "unpriced": sorted(set().union(*[p["unpriced_models"] for p in parts])) if parts else [],
        }
        if want_hit:
            rec_["f"] = fit_hit(d["row"], tools)
        out.append(rec_)
    return out


def analyze(data, until):
    priced = [d for d in data if d["cost"] > 0]
    rep = {"window": [START.isoformat(), until.isoformat()], "rows_closed_in_window": len(data),
           "rows_with_cost": len(priced), "dropped_no_transcript": len(data) - len(priced),
           "upkeep_last_two_weeks": None, "models": {}, "verdict": {}}
    last2 = [d for d in data if (until - dt.date.fromisoformat(d["closed"])).days < 14]
    if last2:
        rep["upkeep_last_two_weeks"] = sum(d["upkeep"] for d in last2) / len(last2)
    if len(priced) < FLOOR:
        rep["verdict"]["compounding"] = "too few to say (n=%d, floor %d); grain fidelity" % (len(priced), FLOOR)
        return rep
    raw = lambda d: [d["top_share"], math.log1p(d["size"]), d["prio"]]
    keep = [i for i in range(3) if len({round(raw(d)[i], 9) for d in priced}) > 1]  # constant controls drop out
    ctrl = lambda d: [raw(d)[i] for i in keep]
    y = [math.log(d["cost"]) for d in priced]
    yh = [math.log1p(d["turns"]) for d in priced]
    M0 = ols([[1] + ctrl(d) for d in priced], y)
    M1 = ols([[1, math.log(d["X"])] + ctrl(d) for d in priced], y)
    M2 = ols([[1, d["t"]] + ctrl(d) for d in priced], y)
    m3rows = [d for d in priced if d["r"] is not None]
    M3 = ols([[1, math.log(d["X"]), d["r"], math.log1p(d["k"])] + ctrl(d) for d in m3rows],
             [math.log(d["cost"]) for d in m3rows]) if len(m3rows) >= FLOOR else None
    H0 = ols([[1] + ctrl(d) for d in priced], yh)
    H1 = ols([[1, math.log(d["X"])] + ctrl(d) for d in priced], yh)
    for name, f in (("M0", M0), ("M1", M1), ("M2", M2), ("M3", M3), ("H0", H0), ("H1", H1)):
        rep["models"][name] = None if f is None else {"aic": round(f["aic"], 2), "n": f["n"],
                                                      "beta": [round(b, 4) for b in f["beta"]],
                                                      "se": [round(s, 4) for s in f["se"]]}
    v = rep["verdict"]
    if not (M0 and M1 and M2):
        v["compounding"] = "fit failed (singular design); no verdict"
        return rep
    b, (lo, hi) = -M1["beta"][1], ci(M1, 1)  # model is ln c = a - b ln X, so b = -coef
    rep["b"] = {"estimate": round(b, 4), "ci90": [round(-hi, 4), round(-lo, 4)]}
    upkeep_fail = rep["upkeep_last_two_weeks"] is not None and rep["upkeep_last_two_weeks"] > 0.5
    if -hi > 0 and M0["aic"] - M1["aic"] >= AIC_MARGIN and not upkeep_fail:
        v["compounding"] = "supported"
    elif -hi <= 0 <= -lo or b < 0 or upkeep_fail:
        v["compounding"] = "falsified" + (" (upkeep share above 50%)" if upkeep_fail else "")
    else:
        v["compounding"] = "not shown (b positive but M1 does not beat M0 by %g AIC)" % AIC_MARGIN
    k_neg = M3 is not None and ci(M3, 3)[1] < 0
    if M1["aic"] - M2["aic"] >= AIC_MARGIN and k_neg:
        v["shape"] = "exponential"
    elif v["compounding"] == "supported":
        v["shape"] = "power law"
    else:
        v["shape"] = "no detectable trend"
    hits = [d for d in priced if d.get("f") is not None]
    if not any("f" in d for d in data):
        v["fit"] = "not computed (run with --fit-hit)"
    elif len(hits) < FLOOR:
        v["fit"] = "too few to say (n=%d)" % len(hits)
    else:
        L = logistic([[1, math.log(d["X"])] for d in hits], [d["f"] for d in hits])
        Mf = ols([[1, math.log(d["X"]), d["r"] or 0, d["f"]] + ctrl(d) for d in hits],
                 [math.log(d["cost"]) for d in hits])
        rises = L is not None and ci(L, 1)[0] > 0
        pays = Mf is not None and ci(Mf, 3)[1] < 0
        v["fit"] = ("supported" if rises and pays else
                    "matching improved without paying off yet" if rises else "mechanism not shown")
    if H0 and H1:
        att = ci(H1, 1)[1] < 0 and H0["aic"] - H1["aic"] >= AIC_MARGIN
        v["attention"] = "falls with X" if att else "does not fall with X (attention is the unpriced cost)"
    return rep


def self_test():
    import random
    random.seed(7)
    mk = lambda i, c: {"id": "r%d" % i, "closed": (START + dt.timedelta(days=i % 50)).isoformat(), "X": i + 1,
                       "t": i % 50, "cost": c, "turns": 5, "r": 0.5, "k": 2, "top_share": random.random(),
                       "size": random.randint(10, 500), "prio": 2, "upkeep": 0, "unpriced": []}
    until = START + dt.timedelta(days=60)
    power = [mk(i, 50 * (i + 1) ** -0.4 * math.exp(random.gauss(0, 0.2))) for i in range(80)]
    flat = [mk(i, 5 * math.exp(random.gauss(0, 0.2))) for i in range(80)]
    few = power[:10]
    ok = True
    for name, data, want in (("power", power, "supported"), ("flat", flat, "falsified"), ("few", few, "too few")):
        got = analyze(data, until)["verdict"]["compounding"]
        good = got.startswith(want)
        ok &= good
        print("%-5s %-4s want %-10s got %s" % (name, "ok" if good else "FAIL", want, got))
    up = [dict(d, upkeep=1) for d in power]
    got = analyze(up, until)["verdict"]["compounding"]
    good = got.startswith("falsified (upkeep")
    ok &= good
    print("upkeep %-4s want falsified (upkeep) got %s" % ("ok" if good else "FAIL", got))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--until", default=None, help="last close date counted (default: today, capped at the read date)")
    ap.add_argument("--fit-hit", action="store_true", help="compute measure 7 (slow: one checkout per row)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    until = dt.date.fromisoformat(a.until) if a.until else min(dt.date.today(), READ_DATE)
    data = build(until, a.fit_hit)
    rep = analyze(data, until)
    if a.json:
        print(json.dumps({"report": rep, "rows": data}, indent=1, default=str)); return
    print("compounding fit (rules: _PATTERNS/2026-11-11-compounding-preregistration.md)")
    print("window %s to %s · closed %d · with cost %d · dropped (no transcript) %d" % (
        rep["window"][0], rep["window"][1], rep["rows_closed_in_window"], rep["rows_with_cost"],
        rep["dropped_no_transcript"]))
    if data:
        tot = sum(d["cost"] for d in data)
        print("shadow cost, list prices: total $%.2f · median per priced row $%.2f" % (
            tot, sorted(d["cost"] for d in data if d["cost"] > 0)[len([d for d in data if d["cost"] > 0]) // 2]
            if rep["rows_with_cost"] else 0))
    if rep["upkeep_last_two_weeks"] is not None:
        print("upkeep share, last two weeks: %.0f%%" % (100 * rep["upkeep_last_two_weeks"]))
    for k, m in rep["models"].items():
        if m:
            print("  %s aic %.1f n %d beta %s" % (k, m["aic"], m["n"], m["beta"]))
    if "b" in rep:
        e = rep["b"]["estimate"]
        print("b (elasticity of cost to closed rows) %s, 90%% CI %s; cost change per doubling %+.0f%%" % (
            e, rep["b"]["ci90"], 100 * (2 ** -e - 1)))
    tag = "verdict" if until >= READ_DATE else "interim"
    for k, v in rep["verdict"].items():
        print("%s %-11s %s" % (tag, k, v))
    if until < READ_DATE:
        print("interim read: the pre-registered verdict is the %s read, not this one" % READ_DATE)


if __name__ == "__main__":
    main()
