# Tutorial skeleton (draft, structure only; no step is final until the probes pass on a real node)
Style: vintage terminal game. Each section is a "room" with a prompt, one command, one expected line of output, and an exit. Plain sentences, one idea each, readable at 360px. Facts come from concepts.md with their sources; anything not yet proven on a node is marked TODO-PROVE.

```
ARCS READ NODE  //  you are standing at a blank terminal.
There are three doors. Type the first command to begin.
```

## Room 0: The rules of the house (read before any key exists)
- Use a test account only. Never your main wallet. Never paste a seed phrase into software you have not read. (concepts.md section 7)
- You will create a throwaway account and delegate a signer key to the client. The client never asks for a seed phrase on the command line.
- TODO-PROVE: the exact amount of test funds needed (see concepts.md section 5, price and capacity are in conflict).

## Room 1: Command 1, get a machine
- One command provisions a server (16 GB RAM, 4 CPU, 2 TB disk) and tags it for teardown. (quickstart.sh, dry run first; spending needs the reader's own account.)
- Expected: a server id and a monthly cost estimate printed before anything is created.
- Exit: the teardown command is printed next to the create command.

## Room 2: Command 2, run the node
- One command runs the official Snapchain bootstrap script, pinned to a commit. Read the script first.
- Expected: logs that count down while the node catches up. Sync takes hours. (TODO-PROVE on a real node: how many.)
- Exit: the node answers on port 3381.

## Room 3: Command 3, run the client
- The client reads the feed from your node only. No API keys.
- Expected: a text feed of recent casts, newest at the bottom.
- TODO-PROVE: events probe verdict "proven".

## Room 4: Your key
- Create a throwaway account, then add a delegated signer with a gasless KEY_ADD scoped to the message types the client needs. (concepts.md section 6)
- Expected: the node reports the signer.
- TODO-PROVE: write-path probe verdict "proven".

## Room 5: Post, follow, react
- Three commands, one line of output each. The node relays the message; wait for the merge event before saying it worked.

## Room 6: Hooks (optional)
- A hook is a script that gets one event as JSON on its standard input. Example: print every new cast that mentions you.
- The receipts gate is a hook that checks a claim against its receipt before you sign. It checks that the receipt resolves, is recent, shares keywords and is not by you. It does not judge whether the receipt proves the claim.

## Room 7: Leave no trace
- Run the teardown command, then the verify command, and read an empty result.

## For the second human (the voucher)
- Create your own read node AND your own client by following this page. A quick endorsement is not enough.
- Then post publicly about it on Farcaster, with the repo link.
