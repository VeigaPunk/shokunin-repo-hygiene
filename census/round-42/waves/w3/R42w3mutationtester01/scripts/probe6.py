#!/usr/bin/env python3
"""Sixth probe set for R42w3mutationtester01: the three survivors whose
equivalence argument needs a sharper scenario, plus the PATH caveat.

  W32  --full-history dropped   (a merge that is TREESAME to a parent)
  W33  --no-renames dropped     (a prereg path that is a DIRECTORY, so git's
                                 rename detection can pair source and target
                                 inside the pathspec)
  W57  ls-tree without the '--' separator (a path that literally starts with
                                 '-', which git would take as an option)
  W55  PATH hardcoded to /usr/bin:/bin (git is NOT on the caller's PATH)
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import (SEAT, PRISTINE, LANE, GITENV, git, write, commit, newrepo, sha, prereg, run,
                   compare, COUNTER, POP, CONTROL, std_repo)


def p_W32_treesame_merge():
    """W32: --full-history dropped, with a merge that is TREESAME to a parent."""
    d = newrepo("W32d")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    # the prereg exists on main with content X
    write(d, "prereg.txt", prereg(base))
    main_add = commit(d, "prereg on main")
    # a side branch that creates the SAME prereg content independently
    git(d, "checkout", "-q", "-b", "side")
    git(d, "rm", "-q", "prereg.txt")
    commit(d, "remove prereg on the side branch")
    write(d, "prereg.txt", prereg(base))
    side_add = commit(d, "prereg on the side branch")
    git(d, "checkout", "-q", "main")
    git(d, "merge", "-q", "--no-ff", "-m", "merge side", "side")
    tip = git(d, "rev-parse", "HEAD")
    print("=== W32 main add=%s side add=%s" % (main_add[:12], side_add[:12]))
    for flags, tag in ((("--diff-filter=A", "--no-renames", "--full-history", "--reverse"), "with --full-history"),
                       (("--diff-filter=A", "--no-renames", "--reverse"), "without --full-history")):
        out = git(d, "log", *flags, "--format=%H", tip, "--", "prereg.txt")
        print("    %-24s %s" % (tag, out.replace("\n", " ") or "(nothing)"))
    return compare("a merge that is TREESAME to the mainline for the prereg", "W32", d)


def p_W33_directory_prereg():
    """W33: --no-renames dropped, with a prereg path that is a DIRECTORY."""
    d = newrepo("W33d")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "preregdir/draft.txt", prereg(base))
    commit(d, "a draft inside preregdir")
    git(d, "mv", "preregdir/draft.txt", "preregdir/prereg.txt")
    commit(d, "rename the draft inside preregdir")
    tip = git(d, "rev-parse", "HEAD")
    for flags, tag in ((("--diff-filter=A", "--no-renames", "--full-history", "--reverse"), "with --no-renames"),
                       (("--diff-filter=A", "--full-history", "--reverse"), "without --no-renames")):
        out = git(d, "log", *flags, "--format=%H", tip, "--", "preregdir")
        print("=== W33 dir-path freeze log %-22s %s" % (tag, out.replace("\n", " ") or "(nothing)"))
    # the tool reads a blob at rev:path, so a directory is not a blob -> the tool refuses
    return compare("a prereg path that is a directory", "W33", d, prereg_path="preregdir")


def p_W57_leading_dash_root():
    """W57: ls-tree without the '--' separator, on a path that starts with '-'."""
    d = newrepo("W57d")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "real-c1.py", COUNTER)
    os.symlink("real-c1.py", os.path.join(d, "-link.py"))
    keys = {"Base": base, "Counter": "-link.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("a symlink Counter path that starts with '-'", "W57", d)


def p_W55_path_without_git():
    """W55: PATH hardcoded to /usr/bin:/bin -> the caller's PATH is ignored."""
    d = std_repo("W55c")
    mp = os.path.join(SEAT, "mutants", "W55.py")
    prc, pl, _ = run(PRISTINE, d)
    env = dict(GITENV, PATH="/nonexistent", TMPDIR=d)
    p = subprocess.run(["/usr/bin/python3", "-B", mp, "--root", d, "--prereg", "prereg.txt",
                        "--rev", git(d, "rev-parse", "HEAD")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, env=env)
    ml = sorted(x for x in p.stdout.splitlines() if x.startswith("FINDING "))
    print("=== PATH=/nonexistent in the caller's environment [W55]")
    print("  pristine rc=%d %s" % (prc, " | ".join(pl) or "(no findings)"))
    print("  mutant   rc=%d %s" % (p.returncode, " | ".join(ml) or "(no findings)"))
    print("  stderr   %r" % p.stderr.strip()[:150])
    differ = (pl != ml or prc != p.returncode)
    print("  DIFFER=%s" % differ)
    return differ


PROBES = {"W32": p_W32_treesame_merge, "W33": p_W33_directory_prereg,
          "W55": p_W55_path_without_git, "W57": p_W57_leading_dash_root}


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
