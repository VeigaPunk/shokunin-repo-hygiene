#!/usr/bin/env python3
"""Which attribute sources does `git check-attr` see, and does `git status` apply the clean filter?"""
import os, subprocess, sys, tempfile

S = "/fast/scratch/hyaku/souji-r71/S71Sentinel"
GENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
GENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_DATE="2026-11-06T12:00:00Z", GIT_COMMITTER_DATE="2026-11-06T12:00:00Z",
            GIT_OPTIONAL_LOCKS="0")

def g(d, *a, inp=None):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, input=inp, env=GENV)

def mk(name):
    d = tempfile.mkdtemp(prefix=name + ".", dir=S)
    assert d and os.path.isdir(d), d
    g(d, "init", "-q")
    top = g(d, "rev-parse", "--show-toplevel").stdout.decode().strip()
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    g(d, "config", "user.name", "probe"); g(d, "config", "user.email", "probe@invalid")
    os.makedirs(os.path.join(d, "tools"), exist_ok=True)
    open(os.path.join(d, "tools", "counter.py"), "wb").write(b"counter v1\n")
    open(os.path.join(d, "tools", "instr.sh"), "wb").write(b"#!/bin/sh\necho ok\n")
    os.chmod(os.path.join(d, "tools", "instr.sh"), 0o755)
    g(d, "add", "-A"); g(d, "commit", "-qm", "seed")
    return d

def attrtree(d, body):
    blob = g(d, "hash-object", "-w", "--stdin", inp=body.encode()).stdout.decode().strip()
    tree = g(d, "mktree", inp=("100644 blob %s\t.gitattributes\n" % blob).encode()).stdout.decode().strip()
    c = g(d, "commit-tree", "-m", "attrs", tree).stdout.decode().strip()
    assert len(c) == 40, (tree, c)
    return c

def checkattr(d):
    paths = g(d, "ls-files", "-z", ":(top)").stdout
    r = g(d, "check-attr", "--stdin", "-z", "filter", inp=paths)
    return r.returncode, r.stdout.replace(b"\0", b"|").decode("utf-8", "replace").strip(), r.stderr.decode().strip()[:120]

def status(d):
    r = g(d, "-c", "status.showUntrackedFiles=all", "status", "--porcelain")
    return r.stdout.decode().replace("\n", " ").strip() or "(clean)"

def forged(d):
    open(os.path.join(d, "tools", "counter.py"), "wb").write(b"counter v2\n")

def route(label, setup):
    d = mk(label)
    setup(d)
    forged(d)
    ca = checkattr(d)
    print(f"{label:22s} checkattr rc={ca[0]} out={ca[1][:90]!r}")
    print(f"{'':22s} status={status(d)!r}")
    return d

# R1: attr.tree -> non-HEAD commit with the filter attribute
def r1(d):
    g(d, "config", "filter.t.clean", "sed s/v2/v1/")
    c = attrtree(d, "tools/counter.py filter=t\n")
    g(d, "config", "attr.tree", c)
route("R1 attr.tree", r1)

# R2: repository-local core.attributesFile
def r2(d):
    g(d, "config", "filter.t.clean", "sed s/v2/v1/")
    p = os.path.join(S, "r2-attrs-" + os.path.basename(d))
    open(p, "w").write("tools/counter.py filter=t\n")
    g(d, "config", "core.attributesFile", p)
route("R2 core.attributesFile", r2)

# R3: info/attributes control (known-covered source)
def r3(d):
    g(d, "config", "filter.t.clean", "sed s/v2/v1/")
    os.makedirs(os.path.join(d, ".git", "info"), exist_ok=True)
    open(os.path.join(d, ".git", "info", "attributes"), "w").write("tools/counter.py filter=t\n")
route("R3 info/attributes", r3)
