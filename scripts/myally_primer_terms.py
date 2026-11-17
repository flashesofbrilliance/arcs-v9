#!/usr/bin/env python3
"""myally_primer_terms.py: keep the My Ally Primer's glossary, its hover definitions and the hub's copy in step.

Idempotent. Each run:
  1. adds any glossary entry in NEW_ENTRIES that public/myally-primer.html lacks (by id), in its group;
  2. removes every hover definition this script made before (marked data-gen="terms"), then wraps the
     first use of each term in TERMS inside every other entry's definition with the Primer's own
     hover pattern (.termwrap > a.gl + .tip, wired by the script already in the page). The popup text
     is the target entry's plain meaning, read from the glossary itself, so there is one source;
  3. rebuilds the Primer copy embedded in public/myally-hub.html (iframe srcdoc) from the file, keeping
     the hub's own style and script block that sits before </body>;
  4. writes the same definitions into the hub's /*GLOSS:BEGIN*/.../*GLOSS:END*/ block, so the Step 1
     tab's details panel shows the Primer's meanings on hover (one source).

  python3 scripts/myally_primer_terms.py          # write
  python3 scripts/myally_primer_terms.py --check  # read-only; exit 1 if a run would change anything

Stdlib only. Writes only public/myally-primer.html and public/myally-hub.html.
"""
import html, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIMER = os.path.join(ROOT, "public", "myally-primer.html")
HUB = os.path.join(ROOT, "public", "myally-hub.html")
HUB_BLOCK = "<script>(function(){var d=document.documentElement,M={"  # start of the hub's block in the embed

# Entries the Step 1 tab and the agreement use that the Primer did not define (sweep 2026-11-08).
# (group heading id, entry id to insert after or None for the end, id, term, meaning, picture, why)
NEW_ENTRIES = [
    ("g-grp-keeping-the-build-safe", None, "g-github", "GitHub",
     "An online home for your app's code that keeps every version of it.",
     "A filing cabinet that remembers every draft.",
     "Your code lives in your own account, so it stays yours whoever works on it."),
    ("g-grp-keeping-the-build-safe", None, "g-ci-cd", "CI/CD",
     "Automatic checks and releases: each change is tested, then put live, without anyone doing it by hand.",
     "A spell-check and a print run that start on their own.",
     "It belongs to Steps 2 and 3, not Step 1."),
    ("g-grp-who-can-see-what", None, "g-database-rules", "Database rules",
     "The settings that decide who may read or change each piece of stored information.",
     "The lock on each drawer of the filing cabinet.",
     "The Step 1 data check reads these."),
    ("g-grp-who-can-see-what", None, "g-data-separation", "Data separation",
     "Making sure one family can never see another family's information.",
     "Separate lockers, each with its own key.",
     "It is what the Step 1 data check looks for, before any real family uses the app."),
    ("g-grp-the-legal-alphabet-for-your-lawyers-not-for-me", "g-coppa", "g-ferpa", "FERPA",
     "United States federal rules about student education records.",
     None,
     "Whether it applies to My Ally LD is for your lawyers."),
    ("g-grp-working-together", None, "g-prototype", "Prototype",
     "A working early version, made to test an idea with real people rather than to run at full scale.",
     "A model home before the street is built.",
     "Step 3 builds one to test with families."),
    ("g-grp-working-together", None, "g-readout", "Readout",
     "The meeting where I walk you through what I found.",
     "The debrief after a survey.",
     "Step 1 ends with one, then you decide on Step 2."),
    ("g-grp-working-together", None, "g-round-of-changes", "Round of changes",
     "One pass where you tell me what to change in something I delivered, and I change it.",
     "One set of edits on a draft.",
     "Step 1 includes one."),
    ("g-grp-working-together", None, "g-office-hours", "Office hours",
     "Time with me, one to one, booked in 30-minute slots, for any question.",
     "A standing appointment you can use or skip.",
     "4 hours of office hours a month come at no charge, to use however you like."),
    # Step 1 tab sweep (2026-11-09): words on the tab a founder or counsel may not know. Meanings follow the
    # Step 1 agreement's glossary (legal/step1-agreement-rev29.md) where it defines the word.
    ("g-grp-the-building-blocks", "g-lovable-and-supabase", "g-remix", "Remix",
     "Lovable's name for a copy of a project. Changes to the copy don't touch the original.",
     "A photocopy you can write on.",
     "I read a remix with no real family information in it, so your app stays as it is."),
    ("g-grp-the-building-blocks", None, "g-stub", "Stub",
     "A placeholder in the code: a screen or feature that looks built but does not do its job yet.",
     "A door painted on a wall.",
     "The Step 1 map of your spec marks each part as built, stubbed or missing."),
    ("g-grp-who-can-see-what", None, "g-data-governance-plan", "Data governance plan",
     "A written plan for family information: keeping each family's data apart, who can see what, consent, and what to keep out of the app.",
     "House rules for the filing cabinet.",
     "Pilot schools and families are likely to ask for one; your counsel confirms the answers."),
    ("g-grp-working-together", None, "g-working-day", "Working day",
     "Monday to Friday, not counting US federal holidays.",
     "A business day at the bank.",
     "Step 1's five days are counted this way."),
    ("g-grp-working-together", None, "g-spec", "Spec",
     "Your written description of what the app should do. Here, your integration spec.",
     "The brief a campaign is built from.",
     "I read the code against it, to see what is built, stubbed or missing."),
    ("g-grp-working-together", None, "g-review-call", "Review call",
     "A 30-minute call where we go through your batched comments together.",
     "Going through a marked-up draft side by side.",
     "It is part of Step 1, so it doesn't use your office hours."),
    ("g-grp-working-together", None, "g-deliverables", "Deliverables",
     "The written items I hand you, numbered 1 to 6 in section 2 of the Step 1 agreement.",
     None,
     "Your one round of changes applies to these."),
    ("g-grp-working-together", None, "g-design-system", "Design system",
     "A shared set of screen parts, such as buttons, cards and colours, with rules for using them.",
     "A brand kit for screens.",
     "Step 2 turns your existing screens into one, so new screens match."),
    ("g-grp-decisions-and-honesty", None, "g-go-or-stop-memo", "Go or stop memo",
     "A short written verdict on whether what is built can carry a pilot safely, with a ranked list of the problems to fix first.",
     "A surveyor's report before you buy.",
     "Step 1 ends with one, so you decide on Step 2 with it in hand."),
]

