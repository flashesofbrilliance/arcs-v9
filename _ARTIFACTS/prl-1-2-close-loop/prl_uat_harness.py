#!/usr/bin/env python3
"""PRL Tidio->Zapier->SugarCRM runtime UAT harness (Frustration-Gate: repeatable expected-vs-actual).

Turns the manual acceptance test in
_ARTIFACTS/prl-1-1-evidence/2026-08-18-1.2A-web-forms-acceptance-tests.md into a repeatable,
offline-runnable check. Given labeled fixtures (input payload + expected Sugar field
values/rules) and the ACTUAL Sugar records read back from the sandbox, prints a per-lead
per-field PASS/FAIL table + summary; exits non-zero on any FAIL.

This is the runtime twin of prl_depmap_check.py in this same directory — same style
(stdlib only, argparse, sectioned output, exit codes).

REUSE-FIRST, not reinvented: every field rule below is derived from an existing PRL artifact,
cited inline. This harness does not author a competing spec for anything those artifacts
already define.

Field rules and their provenance:
  - first_name / last_name: split on the FIRST space only; a title/suffix stays attached to
    whichever side the split lands it on (not guessed away). This is the EXACT `parseName`
    contract proven by `_ARTIFACTS/prl-zap-kit/task7-state-parser.test.js` (e.g. 'Mary Jane
    Watson' -> first='Mary', last='Jane Watson'; single name -> last=''). Checked as an exact
    match against the fixture's `expected.first_name` / `expected.last_name`.
  - location_c / state_parse_failed / ambiguous: reuses `task7-state-parser.test.js`'s
    `parseState`/`processInputs` output contract verbatim (same field names, same fallback
    behavior) rather than inventing a new state-parse check:
      * `state_code` is ALWAYS a valid 2-letter code — it falls back to "CA"
        (`FALLBACK_STATE`) on any parse failure (garbage, non-US, zip codes, digits, empty).
      * `state_parse_failed` is the flag that distinguishes a real parse from that fallback.
      * Per `2026-08-18-dod-reconciliation.md` ("silent CA-lead (parse fallback; audit-
        trailed)") and `prl-system-ssot.md` ("fallback CA + parse-failed flag" / "Verified
        real run: ... location_c=CT [checkmark] audit [checkmark]"), falling back to CA is
        EXPECTED and NOT itself a defect — the defect class this check guards against is a
        fallback that is silently unflagged (state_parse_failed=false when the code is only
        a guess), which is exactly the "silent-CA-lead" failure mode named in the DoD doc.
  - lead_source: exact expected value — "Chatbot" (chatbot leg, sandbox-only value) vs
    "Web Site" (web-forms leg, valid in both sandbox and prod). Source: 1.2A acceptance-tests
    doc (`_ARTIFACTS/prl-1-1-evidence/2026-08-18-1.2A-web-forms-acceptance-tests.md`) plus
    `prl-system-ssot.md`'s pipeline diagram (`lead_source=Chatbot` / `lead_source=Web Site`).
  - account_name: not silently truncated on a long free-text company name. Source: the 1.2A
    acceptance-tests doc's explicit re-check of "Fix 3" (deferred as low-risk on the chatbot
    leg, re-examined for web forms since forms allow longer free-text company names).
  - duplicate check: fixtures with expected.expected_dedup=true assert the ACTUAL record's
    `lead_ids_seen` (every Sugar lead id observed across that fixture's resubmissions)
    collapses to exactly one distinct id. Source: the 1.2A acceptance-tests doc's duplicate-
    submission check, scoped here to the case Sugar search is documented as SAFE for —
    `2026-08-18-dod-reconciliation.md` / `prl-system-ssot.md` both flag dedup-by-empty-email
    as a separate, still-open CRITICAL defect ("empty-email -> dedup search matches arbitrary
    record -> Path A corrupts real leads"); this harness's dedup fixtures keep email
    populated, matching the documented safe path, not the known-broken one.
  - has_note (chatbot leg only): presence check that a related Note carrying the
    transcript/blurb exists on the actual record. Source: 1.2A acceptance-tests doc.
  - phone_work: must be non-empty. `phone_work` is one of Sugar's 6 REQUIRED Leads fields
    (`account_name`, `first_name`, `last_name`, `phone_work`, `lead_source`, `location_c`),
    confirmed via a read-only live-schema audit (100/100 filled) — `STATE-OF-SUGAR-2026-08-11.md`
    §2 and `INTEGRATION-DOSSIER.md` §B/§D4 ("phone_work is REQUIRED ... the bot must force
    phone or a lead fails to create"). Note: those same docs' claim that email is written to
    `email1` (Sugar has no plain `email` column) is recorded here for schema fidelity but not
    separately gated — no fixture in this set exercises a missing-email path (a still-open,
    separately-tracked CRITICAL defect per ADR-074 / the DoD doc's empty-email dedup finding).

--actuals decouples this harness from live Sugar access: it reads a JSON file mapping
fixture label -> the actual Sugar record dict that was independently read back from the
sandbox (never call the network from this script).

How to produce that actuals file for real, from Zach's machine (do NOT do this from here):
  1. For each fixture in prl-uat-fixtures.json, drive its `input` through the live Tidio/WP
     -> Zapier -> SugarCRM pipeline (or use `scripts/sugar_bulk.py` per AGENTS.md gotcha #9
     for a direct REST read once you have the resulting lead id(s) — sugar_bulk.py talks to
     the sandbox host `prlresinstest.sugarondemand.com/rest/v11/`, connection 65663180,
     NEVER prod).
  2. For a dedup fixture, submit twice and collect every lead id Sugar shows for that
     identity into `lead_ids_seen` (a list) rather than assuming a single id.
  3. Read back each resulting Lead + any related Note directly via the REST API (don't
     trust Zapier's self-reported step output — same lesson as the chatbot leg).
  4. Assemble one JSON object: {"<fixture label>": {<actual Sugar fields>}, ...} and pass
     it via --actuals.

Usage:
  python3 prl_uat_harness.py --actuals <path/to/actuals.json> [--fixtures prl-uat-fixtures.json]
  python3 prl_uat_harness.py --self-test

Exit 0 all PASS, 1 on any FAIL.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY", "DC",
}


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Field rule functions: each returns (passed: bool, actual_repr: str) -----------------

def check_first_name(expected, actual):
    exp = expected.get("first_name")
    act = actual.get("first_name")
    return act == exp, repr(act)


def check_last_name(expected, actual):
    exp = expected.get("last_name")
    act = actual.get("last_name")
    return act == exp, repr(act)


def check_location(expected, actual):
    """Reuses the task7-state-parser `parseState`/`processInputs` output contract verbatim:
    state_code is ALWAYS a valid 2-letter code (falls back to "CA" on parse failure), and
    state_parse_failed is the flag that must truthfully say whether that code is a real parse
    or the fallback. PASS requires: (a) state_code matches the expected code exactly, and
    (b) state_parse_failed matches the expected flag exactly. A fallback to "CA" is fine when
    flagged (state_parse_failed=true, per the DoD doc's 'fallback CA + audit-trailed' —
    expected); the FAIL case this guards is a fallback silently reported as a real parse
    (state_parse_failed=false when it should be true), i.e. the "silent CA-lead" defect."""
    act_code = actual.get("location_c")
    act_failed = actual.get("state_parse_failed")
    exp_code = expected.get("location_c")
    exp_failed = expected.get("state_parse_failed", False)
    code_valid = act_code in US_STATE_CODES
    passed = code_valid and act_code == exp_code and bool(act_failed) == bool(exp_failed)
    return passed, f"location_c={act_code!r} state_parse_failed={act_failed!r}"


def check_lead_source(expected, actual):
    exp = expected.get("lead_source")
    act = actual.get("lead_source")
    return act == exp, repr(act)


def check_account_name(expected, actual):
    """Not silently truncated: actual length clears the fixture's floor, and (for inputs
    longer than that floor) actual isn't shorter than the input company name."""
    act = actual.get("account_name") or ""
    min_len = expected.get("account_name_min_len", 0)
    input_name = expected.get("account_name_input", "")
    floor_ok = len(act) >= min_len
    not_truncated_vs_input = True
    if len(input_name) > min_len:
        not_truncated_vs_input = len(act) >= len(input_name)
    passed = floor_ok and not_truncated_vs_input
    return passed, f"len={len(act)} value={act[:60]!r}{'...' if len(act) > 60 else ''}"


