#!/usr/bin/env python3
"""essay_atlas: cluster the NFTT + TIL corpus with Operator 20's own DBSCAN, and test the
hand-sorted LinkedIn shows against it.

Why: the five shows (Primary Source, Receipts, Rogue Operator, Notomation, Reader) were sorted by
title only. This is the falsifier. If the text-derived clusters disagree, re-sort before building
more hub pages.

Method (stdlib only, no new deps):
  text      rendered body text of each essay (script/style/tags stripped)
  vectors   TF-IDF over word tokens; terms in > MAX_DF of docs are dropped, which removes the
            shared template chrome (memory: template-aliasing-shared-boilerplate-fakes-cross-domain-echo)
  distance  cosine distance
  cluster   operators/arcs_operator20.DBSCAN, unchanged. Its fit() only calls seed.distance(),
            so an essay seed with a cosine distance is a faithful duck-typed input.
  control   pair agreement of the hand sort vs the clusters, compared with the same score for
            200 shuffles of the hand labels. Agreement inside the shuffle band means no signal.
Lexical, not semantic: TF-IDF sees shared vocabulary, not shared ideas. Treat it as a tripwire.

Usage: python3 scripts/essay_atlas.py [--eps 0.80] [--min 2] [--sweep] [--json out.json]
       python3 scripts/essay_atlas.py --bundles [--json out.json]   # Op 21 fills each show
"""
import glob, html, json, math, os, random, re, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "operators"))
from arcs_operator20 import DBSCAN  # noqa: E402

MAX_DF = 0.5
SKIP = re.compile(r"index|loop-hud|recon-report-(cold-1|warm)|post-1-(brief|exec)|dossier")
HAND = {  # the title-only sort from the session, slug -> show
    "til-apple-openai": "Primary Source", "til-zim": "Primary Source",
    "nftt-tuning-into-the-distortion-field": "Primary Source", "nftt-take-home-trap": "Primary Source",
    "nftt-closing-the-loop-receipts": "Receipts", "nftt-four-dates-one-thesis-three-confirmations": "Receipts",
    "nftt-the-pre-mortem-that-asked-to-be-wrong": "Receipts", "nftt-probably-confirmation-bias": "Receipts",
    "til-closing-the-loop": "Receipts", "nftt-the-loop-closes": "Receipts",
    "nftt-recon-report-cold-2": "Rogue Operator", "nftt-receipts-or-it-didnt-happen": "Rogue Operator",
    "nftt-the-question-that-found-the-outage": "Rogue Operator", "nftt-confirmed-not-my-bug": "Rogue Operator",
    "nftt-the-lock-that-was-already-there": "Rogue Operator",
    "nftt-notomation": "Notomation", "nftt-ledger-not-story": "Notomation", "nftt-cheapest-edit-is-a-diff": "Notomation",
    "nftt-second-pass": "Notomation", "nftt-a-draft-is-not-a-verb": "Notomation", "til-a-draft-is-not-a-verb": "Notomation",
    "nftt-schematic-scaffolds": "Notomation",
    "nftt-post-1": "Reader", "nftt-post-2": "Reader", "nftt-post-3": "Reader", "nftt-post-4": "Reader",
    "nftt-the-cold-reconstruction": "Reader", "nftt-the-control-and-the-experiment": "Reader",
    "nftt-the-instinct-before-it-had-a-name": "Reader", "nftt-pulp-governance": "Reader",
}
STOP = set("""a an the and or but if of to in on at for with by from as is are was were be been being it its this that
these those i me my we our you your he she they them their not no so than then there here what which who whom when where
why how all any each few more most other some such only own same too very can will just should now do does did done have
has had having into over under again further once also one two three would could about after before because while""".split())


