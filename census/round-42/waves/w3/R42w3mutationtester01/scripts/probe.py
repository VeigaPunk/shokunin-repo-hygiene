#!/usr/bin/env python3
"""Differential probes for the survivors of souji r42 wave-3 seat R42w3mutationtester01.

Each probe builds a synthetic git repository that exercises exactly the branch a
survivor mutant touches, then runs the PRISTINE tool and the MUTANT over the
same repository and diffs the exit code and the FINDING lines.

  DIFFER=True   the mutant is a real behaviour change that the counter's 37-case
                table and the tool's own --selftest do not observe  -> a GAP
  DIFFER=False  the mutant behaves identically on that branch          -> EQUIVALENT
                (agreement on probed inputs is evidence, not a proof over all inputs)

Written independently of the inherited w2 probe scripts; it reuses only the
frozen-tool-under-test and the git-fixture conventions the preregistration
prescribes (every git call names -C; identity only through the environment).
"""
import hashlib
import os
import shutil
import subprocess
import sys

SEAT = "/fast/scratch/hyaku/souji-r42/R42w3mutationtester01"
PRISTINE = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
GITENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "HOME": SEAT, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
    "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid",
    "GIT_AUTHOR_DATE": "2026-10-29T00:00:00Z", "GIT_COMMITTER_DATE": "2026-10-29T00:00:00Z",
}
COUNTER = "# counter\nprint('counter')\n"
POP = "id\tname\n1\talpha\n2\tbeta\n"
CONTROL = "SUMMARY items=2 corrected=0\nEXIT=1\n"


def git(d, *a, check=True):
    p = subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=GITENV, check=check, text=True)
    return p.stdout.strip()


def write(d, rel, text):
    fp = os.path.join(d, rel)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as fh:
        fh.write(text)


def commit(d, msg):
    git(d, "add", "-A")
    git(d, "commit", "-qm", msg)
    return git(d, "rev-parse", "HEAD")


