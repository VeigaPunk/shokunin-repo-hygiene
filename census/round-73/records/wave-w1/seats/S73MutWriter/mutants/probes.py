#!/usr/bin/env python3
"""S73MutWriter targeted probes: reachability of the branches whose mutants survived both detectors.
Fixtures are created and committed under the seat scratch dir with explicit identity; the lane is never
touched. Every subprocess git call names -C <fixture> explicitly."""
import importlib.util
import os
import struct
import subprocess
import sys
import tempfile

S = "/fast/scratch/hyaku/souji-r73/S73MutWriter"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
W_PRIS = os.path.join(S, "writer-w.py")
W_M01 = os.path.join(S, "M01-pre-truth-dropped.py")
W_M03 = os.path.join(S, "M03-instrument-recompare-dropped.py")
W_M05 = os.path.join(S, "M05-symlink-target-unchecked.py")
INSTRUMENT = b"#!/bin/sh\necho instrument-selftest-ok\n"

_spec = importlib.util.spec_from_file_location("wmod", W_PRIS)
_w = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_w)


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def g(d, *args, **kw):
    assert d and os.path.isdir(d), f"bad fixture dir {d!r}"
    return sh(["git", "-C", d, *args], **kw)


def fixture(prefix):
    d = tempfile.mkdtemp(prefix=prefix, dir=S)
    assert d and os.path.isdir(d)
    r = g(d, "init", "-q")
    assert r.returncode == 0, r.stderr
    top = g(d, "rev-parse", "--show-toplevel")
    assert top.returncode == 0 and os.path.realpath(top.stdout.strip()) == os.path.realpath(d), top.stdout
    with open(os.path.join(d, "instrument.sh"), "wb") as f:
        f.write(INSTRUMENT)
    os.chmod(os.path.join(d, "instrument.sh"), 0o755)
    with open(os.path.join(d, "tracked.txt"), "wb") as f:
        f.write(b"clean\n")
    return d


def commit(d, msg):
    r = g(d, "add", "-A")
    assert r.returncode == 0, r.stderr
    r = g(d, "-c", "user.name=S73MutWriter", "-c", "user.email=seat@example.invalid", "commit", "-q", "-m", msg)
    assert r.returncode == 0, r.stderr


def head(d):
    r = g(d, "rev-parse", "HEAD")
    assert r.returncode == 0
    return r.stdout.strip()


def status(d):
    r = g(d, "status", "--porcelain")
    assert r.returncode == 0, r.stderr
    return r.stdout


def runw(writer, d, rev, out, command, extra=()):
    argv = [sys.executable, "-B", writer, "--root", d, "--rev", rev, "--instrument", "instrument.sh",
            "--out", out, "--allow-outside", *extra, "--command", command]
    return sh(argv, cwd=S)


def rewrite_index_stat(d, rel):
    """Rewrite the index entry's cached stat for `rel` from its current lstat (blob id kept; sha1 sum
    recomputed), then move the index mtime 5 s past the entry -- the same shape as the writer's own
    selftest helper, for symlinks/FIFOs where the bytes must not be written."""
    full = os.path.join(d, rel)
    st = os.lstat(full)
    p = os.path.join(d, ".git", "index")
    data = open(p, "rb").read()
    n = struct.unpack(">I", data[8:12])[0]
    off, out = 12, bytearray(data[:12])
    hit = 0
    for _ in range(n):
        start = off
        ns = off + 62
        z = data.index(b"\0", ns)
        end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
        if data[ns:z] == rel.encode():
            hit += 1
            # keep the entry's git mode (offset 24..28): only the cached stat fields move
            out += struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 10**9, int(st.st_mtime),
                               st.st_mtime_ns % 10**9, st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF,
                               struct.unpack(">I", data[off + 24:off + 28])[0], st.st_uid, st.st_gid,
                               st.st_size) + data[off + 40:off + 62] + data[ns:end]
        else:
            out += data[start:end]
        off = end
    assert hit == 1, f"index entry {rel!r} hit={hit}"
    out += data[off:-20]
    out += __import__("hashlib").sha1(bytes(out)).digest()
    open(p, "wb").write(bytes(out))
    os.utime(p, (st.st_mtime + 5, st.st_mtime + 5))


def show(tag, r, marker=None, out=None):
    print(f"[{tag}] rc={r.returncode} out_exists={os.path.exists(out) if out else None} "
          f"marker={os.path.exists(marker) if marker else None}")
    print(f"[{tag}] stderr={(r.stderr or '').strip()[:300]}")


