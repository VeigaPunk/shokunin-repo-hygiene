#!/usr/bin/env python3
"""Seventh probe set for R42w3mutationtester01: the two survivors whose probe
showed the freeze-detection LOG differs but the tool's VERDICT did not.

The point of a mutation is an observable behaviour change, so the scenario must
make the verdict differ.  Both probes below do that by making the two candidate
freeze commits carry DIFFERENT counter bytes, so the choice of freeze changes
the digest the tool compares.

  W32  --full-history dropped -> git's history simplification prunes a side
        branch, so the freeze moves to a different commit whose counter bytes
        differ (the digest verdict changes).
  W33  --no-renames dropped -> git's rename detection reports the re-added
        preregistration as a RENAME, so --diff-filter=A skips the commit that
        added it, and the freeze moves to a different commit whose counter
        bytes differ.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import (SEAT, PRISTINE, LANE, GITENV, git, write, commit, newrepo, sha, prereg, run,
                   compare, COUNTER, POP, CONTROL, std_repo)


def p_W32_freeze_moves():
    """W32: the freeze moves to a different commit, so the digest verdict changes."""
    d = newrepo("W32g")
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    # the prereg states the sha of the counter as it is at the SIDE add
    want = sha("# side counter\n")
    prereg_text = prereg(base, ctr_sha=want)
    # the SIDE branch adds the prereg with the counter bytes that MATCH the stated sha
    git(d, "checkout", "-q", "-b", "side")
    write(d, "census/c1.py", "# side counter\n")
    commit(d, "side counter")
    write(d, "prereg.txt", prereg_text)
    side_add = commit(d, "prereg on the side branch")
    # the MAINLINE adds the SAME prereg text with DIFFERENT counter bytes
    git(d, "checkout", "-q", "main")
    write(d, "census/c1.py", "# main counter\n")
    main_counter = commit(d, "main counter")
    write(d, "prereg.txt", prereg_text)
    main_add = commit(d, "prereg on the mainline")
    # merge, resolving the conflict on census/c1.py in favour of the mainline
    p = subprocess.run(["git", "-C", d, "merge", "--no-ff", "-m", "merge side", "side"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=GITENV)
    if p.returncode != 0:
        subprocess.run(["git", "-C", d, "checkout", "--ours", "census/c1.py"], env=GITENV, check=True)
        subprocess.run(["git", "-C", d, "add", "census/c1.py"], env=GITENV, check=True)
        subprocess.run(["git", "-C", d, "commit", "-q", "--no-edit"], env=GITENV, check=True)
    tip = git(d, "rev-parse", "HEAD")
    print("=== W32 side add=%s main add=%s (stated sha=%s)" % (side_add[:12], main_add[:12], want[:12]))
    for flags, tag in ((("--diff-filter=A", "--no-renames", "--full-history", "--reverse"), "with --full-history"),
                       (("--diff-filter=A", "--no-renames", "--reverse"), "without --full-history")):
        out = git(d, "log", *flags, "--format=%H", tip, "--", "prereg.txt")
        print("    %-24s %s" % (tag, out.replace("\n", " ") or "(nothing)"))
    return compare("the freeze moves to a commit with different counter bytes", "W32", d)


def p_W33_rename_hides_the_add():
    """W33: rename detection reports the re-added prereg as a RENAME."""
    d = newrepo("W33f")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    # the prereg is first added normally (this is the commit that must be found)
    write(d, "prereg.txt", prereg(base))
    first_add = commit(d, "prereg added")
    # a DIFFERENT file is then renamed ONTO a second prereg path; git's rename
    # detection reports that commit as R (rename), which --diff-filter=A skips,
    # so the freeze moves to the first add instead of the second
    write(d, "other.txt", "not the prereg\n")
    commit(d, "an unrelated file")
    git(d, "rm", "-q", "prereg.txt")
    commit(d, "remove the prereg")
    git(d, "mv", "other.txt", "prereg.txt")
    rename_commit = commit(d, "rename another file onto prereg.txt")
    tip = git(d, "rev-parse", "HEAD")
    print("=== W33 first add=%s rename=%s" % (first_add[:12], rename_commit[:12]))
    for flags, tag in ((("--diff-filter=A", "--no-renames", "--full-history", "--reverse"), "with --no-renames"),
                       (("--diff-filter=A", "--full-history", "--reverse"), "without --no-renames")):
        out = git(d, "log", *flags, "--format=%H", tip, "--", "prereg.txt")
        print("    %-24s %s" % (tag, out.replace("\n", " ") or "(nothing)"))
    return compare("a rename onto the preregistration path", "W33", d)


PROBES = {"W32": p_W32_freeze_moves, "W33": p_W33_rename_hides_the_add}


def main():
    for mid in (sys.argv[1:] or sorted(PROBES)):
        fn = PROBES.get(mid)
        if fn is None:
            print("=== %s: no probe defined" % mid)
            continue
        try:
            fn()
        except Exception as exc:
            print("=== %s: PROBE ERROR %s: %s" % (mid, type(exc).__name__, exc))


if __name__ == "__main__":
    main()
