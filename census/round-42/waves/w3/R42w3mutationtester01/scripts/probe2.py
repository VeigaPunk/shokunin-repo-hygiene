#!/usr/bin/env python3
"""Second probe set for R42w3mutationtester01: corrected dispatch scenarios and
the survivors the first probe set did not reach.

Corrections to the first set:
  * the dispatch probes must add the wave file BEFORE the freeze commit (the
    dispatch check asks "was it added by FREEZE-REV or an ancestor of it");
  * the '### ' sub-heading probe must place the sub-heading BEFORE the keys it
    would swallow;
  * the --full-history and --no-renames probes need the freeze-detection log to
    be observed directly, not only through the tool's verdict.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import (SEAT, PRISTINE, LANE, GITENV, git, write, commit, newrepo, sha, prereg, run,
                   compare, COUNTER, POP, CONTROL, std_repo)


def dispatch_repo(name, wavefile, extra_commits=()):
    """A repo where the wave file is added BEFORE the prereg (so before the freeze)."""
    d = newrepo(name)
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, wavefile, "{}\n")
    commit(d, "wave file before the freeze")
    for msg, rel, text in extra_commits:
        write(d, rel, text)
        commit(d, msg)
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    return d


def p_W30_subheading_swallows():
    """W30: a '### ' sub-heading also closes the claim block (keys after it are lost)."""
    d = newrepo("W30b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    text = ("# prereg\nRound: 42\n## C1 - claim 1\nBase: %s\n### C 9\nCounter: census/c1.py sha256=%s\n"
            % (base, sha(COUNTER)))
    write(d, "prereg.txt", text)
    commit(d, "prereg")
    return compare("'### ' sub-heading swallows the keys after it", "W30", d)


def p_W35_json_before_freeze():
    """W35: every .json under the wave tree counts as a dispatch file."""
    d = dispatch_repo("W35b", ".ufo/waves/round-42/notes.json")
    return compare("a notes.json under the wave tree, added before the freeze", "W35", d)


def p_W36_truncated_commit():
    """W36: the dispatch commit id is truncated to 12 hex before the comparison."""
    d = dispatch_repo("W36b", ".ufo/waves/round-42/w1-dispatch.json")
    return compare("dispatch file added before the freeze (id truncated to 12)", "W36", d)


def p_W63_split_n_dispatch():
    """W63: the dispatch log is split on '\\n' rather than splitlines()."""
    d = dispatch_repo("W63b", ".ufo/waves/round-42/w1-dispatch.json")
    return compare("dispatch file added before the freeze (log split on \\n)", "W63", d)


def p_W64_commit_none_dispatch():
    """W64: a name line before any commit header is accepted."""
    d = dispatch_repo("W64b", ".ufo/waves/round-42/w1-dispatch.json")
    return compare("dispatch file added before the freeze (commit may be None)", "W64", d)


def p_W32_full_history():
    """W32: --full-history dropped -> the freeze-detection log misses a side-branch add."""
    d = newrepo("W32b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    git(d, "checkout", "-q", "-b", "side")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg on the side branch")
    git(d, "checkout", "-q", "main")
    git(d, "merge", "-q", "--no-ff", "-m", "merge side", "side")
    tip = git(d, "rev-parse", "HEAD")
    for flags, tag in ((("--diff-filter=A", "--no-renames", "--full-history", "--reverse"), "with --full-history"),
                       (("--diff-filter=A", "--no-renames", "--reverse"), "without --full-history")):
        out = git(d, "log", *flags, "--format=%H", tip, "--", "prereg.txt")
        print("=== W32 freeze-detection log %s: %s" % (tag, out.replace("\n", " ") or "(nothing)"))
    return compare("prereg added on a merged side branch", "W32", d)


def p_W33_no_renames():
    """W33: --no-renames dropped -> a renamed prereg is not seen as an add."""
    d = newrepo("W33b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    git(d, "mv", "prereg.txt", "prereg-moved.txt")
    commit(d, "rename prereg away")
    git(d, "mv", "prereg-moved.txt", "prereg.txt")
    commit(d, "rename it back")
    tip = git(d, "rev-parse", "HEAD")
    for flags, tag in ((("--diff-filter=A", "--no-renames", "--full-history", "--reverse"), "with --no-renames"),
                       (("--diff-filter=A", "--full-history", "--reverse"), "without --no-renames")):
        out = git(d, "log", *flags, "--format=%H", tip, "--", "prereg.txt")
        print("=== W33 freeze-detection log %s: %s" % (tag, out.replace("\n", " ") or "(nothing)"))
    return compare("prereg renamed away and back", "W33", d)


def p_W11_tab_after_colon():
    """W11: KEYLINE accepts only a space (not a tab) after the colon."""
    d = newrepo("W11")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    text = ("# prereg\nRound: 42\n## C1 - claim 1\nBase:\t%s\nCounter:\tcensus/c1.py sha256=%s\n"
            "Population:\tcensus/pop.tsv sha256=%s\nControl:\tcensus/control.txt\nTarget:\tt\nKill:\tk\n"
            % (base, sha(COUNTER), sha(POP)))
    write(d, "prereg.txt", text)
    commit(d, "prereg")
    return compare("a TAB after the key colon", "W11", d)


def p_W12_short_digest():
    """W12: PATH_SHA accepts a 32-hex digest."""
    d = std_repo("W12")
    base = git(d, "rev-list", "--max-parents=0", "HEAD")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER)[:32],
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg2")
    return compare("a 32-hex digest in the Counter value", "W12", d)


def p_W14_control_trailing_ws():
    """W14: EXIT_LINE accepts trailing whitespace."""
    d = newrepo("W14")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", "SUMMARY items=2 corrected=0\nEXIT=1 \n")
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    return compare("a control whose last line has trailing whitespace", "W14", d)


def p_W15_keys_order():
    """W15: KEYS is reordered -> the order of the FIELD-MISSING findings."""
    d = newrepo("W15")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", "# prereg\nRound: 42\n## C1 - claim 1\nTarget: t\n")
    commit(d, "prereg")
    return compare("a claim with several missing keys", "W15", d)


def p_W18_lc_all():
    """W18: LC_ALL=C.UTF-8 instead of C."""
    d = std_repo("W18")
    return compare("LC_ALL=C.UTF-8", "W18", d)


def p_W19_quotepath():
    """W19: -c core.quotePath=false dropped -> a non-ASCII path is quoted by git."""
    d = newrepo("W19")
    write(d, "census/contrôle.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/contrôle.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("a non-ASCII Counter path", "W19", d)


def p_W26_ls_tree_full_tree():
    """W26: --full-tree dropped from ls-tree."""
    d = std_repo("W26")
    return compare("ls-tree without --full-tree", "W26", d)


def p_W28_line_numbers():
    """W28: the line numbers of the HEADING-MALFORMED findings shift by one."""
    d = std_repo("W28", tail="##C2 - malformed\n")
    return compare("the line number of a HEADING-MALFORMED finding", "W28", d)


def p_W49_dups_order():
    """W49: the duplicated keys are listed in reverse order."""
    d = std_repo("W49", tail="Target: other\nKill: other\n")
    return compare("two duplicated keys listed in reverse order", "W49", d)


def p_W59_badhead_search():
    """W59: BADHEAD.search instead of .match."""
    d = std_repo("W59", tail="prefix ## C2 - malformed\n")
    return compare("a malformed heading not at the start of the line", "W59", d)


def p_W67_missing_upper():
    """W67: the missing-class name is upper-cased."""
    d = std_repo("W67", keys=None)
    base = git(d, "rev-list", "--max-parents=0", "HEAD")
    keys = {"Base": base, "Counter": "census/absent.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg2")
    return compare("a Counter path absent at freeze", "W67", d)


def p_W70_no_claims_detail():
    """W70: the NO-CLAIMS detail text changes (the class does not)."""
    d = newrepo("W70")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", "# prereg\nRound: 42\nno claims here\n")
    commit(d, "prereg")
    return compare("a preregistration with no claims (detail text)", "W70", d)


def p_W71_dup_key_upper():
    """W71: the duplicated key is reported in upper case."""
    d = std_repo("W71", tail="Target: other\n")
    return compare("a duplicated key reported in upper case", "W71", d)


def p_W17_terminal_prompt():
    """W17: GIT_TERMINAL_PROMPT=1 -> git may prompt for credentials."""
    d = std_repo("W17")
    return compare("GIT_TERMINAL_PROMPT=1", "W17", d)


def p_lane(mids):
    """The lane's OWN r42 preregistration at the tip (the counter's `real` leg)."""
    rev = git(LANE, "rev-parse", "HEAD")
    prc, pl, _ = run(PRISTINE, LANE, "census/round-42/preregistration.txt", rev)
    print("=== the lane's own r42 preregistration at %s" % rev[:12])
    print("  PRISTINE rc=%d %s" % (prc, " | ".join(pl) or "(no findings)"))
    for mid in mids:
        mp = os.path.join(SEAT, "mutants", mid + ".py")
        if not os.path.exists(mp):
            print("  %-6s (no mutant file)" % mid)
            continue
        mrc, ml, mtb = run(mp, LANE, "census/round-42/preregistration.txt", rev)
        print("  %-6s rc=%d%s %s" % (mid, mrc, " TRACEBACK" if mtb else "",
                                    " | ".join(ml) or "(no findings)"))
        print("  DIFFER=%s" % (pl != ml or prc != mrc))
    return None


PROBES = {
    "W11": p_W11_tab_after_colon, "W12": p_W12_short_digest, "W14": p_W14_control_trailing_ws,
    "W15": p_W15_keys_order, "W17": p_W17_terminal_prompt, "W18": p_W18_lc_all,
    "W19": p_W19_quotepath, "W26": p_W26_ls_tree_full_tree, "W28": p_W28_line_numbers,
    "W30": p_W30_subheading_swallows, "W32": p_W32_full_history, "W33": p_W33_no_renames,
    "W35": p_W35_json_before_freeze, "W36": p_W36_truncated_commit, "W49": p_W49_dups_order,
    "W59": p_W59_badhead_search, "W63": p_W63_split_n_dispatch, "W64": p_W64_commit_none_dispatch,
    "W67": p_W67_missing_upper, "W70": p_W70_no_claims_detail, "W71": p_W71_dup_key_upper,
}


def main():
    want = sys.argv[1:] or sorted(PROBES)
    for mid in want:
        if mid == "lane":
            p_lane(["M61", "M62", "W61", "W62", "W63", "W08", "W13"])
            continue
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