def check_has_note(expected, actual):
    exp = expected.get("has_note", False)
    notes = actual.get("notes") or []
    act_has_note = len(notes) > 0
    if not exp:
        # Not required either way when the fixture doesn't expect one.
        return True, f"notes_count={len(notes)} (not required)"
    return act_has_note == exp, f"notes_count={len(notes)}"


def check_phone_work(expected, actual):
    """phone_work is a hard-required Sugar Leads field (STATE-OF-SUGAR-2026-08-11.md §2,
    INTEGRATION-DOSSIER.md §D4) — a lead with it empty would have failed to create at all."""
    if not expected.get("phone_work_required", True):
        return True, "(not required for this fixture)"
    act = actual.get("phone_work") or ""
    passed = str(act).strip() != ""
    return passed, repr(act)


def check_dedup(expected, actual):
    exp = expected.get("expected_dedup", False)
    if not exp:
        return True, "(no dedup check for this fixture)"
    seen = actual.get("lead_ids_seen") or []
    distinct = set(seen)
    passed = len(distinct) == 1 and len(seen) >= 2
    return passed, f"lead_ids_seen={seen} distinct={sorted(distinct)}"


CHECKS = [
    ("first_name", check_first_name),
    ("last_name", check_last_name),
    ("location_c", check_location),
    ("lead_source", check_lead_source),
    ("account_name", check_account_name),
    ("phone_work", check_phone_work),
    ("has_note", check_has_note),
    ("dedup", check_dedup),
]


