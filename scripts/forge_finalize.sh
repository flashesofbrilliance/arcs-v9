#!/usr/bin/env bash
# forge_finalize.sh <jobid> <slug> <actual_tokens> "<note>" — mechanical close of a light-tier forge run:
# verify 2 pages + air-gap greps, register in runtime/specs/forge-bundles.json, ledger line,
# PATCH the board row to built with viewer links, mirror to iCloud. Fails loud on a bad cut.
set -euo pipefail
J=$1; S=$2; TOK=$3; NOTE=$4; B=_ARTIFACTS/forge-$S
PDF=$B/resume-$S.pdf; [ -f "$PDF" ] || PDF=$B/resume-$S-ats.pdf
PAGES=$(pdfinfo "$PDF" | awk '/^Pages/{print $2}')
[ "$PAGES" = "2" ] || { echo "FAIL $S: $PAGES pages"; exit 1; }
EM=$(grep -c '—' $B/page.html || true); SV=$(grep -ciE '\b(tier|band|composite|pursue)\b' $B/page.html || true)
[ "$EM" = "0" ] && [ "$SV" = "0" ] || { echo "FAIL $S: em-dashes=$EM scoring-vocab=$SV on page.html"; exit 1; }
python3 - "$J" "$S" "$(basename "$PDF")" <<'PY'
import json,sys;j,s,pdf=sys.argv[1:];p='runtime/specs/forge-bundles.json';m=json.load(open(p))
m['bundles'][j]={"dir":f"forge-{s}","slug":s,"resume":pdf};json.dump(m,open(p,'w'),indent=2);print('manifest',len(m['bundles']))
PY
printf '{"date": "%s", "target": "%s", "stage": "forge-light", "est_tokens": null, "actual_tokens": %s, "metered": true, "notes": "inputs pre-staged; sonnet; harness-metered"}\n' "$(date +%F)" "$S" "$TOK" >> _STATE/job-search/forge-cost-ledger.jsonl
set -a; . ~/.arcs/jobs-pipeline.env; set +a
python3 - "$J" "$S" "$(basename "$PDF")" "$NOTE" <<'PY' > /tmp/fb.json
import json,sys;j,s,pdf,note=sys.argv[1:]
print(json.dumps({"jobid":j,"status":"built","url":f"/jobs/{j}/forge","resumeUrl":f"/jobs/{j}/forge?file={pdf}","notes":note}))
PY
curl -s -o /dev/null -w "board PATCH %{http_code}\n" -X PATCH -H "x-jobs-token: $JOBS_PIPELINE_TOKEN" -H "content-type: application/json" -d @/tmp/fb.json https://jobs.arcs.care/api/jobs/forge
scripts/forge_mirror_icloud.sh
echo "OK $S: 2 pages, air-gap clean"
