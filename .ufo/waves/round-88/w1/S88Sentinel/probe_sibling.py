#!/usr/bin/env python3
"""S88Sentinel probe: the SIBLING branches of the K4 detail (no-verdict, status-failed) still embed raw stderr in
the record cell, so a TAB in the delegated stderr splits the MISMATCH row and a raw control byte reaches stdout.

The r88 repair changed the FLAGFAIL branch only; the prereg's stated limits say so explicitly ("_stderr_tail's use
in the other branches (status-failed, no-verdict) is unchanged"). This probe measures the sibling branches so the
carry item is sized, not asserted.

Modes:
  noverdict_tab   the delegated writer raises a non-SystemExit exception whose message carries a TAB and a SOH:
                   the bootstrap's traceback reaches the parent's stderr, and the no-verdict branch renders it
                   through _stderr_tail (raw, unescaped).
  status_failed   the delegated writer's git() is never reached; instead the tool's OWN `git status` fails. This is
                   hard to force from a stub, so it is measured by inspection and reported as such.

Reported: the number of tab-separated cells in the MISMATCH row (the record shape is key<TAB>record<TAB>class<TAB>detail
= 4 cells + a trailing newline; a TAB inside the detail makes it 5+), and any raw control byte in stdout.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOLS = {"r88": os.path.join(LANE, "tools/souji-record-agreement.py"),
         "r87": os.path.join(LANE, "census/round-88/controls/c2-before-tool.py")}
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "s88 sentinel", "GIT_AUTHOR_EMAIL": "s88@s88.invalid",
            "GIT_COMMITTER_NAME": "s88 sentinel", "GIT_COMMITTER_EMAIL": "s88@s88.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})

STUB = '''import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    return P(1, b"", b"fatal: cannot read index\\n")


def _truth_refusal(root):
    if os.environ.get("R88_MODE") == "noverdict_tab":
        raise ValueError("boom\\twith\\x01tab")
    return ""


def _flag_refusal(*args):
    return None
'''


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode()[:200])
    return p.stdout.decode().strip()


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
    git(repo, "commit", "-q", "--no-verify", "-m", "s88 fixture seed")
    return copy, repo, git(repo, "rev-parse", "HEAD")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("S88-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"S88-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    for label, toolpath in TOOLS.items():
        print(f"===== TOOL {label} sha256={hashlib.sha256(open(toolpath, 'rb').read()).hexdigest()}")
        kit = make_kit(os.path.join(work, f"kit-{label}"), toolpath)
        toolcopy, repo, rev = kit
        env = dict(ENV)
        env["R88_MODE"] = "noverdict_tab"
        p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        raw = p.stdout
        out = raw.decode("utf-8", "backslashreplace")
        rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
        for line in rows:
            cells = line.split("\t")
            print(f"  MODE noverdict_tab: k4rows={len(rows)} tab_cells_in_row={len(cells)}")
            print(f"      detail={(cells[4] if len(cells) > 4 else '<none>')!r}")
        for name, ch in (("SOH", b"\x01"), ("NEL", b"\x85"), ("U2028", b"\xe2\x80\xa8")):
            n = raw.count(ch)
            if n:
                print(f"      RAW {name} bytes in the tool's stdout: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
