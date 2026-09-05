# Contagious Interview — detection bundle

Version-controlled, CI-ingestible detection artifacts for the DPRK "Contagious Interview" / Famous
Chollima campaign (MITRE ATT&CK **G1052**). The reusable, general-purpose payload scanner that grew
out of these patterns now lives as its own skill (see below).

Full analysis: `analysis/contagious-interview-dossier.html` (or the published dossier artifact) —
§03 Malicious BOM, §04 Detection, §07 ARCS layer.

## Contents

| File | Use |
|------|-----|
| `iocs.csv` | Structured indicators (type, value, severity, note). Feed to blocklists or the scanner's `--iocs`. |
| `beavertail_contagious_interview.yar` | YARA — BeaverTail JS stealer/loader (pinned infra OR behavior cluster). |
| `sigma_net_beacon_1224.yml` | Sigma — network beacon to the C2 / port 1224. |
| `sigma_proc_curl_pipe_shell.yml` | Sigma — dev-tool spawning remote pipe-to-shell. |

## The scanner (reusable) → `sbom-payload-scan` skill

The read-only payload scanner (PTV-01..07) is packaged as the **`sbom-payload-scan`** skill at
`.claude/skills/sbom-payload-scan/`. It is stdlib-only and inert by construction: it reads files and
never installs, executes, evals, or touches the network — safe to run on an untrusted repo *before*
you open or install it.

```bash
# scan an untrusted repo you have NOT opened or installed; feed campaign IOCs
python3 .claude/skills/sbom-payload-scan/scripts/scan_repo.py <suspect-repo> \
  --min-severity HIGH --iocs analysis/detections/iocs.csv

# CI gate: exit 2 = CRITICAL, 1 = HIGH/MEDIUM, 0 = clean
```

## Pattern-threat-vectors

Documented in the skill's `references/patterns.md`. Summary: PTV-01 folderOpen task · PTV-02 install
hooks · PTV-03 curl|bash · PTV-04 eval+net · PTV-05 process.env exfil · PTV-06 obfuscated appended
line · PTV-07 known-bad IOC / port 1224.

## Safety contract

Never run `npm install` on an untrusted repo to "see what it does" — that is the exploit. Read it,
scan it, and if you must run it, do so only in a disposable VM with no network, no real credentials,
and `npm config set ignore-scripts true`.
