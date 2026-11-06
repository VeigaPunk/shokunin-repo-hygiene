#!/usr/bin/env python3
"""S73ExecEvade — falsification of the stage-W receipt writer's byte-truth check (r73 C1).

Tests the writer at b84ff90bff05fb057c5a8c4b0661a9ec41d9e4a2 (sha256 d1ad5c79...) against
forged bytes that git status reports clean (index stat-cache rewrite) and against honest trees.

Routes (target list):
  a  index v4 (prefix-compressed) forged stat entry
  b  split index, forged stat entry in the shared index
  c  newline/CR/tab/backslash/leading-quote/non-UTF-8 path names
  d  detached background forge after the post-run checks, before publication
  e  hard-link replacement; honest hard link
  f  .gitattributes text/eol conversion
  g  core.symlinks=false with a tracked symlink (honest tree)
  h  intent-to-add / staged / rename under --allow-dirty
  i  (extra) stale --rev: no rev<->HEAD binding

Usage: python3 -B evade-probe.py --work DIR [--only a,b,...]
Every fixture is created under --work (must be outside the lane); the writer is a scratch copy.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import stat as statmod
import shutil
import struct
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-73/w1/S73ExecEvade")
WRITER_SRC = os.path.join(LANE, "tools/souji-receipt-write.py")
WRITER_SHA = "d1ad5c797110429f4edc67cce6eb45a94686490c09d25a5693950bf3a50f7c39"
WRITER = os.path.join(SEAT, "souji-receipt-write.py")
RACER = os.path.join(SEAT, "racer.py")
TRUTH_CLASS = "RECEIPT-WORKTREE-STAT-CONCEALED"
GIT_ID = ("-c", "user.email=s73exec@example.invalid", "-c", "user.name=S73ExecEvade")
OUTPUT = []

INSTRUMENT = b"#!/bin/sh\necho instrument-ok\n"
SEED = {"tracked.txt": b"clean\n", "tools/counter.py": b"counter v1\n"}
ODD_NAMES = [b"nl\nname.txt", b"quote\"lead.txt", b"back\\slash.txt", b"tab\tname.txt",
             b"cr\rname.txt", b"raw-\xff-name.txt", b'"n\\\n\t\xff.txt']


def env():
    e = {k: v for k, v in os.environ.items()
         if not k.startswith("GIT_") and k not in ("HOME", "XDG_CONFIG_HOME")}
    e.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
              "GIT_AUTHOR_DATE": "2026-11-06T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-06T12:00:00Z"})
    return e


def g(repo, *args, data=None, check=True, cwd=None):
    r = subprocess.run(["git", "-C", repo, *args], input=data, capture_output=True, env=env(),
                       timeout=180, cwd=cwd)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {repo}: {r.stderr.decode('utf-8', 'replace')}")
    return r


def gb(repo, *args, data=None):
    return g(repo, *args, data=data, check=True).stdout


def fixture(work, name, core=None):
    case = os.path.join(work, name)
    shutil.rmtree(case, ignore_errors=True)
    repo = os.path.join(case, "repo")
    os.makedirs(os.path.join(repo, "tools"), exist_ok=True)
    r = subprocess.run(["git", "-C", repo, "init", "-q"], capture_output=True, env=env())
    if r.returncode != 0:
        raise SystemExit(f"git init failed: {r.stderr.decode()}")
    top = gb(repo, "rev-parse", "--show-toplevel").decode().strip()
    if os.path.realpath(top) != os.path.realpath(repo):
        raise SystemExit(f"fixture toplevel mismatch {top!r} != {repo!r}")
    for k, v in (core or {}).items():
        g(repo, "config", k, v)
    for rel, data in SEED.items():
        with open(os.path.join(repo, rel), "wb") as f:
            f.write(data)
    with open(os.path.join(repo, "instrument.sh"), "wb") as f:
        f.write(INSTRUMENT)
    os.chmod(os.path.join(repo, "instrument.sh"), 0o755)
    return repo


def commit_all(repo, msg="seed"):
    g(repo, "add", "-A")
    g(repo, *GIT_ID, "commit", "-q", "-m", msg)
    return gb(repo, "rev-parse", "HEAD").decode().strip()


def head(repo):
    return gb(repo, "rev-parse", "HEAD").decode().strip()


def status(repo):
    return gb(repo, "status", "--porcelain")


def blob(repo, oid):
    return gb(repo, "cat-file", "blob", oid.decode())


# ---------------------------------------------------------------- index plumbing
def _u32b(v):
    return struct.pack(">I", v & 0xFFFFFFFF)


def stat40(st):
    return (_u32b(int(st.st_ctime)) + _u32b(st.st_ctime_ns % 10 ** 9)
            + _u32b(int(st.st_mtime)) + _u32b(st.st_mtime_ns % 10 ** 9)
            + _u32b(st.st_dev) + _u32b(st.st_ino) + _u32b(st.st_mode)
            + _u32b(st.st_uid) + _u32b(st.st_gid) + _u32b(st.st_size))


def index_version(path):
    data = open(path, "rb").read()
    if data[:4] != b"DIRC":
        raise SystemExit(f"{path}: not a DIRC file")
    return struct.unpack(">I", data[4:8])[0]


def iter_entries(data):
    """Yield (name, start, end, stat40) for index versions 2, 3 and 4 (bytes)."""
    if data[:4] != b"DIRC":
        raise SystemExit("not a DIRC file")
    ver, n = struct.unpack(">II", data[4:12])
    off, prev = 12, b""
    for _ in range(n):
        start = off
        flags = struct.unpack(">H", data[off + 60:off + 62])[0]
        p = off + 62
        if flags & 0x4000:
            p += 2
        if ver == 4:
            c = data[p]
            p += 1
            strip = c & 0x7F
            while c & 0x80:
                strip += 1
                c = data[p]
                p += 1
                strip = (strip << 7) + (c & 0x7F)
            z = data.index(b"\0", p)
            name = prev[:len(prev) - strip] + data[p:z]   # v4 strip = bytes dropped from prev's END
            end = z + 1
        elif ver in (2, 3):
            z = data.index(b"\0", p)
            name = data[p:z]
            end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
        else:
            raise SystemExit(f"unsupported index version {ver}")
        yield name, start, end, data[start:start + 40]
        prev, off = name, end


def entry_stat40(index_path, rel):
    rel = os.fsencode(rel) if isinstance(rel, str) else rel
    data = open(index_path, "rb").read()
    for name, start, end, s40 in iter_entries(data):
        if name == rel:
            return s40
    return None


def patch_index(index_path, rel, st):
    """Rewrite one entry's 40-byte stat block to `st`; keep mode/oid/flags/name; recompute sha1."""
    rel = os.fsencode(rel) if isinstance(rel, str) else rel
    data = open(index_path, "rb").read()
    out, hit = bytearray(data), False
    for name, start, end, _ in iter_entries(data):
        if name == rel:
            out[start:start + 40] = stat40(st)
            hit = True
            break
    if not hit:
        raise SystemExit(f"{rel!r} not in {index_path}")
    body = bytes(out[:-20])
    out[-20:] = hashlib.sha1(body).digest()
    with open(index_path, "wb") as f:
        f.write(bytes(out))
    t = st.st_mtime + 5
    os.utime(index_path, (t, t))


