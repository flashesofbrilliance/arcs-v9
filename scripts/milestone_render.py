#!/usr/bin/env python3
"""milestone_render — inject a data JSON into the fixed milestone template.

The layout is pre-verified and frozen in _ARTIFACTS/milestones/_template.html; only
the DATA changes per run. This keeps headless (cron) renders from ever reintroducing
a layout bug — there is no layout to break, only data to fill.

  milestone_render.py <data.json> <out.html>

The data JSON must match window.MILESTONE_DATA (schema documented in the template head).
Stdlib only.
"""
import json, sys, os

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
TEMPLATE = os.path.join(ROOT, "_ARTIFACTS/milestones/_template.html")
MARKER = "__MILESTONE_DATA__"


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: milestone_render.py <data.json> <out.html>\n")
        sys.exit(2)
    data = json.load(open(sys.argv[1]))            # validates JSON
    tmpl = open(TEMPLATE).read()
    if MARKER not in tmpl:
        sys.stderr.write(f"template missing {MARKER} marker\n")
        sys.exit(1)
    # inject as a JS literal (json.dumps is valid JS). Replace ALL occurrences so a
    # stray marker in a comment can't shadow the real one in the script.
    html = tmpl.replace(MARKER, json.dumps(data, ensure_ascii=False))
    with open(sys.argv[2], "w") as f:
        f.write(html)
    print(f"rendered {sys.argv[2]} ({len(data.get('clusters',[]))} clusters, {len(data.get('trace',[]))} trace points)")


if __name__ == "__main__":
    main()