# entry id -> phrases that point to it (case-insensitive, whole words). Only clear jargon, not everyday words.
TERMS = {
    "g-ai-model": ["AI model"], "g-lovable-and-supabase": ["Supabase", "Lovable"], "g-api": ["API"],
    "g-token": ["token", "tokens"], "g-prompt": ["prompt", "prompts"], "g-database": ["database"],
    "g-back-end": ["back end"], "g-front-end": ["front end"], "g-lock-in": ["lock-in"],
    "g-retrieval": ["retrieval"], "g-hallucination": ["hallucination"], "g-redaction": ["redaction"],
    "g-version-control-branch": ["version control", "branch"], "g-environment-testing-live": ["environment", "environments"],
    "g-data-placement": ["data placement"], "g-evidence-trail": ["evidence trail"],
    "g-role-based-access": ["role-based access"], "g-audit-log": ["audit log"], "g-retention": ["retention"],
    "g-synthetic-data": ["synthetic data"], "g-hipaa": ["HIPAA"], "g-coppa": ["COPPA"], "g-ferpa": ["FERPA"],
    "g-baa": ["BAA"], "g-nda": ["NDA"], "g-cost-model": ["cost model"], "g-sprint": ["sprint"],
    "g-dependency": ["dependency"], "g-backlog": ["backlog"], "g-definition-of-done": ["definition of done"],
    "g-checkpoint": ["checkpoint"], "g-handoff-pack": ["handoff pack", "handoff"], "g-unit-economics": ["unit economics"],
    "g-github": ["GitHub"], "g-ci-cd": ["CI/CD"], "g-database-rules": ["database rules"],
    "g-data-separation": ["data separation", "kept apart"], "g-prototype": ["prototype"],
    "g-readout": ["readout"], "g-round-of-changes": ["round of changes"], "g-office-hours": ["office hours"],
    "g-remix": ["remix"], "g-stub": ["stubbed", "stub"], "g-data-governance-plan": ["data governance plan", "governance plan"],
    "g-working-day": ["working days", "working day"], "g-spec": ["integration spec", "spec"], "g-review-call": ["review call", "review calls"],
    "g-deliverables": ["deliverables"], "g-design-system": ["design system"], "g-go-or-stop-memo": ["go or stop memo"],
    # The rest of the Primer (2026-11-12): every entry gets hover text, so no Primer term is left without one.
    "g-vendor-provider": ["vendor", "vendors", "provider", "providers"], "g-usage-cap": ["usage cap", "usage caps"],
    "g-model-version-freezing-it": ["model version", "freezing"], "g-backup-and-restore-test": ["restore test", "backup"],
    "g-re-platforming": ["re-platforming", "re-platform"], "g-second-check-at-login": ["second check at login"],
    "g-accessibility-standard": ["accessibility standard", "accessibility"], "g-scope": ["scope"],
    "g-roadmap": ["roadmap"], "g-first-release-thin-path": ["thin path", "first release"],
    "g-trial-run-spike": ["trial run", "spike"], "g-fixed-grows-with-use-hidden-costs": ["hidden costs", "grows with use"],
    "g-best-likely-worst-case": ["worst case", "best case", "likely case"], "g-decision-record": ["decision record", "decision records"],
    "g-imagine-it-failed-exercise": ["imagine it failed"], "g-looking-back": ["looking back"],
    "g-predict-first-check-later": ["predict first"], "g-fact-check": ["fact-check", "fact check"],
    "g-shared-documents-versus-shared-understanding": ["shared understanding"],
}

