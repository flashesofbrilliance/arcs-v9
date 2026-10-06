#!/usr/bin/env python3
"""Fail when decision text could reach a sink the trust contract rules out (PL-011).

Public claims bound here (src/app/trust/page.tsx §2, src/app/privacy/page.tsx):
  - "Input never trains a model": the only model provider is Anthropic's API, so no
    other LLM or ML SDK may be imported under src/.
  - Analytics "No cookies, no decision text": Vercel Analytics is the only analytics
    SDK, and every track() payload uses only the allowlisted keys below (ids and
    enums, never free text). A new key must be added here on purpose, in review.
Stdlib only.

Usage: python3 scripts/purpose_guard.py [repo_root]
"""
import re
import sys
from pathlib import Path

TRACK_KEYS = {"receiptId", "method", "campaign", "source", "reason", "status"}
FORBIDDEN_SDK = re.compile(
    r"""(?:from|require\()\s*['"](openai|@openai/[^'"]*|@google/gen(erative-)?ai|cohere-ai|@mistralai/[^'"]*|"""
    r"""replicate|groq-sdk|together-ai|@huggingface/[^'"]*|ai|@ai-sdk/[^'"]*|posthog-[^'"]*|posthog-js|"""
    r"""mixpanel[^'"]*|@segment/[^'"]*|@amplitude/[^'"]*|@sentry/[^'"]*|@datadog/[^'"]*|"""
    r"""@?heap[^'"]*|@fullstory/[^'"]*|logrocket[^'"]*|hotjar[^'"]*)['"]"""
)
TRACK_CALL = re.compile(r"\btrack\(\s*(['\"][^'\"]+['\"])\s*(?:,\s*\{([^}]*)\})?\s*\)")
TRACK_ANY = re.compile(r"\btrack\(")
KEY = re.compile(r"([A-Za-z_$][\w$]*)\s*(?::|,|$)")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    errs = []
    for f in sorted((root / "src").rglob("*")):
        if not f.is_file() or f.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
            continue
        rel = f.relative_to(root).as_posix()
        text = f.read_text(errors="ignore")
        for m in FORBIDDEN_SDK.finditer(text):
            errs.append(f"{rel}: imports '{m.group(1)}' (only Anthropic may see input; only Vercel Analytics may count)")
        n_any = len(TRACK_ANY.findall(text))
        calls = list(TRACK_CALL.finditer(text))
        if n_any != len(calls):
            errs.append(f"{rel}: track() call not in literal form track(\"event\", {{ key, ... }}) so its payload can't be checked")
        for m in calls:
            body = (m.group(2) or "").strip()
            keys = {k for k in KEY.findall(body)} if body else set()
            if "..." in body:
                errs.append(f"{rel}: track({m.group(1)}) spreads an object into the payload")
            bad = keys - TRACK_KEYS
            if bad:
                errs.append(f"{rel}: track({m.group(1)}) sends non-allowlisted key(s) {sorted(bad)}")
    if errs:
        print("purpose_guard FAIL (PL-011, trust contract §2 / privacy analytics claim):")
        print("\n".join("  " + e for e in errs))
        return 1
    print("purpose_guard OK: no non-Anthropic model SDK, no third-party analytics, track() payloads allowlisted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
