#!/usr/bin/env python3
"""
scan_repo.py — read-only malicious-payload pattern scanner (SBOM payload check).

Detects the DPRK "Contagious Interview" / Famous Chollima (MITRE ATT&CK G1052)
trigger class and, more generally, the reusable pattern-threat-vectors
PTV-01..07 documented in the Contagious Interview dossier.

SAFETY CONTRACT — this tool is static and inert by construction:
  * It only READS files. It never installs, executes, evals, spawns a shell,
    opens a socket, or resolves a hostname.
  * It is therefore safe to run on an UNTRUSTED repo BEFORE you open it in an
    editor or run `npm install`. That is the entire point: catch the trigger
    before it fires.

Exit codes (CI gate):  2 = CRITICAL finding · 1 = HIGH/MEDIUM only · 0 = clean.

Usage:
  python3 scan_repo.py <path> [--json] [--min-severity HIGH] [--iocs FILE]
"""
import argparse, json, math, os, re, sys
from collections import Counter

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
             "dist", "build", ".next", "vendor", ".cache"}
# extensions we bother reading (payloads hide in source/config/scripts)
TEXT_EXT = {".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".json", ".jsonc",
            ".sh", ".bash", ".zsh", ".py", ".rb", ".ps1", ".yml", ".yaml",
            ".env", ".txt", ".md", ""}
MAX_BYTES = 2_000_000
SEV_ORDER = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "INFO": 0}

# Known-bad indicators for this campaign. Override/extend with --iocs (one per line).
DEFAULT_IOCS = [
    "91.121.235.127", "checkStatus", "vscode-check-mo4-ten.vercel.app",
    "hiringtecjreview@outlook.com", "richardstein692@gmail.com",
    "Cryptense-Eco/Jackpot",
]

RE_CURL_PIPE = re.compile(r"\b(?:curl|wget)\b[^\n|]*\|[^\n]*\b(?:bash|sh|zsh)\b", re.I)
RE_EVAL = re.compile(r"\beval\s*\(|\bnew\s+Function\s*\(")
RE_NET = re.compile(r"\b(?:fetch|axios|node-fetch|got|https?\.request|XMLHttpRequest)\b")
RE_ENV = re.compile(r"process\.env\b")
RE_ENV_SER = re.compile(r"(?:JSON\.stringify\s*\(\s*process\.env|\.\.\.\s*process\.env|body[^=\n]{0,40}process\.env)")
RE_PORT1224 = re.compile(r":1224\b")
RE_FOLDEROPEN = re.compile(r'"runOn"\s*:\s*"folderOpen"')
INSTALL_HOOKS = {"preinstall", "install", "postinstall", "prepare",
                 "prepublish", "prepublishOnly", "preprepare", "postprepare"}
RE_HOOK_NET = re.compile(r"\b(?:curl|wget|bash|sh\s+-c|node\s+-e|powershell|Invoke-WebRequest)\b|https?://", re.I)

findings = []


def add(sev, ptv, title, path, line, detail):
    findings.append({"severity": sev, "ptv": ptv, "title": title,
                     "file": path, "line": line, "detail": detail})


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def shannon(s):
    if not s:
        return 0.0
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in Counter(s).values())


def iter_files(root):
    if os.path.isfile(root):
        yield root
        return
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            ext = os.path.splitext(fn)[1].lower()
            if ext and ext not in TEXT_EXT:
                continue
            p = os.path.join(dp, fn)
            try:
                if os.path.getsize(p) > MAX_BYTES:
                    continue
            except OSError:
                continue
            yield p


