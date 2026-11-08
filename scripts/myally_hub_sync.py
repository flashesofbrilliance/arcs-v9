#!/usr/bin/env python3
"""myally_hub_sync.py: inline the engine's Step 1 tree into the myally.arcs.care hub.

The "Light audit and code review" tab in public/myally-hub.html draws its rows from
_ARTIFACTS/engagements/myally-ld/out/step1_tree.json (rendered from engagement.json by
scripts/engagement_render.py). This copies that JSON between the /*S1:BEGIN*/ and /*S1:END*/
sentinels, so the tab, the agreement and Exhibit A all cite one record.

  python3 scripts/myally_hub_sync.py          # write
  python3 scripts/myally_hub_sync.py --check  # read-only; exit 1 when the hub is stale

Gift files (rows with "download", released once their unlock row is done) are copied from the
engagement's private gifts/ folder to public/myally-skills/; any file there that is not released is
removed, so nothing is downloadable before it is earned. --check covers the files too.

Stdlib only. Writes only public/myally-hub.html and public/myally-skills/.
"""
import json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "_ARTIFACTS", "engagements", "myally-ld", "out", "step1_tree.json")
HUB = os.path.join(ROOT, "public", "myally-hub.html")
GIFTS = os.path.join(ROOT, "_ARTIFACTS", "engagements", "myally-ld", "gifts")
PUB = os.path.join(ROOT, "public", "myally-skills")
PAT = re.compile(r"/\*S1:BEGIN\*/.*?/\*S1:END\*/", re.S)


def payload() -> str:
    data = json.load(open(SRC, encoding="utf-8"))
    # Compact, and safe inside a <script>: no "</" can close the tag.
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("</", "<\\/")


def synced(hub: str) -> str:
    if len(PAT.findall(hub)) != 1:
        sys.exit("myally_hub_sync: expected exactly one /*S1:BEGIN*/.../*S1:END*/ block in the hub")
    return PAT.sub(lambda _: "/*S1:BEGIN*/" + payload() + "/*S1:END*/", hub)


def released() -> dict:
    """{public file name: bytes} for every row whose download is released."""
    data = json.load(open(SRC, encoding="utf-8"))
    out = {}
    for r in data.get("rows", []):
        if r.get("download"):
            name = os.path.basename(r["download"])
            out[name] = open(os.path.join(GIFTS, name), "rb").read()
    return out


def gift_drift(want: dict) -> list:
    have = {n: open(os.path.join(PUB, n), "rb").read() for n in (os.listdir(PUB) if os.path.isdir(PUB) else [])}
    return sorted(n for n in set(want) | set(have) if want.get(n) != have.get(n))


def write_gifts(want: dict) -> None:
    if want:
        os.makedirs(PUB, exist_ok=True)
    for n in (os.listdir(PUB) if os.path.isdir(PUB) else []):
        if n not in want:
            os.remove(os.path.join(PUB, n))
    for n, b in want.items():
        open(os.path.join(PUB, n), "wb").write(b)
    if os.path.isdir(PUB) and not os.listdir(PUB):
        os.rmdir(PUB)


def main() -> int:
    hub = open(HUB, encoding="utf-8").read()
    new = synced(hub)
    want = released()
    if "--check" in sys.argv:
        drift = gift_drift(want)
        if drift:
            print("myally_hub_sync --check: public/myally-skills/ does not match the released gifts: " + ", ".join(drift) + "; run scripts/myally_hub_sync.py", file=sys.stderr)
            return 1
        if new != hub:
            print("myally_hub_sync --check: the hub's Step 1 tab is stale against step1_tree.json; run scripts/myally_hub_sync.py", file=sys.stderr)
            return 1
        print("myally_hub_sync --check: fresh")
        return 0
    if gift_drift(want):
        write_gifts(want)
        print("myally_hub_sync: released gifts now " + (", ".join(sorted(want)) or "none"))
    if new != hub:
        open(HUB, "w", encoding="utf-8").write(new)
        print("myally_hub_sync: wrote public/myally-hub.html")
    else:
        print("myally_hub_sync: already fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
