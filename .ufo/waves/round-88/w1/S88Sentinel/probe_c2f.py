#!/usr/bin/env python3
"""S88Sentinel probes, part 6: the parent's verdict dispatch reads the WHOLE child stdout, so a line the WRITER
prints can select the branch the parent takes.

Modes (the delegated read FAILS in every mode: the writer's git() returns rc=1, so the bootstrap's honest verdict
is FLAGFAIL, never CLEAN):
  honest        the writer prints nothing.
  clean_after   the writer prints "CLEAN" (an ordinary buffered print): the parent's `out` now starts with CLEAN
                and the parent accepts a clean verdict although the delegated read failed.
  noise_after   the writer prints "diagnostic": no branch matches; the tool falls into the no-verdict branch.
  writer_after  the writer prints "WRITER <its own digest>": the parent's swap check compares the forged line
                against the header, then the remaining stdout starts with the real WRITER line and no branch matches.
  forged_clean  the writer prints "WRITER <its own digest>" and then "CLEAN": the forged WRITER line matches the
                header, the real WRITER line is left in `out`, and out still starts with CLEAN.

Reported: the tool's exit code, the number of K4 MISMATCH rows, and the detail.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOL = os.path.join(LANE, "tools/souji-record-agreement.py")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "s88 sentinel", "GIT_AUTHOR_EMAIL": "s88@s88.invalid",
            "GIT_COMMITTER_NAME": "s88 sentinel", "GIT_COMMITTER_EMAIL": "s88@s88.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})

STUB = r'''
import hashlib
import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    return P(1, b"", b"fatal: cannot read index\n")


def _truth_refusal(root):
    m = os.environ.get("R88_MODE", "honest")
    if m in ("clean_after", "forged_clean"):
        print("CLEAN")
    elif m == "noise_after":
        print("diagnostic")
    elif m in ("writer_after", "forged_clean"):
        d = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
        print("WRITER " + d)
    return ""


def _flag_refusal(*args):
    return None
'''


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}")
    return p.stdout.decode().strip()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make_kit(root, toolpath):
    tools = os.path.join(root, "tools")
    os.makedirs(tools)
    copy = os.path.join(tools, "souji-record-agreement.py")
    shutil.copyfile(toolpath, copy)
    with open(os.path.join(tools, "souji-receipt-write.py"), "w", encoding="utf-8") as f:
        f.write(STUB)
    repo = os.path.join(root, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q")
    top = git(repo, "rev-parse", "--show-toplevel")
    if os.path.realpath(top) != os.path.realpath(repo):
        raise RuntimeError("fixture toplevel mismatch")
    with open(os.path.join(repo, "a.txt"), "w", encoding="utf-8") as f:
        f.write("seed\n")
    git(repo, "add", "--", "a.txt")
    git(repo, "commit", "-q", "--no-verify", "-m", "r88 fixture seed")
    return copy, repo, git(repo, "rev-parse", "HEAD")


MODES = ("honest", "clean_after", "noise_after", "writer_after", "forged_clean")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--tool", default=TOOL)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("S88-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"S88-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    toolpath = os.path.abspath(ns.tool)
    print(f"# tool sha256={sha(toolpath)}")
    for mode in MODES:
        kit = make_kit(os.path.join(work, "kit-" + mode), toolpath)
        toolcopy, repo, rev = kit
        env = dict(ENV)
        env["R88_MODE"] = mode
        p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        out = p.stdout.decode("utf-8", "backslashreplace")
        rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
        print(f"--- MODE {mode} tool_rc={p.returncode} k4_rows={len(rows)}")
        for line in rows:
            cells = line.split("\t")
            print(f"    cells={len(cells)} detail={(cells[4] if len(cells) > 4 else '<none>')[:220]!r}")
        if not rows:
            print("    NO K4 ROW -> the parent accepted the tree as verified")
        print(f"    tool_stdout_head={out.split(chr(10))[:3]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