def read(p):
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def scan_file(path, text, iocs):
    base = os.path.basename(path)

    # PTV-07 — known-bad IOCs / campaign signature (highest confidence)
    for tok in iocs:
        i = text.find(tok)
        if i != -1:
            add("CRITICAL", "PTV-07", "Known-bad indicator present",
                path, lineno(text, i), f"matched IOC: {tok}")
    for m in RE_PORT1224.finditer(text):
        add("CRITICAL", "PTV-07", "Egress to campaign port :1224",
            path, lineno(text, m.start()), m.group(0))

    # PTV-01 — VS Code auto-run on folder open
    if base in ("tasks.json",) or base.endswith("tasks.json"):
        m = RE_FOLDEROPEN.search(text)
        if m:
            hidden = '"reveal"' in text and '"never"' in text
            add("CRITICAL", "PTV-01", "VS Code task auto-runs on folderOpen",
                path, lineno(text, m.start()),
                "runOn:folderOpen" + (" + reveal:never (hidden terminal)" if hidden else ""))

    # PTV-02 — npm lifecycle-hook execution
    if base == "package.json":
        try:
            data = json.loads(text)
            for name, cmd in (data.get("scripts") or {}).items():
                if name in INSTALL_HOOKS and isinstance(cmd, str):
                    if RE_HOOK_NET.search(cmd):
                        add("HIGH", "PTV-02", f"Install hook '{name}' fetches/executes",
                            path, lineno(text, text.find(f'"{name}"')), cmd[:120])
                    else:
                        add("MEDIUM", "PTV-02", f"Install hook '{name}' runs code on install",
                            path, lineno(text, text.find(f'"{name}"')), cmd[:120])
        except (ValueError, TypeError):
            pass

    # PTV-03 — remote pipe-to-shell
    for m in RE_CURL_PIPE.finditer(text):
        add("HIGH", "PTV-03", "Remote pipe-to-shell (curl|bash)",
            path, lineno(text, m.start()), m.group(0)[:120])

    has_net = RE_NET.search(text) is not None

    # PTV-04 — server-driven eval
    for m in RE_EVAL.finditer(text):
        sev = "HIGH" if has_net else "INFO"
        add(sev, "PTV-04", "Dynamic eval / new Function"
            + (" co-located with network I/O" if has_net else ""),
            path, lineno(text, m.start()), m.group(0))

    # PTV-05 — env-var exfiltration
    if RE_ENV.search(text) and has_net:
        ser = RE_ENV_SER.search(text)
        if ser:
            add("HIGH", "PTV-05", "process.env serialized toward network",
                path, lineno(text, ser.start()), ser.group(0)[:120])
        else:
            add("MEDIUM", "PTV-05", "process.env read in a file that also does network I/O",
                path, lineno(text, RE_ENV.search(text).start()), "review for exfil")

    # PTV-06 — obfuscated payload appended as a long, high-entropy line
    if os.path.splitext(base)[1].lower() in (".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx"):
        for n, ln in enumerate(text.splitlines(), 1):
            if len(ln) > 500 and shannon(ln) > 4.5:
                add("MEDIUM", "PTV-06", "Long high-entropy line (possible appended payload)",
                    path, n, f"len={len(ln)} entropy={shannon(ln):.2f}")
                break  # one per file is enough signal


def main():
    ap = argparse.ArgumentParser(description="Read-only malicious-payload pattern scanner (PTV-01..07).")
    ap.add_argument("path", help="repo or file to scan (never executed)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--min-severity", default="INFO", choices=list(SEV_ORDER),
                    help="only report at/above this severity")
    ap.add_argument("--iocs", help="file with extra IOCs, one per line")
    args = ap.parse_args()

    iocs = list(DEFAULT_IOCS)
    if args.iocs:
        txt = read(args.iocs) or ""
        iocs += [l.strip() for l in txt.splitlines() if l.strip() and not l.startswith("#")]

    if not os.path.exists(args.path):
        print(f"error: path not found: {args.path}", file=sys.stderr)
        return 2

    for p in iter_files(args.path):
        t = read(p)
        if t is not None:
            scan_file(os.path.relpath(p, args.path if os.path.isdir(args.path) else os.path.dirname(p) or "."), t, iocs)

    floor = SEV_ORDER[args.min_severity]
    shown = [f for f in findings if SEV_ORDER[f["severity"]] >= floor]
    shown.sort(key=lambda f: (-SEV_ORDER[f["severity"]], f["ptv"], f["file"]))

    if args.json:
        print(json.dumps({"findings": shown, "total": len(shown)}, indent=2))
    else:
        if not shown:
            print("clean — no PTV patterns at/above", args.min_severity)
        for f in shown:
            print(f"[{f['severity']:8}] {f['ptv']}  {f['file']}:{f['line']}  {f['title']}")
            if f["detail"]:
                print(f"           └ {f['detail']}")
        print(f"\n{len(shown)} finding(s). Reminder: never run/install this repo to inspect it.")

    worst = max((SEV_ORDER[f["severity"]] for f in findings), default=0)
    return 2 if worst >= SEV_ORDER["CRITICAL"] else (1 if worst >= SEV_ORDER["MEDIUM"] else 0)


if __name__ == "__main__":
    sys.exit(main())
