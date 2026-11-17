#!/usr/bin/env python3
"""test_prior_art_recall.py: tool-recall fixtures for scripts/prior_art.py.

WHY: on 2026-11-11 Zach asked for a "master audit ... synthesis ... recapitulation" of all artifacts,
which the /meta-audit skill already does, and prior_art.py did not rank it in its top 5 tool hits.
Zach: "I'm reinventing the wheel because I don't remember the tools for the job we've already
created." Each fixture is a real request that should have surfaced an existing tool. A failing
fixture is a recall miss to fix in the ranker or the tool's own description, never by deleting
the fixture. Add a fixture every time a session reinvents or nearly reinvents a tool.

Run:  python3 scripts/tests/test_prior_art_recall.py        (exit 1 on any miss)
      python3 scripts/tests/test_prior_art_recall.py --json (one line per fixture, for night moves)
Stdlib only; calls prior_art.py --json --no-jtbd so the result does not depend on the graph cache.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOP = 5

# (date added, request in the user's words, substring that must appear in a top-TOP tool ref, note)
FIXTURES = [
    ("2026-11-11", "reading room sync refresh renders", "chronicle_render", "control: passes 2026-11-11"),
    ("2026-11-11", "master audit synthesis of all artifacts modularity", "meta-audit",
     "miss 2026-11-11: /meta-audit absent from top 5 (KINTSUGI G56)"),
]


def tool_refs(query):
    p = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "prior_art.py"), "--json", "--no-jtbd",
                        "--top", str(TOP), query], cwd=ROOT, capture_output=True, text=True)
    try:
        return [h.get("ref", "") for h in json.loads(p.stdout).get("tool", [])][:TOP]
    except ValueError:
        return None


def main():
    as_json = "--json" in sys.argv[1:]
    misses = 0
    for added, query, want, note in FIXTURES:
        refs = tool_refs(query)
        ok = refs is not None and any(want in r for r in refs)
        misses += not ok
        if as_json:
            print(json.dumps({"added": added, "query": query, "want": want, "ok": ok, "top": refs, "note": note}))
        else:
            print(f"{'ok  ' if ok else 'MISS'} want {want!r} for {query!r}" + ("" if ok else f"  top={refs}"))
    if not as_json:
        print(f"prior_art recall: {len(FIXTURES) - misses}/{len(FIXTURES)} fixtures pass")
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
