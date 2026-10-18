#!/usr/bin/env bash
# Offline tests for the poller and feed. Prints one line per test and a total.
cd "$(dirname "$0")"; P=0; T=0; C=FC_TEST_CANARY_0xDEADBEEF
t() { T=$((T+1)); if [ "$2" = 0 ]; then P=$((P+1)); echo "ok   $1"; else echo "FAIL $1"; fi; }
rm -f /tmp/fc-client-cur.json
out=$(node poller.mjs --fixture-dir fixtures --cursor /tmp/fc-client-cur.json); echo "$out" | grep -q '"delivered":5'; t "first run delivers 5 events" $?
out=$(node poller.mjs --fixture-dir fixtures --cursor /tmp/fc-client-cur.json); echo "$out" | grep -q '"delivered":0'; t "restart from saved cursor delivers 0 (no duplicates)" $?
node feed.mjs fixtures | grep -q "third cast after a block jump"; t "feed shows casts across a block jump" $?
rm -f /tmp/fc-client-cur.json; node poller.mjs --fixture-dir fixtures --cursor /tmp/fc-client-cur.json --hook hooks/print-mentions.sh | grep -q "HOOK cast fid 333"; t "hook receives one event as JSON on stdin" $?
K=0x$(printf "ab%.0s" $(seq 1 32)); node poller.mjs --fixture-dir fixtures --cursor $K >/dev/null 2>&1; [ $? = 2 ]; t "key-shaped value (0x + 64 hex) for an allowed flag is refused" $?
node poller.mjs --key $C >/tmp/fc-client-out.txt 2>&1; rc=$?; [ $rc = 2 ] && ! grep -q "$C" /tmp/fc-client-out.txt; t "canary in argv refused and not echoed" $?
grep -q "$C" /tmp/fc-client-cur.json; [ $? -ne 0 ]; t "cursor file holds no canary" $?
echo "client tests $P/$T"; [ $P = $T ]
