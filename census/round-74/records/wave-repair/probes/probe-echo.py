#!/usr/bin/env python3
"""probe-echo.py — S74Sentinel: does the stage-W gate echo tracked path names to
stderr unescaped?

Two surfaces:
  (a) status-listed paths   -> `printf 'detail-clean: %s\\n' "$status"`  (git porcelain quoting applies)
  (b) stat-cache-forged paths -> writer `_truth_refusal` builds
      `", ".join(os.fsdecode(p) for p in sorted(bad)[:5])` and the gate prints it
      with `printf 'detail-clean: byte truth: %s\\n'` — no quoting at all.

Fixture names carry a newline, an ESC (0x1b) and a CR. A name is chosen so that
the injected line reads exactly `check-clean=PASS`, to show that a merged 2>&1
receipt can be made to carry a forged PASS line.

Usage: probe-echo.py --scratch ABS --gate DIR
"""
import argparse
import hashlib
import os
import struct
import subprocess
import sys

IDENT = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
         "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"]


def git(repo, *args, check=True, data=None):
    assert os.path.isabs(repo) and repo, "refusing git -C with a relative path"
    p = subprocess.run(["git", "-C", repo, *args], input=data, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=120)
    if check and p.returncode != 0:
        raise SystemExit("git %s: %s" % (" ".join(map(str, args)), p.stderr.decode("utf-8", "replace")))
    return p


def forge_index_stat(repo, rel):
    st = os.lstat(os.path.join(os.fsencode(repo), rel))
    p = os.path.join(repo, ".git", "index")
    data = open(p, "rb").read()
    ver, n = struct.unpack(">II", data[4:12])
    off, out, target, hit = 12, bytearray(data[:12]), rel, False
    for _ in range(n):
        start = off
        fixed = data[off:off + 62]
        sha, flags = fixed[40:60], fixed[60:62]
        mode = struct.unpack(">I", fixed[24:28])[0]
        ns = off + 62
        z = data.index(b"\0", ns)
        name = data[ns:z]
        tail_end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
        if name == target:
            hit = True
            fixed = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                                int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                                st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF, mode,
                                st.st_uid, st.st_gid, st.st_size & 0xFFFFFFFF) + sha + flags
            out += fixed + data[ns:tail_end]
        else:
            out += data[start:tail_end]
        off = tail_end
    if not hit:
        raise SystemExit("%r not in index" % rel)
    out += data[off:-20]
    out += hashlib.sha1(bytes(out)).digest()
    open(p, "wb").write(bytes(out))
    t = st.st_mtime + 5
    os.utime(p, (t, t))


def lane(root):
    origin = os.path.join(root, "origin.git")
    cl = os.path.join(root, "lane")
    os.makedirs(root, exist_ok=True)
    git(root, "init", "-q", "--bare", "-b", "master", origin)
    git(root, "init", "-q", "-b", "master", cl)
    if git(cl, "rev-parse", "--show-toplevel").stdout.strip().decode() != os.path.realpath(cl):
        raise SystemExit("fixture toplevel mismatch")
    git(cl, "remote", "add", "origin", origin)
    return cl


def commit(cl, names):
    for n in names:
        with open(os.path.join(os.fsencode(cl), n), "wb") as f:
            f.write(b"AAAA\n")
        git(cl, "add", "--", n)
    git(cl, *IDENT, "commit", "-qm", "base")
    git(cl, "push", "-q", "-u", "origin", "master")


def gate(gate_dir, cl, root):
    rep = os.path.join(root, "report.md")
    pre = os.path.join(root, "prereg.txt")
    open(rep, "w").write("# Report\n\n## SHONEN\n[~] box `a`\n")
    open(pre, "w").write("prereg\n")
    p = subprocess.run(["bash", os.path.join(gate_dir, "gate-w.sh"), "--lane", cl,
                        "--branch", "master", "--report", rep, "--prereg", pre],
                       cwd=cl, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    return p


def show(label, p):
    combined = p.stdout + p.stderr
    print("---- %s rc=%d ----" % (label, p.returncode))
    print("combined-repr: %r" % combined[:600])
    print("check-clean lines: %r" % [l for l in combined.split(b"\n") if l.startswith(b"check-clean=")])
    print("raw-ESC-in-output: %s  raw-CR-in-output: %s"
          % (b"\x1b" in combined, b"\r" in combined))
    print("forged-PASS-line-present: %s"
          % any(l == b"check-clean=PASS" for l in combined.split(b"\n")))
    return combined


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--gate", required=True)
    a = ap.parse_args(argv)
    S = os.path.abspath(a.scratch)
    if not S.startswith("/fast/scratch/hyaku/souji-r74/"):
        raise SystemExit("scratch outside the seat scratch")

    # (a) status-listed path with ESC + newline: git porcelain must quote it.
    R = os.path.join(S, "q1")
    os.makedirs(R, exist_ok=True)
    cl = lane(R)
    evil = b"esc\x1b[31mred\x1b[0m.txt"
    commit(cl, [evil])
    with open(os.path.join(os.fsencode(cl), evil), "ab") as f:
        f.write(b"CHANGED\n")
    print("=== (a) status-listed path, git porcelain quoting ===")
    st = git(cl, "status", "--porcelain=v1", "--untracked-files=all").stdout
    print("git-status-raw-repr: %r" % st)
    show("status-path", gate(a.gate, cl, R))

    # (b) status-clean forged path whose name injects a line and an ESC.
    R = os.path.join(S, "q2")
    os.makedirs(R, exist_ok=True)
    cl = lane(R)
    inject = b"inj\ncheck-clean=PASS\n\x1b[2Jz.txt"
    commit(cl, [inject])
    full = os.path.join(os.fsencode(cl), inject)
    with open(full, "wb") as f:
        f.write(b"BBBB\n")
    forge_index_stat(cl, inject)
    print()
    print("=== (b) stat-cache-forged path, writer message ===")
    st = git(cl, "status", "--porcelain=v1", "--untracked-files=all").stdout
    print("git-status-raw-repr: %r (empty => status-clean)" % st)
    show("forged-path", gate(a.gate, cl, R))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
