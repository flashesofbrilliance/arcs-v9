#!/usr/bin/env python3
"""tune_serve: one editor for every page. Serves the token tuner locally and maps a page URL back to its source file.

    python3 scripts/tune_serve.py [--port 8799]          serve the install page (the bookmarklet) on 127.0.0.1
    python3 scripts/tune_serve.py --install OUT.html     write the install page to a file instead (open it, drag the link)
    python3 scripts/tune_serve.py --where URL            print the repo file that serves URL (from the surface catalog)
    python3 scripts/tune_serve.py --apply URL EDITS.json apply the tuner's "Copy edits" list to that page's file
    python3 scripts/tune_serve.py --self-test

How to use it: run the server, open http://127.0.0.1:8799/ and drag "ARCS tune" to the bookmarks bar. On any page
(localhost, a preview, or a live arcs.care host you have unlocked), click it: the tuner runs in that page without the
page carrying it, so nothing a counterpart can see changes. The bookmarklet holds the whole tuner (an https page may not
load scripts from 127.0.0.1), so re-drag it after src/ui-kit/token-tuner.js changes. Double-click text to edit, Copy edits, then --apply.

Edits land in the file the surface catalog says serves the URL. Many public pages are BUILT from a source by a script;
--apply then names the scripts that write that file and refuses, so the change goes into the source instead (an edit to a
built file is clobbered by the next build). Pass --force-built to write the built file anyway.
Limit: the bookmarklet loads after the page's own scripts, so JS-side breakpoints (matchMedia) do not follow the slider;
CSS @media rules do. Pages that carry the tuner inline (token_tuner_inline.py) do not have this limit.
"""
import http.server
import json
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "ui-kit", "token-tuner.js")
CATALOG = os.path.join(ROOT, "runtime", "specs", "surface-catalog.json")
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def bookmarklet(port=None):
    """The bookmarklet carries the whole tuner, so it works on any https page with no local server reachable from it
    (browsers block https pages from loading http://127.0.0.1). Re-drag it after the tuner changes."""
    with open(SRC, encoding="utf-8") as fh:
        code = fh.read()
    from urllib.parse import quote
    body = ("(function(){if(window.__arcsTokenTuner)return;window.__arcsTuneForce=1;var c=%s;window.__arcsTuneSrc=c;"
            "var s=document.createElement('script');s.textContent=c;(document.body||document.documentElement).appendChild(s);})()"
            % json.dumps(code))
    return "javascript:" + quote(body, safe="(){};,=!'*:/.?&+$@[]")


def rows():
    with open(CATALOG, encoding="utf-8") as fh:
        return json.load(fh)["rows"]


def where(url, catalog=None):
    """The repo file serving url: a catalog row for its host and path, else public/<path> for a local server."""
    u = urlparse(url if "://" in url else "http://" + url)
    host, path = (u.hostname or "").lower(), (u.path or "/").rstrip("/") or "/"
    for r in catalog if catalog is not None else rows():
        if r.get("file") and not r.get("pattern") and r.get("host") == host and (r.get("path") or "/").rstrip("/") in (path, "") and \
                ((r.get("path") or "/").rstrip("/") or "/") == path:
            return r["file"]
    cand = os.path.join("public", path.lstrip("/"))
    if host in ("localhost", "127.0.0.1") and cand.endswith(".html") and os.path.exists(os.path.join(ROOT, cand)):
        return cand
    # the house naming for a gated subpage the catalog does not list: louisville.arcs.care/proposal -> public/louisville-proposal.html
    sub = host.split(".")[0]
    if path != "/" and host.endswith(".arcs.care"):
        guess = "public/%s-%s.html" % (sub, path.strip("/").replace("/", "-"))
        if os.path.exists(os.path.join(ROOT, guess)):
            return guess
    return None


def writers(rel):
    """Scripts that name this file: likely its builder. Read-only git grep."""
    out = subprocess.run(["git", "-C", ROOT, "grep", "-l", "-F", rel, "--", "scripts/*.py", "scripts/*.mjs", "scripts/*.sh"],
                         capture_output=True, text=True).stdout.split()
    return [w for w in out if w not in ("scripts/tune_serve.py", "scripts/surface_catalog_emit.py")]


# Built pages whose source is known: edits go to the source, then the named command rebuilds the served file.
# None as the source means the served file IS the source (its scripts only rewrite a marked block).
# A string reason means: edit through that page's own path instead.
SOURCES = {
    "public/louisville-proposal.html": ("_ARTIFACTS/louisville-proposal/source.html", "python3 scripts/proposal_build.py --louisville"),
    "public/myally-hub.html": (None, "python3 scripts/myally_hub_sync.py --check"),
    "public/gravity-brief.html": "built from _ARTIFACTS/tabbed-brief/gravity.json: build a --tune copy with "
                                 "scripts/tabbed_brief_build.py, open it with ?tune&edit, Copy JSON, then --apply the patch",
}
for _seat in ("eir", "founder", "open", "principal"):
    SOURCES[f"public/gravity-brief-{_seat}.html"] = SOURCES["public/gravity-brief.html"]


