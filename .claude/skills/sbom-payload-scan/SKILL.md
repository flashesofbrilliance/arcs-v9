---
name: sbom-payload-scan
description: >
  Statically scan an untrusted repo, npm/pip package, or dependency for malicious install-time and
  open-time payload triggers BEFORE opening or installing it. Use this whenever a repo arrives from a
  recruiter or "coding assignment/take-home", an unfamiliar dependency is about to be added, a
  package.json / .vscode / postinstall hook looks suspicious, or someone asks "is it safe to open this
  repo?" — even if they don't say "scan" or "malware". Catches the DPRK Contagious Interview / Famous
  Chollima (MITRE G1052) trigger class and the general pattern-threat-vectors PTV-01..07 (folderOpen
  tasks, install lifecycle hooks, curl|bash, server-driven eval, process.env exfil, obfuscated
  appended lines, known-bad IOCs). Prefer this over reading the files by hand or (never) running
  `npm install` to "see what it does".
---

# SBOM payload scan

A read-only tripwire for the "opening the folder is the exploit" threat class. Modern supply-chain
lures (fake interviews, trojanized dependencies) execute the moment you open or install them, so the
tool that inspects them must never itself run them. This skill is that tool.

## When to reach for it
- A repo/zip arrived via a recruiter, take-home, "debug my project", or unsolicited DM.
- Before adding or auditing an unfamiliar npm/pip dependency, or reviewing a suspicious PR.
- Any supply-chain scare where the question is "is this safe to open?" and you must answer without
  detonating it.

## How to run it
The engine is `scripts/scan_repo.py` — Python stdlib only, and inert by construction: it **reads**
files and never installs, executes, evals, spawns a shell, or touches the network. Run it against the
suspect path from a location where the repo is NOT open in an editor and has NOT been installed.

```bash
python3 scripts/scan_repo.py <suspect-path> --min-severity HIGH --json
```

Interpret the exit code as a CI gate:
- `2` — CRITICAL. Block. If the repo was already opened/installed, treat the host as compromised and
  move to incident response (isolate, rotate every reachable credential, hunt outbound C2).
- `1` — HIGH/MEDIUM. Review each finding; some install hooks are legitimate, so read them.
- `0` — clean at the chosen floor. Means "no known pattern fired," not "provably safe."

Extend the known-bad indicator list with `--iocs <file>` (one indicator per line, `#` comments ok).

## What it checks
The seven pattern-threat-vectors are documented in `references/patterns.md` (read it to explain a
finding or tune severity). In short: PTV-01 folderOpen task · PTV-02 install lifecycle hooks ·
PTV-03 curl|bash · PTV-04 eval fed by network · PTV-05 process.env exfil · PTV-06 obfuscated appended
line · PTV-07 known-bad IOC / port 1224.

## The safe-inspection rule (say this to the user if they're about to run the repo)
Never `npm install` or open an untrusted repo to inspect it — that is the exploit. Read it, scan it,
and if you must execute it, do so only in a disposable VM with no network, no real credentials, and
`npm config set ignore-scripts true`.

## Honest limits
This is a static heuristic, not a sandbox or a guarantee. It will miss novel obfuscation and can
false-positive on legitimate build tooling, so read the flagged lines rather than trusting the verdict
blindly. A clean result lowers suspicion; it does not certify safety. Pair any CRITICAL with a real
incident-response process.

## Verifying changes to this skill
`evals/fixtures/` holds a matched pair — a synthetic malicious repo (`evil/`) and a clean one
(`benign/`). After editing `scan_repo.py`, confirm it still fires on `evil` (exit 2) and stays quiet
on `benign` (exit 0). `evals/evals.json` carries the test prompts for a fuller skill-creator run.