def forge_file_stat(repo, rel, forged):
    full = os.path.join(repo, rel)
    with open(full, "wb") as f:
        f.write(forged)
    st = os.lstat(full)
    patch_index(os.path.join(repo, ".git", "index"), rel, st)
    return st


def forge_code(repo, rel_bytes, forged, mac=0o755):
    """Self-contained python source: write forged bytes to repo/rel and rewrite the index stat."""
    return (
        "import hashlib, os, struct\n"
        f"repo, rel, forged, mode = {repo!r}, {rel_bytes!r}, {forged!r}, {mac!r}\n"
        "full = os.path.join(repo, rel)\n"
        "open(full, 'wb').write(forged)\n"
        "os.chmod(full, mode)\n"
        "st = os.lstat(full)\n"
        "p = os.path.join(repo, '.git', 'index')\n"
        "data = open(p, 'rb').read()\n"
        "assert data[:4] == b'DIRC'\n"
        "ver, n = struct.unpack('>II', data[4:12])\n"
        "off, prev, out, hit = 12, b'', bytearray(data), False\n"
        "for _ in range(n):\n"
        "    start = off\n"
        "    flags = struct.unpack('>H', data[off+60:off+62])[0]\n"
        "    q = off + 62\n"
        "    if flags & 0x4000: q += 2\n"
        "    if ver == 4:\n"
        "        c = data[q]; q += 1; strip = c & 0x7f\n"
        "        while c & 0x80:\n"
        "            strip += 1; c = data[q]; q += 1; strip = (strip << 7) + (c & 0x7f)\n"
        "        z = data.index(b'\\0', q); name = prev[:len(prev)-strip] + data[q:z]; end = z + 1\n"
        "    else:\n"
        "        z = data.index(b'\\0', q); name = data[q:z]; end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)\n"
        "    if name == rel:\n"
        "        s = struct.pack('>10I', int(st.st_ctime), st.st_ctime_ns % 10**9, int(st.st_mtime),\n"
        "                        st.st_mtime_ns % 10**9, st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF,\n"
        "                        st.st_mode, st.st_uid, st.st_gid, st.st_size)\n"
        "        out[start:start+40] = s; hit = True\n"
        "    prev = name; off = end\n"
        "assert hit, 'entry not found'\n"
        "out[-20:] = hashlib.sha1(bytes(out[:-20])).digest()\n"
        "open(p, 'wb').write(bytes(out))\n"
        "os.utime(p, (st.st_mtime + 5, st.st_mtime + 5))\n")


