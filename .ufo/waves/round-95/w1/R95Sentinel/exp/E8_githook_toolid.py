#!/usr/bin/env python3
"""E8: does the sitecustomize reach a Python git hook / helper, and can it steal a monitoring tool id?

Part 1 (git hook): a scratch git repo whose pre-commit hook is a Python script that reports whether the r95
sitecustomize was loaded.  The hook inherits the environment (including PYTHONPATH) from the git process, so a
git hook run under the hook-enabled environment loads the sentinel.  The lane's own harness sets
core.hooksPath=/dev/null for git calls, so the lane has no live hooks; this shows the MECHANISM.

Part 2 (tool id): a .pth file that takes sys.monitoring tool ids 3 and 4 BEFORE sitecustomize runs (site.py
imports .pth files first, then sitecustomize), so the sentinel's `for _souji_id in range(3, 6)` loop falls
through to id 5 -- sys.monitoring.OPTIMIZER_ID, an id reserved for the interpreter's optimizer.
"""
import os
import subprocess
import sys
import textwrap

SCRATCH = "/fast/scratch/hyaku/souji-r95/R95Sentinel"
HOOK_DIR = os.path.join(SCRATCH, "hook")


def part1_git_hook():
    repo = os.path.join(SCRATCH, "e8-repo")
    subprocess.run(["rm", "-rf", repo])
    os.makedirs(repo)
    subprocess.run(["git", "-C", repo, "init", "-q"], check=True)
    top = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE,
                         check=True).stdout.decode().strip()
    assert os.path.realpath(top) == os.path.realpath(repo), f"git toplevel {top} != {repo}"
    hook = os.path.join(repo, ".git", "hooks", "pre-commit")
    with open(hook, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent("""\
            #!/usr/bin/env python3
            import os, sys
            print("HOOK os._exit is", getattr(os._exit, "__name__", os._exit))
            print("HOOK excepthook is", getattr(sys.excepthook, "__name__", sys.excepthook))
            from sys import monitoring as m
            print("HOOK tool3 owner:", m.get_tool(3))
            """))
    os.chmod(hook, 0o755)
    with open(os.path.join(repo, "a.txt"), "w", encoding="utf-8") as f:
        f.write("x\n")
    env = dict(os.environ)
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t.invalid"})
    for label, extra in (("plain", {}), ("hooked", {"PYTHONPATH": HOOK_DIR})):
        e = dict(env)
        e.update(extra)
        p = subprocess.run(["git", "-C", repo, "commit", "-q", "-m", "t"], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, env=e, timeout=60)
        print(f"[git-hook {label:6}] rc={p.returncode} out={p.stdout.decode(errors='replace').strip()[:300]!r}")


def part2_tool_id():
    pth_dir = os.path.join(SCRATCH, "e8-pth")
    subprocess.run(["rm", "-rf", pth_dir])
    os.makedirs(pth_dir)
    with open(os.path.join(pth_dir, "zzz_take_ids.pth"), "w", encoding="utf-8") as f:
        f.write("import sys; sys.monitoring.use_tool_id(3, 'other-tool'); sys.monitoring.use_tool_id(4, 'other-tool')\n")
    child = os.path.join(SCRATCH, "e8-pth", "child.py")
    with open(child, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent("""\
            import sys
            from sys import monitoring as m
            print("tool 3:", m.get_tool(3), "| 4:", m.get_tool(4), "| 5:", m.get_tool(5))
            print("OPTIMIZER_ID:", m.OPTIMIZER_ID, "COVERAGE_ID:", m.COVERAGE_ID)
            """))
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = pth_dir + os.pathsep + HOOK_DIR
    for label, env in (("plain", base), ("hooked", hooked)):
        p = subprocess.run([sys.executable, "-B", child], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                           timeout=30)
        print(f"[tool-id {label:6}] rc={p.returncode} out={p.stdout.decode().strip()!r} "
              f"err={p.stderr.decode().strip()[:200]!r}")


if __name__ == "__main__":
    part1_git_hook()
    part2_tool_id()