def newrepo(name):
    d = os.path.join(SEAT, "probe-repos", name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main", d)
    assert os.path.realpath(git(d, "rev-parse", "--show-toplevel")) == os.path.realpath(d)
    return d


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prereg(base, ctr_sha=None, pop_sha=None, round_line="Round: 42\n", tail="", keys=None):
    k = keys if keys is not None else {
        "Base": base, "Counter": "census/c1.py sha256=%s" % (ctr_sha or sha(COUNTER)),
        "Population": "census/pop.tsv sha256=%s" % (pop_sha or sha(POP)),
        "Control": "census/control.txt", "Target": "items=2 corrected=2", "Kill": "any uncorrected"}
    return "# prereg\n%s\n## C1 - claim 1\n%s%s" % (round_line, "".join("%s: %s\n" % kv for kv in k.items()), tail)


def run(tool, d, prereg_path="prereg.txt", rev=None):
    p = subprocess.run(["python3", "-B", tool, "--root", d, "--prereg", prereg_path,
                        "--rev", rev or git(d, "rev-parse", "HEAD")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env=dict(GITENV, TMPDIR=d))
    lines = [x for x in p.stdout.splitlines() if x.startswith("FINDING ")]
    tb = "Traceback" in p.stderr
    return p.returncode, sorted(lines), tb


def compare(tag, mid, d, prereg_path="prereg.txt", rev=None):
    prc, pl, ptb = run(PRISTINE, d, prereg_path, rev)
    mp = os.path.join(SEAT, "mutants", mid + ".py")
    mrc, ml, mtb = run(mp, d, prereg_path, rev)
    print("=== %s [%s]" % (tag, mid))
    print("  pristine rc=%d%s %s" % (prc, " TRACEBACK" if ptb else "", " | ".join(pl) or "(no findings)"))
    print("  mutant   rc=%d%s %s" % (mrc, " TRACEBACK" if mtb else "", " | ".join(ml) or "(no findings)"))
    differ = (pl != ml or prc != mrc or ptb != mtb)
    print("  DIFFER=%s" % differ)
    return differ


def std_repo(name, keys=None, tail="", round_line="Round: 42\n", prereg_extra=None):
    """A standard synthetic repo with one clean claim."""
    d = newrepo(name)
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    text = prereg(base, tail=tail, round_line=round_line, keys=keys)
    if prereg_extra is not None:
        text = prereg_extra(text)
    write(d, "prereg.txt", text)
    commit(d, "prereg")
    return d


# ------------------------------------------------------------------ probes
def p_W08_upper_hex():
    """W08: FULL40 accepts \\w (uppercase hex and underscore)."""
    d = newrepo("W08")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base.upper(), "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP), "Control": "census/control.txt",
            "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("uppercase Base hex", "W08", d)


def p_W10_bare_digit_heading():
    """W10: BADHEAD accepts a bare '## 2' heading (no C)."""
    d = std_repo("W10", tail="## 2 - bare number\n")
    return compare("bare '## 2' heading", "W10", d)


def p_W13_empty_round_digits():
    """W13: ROUND's (\\d*) accepts 'Round:' with no digits -> round-'' tree."""
    d = std_repo("W13", round_line="Round: \n")
    return compare("Round: with no digits", "W13", d)


def p_W16_system_config():
    """W16: GIT_CONFIG_SYSTEM dropped from the whitelist."""
    d = std_repo("W16")
    return compare("GIT_CONFIG_SYSTEM dropped", "W16", d)


def p_W21_inherit_env():
    """W21: env=None -> the tool inherits the caller's environment (GIT_DIR can redirect it)."""
    d = std_repo("W21")
    decoy = newrepo("W21-decoy")
    write(decoy, "census/c1.py", "# decoy\n")
    write(decoy, "census/pop.tsv", POP)
    write(decoy, "census/control.txt", CONTROL)
    commit(decoy, "decoy")
    prc, pl, _ = run(PRISTINE, d)
    mp = os.path.join(SEAT, "mutants", "W21.py")
    env = dict(GITENV, GIT_DIR=os.path.join(decoy, ".git"), TMPDIR=d)
    p = subprocess.run(["python3", "-B", mp, "--root", d, "--prereg", "prereg.txt",
                        "--rev", git(d, "rev-parse", "HEAD")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, env=env)
    ml = sorted(x for x in p.stdout.splitlines() if x.startswith("FINDING "))
    print("=== hostile GIT_DIR in the caller's environment [W21]")
    print("  pristine rc=%d %s" % (prc, " | ".join(pl) or "(no findings)"))
    print("  mutant   rc=%d %s" % (p.returncode, " | ".join(ml) or "(no findings)"))
    differ = (pl != ml or prc != p.returncode)
    print("  DIFFER=%s" % differ)
    return differ


def p_W22_devnull_stderr():
    """W22: git stderr goes to /dev/null."""
    d = std_repo("W22")
    return compare("git stderr discarded", "W22", d)


def p_W23_rev_pec():
    """W23: rev-parse without ^{commit} -> a tag or a blob resolves."""
    d = std_repo("W23")
    return compare("rev resolved without ^{commit}", "W23", d)


def p_W25_blob_rc():
    """W25: blob() returns stdout even when git failed (empty bytes) -> COUNTER-MISSING lost."""
    d = std_repo("W25", keys=None)
    # rewrite the prereg to name a Counter path that does not exist
    base = git(d, "rev-list", "--max-parents=0", "HEAD")
    keys = {"Base": base, "Counter": "census/absent.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP), "Control": "census/control.txt",
            "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg2")
    return compare("Counter path absent at freeze", "W25", d)


def p_W27_merge_base_rc():
    """W27: merge-base exit code 1 (not an ancestor) counted as an ancestor."""
    d = std_repo("W27")
    return compare("merge-base exit 1 treated as ancestor", "W27", d)


def p_W29_crlf():
    """W29: text.split('\\n') keeps the CR of a CRLF file."""
    d = std_repo("W29")
    base = git(d, "rev-list", "--max-parents=0", "HEAD")
    body = prereg(base).replace("\n", "\r\n")
    write(d, "prereg.txt", body)
    commit(d, "prereg-crlf")
    return compare("CRLF preregistration", "W29", d)


def p_W30_subheading_closes():
    """W30: a '### ' sub-heading also closes the claim block."""
    d = std_repo("W30", tail="### C 9\n")
    return compare("'### ' sub-heading closes the claim", "W30", d)


def p_W31_dup_same_value():
    """W31: a duplicated key with an IDENTICAL value is not reported as KEY-DUPLICATE."""
    d = std_repo("W31", tail="Target: items=2 corrected=2\n")
    return compare("duplicated key, identical value", "W31", d)


def p_W32_full_history():
    """W32: --full-history dropped from the freeze-detection log."""
    d = newrepo("W32")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    # a merge commit that brings the prereg in from a side branch
    git(d, "checkout", "-q", "-b", "side")
    write(d, "side.txt", "side\n")
    commit(d, "side")
    git(d, "checkout", "-q", "main")
    git(d, "merge", "-q", "--no-ff", "-m", "merge side", "side")
    return compare("prereg added on a merged side branch", "W32", d)


def p_W33_no_renames():
    """W33: --no-renames dropped from the freeze-detection log."""
    d = newrepo("W33")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    git(d, "mv", "prereg.txt", "prereg-renamed.txt")
    commit(d, "rename prereg")
    git(d, "mv", "prereg-renamed.txt", "prereg.txt")
    commit(d, "rename back")
    return compare("prereg renamed and renamed back", "W33", d)


def p_W34_round_match():
    """W34: ROUND.match instead of .search -> the Round line must be at the very top."""
    d = newrepo("W34")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", "# a leading comment\n" + prereg(base))
    commit(d, "prereg")
    return compare("Round: line not first in the file", "W34", d)


def p_W35_results_json():
    """W35: every .json under the wave tree counts as a dispatch file."""
    d = newrepo("W35")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    write(d, ".ufo/waves/round-42/notes.json", "{}\n")
    commit(d, "notes json before freeze")
    return compare("a .json file under the wave tree", "W35", d)


def p_W36_short_commit():
    """W36: the dispatch commit id is truncated to 12 hex before the ancestry test."""
    d = newrepo("W36")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    write(d, ".ufo/waves/round-42/w1-dispatch.json", "{}\n")
    commit(d, "dispatch before freeze")
    return compare("dispatch file added before the freeze", "W36", d)


def p_W37_no_path():
    """W37: the PATH_SHA fallback yields an empty path -> the Counter is never checked."""
    d = std_repo("W37", keys=None)
    base = git(d, "rev-list", "--max-parents=0", "HEAD")
    keys = {"Base": base, "Counter": "census/c1.py", "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg2")
    return compare("Counter value without a sha256", "W37", d)


def p_W38_empty_path_guard():
    """W38: the 'if not path' guard is gone."""
    d = std_repo("W38", keys=None)
    base = git(d, "rev-list", "--max-parents=0", "HEAD")
    keys = {"Base": base, "Counter": "", "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg2")
    return compare("empty Counter value", "W38", d)


def p_W39_blob_at_rev():
    """W39: the digest is taken at REV, not at FREEZE."""
    d = newrepo("W39")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    write(d, "census/c1.py", COUNTER + "# edited after the freeze\n")
    commit(d, "edit counter")
    return compare("counter edited after the freeze", "W39", d)


def p_W40_empty_blob():
    """W40: an empty blob at freeze counts as missing."""
    d = newrepo("W40")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(""),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    write(d, "census/c1.py", "")
    commit(d, "empty counter")
    return compare("empty counter file at freeze", "W40", d)


def p_W41_symlink_at_rev():
    """W41: the symlink test runs at REV, not at FREEZE."""
    d = newrepo("W41")
    write(d, "census/real-c1.py", COUNTER)
    os.symlink("real-c1.py", os.path.join(d, "census/c1.py"))
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    # replace the symlink with a regular file AFTER the freeze
    os.unlink(os.path.join(d, "census/c1.py"))
    write(d, "census/c1.py", COUNTER)
    commit(d, "symlink replaced")
    return compare("counter was a symlink at freeze, a file at rev", "W41", d)


def p_W45_crlf_normalise():
    """W45: parse_claims normalises CRLF before parsing."""
    d = std_repo("W45")
    base = git(d, "rev-list", "--max-parents=0", "HEAD")
    write(d, "prereg.txt", prereg(base).replace("\n", "\r\n"))
    commit(d, "prereg-crlf")
    return compare("CRLF preregistration (normalised)", "W45", d)


def p_W46_one_bad_heading():
    """W46: only the FIRST malformed heading is reported."""
    d = std_repo("W46", tail="##C2 - one\n##C3 - two\n")
    return compare("two malformed headings", "W46", d)


def p_W47_no_claims_and_bad():
    """W47: NO-CLAIMS is not reported when a malformed heading is also present."""
    d = newrepo("W47")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", "# prereg\nRound: 42\nno claims here\n##C2 - malformed\n")
    commit(d, "prereg")
    return compare("no claims AND a malformed heading", "W47", d)


def p_W48_first_claim_only():
    """W48: only the first claim block is evaluated."""
    d = newrepo("W48")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    good = prereg(base)
    body = good.split("## C1 - claim 1\n")[1]
    write(d, "prereg.txt", "# prereg\nRound: 42\n## C1 - claim 1\n" + body +
          "## C2 - claim 2\nTarget: t\n")
    commit(d, "prereg")
    return compare("two claims, the second missing keys", "W48", d)


def p_W50_kill_key():
    """W50: the 'Kill' key is not checked for FIELD-MISSING."""
    d = newrepo("W50")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("a claim with no Kill key", "W50", d)


def p_W53_base_exception():
    """W53: Refusal derives from BaseException."""
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
    """W55: PATH is hardcoded to /usr/bin:/bin."""
    d = std_repo("W55")
    return compare("PATH hardcoded", "W55", d)


def p_W56_rev_parse_verbose():
    """W56: rev-parse without -q."""
    d = std_repo("W56")
    return compare("rev-parse without -q", "W56", d)


def p_W57_ls_tree_no_dashdash():
    """W57: ls-tree without the '--' separator."""
    d = std_repo("W57")
    return compare("ls-tree without --", "W57", d)


def p_W58_header_search():
    """W58: HEADER.search instead of .match."""
    d = std_repo("W58", tail="prefix ## C3 - later claim\n")
    return compare("a claim heading not at the start of the line", "W58", d)


def p_W60_dup_lowercase():
    """W60: the duplicated key is lowercased in the finding."""
    d = std_repo("W60", tail="Target: other\n")
    return compare("duplicated key reported in lower case", "W60", d)


def p_W61_or_x():
    """W61: a duplicated key's second value falls back to 'x'."""
    d = std_repo("W61", tail="Target: other\n")
    return compare("duplicated Target with a non-empty second value", "W61", d)


def p_W62_ids_no_filter():
    """W62: the freeze-detection ids are not filtered by FULL40."""
    d = std_repo("W62")
    return compare("freeze ids not filtered", "W62", d)


def p_W63_split_n():
    """W63: the dispatch log is split on '\\n' rather than splitlines()."""
    d = newrepo("W63")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    write(d, ".ufo/waves/round-42/w1-dispatch.json", "{}\n")
    commit(d, "dispatch before freeze")
    return compare("dispatch file added before the freeze", "W63", d)


def p_W64_commit_none():
    """W64: a name line before any commit header is accepted."""
    d = newrepo("W64")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    write(d, ".ufo/waves/round-42/w1-dispatch.json", "{}\n")
    commit(d, "dispatch before freeze")
    return compare("dispatch file added before the freeze", "W64", d)


def p_W66_path_sha_strip():
    """W66: PATH_SHA.match(value.strip())."""
    d = std_repo("W66")
    return compare("Counter value with surrounding spaces", "W66", d)


def p_W69_orig_path():
    """W69: the FROZEN-EDITED comparison reads path + '.orig'."""
    d = newrepo("W69")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base))
    commit(d, "prereg")
    write(d, "census/c1.py", COUNTER + "# edited after the freeze\n")
    commit(d, "edit counter")
    return compare("counter edited after the freeze", "W69", d)


def p_W72_kill_field_missing():
    """W72: 'Kill' is exempt from FIELD-MISSING."""
    d = newrepo("W72")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("a claim with no Kill key", "W72", d)


def p_lane_r42(mids):
    """The lane's OWN r42 preregistration at the tip (the counter's `real` leg)."""
    rev = git(LANE, "rev-parse", "HEAD")
    prc, pl, _ = run(PRISTINE, LANE, "census/round-42/preregistration.txt", rev)
    print("=== the lane's own r42 preregistration at %s" % rev[:12])
    print("  PRISTINE rc=%d %s" % (prc, " | ".join(pl) or "(no findings)"))
    for mid in mids:
        mp = os.path.join(SEAT, "mutants", mid + ".py")
        if not os.path.exists(mp):
            continue
        mrc, ml, mtb = run(mp, LANE, "census/round-42/preregistration.txt", rev)
        print("  %-6s rc=%d%s %s" % (mid, mrc, " TRACEBACK" if mtb else "",
                                    " | ".join(ml) or "(no findings)"))
        print("  DIFFER=%s" % (pl != ml or prc != mrc))
    return None


PROBES = {
    "W08": p_W08_upper_hex, "W10": p_W10_bare_digit_heading, "W13": p_W13_empty_round_digits,
    "W16": p_W16_system_config, "W21": p_W21_inherit_env, "W22": p_W22_devnull_stderr,
    "W23": p_W23_rev_pec, "W25": p_W25_blob_rc, "W27": p_W27_merge_base_rc,
    "W29": p_W29_crlf, "W30": p_W30_subheading_closes, "W31": p_W31_dup_same_value,
    "W32": p_W32_full_history, "W33": p_W33_no_renames, "W34": p_W34_round_match,
    "W35": p_W35_results_json, "W36": p_W36_short_commit, "W37": p_W37_no_path,
    "W38": p_W38_empty_path_guard, "W39": p_W39_blob_at_rev, "W40": p_W40_empty_blob,
    "W41": p_W41_symlink_at_rev, "W45": p_W45_crlf_normalise, "W46": p_W46_one_bad_heading,
    "W47": p_W47_no_claims_and_bad, "W48": p_W48_first_claim_only, "W50": p_W50_kill_key,
    "W53": p_W53_base_exception, "W54": p_W54_root_dot, "W55": p_W55_fixed_path,
    "W56": p_W56_rev_parse_verbose, "W57": p_W57_ls_tree_no_dashdash,
    "W58": p_W58_header_search, "W60": p_W60_dup_lowercase, "W61": p_W61_or_x,
    "W62": p_W62_ids_no_filter, "W63": p_W63_split_n, "W64": p_W64_commit_none,
    "W66": p_W66_path_sha_strip, "W69": p_W69_orig_path, "W72": p_W72_kill_field_missing,
}


def main():
    want = sys.argv[1:] or sorted(PROBES)
    for mid in want:
        if mid == "lane":
            p_lane_r42(sorted(PROBES))
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
