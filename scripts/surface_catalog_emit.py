#!/usr/bin/env python3
"""surface_catalog_emit.py: one catalog row per arcs.care surface, harvested from the routing sources.

WHY: the only inventory of the ~95 arcs.care hosts was a July prose map (_PATTERNS, 2026-07-10)
that went stale the week it was written, because every new counterpart page adds a rewrite in
next.config.ts or a host block in src/proxy.ts and nothing ever listed them back. This emitter
reads those two files (plus the app route tree) and writes the catalog; a host that is routed but
absent from the catalog fails --check, so the inventory cannot drift from the config again.

SOURCES (parsed, never hand-listed):
  next.config.ts   rewrites() `has: host` rules (expanded: /:seg(a|b) enumerations become rows,
                   /:path(...) catch-alls become the host root), headers() X-Robots-Tag hosts,
                   redirects() retired hosts
  src/proxy.ts     SUBDOMAIN_MAP, AMMO_HOSTS, MULTI_PATH_MAP, and every `if (sub === '...')` block
                   (a block that calls ammoUnlocked() is a passcode gate)
  src/app/**       page.tsx + route.ts outside /api: path from the folder, purpose from the
                   nearest `metadata` (own file, sibling layout, ancestor layout), gate from an
                   auth() / isAdmin() call in the handler
  the destination  <title>, <meta name="description">, <meta name="robots">, first <h1> as the
                   title fallback; git for the file's last commit date

EMITS  runtime/specs/surface-catalog.json (one row per host+path) and runtime/warroom/surfaces.html, a
       self-contained page rendered from that JSON (inline _tokens.css verbatim, sentinel kept).
       Deterministic: no wall clock in the output; run twice, diff clean.

KIND   explorer | status | ledger | product page | gated. First matching rule wins:
       gated = passcode or admin-session gate on the row · ledger = belief/gauntlet logs, /history
       status = status.html, prl-status-* · explorer = playground, pf-*, monolith, forge-pattern,
       forge-cut, *observatory*, /observatory · product page = everything else.

CHECK  python3 scripts/surface_catalog_emit.py --check   exits 1 when
       (a) a host named in next.config.ts is missing from the committed catalog (rows, retired
           list, or header-only list),
       (b) the committed catalog differs from a fresh harvest on any field except last_commit
           (dates move with every page edit; they are refreshed by a full emit, not gated), or
       (c) runtime/warroom/surfaces.html is not the render of the committed JSON.
       CI checkouts can be shallow, so --check never calls git.

  python3 scripts/surface_catalog_emit.py              # emit JSON + HTML
  python3 scripts/surface_catalog_emit.py --check      # gate (pre-commit + CI)
  python3 scripts/surface_catalog_emit.py --self-test  # fails-on-bad + passes-on-good
Stdlib only.
"""
import argparse
import glob
import html
import html.parser
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NEXT_CONFIG = os.path.join(ROOT, "next.config.ts")
PROXY = os.path.join(ROOT, "src", "proxy.ts")
APP_DIR = os.path.join(ROOT, "src", "app")
TOKENS = os.path.join(ROOT, "src", "ui-kit", "recoil-report", "_tokens.css")
OUT_JSON = os.path.join(ROOT, "runtime", "specs", "surface-catalog.json")
OUT_HTML = os.path.join(ROOT, "runtime", "warroom", "surfaces.html")
CATALOG_HOST = "surfaces.arcs.care"
APP_HOST = "app.arcs.care"
DOMAIN = ".arcs.care"

KINDS = ("explorer", "status", "ledger", "product page", "gated")
GATE_PASSCODE = "shared passcode"
GATE_ADMIN = "admin session"

# ---------------------------------------------------------------------------- helpers


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def unescape_ts(s):
    """A TS string literal body: `\\\\` is one backslash, `\\.` stays as written."""
    return s.replace("\\\\", "\\")


# ---------------------------------------------------------------------------- next.config.ts

RULE_RE = re.compile(
    r"\{\s*source:\s*\"((?:[^\"\\]|\\.)*)\"\s*,\s*destination:\s*\"((?:[^\"\\]|\\.)*)\""
    r"(?:\s*,\s*has:\s*\[\{\s*type:\s*\"host\"\s*,\s*value:\s*\"([^\"]+)\"\s*\}\])?\s*\}"
)
HOST_LITERAL_RE = re.compile(r"\"([a-z0-9-]+\.arcs\.care)\"")


def _region(text, start_marker, end_markers):
    i = text.find(start_marker)
    if i < 0:
        return ""
    ends = [text.find(m, i + len(start_marker)) for m in end_markers]
    ends = [e for e in ends if e >= 0]
    return text[i:min(ends)] if ends else text[i:]


def parse_next_config(text):
    rewrites = _region(text, "async rewrites()", ["async redirects()"])
    headers = _region(text, "async headers()", ["async rewrites()"])
    redirects = _region(text, "async redirects()", ["};\n\nexport default"])

    rules = []
    for m in RULE_RE.finditer(rewrites):
        rules.append({"source": unescape_ts(m.group(1)), "destination": unescape_ts(m.group(2)),
                      "host": m.group(3)})

    noindex_hosts = []
    for m in re.finditer(r"value:\s*\"([a-z0-9-]+\.arcs\.care)\"", headers):
        if "X-Robots-Tag" in headers[m.end():m.end() + 200]:
            noindex_hosts.append(m.group(1))

    retired = []
    m = re.search(r"retiredFanaticsHosts\s*=\s*\[(.*?)\]", redirects, re.S)
    if m:
        retired = HOST_LITERAL_RE.findall(m.group(1))

    all_hosts = sorted(set(HOST_LITERAL_RE.findall(text)))
    return rules, sorted(set(noindex_hosts)), sorted(set(retired)), all_hosts


