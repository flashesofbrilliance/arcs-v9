#!/usr/bin/env python3
"""trust_name_leak: Job Factory slice 6. A staged artifact (resume cut, draft page,
cover letter, answers) must not carry a name from Zach's champion list unless Zach
put it there on purpose. The trust list is private network data; a name in an
outbound draft is a disclosure the system must never make on its own.

Names come from runtime/data/champion-shortlist-v1.tsv (column 2). A name counts
as present when the FULL name appears with word edges (case-insensitive); first
names alone never fire, so "Robin" in prose is fine and "Robin Daniels" is not.
Allowed names: --allow "First Last" (repeatable) or an allowed-names.txt beside
the draft (one per line), which is how Zach adds a referral by hand.

  python3 scripts/trust_name_leak.py <file> [...]            # exit 1 on any unallowed name
  python3 scripts/trust_name_leak.py --allow "First Last" <file>
  python3 scripts/trust_name_leak.py --self-test
Output never prints a matched name in full (initials only), so a CI log is not itself a leak.
"""
import argparse, os, re, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TSV = os.path.join(ROOT, "runtime", "data", "champion-shortlist-v1.tsv")


def load_names(path=TSV):
    names = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == 0 or not line.strip():
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) > 1 and len(cols[1].split()) >= 2:
                names.append(cols[1].strip())
    return names


def initials(n):
    return ".".join(p[0].upper() for p in n.split() if p) + "."


def allowed_for(path, extra):
    out = {a.strip().lower() for a in extra}
    side = os.path.join(os.path.dirname(os.path.abspath(path)), "allowed-names.txt")
    if os.path.isfile(side):
        out |= {l.strip().lower() for l in open(side, encoding="utf-8") if l.strip()}
    return out


def scan(path, names, extra=()):
    text = open(path, encoding="utf-8", errors="replace").read()
    ok = allowed_for(path, extra)
    hits = []
    for n in names:
        if n.lower() in ok:
            continue
        if re.search(r"(?<!\w)" + re.escape(n) + r"(?!\w)", text, re.I):
            hits.append(initials(n))
    return hits


def self_test():
    d = tempfile.mkdtemp()
    tsv = os.path.join(d, "list.tsv")
    open(tsv, "w").write("lane\tname\tposition\tcompany\turl\nwarm\tRobin Daniels\tVP\tAcme\tx\nwarm\tCher\tCEO\tSolo\tx\n")
    names = load_names(tsv)
    f = os.path.join(d, "cover.md")
    checks = []
    open(f, "w").write("Robin suggested I write. The robin on the sill sang.")
    checks.append(("first name alone never fires", scan(f, names) == []))
    open(f, "w").write("Robin Daniels suggested I write.")
    checks.append(("full name fires, reported as initials", scan(f, names) == ["R.D."]))
    checks.append(("--allow clears it", scan(f, names, ["robin daniels"]) == []))
    open(os.path.join(d, "allowed-names.txt"), "w").write("Robin Daniels\n")
    checks.append(("allowed-names.txt clears it", scan(f, names) == []))
    checks.append(("single-word names are not loaded (too ambiguous)", "Cher" not in names))
    for name, passed in checks:
        print(("ok   " if passed else "FAIL ") + name)
    return 0 if all(p for _, p in checks) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--allow", action="append", default=[])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if not a.files:
        ap.error("pass at least one file")
    names = load_names()
    bad = 0
    for p in a.files:
        hits = scan(p, names, a.allow)
        if hits:
            bad += 1
            print(f"[FAIL] {p}: {len(hits)} name(s) from the champion list ({', '.join(hits)}); remove, or allow on purpose")
        else:
            print(f"[ok]   {p}")
    sys.exit(1 if bad else 0)
