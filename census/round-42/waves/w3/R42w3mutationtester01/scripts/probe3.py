#!/usr/bin/env python3
"""Third probe set for R42w3mutationtester01: the survivors the first two sets
did not reach, plus the lane-leg check for the survivors the counter's `real`
leg fails on.

Reached here:
  W24 (killed) -- already killed; W25 (killed)
  W26 ls-tree without --full-tree
  W27 merge-base exit 1 treated as an ancestor
  W53 Refusal as BaseException
  W54 --root with a '/.' suffix
  W55 PATH hardcoded to /usr/bin:/bin
  W56 rev-parse without -q
  W57 ls-tree without the '--' separator
  W58 HEADER.search instead of .match
  W60 duplicated key lower-cased
  W61 a duplicated key whose second value is empty -> 'x'
  W62 freeze ids not filtered by FULL40
  W66 PATH_SHA.match(value.strip())
  W67 the missing-class name upper-cased
  W68 the digest compared against want.lower()
  W69 the FROZEN-EDITED comparison reads path + '.orig'
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import (SEAT, PRISTINE, LANE, GITENV, git, write, commit, newrepo, sha, prereg, run,
                   compare, COUNTER, POP, CONTROL, std_repo)


def p_W26_ls_tree():
    """W26: --full-tree dropped from ls-tree -> paths are relative to the cwd."""
    d = newrepo("W26b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    return compare("ls-tree without --full-tree (repo with a nested path)", "W26", d)


def p_W27_merge_base():
    """W27: merge-base exit code 1 (not an ancestor) is treated as an ancestor."""
    d = newrepo("W27b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    git(d, "checkout", "-q", "-b", "side")
    write(d, "side.txt", "side\n")
    side = commit(d, "side")
    git(d, "checkout", "-q", "main")
    write(d, "prereg.txt", prereg(side))
    commit(d, "prereg")
    return compare("a Base on a branch that is not an ancestor of the freeze", "W27", d)


def p_W53_base_exception():
    """W53: Refusal derives from BaseException (KeyboardInterrupt no longer caught)."""
    d = std_repo("W53")
    return compare("Refusal as BaseException", "W53", d)


def p_W54_root_dot():
    """W54: --root gets a '/.' suffix."""
    d = std_repo("W54")
    prc, pl, _ = run(PRISTINE, d)
    mp = os.path.join(SEAT, "mutants", "W54.py")
    p = subprocess.run(["python3", "-B", mp, "--root", d + "/.", "--prereg", "prereg.txt",
                        "--rev", git(d, "rev-parse", "HEAD")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env=dict(GITENV, TMPDIR=d))
    ml = sorted(x for x in p.stdout.splitlines() if x.startswith("FINDING "))
    print("=== --root with a '/.' suffix [W54]")
    print("  pristine rc=%d %s" % (prc, " | ".join(pl) or "(no findings)"))
    print("  mutant   rc=%d %s" % (p.returncode, " | ".join(ml) or "(no findings)"))
    differ = (pl != ml or prc != p.returncode)
    print("  DIFFER=%s" % differ)
    return differ


def p_W55_fixed_path():
    """W55: PATH is hardcoded to /usr/bin:/bin (the caller's PATH is ignored)."""
    d = std_repo("W55")
    return compare("PATH hardcoded to /usr/bin:/bin", "W55", d)


def p_W56_rev_parse():
    """W56: rev-parse without -q."""
    d = std_repo("W56")
    return compare("rev-parse without -q", "W56", d)


def p_W57_ls_tree_dashdash():
    """W57: ls-tree without the '--' separator (a path that looks like an option)."""
    d = newrepo("W57b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("ls-tree without --", "W57", d)


def p_W58_header_search():
    """W58: HEADER.search instead of .match."""
    d = newrepo("W58b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    text = "# prereg\nRound: 42\n## C1 - claim 1\nBase: %s\nCounter: census/c1.py sha256=%s\n" \
           "Population: census/pop.tsv sha256=%s\nControl: census/control.txt\nTarget: t\nKill: k\n" \
           "prefix ## C2 - a heading inside a line\n" % (base, sha(COUNTER), sha(POP))
    write(d, "prereg.txt", text)
    commit(d, "prereg")
    return compare("a claim heading inside a line", "W58", d)


def p_W60_dup_lower():
    """W60: the duplicated key is stored lower-cased."""
    d = std_repo("W60", tail="Target: other\n")
    return compare("a duplicated key stored in lower case", "W60", d)


def p_W61_dup_empty():
    """W61: a duplicated key whose second value is empty becomes 'x'."""
    d = newrepo("W61b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys, tail="Target:\n"))
    commit(d, "prereg")
    return compare("a duplicated Target whose second value is empty", "W61", d)


def p_W62_ids_unfiltered():
    """W62: the freeze-detection ids are not filtered by FULL40."""
    d = std_repo("W62")
    return compare("the freeze ids are not filtered", "W62", d)


def p_W66_path_sha_strip():
    """W66: PATH_SHA.match(value.strip())."""
    d = std_repo("W66")
    return compare("PATH_SHA.match(value.strip())", "W66", d)


def p_W67_missing_upper():
    """W67: the missing-class name is upper-cased (it already is)."""
    d = std_repo("W67", keys=None)
    base = git(d, "rev-list", "--max-parents=0", "HEAD")
    keys = {"Base": base, "Counter": "census/absent.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg2")
    return compare("a Counter path absent at freeze", "W67", d)


def p_W68_want_lower():
    """W68: the digest is compared against want.lower()."""
    d = std_repo("W68")
    return compare("the digest compared against want.lower()", "W68", d)


def p_W69_orig_path():
    """W69: the FROZEN-EDITED comparison reads path + '.orig'."""
    d = newrepo("W69b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    write(d, "census/c1.py", COUNTER + "# edited after the freeze\n")
    commit(d, "edit counter")
    return compare("the counter edited after the freeze", "W69", d)


PROBES = {
    "W26": p_W26_ls_tree, "W27": p_W27_merge_base, "W53": p_W53_base_exception,
    "W54": p_W54_root_dot, "W55": p_W55_fixed_path, "W56": p_W56_rev_parse,
    "W57": p_W57_ls_tree_dashdash, "W58": p_W58_header_search, "W60": p_W60_dup_lower,
    "W61": p_W61_dup_empty, "W62": p_W62_ids_unfiltered, "W66": p_W66_path_sha_strip,
    "W67": p_W67_missing_upper, "W68": p_W68_want_lower, "W69": p_W69_orig_path,
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