GEN = re.compile(r'<span class="termwrap" data-gen="terms"><a [^>]*>(.*?)</a><span class="tip".*?<span class="tiphint">[^<]*</span></span></span>', re.S)
ENTRY = re.compile(r'<div id="(g-[a-z0-9-]+)"><dt>(.*?)</dt><dd>(.*?)</dd></div>', re.S)


def entry_html(eid, term, meaning, pic, why):
    p = f' <span class="pic">Picture: {html.escape(pic)}</span>' if pic else ""
    return (f'<div id="{eid}"><dt>{html.escape(term)}</dt><dd>{html.escape(meaning)}{p} '
            f'<span class="why">Why it matters: {html.escape(why)}</span></dd></div>')


def add_entries(s):
    for grp, after, eid, term, meaning, pic, why in NEW_ENTRIES:
        if f'<div id="{eid}">' in s:
            continue
        new = entry_html(eid, term, meaning, pic, why)
        if after and f'<div id="{after}">' in s:
            i = s.index(f'<div id="{after}">')
            j = s.index("</div>", s.index("</dd>", i)) + len("</div>")
            s = s[:j] + new + s[j:]
            continue
        h = s.index(f'<h2 id="{grp}">')
        end = s.index("</dl>", h)
        s = s[:end] + new + s[end:]
    return s


def meanings(s):
    out = {}
    for m in ENTRY.finditer(s):
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(3)))
        out[m.group(1)] = (html.unescape(re.sub(r"<[^>]+>", "", m.group(2))), re.split(r" Picture:| Why it matters:| In the proposal:", text)[0].strip())
    return out


def tip_html(gid, shown, mean):
    term, defn = mean[gid]
    return (f'<span class="termwrap" data-gen="terms"><a class="gl" href="#{gid}" aria-expanded="false">{shown}</a>'
            f'<span class="tip" role="tooltip" hidden><b>{html.escape(term)}</b>{html.escape(defn)}'
            f'<span class="tipbar"><a class="tipgo" href="#{gid}">Full entry</a><button type="button" class="tipclose">Close</button></span>'
            f'<span class="tiphint">Click to keep it open.</span></span></span>')


def wrap_dd(dd, own, mean):
    """Wrap the first use of each other entry's term in this definition. Text inside links is left alone."""
    tips, done = [], set()
    parts = re.split(r"(<[^>]+>)", dd)
    in_a = 0
    for k, part in enumerate(parts):
        if part.startswith("<"):
            in_a += 1 if re.match(r"<a[\s>]", part) else -1 if part.startswith("</a") else 0
            continue
        if in_a:
            continue
        for gid, phrases in TERMS.items():
            if gid == own or gid in done or gid not in mean:
                continue
            for ph in phrases:
                m = re.search(r"(?<![\w/-])" + re.escape(ph) + r"(?![\w/-])", part, re.I)
                if m:
                    tips.append(tip_html(gid, m.group(0), mean))
                    part = part[:m.start()] + f"\x00{len(tips) - 1}\x00" + part[m.end():]
                    done.add(gid)
                    break
        parts[k] = part
    out = "".join(parts)
    return re.sub(r"\x00(\d+)\x00", lambda x: tips[int(x.group(1))], out)


