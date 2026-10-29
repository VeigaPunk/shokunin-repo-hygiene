#!/usr/bin/env python3
"""Fourth probe set for R42w3mutationtester01: sharper scenarios for the five
survivors whose first probes did not discriminate the mutated branch.

  W18  LC_ALL=C -> C.UTF-8        (a NON-ASCII path: git's path quoting is
                                   locale-dependent, and the symlink test reads
                                   the mode out of git's output)
  W19  -c core.quotePath=false dropped (the same non-ASCII symlink)
  W32  --full-history dropped      (a prereg added on a side branch, deleted
                                   and re-added on the mainline after the merge)
  W33  --no-renames dropped        (a prereg ADDED BY a rename: git reports R,
                                   not A, so --diff-filter=A finds nothing)
  W40  at_freeze is None or not at_freeze (the counter file is EMPTY at the
                                   freeze commit, so the mutant reports
                                   COUNTER-MISSING where the pristine reports
                                   COUNTER-DIGEST)
  W57  ls-tree without the '--' separator (a path that begins with '-')
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import (SEAT, PRISTINE, LANE, GITENV, git, write, commit, newrepo, sha, prereg, run,
                   compare, COUNTER, POP, CONTROL, std_repo)


def p_W18_W19_nonascii_symlink():
    """W18/W19: a non-ASCII SYMLINK counter path (git quotes non-ASCII paths)."""
    for mid in ("W18", "W19"):
        d = newrepo(mid + "-utf8")
        write(d, "census/real-c1.py", COUNTER)
        os.symlink("real-c1.py", os.path.join(d, "census/contrôle.py"))
        write(d, "census/pop.tsv", POP)
        write(d, "census/control.txt", CONTROL)
        base = commit(d, "c1")
        keys = {"Base": base, "Counter": "census/contrôle.py sha256=%s" % sha(COUNTER),
                "Population": "census/pop.tsv sha256=%s" % sha(POP),
                "Control": "census/control.txt", "Target": "t", "Kill": "k"}
        write(d, "prereg.txt", prereg(base, keys=keys))
        commit(d, "prereg")
        compare("a non-ASCII symlink Counter path", mid, d)
    return None


def p_W32_readd_after_merge():
    """W32: --full-history dropped -> the freeze is found on the mainline, not the side branch."""
    d = newrepo("W32c")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    git(d, "checkout", "-q", "-b", "side")
    write(d, "prereg.txt", prereg(base))
    side_add = commit(d, "prereg on the side branch")
    git(d, "checkout", "-q", "main")
    git(d, "merge", "-q", "--no-ff", "-m", "merge side", "side")
    # delete and re-add on the mainline, so the mainline has its own 'A' commit
    git(d, "rm", "-q", "prereg.txt")
    commit(d, "delete prereg")
    write(d, "prereg.txt", prereg(base))
    main_add = commit(d, "re-add prereg")
    tip = git(d, "rev-parse", "HEAD")
    print("=== W32 side add=%s main re-add=%s" % (side_add[:12], main_add[:12]))
    for flags, tag in ((("--diff-filter=A", "--no-renames", "--full-history", "--reverse"), "with --full-history"),
                       (("--diff-filter=A", "--no-renames", "--reverse"), "without --full-history")):
        out = git(d, "log", *flags, "--format=%H", tip, "--", "prereg.txt")
        print("    %-24s %s" % (tag, out.replace("\n", " ") or "(nothing)"))
    return compare("prereg added on a side branch, deleted and re-added on the mainline", "W32", d)


def p_W33_added_by_rename():
    """W33: --no-renames dropped -> a prereg ADDED BY A RENAME is not an 'A' commit."""
    d = newrepo("W33c")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "draft.txt", prereg(base))
    commit(d, "a draft file")
    git(d, "mv", "draft.txt", "prereg.txt")
    commit(d, "rename the draft to prereg.txt")
    tip = git(d, "rev-parse", "HEAD")
    for flags, tag in ((("--diff-filter=A", "--no-renames", "--full-history", "--reverse"), "with --no-renames"),
                       (("--diff-filter=A", "--full-history", "--reverse"), "without --no-renames")):
        out = git(d, "log", *flags, "--format=%H", tip, "--", "prereg.txt")
        print("=== W33 freeze-detection log %-22s %s" % (tag, out.replace("\n", " ") or "(nothing)"))
    return compare("a prereg added by renaming another file", "W33", d)


def p_W40_empty_at_freeze():
    """W40: the counter file is EMPTY at the freeze commit."""
    d = newrepo("W40b")
    write(d, "census/c1.py", "")
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(""),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("an EMPTY counter file at the freeze commit", "W40", d)


def p_W57_leading_dash():
    """W57: ls-tree without the '--' separator, on a path that begins with '-'."""
    d = newrepo("W57c")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "census/real-c1.py", COUNTER)
    os.symlink("real-c1.py", os.path.join(d, "census/-link.py"))
    keys = {"Base": base, "Counter": "census/-link.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("a symlink Counter path beginning with '-'", "W57", d)


PROBES = {
    "W18W19": p_W18_W19_nonascii_symlink, "W32": p_W32_readd_after_merge,
    "W33": p_W33_added_by_rename, "W40": p_W40_empty_at_freeze, "W57": p_W57_leading_dash,
}


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