# ---------------------------------------------------------------- writer + truth
def split_index_files(repo):
    return glob.glob(os.path.join(repo, ".git", "sharedindex.*"))


def truth(repo, rev):
    """Stat-free oracle: every path at rev vs the worktree (bytes), plus index-only paths."""
    rb = os.fsencode(repo)
    diffs, extra, seen = [], [], set()
    for rec in gb(repo, "ls-tree", "-r", "-z", rev).split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        mode, typ, oid = meta.split(b" ")
        seen.add(path)
        if mode == b"160000":
            continue
        full = os.path.join(rb, path)
        want = blob(repo, oid)
        if mode == b"120000":
            try:
                if os.path.islink(full) and os.readlink(full) == want:
                    continue
            except OSError:
                pass
            diffs.append(path)
            continue
        try:
            with open(full, "rb") as f:
                have = f.read()
        except OSError:
            diffs.append(path)
            continue
        if have != want:
            diffs.append(path)
    for rec in gb(repo, "ls-files", "-s", "-z", ":(top)").split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        if path not in seen:
            extra.append(path)
    return diffs, extra


def run_writer(repo, rev, out, extra=None, argv=None, max_bytes=None):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = [sys.executable, "-B", WRITER, "--root", repo, "--rev", rev, "--instrument", "instrument.sh",
           "--out", out, "--allow-outside"]
    if max_bytes is not None:
        cmd += ["--max-bytes", str(max_bytes)]
    cmd += list(extra or [])
    if argv is not None:
        cmd += ["--", *argv]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env(), timeout=300,
                       cwd=os.path.dirname(out))
    wrote = os.path.isfile(out)
    lines = [ln for ln in (p.stderr or "").strip().splitlines() if ln.strip()]
    tok = ""
    if lines:
        m = re.match(r"refused: ([A-Z][A-Z0-9-]+):", lines[-1].strip())
        tok = m.group(1) if m else lines[-1].strip().split(":")[0][:60]
    return {"rc": p.returncode, "wrote": wrote, "class": tok, "stderr": (lines[-1] if lines else "")[:300],
            "stdout": (p.stdout or "").strip()[:200], "out": out}


def show(paths):
    return ",".join(os.fsdecode(p) for p in paths).replace("\n", "\\n").replace("\r", "\\r")[:200] or "-"


def record(route, scope, expect, w, diffs, extra, pre=None, post=None, note=""):
    if w["wrote"] and (diffs or extra):
        verdict = "FORGERY"
    elif w["wrote"]:
        verdict = "ACCEPT"
    elif diffs or extra:
        verdict = "CAUGHT"
    else:
        verdict = "OVER-REFUSAL"
    ok = verdict == expect
    if scope == "clean-status" and (pre or b"").strip():
        ok = False
        note = (note + " FIXTURE-DIRTY-MARKED-CLEAN").strip()
    OUTPUT.append({"route": route, "scope": scope, "expect": expect, "got": verdict, "ok": ok,
                   "rc": w["rc"], "wrote": w["wrote"], "class": w["class"],
                   "truth": show(diffs), "extra": show(extra),
                   "pre_status": (pre or b"").decode("utf-8", "replace").replace("\n", "|") or "<clean>",
                   "post_status": (post or b"").decode("utf-8", "replace").replace("\n", "|") or "<clean>",
                   "note": note})
    print(f"PROBE route={route} scope={scope} rc={w['rc']} wrote={int(w['wrote'])} class={w['class'] or '-'} "
          f"truth={show(diffs)} extra={show(extra)} verdict={verdict} expect={expect} ok={int(ok)}"
          + (f" note={note}" if note else ""))


