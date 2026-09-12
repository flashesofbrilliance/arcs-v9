#!/usr/bin/env python3
"""
recoil_report.py -- self-contained CLI for the ARCS recoil-report artifact pipeline.

Stdlib only (json, argparse, html, math, os, re, sys). No third-party deps.
Bundled resources live beside this file: schema/report.schema.json, sample/sample-report.json.

Subcommands
  new       Scaffold a schema-valid report JSON from the bundled sample.
  validate  Check a report JSON against the bundled schema (minimal draft-07 subset).
  segments  Print the spec cadence max(3, round(sqrt(duration_minutes))).
  render    Render a report JSON to a standalone HTML page (tolerates both shapes).

Passthrough
  --set dotted.key=value   Override any key at generation/render time (applies to new & render).
                           Values that parse as int/float/bool/JSON are coerced; else kept as string.

Exit codes
  0 ok · 1 validation failed · 2 usage/IO error
"""
import argparse, json, html, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "schema", "report.schema.json")
SAMPLE_PATH = os.path.join(HERE, "sample", "sample-report.json")
# Default landing zone for generated reports, resolved relative to repo root (../../).
GENERATED_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "runtime", "recoil", "generated"))


# --------------------------------------------------------------------------- io
def load_json(path):
    with open(path) as f:
        return json.load(f)


def coerce(val):
    """Coerce a --set string to int/float/bool/JSON when it parses, else leave as string."""
    low = val.strip().lower()
    if low in ("true", "false"):
        return low == "true"
    try:
        return json.loads(val)
    except (ValueError, TypeError):
        return val


def apply_overrides(data, sets):
    """--set a.b.c=value -> data['a']['b']['c'] = coerce(value). Creates intermediate dicts."""
    for kv in sets or []:
        if "=" not in kv:
            raise SystemExit(f"recoil-report: bad --set '{kv}', expected dotted.key=value")
        path, raw = kv.split("=", 1)
        node, keys = data, path.split(".")
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = coerce(raw)
    return data


# ----------------------------------------------------------------- validator
# Minimal JSON-Schema (draft-07 subset): type, required, properties, items, enum.
# Enough to catch a dropped section or a mistyped key; not a full validator.
_TYPES = {
    "object": dict, "array": list, "string": str,
    "number": (int, float), "integer": int, "boolean": bool, "null": type(None),
}


def _type_ok(value, t):
    if isinstance(t, list):
        return any(_type_ok(value, one) for one in t)
    py = _TYPES.get(t)
    if py is None:
        return True
    if t == "number" and isinstance(value, bool):
        return False  # bool is a subclass of int; don't let True count as a number
    return isinstance(value, py)


def validate(node, schema, path="$", errors=None):
    if errors is None:
        errors = []
    t = schema.get("type")
    if t is not None and not _type_ok(node, t):
        errors.append(f"{path}: expected type {t}, got {type(node).__name__}")
        return errors  # type is wrong; deeper checks would be noise
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: {node!r} not in enum {schema['enum']}")
    if isinstance(node, dict):
        for req in schema.get("required", []):
            if req not in node:
                errors.append(f"{path}: missing required key '{req}'")
        props = schema.get("properties", {})
        for key, subschema in props.items():
            if key in node:
                validate(node[key], subschema, f"{path}.{key}", errors)
    if isinstance(node, list) and "items" in schema:
        for i, item in enumerate(node):
            validate(item, schema["items"], f"{path}[{i}]", errors)
    return errors


# -------------------------------------------------------------------- render
_TOK = {  # ARCS design tokens (inline; the package carries its own look)
    "bg": "#020408", "surface": "#0d1117", "border": "#1e293b", "text": "#e2e8f0",
    "muted": "#94a3b8", "dimmed": "#64748b", "cyan": "#00F0FF", "green": "#00FF9D",
    "gold": "#FFD700", "red": "#FF4D6D",
}
_SEV = {"warning": _TOK["red"], "caution": _TOK["gold"], "info": _TOK["cyan"],
        "success": _TOK["green"], "high": _TOK["red"], "med": _TOK["gold"], "low": _TOK["dimmed"]}