def primer_text(s):
    s = GEN.sub(r"\1", s)            # forget earlier runs
    s = add_entries(s)
    mean = meanings(s)
    def one(m):
        return f'<div id="{m.group(1)}"><dt>{m.group(2)}</dt><dd>{wrap_dd(m.group(3), m.group(1), mean)}</dd></div>'
    return ENTRY.sub(one, s)


def gloss_json(primer):
    import json
    mean = meanings(primer)
    g = {gid: {"t": mean[gid][0], "d": mean[gid][1], "p": ph} for gid, ph in TERMS.items() if gid in mean}
    return json.dumps(g, ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("</", "<\\/")


def hub_text(hub, primer):
    pat = re.compile(r"/\*GLOSS:BEGIN\*/.*?/\*GLOSS:END\*/", re.S)
    if len(pat.findall(hub)) != 1:
        sys.exit("myally_primer_terms: expected one /*GLOSS:BEGIN*/ block in the hub")
    hub = pat.sub(lambda _: "/*GLOSS:BEGIN*/" + gloss_json(primer) + "/*GLOSS:END*/", hub)
    m = re.search(r'(<iframe title="Primer" srcdoc=")([^"]*)(")', hub)
    doc = html.unescape(m.group(2))
    i = doc.index(HUB_BLOCK)
    block = doc[i:doc.rindex("</body>")]
    # The hub's click catcher for in-page # links must leave definition terms (a.gl) to the Primer's own
    # popup script; otherwise a tap on a phone never opens a definition (found by myally_hub_crawl.py).
    catch = "var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;"
    block = block.replace(catch, "var a=e.target.closest&&e.target.closest('a[href]');if(!a||a.classList.contains('gl'))return;")
    body = primer.replace("—", "-")    # the embed has always carried hyphens for the two token-comment dashes
    # Inside the hub the Primer's own top bar (wordmark, MNDA button, theme toggle, menu) duplicates the hub's
    # chrome and its MNDA link leads to a locked tab (Zach, 2026-11-09). Hide it in the embed only, and zero the
    # sticky-header offset it sets, so in-page jumps still land right.
    embed_css = '<style data-embed="hub">header.top{display:none!important}html{--hdr:0px!important}</style>'
    body = body.replace("</head>", embed_css + "</head>", 1)
    new = body[:body.rindex("</body>")] + block + body[body.rindex("</body>"):]
    return hub[:m.start(2)] + html.escape(new, quote=True) + hub[m.end(2):]


def main():
    p_old = open(PRIMER, encoding="utf-8").read()
    h_old = open(HUB, encoding="utf-8").read()
    p_new = primer_text(p_old)
    h_new = hub_text(h_old, p_new)
    untipped = [gid for gid in meanings(p_new) if gid not in TERMS]
    if untipped:
        print("myally_primer_terms: Primer entries with no hover phrases in TERMS: " + ", ".join(untipped), file=sys.stderr)
        return 1
    if "--check" in sys.argv:
        stale = [n for n, a, b in (("public/myally-primer.html", p_old, p_new), ("public/myally-hub.html", h_old, h_new)) if a != b]
        if stale:
            print("myally_primer_terms --check: stale: " + ", ".join(stale) + "; run scripts/myally_primer_terms.py", file=sys.stderr)
            return 1
        print("myally_primer_terms --check: fresh")
        return 0
    n = len(GEN.findall(p_new))
    if p_new != p_old:
        open(PRIMER, "w", encoding="utf-8").write(p_new)
    if h_new != h_old:
        open(HUB, "w", encoding="utf-8").write(h_new)
    print(f"myally_primer_terms: {n} hover definitions; primer {'written' if p_new != p_old else 'unchanged'}, hub {'written' if h_new != h_old else 'unchanged'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
