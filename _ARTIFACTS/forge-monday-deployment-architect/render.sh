#!/usr/bin/env bash
# render.sh — HTML resume -> print-safe PDF + rasterized pages + ATS plain text.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IN="${1:-$HERE/resume-monday-deployment-architect-ats.html}"
BASE="${2:-$HERE/resume-monday-deployment-architect}"
OUT="${BASE}.pdf"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || CHROME="/Applications/Chromium.app/Contents/MacOS/Chromium"
[ -x "$CHROME" ] || CHROME="$(command -v google-chrome || command -v chromium || true)"
[ -n "$CHROME" ] || { echo "no Chrome/Chromium found"; exit 1; }

ABS="$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$OUT" "file://$ABS" 2>/dev/null
sleep 1

rm -f "${BASE}-page-"*.png
if command -v pdftoppm >/dev/null 2>&1; then
  pdftoppm -png -r 110 "$OUT" "${BASE}-page" 2>/dev/null
elif command -v magick >/dev/null 2>&1; then
  magick -density 110 "$OUT" "${BASE}-page-%d.png"
elif command -v gs >/dev/null 2>&1; then
  gs -sDEVICE=png16m -r110 -o "${BASE}-page-%d.png" "$OUT" >/dev/null 2>&1
else
  echo "no rasterizer (pdftoppm|magick|gs); PDF only"
fi

python3 - "$ABS" "${BASE}.txt" <<'PY'
import sys, re, html
from html.parser import HTMLParser
src, dst = sys.argv[1], sys.argv[2]
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.out=[]; s.skip=0; s.buf=''
    def handle_starttag(s, t, a):
        if t in ('style','script','head'): s.skip+=1
        if t=='span' and s.buf and not s.buf.endswith(' '):
            cls=dict(a).get('class','')
            if any(c in cls for c in ('gloss','fit','yr','dom','job-role')): s.buf+=' · '
        if t in ('div','p','li','section','header','footer','br','ul'): s.flush()
        if t=='li': s.buf='- '
        if t=='section': s.out.append('')
    def handle_endtag(s, t):
        if t in ('style','script','head'): s.skip-=1
        if t in ('div','p','li','section','header','footer','ul'): s.flush()
    def handle_data(s, d):
        if s.skip: return
        s.buf += d
    def flush(s):
        line = re.sub(r'\s+',' ', s.buf).strip()
        if line: s.out.append(line)
        s.buf=''
raw = open(src, encoding='utf-8').read()
raw = re.sub(r'<title>.*?</title>', '', raw, flags=re.S)
p = P(); p.feed(raw); p.flush()
text = '\n'.join(p.out)
text = re.sub(r'\n{3,}', '\n\n', text)
open(dst,'w',encoding='utf-8').write(text.strip()+'\n')
PY

PAGES=$(ls "${BASE}-page-"*.png 2>/dev/null | wc -l | tr -d ' ')
echo "PDF: $OUT  ($(du -h "$OUT" | cut -f1))  ·  pages: $PAGES  ·  ATS: ${BASE}.txt"
