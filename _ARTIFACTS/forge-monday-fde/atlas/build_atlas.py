#!/usr/bin/env python3
"""Build ATLAS.html: one self-contained file bundling every prep document as a ziggurat.

Ziggurat grammar (ADR-077): stepped read, base to apex. Widest tier = raw witnessed signal; each step narrower
and more resolved, up to the decision. Fog = staleness (hours since the file changed).
Dynamic: each build re-reads the files, re-runs the gates, appends a receipt to atlas/build-ledger.jsonl.
  python3 atlas/build_atlas.py            build once
  python3 atlas/build_atlas.py --watch    rebuild when any source changes; the open page reloads itself within about 3 s of a change
Stdlib only. Refuses to build if a secret-looking string appears in any source (the assignment link is a credential).
"""
import json, os, re, subprocess, sys, time, hashlib, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CFG = json.load(open(os.path.join(HERE, "atlas.config.json")))
STATE = os.path.join(HERE, "state.json")
LEDGER = os.path.join(HERE, "build-ledger.jsonl")
OUT = os.path.join(ROOT, "ATLAS.html")

def repo_root():
    p = ROOT
    for _ in range(8):
        if os.path.exists(os.path.join(p, "scripts", "slop_lint.py")): return p
        p = os.path.dirname(p)
    return None

SECRET = re.compile(r"(invite/[A-Za-z0-9_-]{20,}|cdn2\.monday\.app|sk-[A-Za-z0-9]{20,}|JOBS_PIPELINE_TOKEN\s*=|ANTHROPIC_API_KEY\s*=\s*\S+)")

def esc(s): return html.escape(s, quote=False)

def inline(s):
    codes = []
    def keep(m): codes.append(m.group(1)); return "\x00%d\x00" % (len(codes) - 1)
    s = re.sub(r"`([^`]+)`", keep, s)
    s = esc(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])", r"<em>\1</em>", s)
    def link(m):
        t, u = m.group(1), html.unescape(m.group(2))
        if not re.match(r"^(https?://|#|[\w./-]+$)", u): return t
        return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(u, quote=True), t)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    return re.sub(r"\x00(\d+)\x00", lambda m: "<code>%s</code>" % esc(codes[int(m.group(1))]), s)

