#!/usr/bin/env python3
"""mkfixture.py — build one isolated real-git lane for S74Sentinel gate probes.

Creates <root>/origin.git (bare) and <root>/lane (worktree) with one pushed
commit on master whose tracked file a.txt holds `alpha v1\n`, then optionally
applies the r74 GF1 same-size index stat-cache forge (worktree bytes changed to
`alpha v2\n`, index stat fields rewritten from the forged lstat, object id
kept), so `git status` reads clean while the bytes differ from the object.

Usage: mkfixture.py --root ABS [--forge]
Prints `basetip=<sha>` and `forged=<yes|no>`.
"""
import argparse
import hashlib
import os
import struct
import subprocess
import sys

IDENT = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
         "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"]


def git(repo, *args, check=True):
    assert os.path.isabs(repo) and repo, "refusing git -C with a relative path"
    p = subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=120)
    if check and p.returncode != 0:
        raise SystemExit("git %s: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")))
    return p


def forge_index_stat(repo, rel):
    st = os.lstat(os.path.join(repo, rel))
    p = os.path.join(repo, ".git", "index")
    data = open(p, "rb").read()
    if data[:4] != b"DIRC":
        raise SystemExit("bad index signature")
    ver, n = struct.unpack(">II", data[4:12])
    if ver not in (2, 3):
        raise SystemExit("index version %d" % ver)
    off, out, target, hit = 12, bytearray(data[:12]), rel.encode(), False
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
        raise SystemExit("%s not in index" % rel)
    out += data[off:-20]
    out += hashlib.sha1(bytes(out)).digest()
    with open(p, "wb") as f:
        f.write(bytes(out))
    t = st.st_mtime + 5
    os.utime(p, (t, t))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--forge", action="store_true")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    if not root.startswith("/fast/scratch/hyaku/souji-r74/"):
        raise SystemExit("refusing root outside the seat scratch: %r" % root)
    origin = os.path.join(root, "origin.git")
    lane = os.path.join(root, "lane")
    os.makedirs(root, exist_ok=True)
    git(root, "init", "-q", "--bare", "-b", "master", origin)
    git(root, "init", "-q", "-b", "master", lane)
    top = git(lane, "rev-parse", "--show-toplevel").stdout.strip().decode()
    if top != os.path.realpath(lane):
        raise SystemExit("fixture toplevel mismatch: %r != %r" % (top, os.path.realpath(lane)))
    with open(os.path.join(lane, "a.txt"), "wb") as f:
        f.write(b"alpha v1\n")
    git(lane, "add", "a.txt")
    git(lane, *IDENT, "commit", "-qm", "base")
    git(lane, "remote", "add", "origin", origin)
    git(lane, "push", "-q", "-u", "origin", "master")
    tip = git(lane, "rev-parse", "HEAD").stdout.strip().decode()
    forged = "no"
    if a.forge:
        with open(os.path.join(lane, "a.txt"), "wb") as f:
            f.write(b"alpha v2\n")
        forge_index_stat(lane, "a.txt")
        forged = "yes"
    print("basetip=%s" % tip)
    print("forged=%s" % forged)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
