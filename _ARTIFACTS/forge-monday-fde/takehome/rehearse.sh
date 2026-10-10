#!/bin/sh
# Dress rehearsal runner for the Maple Creek take-home. Private helper; lives outside the submission repo.
#   ./rehearse.sh           preflight + free mock run only (no monday calls, no API spend)
#   ./rehearse.sh --live    preflight, then the DEMO.md path on the real boards with the live poller
# Every step is timed and logged to ~/ret-rfp-rehearsal-<time>.log. Stops at the first failure.
set -eu
REPO="${RFP_REPO:-$HOME/ret-rfp-intelligence}"
LIVE=0; [ "${1:-}" = "--live" ] && LIVE=1
LOG="$HOME/ret-rfp-rehearsal-$(date +%Y%m%d-%H%M%S).log"
BOARDS="https://assessment-lab-assignment.monday.com/boards"
POLLER=""

cleanup() { [ -n "$POLLER" ] && kill "$POLLER" 2>/dev/null && echo "poller stopped" | tee -a "$LOG"; return 0; }
trap cleanup EXIT INT TERM

step() {
  name="$1"; shift
  printf '\n== %s ==\n' "$name" | tee -a "$LOG"
  t0=$(date +%s)
  if "$@" >>"$LOG" 2>&1; then
    echo "PASS  $name  ($(( $(date +%s) - t0 ))s)" | tee -a "$LOG"
  else
    echo "FAIL  $name  ($(( $(date +%s) - t0 ))s). See $LOG; fixes in TROUBLESHOOT.md" | tee -a "$LOG"
    exit 1
  fi
}

cd "$REPO"
echo "Rehearsal $(date '+%a %b %d %H:%M'), repo $(git log -1 --format='%h %s' | cut -c1-70), mode $([ $LIVE = 1 ] && echo live || echo mock)" | tee "$LOG"

# 1. Preflight: the same checks ONBOARDING.md asks for.
step "python 3.9+"            python3 -c 'import sys; assert sys.version_info >= (3, 9)'
step "doctor (keys present, never printed)" ./rfp doctor
step "seam tests + regression" ./rfp check

# 2. Free proof: the whole demo path on the mock model and a fake monday.
step "e2e mock x1"            ./rfp e2e --provider mock --runs 1
step "ask (mock)"             ./rfp ask --provider mock "When are proposals due?"

if [ $LIVE = 0 ]; then
  printf "\n%s\n" "Mock rehearsal green. Run with --live for the real boards (about 84 monday calls; check ./rfp doctor for today's count)." | tee -a "$LOG"
  exit 0
fi

# 3. Live: DEMO.md "Before" section, then the poller in the background.
step "reset rehearsal questions" ./rfp reset
step "sync boards"            ./rfp sync
step "re-sync creates 0"      ./rfp sync
./rfp poll --interval 60 --max-idle-min 30 >>"$LOG" 2>&1 &
POLLER=$!
echo "poller running (pid $POLLER), log $LOG" | tee -a "$LOG"
open "$BOARDS/18434901168" "$BOARDS/18434901140" "$BOARDS/18434901212" 2>/dev/null || true

echo "
Now follow DEMO.md minute by minute:
  0-2  Key Facts board            2-4  Solicitations, re-sync shows 0 new
  4-7  add a question on Questions; answer lands within ~60 s
  7-9  'union labor' and 'draft our executive summary' (declined)
  9-15 test bench, answer.py walk, Evidence tab  ->  ./rfp serve in another terminal
Note every stumble. Press Enter when done to run the graded rehearsal check." | tee -a "$LOG"
read _ignored

step "rehearse (step graph)"  ./rfp rehearse --live
printf "\n%s\n" "Done. Send the stumbles plus $LOG to the writer session for the one fix pass." | tee -a "$LOG"