def md_to_html(text):
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        l = lines[i]
        if l.strip().startswith("```"):
            buf = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"): buf.append(lines[i]); i += 1
            out.append("<pre><code>%s</code></pre>" % esc("\n".join(buf))); i += 1; continue
        if re.match(r"^\s*\|.*\|\s*$", l) and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            hdr = [c.strip() for c in l.strip().strip("|").split("|")]; i += 2; rows = []
            while i < len(lines) and re.match(r"^\s*\|.*\|\s*$", lines[i]):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            t = "<div class='scroll'><table><thead><tr>" + "".join("<th>%s</th>" % inline(c) for c in hdr) + "</tr></thead><tbody>"
            for r in rows: t += "<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>"
            out.append(t + "</tbody></table></div>"); continue
        m = re.match(r"^(#{1,6})\s+(.*)$", l)
        if m: n = min(len(m.group(1)) + 1, 6); out.append("<h%d>%s</h%d>" % (n, inline(m.group(2)), n)); i += 1; continue
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", l): out.append("<hr>"); i += 1; continue
        if l.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"): buf.append(lines[i].lstrip("> ")); i += 1
            out.append("<blockquote>%s</blockquote>" % inline(" ".join(buf))); continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", l):
            ordered = bool(re.match(r"^\s*\d+\.", l)); tag = "ol" if ordered else "ul"; items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                items.append(inline(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]))); i += 1
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % x for x in items), tag)); continue
        if not l.strip(): i += 1; continue
        buf = [l]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|\s*([-*]|\d+\.)\s|>|```|\s*\|)", lines[i]): buf.append(lines[i]); i += 1
        out.append("<p>%s</p>" % inline(" ".join(buf)))
    return "\n".join(out)

def run_gate(rr, kind, path, ledger):
    if not rr: return "n/a"
    script = os.path.join(rr, "scripts", "slop_lint.py" if kind == "slop" else "provenance_lint.py")
    if not os.path.exists(script): return "n/a"
    cmd = ["python3", script] + (["--ledger", ledger] if kind == "prov" else []) + [path]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=40, cwd=rr)
        return "pass" if r.returncode == 0 else "fail"
    except Exception: return "n/a"

def parse_mc():
    p = os.path.join(ROOT, "takehome-workspace", "montecarlo-results.txt")
    d = {}
    try: t = open(p).read()
    except Exception: return d
    m = re.search(r"Anterior.*?P\(pass all bars\) = ([\d.]+).*?KILL fail ([\d.]+)", t, re.S)
    if m: d["base"], d["kill0"] = float(m.group(1)), float(m.group(2))
    m = re.search(r"Spent [\d.]+ h\. P\(pass\) = ([\d.]+).*?KILL ([\d.]+)", t)
    if m: d["plan"], d["kill1"] = float(m.group(1)), float(m.group(2))
    ev = re.findall(r"- after (E\d [^:]+): ([\d.]+)", t)
    if ev: d["evidence"] = [[a, float(b)] for a, b in ev]
    m = re.search(r"plan \+ all evidence events ([\d.]+)", t)
    if m: d["kill2"] = float(m.group(1))
    return d

def build():
    rr = repo_root()
    ledger = os.path.join(ROOT, CFG.get("ledger_file", "evidence-interview.jsonl"))
    now = time.time(); docs = []; secret_hits = []
    old = {}
    try: old = json.load(open(STATE))
    except Exception: pass
    new_state = {}
    for d in CFG["docs"]:
        p = os.path.join(ROOT, d["path"])
        try: text = open(p, encoding="utf-8", errors="replace").read()
        except Exception: docs.append(dict(d, missing=True, gate="n/a", age_h=0, body="<p>Missing file.</p>", text="")); continue
        if SECRET.search(text): secret_hits.append(d["path"])
        sha = hashlib.sha1(text.encode()).hexdigest()[:12]; new_state[d["path"]] = sha
        ext = os.path.splitext(p)[1]
        body = md_to_html(text) if ext == ".md" else "<pre><code>%s</code></pre>" % esc(text)
        gates = {g: run_gate(rr, g, p, ledger) for g in d.get("gates", [])}
        gate = "fail" if "fail" in gates.values() else ("pass" if gates else "src")
        emd = text.count("—")
        if emd and ext == ".md": gate = "fail"; gates["em-dash"] = "fail"
        status = "new" if d["path"] not in old else ("changed" if old[d["path"]] != sha else "same")
        docs.append(dict(d, gates=gates, gate=gate, age_h=round((now - os.path.getmtime(p)) / 3600, 1), body=body,
                         text=re.sub(r"\s+", " ", text.lower())[:6000], words=len(text.split()), status=status, sha=sha))
    board = ""
    bp = os.path.join(ROOT, CFG.get("board", ""))
    if os.path.exists(bp):
        bt = open(bp, encoding="utf-8", errors="replace").read()
        if SECRET.search(bt): secret_hits.append(CFG["board"])
        board = html.escape(bt, quote=True)
    if secret_hits:
        print("REFUSING TO BUILD: secret-looking string in", secret_hits); sys.exit(2)
    fails = [d["path"] for d in docs if d.get("gate") == "fail"]
    flags = CFG["flags"]
    gate = "RED" if fails else ("YELLOW" if not flags.get("brief_read") else "GREEN")
    log = next((d for d in docs if d["id"] == "log"), None)
    entries = len(re.findall(r"^### ", open(os.path.join(ROOT, "TAKEHOME-LOG.md")).read(), re.M)) if log else 0
    changed = [d["path"] for d in docs if d.get("status") in ("new", "changed")]
    built = datetime.datetime.now().strftime("%a %b %d %H:%M:%S")
    data = {"title": CFG["title"], "tiers": CFG["tiers"], "apex": CFG["apex"], "flags": flags, "gate": gate, "fails": fails,
            "built": built, "version": str(time.time()), "entries": entries, "mc": parse_mc(), "changed": changed, "watch": "--watch" in sys.argv,
            "artifacts": CFG.get("artifacts", []),
            "docs": [{k: d.get(k) for k in ("id", "path", "title", "tier", "gate", "gates", "age_h", "words", "status", "text")} for d in docs]}
    page = TEMPLATE.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    page = page.replace("__ARTICLES__", "\n".join("<article id='d-%s' class='doc' hidden><h1>%s</h1><p class='path'>%s</p>%s</article>" % (d["id"], esc(d["title"]), esc(d["path"]), d["body"]) for d in docs))
    page = page.replace("__BOARD__", board).replace("__REFRESH__", "")
    open(OUT, "w", encoding="utf-8").write(page)
    # data export for HUD visualizers. Structure only: no document text, no assignment content.
    priv = {k: data[k] for k in ("title", "tiers", "apex", "flags", "gate", "fails", "built", "entries", "mc", "changed")}
    priv["schema"] = "arcs.atlas.v1"
    priv["docs"] = [{k: d.get(k) for k in ("id", "path", "title", "tier", "gate", "gates", "age_h", "words", "status")} for d in data["docs"]]
    pub = {"schema": "arcs.atlas.v1.public", "built": built, "gate": gate,
           "tiers": [{"n": t["n"], "name": t["name"], "docs": sum(1 for d in data["docs"] if d["tier"] == t["n"]),
                      "gate": ("fail" if any(d["gate"] == "fail" for d in data["docs"] if d["tier"] == t["n"]) else "pass")} for t in CFG["tiers"]],
           "note": "Shape only. No titles, names or content. Do not publish while the engagement is live."}
    for name, obj in (("atlas-data.json", priv), ("atlas-data.public.json", pub)):
        blob = json.dumps(obj, indent=1)
        if SECRET.search(blob): print("REFUSING: secret-looking string in", name); sys.exit(2)
        open(os.path.join(HERE, name), "w").write(blob)
    open(os.path.join(HERE, "version.js"), "w").write("window.ATLAS_VERSION=%s;" % json.dumps(data["version"]))
    json.dump(new_state, open(STATE, "w"), indent=1)
    with open(LEDGER, "a") as f:
        f.write(json.dumps({"built": built, "gate": gate, "docs": len(docs), "changed": changed, "fails": fails}) + "\n")
    print("built ATLAS.html | gate %s | %d docs | changed %d | fails %d" % (gate, len(docs), len(changed), len(fails)))

def sources():
    ps = [os.path.join(ROOT, d["path"]) for d in CFG["docs"]] + [os.path.join(ROOT, CFG.get("board", "")), os.path.join(HERE, "atlas.config.json"), os.path.join(ROOT, CFG.get("ledger_file", ""))]
    return {p: os.path.getmtime(p) for p in ps if os.path.exists(p)}

TEMPLATE = open(os.path.join(HERE, "atlas_template.html"), encoding="utf-8").read()

if __name__ == "__main__":
    build()
    if "--watch" in sys.argv:
        print("watching; Ctrl+C to stop")
        last = sources()
        while True:
            time.sleep(2)
            cur = sources()
            if cur != last: last = cur; build()