def body_text(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    t = re.sub(r"(?s)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def tokens(s):
    return [w for w in re.findall(r"[a-z][a-z'-]{2,}", s.lower()) if w not in STOP]


class EssaySeed:
    def __init__(self, slug, vec):
        self.slug, self.vec = slug, vec

    def distance(self, other):
        dot = sum(v * other.vec.get(k, 0.0) for k, v in self.vec.items())
        return 1.0 - dot  # vectors are L2-normalised


def load():
    docs = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "public", "blog-*.html"))):
        slug = os.path.basename(p)[5:-5]
        if not SKIP.search(slug):
            docs[slug] = tokens(body_text(p))
    n = len(docs)
    df = collections.Counter(w for toks in docs.values() for w in set(toks))
    seeds = []
    for slug, toks in docs.items():
        tf = collections.Counter(w for w in toks if df[w] / n <= MAX_DF and df[w] >= 2)
        vec = {w: c * math.log(n / df[w]) for w, c in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        seeds.append(EssaySeed(slug, {w: v / norm for w, v in vec.items()}))
    return seeds


def pair_agreement(a, b):
    """Rand index over the pairs both labelings cover (noise counts as its own singleton)."""
    keys = [k for k in a if k in b]
    agree = tot = 0
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            x, y = keys[i], keys[j]
            sa = a[x] == a[y] and a[x] != -1
            sb = b[x] == b[y]
            agree += sa == sb; tot += 1
    return agree / tot if tot else 0.0


def top_terms(seeds, k=6):
    c = collections.Counter()
    for s in seeds: c.update(s.vec)
    return [w for w, _ in c.most_common(k)]


def run(seeds, eps, mn):
    labels = DBSCAN(epsilon=eps, min_samples=mn).fit(seeds)
    lab = {s.slug: l for s, l in zip(seeds, labels)}
    real = pair_agreement(lab, HAND)
    rng = random.Random(7); vals = list(HAND.values()); ctrl = []
    for _ in range(200):
        rng.shuffle(vals); ctrl.append(pair_agreement(lab, dict(zip(HAND, vals))))
    ctrl.sort()
    return lab, real, (ctrl[10], ctrl[189])


def main(a):
    eps = float(a[a.index("--eps") + 1]) if "--eps" in a else 0.80
    mn = int(a[a.index("--min") + 1]) if "--min" in a else 2
    seeds = load()
    if "--sweep" in a:
        for e in [0.70, 0.75, 0.80, 0.85, 0.88, 0.90, 0.92]:
            lab, real, band = run(seeds, e, mn)
            k = len({l for l in lab.values() if l != -1}); noise = sum(l == -1 for l in lab.values())
            print(f"eps={e:.2f} clusters={k:2d} noise={noise:2d} agreement={real:.3f} shuffle90%=[{band[0]:.3f},{band[1]:.3f}]")
        return 0
    lab, real, band = run(seeds, eps, mn)
    groups = collections.defaultdict(list)
    for s in seeds: groups[lab[s.slug]].append(s)
    out = {"eps": eps, "min_samples": mn, "n": len(seeds), "agreement": round(real, 3),
           "shuffle_band_90": [round(band[0], 3), round(band[1], 3)],
           "signal": "ABOVE-CONTROL" if real > band[1] else "INSIDE-CONTROL", "clusters": []}
    for l in sorted(groups, key=lambda x: (x == -1, x)):
        g = groups[l]
        row = {"label": l, "terms": top_terms(g), "members": [{"slug": s.slug, "hand": HAND.get(s.slug, "(unsorted)")} for s in g]}
        out["clusters"].append(row)
        print(f"\n## {'NOISE' if l == -1 else 'cluster ' + str(l)}  terms: {', '.join(row['terms'])}")
        for m in row["members"]: print(f"   {m['slug']:<52} hand: {m['hand']}")
    print(f"\nagreement with hand sort {real:.3f} vs shuffled-label 90% band [{band[0]:.3f}, {band[1]:.3f}] -> {out['signal']}")
    if "--json" in a:
        json.dump(out, open(a[a.index("--json") + 1], "w"), indent=1)
    return 0


def _entry(a):
    if "--bundles" in a:
        out = bundles()
        if "--json" in a:
            json.dump(out, open(a[a.index("--json") + 1], "w"), indent=1, default=str)
        return 0
    return main(a)


# --- Op 21: fill each show's bundle by expected value (Librarian, unchanged) ------------------
SHOWS = {
    "Receipts": "prediction falsifier scored checked against the primary document filing ledger correction conviction Apple margin",
    "The Agent That Sent It": "agent sent email unauthorized memory reconstruction cold warm reader send attested gated",
    "In the Repo": "governance branch pull request main merge ledger lattice outage second pass ancestry",
}


def bundles(budget=60000, n_max=8, stakes="medium"):
    from pathlib import Path
    from arcs_librarian import Librarian, Candidate
    cands = []
    for p in sorted(glob.glob(os.path.join(ROOT, "public", "blog-*.html"))):
        slug = os.path.basename(p)[5:-5]
        if SKIP.search(slug):
            continue
        t = body_text(p)
        cands.append(Candidate(id=slug, cls="essay", text=t[:6000], path=os.path.relpath(p, ROOT),
                               date="2026-09-29", source="claude-fable"))
    lib = Librarian(root=Path(ROOT), load_corpus=False, extra_candidates=cands)
    out = {}
    for show, q in SHOWS.items():
        r = lib.recommend(q, budget=budget, stakes=stakes, n_max=n_max, classes=["essay"])
        out[show] = r
        taken = r.get("items") or []
        print(f"\n## {show}  (reserve {r.get('reserve_ratio')}, curation_debt {r.get('curation_debt')})")
        for t in taken:
            print(f"   {t.get('id'):<52} value={t.get('value')} cost={t.get('cost')}")
    return out


if __name__ == "__main__":
    sys.exit(_entry(sys.argv[1:]))
