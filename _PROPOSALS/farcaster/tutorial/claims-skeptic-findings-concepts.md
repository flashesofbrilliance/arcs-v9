<!-- Verbatim text returned by the claims-skeptic agent for concepts.md v1, 2026-10-17. Unedited. Author's summary: claims-skeptic-findings-concepts-summary.md -->
**Scope.** I fetched every cited URL. The five Snapchain repo files came from raw.githubusercontent.com at commit fc87f268 (the full SHA used in the file's links). The two docs.farcaster.xyz pages came directly. I read them in full. `check_concepts.py` reports 0 violations, and the file has no em-dashes or en-dashes.

## Findings, ranked

**HIGH-1. Lines 46-47 are false as worded and contradict the file's own citations.**
- The `messages` page cited at lines 18, 19, 24, 25 and 42-44 states the price and limits directly. It says: "A unit of storage costs $7 today, lasts for one year". It lists the limits as 5000 Casts, 2500 Reactions, 2500 Links, 50 Profile Data and 50 Verifications.
- Line 47 says "I found no primary page for it." That is false, because a primary page exists and is already cited in the file.
- Line 46 says the price and limits are unverified because storage pages returned 404. The unit price and per-unit limits are on a page the draft cites.
- The data is not simply usable, though. The Snapchain `storagelimits.md` sample shows Casts limit 77000, Links 38500 and Reactions 38500. That is far from 5000, 2500 and 2500, so the docs page is likely stale.
- The correct state is a conflict between two sources, with a $7/5000 figure that may be outdated. Neither is a clean UNVERIFIED nor a clean fact.
- This does not break the pre-registered pass line, since a wrongly-UNVERIFIED line is not stated as fact. It is a draft accuracy defect that would mislead the reader.

**MEDIUM-1. Line 9 is unsupported.**
- "Every account you use on Farcaster is one FID." The accounts page says only that IdGateway "will assign a new Farcaster ID or fid to your Ethereum address." Nothing in it says every account is one FID.
- This is a sentence stated as fact that goes beyond its source. It fails pass line (b)'s spirit.

**MEDIUM-2. Line 42 overreaches.**
- "Your account must have paid for storage to publish."
- The messages page says an account "must pay rent to keep their messages", and that a lapsed unit may lose messages. It does not say payment is required to publish.
- The "so you can publish messages" wording is in writing-messages.mdx, a different source from the one cited.

**MEDIUM-3. Line 24 is partly beyond the source.**
- "A valid message must be signed by an authorized account key, and the account must have paid for storage."
- The messages page says messages are signed with a key and that accounts pay rent. It has no validity rule joining the two. The "valid only if" framing is the draft's inference.

**MEDIUM-4. Line 26 generalizes a read-node rule.**
- "A node that accepts a message checks that it is valid and not already merged."
- node-types.mdx says "valid and not already merged" only in the read-node bullet. For both roles it says only "routes… validates it against that shard's state."
- The "not already merged" part is read-node only as worded in the source.

**LOW-1. Line 23, "basic unit of change".**
- The messages page says nothing like it in the body. The only match is the Resources link text "Messages - the atomic unit of change." That is "atomic", not "basic".
- The list of five message types is correct.

**LOW-2. Line 4 contains unsourced factual claims.**
- "The Snapchain docs site is built from the files in the snapchain repo." This is a fact with no URL and no date. It is not covered by the pass-line check.
- The file's own preregistration only says "the Snapchain site source lives in github.com/farcasterxyz/snapchain/site", so the claim has a basis there, but it is not cited in concepts.md.

**LOW-3. Wording drift.**
- Line 14 says the custody address "pays for the account registration and storage." The source says it "funds the initial id registration and storage" and uses "pays" only for the ~$10.
- Line 44 says "before messages are lost." The source says the account "may lose all its messages" and "must renew or lose".
- Line 34 adds a "so" that makes the source's separate statements a causal chain. It is minor.

**LOW-4. Sentences too long for 360px.**
- Counts below are words before "Source:".
- Line 4 is 38 words. Line 46 is 38 words. Line 64 is 32 words. Line 35 is 30 words. Line 53 is 29 words. Line 63 is 29 words.
- Line 35, which has two clauses, should be split.

## Verified as supported
These lines match their cited sources as worded:
- Lines 8, 15-19.
- Line 25: 15-minute rule.
- Lines 27, 28 and 33.
- Lines 35-38: includes 16 GB, 4 cores, 2 TB and ports 3381-3383.
- Lines 43, 45 and 48.
- Lines 52-58: gasless keys.
- Line 62.

## Could not verify
- The rendered snapchain.farcaster.xyz pages. The draft says it did not load them either, and I read only the repo files.
- Line 66, the contest author's seed-phrase wording. The draft itself says it is second-hand.
- Line 29, the merge rules, which the draft marks UNVERIFIED. I did not read the protocol spec, so that is still unverified.
- Line 10, FID cost. I did not find a price on the accounts page, which agrees with the draft. The $10 on line 48 is a funding figure for registration plus storage, not an FID price.
- Whether docs.farcaster.xyz now carries the 77000-style limits. A live fetch returned the older 5000 numbers, so which is current needs the Storage Registry or `storageLimitsByFid` on a live node.

**Safe to rely on?** Mostly, with fixes. About 85% of sourced lines are supported. Lines 9, 24, 26 and 42 overreach, and lines 46-47 wrongly deny that a primary page exists. The pass line as written is mechanically met, and the adversarial review above finds that it is not substantively met until those lines are fixed.

Files:
- /Users/zharris/arcs-v9/.claude/worktrees/fc-cli-loop2-d953c2/_PROPOSALS/farcaster/tutorial/concepts.md
- /Users/zharris/arcs-v9/.claude/worktrees/fc-cli-loop2-d953c2/_PROPOSALS/farcaster/tutorial/preregistration-concepts.md
