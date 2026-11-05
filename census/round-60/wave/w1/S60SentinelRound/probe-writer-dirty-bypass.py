#!/usr/bin/env python3
"""probe-writer-dirty-bypass.py - can the C2 writer's clean-tree guard (behaviour 7) be defeated
without --allow-dirty?

The writer runs `git -C root status --porcelain` with an environment that scrubs only GIT_DIR and
GIT_WORK_TREE, so every other GIT_* variable and the repo's own config still steer that call.

  D1  GIT_CONFIG_COUNT/KEY/VALUE in the caller env: status.showUntrackedFiles=no hides an
      untracked file from --porcelain.
  D2  repo-local config `status.showUntrackedFiles=no`: same hiding with no environment at all
      (any actor who can write .git/config, e.g. a sibling seat, can set it).
  D3  GIT_INDEX_FILE=/dev/null: what does the guard see?
  D4  a lane-ignored path (this lane's .gitignore carries `.ufo/waves/` and
      `census/operator-sweep-*/`): porcelain never reports it, so a receipt can be written while
      the ignored tree is dirty.

Usage: probe-writer-dirty-bypass.py --work DIR --tool PATH
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _h  # noqa: E402


def run_writer(tool, root, rev, out, extra_env=None, extra=()):
    argv = [sys.executable, "-B", tool, "--root", root, "--rev", rev,
            "--instrument", "instrument.sh", "--out", out] + list(extra) + ["--", "/bin/echo", "ok"]
    return _h.run(argv, env=extra_env)


def fresh(tag, work, gitignore=None):
    repo = _h.make_repo(os.path.join(work, tag))
    _h.write(repo, "instrument.sh", "#!/bin/sh\necho i\n")
    if gitignore:
        _h.write(repo, ".gitignore", gitignore)
    _h.write(repo, "tracked.txt", "clean\n")
    rev = _h.commit(repo, "seed")
    return repo, rev


def main():
    work = _h.scratch_root(sys.argv)
    tool = os.path.abspath(_h.opt(sys.argv, "--tool"))
    p = _h.Probe("writer-dirty-bypass")
    if not (tool and os.path.isfile(tool)):
        p.check("D0 tool-present", False, "absent: %r" % tool)
        return p.finish()
    p.check("D0 tool-present", True, tool)

    # ---- D1: GIT_CONFIG_COUNT hides the untracked file from the guard ------------------------
    repo, rev = fresh("d1", work)
    _h.write(repo, "stray-untracked.txt", "dirty\n")
    out = os.path.join(work, "d1-out", "receipt.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rc, so, se = run_writer(tool, repo, rev, out)
    p.check("D1a control: dirty refused", rc == 2 and not os.path.exists(out),
            "rc=%d err=%r" % (rc, se.strip()[:100]))
    if os.path.exists(out):
        os.unlink(out)
    env = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "status.showUntrackedFiles",
           "GIT_CONFIG_VALUE_0": "no"}
    rc, so, se = run_writer(tool, repo, rev, out, env)
    p.check("D1b GIT_CONFIG_COUNT writes receipt on dirty tree",
            rc == 0 and os.path.exists(out),
            "rc=%d receipt=%s err=%r" % (rc, os.path.exists(out), se.strip()[:100]))
    if os.path.exists(out):
        body = open(out, encoding="utf-8").read()
        p.check("D1c receipt carries no dirtiness record", "dirty" not in body,
                "receipt lines: %r" % body.splitlines()[:4])

    # ---- D2: repo-local config does the same with no env -------------------------------------
    repo2, rev2 = fresh("d2", work)
    _h.write(repo2, "stray-untracked.txt", "dirty\n")
    _h.git(repo2, "config", "status.showUntrackedFiles", "no")
    out2 = os.path.join(work, "d2-out", "receipt.txt")
    os.makedirs(os.path.dirname(out2), exist_ok=True)
    rc, so, se = run_writer(tool, repo2, rev2, out2)
    p.check("D2 repo-local config writes receipt on dirty tree",
            rc == 0 and os.path.exists(out2),
            "rc=%d receipt=%s err=%r" % (rc, os.path.exists(out2), se.strip()[:100]))

    # ---- D3: GIT_INDEX_FILE ---------------------------------------------------------------
    repo3, rev3 = fresh("d3", work)
    _h.write(repo3, "stray-untracked.txt", "dirty\n")
    out3 = os.path.join(work, "d3-out", "receipt.txt")
    os.makedirs(os.path.dirname(out3), exist_ok=True)
    rc, so, se = run_writer(tool, repo3, rev3, out3, {"GIT_INDEX_FILE": os.devnull})
    p.check("D3 GIT_INDEX_FILE=/dev/null", rc != 0 or not os.path.exists(out3),
            "rc=%d receipt=%s err=%r" % (rc, os.path.exists(out3), se.strip()[:120]))

    # ---- D4: lane-ignored path ------------------------------------------------------------
    repo4, rev4 = fresh("d4", work, gitignore=".ufo/waves/\ncensus/operator-sweep-*/\n")
    _h.write(repo4, ".ufo/waves/round-60/w1/dirty.txt", "ignored dirt\n")
    _h.write(repo4, "census/operator-sweep-x/junk.txt", "ignored dirt\n")
    st = _h.out(_h.git(repo4, "status", "--porcelain"))
    out4 = os.path.join(work, "d4-out", "receipt.txt")
    os.makedirs(os.path.dirname(out4), exist_ok=True)
    rc, so, se = run_writer(tool, repo4, rev4, out4)
    p.check("D4 ignored dirt invisible to the guard",
            not st.strip() and rc == 0 and os.path.exists(out4),
            "porcelain=%r rc=%d receipt=%s" % (st, rc, os.path.exists(out4)))
    return p.finish()


if __name__ == "__main__":
    sys.exit(main())
