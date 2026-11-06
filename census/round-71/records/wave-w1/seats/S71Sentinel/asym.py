#!/usr/bin/env python3
"""Asymmetry tests: can `git status` apply a clean filter that the writer's check-attr cannot see?"""
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

def commit_tree_of(d, files):
    """Build an unreferenced commit whose tree holds exactly the given {path: bytes}."""
    lines = []
    for path, body in files.items():
        blob = g(d, "hash-object", "-w", "--stdin", inp=body).stdout.decode().strip()
        lines.append("100644 blob %s\t%s\n" % (blob, path))
    tree = g(d, "mktree", inp="".join(lines).encode()).stdout.decode().strip()
    return g(d, "commit-tree", "-m", "attrs", tree).stdout.decode().strip()

def checkattr(d):
    paths = g(d, "ls-files", "-z", ":(top)").stdout
    r = g(d, "check-attr", "--stdin", "-z", "filter", inp=paths)
    return r.returncode, r.stdout.replace(b"\0", b"|").decode("utf-8", "replace").strip()

def status(d):
    r = g(d, "-c", "status.showUntrackedFiles=all", "status", "--porcelain")
    return r.stdout.decode().replace("\n", " ").strip() or "(clean)"

def forged(d):
    open(os.path.join(d, "tools", "counter.py"), "wb").write(b"counter v2\n")

print("R4: HEAD commits .gitattributes filter=t; attr.tree points at a tree WITHOUT the attribute")
d = mk("r4")
g(d, "config", "filter.t.clean", "sed s/v2/v1/")
open(os.path.join(d, ".gitattributes"), "w").write("tools/counter.py filter=t\n")
g(d, "add", ".gitattributes"); g(d, "commit", "-qm", "attrs")
bare = commit_tree_of(d, {"tools/counter.py": b"counter v1\n"})
g(d, "config", "attr.tree", bare)
forged(d)
print("  checkattr:", checkattr(d))
print("  status   :", status(d))
print("  attr.tree:", g(d, "config", "--get", "attr.tree").stdout.decode().strip()[:12])

print("R4b: same but attr.tree = HEAD~1 (pre-attribute commit)")
d = mk("r4b")
g(d, "config", "filter.t.clean", "sed s/v2/v1/")
old = g(d, "rev-parse", "HEAD").stdout.decode().strip()
open(os.path.join(d, ".gitattributes"), "w").write("tools/counter.py filter=t\n")
g(d, "add", ".gitattributes"); g(d, "commit", "-qm", "attrs")
g(d, "config", "attr.tree", old)
forged(d)
print("  checkattr:", checkattr(d))
print("  status   :", status(d))

print("R4c: control - same repo, attr.tree unset")
g(d, "config", "--unset", "attr.tree")
print("  checkattr:", checkattr(d))
print("  status   :", status(d))
