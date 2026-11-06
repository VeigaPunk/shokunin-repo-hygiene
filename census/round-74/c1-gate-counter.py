#!/usr/bin/env python3
"""souji r74 C1 counter (frozen at the r74 freeze; L1-built): the lane's pre-report gate clean check
against index stat-cache forgeries (r73 routed d / S73Connector HIGH; gitformat-index(5) S317,
racy-git.adoc S315, git-hash-object(1) S316).

For every row a scratch fixture is built: a bare origin and a clone whose master is pushed (so the
gate's tip check passes), a report carrying one `## SHONEN` heading and a non-empty preregistration
file outside the clone. The row's mutation is applied to the clone, then the gate under test runs as
    bash <gate> --lane <clone> --branch master --report <report> --prereg <prereg>
and its `check-clean=` line and exit code are read. A row matches when check-clean equals the row's
expectation AND the exit code is 0 for an expected PASS and 1 for an expected FAIL (every other check
passes by construction; a fixture whose other checks fail is a mismatch, never a pass).

Rows (frozen; expect = check-clean):
  GF1 refuse  same-size forge of tracked a.txt, its index entry's stat fields rewritten from the forged
              file's lstat (object id kept), index mtime moved 5 s past the entry: `git status` clean.
  GF2 refuse  tracked symlink `ln` retargeted to a same-length target, entry stat rewritten likewise.
  GF3 refuse  size-changing forge of tracked sub/b.txt, entry stat (size included) rewritten likewise.
  GD1 refuse  plain edit of a.txt (status lists it).
  GU1 refuse  an untracked file (status lists it).
  GH1 accept  the clean fixture (tracked regular files, an executable, a symlink).
  GH2 accept  honest stale stat: a.txt mtime moved +10 s, bytes unchanged.
  GH3 accept  honest core.autocrlf=true CRLF file re-staged (its converted blob is the committed one).
  GH4 accept  a tracked file whose name holds a newline and a double quote.

Output: one `ROW <id> expect=<PASS|FAIL> clean=<observed> rc=<rc> match=<yes|no>` line per row, then
`SUMMARY rows=9 mismatches=<n> errors=<n>` and `EXIT=<0 if mismatches == 0 and errors == 0 else 1>`.
Usage: c1-gate-counter.py --gate <gate.sh> --work <scratch dir> [--rows GF1,GH1,...]
Scratch: --work must not exist or be empty; it is removed on exit unless --keep."""
import argparse
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import time

ROWS = [("GF1", "FAIL"), ("GF2", "FAIL"), ("GF3", "FAIL"), ("GD1", "FAIL"), ("GU1", "FAIL"),
        ("GH1", "PASS"), ("GH2", "PASS"), ("GH3", "PASS"), ("GH4", "PASS")]
ODD = "odd\nname\"q.txt"
IDENT = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@invalid",
         "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@invalid"}


class FixtureError(Exception):
    pass


def env() -> dict:
    e = {k: v for k, v in os.environ.items()
         if not k.startswith("GIT_") and k not in ("HOME", "XDG_CONFIG_HOME")}
    e.update(IDENT)
    e.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "LC_ALL": "C"})
    return e


def git(repo: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    if not repo or not os.path.isabs(repo):
        raise FixtureError(f"refusing git -C with {repo!r}")
    p = subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=env(), timeout=120)
    if check and p.returncode != 0:
        raise FixtureError(f"git {' '.join(args)}: {p.stderr.decode('utf-8', 'replace').strip()}")
    return p


def forge_index_stat(repo: str, rel: str) -> None:
    """Rewrite rel's index entry stat fields from the worktree path's lstat (object id and flags kept),
    re-checksum the index and move its mtime 5 s past the entry (not racily clean). Index v2/v3, SHA-1."""
    st = os.lstat(os.path.join(repo, rel))
    p = os.path.join(repo, ".git", "index")
    data = open(p, "rb").read()
    if data[:4] != b"DIRC":
        raise FixtureError("bad index signature")
    ver, n = struct.unpack(">II", data[4:12])
    if ver not in (2, 3):
        raise FixtureError(f"index version {ver}")
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
        raise FixtureError(f"{rel} not in index")
    out += data[off:-20]
    out += hashlib.sha1(bytes(out)).digest()
    with open(p, "wb") as f:
        f.write(bytes(out))
    t = st.st_mtime + 5
    os.utime(p, (t, t))


