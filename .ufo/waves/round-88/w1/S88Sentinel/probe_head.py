#!/usr/bin/env python3
"""S88Sentinel probe: does the r88 escape-first order still keep the exception's TYPE NAME in the head?

r88 `_one_line` escapes FIRST and bounds the ESCAPED text (head 100 / … / tail 99). An escape expands one byte to
four characters (\\xNN), so 25+ control bytes at the front of the stderr consume the whole 100-character head before
the exception's type name is reached. r87's `_stderr_tail` bounded the RAW text (head 100 / … / tail 99) and then the
parent embedded it raw, so the type name at raw position 0 always survived.

This measures the same stderr on the r88 bytes and the r87 control bytes:
  A  400 * 'A' then "AttributeError: boom"          (the KFF3 shape: no control bytes)
  B  40 SOH then "AttributeError: " then 200 'x'     (control bytes ahead of the type name)
  C  40 SOH then "AttributeError: boom"             (short message: the name may survive in the tail)
  D  120 SOH then "AttributeError: boom"            (as in probe_c2d)

Reported: the detail, whether it names AttributeError, and how many raw bytes of the stderr the head covers.
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
    return P(1, b"", os.environ["R88_ERR"].encode("latin-1"))


def _truth_refusal(root):
    return ""


def _flag_refusal(*args):
    return None
'''

CASES = {
    "A-400A-then-AttributeError": b"A" * 400 + b"AttributeError: boom",
    "B-40SOH-then-AttributeError-then-200x": b"\x01" * 40 + b"AttributeError: " + b"x" * 200,
    "C-40SOH-then-AttributeError-boom": b"\x01" * 40 + b"AttributeError: boom",
    "D-120SOH-then-AttributeError-boom": b"\x01" * 120 + b"AttributeError: boom",
}


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
        print(f"===== TOOL {label} sha256={hashlib.sha256(open(toolpath,'rb').read()).hexdigest()}")
        for name, payload in CASES.items():
            kit = make_kit(os.path.join(work, f"kit-{label}-{name[:2]}"), toolpath)
            toolcopy, repo, rev = kit
            env = dict(ENV)
            env["R88_ERR"] = payload.decode("latin-1")
            p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            out = p.stdout.decode("utf-8", "backslashreplace")
            rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
            d = rows[0].split("\t")[4] if rows and len(rows[0].split("\t")) > 4 else ""
            print(f"  {name:>42}: k4rows={len(rows)} names_AttributeError={'AttributeError' in d} "
                  f"detail={d[:120]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
