#!/usr/bin/env python3
"""
repo_intake_scan.py — mechanical pre-flight for UNTRUSTED repos.

Run this BEFORE reading a stranger's repo for meaning, and long before
`npm install` / opening it in an editor. It greps for the IOC classes used by
the DPRK "Contagious Interview" (BeaverTail) malicious take-home repos and the
broader supply-chain-injection family: silent auto-run hooks, curl|bash loaders,
off-screen-padded lines, and base64+eval/fetch beacons.

Stdlib-only. Read-only: it NEVER executes repo code, resolves URLs, or installs.
The scan itself is safe to run on a hostile tree. Cloning is inert; the danger is
install/folder-open/run — this tells you whether those are booby-trapped first.

Usage:
    python3 scripts/repo_intake_scan.py <path-to-cloned-repo>
Exit codes: 0 = clean, 1 = HIGH-severity hit(s), 2 = only MEDIUM/LOW, 3 = usage error.

Related: memory malicious-take-home-contagious-interview-redflags;
cheap-tripwire-before-expensive-jtbd; when-to-teleport-to-terminal-vs-agents.
"""
import base64
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", "__pycache__", "venv", ".venv"}
TEXT_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".py", ".rb", ".go",
    ".sh", ".bash", ".ps1", ".bat", ".cmd", ".yml", ".yaml", ".toml", ".env",
    ".md", ".txt", ".cfg", ".ini", "",
}
MAX_BYTES = 2_000_000  # skip anything larger; malware payloads are small

# (severity, label, compiled regex, why)
PATTERNS = [
    ("HIGH", "curl|bash / wget|sh remote loader",
     re.compile(r"(curl|wget)\b[^\n|]*\|\s*(ba)?sh\b|(curl|wget)\b[^\n|]*\|\s*cmd\b", re.I),
     "Downloads and executes a remote script. Classic second-stage loader."),
    ("HIGH", "VS Code task auto-run on folder open",
     re.compile(r'"runOn"\s*:\s*"folderOpen"', re.I),
     "tasks.json runs a command the instant the folder is opened in VS Code."),
    ("HIGH", "eval of network / decoded content",
     re.compile(r"eval\s*\(\s*(await\s+)?(fetch|response|res|data|resp|atob|Buffer)", re.I),
     "Executes attacker-controlled bytes = remote code execution beacon."),
    ("HIGH", "process.env exfiltration",
     re.compile(r"(fetch|axios|request|https?\.request|XMLHttpRequest)[^\n]{0,80}process\.env|"
                r"(JSON\.stringify|URLSearchParams)\([^\n]{0,40}process\.env", re.I),
     "Sends the full environment (all secrets) off-box."),
    ("HIGH", "hardcoded IP:port C2 (incl. BeaverTail :1224)",
     re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\s*[:/]\s*(1224|\d{2,5})\b"),
     "Hardcoded IP endpoint; port 1224 is a documented BeaverTail C2 IOC."),
    ("MED", "npm lifecycle hook (pre/post-install, prepare)",
     re.compile(r'"(preinstall|postinstall|prepare|prepublish)"\s*:', re.I),
     "Runs automatically on `npm install`. Legit sometimes; a common payload trigger."),
    ("MED", "base64 blob (>=40 chars) — decode & inspect",
     re.compile(r"[A-Za-z0-9+/]{40,}={0,2}"),
     "Long base64 often hides a URL/command. Decoded below when it looks like one."),
    ("MED", "child_process / os exec",
     re.compile(r"child_process|require\(\s*['\"]child_process['\"]\s*\)|\bexecSync\b|\bspawnSync\b", re.I),
     "Shell-out primitive. Review what it runs."),
    ("LOW", "obfuscated hex-name identifiers (_0x…)",
     re.compile(r"_0x[0-9a-f]{4,}"),
     "Hallmark of javascript-obfuscator output; legit code rarely looks like this."),
]

# Lines padded far to the right hide payloads off-screen in an editor.
PADDING_RE = re.compile(r"^\s{200,}\S|\S\s{200,}\S")
B64_LIKELY = re.compile(r"^[A-Za-z0-9+/]{40,}={0,2}$")


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext and ext not in TEXT_EXT:
                continue
            path = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(path) > MAX_BYTES:
                    continue
            except OSError:
                continue
            yield path


def decode_b64_hint(token):
    """Return decoded text if it looks like a URL/command, else None."""
    try:
        raw = base64.b64decode(token, validate=True)
    except Exception:
        return None
    try:
        txt = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if re.search(r"https?://|\.onion|/api/|bash|curl|wget|eval|\d{1,3}(\.\d{1,3}){3}", txt, re.I):
        return txt
    return None


def scan(root):
    findings = []
    for path in iter_files(root):
        rel = os.path.relpath(path, root)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if PADDING_RE.search(line):
                findings.append(("HIGH", "off-screen whitespace padding (hidden payload)",
                                 rel, i, "Content pushed far right to hide it in an editor.", ""))
            for sev, label, rx, why in PATTERNS:
                m = rx.search(line)
                if not m:
                    continue
                extra = ""
                if label.startswith("base64"):
                    tok = m.group(0)
                    if B64_LIKELY.match(tok):
                        dec = decode_b64_hint(tok)
                        if dec is None:
                            continue  # boring base64 (hashes, integrity) — skip noise
                        extra = f"decodes to: {dec[:120]}"
                    else:
                        continue
                findings.append((sev, label, rel, i, why, extra))
    return findings


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 3
    root = argv[1]
    if not os.path.isdir(root):
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 3

    findings = scan(root)
    order = {"HIGH": 0, "MED": 1, "LOW": 2}
    findings.sort(key=lambda f: (order.get(f[0], 9), f[2], f[3]))

    if not findings:
        print(f"CLEAN — no known injection IOCs in {root}")
        print("(Absence of hits is not proof of safety. Still sandbox + read before running.)")
        return 0

    counts = {"HIGH": 0, "MED": 0, "LOW": 0}
    print(f"repo-intake scan: {root}\n" + "=" * 60)
    for sev, label, rel, line, why, extra in findings:
        counts[sev] = counts.get(sev, 0) + 1
        print(f"[{sev}] {label}\n      {rel}:{line} — {why}")
        if extra:
            print(f"      >> {extra}")
    print("=" * 60)
    print("summary: " + json.dumps(counts))
    if counts.get("HIGH"):
        print("VERDICT: DO NOT install / open in an editor / run. Treat as hostile until cleared.")
        return 1
    print("VERDICT: review the medium/low hits before running.")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
