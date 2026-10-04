#!/usr/bin/env python3
"""nftt_published: one frozen publish timestamp per NFTT post, stamped into the post itself.

Why this exists (2026-10-04): a series preoccupied with time shipped 32 posts with no publish
date on any of them. No <time>, no article:published_time, nothing a reader or a crawler could
read. Nobody noticed because no gate asked. This is the Frustration Gate for that class
(AGENTS.md #15): a routed post without a stamp fails CI.

What "published" means here: the moment the post's route ('/blog/nftt/<slug>' in src/proxy.ts)
first became part of origin/main, because good.arcs.care deploys from main and the route is
what makes a post reachable (the story factory keeps drafts unrouted until the bless).
  1. X = the earliest non-merge commit on main's history that added the route string
  2. M = the first commit on main's TRUE line that contains X, where the true line follows first
     parents but hops to the second parent at a sync merge ("Merge ... 'origin/main' into ...")
  published_at = committer date of M, shown in America/New_York.
Why the hop: a few branches were fast-forwarded onto main, so the plain first-parent line
detours through their sync merges and branch commits, and claimed five posts a day after
PR #505 had already shipped them. A sync merge's second parent is where main really was.

SSOT: runtime/specs/nftt-published.json. Committed, because CI checks out shallow and cannot
re-derive deep history. A recorded timestamp is never rewritten by `derive`; a post is
published once.

Usage:
  python3 scripts/nftt_published.py derive        # add ledger rows for routed posts that lack one
                                                  # (needs full history: git fetch --unshallow)
  python3 scripts/nftt_published.py derive --now <slug>
                                                  # new post not yet on main: record now, method=stamped
  python3 scripts/nftt_published.py stamp         # write <time> + article:published_time into posts
  python3 scripts/nftt_published.py --check       # exit 1 if any routed post lacks a ledger row or stamp
  python3 scripts/nftt_published.py --self-test
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "runtime", "specs", "nftt-published.json")
PROXY = os.path.join(ROOT, "src", "proxy.ts")
TZ = ZoneInfo("America/New_York")
MAIN = "origin/main"
ROUTE_FILES = ["src/proxy.ts", "src/middleware.ts", "middleware.ts", "next.config.ts"]

# A top-level post route: '/blog/nftt/<slug>': '/blog-nftt-<file>.html' (sub-paths like /full are tiers).
ROUTE_RE = re.compile(r"'/blog/nftt/([a-z0-9-]+)':\s*'/(blog-nftt-[a-z0-9-]+\.html)'")
BYLINE_RE = re.compile(r'(<p class="byline"[^>]*>)')
STAMP_RE = re.compile(r'<time data-pub datetime="[^"]*">[^<]*</time> &middot; ')
ORIG_RE = re.compile(r'<span data-orig>.*?</span> &middot; ')
ORIGINALS = os.path.join(ROOT, "runtime", "specs", "nftt-originals.json")
META_RE = re.compile(r'<meta property="article:published_time" content="[^"]*">\n?')


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def routes(proxy_text=None):
    """slug -> served file, for every top-level /blog/nftt/<slug> route."""
    if proxy_text is None:
        with open(PROXY, encoding="utf-8") as f:
            proxy_text = f.read()
    return {s: f for s, f in ROUTE_RE.findall(proxy_text)}


def load():
    if not os.path.exists(LEDGER):
        return {}
    with open(LEDGER, encoding="utf-8") as f:
        return json.load(f)["posts"]


def save(posts):
    doc = {
        "_about": "One frozen publish timestamp per routed NFTT post. Written by scripts/nftt_published.py; "
                  "never hand-edit a recorded row. published_at = first time the route reached origin/main.",
        "posts": dict(sorted(posts.items(), key=lambda kv: kv[1]["published_at"])),
    }
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")


def iso_et(epoch):
    return datetime.fromtimestamp(int(epoch), TZ).isoformat()


SYNC_RE = re.compile(r"^Merge (remote-tracking )?branch '(origin/)?main' into ")
PR_NUM_RE = re.compile(r"\(#\d+\)$")  # a GitHub squash merge ends its subject with (#N)


def true_main_line():
    """origin/main's real history, oldest first: first parents, except that a sync merge
    ("Merge origin/main into <branch>", fast-forwarded onto main later) hands over to its
    second parent, which is where main actually was."""
    meta = {}
    for row in git("log", MAIN, "--format=%H|%P|%ct|%s").splitlines():
        h, parents, ct, subject = row.split("|", 3)
        meta[h] = (parents.split(), int(ct), subject)
    line, c = [], git("rev-parse", MAIN)
    while c:
        line.append(c)
        parents, _, subject = meta[c]
        if not parents:
            break
        c = parents[1] if SYNC_RE.match(subject) and len(parents) > 1 else parents[0]
    line.reverse()
    return line, meta


def derive_from_git(slug, line, meta):
    needle = f"'/blog/nftt/{slug}'"
    adds = git("log", MAIN, "--reverse", "--no-merges", f"-S{needle}", "--format=%H", "--", *ROUTE_FILES).split()
    if not adds:
        return None
    x = adds[0]
    # Ancestry is monotonic along a parent chain, so bisect for the first commit containing X.
    lo, hi = 0, len(line) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if subprocess.run(["git", "merge-base", "--is-ancestor", x, line[mid]], cwd=ROOT).returncode == 0:
            hi = mid
        else:
            lo = mid + 1
    m = line[lo]
    row = {"published_at": iso_et(meta[m][1]), "main_commit": m[:8], "route_commit": x[:8],
           "method": "git-route-on-main"}
    parents, _, subject = meta[m]
    if len(parents) == 1 and not PR_NUM_RE.search(subject):
        # Pushed straight onto main: git keeps the commit time, never the push time.
        row["method"] = "git-direct-commit"
        row["note"] = "commit time, a lower bound: the push to main is not recorded in git"
    return row


def cmd_derive(now=None):
    posts = load()
    live = routes()
    if now is not None:
        slug = now
        if slug not in live:
            sys.exit(f"[nftt-published] no route for '{slug}' in src/proxy.ts; route it first")
        if slug in posts:
            sys.exit(f"[nftt-published] '{slug}' already recorded at {posts[slug]['published_at']}; not rewriting")
        posts[slug] = {"published_at": datetime.now(TZ).replace(microsecond=0).isoformat(), "method": "stamped"}
        save(posts)
        print(f"[nftt-published] recorded {slug} at {posts[slug]['published_at']} (stamped)")
        return 0
    if git("rev-parse", "--is-shallow-repository") == "true":
        sys.exit("[nftt-published] shallow clone: run `git fetch --unshallow origin main` first")
    line, meta = true_main_line()
    added = 0
    for slug in live:
        if slug in posts:
            continue
        row = derive_from_git(slug, line, meta)
        if row is None:
            print(f"[nftt-published] {slug}: route not on {MAIN} yet; use `derive --now {slug}` once blessed")
            continue
        posts[slug] = row
        added += 1
        print(f"[nftt-published] {slug}: {row['published_at']} (main {row['main_commit']})")
    save(posts)
    print(f"[nftt-published] {added} added, {len(posts)} recorded")
    return 0


def human(iso):
    d = datetime.fromisoformat(iso).astimezone(TZ)
    hour = d.strftime("%I").lstrip("0")
    return f"{d.strftime('%b')} {d.day}, {d.year} &middot; {hour}:{d.strftime('%M %p')} ET"


def origin_segment(o):
    """'From the LinkedIn original(s), <dates>' for a post written from earlier pieces; each date in a <time>."""
    ds = [datetime.strptime(d, "%Y-%m-%d") for d in o["dates"]]
    same_year = len({d.year for d in ds}) == 1
    parts = [f'<time datetime="{d:%Y-%m-%d}">{d:%b} {d.day}' + ("" if same_year else f", {d.year}") + "</time>" for d in ds]
    joined = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    if same_year:
        joined += f", {ds[0].year}"
    label = "original" if len(ds) == 1 else "originals"
    return f'<span data-orig>From the {o["platform"]} {label}, {joined}</span> &middot; '


def stamp_text(html, iso, origin=None):
    """Idempotently write the head meta, the byline <time>, and (if any) the originals segment. Returns new html."""
    html = META_RE.sub("", html)
    html = html.replace("</title>\n", f'</title>\n<meta property="article:published_time" content="{iso}">\n', 1)
    html = STAMP_RE.sub("", html)
    html = ORIG_RE.sub("", html)
    tag = f'<time data-pub datetime="{iso}">Published {human(iso)}</time> &middot; '
    if origin:
        tag += origin_segment(origin)
    html, n = BYLINE_RE.subn(lambda m: m.group(1) + tag, html, count=1)
    if n == 0:
        raise ValueError("no <p class=\"byline\"> to stamp")
    return html


def load_originals():
    if not os.path.exists(ORIGINALS):
        return {}
    with open(ORIGINALS, encoding="utf-8") as f:
        return json.load(f)["posts"]


def problems(posts, live, read, originals=None):
    originals = originals or {}
    out = []
    for slug, fname in sorted(live.items()):
        row = posts.get(slug)
        if not row:
            out.append(f"{slug}: routed but no ledger row (run: nftt_published.py derive)")
            continue
        html = read(fname)
        iso = row["published_at"]
        if f'<meta property="article:published_time" content="{iso}">' not in html:
            out.append(f"{fname}: missing/stale article:published_time (run: nftt_published.py stamp)")
        if f'<time data-pub datetime="{iso}">Published {human(iso)}</time>' not in html:
            out.append(f"{fname}: missing/stale byline <time> (run: nftt_published.py stamp)")
        if slug in originals:
            if origin_segment(originals[slug]) not in html:
                out.append(f"{fname}: missing/stale originals segment (run: nftt_published.py stamp)")
        elif "<span data-orig>" in html:
            out.append(f"{fname}: carries an originals segment with no row in nftt-originals.json")
    for slug in originals:
        if slug not in live:
            out.append(f"{slug}: in nftt-originals.json but not a routed post")
    return out


def _read(fname):
    with open(os.path.join(ROOT, "public", fname), encoding="utf-8") as f:
        return f.read()


def cmd_stamp():
    posts, live, originals = load(), routes(), load_originals()
    for slug, fname in sorted(live.items()):
        if slug not in posts:
            print(f"[nftt-published] skip {slug}: no ledger row")
            continue
        path = os.path.join(ROOT, "public", fname)
        before = _read(fname)
        after = stamp_text(before, posts[slug]["published_at"], originals.get(slug))
        if after != before:
            with open(path, "w", encoding="utf-8") as f:
                f.write(after)
            print(f"[nftt-published] stamped {fname}")
    return 0


def cmd_check():
    bad = problems(load(), routes(), _read, load_originals())
    for b in bad:
        print(f"[nftt-published] FAIL {b}", file=sys.stderr)
    if bad:
        return 1
    print(f"[nftt-published] check: {len(routes())} routed posts stamped")
    return 0


def self_test():
    page = '<title>X · NFTT</title>\n<body><p class="byline">Field notes</p></body>'
    iso = "2026-10-03T18:52:22-04:00"
    ok = 0
    once = stamp_text(page, iso)
    ok += human(iso) == "Oct 3, 2026 &middot; 6:52 PM ET"
    ok += stamp_text(once, iso) == once                                 # idempotent
    ok += once.count("article:published_time") == 1
    ok += '<p class="byline"><time data-pub datetime="2026-10-03T18:52:22-04:00">' in once
    live = routes("'/blog/nftt/a': '/blog-nftt-a.html', '/blog/nftt/a/full': '/blog-nftt-a.html'")
    ok += live == {"a": "blog-nftt-a.html"}                              # tiers are not posts
    ok += len(problems({}, live, lambda f: once)) == 1                   # fail-on-bad: no row
    ok += len(problems({"a": {"published_at": iso}}, live, lambda f: page)) == 2   # fail-on-bad: unstamped
    ok += problems({"a": {"published_at": iso}}, live, lambda f: once) == []      # pass-on-good
    try:
        stamp_text("<title>x</title>\n", iso)
    except ValueError:
        ok += 1                                                          # no byline is loud
    ok += bool(SYNC_RE.match("Merge remote-tracking branch 'origin/main' into claude/x"))  # sync: hop
    ok += bool(SYNC_RE.match("Merge branch 'main' into claude/x"))                      # sync: hop
    ok += not SYNC_RE.match("Merge branch 'claude/x'")                   # merging a branch INTO main is real
    ok += not SYNC_RE.match("Merge pull request #505 from x/y")          # a PR merge is real
    one = {"platform": "LinkedIn", "dates": ["2026-01-30"]}
    span = {"platform": "LinkedIn", "dates": ["2019-02-07", "2025-09-12"]}
    three = {"platform": "LinkedIn", "dates": ["2026-01-30", "2026-02-19", "2026-05-25"]}
    ok += origin_segment(one) == '<span data-orig>From the LinkedIn original, <time datetime="2026-01-30">Jan 30</time>, 2026</span> &middot; '
    ok += 'Feb 7, 2019</time> and <time datetime="2025-09-12">Sep 12, 2025</time></span>' in origin_segment(span)
    ok += 'originals, <time datetime="2026-01-30">Jan 30</time>, <time datetime="2026-02-19">Feb 19</time> and <time datetime="2026-05-25">May 25</time>, 2026<' in origin_segment(three)
    withorig = stamp_text(once, iso, one)
    ok += stamp_text(withorig, iso, one) == withorig and withorig.count("data-orig") == 1   # idempotent
    ok += len(problems({"a": {"published_at": iso}}, live, lambda f: once, {"a": one})) == 1  # fail-on-bad: missing
    ok += len(problems({"a": {"published_at": iso}}, live, lambda f: withorig, {})) == 1      # fail-on-bad: orphan
    ok += problems({"a": {"published_at": iso}}, live, lambda f: withorig, {"a": one}) == []  # pass-on-good
    ok += "data-orig" not in stamp_text(withorig, iso, None)            # removable
    ok_cli, n_cli = cli_self_test()
    ok += ok_cli
    total = 21 + n_cli
    print(f"[nftt-published] self-test {ok}/{total}")
    return 0 if ok == total else 1


def cli_self_test():
    """Run this script as a subprocess from a copy inside a throwaway repo (ROOT follows __file__,
    so the copy's ROOT is the temp dir). Asserts argv strictness and that look-only modes write nothing."""
    page = '<title>X</title>\n<body><p class="byline">Field notes</p></body>'
    iso = "2026-10-03T18:52:22-04:00"
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        for d in ("scripts", os.path.join("runtime", "specs"), "public", "src"):
            os.makedirs(os.path.join(tmp, d))
        me = os.path.join(tmp, "scripts", "nftt_published.py")
        shutil.copy(os.path.abspath(__file__), me)
        with open(os.path.join(tmp, "src", "proxy.ts"), "w") as f:
            f.write("'/blog/nftt/a': '/blog-nftt-a.html',\n'/blog/nftt/b': '/blog-nftt-b.html',\n")
        for slug in ("a", "b"):
            with open(os.path.join(tmp, "public", f"blog-nftt-{slug}.html"), "w") as f:
                f.write(page)
        with open(os.path.join(tmp, "runtime", "specs", "nftt-published.json"), "w") as f:
            json.dump({"posts": {"a": {"published_at": iso}}}, f)
        ledger = os.path.join(tmp, "runtime", "specs", "nftt-published.json")

        def snap():
            out = {}
            for d, _, fs in os.walk(tmp):
                for fn in fs:
                    fp = os.path.join(d, fn)
                    with open(fp, "rb") as f:
                        out[fp] = (os.stat(fp).st_mtime_ns, hashlib.sha256(f.read()).hexdigest())
            return out

        def run(*a):
            return subprocess.run([sys.executable, me, *a], cwd=tmp, capture_output=True, text=True).returncode

        def case(name, ok):
            results.append(ok)
            if not ok:
                print(f"[nftt-published] FAIL cli: {name}")

        base = snap()
        case("unknown flag exits 2", run("--bogus") == 2)
        case("unknown flag on stamp exits 2", run("stamp", "--bogus") == 2)
        case("extra positional on stamp exits 2", run("stamp", "extra") == 2)
        case("unknown flag on derive exits 2", run("derive", "--dry-run") == 2)
        case("extra positional on derive exits 2", run("derive", "--now", "b", "extra") == 2)
        case("derive --now with no value exits 2", run("derive", "--now") == 2)
        case("unknown command exits 2", run("publish") == 2)
        case("no args exits 2", run() == 2)
        case("--check on unstamped fixture exits 1", run("--check") == 1)
        case("--check and rejected argv write nothing", snap() == base)
        case("derive --now b exits 0", run("derive", "--now", "b") == 0)
        with open(ledger) as f:
            case("derive --now writes the ledger row", "b" in json.load(f)["posts"])
        with open(ledger) as f:
            before = f.read()
        case("derive --now on a recorded slug refuses", run("derive", "--now", "b") != 0)
        with open(ledger) as f:
            case("refused derive leaves the ledger", f.read() == before)
        case("real stamp exits 0", run("stamp") == 0)
        after = snap()
        case("--check after stamp exits 0", run("--check") == 0)
        case("--check on current fixture writes nothing", snap() == after)
    return sum(results), len(results)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="nftt_published.py", description="One frozen publish timestamp per NFTT post.")
    ap.add_argument("--check", action="store_true", help="exit 1 if any routed post lacks a ledger row or stamp (writes nothing)")
    ap.add_argument("--self-test", action="store_true", help="run the built-in tests (writes only to a temp dir)")
    sub = ap.add_subparsers(dest="cmd")
    d = sub.add_parser("derive", help="add ledger rows for routed posts that lack one")
    d.add_argument("--now", metavar="SLUG", help="new post not yet on main: record now, method=stamped")
    sub.add_parser("stamp", help="write <time> + article:published_time into posts")
    args = ap.parse_args(argv)
    # Precedence kept from the hand parser: --self-test, then --check, then the subcommand.
    if args.self_test:
        return self_test()
    if args.check:
        return cmd_check()
    if args.cmd == "derive":
        return cmd_derive(args.now)
    if args.cmd == "stamp":
        return cmd_stamp()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
