#!/bin/sh
# phosphor_suite.sh: run every Phosphor check ONE process at a time against the built page, N rounds (default 1), and print a flake ledger:
# any check whose result changed between rounds. Excludes the five known-failing or fixture-hungry checks (slice, twin, sing, gold, fx) unless --all.
# Usage: sh scripts/phosphor_suite.sh [rounds] [--all]    (PHOSPHOR_BROWSER=webkit or firefox runs the same checks on that engine)    Fixtures: /private/tmp/claude-501/fx (python3 scripts/beat_truth_tracks.py <dir> to regenerate)
ROUNDS=${1:-1}; NODEOPT=""; [ -n "$PHOSPHOR_BROWSER" ] && NODEOPT="--import ./scripts/lib/phosphor_engine.mjs"; PAGE=_ARTIFACTS/phosphor.html; FX=/private/tmp/claude-501/fx; OUT=${TMPDIR:-/tmp}/phosphor_suite.$$; mkdir -p "$OUT"
[ -f "$FX/break-100.wav" ] || python3 scripts/beat_truth_tracks.py "$FX" >/dev/null 2>&1
r=1
while [ "$r" -le "$ROUNDS" ]; do
  : > "$OUT/round$r.txt"
  for s in scripts/phosphor_check.mjs scripts/phosphor_*_check.mjs; do
    n=$(basename "$s" .mjs)
    case "$n" in phosphor_slice_check|phosphor_twin_check|phosphor_sing_check|phosphor_gold_check|phosphor_fx_check) [ "$3" = "--all" ] || [ "$2" = "--all" ] || continue;; esac
    case "$n" in
      phosphor_mixer_check) E="$FX/break-100.wav,$FX/break-120.wav";;
      phosphor_bars_check|phosphor_dock_check|phosphor_gate_check|phosphor_glitchoff_check|phosphor_pins_check|phosphor_flash_check|phosphor_mix_check|phosphor_zoomrow_check|phosphor_font_check|phosphor_playlog_check|phosphor_recipe_check|phosphor_pads_check|phosphor_hidden_check|phosphor_kidcap_check|phosphor_render_check|phosphor_grab_check) E="$FX/break-100.wav";;
      *) E="";;
    esac
    PHOSPHOR_FILES=$E node $NODEOPT "$s" "$PAGE" >"$OUT/$n.r$r.txt" 2>&1; echo "$n $?" >> "$OUT/round$r.txt"
  done
  echo "round $r: $(grep -c ' 0$' "$OUT/round$r.txt") pass, $(grep -vc ' 0$' "$OUT/round$r.txt") fail"; grep -v ' 0$' "$OUT/round$r.txt" | sed 's/^/  FAIL /'
  r=$((r+1))
done
if [ "$ROUNDS" -gt 1 ]; then
  echo "flake ledger (checks whose result changed between rounds):"; cat "$OUT"/round*.txt | sort | uniq -c | awk '{print $2" "$3" x"$1}' | sort | awk '{c[$1]++; l[$1]=l[$1]" "$2"x"$3} END {for (k in c) if (c[k]>1) print "  "k":"l[k]}' | sort
fi
echo "details in $OUT"
