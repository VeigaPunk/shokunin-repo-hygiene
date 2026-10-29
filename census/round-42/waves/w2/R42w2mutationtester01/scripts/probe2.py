#!/usr/bin/env python3
"""Second-round directed probes for the r42 w2 mutation-tester survivors.

Each probe builds a synthetic git repo that exercises exactly the branch a
survivor mutant touches, then runs the PRISTINE tool and the MUTANT over the
same repo and diffs the FINDING lines.  DIFFER=True means the survivor is a
real behaviour change the counter's 37 cases and the tool's --selftest do not
observe; DIFFER=False means the mutant is behaviour-equivalent on that branch.
"""
import os
import shutil
import subprocess

SEAT = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester01"
PRISTINE = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py"
GITENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "HOME": SEAT, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
    "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid",
    "GIT_AUTHOR_DATE": "2026-10-28T00:00:00Z", "GIT_COMMITTER_DATE": "2026-10-28T00:00:00Z",
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
    d = os.path.join(SEAT, "probe2-repos", name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main", d)
    assert os.path.realpath(git(d, "rev-parse", "--show-toplevel")) == os.path.realpath(d)
    return d


def sha(text):
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prereg(base, ctr_sha=None, pop_sha=None, round_line="Round: 42\n", tail="", keys=None):
    k = keys if keys is not None else {
        "Base": base, "Counter": "census/c1.py sha256=%s" % (ctr_sha or sha(COUNTER)),
        "Population": "census/pop.tsv sha256=%s" % (pop_sha or sha(POP)),
        "Control": "census/control.txt", "Target": "items=2 corrected=2", "Kill": "any uncorrected"}
    return "# prereg\n%s\n## C1 - claim 1\n%s%s" % (round_line, "".join("%s: %s\n" % kv for kv in k.items()), tail)


def run(tool, d, prereg_path="prereg.txt"):
    p = subprocess.run(["python3", "-B", tool, "--root", d, "--prereg", prereg_path,
                        "--rev", git(d, "rev-parse", "HEAD")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env=dict(GITENV, TMPDIR=d))
    lines = [x for x in p.stdout.splitlines() if x.startswith("FINDING ")]
    tb = "Traceback" in p.stderr
    return p.returncode, sorted(lines), tb


def compare(tag, mid, d, prereg_path="prereg.txt"):
    prc, pl, ptb = run(PRISTINE, d, prereg_path)
    mp = os.path.join(SEAT, "mutants", mid + ".py")
    mrc, ml, mtb = run(mp, d, prereg_path)
    print("=== %s %s" % (tag, mid))
    print("  pristine rc=%d%s %s" % (prc, " TRACEBACK" if ptb else "", " | ".join(pl) or "(no findings)"))
    print("  mutant   rc=%d%s %s" % (mrc, " TRACEBACK" if mtb else "", " | ".join(ml) or "(no findings)"))
    print("  DIFFER=%s" % (pl != ml or prc != mrc))
    return pl != ml or prc != mrc


# ------------------------------------------------------------------ probes
def p_M02():
    """M02: FULL40 accepts uppercase hex -> a Base written in upper case resolves."""
    d = newrepo("M02")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base.upper()))
    commit(d, "prereg")
    return compare("uppercase Base hex", "M02", d)


def p_M03():
    """M03: FULL40 loses its end anchor -> a 40-hex Base with trailing junk still matches."""
    d = newrepo("M03")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", prereg(base + "JUNK"))
    commit(d, "prereg")
    return compare("Base with trailing junk", "M03", d)


def p_M13():
    """M13: ROUND loses BOM tolerance -> a BOM before 'Round:' hides the round number."""
    d = newrepo("M13")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    base = commit(d, "c1")
    write(d, "prereg.txt", "# prereg\n﻿Round: 42\n\n## C1 - claim 1\n"
          + "".join("%s: %s\n" % kv for kv in [
              ("Base", base), ("Counter", "census/c1.py sha256=%s" % sha(COUNTER)),
              ("Population", "census/pop.tsv sha256=%s" % sha(POP)),
              ("Control", "census/control.txt"), ("Target", "t"), ("Kill", "k")]))
    commit(d, "prereg")
    return compare("BOM before Round:", "M13", d)


