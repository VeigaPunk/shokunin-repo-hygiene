#!/usr/bin/env python3
"""S88Sentinel probe: the parent's WRITER-digest binding, and whether a swapped-in writer can forge the line.

Part 1 — the exact bootstrap replication: run the tool's own bootstrap source against a writer, and dump the RAW
child stdout in bytes so the ordering of the bootstrap's buffered `print('WRITER ...')` and the writer's
`os.write(1, ...)` is measured, not assumed.

Part 2 — the swap, done ATOMICALLY (temp file + os.replace), so the delegated read always sees a complete file.
Three arms: no swap; swap with an honest swapped-in writer; swap with a swapped-in writer that forges a WRITER
line naming the ORIGINAL (pre-swap) digest.
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

W_HONEST = '''import os


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

# the swapped-in writer that forges: the forged line names {DIGEST} (the digest of the bytes that DID run)
W_FORGED = '''import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    return P(1, b"", b"fatal: cannot read index\\n")


def _truth_refusal(root):
    os.write(1, b"WRITER " + b"{DIGEST}" + b"\\n")
    return ""


def _flag_refusal(*args):
    return None
'''

# the swapped-in writer that forges at MODULE level (during exec)
W_FORGED_IMPORT = '''import os

os.write(1, b"WRITER " + b"{DIGEST}" + b"\\n")


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


def atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def arm(name, work, writer_text, swap_text, digest_for_forgery=None):
    kit = make_kit(os.path.join(work, name), writer_text)
    toolcopy, repo, rev, writer = kit
    p = subprocess.Popen([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    seen = threading.Event()
    chunks = []

    def reader():
        for line in p.stdout:
            chunks.append(line)
            if line.startswith(b"# writer path="):
                seen.set()
    threading.Thread(target=reader, daemon=True).start()
    if swap_text is not None:
        seen.wait(10)
        text = swap_text
        if digest_for_forgery:
            text = text.replace("{DIGEST}", digest_for_forgery)
        atomic_write(writer, text)
    p.wait(60)
    out = b"".join(chunks).decode("utf-8", "backslashreplace")
    rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
    print(f"--- ARM {name}: k4rows={len(rows)}")
    for line in rows:
        cells = line.split("\t")
        print(f"    detail={(cells[4] if len(cells) > 4 else '<none>')[:200]!r}")
    if not rows:
        print("    NO K4 ROW -> the parent accepted the tree as verified")
    return out


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
    d_honest = sha_bytes(W_HONEST.encode())
    print(f"# honest writer digest={d_honest}")
    arm("A-no-swap", work, W_HONEST, None)
    arm("B-atomic-swap-honest", work, W_HONEST, W_HONEST)
    arm("C-atomic-swap-forged-in-truth_refusal", work, W_HONEST, W_FORGED, digest_for_forgery=d_honest)
    arm("D-atomic-swap-forged-at-import", work, W_HONEST, W_FORGED_IMPORT, digest_for_forgery=d_honest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
