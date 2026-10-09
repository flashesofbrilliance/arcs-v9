#!/usr/bin/env python3
"""held_exceptions.py — every dependency we hold back must say when it can be let go.

Dependabot handles the forward direction (newer versions). It cannot see the reverse: an npm
override or a Dependabot ignore we added on purpose, waiting for some upstream change. Those
sit in package.json or a YAML comment and go stale silently. This keeps them honest.

  held_exceptions.py check   pairing gate (pre-commit): every package.json override and every
                             .github/dependabot.yml ignore has an entry in
                             runtime/specs/held-exceptions.json, and every entry still points at
                             a live override/ignore. Offline. Exit 1 on a mismatch.
  held_exceptions.py watch   evaluate each entry's lift_when against the npm registry
                             (`npm view`). Prints LIFT / HOLD / UNKNOWN per entry. Read-only;
                             never edits package.json. Exit 0 always (a report, not a gate).
  add --json to either for machine output.

lift_when types:
  dep-pin-at-least   {package, dep, min, absent_ok}: the newest stable <package> depends on <dep>
                     at a version >= min (or no longer depends on it, when absent_ok).
  peer-range-admits  {package, peer, major}: the newest stable <package>'s peerDependencies[<peer>]
                     mentions the given major (e.g. ^10, >=10, || 10).

Stdlib only.
"""
import json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(REPO, "runtime", "specs", "held-exceptions.json")
PKG = os.path.join(REPO, "package.json")
DEPENDABOT = os.path.join(REPO, ".github", "dependabot.yml")
VER_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def live_overrides():
    return set((load_json(PKG, {}).get("overrides") or {}).keys())


def live_ignores():
    """dependency-name values under any `ignore:` block. Line-based; dependabot.yml is simple."""
    names, in_ignore, ind = set(), False, 0
    try:
        lines = open(DEPENDABOT, encoding="utf-8").read().splitlines()
    except OSError:
        return names
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if stripped.startswith("ignore:"):
            in_ignore, ind = True, indent
            continue
        if in_ignore and indent <= ind:
            in_ignore = False
        if in_ignore:
            m = re.search(r"dependency-name:\s*[\"']?([^\"'\s]+)", stripped)
            if m:
                names.add(m.group(1))
    return names


def entries():
    return load_json(REGISTRY, {}).get("exceptions", [])


def check():
    live = {("npm-override", n) for n in live_overrides()} | \
           {("dependabot-ignore", n) for n in live_ignores()}
    registered = {(e.get("kind"), e.get("target")) for e in entries()}
    problems = []
    for kind, name in sorted(live - registered):
        problems.append(f"UNREGISTERED {kind} '{name}': add an entry with reason + lift_when "
                        f"to runtime/specs/held-exceptions.json")
    for kind, name in sorted(registered - live):
        problems.append(f"STALE entry {kind} '{name}': the hold is gone; delete its entry")
    for e in entries():
        if not e.get("lift_when") or not e.get("reason"):
            problems.append(f"INCOMPLETE entry '{e.get('id')}': needs reason and lift_when")
    return problems


def npm_view(spec, field):
    try:
        out = subprocess.run(["npm", "view", spec, field, "--json"], capture_output=True,
                             text=True, timeout=60).stdout.strip()
        return json.loads(out) if out else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def newest_stable(pkg):
    """Highest published version with no prerelease suffix. The `latest` dist-tag can point at
    an rc (prisma did on 2026-10-09), which would hide a stable patch on the older line."""
    vs = npm_view(pkg, "versions") or []
    if isinstance(vs, str):
        vs = [vs]
    stable = [v for v in vs if re.fullmatch(r"\d+\.\d+\.\d+", v)]
    return max(stable, key=ver) if stable else None


def ver(s):
    m = VER_RE.search(s or "")
    return tuple(int(x) for x in m.groups()) if m else None


def evaluate(e):
    lw = e.get("lift_when") or {}
    pkg = lw.get("package")
    latest = newest_stable(pkg) if pkg else None
    if not latest:
        return "UNKNOWN", f"could not read a stable {pkg} version from npm"
    if lw.get("type") == "dep-pin-at-least":
        deps = npm_view(f"{pkg}@{latest}", "dependencies") or {}
        pin = deps.get(lw["dep"])
        if pin is None:
            ok = lw.get("absent_ok", False)
            return ("LIFT" if ok else "HOLD"), f"{pkg}@{latest} no longer depends on {lw['dep']}"
        got, need = ver(pin), ver(lw["min"])
        if got and need and got >= need:
            return "LIFT", f"{pkg}@{latest} pins {lw['dep']} {pin} (>= {lw['min']})"
        return "HOLD", f"{pkg}@{latest} pins {lw['dep']} {pin} (< {lw['min']})"
    if lw.get("type") == "peer-range-admits":
        peers = npm_view(f"{pkg}@{latest}", "peerDependencies") or {}
        rng = peers.get(lw["peer"], "")
        major = str(lw["major"])
        if re.search(r"(^|[\s|^~>=])" + major + r"(\.|\b)", rng):
            return "LIFT", f"{pkg}@{latest} peer {lw['peer']} '{rng}' admits {major}"
        return "HOLD", f"{pkg}@{latest} peer {lw['peer']} '{rng}' does not admit {major}"
    return "UNKNOWN", f"unknown lift_when type {lw.get('type')!r}"


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    cmd = next((a for a in args if not a.startswith("-")), "")
    if cmd == "check":
        problems = check()
        if as_json:
            print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
        else:
            for p in problems:
                print(f"held_exceptions: {p}", file=sys.stderr)
            if not problems:
                print(f"held_exceptions: {len(entries())} held exception(s), all registered")
        sys.exit(1 if problems else 0)
    if cmd == "watch":
        rows = []
        for e in entries():
            verdict, why = evaluate(e)
            rows.append({"id": e.get("id"), "verdict": verdict, "why": why,
                         "also_recheck": e.get("also_recheck")})
        if as_json:
            print(json.dumps(rows, indent=2))
        else:
            for r in rows:
                print(f"{r['verdict']:<7} {r['id']}: {r['why']}")
                if r["verdict"] == "LIFT" and r["also_recheck"]:
                    print(f"        also re-check: {r['also_recheck']}")
            problems = check()
            for p in problems:
                print(f"note    {p}")
        return
    print(__doc__.strip().split("\n\n")[1], file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
