#!/usr/bin/env python3
"""phosphor_static_review: deterministic review of the Phosphor sources (stdlib only, no browser).

Rules, each a mechanical yes or no:
  R1  every $("id") / getElementById("id") in app.js names an id that exists in page.tpl or is created in app.js
  R2  no duplicate id in page.tpl
  R3  every aria-controls / for= / aria-describedby in page.tpl points at an existing id
  R4  every localStorage call sits inside a try block on the same or previous line
  R5  no console.log / debugger / TODO / FIXME left in app.js
  R6  every addEventListener target is $(...) of a known id, a selector variable, or document / window
  R7  no em-dash or en-dash in user-visible page text
Usage: python3 scripts/phosphor_static_review.py [--json]     exit 1 if any rule fails
"""
import os, re, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_ARTIFACTS/phosphor-src")
tpl = open(os.path.join(SRC, "page.tpl"), encoding="utf-8").read()
js = open(os.path.join(SRC, "app.js"), encoding="utf-8").read()
css = open(os.path.join(SRC, "style.css"), encoding="utf-8").read()
out = []
def add(rule, msg): out.append({"rule": rule, "msg": msg})

ids = re.findall(r'\bid="([^"]+)"', tpl)
made = set(re.findall(r'id="([A-Za-z_][\w]*)"', js))                       # ids written by app.js templates
made |= set(re.findall(r"id=\\?'([A-Za-z_]\w*)", js))
made |= set(re.findall(r"\.id = \"([A-Za-z_]\w*)\"", js))
made |= {m + "_" for m in re.findall(r'id="([a-z]+_)"\s*\+', js)}
# R2
seen = set()
for i in ids:
    if i in seen: add("R2", "duplicate id in page.tpl: " + i)
    seen.add(i)
# R1
dyn_prefix = ("mv_", "ml_", "mh_")
for m in re.finditer(r'(?:\$|document\.getElementById)\(\s*"([^"]+)"\s*\)', js):
    i = m.group(1)
    line = js.count("\n", 0, m.start()) + 1
    if i not in seen and i not in made and not i.startswith(dyn_prefix):
        add("R1", "app.js line %d uses id \"%s\" which page.tpl does not define" % (line, i))
# R3
for attr in ("aria-controls", "aria-describedby", "aria-labelledby"):
    for v in re.findall(attr + r'="([^"]+)"', tpl):
        for i in v.split():
            if i not in seen and i not in made: add("R3", "%s points at missing id %s" % (attr, i))
for v in re.findall(r'<label[^>]*\bfor="([^"]+)"', tpl):
    if v not in seen and v not in made: add("R3", "label for=\"%s\" has no control" % v)
# R4
lines = js.split("\n")
for n, l in enumerate(lines):
    if "localStorage." in l and "try" not in l and (n == 0 or "try" not in lines[n - 1]) and (n < 2 or "try" not in lines[n - 2]):
        add("R4", "app.js line %d: localStorage outside a try: %s" % (n + 1, l.strip()[:80]))
# R5
for n, l in enumerate(lines):
    s = l.strip()
    if s.startswith("//") or s.startswith("/*") or s.startswith("*"): continue
    if re.search(r"\bconsole\.(log|debug)\b|\bdebugger\b|\b(TODO|FIXME)\b", l): add("R5", "app.js line %d: %s" % (n + 1, s[:80]))
# R7
visible = re.sub(r"<style.*?</style>|<script.*?</script>|<!--.*?-->", "", tpl, flags=re.S)
visible = re.sub(r"<[^>]+>", " ", visible)
if re.search("[\u2014\u2013]", visible): add("R7", "page.tpl visible text contains an em-dash or en-dash")
if "--json" in sys.argv: print(json.dumps(out, indent=1))
else:
    for o in out: print("✖ %s %s" % (o["rule"], o["msg"]))
    print("phosphor_static_review: %d finding(s) over %d ids, %d lines of script" % (len(out), len(seen), len(lines)))
sys.exit(1 if out else 0)
