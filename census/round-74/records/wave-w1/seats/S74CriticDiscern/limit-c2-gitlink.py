#!/usr/bin/env python3
"""S74CriticDiscern — empirical test of the r74 C2 named limit: "the gitlink skip still follows lstat
(S73MutCounter F4, a missing gitlink path reads `missing`)".

Builds a fixture repo whose HEAD tree carries a gitlink entry (mode 160000) for `sub` with no worktree
path, then calls the r74 counter's own tree_divergence(repo, "HEAD") twice: (1) gitlink path absent,
(2) gitlink path present as a directory. Expect (1) [('sub','missing')] — the skip does NOT suppress a
missing gitlink — and (2) no ('sub', ...) record.
"""
import importlib.util
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-74/c1-counter.py")
SCRATCH = "/fast/scratch/hyaku/souji-r74/S74CriticDiscern"
IDENT = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@invalid",
         "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@invalid"}


def git(repo, *args):
    assert os.path.isabs(repo) and repo
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          env={**os.environ, **IDENT}, timeout=120)


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    d = subprocess.run(["mktemp", "-d", "-p", SCRATCH, "fx.XXXXXX"], capture_output=True, check=True)
    d = d.stdout.decode().strip()
    assert d and os.path.isdir(d), d
    try:
        assert git(d, "init", "-q").returncode == 0
        top = git(d, "rev-parse", "--show-toplevel").stdout.decode().strip()
        assert os.path.realpath(top) == os.path.realpath(d), (top, d)
        with open(os.path.join(d, "a.txt"), "wb") as f:
            f.write(b"alpha\n")
        assert git(d, "add", "--", "a.txt").returncode == 0
        assert git(d, "commit", "-q", "-m", "seed").returncode == 0
        head = git(d, "rev-parse", "HEAD").stdout.decode().strip()
        assert len(head) == 40
        assert git(d, "update-index", "--add", "--cacheinfo", f"160000,{head},sub").returncode == 0
        assert git(d, "commit", "-q", "-m", "gitlink").returncode == 0
        ls = git(d, "ls-tree", "-r", "HEAD").stdout.decode()
        print("HEAD tree:", ls.replace("\n", " | ").strip())
        spec = importlib.util.spec_from_file_location("c1counter", COUNTER)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assert os.path.realpath(git(d, "rev-parse", "--show-toplevel").stdout.decode().strip()) == os.path.realpath(d)
        before = m.tree_divergence(d, "HEAD")
        print("gitlink path absent  ->", before)
        os.makedirs(os.path.join(d, "sub"), exist_ok=True)
        after = m.tree_divergence(d, "HEAD")
        print("gitlink path present ->", after)
        print("limit TRUE" if before == [("sub", "missing")] and not any(p == "sub" for p, _ in after)
              else "limit FALSE")
        return 0
    finally:
        assert d.startswith(SCRATCH + "/")
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
