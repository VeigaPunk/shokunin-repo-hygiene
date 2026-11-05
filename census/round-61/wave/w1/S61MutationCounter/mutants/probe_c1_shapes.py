#!/usr/bin/env python3
"""Supplementary C1 shape probe (S61MutationCounter): builds throwaway fixture repos per shape and
runs each tool with `--substance`. Shapes are NOT part of the frozen 11-row matrix; they only test
whether a surviving mutant is distinguishable at all.

usage: probe_c1_shapes.py WORK TOOL [TOOL...]
prints: SHAPE <name> <tool-basename> rc=<n> findings=<sorted classes or ->
"""
import hashlib
import os
import shutil
import subprocess
import sys

SHA_C = hashlib.sha256(b"c\n").hexdigest()
SHA_P = hashlib.sha256(b"h\nr\n").hexdigest()
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": "/nonexistent", "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@invalid",
       "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@invalid"}


TS = [1767225600]


def git(d, *a):
    env = dict(ENV)
    if a and a[0] == "commit":
        # deterministic, strictly increasing commit dates so `git log` order is reproducible
        TS[0] += 60
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = "@%d +0000" % TS[0]
    r = subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if r.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(a), r.stderr.decode()))
    return r.stdout.decode().strip()


def write(d, p, data):
    fp = os.path.join(d, p)
    os.makedirs(os.path.dirname(fp) or d, exist_ok=True)
    with open(fp, "wb") as f:
        f.write(data)


def receipt(base):
    return ("instrument=c.py\ninstrument_sha256=%s\nrev=%s\ncommand=python3 -B c.py\nEXIT=1\n"
            % (SHA_C, base)).encode()


def prereg(base):
    return ("Round: 1\n## C1\nBase: %s\nCounter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\n"
            "Control: ctl.txt\nTarget: t\nKill: k\n" % (base, SHA_C, SHA_P)).encode()


def seed(d):
    git(d, "init", "-q")
    assert git(d, "rev-parse", "--show-toplevel") == d or os.path.realpath(git(d, "rev-parse", "--show-toplevel")) == os.path.realpath(d)
    write(d, "c.py", b"c\n")
    write(d, "p.tsv", b"h\nr\n")
    write(d, "a", b"a\n")
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "base")
    return git(d, "rev-parse", "HEAD")


def shape_readd_at_freeze(d):
    """Receipt added at an ancestor A, removed, re-added in the freeze commit F. Oldest add = A."""
    base = seed(d)
    write(d, "ctl.txt", receipt(base))
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "A add ctl")
    git(d, "rm", "-q", "ctl.txt"); git(d, "commit", "-q", "-m", "R remove ctl")
    write(d, "ctl.txt", receipt(base)); write(d, "pre.txt", prereg(base))
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "F freeze + re-add ctl")
    return git(d, "rev-parse", "HEAD")


def shape_renamed_in(d):
    """Honest: receipt born as old.txt at A, git-mv'd to ctl.txt at R (ancestor), freeze F later."""
    base = seed(d)
    write(d, "old.txt", receipt(base))
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "A add old.txt")
    git(d, "mv", "old.txt", "ctl.txt"); git(d, "commit", "-q", "-m", "R rename to ctl")
    write(d, "pre.txt", prereg(base))
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "F freeze")
    return git(d, "rev-parse", "HEAD")


def shape_merge_side_branch(d):
    """Honest: ctl.txt added on side branch S (ancestor of F via merge M); freeze F after M."""
    base = seed(d)
    git(d, "checkout", "-q", "-b", "side")
    write(d, "ctl.txt", receipt(base))
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "S add ctl")
    git(d, "checkout", "-q", "-")
    git(d, "merge", "-q", "--no-edit", "side")
    write(d, "pre.txt", prereg(base))
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "F freeze")
    return git(d, "rev-parse", "HEAD")


def shape_merge_pruned_add(d):
    """Add on side branch b (oldest, ancestor of F); merge X resolves ctl absent, so X is TREESAME to
    its first parent and default log simplification prunes b. F re-adds ctl as the newest add."""
    base = seed(d)
    git(d, "checkout", "-q", "-b", "side")
    write(d, "ctl.txt", receipt(base))
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "b1 add ctl")
    git(d, "checkout", "-q", "-")
    write(d, "a", b"a2\n")
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "a1")
    git(d, "merge", "-q", "--no-ff", "--no-commit", "side")
    git(d, "rm", "-q", "--cached", "ctl.txt"); os.remove(os.path.join(d, "ctl.txt"))
    git(d, "commit", "-q", "-m", "X merge drops ctl")
    write(d, "ctl.txt", receipt(base)); write(d, "pre.txt", prereg(base))
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "F freeze + re-add ctl")
    return git(d, "rev-parse", "HEAD")


SHAPES = [("readd-at-freeze", shape_readd_at_freeze), ("renamed-in", shape_renamed_in),
          ("merge-side-branch", shape_merge_side_branch), ("merge-pruned-add", shape_merge_pruned_add)]


def main(argv):
    work = os.path.abspath(argv[0])
    tools = [os.path.abspath(t) for t in argv[1:]]
    for name, fn in SHAPES:
        for tool in tools:
            d = os.path.join(work, "%s-%s" % (name, os.path.basename(tool)))
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            freeze = fn(d)
            # honest checker invocation: the prereg path, freeze as the --rev
            r = subprocess.run([sys.executable, "-B", tool, "--root", d, "--prereg", "pre.txt",
                                "--rev", freeze, "--substance"], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=ENV)
            finds = sorted(l.split(" ", 3)[2] + ":" + l.split(" ", 3)[3].split(" ")[0]
                           for l in r.stdout.decode().splitlines() if l.startswith("FINDING "))
            print("SHAPE %s %s rc=%d findings=%s" % (name, os.path.basename(tool), r.returncode,
                                                  ",".join(finds) or "-"))
            if r.returncode not in (0, 1):
                print("  stderr:", r.stderr.decode().strip())


if __name__ == "__main__":
    main(sys.argv[1:])