E = lambda s: html.escape(str(s)) if s is not None else ""


def _cover_badges(cover):
    if cover.get("badges"):
        return cover["badges"]
    out = []
    for k in ("yGate", "conviction", "stability", "renderState"):
        if cover.get(k):
            out.append(cover[k])
    if cover.get("nci") is not None:
        out.append(f"NCI {cover['nci']}")
    return out


def _p(body):
    return f'<p style="font-size:14.5px;color:{_TOK["text"]};margin:0 0 10px;">{E(body)}</p>'


def _card(title, inner):
    return (f'<div style="background:{_TOK["surface"]};border:1px solid {_TOK["border"]};'
            f'border-radius:12px;padding:20px 22px;margin:12px 0;">'
            f'<h2 style="font-size:12px;font-family:ui-monospace,monospace;font-weight:700;'
            f'letter-spacing:0.1em;text-transform:uppercase;color:{_TOK["cyan"]};margin:0 0 12px;">'
            f'{E(title)}</h2>{inner}</div>')


def render_html(d):
    cover = d.get("cover", {})
    headline = cover.get("headline") or cover.get("title") or d.get("reportId", "")
    subline = cover.get("subline") or cover.get("subtitle") or ""
    badges = "".join(
        f'<span style="font-family:ui-monospace,monospace;font-size:10px;font-weight:700;'
        f'letter-spacing:0.12em;padding:4px 9px;border:1px solid {_TOK["border"]};border-radius:6px;'
        f'color:{_TOK["muted"]};margin-right:6px;">{E(b)}</span>' for b in _cover_badges(cover))

    q = d.get("loadBearingQuote", {})
    quote = _card("Load-Bearing Quote",
                  f'<p style="font-size:16px;line-height:1.6;color:{_TOK["text"]};margin:0 0 10px;">'
                  f'&ldquo;{E(q.get("text"))}&rdquo;</p>'
                  f'<p style="font-family:ui-monospace,monospace;font-size:10px;letter-spacing:0.1em;'
                  f'color:{_TOK["dimmed"]};margin:0 0 8px;">{E(q.get("attribution"))}</p>'
                  + (_p(q.get("significance")) if q.get("significance") else "")) if q else ""

    # call walk
    walk_rows = ""
    for s in d.get("callWalk", []):
        head = " · ".join(x for x in [s.get("label"), s.get("time"), s.get("direction")] if x)
        walk_rows += (f'<div style="margin:0 0 14px;">'
                      f'<div style="font-family:ui-monospace,monospace;font-size:10px;letter-spacing:0.1em;'
                      f'color:{_TOK["dimmed"]};margin:0 0 4px;">{E(head)}</div>'
                      + _p(s.get("summary") or s.get("body") or "")
                      + (f'<div style="font-size:12px;color:{_TOK["muted"]};">{E(s.get("divergenceFlag"))}</div>'
                         if s.get("divergenceFlag") else "") + "</div>")
    walk = _card("Call Walk", walk_rows) if walk_rows else ""

    # signal threads
    sig_rows = ""
    for s in d.get("signalThreads", []):
        sig_rows += (f'<div style="margin:0 0 12px;"><div style="font-weight:700;color:{_TOK["text"]};'
                     f'margin:0 0 4px;">{E(s.get("label") or s.get("title"))}'
                     + (f' <span style="font-family:ui-monospace,monospace;font-size:10px;'
                        f'color:{_TOK["dimmed"]};">[{E(s.get("strength"))}]</span>' if s.get("strength") else "")
                     + "</div>" + _p(s.get("description") or s.get("body") or "") + "</div>")
    signals = _card("Signal Threads", sig_rows) if sig_rows else ""

    # scenarios (array or best/base/worst object)
    sc = d.get("scenarios")
    sc_rows = ""
    if isinstance(sc, dict):
        for k in ("best", "base", "worst"):
            if k in sc:
                v = sc[k]
                sc_rows += (f'<div style="margin:0 0 12px;"><div style="font-family:ui-monospace,monospace;'
                            f'font-size:10px;letter-spacing:0.1em;color:{_TOK["dimmed"]};">{k.upper()}</div>'
                            f'<div style="font-weight:700;color:{_TOK["text"]};margin:2px 0 4px;">{E(v.get("title"))}</div>'
                            + _p(v.get("body")) + (_p(v.get("note")) if v.get("note") else "") + "</div>")
    elif isinstance(sc, list):
        for v in sc:
            prob = f' — {v["probability"]}%' if v.get("probability") is not None else ""
            sc_rows += (f'<div style="margin:0 0 12px;"><div style="font-weight:700;color:{_TOK["text"]};'
                        f'margin:0 0 4px;">{E(v.get("label"))}{E(prob)}</div>'
                        + _p(v.get("description")) + (_p("Watch: " + v["watch"]) if v.get("watch") else "") + "</div>")
    scenarios = _card("Scenarios", sc_rows) if sc_rows else ""

    # risk flags
    rf_rows = ""
    for r in d.get("riskFlags", []):
        col = _SEV.get(str(r.get("severity") or r.get("variant") or "").lower(), _TOK["muted"])
        rf_rows += (f'<div style="margin:0 0 12px;border-left:2px solid {col};padding-left:12px;">'
                    f'<div style="font-weight:700;color:{_TOK["text"]};margin:0 0 4px;">'
                    + (f'<span style="color:{col};font-family:ui-monospace,monospace;font-size:10px;'
                       f'margin-right:6px;">{E((r.get("severity") or r.get("variant") or "").upper())}</span>'
                       if (r.get("severity") or r.get("variant")) else "")
                    + f'{E(r.get("label"))}</div>' + _p(r.get("description") or r.get("body") or "")
                    + (_p("→ " + r["action"]) if r.get("action") else "") + "</div>")
    risks = _card("Risk Flags", rf_rows) if rf_rows else ""

    # protocol (object passes/immediateActions or array of steps)
    pr = d.get("protocol")
    pr_inner = ""
    if isinstance(pr, dict):
        for p in pr.get("passes", []):
            pr_inner += (f'<div style="margin:0 0 10px;"><div style="font-weight:700;color:{_TOK["text"]};">'
                         f'{E(p.get("name"))} <span style="color:{_TOK["dimmed"]};font-size:12px;">'
                         f'{E(p.get("direction"))}</span></div>' + _p(p.get("keyFinding")) + "</div>")
        if pr.get("immediateActions"):
            items = "".join(f'<li style="margin:0 0 6px;color:{_TOK["text"]};font-size:14px;">{E(a)}</li>'
                            for a in pr["immediateActions"])
            pr_inner += f'<div style="font-family:ui-monospace,monospace;font-size:10px;letter-spacing:0.1em;color:{_TOK["dimmed"]};margin:8px 0 4px;">IMMEDIATE ACTIONS</div><ul style="margin:0;padding-left:18px;">{items}</ul>'
    elif isinstance(pr, list):
        for p in pr:
            pr_inner += (f'<div style="margin:0 0 10px;"><div style="font-weight:700;color:{_TOK["text"]};">'
                         f'{E(p.get("title") or p.get("label"))}</div>' + _p(p.get("body")) + "</div>")
    protocol = _card("Protocol", pr_inner) if pr_inner else ""

    notice = (f'<div style="font-family:ui-monospace,monospace;font-size:10px;letter-spacing:0.15em;'
              f'color:{_TOK["red"]};margin:0 0 16px;">{E(d.get("notice"))}</div>') if d.get("notice") else ""

    body = (f'{notice}'
            f'<div style="margin:0 0 8px;">{badges}</div>'
            f'<h1 style="font-size:26px;line-height:1.25;color:{_TOK["text"]};margin:8px 0 8px;font-weight:600;">{E(headline)}</h1>'
            f'<p style="font-size:14px;color:{_TOK["muted"]};margin:0 0 20px;">{E(subline)}</p>'
            f'{quote}{walk}{signals}{scenarios}{risks}{protocol}')

    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex,nofollow">'
            f'<title>Recoil Report — {E(d.get("reportId",""))}</title></head>'
            f'<body style="background:{_TOK["bg"]};color:{_TOK["text"]};margin:0;'
            f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',system-ui,sans-serif;'
            f'line-height:1.62;padding:48px 24px 96px;">'
            f'<div style="max-width:760px;margin:0 auto;">{body}</div></body></html>')