SEG_ENUM_RE = re.compile(r"^:(\w+)\(([\w.|-]+)\)$")       # :seg(a|b|c)
SEG_CATCH_RE = re.compile(r"^:(\w+)(\*|\(.*\))?$")        # :path  :path*  :path((?!x).*)


def split_segments(source):
    """Path segments of a rewrite source, splitting on `/` only outside parentheses
    (a catch-all like /:path((?!fonts/).*) carries a slash inside its regex)."""
    segs, cur, depth = [], "", 0
    for ch in source.strip("/"):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "/" and depth == 0:
            segs.append(cur)
            cur = ""
        else:
            cur += ch
    segs.append(cur)
    return [s for s in segs if s != ""]


def expand_source(source, destination):
    """Return [(path, destination, catch_all, pattern)] for one rewrite rule."""
    if source == "/":
        return [("/", destination, False, False)]
    segs = split_segments(source)
    # a single leading free/catch segment is the host root
    if len(segs) == 1 and SEG_CATCH_RE.match(segs[0]) and not SEG_ENUM_RE.match(segs[0]):
        return [("/", destination, True, ":" in destination)]
    combos = [([], destination)]
    for seg in segs:
        em = SEG_ENUM_RE.match(seg)
        if em:
            name, alts = em.group(1), em.group(2).split("|")
            combos = [(p + [a], d.replace(":" + name, a)) for p, d in combos for a in alts]
        elif seg.startswith(":"):
            # a free parameter: keep the rule as one pattern row
            return [(source, destination, False, True)]
        else:
            combos = [(p + [seg], d) for p, d in combos]
    return [("/" + "/".join(p), d, False, ":" in d) for p, d in combos]


# ---------------------------------------------------------------------------- src/proxy.ts

PAIR_RE = re.compile(r"'(/[^']*)'\s*:\s*'(/[^']*)'")


def _object_region(text, name):
    i = text.find("const %s" % name)
    if i < 0:
        return ""
    j = text.find("\n}", i)
    return text[i:j] if j > 0 else text[i:]


def _balanced(text, start, open_ch, close_ch):
    """Index just past the bracket that closes the one at `start`."""
    depth = 0
    for k in range(start, len(text)):
        if text[k] == open_ch:
            depth += 1
        elif text[k] == close_ch:
            depth -= 1
            if depth == 0:
                return k + 1
    return len(text)


def parse_proxy(text):
    out = {"simple": {}, "ammo": {}, "multi": {}, "blocks": []}
    for line in _object_region(text, "SUBDOMAIN_MAP").splitlines():
        m = re.match(r"\s*'([a-z0-9-]+)':\s*'(/[^']+)'", line)
        if m:
            out["simple"][m.group(1)] = m.group(2)
    for m in re.finditer(r"'([a-z0-9-]+)':\s*\{\s*ammoFile:\s*'([^']+)',\s*gateFile:\s*'([^']+)'\s*\}",
                         _object_region(text, "AMMO_HOSTS")):
        out["ammo"][m.group(1)] = {"ammo": m.group(2), "gate": m.group(3)}
    for line in _object_region(text, "MULTI_PATH_MAP").splitlines():
        m = re.match(r"\s*'([a-z0-9-]+)':\s*\{(.*)\}", line)
        if not m:
            continue
        sub, body = m.group(1), m.group(2)
        paths = {p: d for p, d in PAIR_RE.findall(body)}
        dm = re.search(r"default:\s*'(/[^']+)'", body)
        out["multi"][sub] = {"paths": paths, "default": dm.group(1) if dm else None}
    # explicit `if (... sub === 'x' ...) { ... }` blocks
    for m in re.finditer(r"\bif \(", text):
        cond_end = _balanced(text, m.end() - 1, "(", ")")
        cond = text[m.end():cond_end - 1]
        sm = re.search(r"sub === '([a-z0-9-]+)'", cond)
        if not sm:
            continue
        brace = text.find("{", cond_end)
        body = text[brace:_balanced(text, brace, "{", "}")]
        gated_paths = []
        for gm in re.finditer(r"url\.pathname = ok \? '([^']+)' : '([^']+)'", body):
            before = body[:gm.start()]
            pm = list(re.finditer(r"pathname === '([^']+)'", before))
            gated_paths.append({"path": (pm[-1].group(1).rstrip("/") or "/") if pm else "/",
                                "destination": gm.group(1), "gate_file": gm.group(2)})
        plain = [d for d in re.findall(r"url\.pathname = '([^']+)'", body)]
        out["blocks"].append({
            "sub": sm.group(1),
            "host_gate": "ammoUnlocked(" in body and not gated_paths,
            "gated_paths": gated_paths,
            "default": plain[-1] if plain else None,
            "gate_file": plain[-1] if ("ammoUnlocked(" in body and not gated_paths and plain) else None,
        })
    return out


# ---------------------------------------------------------------------------- src/app routes

META_TITLE_RE = re.compile(r"title:\s*(?:\"([^\"]*)\"|'([^']*)'|([A-Z_]+))")
META_DESC_RE = re.compile(r"description:\s*(?:\"([^\"]*)\"|'([^']*)'|([A-Z_]+))")
CONST_RE = re.compile(r"const\s+([A-Z_]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')")
# the gate calls an app handler makes: Auth.js session, the admin allowlist, the jobs-board viewer
# check (src/lib/jobs.ts pageViewerAllowed), or a redirect to the sign-in page
AUTH_RE = re.compile(r"\bawait auth\(\)|\bisAdmin\(|\bpageViewerAllowed\(|redirect\(\"/compass")