# ---------------------------------------------------------------- routes
def route_a(work):
    repo = fixture(work, "a-v4")
    rev = commit_all(repo)
    g(repo, "update-index", "--index-version", "4")
    ver = index_version(os.path.join(repo, ".git", "index"))
    forge_file_stat(repo, "tools/counter.py", b"counter v2\n")
    st = os.lstat(os.path.join(repo, "tools/counter.py"))
    idx = os.path.join(repo, ".git", "index")
    forged_stat = entry_stat40(idx, b"tools/counter.py") == stat40(st)
    oid_before = gb(repo, "ls-files", "-s", "-z", "tools/counter.py").split(b" ")[1].decode()
    pre = status(repo)
    out = os.path.join(work, "a-v4", "out", "receipt.txt")
    w = run_writer(repo, rev, out)
    diffs, extra = truth(repo, rev)
    note = f"index_version={ver} stat_forged={forged_stat} blob={oid_before[:12]}"
    record("a-v4-forge", "clean-status", "CAUGHT", w, diffs, extra, pre, status(repo), note)


def route_b(work):
    repo = fixture(work, "b-split")
    rev = commit_all(repo)
    forge_file_stat(repo, "tools/counter.py", b"counter v2\n")
    st = os.lstat(os.path.join(repo, "tools/counter.py"))
    g(repo, "update-index", "--split-index")
    shared = split_index_files(repo)
    # the split rewrite reset the main index mtime below the forged entry's ctime; move it past the entry
    # so git's racy-clean test trusts the stat cache (the r72 D3 forge does the same to the plain index)
    t = max(st.st_ctime, st.st_mtime) + 5
    for p in [os.path.join(repo, ".git", "index"), *shared]:
        os.utime(p, (t, t))
    stat_in_shared = [p for p in shared if entry_stat40(p, b"tools/counter.py") == stat40(st)]
    pre = status(repo)
    out = os.path.join(work, "b-split", "out", "receipt.txt")
    w = run_writer(repo, rev, out)
    diffs, extra = truth(repo, rev)
    note = f"shared={len(shared)} forged_stat_in_shared={len(stat_in_shared)}"
    record("b-split-forge", "clean-status", "CAUGHT", w, diffs, extra, pre, status(repo), note)


def route_c(work):
    repo = fixture(work, "c-odd")
    rb = os.fsencode(repo)
    for nm in ODD_NAMES:
        with open(os.path.join(rb, nm), "wb") as f:
            f.write(b"odd v1\n")
    rev = commit_all(repo)
    listed = gb(repo, "ls-files", "-z", ":(top)").split(b"\0")
    present = [nm for nm in ODD_NAMES if nm in listed]
    out = os.path.join(work, "c-odd", "out", "honest.txt")
    w = run_writer(repo, rev, out)
    diffs, extra = truth(repo, rev)
    record("c-odd-honest", "clean-status", "ACCEPT", w, diffs, extra, status(repo), status(repo),
           f"odd_names={len(ODD_NAMES)} tracked={len(present)}")
    for i, nm in enumerate(ODD_NAMES):
        full = os.path.join(rb, nm)
        with open(full, "wb") as f:
            f.write(b"odd v2\n")
        st = os.lstat(full)
        patch_index(os.path.join(repo, ".git", "index"), nm, st)
        pre = status(repo)
        out = os.path.join(work, "c-odd", "out", f"forge{i}.txt")
        w = run_writer(repo, rev, out)
        diffs, extra = truth(repo, rev)
        record(f"c-odd-forge-{i}", "clean-status", "CAUGHT", w, diffs, extra, pre, status(repo),
               f"name={show([nm])}")
        # restore the committed bytes and the honest stat
        with open(full, "wb") as f:
            f.write(b"odd v1\n")
        st = os.lstat(full)
        patch_index(os.path.join(repo, ".git", "index"), nm, st)


