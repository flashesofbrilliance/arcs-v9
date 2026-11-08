#!/usr/bin/env python3
"""myally_hub_sync.py: inline the engine's Step 1 tree into the myally.arcs.care hub.

The "Light audit and code review" tab in public/myally-hub.html draws its rows from
_ARTIFACTS/engagements/myally-ld/out/step1_tree.json (rendered from engagement.json by
scripts/engagement_render.py). This copies that JSON between the /*S1:BEGIN*/ and /*S1:END*/
sentinels, so the tab, the agreement and Exhibit A all cite one record.

  python3 scripts/myally_hub_sync.py          # write
  python3 scripts/myally_hub_sync.py --check  # read-only; exit 1 when the hub is stale

Stdlib only. Writes only public/myally-hub.html.
"""
import json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "_ARTIFACTS", "engagements", "myally-ld", "out", "step1_tree.json")
HUB = os.path.join(ROOT, "public", "myally-hub.html")
PAT = re.compile(r"/\*S1:BEGIN\*/.*?/\*S1:END\*/", re.S)


def payload() -> str:
    data = json.load(open(SRC, encoding="utf-8"))
    # Compact, and safe inside a <script>: no "</" can close the tag.
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("</", "<\\/")


def synced(hub: str) -> str:
    if len(PAT.findall(hub)) != 1:
        sys.exit("myally_hub_sync: expected exactly one /*S1:BEGIN*/.../*S1:END*/ block in the hub")
    return PAT.sub(lambda _: "/*S1:BEGIN*/" + payload() + "/*S1:END*/", hub)


def main() -> int:
    hub = open(HUB, encoding="utf-8").read()
    new = synced(hub)
    if "--check" in sys.argv:
        if new != hub:
            print("myally_hub_sync --check: the hub's Step 1 tab is stale against step1_tree.json; run scripts/myally_hub_sync.py", file=sys.stderr)
            return 1
        print("myally_hub_sync --check: fresh")
        return 0
    if new != hub:
        open(HUB, "w", encoding="utf-8").write(new)
        print("myally_hub_sync: wrote public/myally-hub.html")
    else:
        print("myally_hub_sync: already fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
