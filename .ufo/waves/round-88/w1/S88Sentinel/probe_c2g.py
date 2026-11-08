#!/usr/bin/env python3
"""S88Sentinel probe, final: two r88-introduced properties of the FLAGFAIL detail, measured on the r88 bytes and
the r87 control bytes.

P1 INJECTIVITY. Two DIFFERENT delegated stderr payloads that render as the SAME K4 detail cell. The r88 parent does
`raw.decode('utf-8','backslashreplace')` and then `_escape_text`; `backslashreplace` already turns an undecodable
byte into the four literal characters "\\xNN", which is exactly what a stderr that LITERALLY contains "\\xNN" looks
like, so the escape (injective on text) inherits the collision. The r87 control used `.decode('utf-8','replace')`,
which turned the bad byte into U+FFFD and kept the literal text distinct.

P2 HEAD BUDGET. r88 escapes FIRST and then keeps head-100 / … / tail-99 of the ESCAPED text, so a control byte
costs four characters of the 100-character head. A stderr whose control bytes precede the exception's type name
therefore loses the type name from BOTH ends of the excerpt. The r87 control kept the last 200 RAW characters, so it
lost the head too, but it also emitted the raw control bytes.

Each payload is run on the r88 tool and the r87 control; the detail cells are compared for equality.
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

# (label, payload bytes). Each PAIR is two DIFFERENT stderr payloads.
PAIRS = [
    ("byte-FF vs literal-\\xff", b"\xff", b"\\xff"),
    ("byte-80 vs literal-\\x80", b"\x80", b"\\x80"),
    ("byte-FF-line vs literal-line", b"boom \xff", b"boom \\xff"),
]


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


def detail_for(kit, payload):
    toolcopy, repo, rev = kit
    env = dict(ENV)
    env["R88_ERR"] = payload.decode("latin-1")
    p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out = p.stdout.decode("utf-8", "backslashreplace")
    rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
    if not rows:
        return None, 0
    cells = rows[0].split("\t")
    return (cells[4] if len(cells) > 4 else ""), len(cells)


HEAD_CASES = [
    ("plain-400A-then-AttributeError", b"A" * 400 + b"AttributeError: boom"),
    ("KFF3-shape-AttributeError-then-380x", b"AttributeError: " + b"x" * 380),
    ("10-SOH-then-AttributeError-then-200x", b"\x01" * 10 + b"AttributeError: " + b"x" * 200),
    ("25-SOH-then-AttributeError-then-200x", b"\x01" * 25 + b"AttributeError: " + b"x" * 200),
    ("30-SOH-then-AttributeError-then-200x", b"\x01" * 30 + b"AttributeError: " + b"x" * 200),
    ("40-SOH-then-AttributeError-then-200x", b"\x01" * 40 + b"AttributeError: " + b"x" * 200),
]


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
        print("-- P1 injectivity (two different stderr payloads, one detail?) --")
        for name, a, b in PAIRS:
            tag = name.replace("\\", "").replace("-", "_").replace(" ", "_")[:24]
            ka = make_kit(os.path.join(work, f"p1a-{label}-{tag}"), toolpath)
            kb = make_kit(os.path.join(work, f"p1b-{label}-{tag}"), toolpath)
            da, ca = detail_for(ka, a)
            db, cb = detail_for(kb, b)
            same = (da == db) and (da is not None)
            print(f"  {name}")
            print(f"      A detail={da!r}")
            print(f"      B detail={db!r}")
            print(f"      SAME DETAIL: {same}  (cells A={ca} B={cb})")
        print("-- P2 head budget (does the detail still name the exception type?) --")
        for name, payload in HEAD_CASES:
            kit = make_kit(os.path.join(work, f"p2-{label}-{name[:6]}"), toolpath)
            d, c = detail_for(kit, payload)
            named = (d is not None) and ("AttributeError" in d)
            print(f"  {name:>44}: names_AttributeError={named} cells={c}")
            print(f"      detail={d[:140]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
