#!/usr/bin/env python3
"""R41w2critic05 probes: root-repository variants (.git dir vs .git FILE) and TOTAL orders,
run against pinned (lane tip) and base (7eebc18) tools. Scratch only."""
import os
import subprocess
import sys
import tempfile

PINNED = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py"
BASE = "/fast/scratch/hyaku/souji-r41/R41w2critic05/base-tool.py"
WORK = sys.argv[1]
ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
    "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid",
}


def sh(*cmd):
    return subprocess.run(list(cmd), env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=False)


def repo(path):
    os.makedirs(path)
    sh("git", "init", "-q", "-b", "main", path)
    with open(os.path.join(path, "f"), "w") as h:
        h.write("x\n")
    sh("git", "-C", path, "add", "f")
    sh("git", "-C", path, "commit", "-qm", "b")


def run(tool, root, record_body, extra=()):
    rec = os.path.join(WORK, "rec-%d.tsv" % abs(hash((tool, root, record_body, tuple(extra)))))
    with open(rec, "w") as h:
        h.write(record_body)
    p = subprocess.run(["python3", "-B", tool, "--root", root, "--record", rec, "--timeout", "30", *extra],
                       env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    os.unlink(rec)
    return p.returncode, (p.stdout + p.stderr).replace(WORK, "$W")


def show(label, root, body, extra=()):
    for name, tool in (("pinned", PINNED), ("base", BASE)):
        rc, out = run(tool, root, body, extra)
        print("%-34s %-6s rc=%d %s" % (label, name, rc, out.strip().replace("\n", " | ")))
    print()


# --- root variant A: root is a real repo dir (.git DIR), holds alpha
rootdir = os.path.join(WORK, "rootrepo")
repo(rootdir)
repo(os.path.join(rootdir, "alpha"))
show("A .git-dir root, unnamed", rootdir, "REPO\talpha\tregs=1\tprunable=0\n")
show("A .git-dir root, named", rootdir, "REPO\trootrepo\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n", ("--skip-unrecorded",))

# --- root variant B: root has a .git FILE whose gitdir lies INSIDE root (linked-worktree style)
fileroot = os.path.join(WORK, "fileroot")
os.makedirs(fileroot)
gitdir = os.path.join(fileroot, ".gitstore")
os.makedirs(gitdir)
sh("git", "init", "-q", "--bare", gitdir)
with open(os.path.join(fileroot, ".git"), "w") as h:
    h.write("gitdir: %s\n" % gitdir)
repo(os.path.join(fileroot, "alpha"))
show("B .git-file root, unnamed", fileroot, "REPO\talpha\tregs=1\tprunable=0\n")
show("B .git-file root, unnamed+skip", fileroot, "REPO\talpha\tregs=1\tprunable=0\n", ("--skip-unrecorded",))
show("B .git-file root, named", fileroot, "REPO\tfileroot\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n", ("--skip-unrecorded",))

# --- root variant C: root .git FILE, but bare-ish gitdir outside root (containment)
outside = os.path.join(WORK, "outside-gitdir.git")
sh("git", "init", "-q", "--bare", outside)
croot = os.path.join(WORK, "crootfile")
os.makedirs(croot)
with open(os.path.join(croot, ".git"), "w") as h:
    h.write("gitdir: %s\n" % outside)
repo(os.path.join(croot, "alpha"))
show("C .git-file->outside, named", croot, "REPO\tcrootfile\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n", ("--skip-unrecorded",))
show("C .git-file->outside, unnamed", croot, "REPO\talpha\tregs=1\tprunable=0\n")

# --- child repo that is a .git FILE (control: discovery & repo_path accept it)
ctl = os.path.join(WORK, "ctlroot")
os.makedirs(ctl)
repo(os.path.join(ctl, "alpha"))
cg = os.path.join(ctl, "alpha", ".git")
show("D child-file-control, unnamed", ctl, "REPO\talpha\tregs=1\tprunable=0\n")