def apply(url, edits_path, force_built=False):
    import token_tuner_inline as tti
    rel = where(url)
    if not rel:
        print(f"✖ no repo file serves {url}; check runtime/specs/surface-catalog.json")
        return 1
    known = SOURCES.get(rel)
    if isinstance(known, str):
        print(f"✖ {rel} is {known}")
        return 1
    if known:
        src, after = known
        code = tti.main(["--apply-text", edits_path, os.path.join(ROOT, src or rel)])
        if code == 0:
            print(f"next: {after}")
        return code
    built = [w for w in writers(rel) if re.search(r"(build|emit|sync|render|forge)", w)]
    if built and not force_built:
        print(f"✖ {rel} is written by {', '.join(built)}; apply the edits to that builder's source instead")
        print(f"  (python3 scripts/token_tuner_inline.py --apply-text {edits_path} <source>, then rebuild), or pass --force-built")
        return 1
    return tti.main(["--apply-text", edits_path, os.path.join(ROOT, rel)])


class Handler(http.server.BaseHTTPRequestHandler):
    port = 8799

    def _send(self, code, body, ctype):
        b = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_OPTIONS(self):
        self._send(204, "", "text/plain")

    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/token-tuner.js":
            with open(SRC, encoding="utf-8") as fh:
                return self._send(200, fh.read(), "text/javascript; charset=utf-8")
        if p == "/":
            bm = bookmarklet(self.port).replace("&", "&amp;").replace('"', "&quot;")
            return self._send(200, PAGE.replace("{BM}", bm), "text/html; charset=utf-8")
        self._send(404, "not found", "text/plain")

    def log_message(self, *a):
        pass


PAGE = """<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ARCS tune</title>
<body style="margin:0;padding:32px 16px;background:#020408;color:#e2e8f0;font:16px/1.55 system-ui,sans-serif">
<main style="max-width:640px;margin:0 auto">
<h1 style="font-size:24px;margin:0 0 12px">ARCS tune</h1>
<p>Drag this to your bookmarks bar, then click it on any page:</p>
<p><a href="{BM}" style="display:inline-block;padding:12px 18px;min-height:44px;box-sizing:border-box;border:1px solid #00F0FF;color:#00F0FF;text-decoration:none;border-radius:6px">ARCS tune</a></p>
<p>Double-click text to edit it. Clear a line and click away to remove it. Backspace at the start of a line joins it to the line above; Delete at the end pulls the next line up. Copy edits, then:</p>
<pre style="white-space:pre-wrap;background:#0d1117;border:1px solid #1e293b;padding:12px;border-radius:6px">python3 scripts/tune_serve.py --apply PAGE_URL edits.json</pre>
<p>Nothing here changes the live page until you apply and ship.</p>
</main></body>"""


def self_test():
    cat = [{"host": "louisville.arcs.care", "path": "/proposal", "file": "public/louisville-proposal.html", "pattern": False},
           {"host": "good.arcs.care", "path": "/blog/nftt/:slug", "file": None, "pattern": True}]
    assert where("https://louisville.arcs.care/proposal", cat) == "public/louisville-proposal.html", "host and path map to the file"
    assert where("https://louisville.arcs.care/proposal/", cat) == "public/louisville-proposal.html", "a trailing slash still maps"
    assert where("https://good.arcs.care/blog/nftt/x", cat) is None, "a pattern row has no single file"
    bm = bookmarklet(8799)
    assert bm.startswith("javascript:") and "__arcsTuneForce" in bm and "__arcsTuneSrc" in bm, "bookmarklet carries the tuner"
    from urllib.parse import unquote
    assert "arcs-token-tuner" in unquote(bm), "bookmarklet holds the tuner source itself"
    with open(SRC, encoding="utf-8") as fh:
        assert "__arcsTuneForce" in fh.read(), "the tuner honours the bookmarklet's force flag"
    print("tune_serve self-test: ok")
    return 0


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] == ["--where"] and len(argv) == 2:
        rel = where(argv[1])
        print(rel or "no file")
        return 0 if rel else 1
    if argv[:1] == ["--install"] and len(argv) == 2:
        bm = bookmarklet().replace("&", "&amp;").replace('"', "&quot;")
        with open(argv[1], "w", encoding="utf-8") as fh:
            fh.write(PAGE.replace("{BM}", bm))
        print(f"wrote {argv[1]}: open it and drag ARCS tune to the bookmarks bar")
        return 0
    if argv[:1] == ["--apply"] and len(argv) in (3, 4):
        return apply(argv[1], argv[2], force_built="--force-built" in argv)
    port = 8799
    if argv[:1] == ["--port"] and len(argv) == 2:
        port = int(argv[1])
    elif argv:
        print(__doc__)
        return 2
    Handler.port = port
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"ARCS tune on http://127.0.0.1:{port}/ (drag the bookmarklet from there). Ctrl-C stops it.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
