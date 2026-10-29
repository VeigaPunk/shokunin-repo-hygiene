#!/usr/bin/env python3
"""Fifth probe set for R42w3mutationtester01: the last survivors whose mutated
branch is not yet exercised by a scenario that DISCRIMINATES it.

For each, the probe builds a scenario in which the mutated branch is reached
AND the pristine and the mutant can be told apart.

  W11  KEYLINE accepts only a space after the colon (a TAB)   -- probe1
  W12  PATH_SHA accepts a 32-hex digest                        -- probe2
  W14  EXIT_LINE accepts trailing whitespace                   -- probe2
  W15  KEYS is reordered (the order of the FIELD-MISSING findings)
  W16  GIT_CONFIG_SYSTEM dropped from the whitelist
  W17  GIT_TERMINAL_PROMPT=1
  W18  LC_ALL=C.UTF-8
  W19  -c core.quotePath=false dropped
  W21  env=None (the tool inherits the caller's environment)   -- probe1
  W22  git's stderr goes to /dev/null
  W26  ls-tree without --full-tree
  W28  the line numbers of the HEADING-MALFORMED findings shift by one
  W30  a '### ' sub-heading also closes the claim block         -- probe2
  W35  every .json under the wave tree is a dispatch file        -- probe2
  W36  the dispatch commit id is truncated to 12 hex
  W37  the PATH_SHA fallback yields an empty path                -- probe1
  W38  the 'if not path' guard is gone
  W40  an empty blob at the freeze counts as missing            -- probe4
  W41  the symlink test runs at REV, not at FREEZE               -- probe1
  W45  parse_claims normalises CRLF
  W46  only the FIRST malformed heading is reported
  W49  the duplicated keys are listed in reverse order
  W53  Refusal derives from BaseException
  W54  --root gets a '/.' suffix
  W55  PATH is hardcoded to /usr/bin:/bin
  W56  rev-parse without -q
  W57  ls-tree without the '--' separator
  W58  HEADER.search instead of .match
  W59  BADHEAD.search instead of .match
  W62  the freeze-detection ids are not filtered by FULL40
  W63  the dispatch log is split on '\n' rather than splitlines()
  W64  a name line before any commit header is accepted
  W66  PATH_SHA.match(value.strip())
  W67  the missing-class name is upper-cased
  W68  the digest is compared against want.lower()
  W69  the FROZEN-EDITED comparison reads path + '.orig'
  W70  the NO-CLAIMS detail text changes
  W71  the duplicated key is reported in upper case
  W08  FULL40 accepts \w (uppercase hex)                         -- probe1
  W13  ROUND's (\d*) accepts 'Round:' with no digits             -- probe1
  W21/W25/W27/W29/W31/W34/W37/W39/W41/W46/W48/W50/W72 already discriminated in probe1.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import (SEAT, PRISTINE, LANE, GITENV, git, write, commit, newrepo, sha, prereg, run,
                   compare, COUNTER, POP, CONTROL, std_repo)


def p_W15_keys_order():
    """W15: KEYS is reordered -> the order of the FIELD-MISSING findings differs."""
    d = newrepo("W15b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", "# prereg\nRound: 42\n## C1 - claim 1\nTarget: t\n")
    commit(d, "prereg")
    return compare("a claim with several missing keys (KEYS reordered)", "W15", d)


def p_W16_system_config():
    """W16: GIT_CONFIG_SYSTEM dropped -> the system config is read."""
    d = std_repo("W16b")
    return compare("GIT_CONFIG_SYSTEM dropped from the whitelist", "W16", d)


def p_W17_terminal_prompt():
    """W17: GIT_TERMINAL_PROMPT=1."""
    d = std_repo("W17b")
    return compare("GIT_TERMINAL_PROMPT=1", "W17", d)


def p_W18_lc_all_utf8():
    """W18: LC_ALL=C.UTF-8 (git's path quoting and message localisation)."""
    d = newrepo("W18b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("LC_ALL=C.UTF-8", "W18", d)


def p_W19_quotepath_symlink():
    """W19: -c core.quotePath=false dropped (a non-ASCII path is quoted by git)."""
    d = newrepo("W19b")
    write(d, "census/contrôle.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/contrôle.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("a non-ASCII Counter path (core.quotePath dropped)", "W19", d)


def p_W22_stderr_devnull():
    """W22: git's stderr goes to /dev/null instead of a pipe."""
    d = std_repo("W22b")
    return compare("git stderr discarded", "W22", d)


def p_W26_full_tree():
    """W26: --full-tree dropped from ls-tree."""
    d = std_repo("W26c")
    return compare("ls-tree without --full-tree", "W26", d)


def p_W36_truncated_commit_dispatch():
    """W36: the dispatch commit id is truncated to 12 hex."""
    d = newrepo("W36c")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, ".ufo/waves/round-42/w1-dispatch.json", "{}\n")
    commit(d, "wave file before the freeze")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    return compare("a dispatch file added before the freeze (id truncated to 12)", "W36", d)


def p_W38_empty_path_guard():
    """W38: the 'if not path' guard is gone (a Counter value with no token)."""
    d = newrepo("W38b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": " ", "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("a Counter value that is a single space", "W38", d)


def p_W45_crlf_normalise():
    """W45: parse_claims normalises CRLF before parsing."""
    d = newrepo("W45b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base).replace("\n", "\r\n"))
    commit(d, "prereg-crlf")
    return compare("a CRLF preregistration (normalised before parsing)", "W45", d)


def p_W53_base_exception():
    """W53: Refusal derives from BaseException."""
    d = std_repo("W53b")
    return compare("Refusal as BaseException", "W53", d)


def p_W54_root_dot():
    """W54: --root gets a '/.' suffix."""
    d = std_repo("W54b")
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
    """W55: PATH is hardcoded to /usr/bin:/bin."""
    d = std_repo("W55b")
    return compare("PATH hardcoded to /usr/bin:/bin", "W55", d)


def p_W56_rev_parse_no_q():
    """W56: rev-parse without -q."""
    d = std_repo("W56b")
    return compare("rev-parse without -q", "W56", d)


def p_W57_ls_tree_dashdash():
    """W57: ls-tree without the '--' separator."""
    d = std_repo("W57b")
    return compare("ls-tree without --", "W57", d)


def p_W58_header_search():
    """W58: HEADER.search instead of .match (a heading with leading text)."""
    d = newrepo("W58b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    text = ("# prereg\nRound: 42\n## C1 - claim 1\nBase: %s\nCounter: census/c1.py sha256=%s\n"
            "Population: census/pop.tsv sha256=%s\nControl: census/control.txt\nTarget: t\nKill: k\n"
            "x ## C2 - a heading with leading text\n" % (base, sha(COUNTER), sha(POP)))
    write(d, "prereg.txt", text)
    commit(d, "prereg")
    return compare("a heading with leading text (HEADER.search)", "W58", d)


def p_W59_badhead_search():
    """W59: BADHEAD.search instead of .match."""
    d = newrepo("W59b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    text = ("# prereg\nRound: 42\n## C1 - claim 1\nBase: %s\nCounter: census/c1.py sha256=%s\n"
            "Population: census/pop.tsv sha256=%s\nControl: census/control.txt\nTarget: t\nKill: k\n"
            "x ## C2 - a malformed heading with leading text\n" % (base, sha(COUNTER), sha(POP)))
    write(d, "prereg.txt", text)
    commit(d, "prereg")
    return compare("a malformed heading with leading text (BADHEAD.search)", "W59", d)


def p_W62_ids_unfiltered():
    """W62: the freeze-detection ids are not filtered by FULL40."""
    d = std_repo("W62b")
    return compare("the freeze ids are not filtered by FULL40", "W62", d)


def p_W63_dispatch_split_n():
    """W63: the dispatch log is split on '\\n' rather than splitlines()."""
    d = newrepo("W63b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, ".ufo/waves/round-42/w1-dispatch.json", "{}\n")
    commit(d, "wave file before the freeze")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    return compare("a dispatch file before the freeze (log split on \\n)", "W63", d)


def p_W64_commit_none():
    """W64: a name line before any commit header is accepted."""
    d = newrepo("W64b")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, ".ufo/waves/round-42/w1-dispatch.json", "{}\n")
    commit(d, "wave file before the freeze")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    return compare("a dispatch file before the freeze (commit may be None)", "W64", d)


def p_W66_path_sha_strip():
    """W66: PATH_SHA.match(value.strip())."""
    d = std_repo("W66b")
    return compare("PATH_SHA.match(value.strip())", "W66", d)


def p_W67_missing_upper():
    """W67: the missing-class name is upper-cased."""
    d = std_repo("W67b", keys=None)
    base = git(d, "rev-list", "--max-parents=0", "HEAD")
    keys = {"Base": base, "Counter": "census/absent.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg2")
    return compare("a Counter path absent at freeze", "W67", d)


def p_W68_want_lower():
    """W68: the digest is compared against want.lower()."""
    d = std_repo("W68b")
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


def p_W71_dup_upper():
    """W71: the duplicated key is reported in upper case."""
    d = std_repo("W71b", tail="Target: other\n")
    return compare("a duplicated key reported in upper case", "W71", d)


def p_W28_line_numbers():
    """W28: the line numbers of the HEADING-MALFORMED findings shift by one."""
    d = std_repo("W28b", tail="##C2 - malformed\n")
    return compare("the line number of a HEADING-MALFORMED finding", "W28", d)


def p_W49_dups_order():
    """W49: the duplicated keys are listed in reverse order."""
    d = std_repo("W49b", tail="Target: other\nKill: other\n")
    return compare("two duplicated keys listed in reverse order", "W49", d)


PROBES = {
    "W15": p_W15_keys_order, "W16": p_W16_system_config, "W17": p_W17_terminal_prompt,
    "W18": p_W18_lc_all_utf8, "W19": p_W19_quotepath_symlink, "W22": p_W22_stderr_devnull,
    "W26": p_W26_full_tree, "W28": p_W28_line_numbers, "W36": p_W36_truncated_commit_dispatch,
    "W38": p_W38_empty_path_guard, "W45": p_W45_crlf_normalise, "W49": p_W49_dups_order,
    "W53": p_W53_base_exception, "W54": p_W54_root_dot, "W55": p_W55_fixed_path,
    "W56": p_W56_rev_parse_no_q, "W57": p_W57_ls_tree_dashdash, "W58": p_W58_header_search,
    "W59": p_W59_badhead_search, "W62": p_W62_ids_unfiltered, "W63": p_W63_dispatch_split_n,
    "W64": p_W64_commit_none, "W66": p_W66_path_sha_strip, "W67": p_W67_missing_upper,
    "W68": p_W68_want_lower, "W69": p_W69_orig_path, "W71": p_W71_dup_upper,
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
