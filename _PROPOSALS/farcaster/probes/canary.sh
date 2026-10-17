#!/usr/bin/env bash
# Secret leak test: canary in every env var a probe reads; grep all output for it. Pass = 0 occurrences.
cd "$(dirname "$0")"; C=FC_TEST_CANARY_0xDEADBEEF; LOG=$(mktemp); trap "rm -f $LOG" EXIT
export FC_CUSTODY_KEY=$C FC_NODE_URL=http://$C.invalid FC_FID=$C FC_ACK_THROWAWAY=$C FC_DENY_FIDS=$C
for p in events-probe.mjs write-path-probe.mjs; do
  for f in fixtures/*.json; do node $p --fixture $f >>$LOG 2>&1; [ $? -le 11 ] || { echo "probe crashed"; exit 1; }; done
  node $p >>$LOG 2>&1   # live path with a bad key must refuse without echoing it
done
command -v node >/dev/null || { echo "node missing: canary test cannot run"; exit 1; }
# positive control: the grep must catch a planted canary
echo "$C" > $LOG.ctl; [ "$(grep -c "$C" $LOG.ctl)" = 1 ] || { echo "control failed"; exit 1; }; rm -f $LOG.ctl
n=$(grep -c "$C" $LOG); echo "canary occurrences: $n"; [ "$n" = "0" ]