def p_M14_M15():
    """M14/M15: EXIT_LINE anchors -> a control whose last line carries trailing junk."""
    for mid in ("M14", "M15"):
        d = newrepo(mid)
        write(d, "census/c1.py", COUNTER)
        write(d, "census/pop.tsv", POP)
        write(d, "census/control.txt", "SUMMARY items=2 corrected=0\nEXIT=1 (red)\n")
        base = commit(d, "c1")
        write(d, "prereg.txt", prereg(base))
        commit(d, "prereg")
        compare("control last line 'EXIT=1 (red)'", mid, d)


def p_M18():
    """M18: GIT_NO_REPLACE_OBJECTS dropped -> a git replace ref changes the freeze commit."""
    d = newrepo("M18")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    a = commit(d, "c1")
    write(d, "prereg.txt", prereg(a))
    b = commit(d, "prereg")
    write(d, "census/c1.py", COUNTER + "# later\n")
    c = commit(d, "edit")
    git(d, "replace", a, c)
    return compare("git replace ref on the prereg-adding commit", "M18", d)


def p_M19_M20():
    """M19/M20: env hardening drops (system config, mailmap)."""
    for mid in ("M19", "M20"):
        d = newrepo(mid)
        write(d, "census/c1.py", COUNTER)
        write(d, "census/pop.tsv", POP)
        write(d, "census/control.txt", CONTROL)
        write(d, ".mailmap", "Probe Person <probe@example.invalid> <real@example.invalid>\n")
        base = commit(d, "c1")
        write(d, "prereg.txt", prereg(base))
        commit(d, "prereg")
        compare("repo with a .mailmap", mid, d)


def p_M21_M30_M39_M41_M57_M63():
    """Equivalent-mutant checks: the changed expression is unobservable on its branch."""
    for mid in ("M21", "M30", "M39", "M41", "M57", "M63"):
        d = newrepo(mid)
        write(d, "census/c1.py", COUNTER)
        write(d, "census/pop.tsv", POP)
        write(d, "census/control.txt", CONTROL)
        base = commit(d, "c1")
        write(d, "prereg.txt", prereg(base, tail="Target: dup\n"))
        commit(d, "prereg")
        compare("plain prereg with a duplicated Target", mid, d)


def p_M24():
    """M24: is_symlink no longer normalises the path (a '..' component)."""
    d = newrepo("M24")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    os.makedirs(os.path.join(d, "census"), exist_ok=True)
    os.symlink("real-c1.py", os.path.join(d, "census", "link.py"))
    write(d, "census/real-c1.py", COUNTER)
    base = commit(d, "c1")
    keys = {"Base": base, "Counter": "census/./link.py sha256=%s" % sha(COUNTER),
            "Population": "census/pop.tsv sha256=%s" % sha(POP),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg(base, keys=keys))
    commit(d, "prereg")
    return compare("Counter path with a '.' component", "M24", d)


def p_M28_M29():
    """M28/M29: freeze_rev picks the newest instead of the oldest commit that adds the prereg."""
    d = newrepo("M28")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    a = commit(d, "c1")
    write(d, "prereg.txt", prereg(a, ctr_sha=sha("# counter v1\n")))
    commit(d, "prereg-v1")
    write(d, "census/c1.py", "# counter v2\n")
    commit(d, "edit-counter")
    os.remove(os.path.join(d, "prereg.txt"))
    commit(d, "drop-prereg")
    write(d, "prereg.txt", prereg(a, ctr_sha=sha("# counter v2\n")))
    commit(d, "prereg-v2")
    for mid in ("M28", "M29"):
        compare("prereg re-added after the counter changed", mid, d)


def p_M40():
    """M40: dispatch_findings keeps the newest instead of the oldest adding commit."""
    d = newrepo("M40")
    write(d, "census/c1.py", COUNTER)
    write(d, "census/pop.tsv", POP)
    write(d, "census/control.txt", CONTROL)
    write(d, ".ufo/waves/round-42/w1-spec.json", "{}\n")
    a = commit(d, "c1")
    write(d, "prereg.txt", prereg(a))
    commit(d, "prereg")           # freeze commit
    os.remove(os.path.join(d, ".ufo/waves/round-42/w1-spec.json"))
    commit(d, "drop-dispatch")
    write(d, ".ufo/waves/round-42/w1-spec.json", "{}\n")
    commit(d, "dispatch-after")
    return compare("dispatch file added before AND after the freeze", "M40", d)


def main():
    p_M02()
    p_M03()
    p_M13()
    p_M14_M15()
    p_M18()
    p_M19_M20()
    p_M21_M30_M39_M41_M57_M63()
    p_M24()
    p_M28_M29()
    p_M40()


if __name__ == "__main__":
    main()