def route_d(work):
    for tag, rel, forged, mac in (("d-race-tracked", "tools/counter.py", b"counter FORGED\n", 0o644),
                                  ("d-race-instrument", "instrument.sh", b"#!/bin/sh\necho FORGED\n", 0o755)):
        best = None
        for attempt in range(3):
            name = f"{tag}-try{attempt}" if attempt else tag
            case = os.path.join(work, name)
            repo = fixture(work, name)
            rev = commit_all(repo)
            forged_path = os.path.join(case, "prepared.bin")
            with open(forged_path, "wb") as f:
                f.write(forged)
            os.chmod(forged_path, mac)
            outdir = os.path.join(case, "out")
            os.makedirs(outdir)
            out = os.path.join(outdir, "receipt.txt")
            logpath = os.path.join(case, "racer.log")
            body = str(4000000 * (attempt + 1))
            code = (
                "import subprocess, sys\n"
                "a = sys.argv[1:]\n"
                "subprocess.Popen([sys.executable, '-B', a[0], *a[1:7]], stdin=subprocess.DEVNULL,\n"
                "                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,\n"
                "                 start_new_session=True, close_fds=True)\n"
                "sys.stdout.buffer.write(b'x' * int(a[7]))\n"
                "sys.stdout.buffer.flush()\n")
            argv = [sys.executable, "-c", code, RACER, repo, rel, forged_path, outdir, "receipt.txt",
                    logpath, body]
            w = run_writer(repo, rev, out, max_bytes=8000000, argv=argv)
            for _ in range(600):
                if os.path.exists(logpath):
                    break
                time.sleep(0.01)
            log = json.load(open(logpath)) if os.path.exists(logpath) else {"ok": False, "reason": "no-log"}
            diffs, extra = truth(repo, rev)
            head_ok = False
            if w["wrote"]:
                with open(out, "rb") as f:
                    head_bytes = f.read(300)
                with open(out, "rb") as f:
                    f.seek(-64, os.SEEK_END)
                    tail = f.read()
                head_ok = b"instrument_sha256=" in head_bytes and b"EXIT=0" in tail
            note = (f"attempt={attempt} body={body} racer_ok={int(bool(log.get('ok')))} "
                    f"out_before={log.get('out_before')} done_ns={log.get('done_ns')} "
                    f"receipt_mtime_ns={os.stat(out).st_mtime_ns if w['wrote'] else '-'} "
                    f"receipt_size={os.stat(out).st_size if w['wrote'] else '-'} receipt_ok={int(head_ok)}")
            best = (w, diffs, extra, note)
            if log.get("ok") and log.get("out_before") is False:
                break
        w, diffs, extra, note = best
        record(tag, "clean-status", "FORGERY", w, diffs, extra, status(repo), status(repo), note)


def route_e(work):
    repo = fixture(work, "e-hardlink-forge")
    rev = commit_all(repo)
    case = os.path.join(work, "e-hardlink-forge")
    forged = os.path.join(case, "forged.bin")
    with open(forged, "wb") as f:
        f.write(b"counter v2\n")
    target = os.path.join(repo, "tools/counter.py")
    os.unlink(target)
    os.link(forged, target)
    st = os.lstat(target)
    patch_index(os.path.join(repo, ".git", "index"), b"tools/counter.py", st)
    pre = status(repo)
    out = os.path.join(case, "out", "receipt.txt")
    w = run_writer(repo, rev, out)
    diffs, extra = truth(repo, rev)
    record("e-hardlink-forge", "clean-status", "CAUGHT", w, diffs, extra, pre, status(repo),
           f"inode_shared={os.stat(forged).st_ino == st.st_ino}")

    repo2 = fixture(work, "e-hardlink-honest")
    rev2 = commit_all(repo2)
    case2 = os.path.join(work, "e-hardlink-honest")
    alike = os.path.join(case2, "alike.bin")
    with open(alike, "wb") as f:
        f.write(b"counter v1\n")
    t2 = os.path.join(repo2, "tools/counter.py")
    os.unlink(t2)
    os.link(alike, t2)
    st2 = os.lstat(t2)
    patch_index(os.path.join(repo2, ".git", "index"), b"tools/counter.py", st2)
    pre2 = status(repo2)
    out2 = os.path.join(case2, "out", "receipt.txt")
    w2 = run_writer(repo2, rev2, out2)
    diffs2, extra2 = truth(repo2, rev2)
    record("e-hardlink-honest", "clean-status", "ACCEPT", w2, diffs2, extra2, pre2, status(repo2),
           f"bytes_equal={open(alike, 'rb').read() == b'counter v1\\n'}")


