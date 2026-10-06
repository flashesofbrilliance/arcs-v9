#!/usr/bin/env python3
"""model_drift_check: flag when a newer Claude model exists for a role in src/lib/claude-models.ts.

Never switches anything. A model change alters product output, so it is Zach's call after an eval.

    python3 scripts/model_drift_check.py                 # live: GET /v1/models (needs ANTHROPIC_API_KEY)
    python3 scripts/model_drift_check.py --known a,b,c   # offline: compare against a given id list
    python3 scripts/model_drift_check.py --self-test
Prints one DRIFT line per role with a newer same-family model; exit 0 always (advisory),
exit 2 on bad args. No key and no --known -> prints a notice and exits 0.
"""
import json, os, re, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arcs_models import roles  # noqa: E402

VER = re.compile(r"claude-(haiku|sonnet|opus|fable)-(\d+)(?:-(\d+))?(?:-\d{8})?$")


def parse(mid):
    m = VER.match(mid)
    if not m:
        return None
    major, minor = int(m.group(2)), int(m.group(3) or 0)
    if minor > 99:  # a date suffix glued on, e.g. claude-sonnet-4-20250514
        minor = 0
    return m.group(1), (major, minor)


def live_ids():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    req = urllib.request.Request("https://api.anthropic.com/v1/models?limit=100",
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return [m["id"] for m in json.load(r)["data"]]


def drift(role_map, known):
    newest = {}
    for mid in known:
        p = parse(mid)
        if p and (p[0] not in newest or p[1] > newest[p[0]][1]):
            newest[p[0]] = (mid, p[1])
    out = []
    for role, mid in role_map.items():
        p = parse(mid)
        if p and p[0] in newest and newest[p[0]][1] > p[1]:
            out.append((role, mid, newest[p[0]][0]))
    return out


def self_test():
    rm = {"fast": "claude-haiku-4-5", "deep": "claude-sonnet-4-6"}
    got = drift(rm, ["claude-haiku-4-5", "claude-sonnet-5-5", "claude-sonnet-4-20250514", "claude-opus-5-5"])
    ok = got == [("deep", "claude-sonnet-4-6", "claude-sonnet-5-5")] and drift(rm, ["claude-sonnet-4-6"]) == []
    print(f"model_drift_check self-test: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    known = None
    if argv[:1] == ["--known"] and len(argv) == 2:
        known = [s.strip() for s in argv[1].split(",") if s.strip()]
    elif argv:
        print("usage: model_drift_check.py [--known id,id,...] | --self-test", file=sys.stderr)
        return 2
    if known is None:
        try:
            known = live_ids()
        except Exception as e:  # network or auth: advisory, never block
            print(f"model-drift: could not list models ({e.__class__.__name__}); skipped")
            return 0
        if known is None:
            print("model-drift: no ANTHROPIC_API_KEY; skipped (pass --known to check offline)")
            return 0
    found = drift(roles(), known)
    for role, cur, new in found:
        print(f"  DRIFT [model:{role}] runs {cur}; {new} is available. Switch is Zach's call after an eval (src/lib/claude-models.ts).")
    print(f"model-drift: {'DRIFT' if found else 'OK'} · {len(found)} role(s) behind")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
