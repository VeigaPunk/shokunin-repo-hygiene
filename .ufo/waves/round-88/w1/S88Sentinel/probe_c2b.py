#!/usr/bin/env python3
"""S88Sentinel C2 probes, part 2: the parent-order and verdict-token boundary.

Adds the modes part 1 did not cover:
  forged_writer_clean  the writer module writes "WRITER <its own digest>\\nCLEAN\\n" to fd 1 before the
                       bootstrap's buffered WRITER line reaches the pipe: the parent's swap check passes (the
                       forged digest equals the header digest) and the parent's verdict scan reads CLEAN.
  forged_clean_only    the writer module writes "CLEAN\\n" only: lines[0] is not a WRITER line, so the parent's
                       swap check is skipped entirely and out.startswith("CLEAN") reads the verdict.
  forged_forged        the writer module writes "FORGED x\\n".
  forged_refused       the writer raises SystemExit carrying a forged MISMATCH row.
  empty               the delegated stderr is empty -> "no stderr".
  attr400             a 400-character "AttributeError: ..." line (the KFF3 shape).
  b64_writer          the FLAGFAIL payload decodes to a text starting "WRITER <digest>" -> cannot impersonate.
  b64_mismatch        the FLAGFAIL payload decodes to "MISMATCH\\tK4\\t.\\tforged\\tinjected" -> cannot inject.
  b64_badb64          the writer prints "FLAGFAIL <not base64>" as the FIRST stdout line.
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
import base64
import hashlib
import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def _mode():
    return os.environ.get("R88_MODE", "flagfail")


def _forge():
    m = _mode()
    if m == "forged_writer_clean":
        d = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
        os.write(1, b"WRITER " + d.encode() + b"\nCLEAN\n")
    elif m == "forged_clean_only":
        os.write(1, b"CLEAN\n")
    elif m == "forged_forged":
        os.write(1, b"FORGED x\n")
    elif m == "b64_writer":
        os.write(1, b"FLAGFAIL " + base64.b64encode(b"WRITER " + b"0" * 64) + b"\n")
    elif m == "b64_mismatch":
        os.write(1, b"FLAGFAIL " + base64.b64encode(b"MISMATCH\tK4\t.\tforged\tinjected") + b"\n")
    elif m == "b64_badb64":
        os.write(1, b"FLAGFAIL !!!not base64!!!\n")


def git(*args, **kwargs):
    m = _mode()
    if m == "clean":
        return P(0, b"H a.txt\0")
    if m == "empty":
        return P(1, b"", b"")
    if m == "attr400":
        return P(1, b"", b"AttributeError: " + b"x" * 380 + b"\n")
    if m == "forged_refused":
        return P(1, b"", b"fatal: cannot read index\n")
    return P(1, b"", b"fatal: cannot read index\n")


def _truth_refusal(root):
    m = _mode()
    if m == "forged_refused":
        raise SystemExit("r88 refused: bad\nMISMATCH\tK4\t.\tforged\tinjected")
    _forge()
    return ""


def _flag_refusal(*args):
    return None
'''


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.decode()[:200]}")
    return p.stdout.decode().strip()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make_kit(root):
    tools = os.path.join(root, "tools")
    os.makedirs(tools)
    copy = os.path.join(tools, "souji-record-agreement.py")
    shutil.copyfile(TOOL, copy)
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


MODES = ("forged_writer_clean", "forged_clean_only", "forged_forged", "forged_refused",
         "empty", "attr400", "b64_writer", "b64_mismatch", "b64_badb64")


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
    for mode in MODES:
        kit = make_kit(os.path.join(work, "kit-" + mode))
        toolcopy, repo, rev = kit
        env = dict(ENV)
        env["R88_MODE"] = mode
        p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        out = p.stdout.decode("utf-8", "backslashreplace")
        rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
        print(f"--- MODE {mode} rc={p.returncode} k4rows={len(rows)}")
        for line in rows:
            cells = line.split("\t")
            print(f"    cells={len(cells)} detail={cells[4] if len(cells) > 4 else '<none>'!r}")
        for name, ch in (("SOH", b"\x01"), ("NEL", b"\x85"), ("U2028", b"\xe2\x80\xa8"), ("LF", b"\n")):
            n = p.stdout.count(ch)
            if n:
                print(f"    raw {name} count={n}")
        if p.stderr.strip():
            print(f"    stderr={p.stderr.decode()[:200]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
