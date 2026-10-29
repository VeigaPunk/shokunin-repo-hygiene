#!/usr/bin/env python3
"""Byte-for-byte stdout+stderr+rc differential: pristine tool vs mutant, for the equivalence
survivors M21, M24, M30, M39 (tool behaviour) and the config check for M19.

Equivalent means: identical stdout, stderr and exit code on every input below.
Writes nothing into the lane; synthetic repos live under SEAT_SCRATCH.
"""
import hashlib
import os
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester01"
SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRISTINE = os.path.join(LANE, "tools/souji-freeze-check.py")
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": SCRATCH,
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
       "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid"}


def run(tool, root, prereg, rev):
    p = subprocess.run(["python3", "-B", tool, "--root", root, "--prereg", prereg, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                       env=dict(ENV, TMPDIR=SCRATCH))
    return p.returncode, p.stdout, p.stderr


def git(d, *a):
    return subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE, text=True,
                          check=True, env=ENV).stdout.strip()


def fresh(name):
    d = os.path.join(SCRATCH, "p5", name)
    subprocess.run(["rm", "-rf", d], check=True)
    os.makedirs(d)
    subprocess.run(["git", "-C", d, "init", "-q", "-b", "main", d], check=True, env=ENV)
    assert os.path.realpath(git(d, "rev-parse", "--show-toplevel")) == os.path.realpath(d)
    return d


def sha(b):
    return hashlib.sha256(b).hexdigest()


def repo(name, extra=None, dispatch_after=False, counter_path="census/c.py"):
    """Lane-shaped fixture: counter, population, control, then a freeze commit of prereg.txt."""
    d = fresh(name)
    os.makedirs(os.path.join(d, "census"))
    open(os.path.join(d, "census/c.py"), "wb").write(b"c\n")
    open(os.path.join(d, "census/p.tsv"), "wb").write(b"h\nr\n")
    open(os.path.join(d, "census/ctl.txt"), "wb").write(b"x\nEXIT=1\n")
    for rel, data in (extra or {}).items():
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        if isinstance(data, tuple):
            os.symlink(data[0], full)
        else:
            open(full, "wb").write(data)
    git(d, "add", "-A"); git(d, "commit", "-qm", "base")
    base = git(d, "rev-parse", "HEAD")
    text = ("# p\nRound: 42\n\n## C1 - c\nBase: %s\nCounter: %s sha256=%s\n"
            "Population: census/p.tsv sha256=%s\nControl: census/ctl.txt\nTarget: t\nKill: k\n"
            % (base, counter_path, sha(b"c\n"), sha(b"h\nr\n")))
    open(os.path.join(d, "prereg.txt"), "w").write(text)
    git(d, "add", "-A"); git(d, "commit", "-qm", "freeze")
    if dispatch_after:
        os.makedirs(os.path.join(d, ".ufo/waves/round-42"), exist_ok=True)
        open(os.path.join(d, ".ufo/waves/round-42/w1-spec.json"), "w").write("{}\n")
        git(d, "add", "-A"); git(d, "commit", "-qm", "dispatch")
    return d, git(d, "rev-parse", "HEAD")


def compare(mid, root, prereg, rev, tag):
    mt = os.path.join(SEAT, "mutants", mid + ".py")
    a = run(PRISTINE, root, prereg, rev)
    b = run(mt, root, prereg, rev)
    same = a == b
    last = (a[1].strip().splitlines() or ["(empty)"])[-1][:60]
    print("%s | %-30s | rc pristine=%d mutant=%d | identical=%s | %s" % (
        mid, tag, a[0], b[0], same, last))
    return same


def config_check():
    """M19: the mutant drops GIT_CONFIG_NOSYSTEM but keeps GIT_CONFIG_SYSTEM=/dev/null.
    Show that a real system config file is unread with the mutant's environment."""
    cfg = os.path.join(SCRATCH, "p5", "syscfg.ini")
    os.makedirs(os.path.dirname(cfg), exist_ok=True)
    open(cfg, "w").write("[user]\n\tname = SysCfgMarker\n")
    mutant_env = {"PATH": ENV["PATH"], "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    pristine_env = dict(mutant_env, GIT_CONFIG_NOSYSTEM="1")
    open_env = {"PATH": ENV["PATH"], "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": cfg}
    out = []
    for label, e in (("pristine env", pristine_env), ("mutant env", mutant_env), ("no guard (control)", open_env)):
        p = subprocess.run(["git", "config", "--get", "user.name"], stdout=subprocess.PIPE,
                           text=True, env=e, cwd=SCRATCH)
        out.append("%s -> user.name=%r" % (label, p.stdout.strip()))
    ok = out[0].endswith("''") and out[1].endswith("''") and "SysCfgMarker" in out[2]
    for line in out:
        print("M19 config " + line)
    print("M19 system config blocked by GIT_CONFIG_SYSTEM=/dev/null in both envs: %s" % ok)
    return ok


def main():
    lane_rev = git(LANE, "rev-parse", "HEAD")
    results = []
    for mid in ("M21", "M30", "M39"):
        for p in ("census/round-42/preregistration.txt", "census/round-41/preregistration.txt",
                  "census/round-40/preregistration.txt"):
            results.append(compare(mid, LANE, p, lane_rev, "lane tip " + p.split("/")[1]))
    d, rev = repo("plain")
    d2, rev2 = repo("dispatch", dispatch_after=True)
    d3, _ = repo("unres")
    for mid in ("M21", "M30", "M39"):
        results.append(compare(mid, d, "prereg.txt", rev, "synthetic clean"))
        results.append(compare(mid, d2, "prereg.txt", rev2, "synthetic dispatch-after"))
        results.append(compare(mid, d3, "prereg.txt", "1" * 40, "unresolved rev"))
    # M24: counter path with non-normalised spellings and a symlink at the normal spelling
    ds, rs = repo("symlink", extra={"census/link.py": ("c.py",)}, counter_path="census/link.py")
    dn, rn = repo("nonnorm", extra={"census/link.py": ("c.py",)}, counter_path="census/./link.py")
    dd, rd = repo("dbl", extra={"census/link.py": ("c.py",)}, counter_path="census//link.py")
    results.append(compare("M24", ds, "prereg.txt", rs, "symlink at normal path"))
    results.append(compare("M24", dn, "prereg.txt", rn, "counter path census/./link.py"))
    results.append(compare("M24", dd, "prereg.txt", rd, "counter path census//link.py"))
    results.append(config_check())
    print("ALL_IDENTICAL=%s checks=%d" % (all(results), len(results)))


if __name__ == "__main__":
    sys.exit(main())
