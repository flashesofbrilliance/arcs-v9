#!/usr/bin/env python3
"""page_tune: the shared --tune / --apply mechanics for every page builder (one copy; builders call it, never fork it).

A builder wires the live editor (src/ui-kit/token-tuner.js) with two flags:
  --tune OUT.html     an internal copy with the tuner inlined (?tune sliders, ?edit data-src text, double-click text).
                      Refuses any path under public/: the tuner is internal only, and page_gate.py --counterpart
                      fails any page that still carries it.
  --apply FILE [...]  take what the tuner exported and write it back to the page's SOURCE, then rebuild.

What --apply accepts (any mix, one file each):
  Copy JSON        RFC 6902 ops [{op: replace|add, path, value}, {op: move, from, path} (block reorder in one slot)] for the data file (data-src text, a data breakpoint)
  Copy edits       [{old, new}] text pairs from double-click editing
  Export versions  {versions: [...]}: the latest version's whole state (or --version N): tokens, wrapping, breakpoints, text
  Copy CSS         the one-line :root{...} plus text-wrap rules, as a .css or .txt file

Where each part lands is the builder's declaration, not a guess:
  sources   ordered list of (kind, path): "json" (string values, plain text), "json-html" (string values that are trusted
            HTML), "html" (an HTML file), "text" (Markdown or other plain text). A text pair goes to the FIRST source that
            holds its old text; it must be there exactly once, else nothing is written.
  style     where token and wrap changes go: ("block", path) a sentinel block (/* arcs-tuned:start */ .. :end */) placed
            before the last </style> of an HTML file or at the end of a CSS file; ("json-tokens", path, key) merged into a
            data object; None when the page declares no tuner tokens (the change is refused and named).
  bp_ptr    the data pointer the page's own breakpoint lives at (tabbed-brief /stack_below), or None: then a moved
            breakpoint is printed as "set in source by hand" (media and container widths live in kit or template CSS).

JSON is edited in place by value span, so a one-field change is a one-line diff and the file keeps its own format.

  python3 scripts/page_tune.py --self-test
Stdlib only.
"""
import html as htmllib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import token_tuner_inline as tti  # noqa: E402

TUNE = [False]  # on while a --tune build renders: span() wraps each data string in its JSON pointer
B_START, B_END = "/* arcs-tuned:start (page_tune.py --apply; tuner values) */", "/* arcs-tuned:end */"
B_RE = re.compile(re.escape(B_START) + r"\n?(.*?)\n?" + re.escape(B_END) + r"\n?", re.S)


def rel(p):
    """A repo path relative to the root; anything outside the repo stays absolute."""
    a = os.path.abspath(p)
    return os.path.relpath(a, ROOT) if a.startswith(ROOT + os.sep) else a


def span(html_, ptr):
    """Wrap rendered html_ for ?edit when a --tune build is rendering; otherwise return it unchanged."""
    return ('<span data-src="%s">%s</span>' % (htmllib.escape(ptr, quote=True), html_)) if (TUNE[0] and ptr) else html_


def refuse_public(out):
    if os.path.abspath(out).startswith(os.path.join(ROOT, "public") + os.sep):
        raise SystemExit("--tune output must not live under public/: the tuner is internal only")


def tune_write(page, out, bp=None, bp_src=None):
    """Write the internal tuned copy: the tuner inlined first in <body>; the data breakpoint named on <main> if given."""
    refuse_public(out)
    if bp is not None and bp_src:
        page = re.sub(r"<main\b", '<main data-bp="%d" data-bp-src="%s"' % (bp, bp_src), page, count=1)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    try:
        page = tti.inline(page)
    except ValueError:  # a fragment with no <body> or <main> (an Artifact body): the tuner goes first
        page = tti.block() + tti.strip(page)
    open(out, "w", encoding="utf-8").write(page)
    print("wrote %s (open with ?tune for sliders, ?tune&edit to edit text)" % out)


# ---------- the tuner's own tables, read from the JS so units and wrap selectors are never forked ----------
def tuner_tables():
    js = open(tti.SRC, encoding="utf-8").read()
    units = dict(re.findall(r"\['(--[\w-]+)', '(\w*)', -?[\d.]+, -?[\d.]+, [\d.]+\]", js))
    wraps = re.findall(r"\['[\w ]+', '(:is\([^']+\))'\]", js)
    return units, wraps


