#!/usr/bin/env python3
"""S88Sentinel C2 probes, part 3: injectivity of the detail, memory cost of a large payload, and the r87 control.

Modes:
  collide_invalid   the delegated stderr is the single byte 0xFF.
  collide_literal   the delegated stderr is the four literal characters  \\xff.
  collide_tab       the delegated stderr carries a TAB (record shape).
  nel               the delegated stderr carries a raw NEL byte (0x85).
  big10m            the delegated stderr is 10 MB of 'A' (memory cost of the base64 frame).
  big10m_ctrl       the delegated stderr is 10 MB of 0x01 (escape expansion cost).

Runs each mode against BOTH the r88 tool (tools/souji-record-agreement.py) and the r87 control
(census/round-88/controls/c2-before-tool.py) so the delta is measured, not asserted.
"""
import argparse
import hashlib
import os
import resource
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

STUB = r'''
import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    m = os.environ.get("R88_MODE", "flagfail")
    if m == "collide_invalid":
        return P(1, b"", b"\xff")
    if m == "collide_literal":
        return P(1, b"", b"\\xff")
    if m == "collide_tab":
        return P(1, b"", b"a\tb")
    if m == "nel":
        return P(1, b"", b"a\x85b")
    if m == "big10m":
        return P(1, b"", b"A" * 10_000_000)
    if m == "big10m_ctrl":
        return P(1, b"", b"\x01" * 10_000_000)
    return P(1, b"", b"fatal: cannot read index\n")


def _truth_refusal(root):
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
    git(repo, "commit", "-q", "--no-verify", "-m", "s88 fixture seed")
    return copy, repo, git(repo, "rev-parse", "HEAD")


MODES = ("collide_invalid", "collide_literal", "collide_tab", "nel", "big10m", "big10m_ctrl")


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
        print(f"===== TOOL {label} sha256={sha(toolpath)}")
        for mode in MODES:
            kit = make_kit(os.path.join(work, f"kit-{label}-{mode}"), toolpath)
            toolcopy, repo, rev = kit
            env = dict(ENV)
            env["R88_MODE"] = mode
            before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
            p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
            out = p.stdout.decode("utf-8", "backslashreplace")
            rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
            print(f"--- MODE {mode} rc={p.returncode} k4rows={len(rows)} child_maxrss_kb={after} (was {before})")
            for line in rows:
                cells = line.split("\t")
                d = cells[4] if len(cells) > 4 else "<none>"
                print(f"    cells={len(cells)} detail_len={len(d)} detail={d[:160]!r}")
            for name, ch in (("SOH", b"\x01"), ("NEL", b"\x85"), ("U2028", b"\xe2\x80\xa8")):
                n = p.stdout.count(ch)
                if n:
                    print(f"    raw {name} count={n}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
