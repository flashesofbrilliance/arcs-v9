#!/usr/bin/env python3
"""Fail when className / Tailwind / stray stylesheets creep back into src/ (LINT-006).

Inline styles only (AGENTS.md gotcha #2). Tailwind was removed 2026-07-11 and nothing
stopped it returning. Sanctioned exceptions are listed below with their reason; any new
one must be added here on purpose, in review. Stdlib only.

Usage: python3 scripts/classname_guard.py [repo_root]
"""
import json
import re
import sys
from pathlib import Path

# file -> max allowed className occurrences, with why
CLASSNAME_ALLOW = {
    "src/app/layout.tsx": 1,  # next/font variable classes on <html> (framework mechanism)
    "src/app/recoil/[reportId]/ReportActions.tsx": 1,  # @media print hide; inline styles can't express media queries
}
CSS_ALLOW = {
    "src/app/globals.css",  # reset + keyframes + font tokens
    "src/ui-kit/recoil-report/_tokens.css",  # artifact token kit (gotcha #13)
}
TAILWIND = re.compile(r"@tailwind|@apply\b|from ['\"]tailwind|require\(['\"]tailwind")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    errs = []
    for f in sorted((root / "src").rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(root).as_posix()
        if f.suffix in {".css", ".scss", ".sass", ".less"} and rel not in CSS_ALLOW:
            errs.append(f"{rel}: stylesheet outside the sanctioned set")
            continue
        if f.suffix not in {".tsx", ".jsx", ".ts", ".js", ".css"}:
            continue
        text = f.read_text(errors="ignore")
        n = len(re.findall(r"\bclassName\s*=", text))
        if n > CLASSNAME_ALLOW.get(rel, 0):
            errs.append(f"{rel}: {n} className (allowed {CLASSNAME_ALLOW.get(rel, 0)})")
        if TAILWIND.search(text):
            errs.append(f"{rel}: Tailwind directive/import")
    pkg = root / "package.json"
    if pkg.exists():
        deps = {**json.loads(pkg.read_text()).get("dependencies", {}),
                **json.loads(pkg.read_text()).get("devDependencies", {})}
        errs += [f"package.json: {d} dependency" for d in deps if "tailwind" in d]
    for c in root.glob("tailwind.config.*"):
        errs.append(f"{c.name}: Tailwind config present")
    for e in errs:
        print(f"✖ {e}", file=sys.stderr)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