def route_f(work):
    repo = fixture(work, "f-attrs")
    with open(os.path.join(repo, ".gitattributes"), "wb") as f:
        f.write(b"tracked.txt text\n")
    with open(os.path.join(repo, "tracked.txt"), "wb") as f:
        f.write(b"clean\r\n")
    rev = commit_all(repo)
    pre = status(repo)
    out = os.path.join(work, "f-attrs", "out", "honest.txt")
    w = run_writer(repo, rev, out)
    diffs, extra = truth(repo, rev)
    raw = open(os.path.join(repo, "tracked.txt"), "rb").read()
    record("f-attrs-honest-crlf", "clean-status", "ACCEPT", w, diffs, extra, pre, status(repo),
           f"worktree_raw={raw!r} blob={blob(repo, gb(repo, 'rev-parse', rev + ':tracked.txt').strip())!r}")

    full = os.path.join(repo, "tracked.txt")
    with open(full, "wb") as f:
        f.write(b"forge\r\n")
    st = os.lstat(full)
    patch_index(os.path.join(repo, ".git", "index"), b"tracked.txt", st)
    pre = status(repo)
    out = os.path.join(work, "f-attrs", "out", "forge.txt")
    w = run_writer(repo, rev, out)
    diffs, extra = truth(repo, rev)
    record("f-attrs-forge-crlf", "clean-status", "CAUGHT", w, diffs, extra, pre, status(repo),
           "converted_bytes_differ_from_blob")


def route_g(work):
    repo = fixture(work, "g-symlinks-off", core={"core.symlinks": "false"})
    with open(os.path.join(repo, "link"), "wb") as f:
        f.write(b"tracked.txt")
    rev = commit_all(repo)
    ls = gb(repo, "ls-files", "-s", "-z", "link").decode("utf-8", "replace").replace("\0", "|")
    pre = status(repo)
    out = os.path.join(work, "g-symlinks-off", "out", "receipt.txt")
    w = run_writer(repo, rev, out)
    diffs, extra = truth(repo, rev)
    note = f"ls_files={ls} islink={os.path.islink(os.path.join(repo, 'link'))}"
    record("g-symlinks-off-honest", "clean-status", "ACCEPT", w, diffs, extra, pre, status(repo), note)


