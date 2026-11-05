#!/usr/bin/env python3
"""souji-receipt-write.py — hardened atomic receipt writer (round 60, C2).

Candidate for tools/souji-receipt-write.py; replaces
census/round-57/record-receipt.sh. Keeps the base record shape
(instrument=, instrument_sha256=, rev=, combined output, EXIT=<rc>), adds
command=, and hardens the writer:

  * full-40-hex rev only (exit 2, nothing written)
  * instrument must exist at rev as a regular file (symlink refused)
  * worktree instrument bytes must equal the committed blob at rev, so an
    always-write or always-refuse stub swapped into the worktree is rejected
    even under --allow-dirty
  * refuses an existing OUT and a dirty lane tree unless --allow-dirty
  * bounded combined capture (--max-bytes, default 262144)
  * atomic write: temp file beside OUT created only after the wrapped
    command completes, fsync + os.replace + dir fsync; SIGTERM/SIGINT or
    any exception removes the temp and never leaves a partial OUT
  * exit code = the wrapped command's exit code; the receipt is still
    written with EXIT=<rc>
  * stdlib only; reads --root (read-only git plumbing), writes only OUT and
    its temp sibling; scratch honours TMPDIR and no scratch literal is
    hardcoded anywhere in this file

Usage:
  souji-receipt-write.py --root LANE --rev FULL40 --instrument RELPATH \
      --out FILE [--max-bytes N] [--allow-dirty] (--command "CMD" | -- ARGV...)
  souji-receipt-write.py --selftest --work DIR [--report FILE]
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import glob
import hashlib
import os
import posixpath
import re
import shlex
import signal
import subprocess
import tempfile
import time

MAX_BYTES_DEFAULT = 262144
READ_CHUNK = 65536
REV_RE = re.compile(r"^[0-9a-f]{40}$")

WRITER_PATH = os.path.realpath(__file__)
TEMP_MARK = "path"
_TEMP: dict[str, "str | None"] = {TEMP_MARK: None}


def git(root: str, *args: str) -> subprocess.CompletedProcess:
    """Read-only git plumbing against root; scrub GIT_DIR/GIT_WORK_TREE so -C is authoritative."""
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(["git", "-C", root, *args], capture_output=True, env=env)


def refuse(msg: str) -> None:
    """Exit 2 with a reason; every caller guarantees nothing has been written yet."""
    print(f"refused: {msg}", file=sys.stderr)
    sys.exit(2)


def _on_signal(signum: int, frame: object) -> None:
    tmp = _TEMP[TEMP_MARK]
    if tmp:
        _TEMP[TEMP_MARK] = None
        try:
            os.unlink(tmp)
        except OSError:
            pass
    sys.exit(128 + signum)


def instrument_relpath(root: str, instr: str) -> str:
    """Normalize the instrument to a root-relative POSIX path; refuse escapes."""
    p = instr
    if os.path.isabs(p):
        rp = os.path.realpath(p)
        rr = os.path.realpath(root)
        if rp != rr and not rp.startswith(rr + os.sep):
            refuse(f"instrument path is outside root ({instr})")
        p = os.path.relpath(rp, rr)
    p = posixpath.normpath(p.replace(os.sep, "/"))
    if p in ("", ".") or p.startswith("../") or p == ".." or p.startswith("/"):
        refuse(f"instrument path escapes root ({instr})")
    return p


def write_receipt(ns: argparse.Namespace) -> int:
    root = os.path.abspath(ns.root)
    out = os.path.abspath(ns.out)
    rev = ns.rev

    # behaviour 2: full-40-hex rev only
    if not REV_RE.match(rev):
        refuse(f"rev is not full 40-hex ({rev})")
    if not os.path.isdir(root):
        refuse(f"root is not a directory ({root})")
    # r60 amendment 3 (S60ReviewerRecorder i1): a tag OID peels to a commit but is not a revision
    # of record; the receipt's rev= must name the commit object itself.
    kind = git(root, "cat-file", "-t", rev)
    if kind.returncode != 0 or kind.stdout.strip() != b"commit":
        refuse(f"rev is not a commit object ({rev}: {kind.stdout.decode('utf-8', 'replace').strip() or kind.stderr.decode('utf-8', 'replace').strip()})")

    # behaviour 1: command argv from --command or after --
    if ns.command is not None and ns.args:
        refuse("--command and trailing argv are mutually exclusive")
    if ns.command is not None:
        try:
            argv = shlex.split(ns.command)
        except ValueError as exc:
            refuse(f"--command does not parse: {exc}")
        if not argv:
            refuse("--command is empty")
    elif ns.args:
        argv = list(ns.args)
    else:
        refuse("no command given (use --command or argv after --)")

    if ns.max_bytes < 0:
        refuse(f"--max-bytes must be >= 0 ({ns.max_bytes})")

    # behaviour 9: no index flag may conceal worktree divergence.  git status
    # --porcelain cannot see paths whose index entries carry skip-worktree (S)
    # or assume-unchanged (h); refuse every non-H tag unconditionally.
    flags = git(root, "ls-files", "-v", "-z")
    if flags.returncode != 0:
        detail = flags.stderr.decode("utf-8", "replace").strip()
        refuse(f"cannot read index flags of {root}: {detail}")
    concealed: "list[str]" = []
    for rec in flags.stdout.split(b"\0"):
        if not rec:
            continue
        tag = rec[0:1].decode("utf-8", "replace")
        path_bytes = rec[2:] if len(rec) > 1 and rec[1:2] == b" " else rec[1:]
        if tag != "H":
            concealed.append(f"{path_bytes.decode('utf-8', 'replace')} [{tag}]")
    if concealed:
        refuse("RECEIPT-INDEX-FLAG-CONCEALED: " + "; ".join(concealed[:8])
               + (" ..."
                  if len(concealed) > 8 else ""))

    # behaviour 7: clean lane tree unless --allow-dirty
    st = git(root, "status", "--porcelain")
    if st.returncode != 0:
        detail = st.stderr.decode("utf-8", "replace").strip()
        refuse(f"cannot read worktree status of {root}: {detail}")
    if st.stdout and not ns.allow_dirty:
        refuse("lane worktree is dirty (git status --porcelain non-empty); pass --allow-dirty to override")

    # behaviour 3: instrument present and regular at rev
    rel = instrument_relpath(root, ns.instrument)
    lt = git(root, "ls-tree", "-r", "-z", rev, "--", rel)
    if lt.returncode != 0:
        detail = lt.stderr.decode("utf-8", "replace").strip()
        refuse(f"cannot read tree {rev}: {detail}")
    entry: "list[str] | None" = None
    for rec in lt.stdout.split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        if path.decode("utf-8", "replace") == rel:
            entry = meta.decode("utf-8", "replace").split()
            break
    if entry is None:
        refuse(f"{rel} absent at {rev}")
    if entry[0] == "120000":
        refuse(f"{rel} is a symlink at {rev}")
    if entry[0] not in ("100644", "100755"):
        refuse(f"{rel} has unexpected mode {entry[0]} at {rev}")

    blob = git(root, "cat-file", "blob", f"{rev}:{rel}")
    if blob.returncode != 0:
        refuse(f"{rel} absent at {rev}")
    digest = hashlib.sha256(blob.stdout).hexdigest()

    # stub rejection: the worktree instrument must be the committed bytes
    wt = os.path.join(root, *rel.split("/"))
    if os.path.islink(wt):
        refuse(f"{rel} is a symlink in the worktree")
    try:
        with open(wt, "rb") as f:
            wt_bytes = f.read()
    except OSError as exc:
        refuse(f"cannot read worktree instrument {rel}: {exc}")
    if wt_bytes != blob.stdout:
        refuse(f"worktree {rel} differs from committed bytes at {rev}")

    # behaviour 4: OUT must not exist; refuse before any side effect
    if os.path.lexists(out):
        refuse(f"out already exists ({out})")
    outdir = os.path.dirname(out) or "."
    if not os.path.isdir(outdir):
        refuse(f"out directory does not exist ({outdir})")
    # r60 amendment 3 (S60ReviewerRecorder b1): a symlinked out directory must not aim the receipt
    # outside the lane root. The check is on the resolved directory, so a symlink inside the root
    # that resolves inside the root still writes.
    real_outdir = os.path.realpath(outdir)
    real_root = os.path.realpath(root)
    if (real_outdir != real_root and not real_outdir.startswith(real_root + os.sep)
            and not getattr(ns, "allow_outside", False)):
        refuse(f"out directory {real_outdir} is outside the lane root {real_root}")

    # behaviours 6+8: bounded combined capture, exit-code passthrough
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    chunks: list[bytes] = []
    total = 0
    overflow = False
    try:
        while True:
            chunk = proc.stdout.read(READ_CHUNK)
            if not chunk:
                break
            total += len(chunk)
            chunks.append(chunk)
            if total > ns.max_bytes:
                overflow = True
                proc.kill()
                break
    except BaseException:
        proc.kill()
        try:
            proc.wait(timeout=10)
        except Exception:
            pass
        raise
    finally:
        if proc.stdout:
            proc.stdout.close()
    proc.wait()
    if overflow:
        refuse(f"captured output exceeds --max-bytes ({ns.max_bytes} bytes)")
    rc = proc.returncode
    if rc < 0:
        rc = 128 - rc
    body = b"".join(chunks).rstrip(b"\n") + b"\n"

    receipt = b"".join([
        f"instrument={rel}\n".encode("utf-8"),
        f"instrument_sha256={digest}\n".encode("utf-8"),
        f"rev={rev}\n".encode("utf-8"),
        ("command=" + shlex.join(argv) + "\n").encode("utf-8"),
        body,
        f"EXIT={rc}\n".encode("utf-8"),
    ])

    # behaviour 5: atomic write; the temp file exists only from here on
    # r60 amendment 3 (S60ReviewerRecorder c-c1): SIGKILL cannot be trapped, so a killed run can
    # leave `<out>.<rand>.tmp`. Only this writer creates that pattern for this OUT and a temp is
    # never a receipt, so the next write of the same OUT sweeps it first.
    for stale in glob.glob(os.path.join(glob.escape(outdir), glob.escape(os.path.basename(out)) + ".*.tmp")):
        try:
            os.unlink(stale)
        except OSError:
            pass
    try:
        fd, tmp = tempfile.mkstemp(prefix=os.path.basename(out) + ".", suffix=".tmp", dir=outdir)
        _TEMP[TEMP_MARK] = tmp
        with os.fdopen(fd, "wb") as f:
            f.write(receipt)
            f.flush()
            os.fsync(f.fileno())
        # r60 amendment 3 (S60ReviewerRecorder a1/a2): `os.replace` after an existence check is a
        # TOCTOU that clobbers a file another process created during the run. `os.link` publishes
        # atomically and fails with EEXIST, so the loser of a race never destroys the winner's bytes.
        try:
            os.link(tmp, out)
        except FileExistsError:
            refuse(f"out appeared while the command ran ({out})")
        _TEMP[TEMP_MARK] = None
        try:
            os.unlink(tmp)
        except OSError:
            pass
    finally:
        leftover = _TEMP[TEMP_MARK]
        if leftover:
            _TEMP[TEMP_MARK] = None
            try:
                os.unlink(leftover)
            except OSError:
                pass
    try:
        dfd = os.open(outdir, os.O_RDONLY)
    except OSError:
        dfd = None
    if dfd is not None:
        try:
            os.fsync(dfd)
        except OSError:
            pass
        finally:
            os.close(dfd)

    print(f"RECORD {out} rev={rev} instrument={rel} rc={rc}")
    return rc


# ---------------------------------------------------------------- self-test

INSTRUMENT_BYTES = b"#!/bin/sh\necho instrument-selftest-ok\n"
GIT_ID = ("-c", "user.email=s60execrecorder@example.invalid", "-c", "user.name=S60ExecRecorder")


def _fixture(work: str, name: str) -> str:
    d = tempfile.mkdtemp(prefix=name + ".", dir=work)
    r = subprocess.run(["git", "-C", d, "init", "-q"], capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"git init failed: {r.stderr.strip()}")
    top = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0 or os.path.realpath(top.stdout.strip()) != os.path.realpath(d):
        raise AssertionError(f"fixture toplevel mismatch: got {top.stdout.strip()!r}")
    with open(os.path.join(d, "instrument.sh"), "wb") as f:
        f.write(INSTRUMENT_BYTES)
    os.chmod(os.path.join(d, "instrument.sh"), 0o755)
    with open(os.path.join(d, "tracked.txt"), "wb") as f:
        f.write(b"clean\n")
    _commit_all(d, "fixture seed")
    return d


def _commit_all(d: str, msg: str) -> None:
    r = subprocess.run(["git", "-C", d, "add", "-A"], capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"fixture add failed: {r.stderr.strip()}")
    r = subprocess.run(["git", "-C", d, *GIT_ID, "commit", "-q", "-m", msg], capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"fixture commit failed: {r.stderr.strip()}")


def _head(d: str) -> str:
    r = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(r.stderr.strip())
    return r.stdout.strip()


def _run(args: "list[str]", env: "dict[str, str] | None" = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, WRITER_PATH, *args], capture_output=True, text=True, timeout=300, env=env)


def _outdir(work: str) -> str:
    return tempfile.mkdtemp(prefix="out.", dir=work)


def _base_args(d: str, rev: str, out: str) -> "list[str]":
    # r60 amendment 3: the selftest's OUT lives in scratch, outside the fixture repo, which is
    # exactly the case --allow-outside exists for.
    return ["--root", d, "--rev", rev, "--instrument", "instrument.sh", "--out", out,
            "--allow-outside"]


def _no_stray(outdir: str) -> None:
    stray = [n for n in os.listdir(outdir) if ".tmp" in n or ".partial" in n]
    if stray:
        raise AssertionError(f"stray temp files: {stray}")


def case_01_arg_forms(work: str) -> None:
    d = _fixture(work, "c01")
    rev = _head(d)
    outdir = _outdir(work)
    out1 = os.path.join(outdir, "flag.txt")
    out2 = os.path.join(outdir, "argv.txt")
    out3 = os.path.join(outdir, "both.txt")
    r1 = _run([*_base_args(d, rev, out1), "--command", "/bin/echo hello-form"])
    if r1.returncode != 0:
        raise AssertionError(f"flag form rc={r1.returncode}: {r1.stderr.strip()}")
    r2 = _run([*_base_args(d, rev, out2), "--", "/bin/echo", "hello-form"])
    if r2.returncode != 0:
        raise AssertionError(f"argv form rc={r2.returncode}: {r2.stderr.strip()}")
    t1 = open(out1, encoding="utf-8").read()
    t2 = open(out2, encoding="utf-8").read()
    lines = t1.splitlines()
    if lines[0] != "instrument=instrument.sh":
        raise AssertionError(lines[0])
    if not re.match(r"^instrument_sha256=[0-9a-f]{64}$", lines[1]):
        raise AssertionError(lines[1])
    if lines[2] != f"rev={rev}":
        raise AssertionError(lines[2])
    if lines[3] != "command=/bin/echo hello-form":
        raise AssertionError(lines[3])
    if lines[4:] != ["hello-form", "EXIT=0"]:
        raise AssertionError(lines[4:])
    if t1 != t2:
        raise AssertionError("flag and argv forms produced different receipts")
    r3 = _run([*_base_args(d, rev, out3), "--command", "/bin/echo x", "--", "/bin/echo", "y"])
    if r3.returncode != 2:
        raise AssertionError(f"both-forms rc={r3.returncode}")
    if os.path.exists(out3):
        raise AssertionError("both-forms run wrote OUT")
    _no_stray(outdir)


def case_02_rev_format(work: str) -> None:
    d = _fixture(work, "c02")
    rev = _head(d)
    outdir = _outdir(work)
    for i, bad in enumerate(["abc1234", "HEAD", "main", rev.upper()]):
        out = os.path.join(outdir, f"bad{i}.txt")
        r = _run([*_base_args(d, bad, out), "--command", "/bin/echo hi"])
        if r.returncode != 2:
            raise AssertionError(f"rev {bad!r} rc={r.returncode}: {r.stderr.strip()}")
        if os.path.exists(out):
            raise AssertionError(f"rev {bad!r} wrote OUT")
    _no_stray(outdir)
    out = os.path.join(outdir, "good.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"])
    if r.returncode != 0:
        raise AssertionError(f"control rc={r.returncode}: {r.stderr.strip()}")


def case_03_instrument_at_rev(work: str) -> None:
    d = _fixture(work, "c03")
    rev = _head(d)
    outdir = _outdir(work)
    out = os.path.join(outdir, "absent.txt")
    r = _run(["--root", d, "--rev", rev, "--instrument", "no-such.sh", "--out", out, "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"absent rc={r.returncode}: {r.stderr.strip()}")
    os.remove(os.path.join(d, "instrument.sh"))
    with open(os.path.join(d, "target.sh"), "wb") as f:
        f.write(INSTRUMENT_BYTES)
    os.symlink("target.sh", os.path.join(d, "instrument.sh"))
    _commit_all(d, "instrument becomes a symlink")
    sym_rev = _head(d)
    out2 = os.path.join(outdir, "symlink.txt")
    r = _run([*_base_args(d, sym_rev, out2), "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"symlink rc={r.returncode}: {r.stderr.strip()}")
    os.remove(os.path.join(d, "instrument.sh"))
    with open(os.path.join(d, "instrument.sh"), "wb") as f:
        f.write(INSTRUMENT_BYTES)
    os.chmod(os.path.join(d, "instrument.sh"), 0o755)
    _commit_all(d, "instrument restored")
    rev3 = _head(d)
    out3 = os.path.join(outdir, "control.txt")
    r = _run([*_base_args(d, rev3, out3), "--command", "/bin/echo hi"])
    if r.returncode != 0:
        raise AssertionError(f"control rc={r.returncode}: {r.stderr.strip()}")
    _no_stray(outdir)


def case_04_overwrite(work: str) -> None:
    d = _fixture(work, "c04")
    rev = _head(d)
    outdir = _outdir(work)
    out = os.path.join(outdir, "receipt.txt")
    with open(out, "wb") as f:
        f.write(b"SENTINEL-BYTES\n")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo clobber"])
    if r.returncode != 2:
        raise AssertionError(f"rc={r.returncode}: {r.stderr.strip()}")
    if open(out, "rb").read() != b"SENTINEL-BYTES\n":
        raise AssertionError("existing OUT was modified")
    _no_stray(outdir)


def case_05_atomic_signal(work: str) -> None:
    d = _fixture(work, "c05")
    rev = _head(d)
    outdir = _outdir(work)
    for sig, want in ((signal.SIGTERM, 143), (signal.SIGINT, 130)):
        out = os.path.join(outdir, f"sig{sig}.txt")
        proc = subprocess.Popen(
            [sys.executable, WRITER_PATH, *_base_args(d, rev, out), "--command", "sleep 8"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(1.0)
        proc.send_signal(sig)
        rc = proc.wait(timeout=60)
        if rc != want:
            raise AssertionError(f"signal {sig}: rc={rc}, want {want}")
        if os.path.exists(out):
            raise AssertionError(f"signal {sig}: OUT exists")
        if os.listdir(outdir):
            raise AssertionError(f"signal {sig}: outdir not empty: {os.listdir(outdir)}")


def case_06_max_bytes(work: str) -> None:
    d = _fixture(work, "c06")
    rev = _head(d)
    outdir = _outdir(work)
    out = os.path.join(outdir, "over.txt")
    r = _run([*_base_args(d, rev, out), "--max-bytes", "100", "--command", "python3 -c \"print('X' * 1000)\""])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"over-cap rc={r.returncode}: {r.stderr.strip()}")
    out2 = os.path.join(outdir, "default.txt")
    r = _run([*_base_args(d, rev, out2), "--command", "python3 -c \"print('X' * 300000)\""])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"default-cap rc={r.returncode}: {r.stderr.strip()}")
    out3 = os.path.join(outdir, "exact.txt")
    r = _run([*_base_args(d, rev, out3), "--max-bytes", "100", "--command", "python3 -c \"print('X' * 99)\""])
    if r.returncode != 0:
        raise AssertionError(f"exact-cap rc={r.returncode}: {r.stderr.strip()}")
    t = open(out3, encoding="utf-8").read().splitlines()
    if t[-2] != "X" * 99 or t[-1] != "EXIT=0":
        raise AssertionError(t[-2:])
    _no_stray(outdir)


def case_07_dirty_tree(work: str) -> None:
    d = _fixture(work, "c07")
    rev = _head(d)
    outdir = _outdir(work)
    with open(os.path.join(d, "tracked.txt"), "ab") as f:
        f.write(b"dirty\n")
    out = os.path.join(outdir, "mod.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"modified rc={r.returncode}: {r.stderr.strip()}")
    if "dirty" not in r.stderr:
        raise AssertionError(f"unexpected refusal reason: {r.stderr.strip()}")
    with open(os.path.join(d, "tracked.txt"), "wb") as f:
        f.write(b"clean\n")
    with open(os.path.join(d, "untracked.txt"), "wb") as f:
        f.write(b"u\n")
    out2 = os.path.join(outdir, "untracked.txt")
    r = _run([*_base_args(d, rev, out2), "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"untracked rc={r.returncode}: {r.stderr.strip()}")
    out3 = os.path.join(outdir, "allowed.txt")
    r = _run([*_base_args(d, rev, out3), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 0 or not os.path.exists(out3):
        raise AssertionError(f"allow-dirty rc={r.returncode}: {r.stderr.strip()}")
    _no_stray(outdir)


def case_08_exit_code(work: str) -> None:
    d = _fixture(work, "c08")
    rev = _head(d)
    outdir = _outdir(work)
    out = os.path.join(outdir, "fail.txt")
    r = _run([*_base_args(d, rev, out), "--command", "sh -c 'exit 7'"])
    if r.returncode != 7:
        raise AssertionError(f"rc={r.returncode}, want 7")
    if open(out, encoding="utf-8").read().splitlines()[-1] != "EXIT=7":
        raise AssertionError("EXIT=7 line missing")
    out2 = os.path.join(outdir, "ok.txt")
    r = _run([*_base_args(d, rev, out2), "--command", "sh -c 'exit 0'"])
    if r.returncode != 0:
        raise AssertionError(f"rc={r.returncode}")
    if open(out2, encoding="utf-8").read().splitlines()[-1] != "EXIT=0":
        raise AssertionError("EXIT=0 line missing")
    _no_stray(outdir)


def case_09_no_scratch_literal(work: str) -> None:
    d = _fixture(work, "c09")
    rev = _head(d)
    outdir = _outdir(work)
    probe = tempfile.mkdtemp(prefix="probe.", dir=work)
    env = dict(os.environ)
    env["TMPDIR"] = probe
    out = os.path.join(outdir, "r.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo probe"], env=env)
    if r.returncode != 0:
        raise AssertionError(f"rc={r.returncode}: {r.stderr.strip()}")
    if os.listdir(probe):
        raise AssertionError(f"scratch dir was used: {os.listdir(probe)}")
    if not os.path.exists(out):
        raise AssertionError("OUT missing")
    with open(WRITER_PATH, "rb") as f:
        src = f.read()
    needle = b"/" + b"tmp"
    if needle in src:
        raise AssertionError("writer source hardcodes the scratch literal")


def case_10_readonly_root(work: str) -> None:
    d = _fixture(work, "c10")
    rev = _head(d)
    outdir = _outdir(work)

    def snap() -> "list[str]":
        paths = []
        for base, dirs, files in os.walk(d):
            dirs[:] = sorted(x for x in dirs if x != ".git")
            for n in files:
                paths.append(os.path.relpath(os.path.join(base, n), d))
        return sorted(paths)

    before = snap()
    st0 = subprocess.run(["git", "-C", d, "status", "--porcelain"], capture_output=True, text=True).stdout
    if st0:
        raise AssertionError(f"fixture dirty before run: {st0}")
    out = os.path.join(outdir, "r.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo ro"])
    if r.returncode != 0:
        raise AssertionError(f"rc={r.returncode}: {r.stderr.strip()}")
    if snap() != before:
        raise AssertionError("root file set changed")
    st1 = subprocess.run(["git", "-C", d, "status", "--porcelain"], capture_output=True, text=True).stdout
    if st1:
        raise AssertionError(f"root became dirty: {st1}")


def case_11_always_write_stub(work: str) -> None:
    d = _fixture(work, "c11")
    rev = _head(d)
    outdir = _outdir(work)
    with open(os.path.join(d, "instrument.sh"), "wb") as f:
        f.write(b"#!/bin/sh\necho FORGED-PASS\n")
    out = os.path.join(outdir, "r.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"rc={r.returncode}: {r.stderr.strip()}")
    if "differs" not in r.stderr:
        raise AssertionError(f"wrong refusal reason: {r.stderr.strip()}")
    _no_stray(outdir)


def case_12_always_refuse_stub(work: str) -> None:
    d = _fixture(work, "c12")
    rev = _head(d)
    outdir = _outdir(work)
    with open(os.path.join(d, "instrument.sh"), "wb") as f:
        f.write(b"#!/bin/sh\nexit 2\n")
    out = os.path.join(outdir, "r.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"rc={r.returncode}: {r.stderr.strip()}")
    if "differs" not in r.stderr:
        raise AssertionError(f"wrong refusal reason: {r.stderr.strip()}")
    _no_stray(outdir)


CASES = (
    ("arg-forms: --command and post--- argv both accepted, identical receipts; both at once refused", case_01_arg_forms),
    ("rev-format: short/branch/uppercase rev refused with nothing written", case_02_rev_format),
    ("instrument-at-rev: absent refused, symlink-at-rev refused, regular passes", case_03_instrument_at_rev),
    ("overwrite: existing OUT byte-identical, no temp file", case_04_overwrite),
    ("atomic-signal: SIGTERM/SIGINT during the command leave no OUT and no temp", case_05_atomic_signal),
    ("max-bytes: over-cap refused (flag and default), exact cap passes", case_06_max_bytes),
    ("dirty-tree: modified and untracked refused, --allow-dirty overrides", case_07_dirty_tree),
    ("exit-code: wrapped rc passed through, receipt written with EXIT=<rc>", case_08_exit_code),
    ("no-scratch-literal: temp beside OUT only, TMPDIR untouched, source clean", case_09_no_scratch_literal),
    ("readonly-root: fixture file set and porcelain unchanged by a run", case_10_readonly_root),
    ("always-write stub rejected: worktree instrument swapped for a forger", case_11_always_write_stub),
    ("always-refuse stub rejected: worktree instrument swapped for a refuser", case_12_always_refuse_stub),
)


def cmd_selftest(ns: argparse.Namespace) -> int:
    if not ns.work:
        print("refused: --selftest requires --work DIR", file=sys.stderr)
        return 2
    work = os.path.abspath(ns.work)
    os.makedirs(work, exist_ok=True)
    results: "list[tuple[str, bool, str]]" = []
    for name, fn in CASES:
        try:
            fn(work)
            results.append((name, True, ""))
        except Exception as exc:
            results.append((name, False, f"{type(exc).__name__}: {exc}"))
    lines = []
    for name, ok, detail in results:
        lines.append(f"case {'ok' if ok else 'FAIL'}: {name}" + (f" | {detail}" if detail else ""))
    npass = sum(1 for _, ok, _ in results if ok)
    nfail = len(results) - npass
    lines.append(f"SELFTEST cases={len(results)} pass={npass} fail={nfail}")
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    sys.stdout.flush()
    if ns.report:
        with open(os.path.abspath(ns.report), "w", encoding="utf-8") as f:
            f.write(text)
    return 0 if nfail == 0 else 1


def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(
        prog="souji-receipt-write.py",
        description="hardened atomic receipt writer (round 60, C2)",
    )
    ap.add_argument("--root", help="lane root (read-only)")
    ap.add_argument("--allow-outside", action="store_true",
                    help="permit an --out whose resolved directory is outside --root")
    ap.add_argument("--rev", help="full 40-hex revision the receipt binds")
    ap.add_argument("--instrument", help="instrument path relative to --root")
    ap.add_argument("--out", help="receipt file to create (must not exist)")
    ap.add_argument("--command", help="wrapped command as a single shell-parsed string")
    ap.add_argument("--max-bytes", type=int, default=MAX_BYTES_DEFAULT,
                    help="refuse when captured output exceeds N bytes (default 262144)")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="permit a dirty lane worktree (instrument byte-binding still enforced)")
    ap.add_argument("--selftest", action="store_true", help="run the built-in self-test suite")
    ap.add_argument("--work", help="self-test work directory")
    ap.add_argument("--report", help="self-test: also write the report to this file")
    ap.add_argument("args", nargs="*", help="wrapped command argv (after --)")
    ns = ap.parse_args(argv)

    if ns.selftest:
        return cmd_selftest(ns)

    for flag in ("root", "rev", "instrument", "out"):
        if getattr(ns, flag) is None:
            print(f"refused: --{flag.replace('_', '-')} is required", file=sys.stderr)
            return 2
    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)
    return write_receipt(ns)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
