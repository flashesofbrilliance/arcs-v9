#!/usr/bin/env bash
# Secret leak test: canary in every env var a probe reads; grep all output for it. Pass = 0 occurrences.
cd "$(dirname "$0")"; C=FC_TEST_CANARY_0xDEADBEEF; rm -f /tmp/fc-canary.log; : > /tmp/fc-canary.log
export FC_CUSTODY_KEY=$C FC_NODE_URL=http://$C.invalid FC_FID=$C FC_ACK_THROWAWAY=$C FC_DENY_FIDS=$C
for p in events-probe.mjs write-path-probe.mjs; do
  for f in fixtures/*.json; do node $p --fixture $f >>/tmp/fc-canary.log 2>&1; done
  node $p >>/tmp/fc-canary.log 2>&1   # live path with a bad key must refuse without echoing it
done
n=$(grep -c "$C" /tmp/fc-canary.log); echo "canary occurrences: $n"; [ "$n" = "0" ]
