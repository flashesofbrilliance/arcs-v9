#!/usr/bin/env python3
"""linkedin_cut: gate the LinkedIn draft queue (one source essay -> five altitude cuts).

The queue lives in _QUEUE/linkedin/<id>.json. Drafting is judgment (a human or Claude writes the
cuts); this script is the mechanical half. It never posts anything: publishing stays Zach's click.

Altitude ladder (bite-sized -> Flintstone gauge), one thesis carried through all five:
  exec        image      caption <= 40 words, one line on the card
  strategic   poll       question <= 140 chars, 2-4 options <= 30 chars (LinkedIn limits)
  operational carousel   6-10 slides, <= 40 words per slide
  tactical    post       120-260 words, ends with the series footer
  surgical    article    >= 700 words, opens with the AEO answer, cites primary sources

Gates per cut (any miss exits 1):
  expected (pre-registered impressions band, dated before the post: Op 19 closes against it)
  slop_lint (clichés + em-dashes)   provenance_lint (every metric covered by the queue's evidence)
  altitude_canary --strict (article) series footer (post/carousel/article)   PII grep
  AEO: question ends in '?', answer 40-60 words and verbatim in the article's first paragraph,
       every named entity appears in the article, >= 1 primary source URL.

Usage:
  python3 scripts/linkedin_cut.py check [_QUEUE/linkedin/*.json]   # gate (default: whole queue)
  python3 scripts/linkedin_cut.py today [--date YYYY-MM-DD]          # print the cut due today
  python3 scripts/linkedin_cut.py --self-test                        # proves fail-on-bad + argv contract
`check` and `today` are read-only (check lints copies in a temp dir); unknown flags exit 2.
Video: the `video` cut type lives in scripts/video_cut.py (shot spec in _QUEUE/video/ -> HTML scene
for html_video_render.mjs + a per-beat prompt pack); it reuses these gates rather than forking them.
Stdlib only.
"""
import glob, json, os, re, subprocess, sys, tempfile, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUEUE = os.path.join(ROOT, "_QUEUE", "linkedin")
SCRIPTS = os.path.join(ROOT, "scripts")
ORDER = ["exec", "strategic", "operational", "tactical", "surgical"]
FOOTER_FORMATS = {"post", "carousel", "article"}
PII = [re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}")]


def words(s):
    return len(re.findall(r"\S+", s or ""))


def cut_text(c):
    parts = [c.get("text", ""), c.get("caption", "")]
    if c.get("poll"):
        parts += [c["poll"]["question"]] + c["poll"]["options"]
    parts += c.get("slides", [])
    return "\n\n".join(p for p in parts if p)


def run(script, *args):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args],
                       capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def shape_errors(c):
    f, e = c["format"], []
    if f == "image":
        if not c.get("caption") or words(c["caption"]) > 40: e.append("image caption missing or > 40 words")
        if not c.get("card_line"): e.append("image needs card_line (the one line on the card)")
    elif f == "poll":
        p = c.get("poll") or {}
        if len(p.get("question", "")) > 140: e.append("poll question > 140 chars")
        opts = p.get("options", [])
        if not 2 <= len(opts) <= 4: e.append("poll needs 2-4 options")
        e += [f"poll option > 30 chars: {o!r}" for o in opts if len(o) > 30]
    elif f == "carousel":
        s = c.get("slides", [])
        if not 6 <= len(s) <= 10: e.append(f"carousel has {len(s)} slides (want 6-10)")
        e += [f"slide {i+1} > 40 words" for i, t in enumerate(s) if words(t) > 40]
    elif f == "post":
        n = words(c.get("text"))
        if not 120 <= n <= 260: e.append(f"post is {n} words (want 120-260)")
    elif f == "article":
        if words(c.get("text")) < 700: e.append("article < 700 words")
    else:
        e.append(f"unknown format {f!r}")
    return e


def aeo_errors(q, article):
    a, e = q.get("aeo") or {}, []
    if not a.get("question", "").endswith("?"): e.append("aeo.question must be a question")
    n = words(a.get("answer"))
    if not 40 <= n <= 60: e.append(f"aeo.answer is {n} words (want 40-60)")
    first = (article or "").strip().split("\n\n")[0]
    if a.get("answer") and a["answer"] not in first:
        e.append("aeo.answer must appear verbatim in the article's first paragraph")
    e += [f"entity not named in article: {x}" for x in a.get("entities", []) if x not in (article or "")]
    if not any(u.startswith("http") for u in a.get("sources", [])): e.append("aeo.sources needs >= 1 URL")
    return e