def run(fixtures, actuals):
    total_fail = 0
    total_checks = 0
    rows_by_fixture = []

    for fx in fixtures:
        label = fx["label"]
        expected = fx["expected"]
        actual = actuals.get(label)
        rows = []
        if actual is None:
            rows.append(("(all fields)", "actual record present", "MISSING",
                         "FAIL — no actuals entry for this fixture label"))
            total_fail += 1
            total_checks += 1
            rows_by_fixture.append((label, fx.get("notes", ""), rows))
            continue

        for field, fn in CHECKS:
            passed, act_repr = fn(expected, actual)
            exp_repr = {
                "first_name": expected.get("first_name"),
                "last_name": expected.get("last_name"),
                "location_c": (
                    f"{expected.get('location_c')} "
                    f"(state_parse_failed={expected.get('state_parse_failed', False)})"
                ),
                "lead_source": expected.get("lead_source"),
                "account_name": f">= {expected.get('account_name_min_len', 0)} chars, not truncated",
                "phone_work": "non-empty (required field)" if expected.get("phone_work_required", True) else "n/a",
                "has_note": expected.get("has_note", False),
                "dedup": "single lead id across resubmissions" if expected.get("expected_dedup") else "n/a",
            }[field]
            status = "PASS" if passed else "FAIL"
            rows.append((field, repr(exp_repr), act_repr, status))
            total_checks += 1
            if not passed:
                total_fail += 1
        rows_by_fixture.append((label, fx.get("notes", ""), rows))

    return rows_by_fixture, total_checks, total_fail


def print_report(rows_by_fixture, total_checks, total_fail):
    print("PRL UAT harness — Tidio/WP -> Zapier -> SugarCRM")
    print("=" * 72)
    for label, notes, rows in rows_by_fixture:
        print(f"\nFixture: {label}")
        if notes:
            print(f"  note: {notes}")
        field_w = max(len(r[0]) for r in rows) if rows else 10
        for field, exp, act, status in rows:
            marker = "OK  " if status == "PASS" else "FAIL"
            print(f"  [{marker}] {field:<{field_w}}  expected={exp}  actual={act}")
    print("\n" + "=" * 72)
    passed = total_checks - total_fail
    print(f"SUMMARY: {passed}/{total_checks} checks passed, {total_fail} FAIL(s) "
          f"across {len(rows_by_fixture)} fixture(s)")
    if total_fail:
        print("RESULT: FAIL")
    else:
        print("RESULT: PASS")


# --- Self-test: synthetic actuals proving the gate fires on bad AND stays clean on good ---

def _self_test_fixtures():
    return [
        {
            "label": "good-lead",
            "notes": "Synthetic PASS case.",
            "expected": {
                "first_name": "Maria", "last_name": "Gonzalez",
                "location_c": "CA", "lead_source": "Web Site",
                "account_name_min_len": 15, "account_name_input": "Bright Path Labs",
                "has_note": False, "expected_dedup": False,
            },
        },
        {
            "label": "good-lead-with-flagged-fallback",
            "notes": "Synthetic PASS case: non-US state input correctly falls back to CA WITH state_parse_failed=true (task7 'Toronto' case) — a flagged fallback, not a silent one.",
            "expected": {
                "first_name": "Robert", "last_name": "Chen",
                "location_c": "CA", "state_parse_failed": True,
                "lead_source": "Web Site",
                "account_name_min_len": 90,
                "account_name_input": "The Greater Northeastern Regional Manufacturing, Distribution & Logistics Consortium of Independent Family-Owned Enterprises LLC",
                "has_note": False, "expected_dedup": False,
            },
        },
        {
            "label": "good-lead-dedup",
            "notes": "Synthetic PASS case: two submissions collapse to one lead id.",
            "expected": {
                "first_name": "Jane", "last_name": "Smith",
                "location_c": "TX", "state_parse_failed": False,
                "lead_source": "Chatbot",
                "account_name_min_len": 5, "account_name_input": "Acme",
                "has_note": True, "expected_dedup": True,
            },
        },
        {
            "label": "bad-lead-truncated-name-bad-state-dup",
            "notes": "Synthetic FAIL case: every rule this harness enforces is broken on purpose, including a silent-CA-lead (fallback code reported as a real parse).",
            "expected": {
                "first_name": "Dr.", "last_name": "Jane Smith Jr.",
                "location_c": "CA", "state_parse_failed": True,
                "lead_source": "Web Site",
                "account_name_min_len": 90,
                "account_name_input": "The Greater Northeastern Regional Manufacturing, Distribution & Logistics Consortium of Independent Family-Owned Enterprises LLC",
                "has_note": True, "expected_dedup": True,
            },
        },
    ]


