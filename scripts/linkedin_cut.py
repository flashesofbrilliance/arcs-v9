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
  slop_lint (clichés + em-dashes)   provenance_lint (every metric covered by the queue's evidence)
  altitude_canary --strict (article) series footer (post/carousel/article)   PII grep
  AEO: question ends in '?', answer 40-60 words and verbatim in the article's first paragraph,
       every named entity appears in the article, >= 1 primary source URL.

Usage:
  python3 scripts/linkedin_cut.py check [_QUEUE/linkedin/*.json]   # gate (default: whole queue)
  python3 scripts/linkedin_cut.py today [--date YYYY-MM-DD]          # print the cut due today
  python3 scripts/linkedin_cut.py --self-test                        # proves fail-on-bad
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


def self_test():
    good = sorted(glob.glob(os.path.join(QUEUE, "*.json")))
    assert good, "no queue files to test against"
    q = json.load(open(good[0]))
    assert not check_file(good[0]), f"good fixture should pass: {check_file(good[0])}"
    with tempfile.TemporaryDirectory() as d:
        mutations = {
            "em-dash": lambda q: q["cuts"][3].__setitem__("text", q["cuts"][3]["text"] + " — end"),
            "uncited metric": lambda q: q["cuts"][3].__setitem__("text", q["cuts"][3]["text"] + " It grew 87%."),
            "no footer": lambda q: q["cuts"][3].__setitem__("text", q["cuts"][3]["text"].replace(f"Part of {q['show']}", "")),
            "aeo drift": lambda q: q["aeo"].__setitem__("answer", "Short answer that is not in the article at all " * 5),
        }
        for name, mut in mutations.items():
            m = json.loads(json.dumps(q)); mut(m)
            fp = os.path.join(d, "t.json"); json.dump(m, open(fp, "w"))
            assert check_file(fp), f"mutation '{name}' should fail"
            print(f"  fail-on-bad ok: {name}")
    print("linkedin_cut self-test: PASS"); return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--self-test"]: sys.exit(self_test())
    if a[:1] == ["today"]:
        d = a[a.index("--date") + 1] if "--date" in a else datetime.date.today().isoformat()
        sys.exit(cmd_today(d))
    if a[:1] == ["check"]: sys.exit(cmd_check(a[1:]))
    print(__doc__); sys.exit(2)
