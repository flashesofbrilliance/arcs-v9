#!/bin/sh
# Maple Creek launcher. Double-click in Finder (or drag to the Dock). Private helper; not part of the submission.
# Starts the deck server if it isn't running, opens the deck in its own browser window,
# then offers a mock or live rehearsal. Closing this window stops the server it started.
REPO="${RFP_REPO:-$HOME/ret-rfp-intelligence}"
HERE="$(cd "$(dirname "$0")" && pwd)"
URL="http://127.0.0.1:8765"
SERVER=""

stop() { [ -n "$SERVER" ] && kill "$SERVER" 2>/dev/null && echo "Deck server stopped."; }
trap stop EXIT INT TERM

cd "$REPO" || { echo "Repo not found at $REPO"; read _; exit 1; }
clear
echo "Maple Creek  ·  $(git log -1 --format='%h %s' | cut -c1-60)"
echo "Release candidates: $(git tag -l 'rc*' | tr '\n' ' ')"
echo

code=$(curl -s -o /dev/null -w '%{http_code}' "$URL/deck")
if [ "$code" = "200" ]; then
  echo "Deck server already running at $URL"
else
  old=$(lsof -tiTCP:8765 -sTCP:LISTEN 2>/dev/null)
  [ -n "$old" ] && { echo "Restarting an out-of-date deck server (pid $old)"; kill $old; sleep 1; }
  ./rfp serve >/tmp/maple-creek-serve.log 2>&1 &
  SERVER=$!
  for i in 1 2 3 4 5 6 7 8 9 10; do curl -s -o /dev/null "$URL/api/state" && break; sleep 0.5; done
  echo "Deck server started at $URL (log: /tmp/maple-creek-serve.log)"
fi

# Own window: Chrome app mode if installed, otherwise the default browser.
if [ -d "/Applications/Google Chrome.app" ]; then
  open -na "Google Chrome" --args --app="$URL/deck" --new-window
else
  open "$URL/deck"
fi

while :; do
  echo
  echo "  1  Mock rehearsal (free, no monday calls)"
  echo "  2  Live rehearsal (real boards, ~84 monday calls)"
  echo "  3  Doctor (keys, calls left today)"
  echo "  4  Reopen the deck"
  echo "  q  Quit (stops the server this window started)"
  printf "Choose: "; read c
  case "$c" in
    1) sh "$HERE/rehearse.sh" ;;
    2) sh "$HERE/rehearse.sh" --live ;;
    3) ./rfp doctor ;;
    4) open "$URL/deck" ;;
    q|Q) exit 0 ;;
    *) echo "Type 1, 2, 3, 4 or q." ;;
  esac
done
