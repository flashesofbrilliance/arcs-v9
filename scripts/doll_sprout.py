#!/usr/bin/env python3
"""doll_sprout.py — germinate a doll into a tenant memory dir (UserN+1 side).

Unpacks a doll bundle (doll_export.py output) into memory files. The tenant's
own self-cataloging inchworm (memory_index_sync.py --append) indexes them at
next session start — sprout writes files, never touches the tenant's index.

Rules: collision = SKIP + flag (never overwrite a tenant's existing belief);
@ref / @gated shells are pointers, nothing is written for them; every sprouted
file carries a provenance footer naming the doll's epoch.

Usage: doll_sprout.py <doll.json> [--into DIR] [--dry-run]
Stdlib-only.
"""
import argparse, json, os, sys

DEFAULT_DIR = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--into", default=DEFAULT_DIR)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    b = json.load(open(a.bundle, encoding="utf-8"))
    if b.get("format") != "arcs-doll/1":
        sys.exit("not an arcs-doll/1 bundle")
    epoch = b.get("epoch", {})
    prov = (f"\n\n<!-- sprouted from doll root={b['root']} epoch={epoch.get('repo_commit','?')} "
            f"catalog={epoch.get('catalog_sha','?')} exported={epoch.get('exported','?')} -->\n")
    os.makedirs(a.into, exist_ok=True)
    written, skipped, pointers = [], [], 0

    def walk(shell):
        nonlocal pointers
        if "@ref" in shell or "@gated" in shell or shell.get("missing"):
            pointers += 1
            return
        fname = shell.get("source") if str(shell.get("source", "")).endswith(".md") \
            else shell["id"] + ".md"
        path = os.path.join(a.into, fname)
        if os.path.exists(path):
            skipped.append(fname)
        else:
            if "body" in shell:
                content = shell["body"].rstrip("\n") + prov
            else:  # catalog-level doll: synthesize minimal frontmatter (still inchworm-indexable)
                content = ("---\n"
                           f"name: {shell['id']}\n"
                           f"description: {shell.get('desc','(imported from doll; catalog-level)')}\n"
                           "metadata:\n"
                           f"  type: {shell.get('type','reference')}\n"
                           "---\n\n(catalog-level shell; full body lives in User0's "
                           f"{shell.get('source','source file')})" + prov)
            if not a.dry_run:
                open(path, "w", encoding="utf-8").write(content)
            written.append(fname)
        for c in shell.get("declares", []):
            walk(c)

    walk(b["doll"])
    tag = "DRY-RUN " if a.dry_run else ""
    print(f"sprout: {tag}{len(written)} written · {len(skipped)} skipped (tenant belief kept) · "
          f"{pointers} pointers · into {a.into}")
    if skipped:
        print("skipped: " + " ".join(skipped[:10]) + (" …" if len(skipped) > 10 else ""))
    print("next: the tenant's memory_index_sync.py --append will self-catalog these at session start")


if __name__ == "__main__":
    main()
