#!/usr/bin/env python3
"""daily_boot.py: the boot sequence every arcs-v9 thread starts with (Zach, 2026-11-16).

The session-start hook calls it; its few lines become the session's first context. Two tiers:
  - the FIRST session of the local day gets the daily ritual: /scrum standup, then the cruise-control
    sweep, one merge train in the evening, /night-moves at day's end;
  - EVERY session gets the per-thread boot: today's one thing, claim one backlog row before work,
    flip it to DONE inside the feature PR (no separate bookkeeping PR), archive the session once its
    PR merges, at most 4 live sessions.
It prints instructions only. It never runs an agent, merges, or writes to the repo; its one write is a
day marker outside the repo (~/.cache/arcs-v9/daily-boot/<date>), shared by every worktree.

  python3 scripts/daily_boot.py              print the boot block (marks the day on first run)
  python3 scripts/daily_boot.py --self-test  throwaway marker dir; touches nothing else
Stdlib only. Never exits non-zero outside --self-test (a hook must not fail).
"""
import datetime, os, subprocess, sys, tempfile

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
MARK_DIR = os.path.expanduser("~/.cache/arcs-v9/daily-boot")

DAILY = ("daily-boot: FIRST session today. Before other work: run /scrum (standup), then spawn the "
         "cruise-control agent for the read-only sweep and relay its doors. Evening: one merge train from "
         "python3 scripts/approvals_ledger.py. Day's end: /night-moves.")
THREAD = ("boot: claim one backlog row (state RUNNING, claimed_by, claimed_at) before starting work; flip it "
          "to DONE inside the feature PR, not a separate PR; archive this session once its PR merges; "
          "at most 4 live sessions.")


def one_thing():
    try:
        out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/scrum.py"), "standup"],
                             capture_output=True, text=True, timeout=20, cwd=ROOT).stdout
    except Exception:
        return ""
    for line in out.splitlines():
        if line.startswith("today's one thing:"):
            return "boot: " + line.split("  (sprint goal")[0]
    return ""


def boot(mark_dir, today, thing):
    """-> lines to print. Marks the day on the first call."""
    lines = []
    marker = os.path.join(mark_dir, today.isoformat())
    if not os.path.exists(marker):
        try:
            os.makedirs(mark_dir, exist_ok=True)
            open(marker, "w").close()
            lines.append(DAILY)
        except OSError:
            pass
    if thing:
        lines.append(thing)
    lines.append(THREAD)
    return lines


def self_test():
    d = tempfile.mkdtemp()
    day = datetime.date(2026, 11, 16)
    first = boot(d, day, "boot: today's one thing: x")
    second = boot(d, day, "")
    nextday = boot(d, day + datetime.timedelta(days=1), "")
    ok = (first[0] == DAILY and THREAD in first and "boot: today's one thing: x" in first
          and DAILY not in second and second == [THREAD] and nextday[0] == DAILY)
    print("daily_boot self-test", "OK" if ok else "FAILED")
    return ok


def main():
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    try:
        for line in boot(MARK_DIR, datetime.date.today(), one_thing()):
            print(line)
    except Exception:
        pass


if __name__ == "__main__":
    main()
