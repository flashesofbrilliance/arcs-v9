#!/usr/bin/env python3
"""Mechanical check for the pre-registered pass line. (a) every bullet is SOURCE, UNVERIFIED or RULE; (b) no UNVERIFIED text is stated as fact; also no em-dashes."""
import re,sys
t=open(__file__.rsplit("/",1)[0]+"/concepts.md").read()
bad=[]
for n,l in enumerate(t.splitlines(),1):
    if not l.startswith("- "): continue
    if l.startswith("- UNVERIFIED:") or l.startswith("- RULE"): continue
    if not re.search(r"Source: https?://\S+ \(read 2026-10-17\)$", l): bad.append((n,"no source/date",l[:70]))
    if re.search(r"unverified|I did not find", l, re.I): bad.append((n,"hedge inside a fact line",l[:70]))
if "—" in t: bad.append((0,"em-dash",""))
print("violations:",len(bad)); [print(b) for b in bad]; sys.exit(1 if bad else 0)
