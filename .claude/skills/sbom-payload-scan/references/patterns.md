# Pattern-threat-vectors (PTV-01..07)

The scanner abstracts the DPRK "Contagious Interview" trigger chain into reusable, hunt-worthy
patterns. Infrastructure rotates; behavior persists — detecting the pattern class catches the next
repo, not just the one in front of you. Each row is what a finding of that PTV means and why it is
hostile.

| PTV | Pattern | Where it hides | Why it is hostile | Default severity |
|-----|---------|----------------|-------------------|------------------|
| PTV-01 | Auto-run on folder open | `.vscode/tasks.json` (`runOn: folderOpen`) | Executes before any human review; legitimate repos essentially never ship a folderOpen shell task, and `reveal: never` hides the terminal. | CRITICAL |
| PTV-02 | Install lifecycle hook | `package.json` `preinstall`/`install`/`postinstall`/`prepare` | Runs automatically on `npm install`; the #1 npm supply-chain vector. HIGH if it fetches/executes (curl, node -e, remote URL), MEDIUM if it merely runs a repo script. | HIGH / MEDIUM |
| PTV-03 | Remote pipe-to-shell | Any script/config | `curl … \| bash` fetches attacker-chosen code at runtime; nothing malicious is stored on disk to scan. | HIGH |
| PTV-04 | Server-driven eval | Stealer JS | `eval(response)` / `new Function(response)` turns a "status check" into interactive RCE; the payload never appears in source. HIGH when co-located with network I/O. | HIGH |
| PTV-05 | Env-var exfiltration | Stealer JS | `process.env` on a dev machine holds cloud keys, tokens, DB creds. Serializing it toward the network (`JSON.stringify(process.env)`, `...process.env` in a body) is theft. | HIGH / MEDIUM |
| PTV-06 | Obfuscated appended payload | A real-looking source file (e.g. an auth route) | Malice bolted onto a legitimate file as a single long, high-entropy/minified line that hides in a diff. | MEDIUM |
| PTV-07 | Known-bad IOC / signature | Anywhere | A pinned campaign indicator (IP, host, path, email, repo) or the recurring Contagious Interview port `:1224`. Highest confidence. | CRITICAL |

## Campaign reference
- Actor: DPRK "Contagious Interview" / Famous Chollima, MITRE ATT&CK **G1052** (aliases:
  DeceptiveDevelopment, DEV#POPPER, Tenacious Pungsan, UNC5342, PurpleBravo/TAG-121, Gwisin Gang).
- Stage 1: **BeaverTail** (JS stealer/downloader, ATT&CK S1246). Stage 2: **InvisibleFerret** (Python
  backdoor). Sibling loader: **OtterCookie**.
- Lure: fake recruiter → "coding assessment" repo → folderOpen task and/or `prepare` hook detonate.

## Tuning
- Add your own indicators via `--iocs <file>` (one per line). Campaign IOCs ship in the
  Contagious-Interview detection bundle (`analysis/detections/iocs.csv`).
- Legitimate monorepos sometimes use `prepare` for husky/build. Read PTV-02 MEDIUM findings rather
  than blocking on them; reserve the CI hard-fail for CRITICAL (`--min-severity` does not change exit
  codes, which always reflect the worst finding).
