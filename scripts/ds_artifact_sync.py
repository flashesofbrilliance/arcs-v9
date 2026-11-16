#!/usr/bin/env python3
"""Project the UI kit's specimens into the ARCS OS Design System artifact.

The kit (src/ui-kit/specimens/*.json, rendered to src/ui-kit/recoil-report/NN-*.html by
kit_specimen.py) is where parts get trued up. The design system artifact
(claude.ai/artifact/1DnaMvAFvSspGFTvh1f2wi) is where people browse them. Without this
script the artifact only learns about a kit change when someone remembers to copy it,
which is how it fell behind (Zach, 2026-11-16).

  python3 scripts/ds_artifact_sync.py emit <dir>   write project/components/Kit<Name>/{README.md,preview.html}
                                                   and project/ui_kits/arcs-kit/{_tokens.css,_player.js} under <dir>
  python3 scripts/ds_artifact_sync.py --check      list specimens changed since the last recorded publish
  python3 scripts/ds_artifact_sync.py record <artifact-version>
                                                   after publishing, store each specimen's hash so --check is quiet

The publish itself is an Artifact tool call (root=<dir>, files=project/...), made by a
session; this script never reaches the network. Each card is generated: edit the spec,
re-run, republish. Stdlib only.
"""
import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(ROOT, "src", "ui-kit", "specimens")
KIT = os.path.join(ROOT, "src", "ui-kit", "recoil-report")
STAMP = os.path.join(ROOT, "runtime", "specs", "ds-artifact-sync.json")
ARTIFACT = "https://claude.ai/artifact/1DnaMvAFvSspGFTvh1f2wi"
HEIGHT = {"Atom": 220, "Molecule": 460, "Organism": 680}
BIG = {"week-plan": 900, "strata-explorer": 820, "braided-lanes": 820}


def e(s):
    return html.escape(str(s), quote=True)


def md(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def pascal(name):
    return "Kit" + "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", name) if w)


def specs():
    return sorted(os.path.join(SPECS, f) for f in os.listdir(SPECS) if f.endswith(".json"))


def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def readme(s, src):
    lines = [f"`{pascal(s['name'])}`: {s['job']}", "",
             f"Kit part {s['number']} ({s['layer']}), source `src/ui-kit/recoil-report/{s['number']}-{s['slug']}.html`, "
             f"generated from `{src}` by `scripts/ds_artifact_sync.py`. Edit the spec in the repo, not this card.", "",
             "## Anatomy", "", "| Part | Role | Tokens |", "|---|---|---|"]
    lines += [f"| {md(a['part'])} | {md(a['role'])} | {md(a['token'])} |" for a in s["anatomy"]]
    lines += ["", "## Use it when", ""] + [f"- {x}" for x in s["use_when"]]
    lines += ["", "## Do not use it when", ""] + [f"- {x}" for x in s["avoid_when"]]
    lines += ["", "## Provide", "", "| Field | Type | Required | Note |", "|---|---|---|---|"]
    lines += [f"| `{md(d['field'])}` | {md(d['type'])} | {'yes' if d.get('required') else 'no'} | {md(d['note'])} |" for d in s["data"]]
    lines += ["", "## Access", ""] + [f"- {x}" for x in s["access"]]
    lines += ["", "## States", ""] + [f"- **{x['name']}**: {x['note']}" for x in s["states"]]
    return "\n".join(lines) + "\n"


def preview(s):
    h = BIG.get(s["slug"], HEIGHT.get(s["layer"], 460))
    job = s["job"] if len(s["job"]) <= 90 else s["job"][:87].rsplit(" ", 1)[0] + "..."
    states = "".join(f'<figure class="ds-st"><figcaption>{e(x["name"])}</figcaption><div data-state="{i}"></div></figure>'
                     for i, x in enumerate(s["states"]))
    return f"""<!-- @dsCard group="UI kit: {e(s['layer'])}s" height={h} subtitle="{e(s['layer'])} {e(s['number'])}: {e(job)}" -->
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="../../ui_kits/arcs-kit/_tokens.css">
<style>
body {{ margin: 0; padding: 20px; background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); }}
.ds-st {{ margin: 24px 0 0; }}
.ds-st figcaption {{ font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 8px; }}
{s.get('css', '')}
</style></head><body>
<div data-stage></div>{states}
<script src="../../ui_kits/arcs-kit/_player.js"></script>
<script>
var STATES = {json.dumps([x.get("args") for x in s["states"]])};
{s['demo']}
</script></body></html>
"""


def emit(out):
    base = os.path.join(out, "project")
    os.makedirs(os.path.join(base, "ui_kits", "arcs-kit"), exist_ok=True)
    for f in ("_tokens.css", "_player.js"):
        open(os.path.join(base, "ui_kits", "arcs-kit", f), "w", encoding="utf-8").write(open(os.path.join(KIT, f), encoding="utf-8").read())
    names = []
    for p in specs():
        s = json.load(open(p, encoding="utf-8"))
        d = os.path.join(base, "components", pascal(s["name"]))
        os.makedirs(d, exist_ok=True)
        rel = os.path.relpath(p, ROOT)
        open(os.path.join(d, "README.md"), "w", encoding="utf-8").write(readme(s, rel))
        open(os.path.join(d, "preview.html"), "w", encoding="utf-8").write(preview(s))
        names.append(pascal(s["name"]))
    print(f"emitted {len(names)} kit cards and the kit stylesheet under {base}")
    return names


def current():
    return {os.path.relpath(p, ROOT): digest(p) for p in specs() + [os.path.join(KIT, "_tokens.css"), os.path.join(KIT, "_player.js")]}


def check():
    old = json.load(open(STAMP)).get("files", {}) if os.path.exists(STAMP) else {}
    now = current()
    stale = sorted(k for k in now if old.get(k) != now[k])
    gone = sorted(k for k in old if k not in now)
    if not stale and not gone:
        print(f"✓ ds-artifact-sync: the design system artifact carries every kit specimen as of its last publish")
        return 0
    print(f"✖ ds-artifact-sync: {len(stale)} kit file(s) changed since the design system artifact was last synced ({ARTIFACT}):")
    for k in stale + gone:
        print(f"    {k}")
    print("  fix: python3 scripts/ds_artifact_sync.py emit <dir>; publish <dir>/project/... to the artifact; then record <version>")
    return 1


def record(version):
    json.dump({"artifact": ARTIFACT, "version": version, "files": current()}, open(STAMP, "w"), indent=1, sort_keys=True)
    open(STAMP, "a").write("\n")
    print(f"recorded {len(current())} kit files against artifact version {version}")


def main(argv):
    if argv[:1] == ["emit"] and len(argv) == 2:
        emit(argv[1]); return 0
    if argv[:1] == ["record"] and len(argv) == 2:
        record(argv[1]); return 0
    if argv == ["--check"]:
        return check()
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
