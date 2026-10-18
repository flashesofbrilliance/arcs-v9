# Retro sweep of five repos that had no local clone (cloned read-only 2026-10-17)

Method: full clone of each repo into a scratch directory, then the same term list and `git log --all --reverse -i -G` as the 2026-10-15 sweep, then the matching lines were READ by hand because term hits produce false positives. Commit dates are authorship dates. A commit in a private repo discloses nothing by itself; counsel decides what each date means.

| Repo | GitHub today | First commit | Commits | Stars / forks |
|---|---|---|---|---|
| gigi | PUBLIC, created 2026-05-14, last push 2026-05-17 | 2026-03-19 | 870 | 0 / 0 |
| arcs-field-scan | PUBLIC, created 2026-05-04, last push 2026-10-03 | 2026-05-04 | 10 | 0 / 0 |
| arcs-canon | private, created 2026-05-02 | 2026-05-02 | 27 | |
| arcs-field-os | private, created 2026-04-17 | 2026-04-17 | 11 | |
| arcs-immune-system | private, created 2026-05-05 | 2026-05-04 | 9 | |

Both public repos show 0 stars and 0 forks today. Past visibility of every repo is UNVERIFIED (the public ones may have been private earlier; the private ones may have been public earlier).

## Hand classification of the term hits

| Repo | Term hits (first commit) | What the matching text actually is |
|---|---|---|
| gigi (public) | S_min 2026-06-04 (e903556) | FALSE POSITIVE: the substring in a database snapshot-isolation test name (a frontier equal to the minimum). Not the ARCS Law |
| gigi (public) | Y-gate 2026-04-21 (b6dd3cd) | FALSE POSITIVE on the string "holonomy-gated" in a design note. BUT the same note says GIGI's filing covers the geometric database engine and that a claim is "load-bearing on the ICARUS patent claim". It is patent-strategy text in a public repo's history, about a different invention (the geometric database). See FB4 note below |
| gigi (public) | Hypersphere 2026-05-28 (b40eeb5) | FALSE POSITIVE: twelve theory papers using the mathematical hypersphere. Not the ARCS context manifold |
| gigi (public) | Write-lock 2026-03-19 (8ab7858) | FALSE POSITIVE: database write locks in Rust code |
| gigi (public) | Kintsugi, Notomation 2026-05-14 (cf1d8ff) | Concept-level naming in a backlog document (a Kintsugi repair row, a macro-family list). Names only, no mechanism |
| gigi (public) | ARCS Law, ARCS mechanisms at HEAD | None found: zero files contain the formula, Y-gate, orthogonal echo or hypersphere at HEAD |
| arcs-field-scan (public) | Kintsugi (10 files at HEAD), Golden Inchworm (5 files) first 2026-05-04 | REAL, concept and interface level: the report UI renders a "Golden Inchworm" section with the three stages (Red Thread, Golden Thread, Needle) and a Kintsugi section. Names and the 3-stage labels, no formula or code for the mechanism. First commit 2026-05-04, last push 2026-10-03 |
| arcs-canon (private) | Kintsugi, Write-lock, Hypersphere, Inchworm, Notomation 2026-05-02; Orthogonal echo 2026-05-19 | Not read in detail. Private today. Conception evidence for ledger question 5 |
| arcs-field-os (private) | Kintsugi, Write-lock 2026-04-24; Orthogonal echo, Hypersphere, Inchworm, Notomation 2026-05-11; Y-gate 2026-05-26 | Not read in detail. Private today. Conception evidence |
| arcs-immune-system (private) | Notomation 2026-05-04; Kintsugi 2026-10-03 | Not read in detail. Private today |

## What this changes
- **FB6 (a public repo already contains text of a candidate mechanism): CONFIRMED at concept/interface level.** arcs-field-scan renders Golden Inchworm and Kintsugi names and the three stages. gigi does not contain ARCS mechanism text; its hits were generic.
- **Conception evidence is earlier than the arcs-v9 repo:** arcs-field-os (2026-04-17) shows Kintsugi and write-lock text by 2026-04-24 and the orthogonal echo and hypersphere terms by 2026-05-11; arcs-canon shows these terms on 2026-05-02. All private today.
- **FB4 (no patent application ever filed) is now doubtful:** gigi's history says "GIGI's filing". That concerns the geometric database, not the ARCS mechanisms, but it means Zach has patent activity of some kind. Question for Zach: what was filed for GIGI or ICARUS, when, and does any of it overlap the ARCS mechanisms?
- **Tool caveat (kintsugi KF11):** the sweep's term patterns match substrings and other meanings (S_min in a test name, "holonomy-gated" as Y-gate, database write-locks, mathematical hypersphere). Four of the six gigi hits were false positives. The patterns need word-boundary-aware matching before the sweep output is trusted without reading; macOS regex lacks `\b`, so the fix needs `[[:<:]]` or a Python-side filter. Also a label bug: the table renderer names any clone under a path containing "worktrees" as the arcs-v9 worktree.
