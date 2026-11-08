#!/usr/bin/env python3
"""S88Sentinel probe: the parent's WRITER-digest binding under an ATOMIC writer swap.

CONTROL : the writer file is atomically replaced (temp + os.replace, so the delegated read always sees a complete
          file) with DIFFERENT honest bytes. The parent must refuse with RECEIPT-WRITER-SWAPPED.
FORGERY : the same swap, but the swapped-in writer prints a WRITER line naming the ORIGINAL (pre-swap) digest via
          os.write(1, ...) — unbuffered, so it lands in the pipe BEFORE the bootstrap's own buffered print.
          Question: does the parent's digest comparison read the forged line or the genuine one, and is the swap
          detected?

The child's stdout ordering is measured directly (the bootstrap's print() is block-buffered when stdout is a pipe;
the writer's os.write is not), so the report rests on measurement, not on an assumption about buffering.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import threading

sys.dont_write_bytecode = True

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOL = os.path.join(LANE, "tools/souji-record-agreement.py")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "s88 sentinel", "GIT_AUTHOR_EMAIL": "s88@s88.invalid",
            "GIT_COMMITTER_NAME": "s88 sentinel", "GIT_COMMITTER_EMAIL": "s88@s88.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})

W1 = ('import os\n'
      'class P:\n'
      '    def __init__(s,r,o=b"",e=b""): s.returncode,s.stdout,s.stderr=r,o,e\n'
      'def git(*a,**k): return P(1,b"",b"fatal: cannot read index\\n")\n'
      'def _truth_refusal(root): return ""\n'
      'def _flag_refusal(*a): return None\n')
D1 = hashlib.sha256(W1.encode()).hexdigest()
W2 = W1 + "# a different writer\n"
W2_FORGED = W1.replace(
    'def _truth_refusal(root): return ""',
    'def _truth_refusal(root):\n'
    '    os.write(1, b"WRITER ' + D1 + '\\n")\n'
    '    return ""\n')


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode()[:200])
    return p.stdout.decode().strip()


def make_kit(root):
    tools = os.path.join(root, "tools")
    os.makedirs(tools)
    copy = os.path.join(tools, "souji-record-agreement.py")
    shutil.copyfile(TOOL, copy)
    writer = os.path.join(tools, "souji-receipt-write.py")
    with open(writer, "w", encoding="utf-8") as f:
        f.write(W1)
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


def arm(work, label, newtext):
    kit = make_kit(os.path.join(work, label))
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
    seen.wait(10)
    tmp = writer + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(newtext)
    os.replace(tmp, writer)          # atomic: the delegated read sees one whole file or the other
    p.wait(60)
    out = b"".join(chunks).decode("utf-8", "backslashreplace")
    rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
    print(f"--- {label}: k4rows={len(rows)}")
    for l in rows:
        c = l.split("\t")
        print(f"    detail={(c[4] if len(c) > 4 else '<none>')[:240]!r}")
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
    print(f"# W1 (pre-swap) digest={D1}")
    print(f"# W2 (post-swap) digest={hashlib.sha256(W2.encode()).hexdigest()}")
    print(f"# W2_FORGED digest={hashlib.sha256(W2_FORGED.encode()).hexdigest()}")

    # the child's stdout ordering, measured directly
    boot = ("import sys, types, hashlib\n"
            "path, root = sys.argv[1], sys.argv[2]\n"
            "src = open(path, 'rb').read()\n"
            "print('WRITER %s' % hashlib.sha256(src).hexdigest())\n"
            "mod = types.ModuleType('w'); mod.__file__ = path; sys.modules['w'] = mod\n"
            "exec(compile(src, path, 'exec'), mod.__dict__)\n"
            "print('FLAGFAIL payload')\n")
    w = os.path.join(work, "order-w.py")
    with open(w, "w", encoding="utf-8") as f:
        f.write('import os\nos.write(1, b"WRITER FORGED\\n")\n')
    q = subprocess.run([sys.executable, "-I", "-B", "-c", boot, w, work],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"# child stdout ordering (writer os.write vs bootstrap print): {q.stdout!r}")

    arm(work, "CONTROL-swap-different-honest-bytes", W2)
    arm(work, "FORGERY-swap-forged-WRITER-line", W2_FORGED)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
