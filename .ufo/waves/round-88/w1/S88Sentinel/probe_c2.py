#!/usr/bin/env python3
"""S88Sentinel adversarial probes for the r88 C2 FLAGFAIL re-framing.

Each probe puts a stub receipt writer beside a COPY of tools/souji-record-agreement.py and runs the tool's public
path (--root/--rev) on a hermetic scratch repo, then reads the tool's stdout the way a line-oriented consumer
would: split on "\\n", keep the MISMATCH\\tK4\\t rows, and count the tab cells of each detail.

No lane byte is written. Everything is built under --work (never /tmp). Stdlib only.
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

# stub writer: mode chosen by R88_MODE. Every mode keeps the module silent on stdout unless it deliberately
# forges, so the bootstrap's own verdict is the only stdout content in the honest modes.
STUB = r'''
import hashlib
import os
import sys


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def _mode():
    return os.environ.get("R88_MODE", "flagfail")


def git(*args, **kwargs):
    m = _mode()
    if m == "clean":
        return P(0, b"H a.txt\0")
    if m == "flagfail":
        return P(1, b"", b"fatal: cannot read index\n")
    if m == "big":
        return P(1, b"", b"A" * 10_000_000)
    if m == "u2028":
        return P(1, b"", b"fatal: \xe2\x80\xa8 marker\n")
    if m == "nonutf8":
        return P(1, b"", b"fatal: \xff\xfe bad bytes\n")
    if m == "tab":
        return P(1, b"", b"fatal: a\tb\n")
    if m == "trace":
        return P(1, b"", b"Traceback (most recent call last):\n  File \"w\", line 1\nAttributeError: boom\n")
    return P(1, b"", b"fatal: cannot read index\n")


def _truth_refusal(root):
    m = _mode()
    if m == "noverdict":
        raise ValueError("boom\twith\x01tab")
    if m in ("forged_writer", "forged_writer_self", "forged_clean", "invalid_b64", "flagfail_clean"):
        # forge on fd 1 BEFORE the bootstrap's buffered WRITER line reaches the pipe
        if m == "forged_writer":
            os.write(1, b"WRITER " + b"0" * 64 + b"\n")
        elif m == "forged_writer_self":
            src = open(__file__, "rb").read()
            os.write(1, b"WRITER " + hashlib.sha256(src).hexdigest().encode() + b"\n")
        elif m == "forged_clean":
            os.write(1, b"CLEAN\n")
        elif m == "invalid_b64":
            os.write(1, b"FLAGFAIL !!!not base64!!!\n")
        elif m == "flagfail_clean":
            os.write(1, b"CLEAN\n")
        return ""
    return ""


def _flag_refusal(*args):
    return None
'''


class FixtureError(Exception):
    pass


def git(repo, *args):
    if not repo or not os.path.isabs(repo):
        raise FixtureError(f"refusing git -C with {repo!r}")
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise FixtureError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.decode()[:200]}")
    return p.stdout.decode().strip()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make_kit(root, mode):
    tools = os.path.join(root, "tools")
    os.makedirs(tools)
    copy = os.path.join(tools, "souji-record-agreement.py")
    shutil.copyfile(TOOL, copy)
    writer = os.path.join(tools, "souji-receipt-write.py")
    with open(writer, "w", encoding="utf-8") as f:
        f.write(STUB)
    repo = os.path.join(root, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q")
    top = git(repo, "rev-parse", "--show-toplevel")
    if os.path.realpath(top) != os.path.realpath(repo):
        raise FixtureError("fixture toplevel is not the fixture dir")
    with open(os.path.join(repo, "a.txt"), "w", encoding="utf-8") as f:
        f.write("seed\n")
    git(repo, "add", "--", "a.txt")
    git(repo, "commit", "-q", "--no-verify", "-m", "s88 fixture seed")
    return copy, repo, git(repo, "rev-parse", "HEAD"), writer


def run_case(kit, mode):
    toolcopy, repo, rev, writer = kit
    env = dict(ENV)
    env["R88_MODE"] = mode
    p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out = p.stdout.decode("utf-8", "backslashreplace")
    raw = p.stdout
    rows = []
    for line in out.split("\n"):
        if not line.startswith("MISMATCH\tK4\t"):
            continue
        cells = line.split("\t")
        rows.append({"line": line, "cells": len(cells), "detail": cells[4] if len(cells) > 4 else "<none>"})
    return {"out": out, "raw": raw, "rows": rows, "rc": p.returncode,
            "stderr": p.stderr.decode("utf-8", "backslashreplace")}


MODES = ("flagfail", "trace", "big", "u2028", "nonutf8", "tab", "clean",
         "forged_writer", "forged_writer_self", "forged_clean", "invalid_b64", "noverdict")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--mode", default=None)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("S88-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"S88-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    print(f"# tool sha256={sha(TOOL)}")
    modes = (ns.mode,) if ns.mode else MODES
    for mode in modes:
        kit = make_kit(os.path.join(work, "kit-" + mode), mode)
        r = run_case(kit, mode)
        print(f"--- MODE {mode} rc={r['rc']} k4rows={len(r['rows'])}")
        if r["rows"]:
            for row in r["rows"]:
                one_line = "\n" not in row["line"] and "\r" not in row["line"]
                print(f"    cells={row['cells']} one_line={one_line} detail={row['detail']!r}")
        else:
            print("    (no K4 row)")
        # raw control bytes in the whole stdout
        for name, ch in (("SOH", b"\x01"), ("NEL", b"\x85"), ("U2028", b"\xe2\x80\xa8"),
                         ("TAB", b"\t"), ("CR", b"\r")):
            n = r["raw"].count(ch)
            if n:
                print(f"    raw {name} count={n}")
        if r["stderr"].strip():
            print(f"    stderr={r['stderr'][:300]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
