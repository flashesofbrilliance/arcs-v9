#!/usr/bin/env python3
"""option_board.py: render a design review as about three rendered options per block.

Why (Zach, 2026-11-13): choosing between real renders beats prose or a single take. Each block
of a page gets options A, B, C built from kit tokens and the page's real copy, tagged with its
atomic layer (atom, molecule, organism, template, page). The reviewer clicks one per block,
moves the dials, and the picks come back as one line, for example
"Header C, Stats B, Week One C. Others unchanged. Glass strength 1x."
Memory: visual-work-three-rendered-options-per-block.

Spec (JSON):
  id, title, subject, lede                      strings
  dials: [{id, label, min, max, step, value, unit}]   optional; each sets --k-<id> on <html>
  blocks: [{id, label, layer, note?, variants: [{key, name, why?, html, css?}]}]
     2 to 4 variants per block (3 is the norm). In css, ":scope" means this variant's stage,
     so rules never leak into another option. Variant CSS may use var(--k-<dial id>).

Kit template: src/ui-kit/option-board/ (page.tpl, board.css, board.js). Tokens are
src/ui-kit/recoil-report/_tokens.css inlined verbatim (token_source_gate.py sentinel kept).

Usage:
  python3 scripts/option_board.py SPEC.json -o OUT.html
  python3 scripts/option_board.py SPEC.json --fragment -o OUT.html   body-only, for show_widget
  python3 scripts/option_board.py --self-test
"""
import argparse, html, json, os, re, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "src/ui-kit/option-board")
TOKENS = os.path.join(ROOT, "src/ui-kit/recoil-report/_tokens.css")
LAYERS = {"atom", "molecule", "organism", "template", "page"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def validate(spec):
    errs = []
    for k in ("id", "title", "subject", "lede", "blocks"):
        if not spec.get(k):
            errs.append("missing %s" % k)
    seen = set()
    for i, b in enumerate(spec.get("blocks") or []):
        where = "blocks[%d]" % i
        if not ID_RE.match(b.get("id", "")):
            errs.append("%s: id must be kebab-case" % where)
        if b.get("id") in seen:
            errs.append("%s: duplicate id %s" % (where, b.get("id")))
        seen.add(b.get("id"))
        if not b.get("label"):
            errs.append("%s: missing label" % where)
        if b.get("layer") not in LAYERS:
            errs.append("%s: layer must be one of %s" % (where, ", ".join(sorted(LAYERS))))
        vs = b.get("variants") or []
        if not 2 <= len(vs) <= 4:
            errs.append("%s: needs 2 to 4 variants, has %d" % (where, len(vs)))
        keys = [v.get("key") for v in vs]
        if len(set(keys)) != len(keys) or not all(k and re.match(r"^[A-Z]$", k) for k in keys):
            errs.append("%s: variant keys must be distinct single capitals" % where)
        for v in vs:
            if not v.get("name") or not v.get("html"):
                errs.append("%s.%s: needs name and html" % (where, v.get("key")))
    for d in spec.get("dials") or []:
        if not ID_RE.match(d.get("id", "")) or not d.get("label"):
            errs.append("dial needs a kebab-case id and a label")
            continue
        try:
            lo, hi, val = float(d["min"]), float(d["max"]), float(d["value"])
            if not lo <= val <= hi:
                errs.append("dial %s: value outside min..max" % d["id"])
        except (KeyError, ValueError, TypeError):
            errs.append("dial %s: min, max, value must be numbers" % d.get("id"))
    if "\u2014" in json.dumps(spec, ensure_ascii=False):
        errs.append("spec contains an em-dash")
    return errs


def scope(css, sel):
    return css.replace(":scope", sel)


def build(spec, fragment=False):
    errs = validate(spec)
    if errs:
        raise SystemExit("option_board: invalid spec:\n  " + "\n  ".join(errs))
    e = html.escape
    vcss, blocks = [], []
    for b in spec["blocks"]:
        opts = []
        for v in b["variants"]:
            sel = '.ob-stage[data-v="%s-%s"]' % (b["id"], v["key"])
            if v.get("css"):
                vcss.append("/* %s %s */\n%s" % (b["id"], v["key"], scope(v["css"], sel)))
            why = '<p class="ob-opt-why">%s</p>' % e(v["why"]) if v.get("why") else ""
            opts.append(
                '<button type="button" class="ob-opt" aria-pressed="false" data-block="%s" data-key="%s">'
                '<span class="ob-opt-cap"><span><span class="ob-opt-key">%s</span> <span class="ob-opt-name">%s</span></span>'
                '<span class="ob-opt-pick">Pick</span></span>'
                '<span class="ob-stage" data-v="%s-%s">%s</span>%s</button>'
                % (e(b["id"]), e(v["key"]), e(v["key"]), e(v["name"]), e(b["id"]), e(v["key"]), v["html"], why))
        note = '<p class="ob-block-note">%s</p>' % e(b["note"]) if b.get("note") else ""
        blocks.append(
            '<section class="ob-block" aria-labelledby="h-%s"><div class="ob-block-head"><h2 id="h-%s">%s</h2>'
            '<span class="ob-layer">%s</span></div>%s<div class="ob-options">%s</div></section>'
            % (e(b["id"]), e(b["id"]), e(b["label"]), e(b["layer"]), note, "".join(opts)))
    dials = ""
    if spec.get("dials"):
        rows = []
        for d in spec["dials"]:
            rows.append(
                '<div class="ob-dial"><label for="dial-%s">%s</label>'
                '<input type="range" id="dial-%s" min="%s" max="%s" step="%s" value="%s">'
                '<output id="dial-%s-out" for="dial-%s"></output></div>'
                % (e(d["id"]), e(d["label"]), e(d["id"]), d["min"], d["max"], d.get("step", 0.1), d["value"], e(d["id"]), e(d["id"])))
        dials = '<div class="ob-dials" role="group" aria-label="Dials">%s</div>' % "".join(rows)
        vcss.insert(0, ":root { %s }" % " ".join("--k-%s: %s;" % (d["id"], d["value"]) for d in spec["dials"]))
    tokens = read(TOKENS)
    assert tokens.startswith("/* ARCS Recoil Report"), "token sentinel missing"
    spec_json = json.dumps({"id": spec["id"], "dials": spec.get("dials", []),
                            "blocks": [{"id": b["id"], "label": b["label"]} for b in spec["blocks"]]})
    spec_json = spec_json.replace("</", "<\\/")
    page = read(os.path.join(TPL, "page.tpl"))
    for k, v in (("TOKENS", tokens), ("BOARD_CSS", read(os.path.join(TPL, "board.css"))),
                 ("VARIANT_CSS", "\n".join(vcss)), ("DIALS", dials), ("BLOCKS", "\n".join(blocks)),
                 ("SPEC_JSON", spec_json), ("BOARD_JS", read(os.path.join(TPL, "board.js"))),
                 ("TITLE", e(spec["title"])), ("SUBJECT", e(spec["subject"])), ("LEDE", e(spec["lede"]))):
        page = page.replace("{{%s}}" % k, v)
    if fragment:
        css = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
        body = re.search(r"<body>(.*)</body>", page, re.S).group(1)
        page = "<style>%s\nbody{background:transparent}</style>\n%s" % (css, body)
    return page


def self_test():
    ok = True
    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond
    v = lambda k: {"key": k, "name": "Opt " + k, "html": "<p>x</p>", "css": ":scope p { color: var(--cyan); }"}
    good = {"id": "t", "title": "T", "subject": "S", "lede": "L",
            "dials": [{"id": "glass", "label": "Glass strength", "min": 0, "max": 2, "step": 0.25, "value": 1, "unit": "x"}],
            "blocks": [{"id": "header", "label": "Header", "layer": "organism", "variants": [v("A"), v("B"), v("C")]}]}
    check("good spec validates", validate(good) == [])
    out = build(good)
    check("tokens inlined with sentinel", "/* ARCS Recoil Report" in out)
    check("variant css scoped to its stage", '.ob-stage[data-v="header-B"] p' in out and ":scope" not in out)
    check("three pick buttons", out.count('class="ob-opt"') == 3)
    check("dial default written to :root", "--k-glass: 1;" in out)
    check("send and copy controls present", 'id="ob-send"' in out and 'id="ob-copy"' in out)
    check("no template holes left", "{{" not in out)
    check("no em-dash outside the verbatim token sentinel", "\u2014" not in out.replace(read(TOKENS), ""))
    frag = build(good, fragment=True)
    check("fragment has no doctype or body tag", "<!DOCTYPE" not in frag and "<body" not in frag)
    bad = json.loads(json.dumps(good)); bad["blocks"][0]["variants"] = [v("A")]
    check("one variant is refused", any("2 to 4" in x for x in validate(bad)))
    bad = json.loads(json.dumps(good)); bad["blocks"][0]["layer"] = "widget"
    check("unknown atomic layer is refused", any("layer" in x for x in validate(bad)))
    bad = json.loads(json.dumps(good)); bad["blocks"][0]["variants"][1]["key"] = "A"
    check("duplicate keys are refused", any("distinct" in x for x in validate(bad)))
    bad = json.loads(json.dumps(good)); bad["dials"][0]["value"] = 9
    check("dial value out of range is refused", any("outside" in x for x in validate(bad)))
    bad = json.loads(json.dumps(good)); bad["lede"] = "a \u2014 b"
    check("em-dash in spec is refused", any("em-dash" in x for x in validate(bad)))
    gravity = os.path.join(ROOT, "_ARTIFACTS/option-board/gravity-glass.json")
    if os.path.exists(gravity):
        g = json.load(open(gravity, encoding="utf-8"))
        check("gravity example validates", validate(g) == [])
        gout = build(g)
        check("gravity example renders 5 blocks", gout.count('class="ob-block"') == 5)
        check("gravity example has 15 options", gout.count('class="ob-opt"') == 15)
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(gout)
        built = os.path.join(ROOT, "_ARTIFACTS/option-board/gravity-glass.html")
        if os.path.exists(built):
            check("committed gravity board matches the spec (rebuild if not)", read(built) == gout)
        os.unlink(f.name)
    print("self-test: " + ("ok" if ok else "FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--fragment", action="store_true", help="body-only output for an inline widget")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.spec:
        ap.error("SPEC is required")
    page = build(json.load(open(a.spec, encoding="utf-8")), fragment=a.fragment)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(page)
        print("wrote %s (%d bytes)" % (a.out, len(page)))
    else:
        sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    sys.exit(main())
