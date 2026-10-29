#!/usr/bin/env python3
"""Directed differential probes for the survivors of souji r42 wave-2 seat R42w2mutationtester01.

For each survivor mutant, build a synthetic git repo that exercises the branch the
mutant touches, then run the PRISTINE tool and the MUTANT over the same repo and
compare the FINDING lines.  A difference proves the survivor is a real behaviour
change that the counter's 37 cases and the tool's --selftest do not observe.
Everything lives under the seat scratch; no lane file is touched.
"""
import os
import shutil
import subprocess
import sys

SEAT = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester01"
PRISTINE = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py"
GITENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "HOME": SEAT, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
    "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid",
    "GIT_AUTHOR_DATE": "2026-10-28T00:00:00Z", "GIT_COMMITTER_DATE": "2026-10-28T00:00:00Z",
}


def git(d, *a):
    p = subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=GITENV, check=True, text=True)
    return p.stdout.strip()


def write(d, rel, text):
    fp = os.path.join(d, rel)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as fh:
        fh.write(text)


def build(name, files, later=()):
    """files: {rel: content} committed as ONE commit; later: list of dicts committed after."""
    d = os.path.join(SEAT, "probe-repos", name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main", d)
    assert os.path.realpath(git(d, "rev-parse", "--show-toplevel")) == os.path.realpath(d), d
    for rel, content in files.items():
        write(d, rel, content)
    git(d, "add", "-A")
    git(d, "commit", "-qm", "c1")
    for i, more in enumerate(later):
        for rel, content in more.items():
            if content is None:
                os.remove(os.path.join(d, rel))
            else:
                write(d, rel, content)
        git(d, "add", "-A")
        git(d, "commit", "-qm", "c%d" % (i + 2))
    return d


def run(tool, d, prereg="prereg.txt"):
    p = subprocess.run(["python3", "-B", tool, "--root", d, "--prereg", prereg,
                        "--rev", git(d, "rev-parse", "HEAD")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env=dict(GITENV, TMPDIR=d))
    lines = [x for x in p.stdout.splitlines() if x.startswith("FINDING ")]
    return p.returncode, sorted(lines)


def show(tag, rc, lines):
    print("  %-10s rc=%d %s" % (tag, rc, " | ".join(lines) if lines else "(no findings)"))


def prereg_text(base, counter_sha, tail="", keys=None, round_line="Round: 42\n"):
    k = dict(keys) if keys else {
        "Base": base, "Counter": "census/c1.py sha256=%s" % counter_sha,
        "Population": "census/pop.tsv sha256=%s" % counter_sha,
        "Control": "census/control.txt", "Target": "items=2 corrected=2", "Kill": "any uncorrected",
    }
    body = "".join("%s: %s\n" % (a, b) for a, b in k.items())
    return "# prereg\n%s\n## C1 - claim 1\n%s%s" % (round_line, body, tail)


def sha_of(text):
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- probes
def p_M09():
    """M09: KEYLINE loses its trailing [ \\t]*$ -> a value with trailing spaces is no longer stripped."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M09", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    text = prereg_text(base + "   ", sha_of(counter))  # Base carries trailing spaces
    write(d, "prereg.txt", text)
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg")
    return d


def p_M13():
    """M13: ROUND loses its BOM tolerance -> a BOM-prefixed Round line is not found."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M13", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    text = prereg_text(base, sha_of(counter))
    write(d, "prereg.txt", "﻿" + text)
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg")
    return d


def p_M28_M29():
    """M28/M29: freeze_rev picks the newest instead of the oldest commit that adds the prereg."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M28", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    write(d, "prereg.txt", prereg_text(base, sha_of(counter)))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg-v1")
    os.remove(os.path.join(d, "prereg.txt"))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "drop-prereg")
    write(d, "prereg.txt", prereg_text(base, sha_of(counter)))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg-v2")
    return d


def p_M31():
    """M31: the missing-Round finding class becomes FIELD-EMPTY instead of FIELD-MISSING."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M31", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    write(d, "prereg.txt", prereg_text(base, sha_of(counter), round_line=""))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg")
    return d


def p_M40():
    """M40: dispatch_findings keeps the NEWEST adding commit instead of the oldest."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M40", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    write(d, "prereg.txt", prereg_text(base, sha_of(counter)))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg")
    write(d, ".ufo/waves/round-42/w1-spec.json", "{}\n")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "dispatch-before")
    os.remove(os.path.join(d, ".ufo/waves/round-42/w1-spec.json"))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "drop-dispatch")
    write(d, ".ufo/waves/round-42/w1-spec.json", "{}\n")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "dispatch-after")
    return d


def p_M43():
    """M43: the PATH_SHA fallback takes the whole value instead of its first whitespace token."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M43", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    keys = {"Base": base, "Counter": "census/c1.py extra", "Population": "census/pop.tsv sha256=%s" % sha_of(pop),
            "Control": "census/control.txt", "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg_text(base, sha_of(counter), keys=keys))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg")
    return d


def p_M59():
    """M59: a duplicated key is still evaluated (the docstring says it is not)."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M59", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    keys = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha_of(counter),
            "Population": "census/pop.tsv sha256=%s" % sha_of(pop), "Control": "census/control.txt",
            "Target": "", "Kill": "k"}
    write(d, "prereg.txt", prereg_text(base, sha_of(counter), keys=keys, tail="Target: x\n"))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg")
    return d


def p_M61_M62():
    """M61/M62: a plain '## ' heading no longer closes the claim block."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M61", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    body = "".join("%s: %s\n" % (a, b) for a, b in [
        ("Base", base), ("Counter", "census/c1.py sha256=%s" % sha_of(counter)),
        ("Population", "census/pop.tsv sha256=%s" % sha_of(pop)),
        ("Control", "census/control.txt"), ("Target", "items=2 corrected=2"), ("Kill", "any")])
    text = ("# prereg\nRound: 42\n\n## C1 - claim 1\n%s\n## Notes - not a claim\n"
            "Base: %s\nCounter: census/c1.py sha256=%s\n"
            % (body, base, sha_of(counter)))
    write(d, "prereg.txt", text)
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg")
    return d


def p_M22():
    """M22: the NUL guard in Repo.blob is gone -> a NUL in a path raises instead of returning None."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M22", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    keys = {"Base": base, "Counter": "census/c\x00.py sha256=%s" % sha_of(counter),
            "Population": "census/pop.tsv sha256=%s" % sha_of(pop), "Control": "census/control.txt",
            "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg_text(base, sha_of(counter), keys=keys))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg")
    return d


def p_M24():
    """M24: is_symlink no longer normalises the path."""
    counter = "# counter\n"
    pop = "id\tname\n1\talpha\n"
    d = build("M24", {"census/c1.py": counter, "census/pop.tsv": pop,
                      "census/control.txt": "EXIT=1\n"})
    base = git(d, "rev-parse", "HEAD")
    keys = {"Base": base, "Counter": "census/../census/c1.py sha256=%s" % sha_of(counter),
            "Population": "census/pop.tsv sha256=%s" % sha_of(pop), "Control": "census/control.txt",
            "Target": "t", "Kill": "k"}
    write(d, "prereg.txt", prereg_text(base, sha_of(counter), keys=keys))
    git(d, "add", "-A")
    git(d, "commit", "-qm", "prereg")
    return d


PROBES = {
    "M09": p_M09, "M13": p_M13, "M28": p_M28_M29, "M29": p_M28_M29, "M31": p_M31,
    "M40": p_M40, "M43": p_M43, "M59": p_M59, "M61": p_M61_M62, "M62": p_M61_M62,
    "M22": p_M22, "M24": p_M24,
}


def main():
    want = sys.argv[1:] or sorted(PROBES)
    for mid in want:
        fn = PROBES.get(mid)
        if not fn:
            print("%s: no probe" % mid)
            continue
        d = fn()
        print("=== %s  (repo %s)" % (mid, os.path.basename(d)))
        prc, pl = run(PRISTINE, d)
        show("pristine", prc, pl)
        mp = os.path.join(SEAT, "mutants", mid + ".py")
        mrc, ml = run(mp, d)
        show("mutant", mrc, ml)
        print("  DIFFER=%s" % (pl != ml or prc != mrc))


if __name__ == "__main__":
    main()
