#!/usr/bin/env python3
"""probe-fixture-gitenv.py - the C2 fixture (r60-receipt-write.py) inherits its caller environment
on every `git` call. Two consequences probed here, both against throwaway repos under --work:

  V1  the fixture's own "toplevel guard" is defeated by GIT_DIR+GIT_WORK_TREE, so its `add -A`
      and `commit` land in a caller-named repository (a lane-shaped repo, a sibling repo, ...).
  V2  GIT_CONFIG_COUNT/KEY/VALUE injected into the environment is honoured by those same calls,
      so `core.hooksPath` runs an attacker-named hook during the fixture's commit.

The victim repo here is a decoy under --work; no real lane repo is named by this probe.
Usage: probe-fixture-gitenv.py --work DIR [--fixture PATH]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _h  # noqa: E402

FIXTURE_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                               "S60ExecRecorderFix", "r60-receipt-write.py")


def main():
    work = _h.scratch_root(sys.argv)
    fixture = os.path.abspath(_h.opt(sys.argv, "--fixture", FIXTURE_DEFAULT))
    p = _h.Probe("fixture-gitenv")
    if not os.path.isfile(fixture):
        p.check("V0 fixture-present", False, "absent: %s" % fixture)
        return p.finish()
    p.check("V0 fixture-present", True, fixture)

    # ---- V1: GIT_DIR + GIT_WORK_TREE defeats the toplevel guard ------------------------------
    victim = _h.make_repo(os.path.join(work, "v1-victim"))
    _h.write(victim, "tracked.txt", "victim\n")
    v0 = _h.commit(victim, "victim-base")

    # Reproduce exactly what the fixture does in build_case(), under the hostile environment.
    case_repo = os.path.join(work, "v1-case", "repo")
    os.makedirs(case_repo, exist_ok=True)
    env = {"GIT_DIR": os.path.join(victim, ".git"), "GIT_WORK_TREE": case_repo}

    rc, so, se = _h.run(["git", "init", "-q", "-b", "main", case_repo], env=env)
    p.check("V1a init-under-GIT_DIR rc", rc == 0, "rc=%d %s" % (rc, (se or so).strip()[:120]))
    p.check("V1a case .git created", os.path.isdir(os.path.join(case_repo, ".git")),
            "case/.git exists=%s" % os.path.isdir(os.path.join(case_repo, ".git")))

    rc, top, se = _h.run(["git", "-C", case_repo, "rev-parse", "--show-toplevel"], env=env)
    guard_passes = os.path.realpath(top.strip()) == os.path.realpath(case_repo)
    p.check("V1b toplevel guard passes", guard_passes,
            "guard would see %r for case repo %r" % (top.strip(), case_repo))

    _h.write(case_repo, "payload.txt", "payload\n")
    rc_add, _, se = _h.run(["git", "-C", case_repo, "add", "-A"], env=env)
    rc_com, _, se = _h.run(["git", "-C", case_repo, "commit", "-q", "-m", "fixture-commit"], env=env)
    v1 = _h.out(_h.git(victim, "rev-parse", "HEAD"))
    subject = _h.out(_h.git(victim, "log", "--format=%s", "-1"))
    p.check("V1c fixture commit lands in victim", v1 != v0 and subject == "fixture-commit",
            "victim %s -> %s subject=%r add_rc=%d commit_rc=%d"
            % (v0[:12], v1[:12], subject, rc_add, rc_com))
    staged = _h.out(_h.git(victim, "status", "--porcelain")).replace("\n", " ")
    p.check("V1d victim index mutated", bool(staged.strip()), "victim status: %r" % staged[:120])

    # ---- V2: GIT_CONFIG_COUNT injects core.hooksPath into the fixture's commit --------------
    hooks = os.path.join(work, "v2-hooks")
    os.makedirs(hooks, exist_ok=True)
    marker = os.path.join(work, "v2-hook-ran.marker")
    hook = os.path.join(hooks, "pre-commit")
    with open(hook, "w") as fh:
        fh.write("#!/bin/sh\n: > %r\n" % marker)
    os.chmod(hook, 0o755)
    repo2 = _h.make_repo(os.path.join(work, "v2-repo"))
    _h.write(repo2, "a.txt", "a\n")
    env2 = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": hooks}
    _h.run(["git", "-C", repo2, "add", "-A"], env=env2)
    rc, _, se = _h.run(["git", "-C", repo2, "commit", "-q", "-m", "with-hook"], env=env2)
    ran = os.path.exists(marker)
    p.check("V2 injected hooksPath executed", ran,
            "commit rc=%d marker=%s (env GIT_CONFIG_COUNT=1 core.hooksPath=%s)" % (rc, ran, hooks))
    if ran:
        os.unlink(marker)
    return p.finish()


if __name__ == "__main__":
    sys.exit(main())