def route_h(work):
    # h1: intent-to-add under --allow-dirty (designed accept, or flag refusal)
    repo = fixture(work, "h-ita")
    rev = commit_all(repo)
    with open(os.path.join(repo, "tools/new.py"), "wb") as f:
        f.write(b"new v1\n")
    g(repo, "add", "-N", "tools/new.py")
    pre = status(repo)
    out = os.path.join(work, "h-ita", "out", "ita.txt")
    w = run_writer(repo, rev, out, extra=["--allow-dirty"])
    diffs, extra = truth(repo, rev)
    record("h-ita-accept", "allow-dirty", "ACCEPT", w, diffs, extra, pre, status(repo),
           f"ita_index={gb(repo, 'ls-files', '-s', 'tools/new.py').decode().strip()[:80]}")

    # h2: ita + in-run stat-concealed forge
    code = forge_code(repo, b"tools/new.py", b"new FORGED\n")
    pre = status(repo)
    out = os.path.join(work, "h-ita", "out", "ita-forge.txt")
    w = run_writer(repo, rev, out, extra=["--allow-dirty"], argv=[sys.executable, "-c", code])
    diffs, extra = truth(repo, rev)
    record("h-ita-forge", "allow-dirty", "CAUGHT", w, diffs, extra, pre, status(repo),
           "in-run forged bytes behind a rewritten stat on an ita entry")

    # h3: staged (X-dirty, Y-clean) path + in-run stat-concealed forge
    repo = fixture(work, "h-staged")
    rev = commit_all(repo)
    with open(os.path.join(repo, "tracked.txt"), "wb") as f:
        f.write(b"v2\n")
    g(repo, "add", "tracked.txt")
    pre = status(repo)
    code = forge_code(repo, b"tracked.txt", b"evil\n", mac=0o644)
    out = os.path.join(work, "h-staged", "out", "receipt.txt")
    w = run_writer(repo, rev, out, extra=["--allow-dirty"], argv=[sys.executable, "-c", code])
    post = status(repo)
    diffs, extra = truth(repo, rev)
    note = f"pre_eq_post={pre == post} idx_blob={gb(repo, 'ls-files', '-s', 'tracked.txt').decode().split()[1][:12]}"
    record("h-staged-forge", "allow-dirty", "FORGERY", w, diffs, extra, pre, post, note)

    # h4: same in-run write WITHOUT the stat rewrite (control: porcelain must change)
    repo = fixture(work, "h-staged-ctrl")
    rev = commit_all(repo)
    with open(os.path.join(repo, "tracked.txt"), "wb") as f:
        f.write(b"v2\n")
    g(repo, "add", "tracked.txt")
    pre = status(repo)
    code = "open(%r, 'wb').write(b'evil\\n')\n" % os.path.join(repo, "tracked.txt")
    out = os.path.join(work, "h-staged-ctrl", "out", "receipt.txt")
    w = run_writer(repo, rev, out, extra=["--allow-dirty"], argv=[sys.executable, "-c", code])
    post = status(repo)
    diffs, extra = truth(repo, rev)
    record("h-staged-ctrl", "allow-dirty", "CAUGHT", w, diffs, extra, pre, post,
           "no stat rewrite; porcelain changes")

    # h5: staged rename under --allow-dirty (designed accept of a visible dirty baseline)
    repo = fixture(work, "h-rename")
    rev = commit_all(repo)
    g(repo, "mv", "tracked.txt", "renamed.txt")
    pre = status(repo)
    out = os.path.join(work, "h-rename", "out", "receipt.txt")
    w = run_writer(repo, rev, out, extra=["--allow-dirty"])
    diffs, extra = truth(repo, rev)
    record("h-rename-accept", "allow-dirty", "ACCEPT", w, diffs, extra, pre, status(repo),
           f"status={pre.decode('utf-8','replace').strip()[:60]}")


def route_i(work):
    repo = fixture(work, "i-stale-rev")
    rev1 = commit_all(repo, "r1")
    with open(os.path.join(repo, "tools/counter.py"), "wb") as f:
        f.write(b"counter v2\n")
    rev2 = commit_all(repo, "r2")
    pre = status(repo)
    out = os.path.join(work, "i-stale-rev", "out", "receipt.txt")
    w = run_writer(repo, rev1, out)
    diffs, extra = truth(repo, rev1)
    note = f"head={rev2[:12]} rev_arg={rev1[:12]} head_eq_rev={rev2 == rev1}"
    record("i-stale-rev", "clean-status", "FORGERY", w, diffs, extra, pre, status(repo), note)


ROUTES = [("a", route_a), ("b", route_b), ("c", route_c), ("d", route_d), ("e", route_e),
          ("f", route_f), ("g", route_g), ("h", route_h), ("i", route_i)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--only", default="")
    ns = ap.parse_args()
    sys.stdout.reconfigure(errors="backslashreplace")
    work = os.path.realpath(ns.work)
    if not os.path.isdir(work):
        raise SystemExit("work dir does not exist")
    if work.startswith(os.path.realpath(LANE) + os.sep) or work.startswith(("/tmp/", "/var/tmp/")):
        raise SystemExit("work dir must be outside the lane and outside /tmp")
    data = open(WRITER_SRC, "rb").read()
    have = hashlib.sha256(data).hexdigest()
    if have != WRITER_SHA:
        raise SystemExit(f"lane writer sha256 {have} != stage-W {WRITER_SHA}")
    with open(WRITER, "wb") as f:
        f.write(data)
    gitver = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip()
    print(f"HARNESS writer={WRITER} sha256={have} work={work} git={gitver}")
    sel = [c.strip() for c in ns.only.split(",") if c.strip()]
    for key, fn in ROUTES:
        if sel and key not in sel:
            continue
        print(f"=== route {key} ===")
        fn(work)
    print("=== TABLE ===")
    for row in OUTPUT:
        print("ROW " + json.dumps(row, ensure_ascii=False, sort_keys=True))
    bad = [r for r in OUTPUT if not r["ok"]]
    print(f"SUMMARY routes={len(OUTPUT)} ok={len(OUTPUT) - len(bad)} deviations={len(bad)}")


if __name__ == "__main__":
    main()