def p1():
    print("=== P1 pre-run truth check: does the wrapped command run on an already-concealed forgery? ===")
    d = fixture("p1.")
    commit(d, "base")
    rev = head(d)
    exec(_w._stat_forge_code(d, "tracked.txt", b"forge\n"), {})
    assert status(d) == "", f"probe invalid, status={status(d)!r}"
    marker = os.path.join(S, "p1.marker")
    if os.path.exists(marker):
        os.unlink(marker)
    cmd = f"/bin/sh -c 'echo ran > {marker}'"
    out1 = os.path.join(S, "p1-pristine.out")
    out2 = os.path.join(S, "p1-M01.out")
    for p in (out1, out2):
        if os.path.exists(p):
            os.unlink(p)
    r1 = runw(W_PRIS, d, rev, out1, cmd)
    show("P1-pristine", r1, marker, out1)
    if os.path.exists(marker):
        os.unlink(marker)  # reset only if the pristine run already produced it
    r2 = runw(W_M01, d, rev, out2, cmd)
    show("P1-M01", r2, marker, out2)


def p2():
    print("=== P2 instrument re-compare: ignored-but-at-rev instrument changed in-run ===")
    d = fixture("p2.")
    commit(d, "base")
    rev = head(d)
    r = g(d, "rm", "--cached", "instrument.sh")
    assert r.returncode == 0, r.stderr
    with open(os.path.join(d, ".gitignore"), "wb") as f:
        f.write(b"instrument.sh\n")
    print(f"[P2] pre-run porcelain={status(d)!r}")
    assert b"?? instrument.sh" not in status(d).encode(), "instrument is untracked-visible to status"
    forge = os.path.join(S, "p2-forge.sh")
    with open(forge, "w") as f:
        f.write(f"#!/bin/sh\nprintf 'forged\\n' > '{os.path.join(d, 'instrument.sh')}'\n")
    os.chmod(forge, 0o755)
    sane = os.path.join(S, "p2-sane.out")
    if os.path.exists(sane):
        os.unlink(sane)
    rs = runw(W_PRIS, d, rev, sane, "/bin/echo hi", extra=("--allow-dirty",))
    show("P2-pristine-sane", rs, None, sane)
    out1 = os.path.join(S, "p2-pristine-forge.out")
    out2 = os.path.join(S, "p2-M03-forge.out")
    for p in (out1, out2):
        if os.path.exists(p):
            os.unlink(p)
    r1 = runw(W_PRIS, d, rev, out1, f"/bin/sh {forge}", extra=("--allow-dirty",))
    show("P2-pristine-forge", r1, None, out1)
    with open(os.path.join(d, "instrument.sh"), "wb") as f:
        f.write(INSTRUMENT)
    r2 = runw(W_M03, d, rev, out2, f"/bin/sh {forge}", extra=("--allow-dirty",))
    show("P2-M03-forge", r2, None, out2)
    if os.path.exists(out2):
        print("[P2] M03 receipt head=" + repr(open(out2, "rb").read().split(b"\n")[:2]))
    print(f"[P2] worktree instrument after M03 run={open(os.path.join(d, 'instrument.sh'), 'rb').read()!r}")


def p5():
    print("=== P5 symlink target: stat-concealed retarget ===")
    d = fixture("p5.")
    with open(os.path.join(d, "other.txt"), "wb") as f:
        f.write(b"other\n")
    os.symlink("tracked.txt", os.path.join(d, "link"))
    commit(d, "base+symlink")
    rev = head(d)
    os.unlink(os.path.join(d, "link"))
    os.symlink("other.txt", os.path.join(d, "link"))
    rewrite_index_stat(d, "link")
    st = status(d)
    print(f"[P5] post-retarget porcelain={st!r}")
    assert st == "", f"probe invalid, status={st!r}"
    out1 = os.path.join(S, "p5-pristine.out")
    out2 = os.path.join(S, "p5-M05.out")
    for p in (out1, out2):
        if os.path.exists(p):
            os.unlink(p)
    r1 = runw(W_PRIS, d, rev, out1, "/bin/echo hi")
    show("P5-pristine", r1, None, out1)
    r2 = runw(W_M05, d, rev, out2, "/bin/echo hi")
    show("P5-M05", r2, None, out2)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in (("p1", p1), ("p2", p2), ("p5", p5)):
        if which in ("all", name):
            fn()
