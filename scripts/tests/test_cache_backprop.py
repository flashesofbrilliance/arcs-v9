#!/usr/bin/env python3
"""Invariants for the cache manifest + back-propagation (build plan 1b).

Runs against a throwaway git repo in a tempdir so it never touches the real tree.
    python3 scripts/tests/test_cache_backprop.py      # (stdlib unittest, no deps)
"""
import json, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)


def run(cwd, script, *args):
    """Invoke a copied script inside the throwaway repo. cache_manifest.py needs --today first."""
    cmd = [sys.executable, os.path.join(cwd, "scripts", script)]
    if script == "cache_manifest.py":
        cmd += ["--today", "2026-09-07"]
    cmd += list(args)
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


class BackpropInvariants(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        g = lambda *a: subprocess.run(["git", *a], cwd=self.d, capture_output=True, text=True, check=True)
        g("init", "-q"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
        os.makedirs(os.path.join(self.d, "_ARTIFACTS/atlas"))
        os.makedirs(os.path.join(self.d, "_DECISIONS"))
        os.makedirs(os.path.join(self.d, "scripts"))
        # a product digest with two epochs, graded against the first commit
        digest = {"domain": "product", "generated": "2026-09-01", "nodes": [
            {"id": "a", "title": "A", "status": "LIVE", "claim": "x", "provenance": "_DECISIONS/d1.md", "epoch": "2026-05"},
            {"id": "b", "title": "B", "status": "LIVE", "claim": "y", "provenance": "_DECISIONS/d2.md", "epoch": "2026-06"},
        ]}
        open(os.path.join(self.d, "_ARTIFACTS/atlas/digest-product.json"), "w").write(json.dumps(digest))
        open(os.path.join(self.d, "_DECISIONS/d1.md"), "w").write("one\n")
        open(os.path.join(self.d, "_DECISIONS/d2.md"), "w").write("two\n")
        # copy the two scripts in so imports resolve relative to a real path
        for s in ("cache_manifest.py", "cache_backprop.py"):
            open(os.path.join(self.d, "scripts", s), "w").write(open(os.path.join(SCRIPTS, s)).read())
        g("add", "-A"); g("commit", "-q", "-m", "seed")
        self.g = g

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.d])

    def stamp(self): return run(self.d, "cache_manifest.py", "stamp")
    def check(self): return run(self.d, "cache_manifest.py", "check")

    def test_dirty_then_backprop_one_slice_leaves_sibling_dirty(self):
        self.stamp()
        self.assertEqual(self.check().returncode, 0)  # clean right after stamp
        # Freshness scope is per-DOMAIN (_DECISIONS/*), so editing any _DECISIONS file dirties
        # EVERY product epoch. Re-grading one epoch then frees only that one (per-slice grain).
        open(os.path.join(self.d, "_DECISIONS/d1.md"), "a").write("edit\n")
        self.g("add", "-A"); self.g("commit", "-q", "-m", "edit d1")
        self.assertEqual(self.check().returncode, 2)  # dirty
        j = json.loads(run(self.d, "cache_manifest.py", "--json", "check").stdout)
        by = {s["epoch"]: s for s in j["slices"]}
        self.assertFalse(by["2026-05"]["fresh"]); self.assertFalse(by["2026-06"]["fresh"])  # domain scope: both dirty
        # back-propagate ONLY 2026-05
        gf = os.path.join(self.d, "g.json"); open(gf, "w").write(json.dumps({"a": {"status": "LIVE", "note": "re-confirmed"}}))
        r = run(self.d, "cache_backprop.py", "apply", "product", "2026-05", "--graded", gf, "--today", "2026-09-07")
        self.assertEqual(r.returncode, 0, r.stderr)
        j = json.loads(run(self.d, "cache_manifest.py", "--json", "check").stdout)
        by = {s["epoch"]: s for s in j["slices"]}
        self.assertTrue(by["2026-05"]["fresh"]); self.assertFalse(by["2026-06"]["fresh"])
        self.assertEqual(j["dirty_count"], 1)  # only the un-re-graded sibling remains

    def test_restamp_preserves_backpropped_slice(self):
        # sibling stays dirty across a whole-file re-stamp (per-slice preservation, the shared-digest hazard)
        self.stamp()
        open(os.path.join(self.d, "_DECISIONS/d1.md"), "a").write("e\n")
        open(os.path.join(self.d, "_DECISIONS/d2.md"), "a").write("e\n")
        self.g("add", "-A"); self.g("commit", "-q", "-m", "edit both")
        gf = os.path.join(self.d, "g.json"); open(gf, "w").write(json.dumps({"a": {"status": "LIVE"}}))
        run(self.d, "cache_backprop.py", "apply", "product", "2026-05", "--graded", gf, "--today", "2026-09-07")
        self.stamp()  # a full re-stamp must NOT resurrect 2026-05 nor free 2026-06
        j = json.loads(run(self.d, "cache_manifest.py", "--json", "check").stdout)
        by = {s["epoch"]: s for s in j["slices"]}
        self.assertTrue(by["2026-05"]["fresh"], "re-graded slice must stay fresh after stamp")
        self.assertFalse(by["2026-06"]["fresh"], "un-re-graded sibling must stay dirty after stamp")

    def test_partial_does_not_stamp_fresh(self):
        # finding 2: a --partial grade advances the digest but must NOT claim slice freshness.
        self.stamp()
        open(os.path.join(self.d, "_DECISIONS/d1.md"), "a").write("e\n")
        self.g("add", "-A"); self.g("commit", "-q", "-m", "edit d1")
        gf = os.path.join(self.d, "g.json")
        # 2026-05 in the test digest has one node "a"; make a two-node epoch to grade a subset
        # -> reuse 2026-06 has one node "b"; instead grade product with an epoch of 2 nodes:
        # simplest: grade 2026-05 fully is not partial. Use --partial on an epoch with an ungraded node.
        # Build that: add a second node to 2026-05 via a fresh digest.
        dp = os.path.join(self.d, "_ARTIFACTS/atlas/digest-product.json")
        dig = json.load(open(dp)); dig["nodes"].append(
            {"id": "a2", "status": "LIVE", "claim": "z", "provenance": "_DECISIONS/d1.md", "epoch": "2026-05"})
        open(dp, "w").write(json.dumps(dig)); self.g("add", "-A"); self.g("commit", "-q", "-m", "add a2")
        self.stamp()
        open(os.path.join(self.d, "_DECISIONS/d1.md"), "a").write("e2\n")
        self.g("add", "-A"); self.g("commit", "-q", "-m", "edit d1 again")
        open(gf, "w").write(json.dumps({"a": {"status": "LIVE"}}))  # grade 1 of 2 in 2026-05
        r = run(self.d, "cache_backprop.py", "apply", "product", "2026-05", "--graded", gf, "--today", "2026-09-07", "--partial")
        self.assertEqual(r.returncode, 2, r.stderr)  # not fully fresh -> exit 2
        j = json.loads(run(self.d, "cache_manifest.py", "--json", "check").stdout)
        by = {s["epoch"]: s for s in j["slices"]}
        self.assertFalse(by["2026-05"]["fresh"], "partial grade must not stamp the slice fresh")

    def test_failed_apply_leaves_digest_untouched(self):
        # finding 1: a failed apply (slice not in manifest) must not half-write the digest.
        # No stamp yet -> no manifest -> apply must exit 1 with the digest byte-identical.
        dp = os.path.join(self.d, "_ARTIFACTS/atlas/digest-product.json")
        before = open(dp).read()
        gf = os.path.join(self.d, "g.json"); open(gf, "w").write(json.dumps({"a": {"status": "DRIFTED", "note": "x"}}))
        r = run(self.d, "cache_backprop.py", "apply", "product", "2026-05", "--graded", gf, "--today", "2026-09-07")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(open(dp).read(), before, "digest must be untouched when apply fails validation")

    def test_apply_rejects_foreign_id_bad_status_and_ungraded(self):
        self.stamp()
        gf = os.path.join(self.d, "g.json")
        open(gf, "w").write(json.dumps({"zzz": {"status": "LIVE"}}))
        self.assertEqual(run(self.d, "cache_backprop.py", "apply", "product", "2026-05", "--graded", gf, "--today", "2026-09-07").returncode, 1)
        open(gf, "w").write(json.dumps({"a": {"status": "BOGUS"}}))
        self.assertEqual(run(self.d, "cache_backprop.py", "apply", "product", "2026-05", "--graded", gf, "--today", "2026-09-07").returncode, 1)
        # 2026-05 has only node a -> fully graded; test ungraded on a multi-node needs 2026-06 (1 node) — use domain-wide:
        open(gf, "w").write(json.dumps({}))
        self.assertEqual(run(self.d, "cache_backprop.py", "apply", "product", "2026-05", "--graded", gf, "--today", "2026-09-07").returncode, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