def _metadata(text):
    """(title, description, noindex) from an `export const metadata` block, consts resolved."""
    i = text.find("export const metadata")
    if i < 0:
        return None
    block = text[i:_balanced(text, text.find("{", i), "{", "}")]
    consts = {m.group(1): m.group(2) or m.group(3) for m in CONST_RE.finditer(text)}

    def pick(rx):
        m = rx.search(block)
        if not m:
            return None
        return m.group(1) or m.group(2) or consts.get(m.group(3) or "", None)

    title = pick(META_TITLE_RE)
    if title is None:
        tm = re.search(r"title:\s*\{\s*default:\s*\"([^\"]*)\"", block)
        title = tm.group(1) if tm else None
    noindex = bool(re.search(r"robots:\s*\{\s*index:\s*false", block))
    return title, pick(META_DESC_RE), noindex


def _first_comment(text):
    """First prose `//` comment line in the file (rule lines like `// ── Data ──` are skipped)."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("//"):
            body = s[2:].strip()
            if re.search(r"[A-Za-z]{3}", body) and not re.match(r"^[─-]{2,}", body):
                return re.sub(r"\s*[─-]{3,}.*$", "", body).rstrip(" :")
    return None


def parse_app_routes():
    rows = []
    files = sorted(glob.glob(os.path.join(APP_DIR, "**", "page.tsx"), recursive=True)
                   + glob.glob(os.path.join(APP_DIR, "**", "route.ts"), recursive=True))
    for f in files:
        r = rel(f)
        if r.startswith("src/app/api/"):
            continue
        d = os.path.dirname(f)
        segs = [s for s in os.path.relpath(d, APP_DIR).split(os.sep) if s and s != "." and not s.startswith("(")]
        path = "/" + "/".join(segs) if segs else "/"
        text = read(f)
        meta = _metadata(text)
        probe = d
        while meta is None and probe.startswith(APP_DIR):
            lay = os.path.join(probe, "layout.tsx")
            if os.path.exists(lay) and (probe != APP_DIR or d == APP_DIR):
                meta = _metadata(read(lay))
            probe = os.path.dirname(probe)
        title, desc, noindex = meta if meta else (None, None, False)
        if title is None and desc is None:
            desc = _first_comment(text)
        rows.append({
            "host": APP_HOST, "path": path, "catch_all": False, "source": path,
            "destination": path, "file": r, "kind": None,
            "title": title, "description": desc,
            "index": "noindex" if noindex else None,
            # A page can read the session for a sub-feature without gating the page
            # (arcs.care/hud: only the ziggurat loader is admin). It opts out with
            # the marker `surface-gate: open` in a comment.
            "gate": GATE_ADMIN if AUTH_RE.search(text) and "surface-gate: open" not in text else None,
            "declared_in": ["src/app"],
        })
    return rows


# ---------------------------------------------------------------------------- page harvest


class Head(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.h1 = None
        self.desc = None
        self.robots = None
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            name = (a.get("name") or "").lower()
            if name == "description" and self.desc is None:
                self.desc = a.get("content")
            elif name == "robots" and self.robots is None:
                self.robots = a.get("content")
        elif tag in ("title", "h1") and getattr(self, tag) is None:
            self._in = tag

    def handle_endtag(self, tag):
        if tag == self._in:
            self._in = None

    def handle_data(self, data):
        if self._in and data.strip():
            cur = getattr(self, self._in) or ""
            setattr(self, self._in, (cur + " " + data.strip()).strip())


def harvest_page(path):
    """title/description/robots of a static HTML file; the first <h1> stands in for a missing title."""
    p = Head()
    try:
        p.feed(read(path))
    except Exception:  # a malformed page still gets a row
        pass
    title = p.title or p.h1
    norm = lambda s: re.sub(r"\s+", " ", s).strip() if s else None
    return norm(title), norm(p.desc), norm(p.robots)


def dest_file(destination):
    """Repo path a destination serves, or None when it is a pattern or an app route."""
    if ":" in destination:
        return None
    if destination.startswith("/warroom/"):
        return "runtime/warroom/%s.html" % destination[len("/warroom/"):]
    if destination.startswith("/prep/"):
        return "runtime/warroom/%s.html" % destination[len("/prep/"):]
    if "." in os.path.basename(destination):
        return "public" + destination
    return None


def git_dates(files):
    out = {}
    for f in sorted({f for f in files if f}):
        if not os.path.exists(os.path.join(ROOT, f)):
            continue
        try:
            r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f], cwd=ROOT,
                               capture_output=True, text=True, timeout=30)
            out[f] = r.stdout.strip() or None
        except (OSError, subprocess.TimeoutExpired):
            out[f] = None
    return out


# ---------------------------------------------------------------------------- assembly

EXPLORER_RE = re.compile(r"^(playground|pf-|monolith|forge-pattern|forge-cut)|observatory", re.I)


def classify(row):
    base = os.path.basename(row["file"] or row["destination"] or "")
    if row.get("gate"):
        return "gated"
    if base in ("belief-log.html", "gauntlet-log.html") or row["path"] == "/history" and row["host"] == APP_HOST:
        return "ledger"
    if base == "status.html" or base.startswith("prl-status-"):
        return "status"
    if EXPLORER_RE.search(base) or (row["host"] == APP_HOST and row["path"] == "/observatory"):
        return "explorer"
    return "product page"


def build():
    cfg_text, proxy_text = read(NEXT_CONFIG), read(PROXY)
    rules, noindex_hosts, retired, cfg_hosts = parse_next_config(cfg_text)
    px = parse_proxy(proxy_text)

    rows = {}

    def put(host, path, destination, catch_all, pattern, declared, gate=None, gate_file=None, source=None):
        key = (host, path)
        row = rows.get(key)
        if row is None:
            row = {"host": host, "path": path, "catch_all": catch_all, "source": source or path,
                   "destination": destination, "pattern": pattern, "file": dest_file(destination),
                   "gate": gate, "gate_file": gate_file, "declared_in": []}
            rows[key] = row
        else:
            # an explicit path beats a catch-all for the same key; keep the fallback on the row
            if row["catch_all"] and not catch_all:
                row.update({"fallback_destination": row["destination"], "destination": destination,
                            "file": dest_file(destination), "pattern": pattern, "catch_all": True})
            elif catch_all and not row["catch_all"]:
                row["fallback_destination"] = destination
                row["catch_all"] = True
            row["gate"] = row["gate"] or gate
            row["gate_file"] = row["gate_file"] or gate_file
        if declared not in row["declared_in"]:
            row["declared_in"].append(declared)
        return row

    # next.config.ts rewrites
    for rule in rules:
        host = rule["host"] or "*"
        for path, dest, catch_all, pattern in expand_source(rule["source"], rule["destination"]):
            put(host, path, dest, catch_all, pattern, "next.config.ts", source=rule["source"])

    # src/proxy.ts maps
    for sub, dest in px["simple"].items():
        put(sub + DOMAIN, "/", dest, True, False, "src/proxy.ts")
    for sub, m in px["multi"].items():
        for path, dest in m["paths"].items():
            if path == dest:
                continue  # asset passthrough (a PDF mapped to itself), not a surface
            put(sub + DOMAIN, path, dest, False, False, "src/proxy.ts")
        if m["default"]:
            put(sub + DOMAIN, "/", m["default"], True, False, "src/proxy.ts")
    for sub, a in px["ammo"].items():
        put(sub + DOMAIN, "/ammo", a["ammo"], False, False, "src/proxy.ts", GATE_PASSCODE, a["gate"])
    for b in px["blocks"]:
        host = b["sub"] + DOMAIN
        for g in b["gated_paths"]:
            put(host, g["path"], g["destination"], False, False, "src/proxy.ts", GATE_PASSCODE, g["gate_file"])
        if b["default"] and not b["host_gate"]:
            put(host, "/", b["default"], True, False, "src/proxy.ts")
        if b["host_gate"]:
            for (h, _p), row in rows.items():
                if h == host:
                    row["gate"] = GATE_PASSCODE + " (whole host)"
                    row["gate_file"] = row["gate_file"] or b["gate_file"]
                    if "src/proxy.ts" not in row["declared_in"]:
                        row["declared_in"].append("src/proxy.ts")

    # src/app routes
    app_rows = parse_app_routes()
    gated_app = {r["path"] for r in app_rows if r["gate"]}
    for r in app_rows:
        rows[(r["host"], r["path"])] = dict(r, pattern=False, gate_file=None)

    # destinations that are instances of a gated app route inherit its gate; a destination that IS
    # an app route (no file extension, e.g. jobs.arcs.care -> /jobs) inherits that route's purpose
    app_by_path = {r["path"]: r for r in app_rows}
    for row in rows.values():
        d = row["destination"] or ""
        for gp in gated_app:
            prefix = gp.split("[")[0]
            if "[" in gp and d.startswith(prefix) and d != prefix.rstrip("/"):
                row["gate"] = row["gate"] or GATE_ADMIN
        target = app_by_path.get(d)
        if target and row["file"] is None and "src/app" not in row["declared_in"]:
            for k in ("file", "title", "description", "index"):
                row[k] = target[k]
            row["gate"] = row["gate"] or target["gate"]

    # page harvest + classification
    missing = []
    for row in rows.values():
        f = row["file"]
        if f and os.path.exists(os.path.join(ROOT, f)) and f.endswith(".html"):
            t, d, robots = harvest_page(os.path.join(ROOT, f))
            row.setdefault("title", t)
            row.setdefault("description", d)
            row["index"] = robots
        elif f and not os.path.exists(os.path.join(ROOT, f)):
            row["file_missing"] = True
            missing.append(f)
        row.setdefault("title", None)
        row.setdefault("description", None)
        row.setdefault("index", None)
        if row["index"] is None and row["host"] in noindex_hosts:
            row["index"] = "noindex (header)"
        row["unlisted"] = bool(row["index"] and "noindex" in row["index"]) or row["host"] in noindex_hosts
        row["purpose"] = row["description"] or row["title"]
        row["kind"] = classify(row)

    ordered = [rows[k] for k in sorted(rows, key=lambda k: (k[0] == "*", k[0], k[1]))]
    for row in ordered:
        row["declared_in"] = sorted(row["declared_in"])
        row.pop("source", None) if row["source"] == row["path"] else None

    routed = {r["file"] for r in ordered if r["file"]} | {dest_file(r["gate_file"]) for r in ordered if r.get("gate_file")}
    unrouted = sorted(rel(p) for p in glob.glob(os.path.join(ROOT, "public", "*.html")) if rel(p) not in routed)

    hosts = sorted({r["host"] for r in ordered if r["host"] != "*"})
    by_kind = {k: sum(1 for r in ordered if r["kind"] == k) for k in KINDS}
    catalog = {
        "version": 1,
        "sources": ["next.config.ts", "src/proxy.ts", "src/app/**/{page.tsx,route.ts}"],
        "counts": {"rows": len(ordered), "hosts": len(hosts), "by_kind": by_kind,
                   "next_config_hosts": len(cfg_hosts), "proxy_hosts": len(px["simple"]) + len(px["multi"]) + len(px["ammo"]) + len({b["sub"] for b in px["blocks"]}),
                   "app_routes": len(app_rows), "missing_purpose": sum(1 for r in ordered if not r["purpose"]),
                   "unlisted": sum(1 for r in ordered if r["unlisted"])},
        "retired_hosts": retired,
        "noindex_header_hosts": noindex_hosts,
        "broken_destinations": sorted(set(missing)),
        "unrouted_public_html": unrouted,
        "rows": ordered,
    }
    return catalog, cfg_hosts


def stamp_dates(catalog):
    dates = git_dates([r["file"] for r in catalog["rows"]])
    for r in catalog["rows"]:
        r["last_commit"] = dates.get(r["file"]) if r["file"] else None
    return catalog


def strip_dates(catalog):
    c = json.loads(json.dumps(catalog))
    for r in c["rows"]:
        r.pop("last_commit", None)
    return c


# ---------------------------------------------------------------------------- render

FONT_FACES = """
@font-face{font-family:'Inter';font-style:normal;font-weight:100 900;font-display:swap;src:url('/fonts/inter-normal-100-900-latin-v1.woff2') format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;}
@font-face{font-family:'Inter';font-style:normal;font-weight:100 900;font-display:swap;src:url('/fonts/inter-normal-100-900-latin-ext-v1.woff2') format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF;}
@font-face{font-family:'JetBrains Mono';font-style:normal;font-weight:100 800;font-display:swap;src:url('/fonts/jetbrains-mono-normal-100-800-latin-v1.woff2') format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;}
@font-face{font-family:'JetBrains Mono';font-style:normal;font-weight:100 800;font-display:swap;src:url('/fonts/jetbrains-mono-normal-100-800-latin-ext-v1.woff2') format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF;}
"""

PAGE_CSS = """
/* DESIGN.md voices: Inter for reading, JetBrains Mono for instrument labels and identifiers, the
   serif display stack for the one title. Sizes are the DESIGN.md ramp (display, headline 1.15rem,
   body 0.925rem, label 0.625rem); radii are its rounded scale (xs 3px, sm 6px, pill). */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;text-size-adjust:100%;-webkit-text-size-adjust:100%}