def build(rowdir: str, row: str) -> tuple[str, str, str]:
    origin = os.path.join(rowdir, "origin.git")
    clone = os.path.join(rowdir, "clone")
    os.makedirs(rowdir)
    git(rowdir, "init", "-q", "--bare", "-b", "master", origin)
    git(rowdir, "init", "-q", "-b", "master", clone)
    if git(clone, "rev-parse", "--show-toplevel").stdout.strip().decode() != os.path.realpath(clone):
        raise FixtureError("fixture toplevel mismatch")
    os.makedirs(os.path.join(clone, "sub"))
    files = {"a.txt": b"alpha v1\n", "sub/b.txt": b"bravo\n", "run.sh": b"#!/bin/sh\necho hi\n",
             "tgt-one": b"one\n", "tgt-two": b"two\n", "crlf.txt": b"line one\nline two\n"}
    if row == "GH4":
        files[ODD] = b"odd\n"
    for rel, data in files.items():
        with open(os.path.join(clone, rel), "wb") as f:
            f.write(data)
    os.chmod(os.path.join(clone, "run.sh"), 0o755)
    os.symlink("tgt-one", os.path.join(clone, "ln"))
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "seed")
    git(clone, "remote", "add", "origin", origin)
    git(clone, "push", "-q", "origin", "master")
    report = os.path.join(rowdir, "report.md")
    with open(report, "w", encoding="utf-8") as f:
        f.write("# report\n\n## SHONEN\n\n- [ ] box\n")
    prereg = os.path.join(rowdir, "prereg.txt")
    with open(prereg, "w", encoding="utf-8") as f:
        f.write("frozen\n")
    # Every fixture starts with a refreshed, non-racy index.
    git(clone, "update-index", "--refresh", check=False)
    old = time.time() - 30
    for rel in list(files) + ["ln"]:
        os.utime(os.path.join(clone, rel), (old, old), follow_symlinks=False)
    git(clone, "update-index", "--really-refresh", check=False)
    return clone, report, prereg


def mutate(clone: str, row: str) -> None:
    if row == "GF1":
        with open(os.path.join(clone, "a.txt"), "wb") as f:
            f.write(b"alpha v2\n")
        forge_index_stat(clone, "a.txt")
    elif row == "GF2":
        os.unlink(os.path.join(clone, "ln"))
        os.symlink("tgt-two", os.path.join(clone, "ln"))
        forge_index_stat(clone, "ln")
    elif row == "GF3":
        with open(os.path.join(clone, "sub", "b.txt"), "wb") as f:
            f.write(b"bravo forged, longer\n")
        forge_index_stat(clone, "sub/b.txt")
    elif row == "GD1":
        with open(os.path.join(clone, "a.txt"), "ab") as f:
            f.write(b"dirty\n")
    elif row == "GU1":
        with open(os.path.join(clone, "new.txt"), "wb") as f:
            f.write(b"untracked\n")
    elif row == "GH2":
        st = os.stat(os.path.join(clone, "a.txt"))
        os.utime(os.path.join(clone, "a.txt"), (st.st_atime + 10, st.st_mtime + 10))
    elif row == "GH3":
        git(clone, "config", "core.autocrlf", "true")
        p = os.path.join(clone, "crlf.txt")
        data = open(p, "rb").read()
        with open(p, "wb") as f:
            f.write(data.replace(b"\n", b"\r\n"))
        git(clone, "add", "--", "crlf.txt")
    elif row in ("GH1", "GH4"):
        pass
    else:
        raise FixtureError(f"unknown row {row}")
    if row in ("GF1", "GF2", "GF3", "GH1", "GH2", "GH3", "GH4"):
        st = git(clone, "status", "--porcelain=v1", "--untracked-files=all").stdout
        if st:
            raise FixtureError(f"{row}: fixture status not clean: {st!r}")


def run_gate(gate: str, clone: str, report: str, prereg: str) -> tuple[int, str, str]:
    p = subprocess.run(["bash", gate, "--lane", clone, "--branch", "master", "--report", report,
                        "--prereg", prereg], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=env(), timeout=300)
    out = p.stdout.decode("utf-8", "replace")
    clean = next((l.split("=", 1)[1] for l in out.splitlines() if l.startswith("check-clean=")), "-")
    return p.returncode, clean, out + p.stderr.decode("utf-8", "replace")


def main(argv: list) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--rows")
    ap.add_argument("--keep", action="store_true")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    gate = os.path.abspath(ns.gate)
    if os.path.exists(work) and os.listdir(work):
        print(f"--work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    rows = ROWS
    if ns.rows:
        want = ns.rows.split(",")
        rows = [r for r in ROWS if r[0] in want]
        if len(rows) != len(want):
            print("unknown row in --rows", file=sys.stderr)
            return 2
    print(f"# gate={ns.gate} sha256={hashlib.sha256(open(gate, 'rb').read()).hexdigest()}")
    print(f"# counter sha256={hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest()}")
    mism = errors = 0
    try:
        for row, expect in rows:
            rowdir = os.path.join(work, row)
            try:
                clone, report, prereg = build(rowdir, row)
                mutate(clone, row)
            except (FixtureError, OSError, subprocess.SubprocessError) as exc:
                errors += 1
                print(f"ROW {row} expect={expect} clean=error rc=- match=no")
                print(f"# detail {row} fixture: {exc}")
                continue
            rc, clean, text = run_gate(gate, clone, report, prereg)
            want_rc = 0 if expect == "PASS" else 1
            ok = clean == expect and rc == want_rc
            mism += 0 if ok else 1
            print(f"ROW {row} expect={expect} clean={clean} rc={rc} match={'yes' if ok else 'no'}")
            for l in text.splitlines():
                if l.startswith(("check-", "detail-")):
                    print(f"# detail {row} {l[:300]}")
    finally:
        if not ns.keep:
            shutil.rmtree(work, ignore_errors=True)
    print(f"SUMMARY rows={len(rows)} mismatches={mism} errors={errors}")
    rc = 0 if mism == 0 and errors == 0 else 1
    print(f"EXIT={rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
