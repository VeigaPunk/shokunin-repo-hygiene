#!/usr/bin/env python3
"""S88Sentinel probe: can a forged WRITER line mask a real writer swap?

Setup: a tool copy beside a receipt writer W1 in a scratch dir, and a hermetic repo. A swapper process watches the
tool's stdout for the header line the tool prints (which names the sha256 of the writer bytes the PARENT read) and,
the moment it appears, replaces W1 with W2 before the tool's delegated bootstrap compiles the writer.

W2 is the honest writer except that its module code writes a WRITER line to fd 1 (unbuffered, so it lands in the
pipe BEFORE the bootstrap's own buffered print) naming the digest of W1 -- the bytes that did NOT run.

Without the forgery the parent sees the bootstrap's WRITER line (digest of W2) != header digest (digest of W1) and
refuses with RECEIPT-WRITER-SWAPPED. With the forgery the parent compares the FORGED first line to the header digest,
they match, and the swap is masked.

Runs both the forged and the un-forged writer so the delta is measured.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import threading
import time

sys.dont_write_bytecode = True

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOL = os.path.join(LANE, "tools/souji-record-agreement.py")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "s88 sentinel", "GIT_AUTHOR_EMAIL": "s88@s88.invalid",
            "GIT_COMMITTER_NAME": "s88 sentinel", "GIT_COMMITTER_EMAIL": "s88@s88.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})

# W1: the honest writer. Its git() fails the delegated read, so the bootstrap's verdict is FLAGFAIL.
W1 = '''import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    return P(1, b"", b"fatal: cannot read index\\n")


def _truth_refusal(root):
    return ""


def _flag_refusal(*args):
    return None
'''

# W2: the swapped-in writer. Same behaviour, plus a forged WRITER line naming the digest of W1.
W2_TEMPLATE = '''import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    return P(1, b"", b"fatal: cannot read index\\n")


def _truth_refusal(root):
    # the forged line names W1's digest: bytes that did NOT run
    os.write(1, b"WRITER %s\\n" % b"{DIGEST}".encode())
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


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def make_kit(root, writer_text):
    tools = os.path.join(root, "tools")
    os.makedirs(tools)
    copy = os.path.join(tools, "souji-record-agreement.py")
    shutil.copyfile(TOOL, copy)
    writer = os.path.join(tools, "souji-receipt-write.py")
    with open(writer, "w", encoding="utf-8") as f:
        f.write(writer_text)
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
    return copy, repo, git(repo, "rev-parse", "HEAD"), writer


def run(toolcopy, repo, rev):
    p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    out = p.stdout.decode("utf-8", "backslashreplace")
    rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
    return out, rows


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
    w1_bytes = W1.encode("utf-8")
    d1 = sha_bytes(w1_bytes)
    print(f"# W1 digest={d1}")

    # --- arm A: no swap at all (baseline) ---
    kit = make_kit(os.path.join(work, "armA"), W1)
    out, rows = run(kit[0], kit[1], kit[2])
    print(f"--- ARM A no swap: k4rows={len(rows)}")
    for line in rows:
        cells = line.split("\t")
        print(f"    detail={(cells[4] if len(cells) > 4 else '<none>')[:180]!r}")

    # --- arm B: the swap happens, and the swapped-in writer does NOT forge a WRITER line ---
    kit = make_kit(os.path.join(work, "armB"), W1)
    toolcopy, repo, rev, writer = kit
    w2_plain = W1.replace("def _truth_refusal(root):\n    return \"\"",
                          "def _truth_refusal(root):\n    return \"\"  # swapped in, honest")
    state = {"swapped": False}

    def swapper():
        # wait for the tool to print its header (the parent has now read the writer's bytes)
        for _ in range(20000):
            time.sleep(0.001)
            if state["swapped"]:
                return
        # the tool is a subprocess; poll the writer file for the parent's read by watching its mtime is not
        # enough, so instead we swap after a short delay that lands inside the run
    # deterministic swap point: the tool prints its header first; we capture stdout live.
    p = subprocess.Popen([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    header_seen = threading.Event()
    lines_out = []

    def reader():
        for line in p.stdout:
            lines_out.append(line.decode("utf-8", "backslashreplace"))
            if line.startswith(b"# writer path="):
                header_seen.set()
    t = threading.Thread(target=reader, daemon=True)
    t.start()
    header_seen.wait(10)
    with open(writer, "w", encoding="utf-8") as f:
        f.write(w2_plain)
    p.wait(60)
    out = "".join(lines_out)
    rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
    print(f"--- ARM B swap, no forgery: k4rows={len(rows)}")
    for line in rows:
        cells = line.split("\t")
        print(f"    detail={(cells[4] if len(cells) > 4 else '<none>')[:180]!r}")

    # --- arm C: the swap happens and the swapped-in writer FORGES the WRITER line naming W1's digest ---
    kit = make_kit(os.path.join(work, "armC"), W1)
    toolcopy, repo, rev, writer = kit
    w2_forged = W2_TEMPLATE.replace("{DIGEST}", d1)
    p = subprocess.Popen([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    header_seen = threading.Event()
    lines_out = []

    def reader2():
        for line in p.stdout:
            lines_out.append(line.decode("utf-8", "backslashreplace"))
            if line.startswith(b"# writer path="):
                header_seen.set()
    t = threading.Thread(target=reader2, daemon=True)
    t.start()
    header_seen.wait(10)
    with open(writer, "w", encoding="utf-8") as f:
        f.write(w2_forged)
    p.wait(60)
    out = "".join(lines_out)
    rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
    print(f"--- ARM C swap + forged WRITER line: k4rows={len(rows)}")
    for line in rows:
        cells = line.split("\t")
        print(f"    detail={(cells[4] if len(cells) > 4 else '<none>')[:180]!r}")
    print("    (no K4 row at all => the swap was masked and the tree was accepted as verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
