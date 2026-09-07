#!/usr/bin/env bash
# forge_finalize_one.sh <jobid> <slug> <tokens> "<note>" — lean per-bundle close:
# verify 2 pages + air-gap, register manifest, ledger, board PATCH, copy JUST this
# bundle to iCloud (not a full re-mirror). Fast; safe to run per completed forge.
set -euo pipefail
J=$1; S=$2; TOK=$3; NOTE=$4; B=_ARTIFACTS/forge-$S
PDF=$B/resume-$S.pdf; [ -f "$PDF" ] || PDF=$(ls $B/resume-$S*.pdf 2>/dev/null|head -1)
PAGES=$(pdfinfo "$PDF" | awk '/^Pages/{print $2}')
[ "$PAGES" = "2" ] || { echo "FAIL $S: $PAGES pages"; exit 1; }
EM=$(grep -c '—' $B/page.html || true); SV=$(grep -ciE '\b(tier|band|composite|pursue)\b' $B/page.html || true)
[ "$EM" = "0" ] && [ "$SV" = "0" ] || { echo "FAIL $S: em=$EM sv=$SV"; exit 1; }
PDFB=$(basename "$PDF")
TXT=$(ls $B/resume-$S-ats.txt 2>/dev/null||ls $B/resume-$S.txt 2>/dev/null|head -1)
python3 - "$J" "$S" "$PDFB" "$(basename "${TXT:-}")" <<'PY'
import json,sys;j,s,pdf,txt=sys.argv[1:];p='runtime/specs/forge-bundles.json';m=json.load(open(p))
m['bundles'][j]={"dir":f"forge-{s}","slug":s,"resume":pdf,"resume_pdf":pdf,"resume_txt":txt or None}
json.dump(m,open(p,'w'),indent=2);print('manifest',len(m['bundles']))
PY
printf '{"date":"%s","target":"%s","stage":"forge-light","actual_tokens":%s,"metered":true,"notes":"batch-clear queued"}\n' "$(date +%F)" "$S" "$TOK" >> _STATE/job-search/forge-cost-ledger.jsonl
set -a; . ~/.arcs/jobs-pipeline.env; set +a
python3 - "$J" "$S" "$PDFB" "$NOTE" <<'PY' > /tmp/fb.json
import json,sys;j,s,pdf,note=sys.argv[1:];print(json.dumps({"jobid":j,"status":"built","url":f"/jobs/{j}/forge","resumeUrl":f"/jobs/{j}/forge?file={pdf}&dl=1","notes":note}))
PY
curl -s -m 25 -o /dev/null -w "board %{http_code}\n" -X PATCH -H "x-jobs-token: $JOBS_PIPELINE_TOKEN" -H "content-type: application/json" -d @/tmp/fb.json https://jobs.arcs.care/api/jobs/forge
# iCloud: just this bundle
R="$HOME/Library/Mobile Documents/com~apple~CloudDocs/ARCS/resumes/$S"; mkdir -p "$R/_bundle"
cp -p "$PDF" "$R/Zach-Harris-Resume-$S.pdf"; [ -n "${TXT:-}" ] && cp -p "$TXT" "$R/Zach-Harris-Resume-$S-ATS.txt"
cp -p $B/* "$R/_bundle/" 2>/dev/null || true
echo "OK $S: 2 pages, air-gap clean, mirrored"