def check_file(path):
    q = json.load(open(path))
    errs = []
    for k in ("id", "show", "thesis", "index_url", "cuts"):
        if not q.get(k): errs.append(f"missing {k}")
    footer = f"Part of {q.get('show')}"
    alts = [c.get("altitude") for c in q.get("cuts", [])]
    if alts != ORDER: errs.append(f"cuts must run {ORDER}, got {alts}")
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "evidence.jsonl"), "w") as fh:
            for ev in q.get("evidence", []):
                fh.write(json.dumps(ev) + "\n")
        article = None
        for c in q.get("cuts", []):
            tag = f"[{c.get('altitude')}/{c.get('format')}]"
            text = cut_text(c)
            errs += [f"{tag} {m}" for m in shape_errors(c)]
            ex = c.get("expected") or {}
            if not (isinstance(ex.get("impressions_low"), int) and isinstance(ex.get("impressions_high"), int)
                    and ex["impressions_low"] <= ex["impressions_high"] and ex.get("registered_at")):
                errs.append(f"{tag} expected: pre-register impressions_low/high + registered_at before posting (Op 19 closes against it)")
            elif c.get("date") and ex["registered_at"] > c["date"]:
                errs.append(f"{tag} expected registered after the post date: that is a retrofit, not a prediction")
            if c.get("format") in FOOTER_FORMATS and footer not in text:
                errs.append(f"{tag} missing series footer '{footer}'")
            errs += [f"{tag} PII-shaped string: {m.group(0)}" for r in PII for m in r.finditer(text)]
            ext = ".md" if c.get("format") == "article" else ".txt"
            fp = os.path.join(d, f"{c.get('altitude')}{ext}")
            open(fp, "w").write(text)
            for script, args in (("slop_lint.py", [fp]), ("provenance_lint.py", [fp])):
                rc, out = run(script, *args)
                if rc: errs.append(f"{tag} {script}: {out.splitlines()[-1] if out else 'fail'}")
            if c.get("format") == "article":
                article = c.get("text")
                rc, out = run("altitude_canary.py", "--strict", fp)
                if rc: errs.append(f"{tag} altitude_canary: NO GROUND RETURN")
        errs += [f"[aeo] {m}" for m in aeo_errors(q, article)]
    return errs


def cmd_check(paths):
    paths = paths or sorted(glob.glob(os.path.join(QUEUE, "*.json")))
    bad = 0
    for p in paths:
        errs = check_file(p)
        print(f"[{'FAIL' if errs else 'PASS'}] {os.path.relpath(p, ROOT)}")
        for e in errs: print(f"   - {e}")
        bad += bool(errs)
    return 1 if bad else 0


def cmd_today(date):
    hits = []
    for p in sorted(glob.glob(os.path.join(QUEUE, "*.json"))):
        q = json.load(open(p))
        hits += [(q, c) for c in q["cuts"] if c.get("date") == date and c.get("status") != "posted"]
    if not hits:
        print(f"linkedin_cut: nothing scheduled for {date}"); return 0
    for q, c in hits:
        print(f"== {date} · {q['show']} · {c['altitude']}/{c['format']} · status={c.get('status')}")
        if c.get("card_line"): print(f"CARD: {c['card_line']}")
        print(cut_text(c))
        if c.get("first_comment"): print(f"\nFIRST COMMENT: {c['first_comment']}")
        print()
    return 0


def legacy_fail_on_bad():
    """The original fail-on-bad cases against the real queue (in-process, read-only)."""
    good = sorted(glob.glob(os.path.join(QUEUE, "*.json")))
    assert good, "no queue files to test against"
    q = json.load(open(good[0]))
    assert not check_file(good[0]), f"good fixture should pass: {check_file(good[0])}"
    names = []
    with tempfile.TemporaryDirectory() as d:
        mutations = {
            "em-dash": lambda q: q["cuts"][3].__setitem__("text", q["cuts"][3]["text"] + " \u2014 end"),
            "uncited metric": lambda q: q["cuts"][3].__setitem__("text", q["cuts"][3]["text"] + " It grew 87%."),
            "no footer": lambda q: q["cuts"][3].__setitem__("text", q["cuts"][3]["text"].replace(f"Part of {q['show']}", "")),
            "no prior": lambda q: q["cuts"][2].pop("expected"),
            "aeo drift": lambda q: q["aeo"].__setitem__("answer", "Short answer that is not in the article at all " * 5),
        }
        for name, mut in mutations.items():
            m = json.loads(json.dumps(q)); mut(m)
            fp = os.path.join(d, "t.json"); json.dump(m, open(fp, "w"))
            assert check_file(fp), f"mutation '{name}' should fail"
            names.append(name)
    return names