body{background:var(--bg);font-size:0.925rem;line-height:1.6;overflow-x:hidden}
a{color:var(--cyan);text-decoration:none}
a:hover{text-decoration:underline}
a:focus-visible,button:focus-visible,input:focus-visible{outline:1px solid var(--cyan);outline-offset:-1px}
.wrap{max-width:1160px;margin:0 auto;padding:0 20px}
.mono{font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace}
.hero{border-bottom:1px solid var(--border);padding:48px 0 32px}
h1{font-family:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Newsreader',serif;font-size:clamp(1.5rem,4vw,2.4rem);font-weight:500;letter-spacing:-0.02em;line-height:1.2}
h1 .g{color:var(--cyan)}
.lede{font-size:1.15rem;font-weight:400;line-height:1.6;color:var(--muted);margin-top:16px;max-width:none}
.lede b{color:var(--text);font-weight:600}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-top:24px}
.stat{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:12px 14px}
.stat .n{font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:1.5rem;font-weight:600;line-height:1.2;color:var(--text)}
.stat .l{font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:0.925rem;font-weight:700;letter-spacing:0.08em;line-height:1.4;text-transform:uppercase;color:var(--dimmed);margin-top:8px}
.stat[data-kind="explorer"] .n{color:var(--cyan)}
.stat[data-kind="status"] .n{color:var(--green)}
.stat[data-kind="ledger"] .n{color:var(--gold)}
.stat[data-kind="gated"] .n{color:var(--red)}
main{padding:24px 0 48px}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;position:sticky;top:0;background:var(--bg);padding:12px 0;border-bottom:1px solid var(--border);z-index:2}
.controls input{flex:1 1 260px;min-height:44px;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);font:inherit;font-size:1.15rem;padding:0 12px}
.controls input:focus{border-color:var(--cyan)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{min-height:44px;padding:0 14px;background:transparent;border:1px solid var(--border);border-radius:999px;color:var(--muted);font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:0.925rem;cursor:pointer}
.chip:hover{border-color:var(--cyan);color:var(--cyan)}
.chip[aria-pressed="true"]{color:var(--cyan);border-color:var(--cyan);background:var(--cyan-bg)}
.count{font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;color:var(--dimmed);margin:12px 0 4px}
.host{margin-top:24px}
.host h2{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:1.15rem;font-weight:600;letter-spacing:-0.01em;line-height:1.25;padding-bottom:8px;border-bottom:1px solid var(--border)}
.host h2 a{color:var(--text)}
.host h2 .meta{font-size:0.925rem;font-weight:400;color:var(--dimmed)}
.badge{display:inline-block;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:0.925rem;font-weight:600;line-height:1.4;padding:2px 8px;border-radius:3px;border:1px solid var(--border);color:var(--muted);white-space:nowrap}
.badge[data-kind="explorer"]{color:var(--cyan);border-color:var(--cyan);background:var(--cyan-bg)}
.badge[data-kind="status"]{color:var(--green);border-color:var(--green);background:var(--green-bg)}
.badge[data-kind="ledger"]{color:var(--gold);border-color:var(--gold);background:var(--gold-bg)}
.badge[data-kind="gated"]{color:var(--red);border-color:var(--red);background:var(--red-bg)}
.badge.unlisted{color:var(--dimmed);border-style:dashed}
table{width:100%;border-collapse:collapse;margin-top:4px}
th{font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:0.925rem;font-weight:700;letter-spacing:0.08em;line-height:1.4;text-transform:uppercase;color:var(--dimmed);text-align:left;padding:10px 10px 8px;border-bottom:1px solid var(--border)}
td{padding:10px;border-bottom:1px solid var(--border);vertical-align:top;overflow-wrap:anywhere}
.cell{display:block}
.kinds{display:flex;flex-wrap:wrap;gap:6px}
td.path a{font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;color:var(--text)}
td.path .src{display:block;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;color:var(--dimmed);margin-top:2px}
td.purpose{color:var(--muted)}
td.purpose .t{display:block;color:var(--text);font-weight:600}
td.purpose .gate{display:block;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;color:var(--red);margin-top:2px}
td.file,td.date{font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;color:var(--dimmed);white-space:nowrap}
td.file{white-space:normal}
tr[hidden]{display:none}
.retired{margin-top:40px;padding:16px 18px;background:var(--surface);border:1px solid var(--border);border-radius:6px}
.retired h2{font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:1.15rem;font-weight:600;line-height:1.25;color:var(--text);margin-bottom:8px}
.retired p,.retired ul{color:var(--muted)}
.retired ul{list-style:none;display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:6px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace}
footer{border-top:1px solid var(--border);padding:20px 0 40px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;color:var(--dimmed);line-height:1.6}
footer b{color:var(--muted);font-weight:600}
@media (max-width:760px){
  thead{display:none}
  table,tbody,tr,td{display:block}
  tr{padding:8px 0;border-bottom:1px solid var(--border)}
  td{border:0;padding:4px 0;display:grid;grid-template-columns:72px 1fr;gap:8px;align-items:start}
  td::before{content:attr(data-l);font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:0.925rem;font-weight:700;letter-spacing:0.08em;line-height:1.4;text-transform:uppercase;color:var(--dimmed);padding-top:4px}
  td.file,td.date{white-space:normal}
  .controls{position:static}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

FILTER_JS = """
(function(){
  var q=document.getElementById('q'),chips=document.querySelectorAll('.chip'),rows=document.querySelectorAll('tr[data-text]'),
      hosts=document.querySelectorAll('section.host'),count=document.getElementById('count'),kind='';
  function apply(){
    var needle=(q.value||'').toLowerCase().trim(),shown=0;
    rows.forEach(function(r){
      var ok=(!kind||r.getAttribute('data-kind')===kind)&&(!needle||r.getAttribute('data-text').indexOf(needle)>=0);
      r.hidden=!ok; if(ok) shown++;
    });
    hosts.forEach(function(h){h.hidden=!h.querySelector('tr[data-text]:not([hidden])');});
    count.textContent=shown+' of '+rows.length+' surfaces'+(kind?' · '+kind:'')+(needle?' · "'+needle+'"':'');
  }
  q.addEventListener('input',apply);
  chips.forEach(function(c){c.addEventListener('click',function(){
    var k=c.getAttribute('data-kind');kind=(kind===k)?'':k;
    chips.forEach(function(x){x.setAttribute('aria-pressed',String(x.getAttribute('data-kind')===kind));});
    apply();
  });});
  apply();
})();
"""


def e(s):
    """Escape for HTML. Harvested titles may carry an em-dash; the page's own copy never does
    (repo rule, artifact_wrap_lint MODE 1), so it is shown as a middle dot. The JSON keeps the verbatim text."""
    s = re.sub(r"\s*—\s*", " · ", s or "")          # em-dash, anywhere
    s = re.sub(r"\s+–\s+", " · ", s)                 # spaced en-dash (a separator, not a range)
    return html.escape(s, quote=True)


def render(catalog):
    tokens = read(TOKENS).strip()
    c = catalog["counts"]
    rows = catalog["rows"]
    hosts = []
    for r in rows:
        if not hosts or hosts[-1][0] != r["host"]:
            hosts.append((r["host"], []))
        hosts[-1][1].append(r)

    out = []
    out.append("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
               "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
               "<meta name=\"robots\" content=\"noindex, nofollow\">\n"
               "<title>ARCS Surfaces</title>\n"
               "<meta name=\"description\" content=\"Every arcs.care surface in one catalog: host, path, what it serves, "
               "what kind of page it is, and when its file last changed. Harvested from the routing config, never hand-listed.\">\n"
               "<style>\n" + tokens + "\n" + FONT_FACES + PAGE_CSS + "</style>\n"
               "<script defer src=\"/_vercel/insights/script.js\"></script>\n</head>\n<body>\n")
    out.append("<header class=\"hero\"><div class=\"wrap\">\n"
               "<h1>Every arcs.care surface, <span class=\"g\">one map.</span></h1>\n"
               "<p class=\"lede\"><b>%d surfaces across %d hosts</b>, harvested from the routing config and the app tree. "
               "Nothing here is hand-listed: a host that is routed but missing from this catalog fails the build. "
               "Dates are the last commit that touched the served file.</p>\n" % (c["rows"], c["hosts"]))
    out.append("<div class=\"stats\">\n<div class=\"stat\"><div class=\"n\">%d</div><div class=\"l\">surfaces</div></div>\n"
               "<div class=\"stat\"><div class=\"n\">%d</div><div class=\"l\">hosts</div></div>\n" % (c["rows"], c["hosts"]))
    for k in KINDS:
        out.append("<div class=\"stat\" data-kind=\"%s\"><div class=\"n\">%d</div><div class=\"l\">%s</div></div>\n"
                   % (e(k), c["by_kind"][k], e(k)))
    out.append("</div>\n</div></header>\n")

    out.append("<main class=\"wrap\">\n<div class=\"controls\">\n"
               "<input type=\"search\" id=\"q\" placeholder=\"Filter by host, path or purpose\" aria-label=\"Filter surfaces\">\n"
               "<div class=\"chips\" role=\"group\" aria-label=\"Kind\">\n")
    for k in KINDS:
        out.append("<button type=\"button\" class=\"chip\" data-kind=\"%s\" aria-pressed=\"false\">%s</button>\n" % (e(k), e(k)))
    out.append("</div>\n</div>\n<p class=\"count\" id=\"count\">%d surfaces</p>\n" % c["rows"])

    for host, hrows in hosts:
        unlisted = any(r["unlisted"] for r in hrows)
        gated = all(r["gate"] for r in hrows)
        label = "any host" if host == "*" else host
        link = ("<span>%s</span>" % e(label)) if host == "*" else \
               ("<a href=\"https://%s\" rel=\"nofollow noopener\">%s</a>" % (e(host), e(host)))
        meta = "%d surface%s" % (len(hrows), "" if len(hrows) == 1 else "s")
        if unlisted:
            meta += " <span class=\"badge unlisted\">unlisted</span>"
        if gated:
            meta += " <span class=\"badge\" data-kind=\"gated\">gated</span>"
        out.append("<section class=\"host\" data-host=\"%s\">\n<h2>%s <span class=\"meta\">%s</span></h2>\n"
                   "<table>\n<thead><tr><th>Path</th><th>Kind</th><th>Purpose</th><th>Serves</th><th>Last change</th></tr></thead>\n<tbody>\n"
                   % (e(host), link, meta))
        for r in hrows:
            text = " ".join(filter(None, [r["host"], r["path"], r["kind"], r["purpose"], r["file"], r["destination"]])).lower()
            href = None if host == "*" or r.get("pattern") else "https://%s%s" % (host, r["path"])
            path_html = ("<a href=\"%s\" rel=\"nofollow noopener\">%s</a>" % (e(href), e(r["path"]))) if href else \
                        ("<span class=\"mono\">%s</span>" % e(r["path"]))
            if r.get("catch_all"):
                path_html += "<span class=\"src\">catch-all</span>"
            purpose = ""
            if r["title"] and r["description"]:
                purpose = "<span class=\"t\">%s</span>%s" % (e(r["title"]), e(r["description"]))
            elif r["purpose"]:
                purpose = e(r["purpose"])
            else:
                purpose = "<span class=\"src\">no title or description declared</span>"
            if r["gate"]:
                purpose += "<span class=\"gate\">gate: %s</span>" % e(r["gate"])
            serves = e(r["file"] or r["destination"])
            if r.get("file_missing"):
                serves += " <span class=\"badge\" data-kind=\"gated\">missing</span>"
            if r.get("fallback_destination"):
                serves += "<span class=\"src\">fallback %s</span>" % e(r["fallback_destination"])
            kind = "<span class=\"badge\" data-kind=\"%s\">%s</span>" % (e(r["kind"]), e(r["kind"]))
            if r["unlisted"]:
                kind += "<span class=\"badge unlisted\">unlisted</span>"
            out.append("<tr data-kind=\"%s\" data-text=\"%s\"><td class=\"path\" data-l=\"path\"><span class=\"cell\">%s</span></td>"
                       "<td data-l=\"kind\"><span class=\"cell kinds\">%s</span></td><td class=\"purpose\" data-l=\"purpose\"><span class=\"cell\">%s</span></td>"
                       "<td class=\"file\" data-l=\"serves\"><span class=\"cell\">%s</span></td><td class=\"date\" data-l=\"changed\"><span class=\"cell\">%s</span></td></tr>\n"
                       % (e(r["kind"]), e(text), path_html, kind, purpose, serves, e(r.get("last_commit") or "")))
        out.append("</tbody>\n</table>\n</section>\n")

    if catalog["retired_hosts"]:
        out.append("<section class=\"retired\">\n<h2>Retired hosts</h2>\n<p>Permanent redirects to arcs.care; "
                   "kept in the config so old links still land somewhere.</p>\n<ul>\n")
        for h in catalog["retired_hosts"]:
            out.append("<li>%s</li>\n" % e(h))
        out.append("</ul>\n</section>\n")
    out.append("</main>\n")
    out.append("<footer><div class=\"wrap\">\n<b>Sources:</b> next.config.ts rewrites, src/proxy.ts host blocks, "
               "src/app routes; titles and descriptions read from each served file; dates from git.<br>\n"
               "<b>Counts:</b> %d routed hosts in next.config.ts · %d hosts in src/proxy.ts · %d app routes · "
               "%d surfaces without a declared title or description · %d served files not routed by any rule.<br>\n"
               "<b>Rebuild:</b> the surface catalog emitter in scripts/ writes the JSON and this page; "
               "the same script gates the build when a routed host is missing from the catalog.\n</div></footer>\n"
               % (c["next_config_hosts"], c["proxy_hosts"], c["app_routes"], c["missing_purpose"],
                  len(catalog["unrouted_public_html"])))
    out.append("<script>" + FILTER_JS + "</script>\n</body>\n</html>\n")
    return "".join(out)


# ---------------------------------------------------------------------------- check / main


def check():
    problems = []
    if not os.path.exists(OUT_JSON):
        return ["catalog missing: %s (run the emitter)" % rel(OUT_JSON)]
    committed = json.load(open(OUT_JSON, encoding="utf-8"))
    fresh, cfg_hosts = build()

    have = {r["host"] for r in committed.get("rows", [])} | set(committed.get("retired_hosts", [])) \
        | set(committed.get("noindex_header_hosts", []))
    for h in cfg_hosts:
        if h not in have:
            problems.append("host in next.config.ts missing from the catalog: %s" % h)

    a, b = strip_dates(committed), strip_dates(fresh)
    if a != b:
        ka = {(r["host"], r["path"]) for r in a["rows"]}
        kb = {(r["host"], r["path"]) for r in b["rows"]}
        for k in sorted(kb - ka):
            problems.append("surface routed but not in the catalog: %s%s" % k)
        for k in sorted(ka - kb):
            problems.append("catalog row no longer routed: %s%s" % k)
        if ka == kb:
            changed = [k for k in sorted(ka) if next(r for r in a["rows"] if (r["host"], r["path"]) == k)
                       != next(r for r in b["rows"] if (r["host"], r["path"]) == k)]
            for k in changed[:10]:
                problems.append("catalog row stale: %s%s" % k)
            for key in ("retired_hosts", "noindex_header_hosts", "broken_destinations", "unrouted_public_html"):
                if a.get(key) != b.get(key):
                    added, gone = sorted(set(b[key]) - set(a[key])), sorted(set(a[key]) - set(b[key]))
                    problems.append("%s changed: +%s -%s" % (key, added or "[]", gone or "[]"))
            if not changed and a.get("counts") != b.get("counts") and len(problems) == 0:
                problems.append("catalog counts stale")

    if not os.path.exists(OUT_HTML):
        problems.append("page missing: %s" % rel(OUT_HTML))
    elif read(OUT_HTML) != render(committed):
        problems.append("%s is not the render of %s (re-run the emitter; never hand-edit the page)"
                        % (rel(OUT_HTML), rel(OUT_JSON)))
    return problems


def emit():
    catalog, _ = build()
    stamp_dates(catalog)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(OUT_HTML, "w", encoding="utf-8") as fh:
        fh.write(render(catalog))
    c = catalog["counts"]
    print("surface-catalog: %d rows · %d hosts · %s · %d unlisted · %d without purpose · %d unrouted public pages -> %s + %s"
          % (c["rows"], c["hosts"], ", ".join("%s %d" % (k, v) for k, v in c["by_kind"].items()),
             c["unlisted"], c["missing_purpose"], len(catalog["unrouted_public_html"]), rel(OUT_JSON), rel(OUT_HTML)))
    if catalog["broken_destinations"]:
        print("  ⚠ rewrite destinations with no file: " + ", ".join(catalog["broken_destinations"]))
    return 0


def self_test():
    """Fails-on-bad and passes-on-good, against synthetic inputs (never the live files)."""
    rules, noindex, retired, hosts = parse_next_config(
        'async headers() { return [ { source: "/:path*", has: [{ type: "host", value: "x.arcs.care" }], '
        'headers: [{ key: "X-Robots-Tag", value: "noindex" }] } ]; }\n'
        'async rewrites() { return { beforeFiles: [ '
        '{ source: "/:seg(a|b)", destination: "/pf-:seg.html", has: [{ type: "host", value: "x.arcs.care" }] }, '
        '{ source: "/:path((?!fonts/).*)", destination: "/x.html", has: [{ type: "host", value: "x.arcs.care" }] }, '
        '{ source: "/case-study", destination: "/case-study.html" } ] }; }\n'
        'async redirects() { const retiredFanaticsHosts = [ "old.arcs.care" ]; return []; }\n};\n\nexport default c;')
    assert [r["host"] for r in rules] == ["x.arcs.care", "x.arcs.care", None], rules
    assert expand_source(rules[0]["source"], rules[0]["destination"]) == [("/a", "/pf-a.html", False, False), ("/b", "/pf-b.html", False, False)]
    assert expand_source(rules[1]["source"], rules[1]["destination"]) == [("/", "/x.html", True, False)]
    assert expand_source("/blog/nftt/:slug/:tier(brief|full)", "/blog-nftt-:slug-:tier.html")[0][3] is True
    assert noindex == ["x.arcs.care"] and retired == ["old.arcs.care"] and hosts == ["old.arcs.care", "x.arcs.care"]
    px = parse_proxy(
        "const SUBDOMAIN_MAP: Record<string, string> = {\n  'resume': '/resume.html',\n}\n"
        "const AMMO_HOSTS = {\n  'sch': { ammoFile: '/sch-ammo.html', gateFile: '/sch-gate.html' },\n}\n"
        "const MULTI_PATH_MAP = {\n  'saul': { '/followup': '/saul-followup.html', '/saul.pdf': '/saul.pdf', default: '/saul.html' },\n}\n"
        "export default async function proxy(request) {\n"
        "  if (sub === 'lw' && !open) {\n    const ok = await ammoUnlocked(a, b)\n    if (!ok) { url.pathname = '/lw-gate.html' }\n  }\n"
        "  if (sub === 'rh') {\n    if (pathname === '/ammo') {\n      const ok = await ammoUnlocked(a, b)\n"
        "      url.pathname = ok ? '/rh-ammo.html' : '/rh-gate.html'\n    }\n    url.pathname = '/rh.html'\n  }\n}\n")
    assert px["simple"] == {"resume": "/resume.html"}
    assert px["ammo"]["sch"]["gate"] == "/sch-gate.html"
    assert px["multi"]["saul"]["paths"]["/followup"] == "/saul-followup.html" and px["multi"]["saul"]["default"] == "/saul.html"
    blocks = {b["sub"]: b for b in px["blocks"]}
    assert blocks["lw"]["host_gate"] is True and blocks["lw"]["gate_file"] == "/lw-gate.html"
    assert blocks["rh"]["gated_paths"] == [{"path": "/ammo", "destination": "/rh-ammo.html", "gate_file": "/rh-gate.html"}]
    assert blocks["rh"]["default"] == "/rh.html" and blocks["rh"]["host_gate"] is False
    title, desc, noi = _metadata('const TITLE = "T"\nexport const metadata = { title: TITLE, description: "D", robots: { index: false } }')
    assert (title, desc, noi) == ("T", "D", True)
    # the live gate: a host dropped from the committed catalog must be reported
    catalog, cfg_hosts = build()
    assert cfg_hosts, "no hosts parsed from next.config.ts"
    missing_host = next(h for h in cfg_hosts if any(r["host"] == h for r in catalog["rows"]))
    bad = json.loads(json.dumps(catalog))
    bad["rows"] = [r for r in bad["rows"] if r["host"] != missing_host]
    have = {r["host"] for r in bad["rows"]} | set(bad["retired_hosts"]) | set(bad["noindex_header_hosts"])
    assert missing_host not in have
    assert render(catalog) == render(catalog), "render is not deterministic"
    print("✓ surface_catalog_emit self-test: parsers, expansion, gate detection and determinism hold; "
          "a dropped host (%s) is detectable" % missing_host)
    return 0


def main():
    ap = argparse.ArgumentParser(description="arcs.care surface catalog: emit, check, self-test")
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed catalog or page is stale or misses a host")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.check:
        problems = check()
        if problems:
            print("✖ surface-catalog --check: %d problem(s)" % len(problems))
            for p in problems:
                print("    " + p)
            print("  fix: python3 scripts/surface_catalog_emit.py  (then stage runtime/specs/surface-catalog.json + runtime/warroom/surfaces.html)")
            return 1
        print("✓ surface-catalog: every next.config.ts host is catalogued; JSON and page are current")
        return 0
    return emit()


if __name__ == "__main__":
    sys.exit(main())