def fmt(v):
    return ("%.4f" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


# ---------- reading what the tuner exported ----------
def parse_css(t):
    """A Copy CSS line -> (tokens {name: value-with-unit}, wraps {selector: value})."""
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    tok, wrap = {}, {}
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", t):
        sel = sel.strip()
        decl = dict((k.strip(), v.strip()) for k, v in (x.split(":", 1) for x in body.split(";") if ":" in x))
        if sel == ":root":
            tok.update(decl)
        elif "text-wrap" in decl:
            wrap[sel] = decl["text-wrap"]
    return tok, wrap


def load(paths, version=None):
    """Every export file -> one change set {ops, pairs, tok, wrap, bp}."""
    units, wraps = tuner_tables()
    cs = {"ops": [], "pairs": [], "tok": {}, "wrap": {}, "bp": {}}
    for p in paths:
        raw = open(p, encoding="utf-8").read()
        try:
            doc = json.loads(raw)
        except ValueError:
            tok, wrap = parse_css(raw)
            for note in re.findall(r"/\* breakpoints, set in source: (.*?) \*/", raw):
                print("note: breakpoints moved (%s); widths live in kit or template CSS, set them in source by hand" % note)
            if not (tok or wrap):
                raise SystemExit("%s: neither JSON nor a Copy CSS line" % p)
            cs["tok"].update(tok); cs["wrap"].update(wrap)
            continue
        if isinstance(doc, list):
            if all(isinstance(x, dict) and "path" in x for x in doc):
                cs["ops"] += doc
            elif all(isinstance(x, dict) and ("old" in x or x.get("op") in STRUCT) for x in doc):
                cs["pairs"] += doc  # Copy edits: {old, new[, html]} pairs, and line joins/removals {op: merge|remove, parts}
            else:
                raise SystemExit("%s: a list, but neither JSON patch ops nor Copy edits" % p)
            continue
        st = doc
        if "versions" in doc:
            vs = doc["versions"] or []
            pick = vs[-1] if version is None else next((v for v in vs if v.get("v") == version), None)
            if not pick:
                raise SystemExit("%s: no version %s" % (p, version if version is not None else "(empty)"))
            st = pick.get("state") or {}
        for k, v in (st.get("tok") or {}).items():
            cs["tok"][k] = fmt(v) + units.get(k, "")
        for i, v in enumerate(st.get("wrap") or []):
            if v and i < len(wraps):
                cs["wrap"][wraps[i]] = v
        cs["bp"].update(st.get("bp") or {})
        cs["ops"] += [{"op": "replace", "path": k, "value": v} for k, v in (st.get("text") or {}).items()]
        cs["pairs"] += st.get("dbl") or []
    return cs


# ---------- JSON edited by value span ----------
_WS = re.compile(r"\s*")
_STR = re.compile(r'"(?:[^"\\]|\\.)*"', re.S)
_NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null")


def spans(raw):
    """{json pointer: (start, end)} for every scalar value in raw JSON text."""
    out = {}

    def val(i, ptr):
        i = _WS.match(raw, i).end()
        c = raw[i]
        if c == "{":
            i = _WS.match(raw, i + 1).end()
            if raw[i] == "}":
                return i + 1
            while True:
                m = _STR.match(raw, _WS.match(raw, i).end())
                key = json.loads(m.group(0))
                i = _WS.match(raw, m.end()).end() + 1  # past ':'
                i = val(i, ptr + "/" + key.replace("~", "~0").replace("/", "~1"))
                i = _WS.match(raw, i).end()
                if raw[i] == "}":
                    return i + 1
                i += 1  # ','
        if c == "[":
            i = _WS.match(raw, i + 1).end()
            if raw[i] == "]":
                return i + 1
            n = 0
            while True:
                i = _WS.match(raw, val(i, "%s/%d" % (ptr, n))).end()
                n += 1
                if raw[i] == "]":
                    return i + 1
                i += 1
        m = (_STR if c == '"' else _NUM).match(raw, i)
        out[ptr] = (m.start(), m.end())
        return m.end()

    val(0, "")
    return out


def enc(v, like):
    """JSON-encode v the way the file wrote its neighbour (escaped non-ASCII or literal)."""
    return json.dumps(v, ensure_ascii=bool(re.search(r"\\u[0-9a-fA-F]{4}", like)))


def get(d, ptr):
    for k in ptr.split("/")[1:]:
        k = k.replace("~1", "/").replace("~0", "~")
        d = d[int(k)] if isinstance(d, list) else d[k]
    return d


def set_ptr(d, ptr, value, op):
    keys = [k.replace("~1", "/").replace("~0", "~") for k in ptr.split("/")[1:]]
    cur = d
    for k in keys[:-1]:
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    last = keys[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    elif op == "replace" and last not in cur:
        raise SystemExit("replace on a missing key: %s" % ptr)
    else:
        cur[last] = value


def move_ptr(d, frm, to):
    """RFC 6902 move, limited to a reorder inside one array: /a/blocks/2 to /a/blocks/0."""
    fa, fi = frm.rsplit("/", 1) if "/" in frm else ("", "")
    ta, ti = to.rsplit("/", 1)
    if fa != ta or not fi.isdigit() or not ti.isdigit():
        raise SystemExit("move must reorder inside one array: %s to %s" % (frm, to))
    arr = get(d, fa) if fa else d
    if not isinstance(arr, list) or int(fi) >= len(arr) or int(ti) >= len(arr):
        raise SystemExit("move out of range: %s to %s" % (frm, to))
    arr.insert(int(ti), arr.pop(int(fi)))


def json_write_ops(path, ops):
    """Apply replace/add ops to a JSON file. Scalars are spliced in place; anything else re-dumps in the file's indent."""
    raw = open(path, encoding="utf-8").read()
    d = json.loads(raw)
    sp = spans(raw)
    edits = []
    # moves (block reorder within one slot) run after every replace/add: text pointers name the pre-move order
    ops = [o for o in ops if o.get("op") != "move"] + [o for o in ops if o.get("op") == "move"]
    for op in ops:
        if op.get("op") == "move":
            move_ptr(d, op.get("from", ""), op["path"])
            edits = None
            continue
        if op.get("op") not in ("replace", "add"):
            raise SystemExit("unsupported op %r (the tuner writes replace, add and move)" % op.get("op"))
        set_ptr(d, op["path"], op["value"], op["op"])
        if op["path"] in sp and not isinstance(op["value"], (dict, list)):
            a, b = sp[op["path"]]
            edits.append((a, b, enc(op["value"], raw[a:b])))
        else:
            edits = None
            break
    if edits is None:  # a new key or a structured value: re-dump in the file's own indent
        m = re.search(r"\n( +)\"", raw)
        out = json.dumps(d, indent=len(m.group(1)) if m else 1, ensure_ascii=False) + ("\n" if raw.endswith("\n") else "")
    else:
        out = raw
        for a, b, t in sorted(edits, reverse=True):
            out = out[:a] + t + out[b:]
    assert json.loads(out) == d, "splice drifted from the parsed result"
    return out, d


# ---------- text pairs ----------
def hits_in(text, old):
    return list(re.finditer(tti.text_pattern(old), text))


def masked(raw, mask):
    """raw with every match of mask (a generated region, e.g. a synced data block) blanked to NULs, same length."""
    return re.sub(mask, lambda m: "\0" * len(m.group(0)), raw, flags=re.S) if mask else raw


STRUCT = ("merge", "remove")  # line joins and removals from double-click editing (token_tuner_inline.run_span)


def place_pairs(pairs, sources):
    """Assign each edit to the first source holding it. A source is (kind, path) or (kind, path, mask regex); masked regions
    of a text or html source are generated, so they never take an edit. Whole-element edits ({html: true}) and line joins or
    removals ({op: merge|remove, parts}) change markup, so only html sources take them.
    Returns ({path: [(kind, target, edit)]}, errors); target is a JSON pointer, or a cut (start, end, replacement)."""
    plan, errors = {}, []
    for i, pr in enumerate(pairs):
        struct, as_html = pr.get("op") in STRUCT, bool(pr.get("html"))
        old = pr.get("old", "")
        if not struct and not old.strip():
            errors.append("edit %d: empty old text" % (i + 1)); continue
        what = (pr.get("parts") or [""])[0] if struct else old
        done = False
        for src in sources:
            kind, path, mask = (tuple(src) + (None,))[:3]
            if (struct or as_html) and kind != "html":
                continue
            raw = open(path, encoding="utf-8").read()
            if struct:
                cut, why = tti.run_span(masked(raw, mask), pr)
                if why and "found 0 times" in why:
                    continue
                if why:
                    errors.append("edit %d in %s: %s" % (i + 1, rel(path), why))
                else:
                    plan.setdefault(path, []).append((kind, cut, pr))
                done = True
                break
            if kind in ("json", "json-html"):
                sp = spans(raw)
                found = [(ptr, h) for ptr, (a, b) in sp.items() if raw[a] == '"' for h in hits_in(json.loads(raw[a:b]), old)]
            else:
                pat = re.escape(old) if as_html else tti.text_pattern(old)
                new = pr.get("new", "") if (as_html or kind != "html") else htmllib.escape(pr.get("new", ""), quote=False)
                found = [((h.start(), h.end(), new), h) for h in re.finditer(pat, masked(raw, mask))]
            if not found:
                continue
            if len(found) > 1:
                errors.append("edit %d: old text found %d times in %s, need exactly 1: %r" % (i + 1, len(found), rel(path), old[:60]))
            else:
                plan.setdefault(path, []).append((kind, found[0][0], pr))
            done = True
            break
        if not done:
            kinds = "an html source" if (struct or as_html) else "any source"
            errors.append("edit %d: not in %s (%s): %r" % (i + 1, kinds, ", ".join(rel(x[1]) for x in sources), what[:60]))
    return plan, errors


def apply_pairs_to(path, items):
    """Write the pairs placed in one source. JSON pairs become replace ops on the value that holds them."""
    kind = items[0][0]
    raw = open(path, encoding="utf-8").read()
    if kind in ("json", "json-html"):
        d = json.loads(raw)
        ops = {}
        for _, ptr, pr in items:
            cur = ops.get(ptr, get(d, ptr))
            new = pr["new"] if kind == "json" else htmllib.escape(pr["new"], quote=False)
            m = hits_in(cur, pr["old"])[0]
            ops[ptr] = cur[:m.start()] + new + cur[m.end():]
        out, _ = json_write_ops(path, [{"op": "replace", "path": p, "value": v} for p, v in ops.items()])
        return out
    # cuts were found on the masked text, same offsets; html text pairs arrive escaped, Markdown literal
    cuts = sorted((cut for _, cut, _ in items), reverse=True)
    for (a, b, _), (c, d, _) in zip(cuts, cuts[1:]):
        if d > a:
            raise SystemExit("two edits overlap in %s" % rel(path))
    for a, b, t in cuts:
        raw = raw[:a] + t + raw[b:]
    return raw


# ---------- style ----------
def style_block(prev, tok, wrap):
    """Merge new token and wrap values into the existing tuned block's rules."""
    ptok, pwrap = parse_css(prev or "")
    ptok.update(tok); pwrap.update(wrap)
    lines = []
    if ptok:
        lines.append(":root{%s}" % "".join("%s:%s;" % kv for kv in sorted(ptok.items())))
    lines += ["%s{text-wrap:%s}" % kv for kv in sorted(pwrap.items())]
    return "\n".join(lines)


def put_block(raw, body, is_html):
    m = B_RE.search(raw)
    blk = B_START + "\n" + body + "\n" + B_END + "\n"
    if m:
        return raw[:m.start()] + blk + raw[m.end():]
    if is_html:
        h = raw.lower().find("</head>")  # the last stylesheet in <head>; never a "</style>" inside a later script string
        i = raw.rfind("</style>", 0, h) if h > -1 else raw.rfind("</style>")
        if i < 0:
            raise SystemExit("no </style> to put the tuned block before")
        return raw[:i] + blk + raw[i:]
    return raw + ("" if raw.endswith("\n") else "\n") + blk


# ---------- the one entry point builders call ----------
def apply(paths, sources, style=None, bp_ptr=None, bp_default=None, version=None, data_path=None, validate=None):
    """Write the exported change set to the page's sources. Nothing is written if any part is refused.
    data_path: the JSON file pointer ops address (default: the first json source). validate(dict) -> [errors]."""
    cs = load(paths, version)
    writes, errors = {}, []
    data_path = data_path or next((s[1] for s in sources if s[0].startswith("json")), None)
    ops = list(cs["ops"])
    if cs["bp"]:
        units_bp = {k: v for k, v in cs["bp"].items()}
        if bp_ptr:
            # the data breakpoint is the one numeric key equal to the page's current value
            try:
                cur = get(json.load(open(data_path, encoding="utf-8")), bp_ptr)
            except (KeyError, IndexError):
                cur = bp_default
            mv = units_bp.pop(str(cur), None) if cur is not None else None
            if mv is not None:
                ops.append({"op": "add", "path": bp_ptr, "value": int(mv) if float(mv).is_integer() else mv})
        for k, v in units_bp.items():
            print("note: breakpoint %s moved to %s; widths live in kit or template CSS, set it in source by hand" % (k, v))
    if ops:
        if not data_path:
            errors.append("JSON patch ops given, but this page has no data file")
        else:
            out, d = json_write_ops(data_path, ops)
            writes[data_path] = out
    plan, perr = place_pairs(cs["pairs"], sources)
    errors += perr
    for path, items in plan.items():
        if path in writes:  # ops and pairs on the same file: apply pairs on top of the op result
            tmp = path + ".page_tune.tmp"
            open(tmp, "w", encoding="utf-8").write(writes[path])
            try:
                writes[path] = apply_pairs_to(tmp, [(k, p, pr) for k, p, pr in items])
            finally:
                os.remove(tmp)
        else:
            writes[path] = apply_pairs_to(path, items)
    if cs["tok"] or cs["wrap"]:
        if not style:
            errors.append("token or wrap changes given (%s), but this page declares no tuner tokens or style sink"
                          % ", ".join(sorted(cs["tok"]) + sorted(cs["wrap"])))
        elif style[0] == "json-tokens":
            _, path, key = style
            if cs["wrap"]:
                errors.append("wrap changes have no sink on this page (data tokens only): %s" % ", ".join(sorted(cs["wrap"])))
            base = writes.get(path) or open(path, encoding="utf-8").read()
            cur = dict(json.loads(base).get(key) or {})
            cur.update(cs["tok"])
            tmp = path + ".page_tune.tmp"
            open(tmp, "w", encoding="utf-8").write(base)
            try:
                writes[path], _ = json_write_ops(tmp, [{"op": "add", "path": "/" + key, "value": cur}])
            finally:
                os.remove(tmp)
        else:
            _, path = style
            raw = writes.get(path) or open(path, encoding="utf-8").read()
            m = B_RE.search(raw)
            writes[path] = put_block(raw, style_block(m.group(1) if m else "", cs["tok"], cs["wrap"]), path.endswith((".html", ".tpl")))
    if validate and data_path in writes:
        errors += validate(json.loads(writes[data_path]))
    if errors:
        for x in errors:
            print("✖ " + x)
        print("nothing written")
        raise SystemExit(1)
    for path, out in writes.items():
        open(path, "w", encoding="utf-8").write(out)
        print("applied to %s" % rel(path))
    if not writes:
        print("nothing to apply")
    return list(writes)


def add_args(ap):
    ap.add_argument("--tune", metavar="OUT.html", help="internal copy with the live editor inlined; refuses public/")
    ap.add_argument("--apply", nargs="+", metavar="EXPORT", help="write the tuner's exports back to the source, then rebuild")
    ap.add_argument("--version", type=int, help="with --apply on an Export versions file: that version, not the latest")


def self_test():
    import tempfile
    d = tempfile.mkdtemp()
    j = os.path.join(d, "d.json")
    raw = '{\n  "a": "Hello & welcome",\n  "b": ["x", "Caf\\u00e9 open"],\n  "n": 1024,\n  "t": {"--sp-2": "16px"}\n}\n'
    open(j, "w").write(raw)
    sp = spans(raw)
    assert set(sp) == {"/a", "/b/0", "/b/1", "/n", "/t/--sp-2"}, sp
    out, _ = json_write_ops(j, [{"op": "replace", "path": "/b/1", "value": "Café shut"}])
    assert out == raw.replace("Caf\\u00e9 open", "Caf\\u00e9 shut"), "span splice keeps the file's escapes and layout"
    mv = os.path.join(d, "mv.json")
    json.dump({"s": {"blocks": [{"t": "a"}, {"t": "b"}, {"t": "c"}]}}, open(mv, "w"), indent=1)
    _, d2 = json_write_ops(mv, [{"op": "move", "from": "/s/blocks/2", "path": "/s/blocks/0"}, {"op": "replace", "path": "/s/blocks/0/t", "value": "A"}])
    assert [b["t"] for b in d2["s"]["blocks"]] == ["c", "A", "b"], "replace lands on the pre-move pointer, then the move runs"
    try:
        json_write_ops(mv, [{"op": "move", "from": "/s/blocks/0", "path": "/x/0"}]); assert False, "cross-array move must refuse"
    except SystemExit:
        pass
    plan, err = place_pairs([{"old": "welcome", "new": "hi"}], [("json", j)])
    assert not err and plan[j][0][1] == "/a"
    assert '"Hello & hi"' in apply_pairs_to(j, plan[j]), "json pairs are plain text (no escaping)"
    plan, err = place_pairs([{"old": "Hello", "new": "y"}, {"old": "nope", "new": "z"}], [("json", j)])
    assert len(err) == 1 and "not in any source" in err[0]
    h = os.path.join(d, "p.html")
    open(h, "w").write("<style>:root{--sp-2:16px}</style><p>Tom &amp; Jerry</p><p>two</p><p>two</p>")
    plan, err = place_pairs([{"old": "two", "new": "2"}], [("json", j), ("html", h)])
    assert err and "2 times" in err[0], "a non-unique pair is refused"
    plan, err = place_pairs([{"old": "Tom & Jerry", "new": "T & J"}], [("json", j), ("html", h)])
    assert not err and h in plan, "falls through to the next source"
    assert "<p>T &amp; J</p>" in apply_pairs_to(h, plan[h]), "html pairs escape new text"
    plan, err = place_pairs([{"old": "two", "new": "2"}], [("html", h, r"<p>two</p><p>two</p>")])
    assert err and "not in any source" in err[0], "a masked (generated) region never takes a pair"
    h2 = os.path.join(d, "q.html")
    open(h2, "w").write('<div>\n  <p class="deck">Line one</p>\n  <p>line &amp; two</p>\n  <p>three</p>\n</div>')
    plan, err = place_pairs([{"op": "merge", "parts": ["Line one", "line &amp; two"], "new": "Line one line &amp; two"}], [("json", j), ("html", h2)])
    assert not err and '<p class="deck">Line one line &amp; two</p>' in apply_pairs_to(h2, plan[h2]), ("a join lands in the html source", err)
    plan, err = place_pairs([{"op": "remove", "parts": ["three"]}], [("json", j)])
    assert err and "not in an html source" in err[0], "a join or removal never lands in data"
    raw_ops = os.path.join(d, "e.json")
    json.dump([{"op": "remove", "parts": ["three"]}], open(raw_ops, "w"))
    assert load([raw_ops])["pairs"] and not load([raw_ops])["ops"], "Copy edits with joins are not read as a JSON patch"
    blk = put_block(open(h).read(), style_block("", {"--sp-2": "18px"}, {}), True)
    assert blk.index(B_START) < blk.index("</style>") and ":root{--sp-2:18px;}" in blk
    blk2 = put_block(blk, style_block(B_RE.search(blk).group(1), {"--gap": "4px"}, {":is(p,li,dd)": "pretty"}), True)
    assert blk2.count(B_START) == 1 and "--sp-2:18px" in blk2 and "--gap:4px" in blk2 and "text-wrap:pretty" in blk2, "blocks merge"
    exp = os.path.join(d, "v.json")
    json.dump({"versions": [{"v": 1, "state": {"tok": {"--sp-2": 18}, "wrap": ["", "pretty"], "bp": {}, "text": {"/a": "Hey"}, "dbl": [{"old": "x", "new": "y"}]}}]}, open(exp, "w"))
    cs = load([exp])
    assert cs["tok"] == {"--sp-2": "18px"} and cs["wrap"] == {":is(p,li,dd)": "pretty"}, cs
    assert cs["ops"] == [{"op": "replace", "path": "/a", "value": "Hey"}] and cs["pairs"] == [{"old": "x", "new": "y"}]
    css = os.path.join(d, "c.css")
    open(css, "w").write(":root{--measure:720px;}:is(h1,h2,h3,h4){text-wrap:balance}/* breakpoints, set in source: 1024px to 980px */")
    cs = load([css])
    assert cs["tok"] == {"--measure": "720px"} and cs["wrap"] == {":is(h1,h2,h3,h4)": "balance"}
    try:
        refuse_public(os.path.join(ROOT, "public", "x.html"))
        assert False, "public/ must be refused"
    except SystemExit:
        pass
    print("page_tune self-test: ok")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    print(__doc__)
    sys.exit(2)