def _snapshot(root):
    import hashlib
    out = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(dp, f)
            out[p] = (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.stat(p).st_mtime_ns)
    return out


def self_test():
    import shutil
    fails = total = 0

    def ok(name, cond):
        nonlocal fails, total
        total += 1; fails += 0 if cond else 1
        print(("  PASS  " if cond else "  FAIL  ") + name)

    try:
        for n in legacy_fail_on_bad():
            ok(f"fail-on-bad: {n}", True)
    except AssertionError as e:
        ok(f"fail-on-bad suite: {e}", False)

    tmp = os.path.realpath(tempfile.mkdtemp(prefix="linkedin-cut-selftest-"))
    try:
        os.makedirs(os.path.join(tmp, "scripts")); os.makedirs(os.path.join(tmp, "_QUEUE", "linkedin"))
        me = os.path.join(tmp, "scripts", "linkedin_cut.py")
        shutil.copy2(os.path.abspath(__file__), me)
        for dep in ("slop_lint.py", "provenance_lint.py", "altitude_canary.py"):
            if os.path.exists(os.path.join(SCRIPTS, dep)):
                shutil.copy2(os.path.join(SCRIPTS, dep), os.path.join(tmp, "scripts", dep))
        fx = {"id": "synthetic", "show": "Synthetic Show", "thesis": "t", "index_url": "https://example.test/x",
              "cuts": [{"altitude": "exec", "format": "image", "caption": "A short synthetic caption.",
                        "card_line": "Synthetic line", "date": "2030-01-02", "status": "draft"}]}
        json.dump(fx, open(os.path.join(tmp, "_QUEUE", "linkedin", "synthetic.json"), "w"))

        def run(*a):
            return subprocess.run([sys.executable, me, *a], capture_output=True, text=True, cwd=tmp)

        before = _snapshot(tmp)
        ok("no command exits 2", run().returncode == 2)
        ok("unknown flag exits 2", run("--bogus").returncode == 2)
        ok("unknown subcommand exits 2", run("chek").returncode == 2)
        ok("check unknown flag exits 2", run("check", "--bogus").returncode == 2)
        ok("today unknown flag exits 2", run("today", "--bogus").returncode == 2)
        ok("today extra positional exits 2", run("today", "extra").returncode == 2)
        ok("today --date without value exits 2", run("today", "--date").returncode == 2)
        ok("today bad date exits 2", run("today", "--date", "2030-13-40").returncode == 2)
        ok("--self-test with a subcommand exits 2", run("--self-test", "check").returncode == 2)
        r = run("today", "--date", "2030-01-02")
        ok("today prints the due cut", r.returncode == 0 and "Synthetic line" in r.stdout)
        r = run("today", "--date", "2030-01-03")
        ok("today empty day exits 0", r.returncode == 0 and "nothing scheduled" in r.stdout)
        r = run("check")
        ok("check flags a malformed queue (exit 1)", r.returncode == 1 and "[FAIL]" in r.stdout)
        r = run("check", os.path.join("_QUEUE", "linkedin", "synthetic.json"))
        ok("check with explicit path runs", r.returncode == 1 and "synthetic.json" in r.stdout)
        ok("check, today and bad argv write nothing", _snapshot(tmp) == before)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"linkedin_cut self-test: {total - fails}/{total}")
    return 1 if fails else 0


def _iso_date(s):
    import argparse
    try:
        return datetime.date.fromisoformat(s).isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a YYYY-MM-DD date: {s!r}")


def build_parser():
    import argparse
    ap = argparse.ArgumentParser(prog="linkedin_cut.py", description="Gate the LinkedIn draft queue.")
    ap.add_argument("--self-test", action="store_true", help="fail-on-bad cases + argv contract")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check", help="gate queue files (default: whole queue); read-only")
    c.add_argument("paths", nargs="*")
    t = sub.add_parser("today", help="print the cut due on a date; read-only")
    t.add_argument("--date", type=_iso_date, default=None, help="YYYY-MM-DD (default: today)")
    return ap


def main(argv):
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.self_test:
        if a.cmd: ap.error("--self-test takes no subcommand")
        return self_test()
    if a.cmd == "check": return cmd_check(a.paths)
    if a.cmd == "today": return cmd_today(a.date or datetime.date.today().isoformat())
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