# --------------------------------------------------------------------- commands
def cmd_segments(args):
    m = args.minutes
    if m <= 0:
        raise SystemExit("recoil-report: minutes must be > 0")
    print(max(3, round(math.sqrt(m))))


def cmd_validate(args):
    schema = load_json(SCHEMA_PATH)
    data = load_json(args.file)
    errs = validate(data, schema)
    if errs:
        print(f"INVALID — {len(errs)} error(s) in {args.file}:", file=sys.stderr)
        for e in errs:
            print(f"  • {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK — {args.file} conforms to {os.path.relpath(SCHEMA_PATH, os.getcwd())}")


def cmd_new(args):
    data = load_json(SAMPLE_PATH)
    data["reportId"] = args.slug
    apply_overrides(data, args.set)
    errs = validate(data, load_json(SCHEMA_PATH))
    if errs:
        print("refusing to scaffold an invalid report (check your --set overrides):", file=sys.stderr)
        for e in errs:
            print(f"  • {e}", file=sys.stderr)
        sys.exit(1)
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if args.out == "-":
        print(text)
        return
    out = args.out or os.path.join(GENERATED_DIR, f"{args.slug}.json")
    if os.path.exists(out) and not args.force:
        raise SystemExit(f"recoil-report: {out} exists (pass --force to overwrite)")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(text + "\n")
    print(out)