def _self_test_actuals():
    return {
        "good-lead": {
            "first_name": "Maria", "last_name": "Gonzalez",
            "location_c": "CA", "state_parse_failed": False,
            "lead_source": "Web Site", "account_name": "Bright Path Labs",
            "phone_work": "203-555-0142",
            "notes": [], "lead_ids_seen": ["L-1001"],
        },
        "good-lead-with-flagged-fallback": {
            "first_name": "Robert", "last_name": "Chen",
            "location_c": "CA", "state_parse_failed": True,
            "lead_source": "Web Site",
            "account_name": "The Greater Northeastern Regional Manufacturing, Distribution & Logistics Consortium of Independent Family-Owned Enterprises LLC",
            "phone_work": "416-555-0173",
            "notes": [], "lead_ids_seen": ["L-1002"],
        },
        "good-lead-dedup": {
            "first_name": "Jane", "last_name": "Smith",
            "location_c": "TX", "state_parse_failed": False,
            "lead_source": "Chatbot", "account_name": "Acme Corp",
            "phone_work": "914-555-0198",
            "notes": ["chat transcript re: pricing"],
            "lead_ids_seen": ["L-1003", "L-1003"],
        },
        "bad-lead-truncated-name-bad-state-dup": {
            # Wrong split: title dropped instead of kept attached.
            "first_name": "Jane", "last_name": "Smith",
            # Silent CA-lead: fallback code reported as if it were a real parse.
            "location_c": "CA", "state_parse_failed": False,
            "lead_source": "Web Site",  # expected "Web Site" too, but truncated account name below fails
            "account_name": "The Greater Northeastern Regional Manufa",  # truncated
            "phone_work": "",  # required field left empty -> FAIL
            "notes": [],  # has_note expected True -> FAIL
            "lead_ids_seen": ["L-2001", "L-2002"],  # two distinct ids -> dedup FAIL
        },
    }


def self_test():
    fixtures = _self_test_fixtures()
    actuals = _self_test_actuals()
    rows_by_fixture, total_checks, total_fail = run(fixtures, actuals)
    print_report(rows_by_fixture, total_checks, total_fail)

    good_labels = {"good-lead", "good-lead-with-flagged-fallback", "good-lead-dedup"}
    bad_label = "bad-lead-truncated-name-bad-state-dup"
    good_fail_count = sum(
        1 for label, _notes, rows in rows_by_fixture if label in good_labels
        for *_r, status in rows if status == "FAIL"
    )
    bad_fail_count = sum(
        1 for label, _notes, rows in rows_by_fixture if label == bad_label
        for *_r, status in rows if status == "FAIL"
    )

    print("\n" + "=" * 72)
    print("SELF-TEST ASSERTIONS")
    ok_good = good_fail_count == 0
    ok_bad = bad_fail_count > 0
    print(f"  [{'OK  ' if ok_good else 'FAIL'}] good fixtures have zero FAILs (got {good_fail_count})")
    print(f"  [{'OK  ' if ok_bad else 'FAIL'}] bad fixture has at least one FAIL (got {bad_fail_count})")
    if ok_good and ok_bad:
        print("SELF-TEST: PASS — gate demonstrably fails-on-bad and passes-on-good.")
        return 0
    print("SELF-TEST: FAIL — the gate is not discriminating correctly.")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fixtures", default=os.path.join(HERE, "prl-uat-fixtures.json"),
                     help="Path to prl-uat-fixtures.json")
    ap.add_argument("--actuals", default=None,
                     help="Path to a JSON file mapping fixture label -> actual Sugar record dict")
    ap.add_argument("--self-test", action="store_true",
                     help="Run against an embedded synthetic actuals set (no --actuals needed)")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not args.actuals:
        print("error: --actuals <file> is required (or pass --self-test)", file=sys.stderr)
        return 2

    fixtures_doc = load(args.fixtures)
    fixtures = fixtures_doc["fixtures"]
    actuals = load(args.actuals)

    rows_by_fixture, total_checks, total_fail = run(fixtures, actuals)
    print_report(rows_by_fixture, total_checks, total_fail)
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