def cmd_render(args):
    data = load_json(args.file)
    apply_overrides(data, args.set)
    if not args.no_validate:
        errs = validate(data, load_json(SCHEMA_PATH))
        if errs:
            print(f"refusing to render an invalid report ({len(errs)} error(s); pass --no-validate to force):",
                  file=sys.stderr)
            for e in errs:
                print(f"  • {e}", file=sys.stderr)
            sys.exit(1)
    out_html = render_html(data)
    if args.out == "-" or not args.out:
        sys.stdout.write(out_html)
    else:
        with open(args.out, "w") as f:
            f.write(out_html)
        print(args.out)


def build_parser():
    p = argparse.ArgumentParser(
        prog="recoil-report",
        description="Self-contained CLI for the ARCS recoil-report artifact pipeline (stdlib only).")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("segments", help="print max(3, round(sqrt(minutes))) — the spec cadence")
    s.add_argument("minutes", type=float)
    s.set_defaults(func=cmd_segments)

    v = sub.add_parser("validate", help="validate a report JSON against the bundled schema")
    v.add_argument("file")
    v.set_defaults(func=cmd_validate)

    n = sub.add_parser("new", help="scaffold a schema-valid report JSON from the bundled sample")
    n.add_argument("slug", help="reportId / filename slug, e.g. 2026-08-01-smith")
    n.add_argument("--out", help="output path, or '-' for stdout (default: runtime/recoil/generated/<slug>.json)")
    n.add_argument("--set", action="append", metavar="dotted.key=value", help="override any key (repeatable)")
    n.add_argument("--force", action="store_true", help="overwrite if the target exists")
    n.set_defaults(func=cmd_new)

    r = sub.add_parser("render", help="render a report JSON to standalone HTML")
    r.add_argument("file")
    r.add_argument("--out", help="output path, or '-'/omit for stdout")
    r.add_argument("--set", action="append", metavar="dotted.key=value", help="override any key (repeatable)")
    r.add_argument("--no-validate", action="store_true", help="skip schema validation before rendering")
    r.set_defaults(func=cmd_render)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except FileNotFoundError as e:
        raise SystemExit(f"recoil-report: {e}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"recoil-report: invalid JSON — {e}")


if __name__ == "__main__":
    main()
