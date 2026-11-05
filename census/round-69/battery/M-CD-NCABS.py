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

round 62 (C1): refuses any index entry whose
`git ls-files -v` tag is not H, before the dirty check.

round 63 (C1): every git call the writer makes runs with core.fsmonitor=false, and the index
flags (git ls-files -v -z) and the worktree status (git status --porcelain) are re-read after the
wrapped command and before any receipt byte is composed; a difference refuses with
RECEIPT-STATE-CHANGED-DURING-RUN, --allow-dirty included. round 63 (C2): a flagged index record is
classed unmerged, gitlink or absent before the generic RECEIPT-INDEX-FLAG-CONCEALED refusal.

round 64 (C1): GIT_INDEX_FILE in the writer's environment refuses before any git call; the real
repository toplevel is resolved and every git ls-files runs from it with a :(top) pathspec, so a
--root inside a subdirectory observes the whole index; and under --allow-dirty a content-bearing
snapshot (sha256 per worktree-modified tracked file, every file under untracked directories) is
re-compared after the wrapped command, so an in-run change that leaves both porcelain reads
byte-identical still refuses (RECEIPT-STATE-CHANGED-DURING-RUN with content rows).

round 65 (C1): every status read overrides the status.showUntrackedFiles config KEY to `all`, so that key
cannot hide untracked entries from the dirty check or the content snapshot. This is key-scoped: routes that make
a path IGNORED rather than untracked (core.excludesFile, .git/info/exclude, a tracked .gitignore) and
GIT_CONFIG_* passthrough is closed by the round-66 env gate (see below); the snapshot payload
records each regular file's mode beside its digest, so a mode-only in-run flip refuses (RECEIPT-STATE-CHANGED-DURING-RUN
with a `mode <path>` row); and the M5 symlink rule is frozen design: a symlink inside an untracked
directory is recorded by name and target string, never followed.

round 66 (C1): caller-injected config and object-redirect env routes are refused before any git call. GIT_CONFIG_COUNT,
GIT_CONFIG_PARAMETERS, and any GIT_CONFIG_KEY_* / GIT_CONFIG_VALUE_* name refuse with RECEIPT-ENV-CONFIG-SET;
GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, and GIT_REPLACE_REF_BASE refuse with RECEIPT-ENV-REDIRECT-SET.
Both are presence checks and print names only. Every git call pins GIT_CONFIG_GLOBAL and core.excludesFile to the null
device, sets GIT_CONFIG_NOSYSTEM=1 and GIT_NO_REPLACE_OBJECTS=1, and keeps GIT_OPTIONAL_LOCKS=0. The snapshot mode byte
carries the full permission bits (setuid, setgid and sticky included). Ignore routes (.git/info/exclude, a tracked
.gitignore, a repository-local core.excludesFile) remain named limits outside C1.

round 67 (C1): a caller-injected GIT_COMMON_DIR is value-checked. When the variable is set at all (an empty value
included), the writer resolves the repository's own common dir (git rev-parse --git-common-dir, with GIT_COMMON_DIR
scrubbed), canonicalizes both sides with os.path.realpath (a relative caller value resolves against the writer's cwd),
and refuses RECEIPT-ENV-COMMONDIR-MISMATCH on a mismatch, an empty value or an unresolvable repository, before any git
call reads the caller's value; only the variable name is printed. An equal value proceeds. Every git call scrubs
GIT_COMMON_DIR together with GIT_DIR and GIT_WORK_TREE.
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
import shutil
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
    """Read-only git plumbing against root; scrub GIT_DIR/GIT_WORK_TREE/GIT_COMMON_DIR so -C is authoritative."""
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    # r66 C1: no host config file, system config or replace ref reaches a read; the excludes file is the null device.
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return subprocess.run(["git", "-C", root, "-c", "core.fsmonitor=false",
                           "-c", f"core.excludesFile={os.devnull}", *args], capture_output=True, env=env)


def refuse(msg: str) -> None:
    """Exit 2 with a reason; every caller guarantees nothing has been written yet."""
    print(f"refused: {msg}", file=sys.stderr)
    sys.exit(2)


def _index_stages(top: str) -> "dict[bytes, list[tuple[bytes, int]]]":
    """Index records keyed by raw path bytes: (mode, stage) per record. Read only on a refusal path.
    r64 C1 (scope): read from the repository toplevel with a :(top) pathspec, so the whole index is
    observed even when --root sits inside a subdirectory."""
    r = git(top, "ls-files", "-s", "-z", ":(top)")
    if r.returncode != 0:
        refuse(f"cannot read index entries of {top}: {r.stderr.decode('utf-8', 'replace').strip()}")
    table: "dict[bytes, list[tuple[bytes, int]]]" = {}
    for rec in r.stdout.split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        mode, _, rest = meta.partition(b" ")
        table.setdefault(path, []).append((mode, int(rest.rpartition(b" ")[2])))
    return table


def _flag_refusal(top: str, tag: bytes, path: bytes) -> str:
    """r63 C2: the refusal text for a non-H index record. The S/h, worktree-present case keeps the r62 text."""
    p = path.decode("utf-8", "replace")
    t = tag.decode("utf-8", "replace")
    entries = _index_stages(top).get(path, [])
    stages = sorted({stage for _, stage in entries})
    if any(stage != 0 for stage in stages):
        return (f"RECEIPT-INDEX-UNMERGED: {p} is unmerged (index stages {' '.join(str(s) for s in stages)}) "
                f"and carries index flag {t}; a conflicted path is not a clean tree; "
                f"resolve it with git add or git rm, then retry")
    if any(mode == b"160000" for mode, _ in entries):
        return (f"RECEIPT-GITLINK-CONCEALED: {p} is a gitlink (mode 160000) carrying index flag {t}; "
                f"the writer does not read submodule state and skip-worktree or assume-unchanged hides it from git status; "
                f"clear it with git update-index --no-skip-worktree or --no-assume-unchanged, then retry")
    if not os.path.lexists(os.path.join(os.fsencode(top), path)):
        return (f"RECEIPT-INDEX-CONCEALED-ABSENT: {p} carries index flag {t} and is absent from the worktree; "
                f"skip-worktree or assume-unchanged hides the deletion from git status; "
                f"restore the file or clear the flag with git update-index --no-skip-worktree or --no-assume-unchanged, then retry")
    return (f"RECEIPT-INDEX-FLAG-CONCEALED: {p} carries index flag {t}; skip-worktree or assume-unchanged hides worktree divergence "
            f"from git status; clear it with git update-index --no-skip-worktree or --no-assume-unchanged, then retry")


def _status_z(root: str) -> subprocess.CompletedProcess:
    """r64 C1: machine-readable porcelain (NUL-separated, unquoted paths) for the content snapshot.
    r65 C1: status.showUntrackedFiles is overridden to `all` on every status read, so an
    operator-injected config cannot hide untracked entries from the dirty check or the snapshot."""
    return git(root, "-c", "status.showUntrackedFiles=all", "status", "--porcelain", "-z")


def _snapshot_entry(full: bytes) -> bytes:
    """Digest payload for one snapshotted path. Regular files record `<mode>:<sha256 hex>` — the
    full permission bits (setuid, setgid and sticky included) are part of the fingerprint (r65 C1: a mode-only in-run flip is invisible to both
    porcelain reads and to a content-only digest); symlinks record their target bytes (record name
    and target, never follow, r65-frozen M5 rule); anything else records a marker. Races degrade to
    markers, so a pre/post mismatch still refuses."""
    if os.path.islink(full):
        try:
            return b"symlink:" + os.readlink(full)
        except OSError:
            return b"symlink-unreadable"
    if not os.path.isfile(full):
        return b"nonregular"
    try:
        h = hashlib.sha256()
        with open(full, "rb") as f:
            while True:
                chunk = f.read(READ_CHUNK)
                if not chunk:
                    break
                h.update(chunk)
        try:
            mode = oct(os.stat(full).st_mode & 0o7777).encode("ascii") + b":"
        except OSError:
            mode = b"mode-unreadable:"
        return mode + h.hexdigest().encode("ascii")
    except OSError:
        return b"unreadable"


def _delta_label(pre: "bytes | None", post: "bytes | None") -> str:
    """r65 C1: classify a snapshot payload mismatch for the refusal message. `mode` when only the
    recorded mode changed (content digest identical); `content` for every other difference."""
    if pre is None or post is None:
        return "content"
    if pre.startswith(b"mode-unreadable:") or post.startswith(b"mode-unreadable:"):
        return "mode"
    try:
        pm, _, ps = pre.rpartition(b":")
        qm, _, qs = post.rpartition(b":")
        if (ps == qs and len(ps) == 64 and pm.startswith(b"0o") and qm.startswith(b"0o")
                and pm != qm):
            return "mode"
    except Exception:
        pass
    return "content"


def _snapshot_walk(dir_path: bytes, rel_prefix: bytes, table: "dict[bytes, bytes]") -> None:
    """Walk an untracked directory into table: iterative (no recursion limit), symlinks to
    directories are not followed (no cycles), a nested .git directory is skipped so the live
    metadata of an embedded repository cannot churn the fingerprint, and every key stays
    toplevel-relative (rel_prefix carries the porcelain's own trailing slash)."""
    stack = [(dir_path, rel_prefix)]
    while stack:
        cur, prefix = stack.pop()
        try:
            with os.scandir(cur) as it:
                entries = list(it)
        except OSError:
            table[prefix] = b"dir-unlistable"
            continue
        for e in entries:
            name = os.fsencode(e.name)
            if name == b".git":
                continue
            full = os.path.join(cur, name)
            rel = prefix + name
            if e.is_dir(follow_symlinks=False):
                stack.append((full, rel + b"/"))
            else:
                table[rel] = _snapshot_entry(full)


def _content_snapshot(top: str, status_z: bytes) -> "dict[bytes, bytes]":
    """r64 C1 (content): fingerprint of the caller-accepted dirty state, keyed by toplevel-relative
    path. Worktree-modified tracked entries (Y in M/T/U) hash their bytes; untracked entries hash
    every file below them. Deleted worktree entries (Y=D) are omitted: their presence flips are
    visible to the porcelain byte compare itself."""
    table: "dict[bytes, bytes]" = {}
    topb = os.fsencode(top)
    records = status_z.split(b"\0")
    i = 0
    while i < len(records):
        rec = records[i]
        i += 1
        if not rec:
            continue
        xy = rec[:2]  # porcelain: exactly two status bytes, one space, then the path
        path = rec[3:]
        if xy[:1] in (b"R", b"C") and i < len(records):
            i += 1  # -z porcelain: a rename/copy's orig path follows as its own record
        if xy == b"??":
            full = os.path.join(topb, path)
            if path.endswith(b"/"):
                _snapshot_walk(full, path, table)
            else:
                table[path] = _snapshot_entry(full)
        elif xy[1:2] in (b"M", b"T", b"U"):
            table[path] = _snapshot_entry(os.path.join(topb, path))
    return table


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


def _check_env_commondir(root: str) -> None:
    """r67 C1 (env): a caller-injected GIT_COMMON_DIR must name this repository's own common dir, or refuse.

    Presence is the test (an empty value refuses). The resolution call runs through git(), which scrubs the variable,
    so no writer git call reads the caller's value. Both sides are canonicalized with os.path.realpath; a relative
    caller value resolves against the writer's cwd. Only the variable name is printed.
    """
    if "GIT_COMMON_DIR" not in os.environ:
        return
    value = os.environ["GIT_COMMON_DIR"]
    mismatch = ("RECEIPT-ENV-COMMONDIR-MISMATCH: GIT_COMMON_DIR is set in the writer's environment and does not "
                "resolve to this repository's common dir (value not shown); unset it and retry")
    if value == "":
        refuse(mismatch)
    r = git(root, "rev-parse", "--git-common-dir")
    if r.returncode != 0:
        refuse(mismatch)
    common = os.path.abspath(os.path.join(root, os.fsdecode(r.stdout).rstrip("\n")))
    if os.path.abspath(value) != common:
        refuse(mismatch)


def write_receipt(ns: argparse.Namespace) -> int:
    root = os.path.abspath(ns.root)
    out = os.path.abspath(ns.out)
    rev = ns.rev

    # r66 C1 (env): caller-injected config and object-redirect env routes refuse before any git call.
    # Presence is the test (an empty value still refuses); only the variable NAMES are printed.
    cfg_env = sorted(k for k in os.environ if k in ("GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS")
                     or k.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")))
    if cfg_env:
        refuse(f"RECEIPT-ENV-CONFIG-SET: {', '.join(cfg_env)} set in the writer's environment; "
               "unset them and retry")
    redirect_env = sorted(k for k in os.environ
                          if k in ("GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE"))
    if redirect_env:
        refuse(f"RECEIPT-ENV-REDIRECT-SET: {', '.join(redirect_env)} set in the writer's environment; "
               "unset them and retry")

    # r64 C1 (env): a caller-set GIT_INDEX_FILE would silently repoint every index read in this
    # writer at a caller-chosen index view. Refuse before any git call; scrubbing would pick the
    # index view for the caller, refusing leaves that choice with the caller.
    if "GIT_INDEX_FILE" in os.environ:
        refuse(f"RECEIPT-INDEX-ENV-SET: GIT_INDEX_FILE is set in the writer's environment "
               "(value not shown); unset it and retry")

    # r67 C1 (env): a caller-injected GIT_COMMON_DIR must resolve to this repository's own common dir, or refuse.
    _check_env_commondir(root)

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

    # r64 C1 (scope): resolve the real repository toplevel; every git ls-files below runs from it
    # with a :(top) pathspec, so a --root inside a subdirectory observes the whole index instead of
    # only its own subtree.
    tp = git(root, "rev-parse", "--show-toplevel")
    if tp.returncode != 0:
        refuse(f"cannot resolve the repository toplevel of {root}: {tp.stderr.decode('utf-8', 'replace').strip()}")
    top = os.fsdecode(tp.stdout.rstrip(b"\n"))
    # r62 C1 (calibration): a skip-worktree (S) or assume-unchanged (h) index entry hides worktree
    # divergence from `git status`, so a clean porcelain status proves nothing about that path.
    # Refuse unconditionally; --allow-dirty does not override this.
    # r63 C2 (coverage): the first non-H record is classed (unmerged, gitlink, absent) before refusal;
    # any other path keeps the r62 class token and message.
    fl = git(top, "ls-files", "-v", "-z", ":(top)")
    if fl.returncode != 0:
        refuse(f"cannot read index flags of {top}: {fl.stderr.decode('utf-8', 'replace').strip()}")
    for rec in fl.stdout.split(b"\0"):
        if not rec:
            continue
        tag, _, path = rec.partition(b" ")
        if tag != b"H":
            refuse(_flag_refusal(top, tag, path))

    # behaviour 7: clean lane tree unless --allow-dirty (r65 C1: the status reads override
    # status.showUntrackedFiles to `all`, so operator config cannot hide untracked entries)
    st = git(root, "-c", "status.showUntrackedFiles=all", "status", "--porcelain")
    if st.returncode != 0:
        detail = st.stderr.decode("utf-8", "replace").strip()
        refuse(f"cannot read worktree status of {root}: {detail}")
    if st.stdout and not ns.allow_dirty:
        refuse("lane worktree is dirty (git status --porcelain non-empty); pass --allow-dirty to override")
    # r63 C1 (operability): the pre-run snapshot. The wrapped command may change either read; both are
    # re-read after it completes and compared byte for byte before any receipt byte is composed.
    pre_flags, pre_status = fl.stdout, st.stdout
    # r64 C1 (content): under --allow-dirty the dirty state itself is the caller's accepted baseline;
    # fingerprint its content (sha256 per worktree-modified tracked file, every file under untracked
    # paths) so an in-run change that leaves both porcelain reads byte-identical still refuses.
    pre_content: "dict[bytes, bytes] | None" = None
    if ns.allow_dirty:
        pre_z = _status_z(top)
        if pre_z.returncode != 0:
            refuse(f"cannot read worktree status of {top}: {pre_z.stderr.decode('utf-8', 'replace').strip()}")
        pre_content = _content_snapshot(top, pre_z.stdout)

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
    # r63 C1 (operability): re-read the pre-run snapshot after the wrapped command and before any receipt
    # byte is composed. A difference refuses unconditionally (--allow-dirty does not override it).
    post_fl = git(top, "ls-files", "-v", "-z", ":(top)")
    post_st = git(root, "-c", "status.showUntrackedFiles=all", "status", "--porcelain")
    changed = []
    if post_fl.returncode != 0 or post_fl.stdout != pre_flags:
        changed.append("index flags (git ls-files -v -z)")
    if post_st.returncode != 0 or post_st.stdout != pre_status:
        changed.append("worktree status (git status --porcelain)")
    if pre_content is not None:
        post_z = _status_z(top)
        if post_z.returncode != 0:
            changed.append("worktree status (git status --porcelain -z)")
        else:
            post_content = _content_snapshot(top, post_z.stdout)
            for path in sorted(set(pre_content) | set(post_content)):
                if pre_content.get(path) != post_content.get(path):
                    changed.append(_delta_label(pre_content.get(path), post_content.get(path))
                                   + " " + path.decode("utf-8", "replace"))
    if changed:
        refuse("RECEIPT-STATE-CHANGED-DURING-RUN: " + " and ".join(changed) + " changed during the wrapped command; no receipt written")
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


def _py(code: str) -> str:
    return "python3 -c " + shlex.quote(code)


def _git_ok(d: str, *args: str, input_bytes: "bytes | None" = None) -> bytes:
    r = subprocess.run(["git", "-C", d, *args], input=input_bytes, capture_output=True)
    if r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout


def case_13_inrun_flag_refused(work: str) -> None:
    d = _fixture(work, "c13")
    rev = _head(d)
    outdir = _outdir(work)
    cmd = "git -C " + shlex.quote(d) + " update-index --skip-worktree tracked.txt"
    for extra in ([], ["--allow-dirty"]):
        out = os.path.join(outdir, f"flag{len(extra)}.txt")
        r = _run([*_base_args(d, rev, out), *extra, "--command", cmd])
        if r.returncode != 2 or os.path.exists(out):
            raise AssertionError(f"in-run flag {extra} rc={r.returncode}: {r.stderr.strip()}")
        if "RECEIPT-STATE-CHANGED-DURING-RUN: index flags" not in r.stderr:
            raise AssertionError(f"wrong in-run refusal {extra}: {r.stderr.strip()}")
        _git_ok(d, "update-index", "--no-skip-worktree", "tracked.txt")
    _no_stray(outdir)


def case_14_inrun_edit_refused(work: str) -> None:
    d = _fixture(work, "c14")
    rev = _head(d)
    outdir = _outdir(work)
    target = os.path.join(d, "tracked.txt")
    cmd = _py(f"open({target!r}, 'ab').write(b'forged\\n')")
    for extra in ([], ["--allow-dirty"]):
        out = os.path.join(outdir, f"edit{len(extra)}.txt")
        r = _run([*_base_args(d, rev, out), *extra, "--command", cmd])
        if r.returncode != 2 or os.path.exists(out):
            raise AssertionError(f"in-run edit {extra} rc={r.returncode}: {r.stderr.strip()}")
        if "RECEIPT-STATE-CHANGED-DURING-RUN: worktree status" not in r.stderr:
            raise AssertionError(f"wrong in-run refusal {extra}: {r.stderr.strip()}")
        with open(target, "wb") as f:
            f.write(b"clean\n")
    _no_stray(outdir)


def case_15_inrun_transient_restore_accepted(work: str) -> None:
    # named limit: an edit reverted before the post-run read is invisible to both reads
    d = _fixture(work, "c15")
    rev = _head(d)
    outdir = _outdir(work)
    target = os.path.join(d, "tracked.txt")
    code = f"p = {target!r}; o = open(p, 'rb').read(); open(p, 'ab').write(b'forged\\n'); open(p, 'wb').write(o)"
    out = os.path.join(outdir, "restore.txt")
    r = _run([*_base_args(d, rev, out), "--command", _py(code)])
    if r.returncode != 0 or not os.path.exists(out):
        raise AssertionError(f"transient restore rc={r.returncode}: {r.stderr.strip()}")
    if open(out, encoding="utf-8").read().splitlines()[-1] != "EXIT=0":
        raise AssertionError("EXIT=0 line missing")
    if open(target, "rb").read() != b"clean\n":
        raise AssertionError("restore did not put the committed bytes back")
    _no_stray(outdir)


def case_16_fsmonitor_silenced(work: str) -> None:
    # r62 sentinel F-1: a core.fsmonitor hook plus an fsmonitor-valid index bit hides a dirty file from
    # git status; the writer runs git with core.fsmonitor=false, so the dirty tree is still refused.
    d = _fixture(work, "c16")
    rev = _head(d)
    outdir = _outdir(work)
    hook = os.path.join(work, "silent-fsmonitor-c16.sh")
    with open(hook, "wb") as f:
        f.write(b'#!/bin/sh\necho "/"\nexit 0\n')
    os.chmod(hook, 0o755)
    _git_ok(d, "config", "core.fsmonitor", hook)
    _git_ok(d, "status", "--porcelain")
    with open(os.path.join(d, "tracked.txt"), "ab") as f:
        f.write(b"dirty\n")
    _git_ok(d, "update-index", "--fsmonitor-valid", "tracked.txt")
    out = os.path.join(outdir, "fsm.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"fsmonitor-silenced rc={r.returncode}: {r.stderr.strip()}")
    if "lane worktree is dirty" not in r.stderr:
        raise AssertionError(f"wrong refusal reason: {r.stderr.strip()}")
    _no_stray(outdir)


def case_17_unmerged_class(work: str) -> None:
    d = _fixture(work, "c17")
    rev = _head(d)
    outdir = _outdir(work)
    b1 = _git_ok(d, "hash-object", "-w", "--stdin", input_bytes=b"one\n").decode("ascii").strip()
    b2 = _git_ok(d, "hash-object", "-w", "--stdin", input_bytes=b"two\n").decode("ascii").strip()
    records = f"0 {'0' * 40}\ttracked.txt\n100644 {b1} 1\ttracked.txt\n100644 {b2} 2\ttracked.txt\n"
    _git_ok(d, "update-index", "--index-info", input_bytes=records.encode("ascii"))
    out = os.path.join(outdir, "unmerged.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"unmerged rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-INDEX-UNMERGED: tracked.txt " not in r.stderr or "RECEIPT-INDEX-FLAG-CONCEALED" in r.stderr:
        raise AssertionError(f"wrong unmerged class: {r.stderr.strip()}")
    _no_stray(outdir)


def case_18_gitlink_class(work: str) -> None:
    d = _fixture(work, "c18")
    head = _head(d)
    _git_ok(d, "update-index", "--add", "--cacheinfo", f"160000,{head},sub")
    r = subprocess.run(["git", "-C", d, *GIT_ID, "commit", "-q", "-m", "gitlink seed"], capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"gitlink commit failed: {r.stderr.strip()}")
    _git_ok(d, "update-index", "--skip-worktree", "sub")
    rev = _head(d)
    outdir = _outdir(work)
    out = os.path.join(outdir, "gitlink.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"gitlink rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-GITLINK-CONCEALED: sub " not in r.stderr or "RECEIPT-INDEX-FLAG-CONCEALED" in r.stderr:
        raise AssertionError(f"wrong gitlink class: {r.stderr.strip()}")
    _no_stray(outdir)


def case_19_absent_class(work: str) -> None:
    d = _fixture(work, "c19")
    rev = _head(d)
    outdir = _outdir(work)
    _git_ok(d, "update-index", "--skip-worktree", "tracked.txt")
    os.remove(os.path.join(d, "tracked.txt"))
    out = os.path.join(outdir, "absent.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"absent rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-INDEX-CONCEALED-ABSENT: tracked.txt " not in r.stderr or "RECEIPT-INDEX-FLAG-CONCEALED" in r.stderr:
        raise AssertionError(f"wrong absent class: {r.stderr.strip()}")
    _no_stray(outdir)


def case_20_generic_flag_byte_identical(work: str) -> None:
    d = _fixture(work, "c20")
    rev = _head(d)
    outdir = _outdir(work)
    tail = ("; skip-worktree or assume-unchanged hides worktree divergence from git status; "
            "clear it with git update-index --no-skip-worktree or --no-assume-unchanged, then retry\n")
    _git_ok(d, "update-index", "--skip-worktree", "tracked.txt")
    out = os.path.join(outdir, "generic-s.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"])
    want = "refused: RECEIPT-INDEX-FLAG-CONCEALED: tracked.txt carries index flag S" + tail
    if r.returncode != 2 or os.path.exists(out) or r.stderr != want:
        raise AssertionError(f"generic S rc={r.returncode}: {r.stderr!r}")
    _git_ok(d, "update-index", "--no-skip-worktree", "tracked.txt")
    _git_ok(d, "update-index", "--assume-unchanged", "tracked.txt")
    out2 = os.path.join(outdir, "generic-h.txt")
    r = _run([*_base_args(d, rev, out2), "--command", "/bin/echo hi"])
    want = "refused: RECEIPT-INDEX-FLAG-CONCEALED: tracked.txt carries index flag h" + tail
    if r.returncode != 2 or os.path.exists(out2) or r.stderr != want:
        raise AssertionError(f"generic h rc={r.returncode}: {r.stderr!r}")
    _no_stray(outdir)


def case_21_inrun_append_to_dirty_allow_dirty(work: str) -> None:
    # r64 C1 (N1): an append to an ALREADY-dirty tracked file under --allow-dirty changes no
    # porcelain bytes; the content snapshot must catch it.
    d = _fixture(work, "c21")
    rev = _head(d)
    outdir = _outdir(work)
    target = os.path.join(d, "tracked.txt")
    with open(target, "ab") as f:
        f.write(b"dirty\n")
    out = os.path.join(outdir, "control.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 0 or not os.path.exists(out):
        raise AssertionError(f"dirty baseline control rc={r.returncode}: {r.stderr.strip()}")
    out2 = os.path.join(outdir, "append.txt")
    cmd = _py(f"open({target!r}, 'ab').write(b'forged\\n')")
    r = _run([*_base_args(d, rev, out2), "--allow-dirty", "--command", cmd])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"in-run dirty append rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-STATE-CHANGED-DURING-RUN: content tracked.txt" not in r.stderr:
        raise AssertionError(f"wrong in-run refusal: {r.stderr.strip()}")
    with open(target, "wb") as f:
        f.write(b"clean\n")
    _no_stray(outdir)


def case_22_inrun_untracked_dir(work: str) -> None:
    # r64 C1 (N2): a new or deleted file inside an ALREADY-untracked directory under --allow-dirty
    # changes no porcelain bytes ("?? extra/" both times); the content snapshot must catch it.
    d = _fixture(work, "c22")
    rev = _head(d)
    outdir = _outdir(work)
    extra = os.path.join(d, "extra")
    os.makedirs(extra)
    with open(os.path.join(extra, "seed.txt"), "wb") as f:
        f.write(b"seed\n")
    out = os.path.join(outdir, "control.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 0 or not os.path.exists(out):
        raise AssertionError(f"untracked-dir baseline control rc={r.returncode}: {r.stderr.strip()}")
    out2 = os.path.join(outdir, "new.txt")
    code = f"import os\nopen(os.path.join({extra!r}, 'new.txt'), 'wb').write(b'new\\n')"
    r = _run([*_base_args(d, rev, out2), "--allow-dirty", "--command", _py(code)])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"in-run new file in untracked dir rc={r.returncode}: {r.stderr.strip()}")
    # r65: the untracked-visibility override lists individual files, so the porcelain byte compare
    # fires beside the content snapshot; assert the class token and the content row, not one message.
    if "RECEIPT-STATE-CHANGED-DURING-RUN" not in r.stderr or "content extra/new.txt" not in r.stderr:
        raise AssertionError(f"wrong refusal: {r.stderr.strip()}")
    out3 = os.path.join(outdir, "delete.txt")
    code = f"import os\nos.remove(os.path.join({extra!r}, 'seed.txt'))"
    r = _run([*_base_args(d, rev, out3), "--allow-dirty", "--command", _py(code)])
    if r.returncode != 2 or os.path.exists(out3):
        raise AssertionError(f"in-run delete in untracked dir rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-STATE-CHANGED-DURING-RUN" not in r.stderr or "content extra/seed.txt" not in r.stderr:
        raise AssertionError(f"wrong refusal: {r.stderr.strip()}")
    shutil.rmtree(extra)
    _no_stray(outdir)


def case_23_inrun_restore_dirty_bytes(work: str) -> None:
    # r64 C1: restore-to-exact-bytes still accepts — the dirty baseline bytes rewritten exactly
    # before the post-run snapshot leave both snapshots equal.
    d = _fixture(work, "c23")
    rev = _head(d)
    outdir = _outdir(work)
    target = os.path.join(d, "tracked.txt")
    with open(target, "ab") as f:
        f.write(b"dirty\n")
    dirty = open(target, "rb").read()
    code = (f"p = {target!r}\n"
            f"o = open(p, 'rb').read()\n"
            f"open(p, 'ab').write(b'forged\\n')\n"
            f"open(p, 'wb').write({dirty!r})\n")
    out = os.path.join(outdir, "restore.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", _py(code)])
    if r.returncode != 0 or not os.path.exists(out):
        raise AssertionError(f"dirty restore rc={r.returncode}: {r.stderr.strip()}")
    if open(out, encoding="utf-8").read().splitlines()[-1] != "EXIT=0":
        raise AssertionError("EXIT=0 line missing")
    if open(target, "rb").read() != dirty:
        raise AssertionError("restore did not put the dirty baseline bytes back")
    with open(target, "wb") as f:
        f.write(b"clean\n")
    _no_stray(outdir)


def case_24_git_index_file_env_refused(work: str) -> None:
    # r64 C1 (N3): GIT_INDEX_FILE in the writer's environment refuses before any git call, even when
    # the redirected index is a byte copy of the repository's own forged index.
    d = _fixture(work, "c24")
    rev = _head(d)
    outdir = _outdir(work)
    _git_ok(d, "update-index", "--skip-worktree", "tracked.txt")
    idx_copy = os.path.join(work, "index-copy-c24")
    shutil.copyfile(os.path.join(d, ".git", "index"), idx_copy)
    out = os.path.join(outdir, "env.txt")
    env = dict(os.environ)
    env["GIT_INDEX_FILE"] = idx_copy
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"], env=env)
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"index-env rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-INDEX-ENV-SET" not in r.stderr:
        raise AssertionError(f"wrong index-env refusal: {r.stderr.strip()}")
    # control: the same forgery read through the repository's own index is still class refused
    out2 = os.path.join(outdir, "env-control.txt")
    r = _run([*_base_args(d, rev, out2), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"index-env control rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-INDEX-FLAG-CONCEALED" not in r.stderr:
        raise AssertionError(f"control should hit the forged flag in the real index: {r.stderr.strip()}")
    _git_ok(d, "update-index", "--no-skip-worktree", "tracked.txt")
    os.remove(idx_copy)
    # an empty GIT_INDEX_FILE is still "set": refused too
    env_empty = dict(os.environ)
    env_empty["GIT_INDEX_FILE"] = ""
    out3 = os.path.join(outdir, "env-empty.txt")
    r = _run([*_base_args(d, rev, out3), "--allow-dirty", "--command", "/bin/echo hi"], env=env_empty)
    if r.returncode != 2 or os.path.exists(out3) or "RECEIPT-INDEX-ENV-SET" not in r.stderr:
        raise AssertionError(f"empty GIT_INDEX_FILE not refused: rc={r.returncode} {r.stderr.strip()}")
    _no_stray(outdir)


def case_25_subdir_root_full_index_scope(work: str) -> None:
    # r64 C1 (N4): a --root inside a subdirectory must still observe the whole index; a concealed
    # flag on a tracked file OUTSIDE the subtree is refused (base saw only the subtree's entries).
    d = _fixture(work, "c25")
    rev = _head(d)
    outdir = _outdir(work)
    sub = os.path.join(d, "sub")
    os.makedirs(sub)
    with open(os.path.join(sub, "ph.txt"), "wb") as f:
        f.write(b"placeholder\n")
    _commit_all(d, "subdir seed")
    rev = _head(d)
    _git_ok(d, "update-index", "--skip-worktree", "tracked.txt")
    out = os.path.join(outdir, "sub.txt")
    r = _run(["--root", sub, "--rev", rev, "--instrument", "ph.txt", "--out", out,
              "--allow-outside", "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"subdir-root concealed rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-INDEX-FLAG-CONCEALED: tracked.txt " not in r.stderr:
        raise AssertionError(f"wrong subdir-root refusal: {r.stderr.strip()}")
    _git_ok(d, "update-index", "--no-skip-worktree", "tracked.txt")
    _no_stray(outdir)


def case_26_inrun_append_to_untracked_file(work: str) -> None:
    # r64 C1 (a) corollary: an append to an untracked FILE under --allow-dirty keeps porcelain bytes
    # ("?? extra.txt" both times); the content snapshot must catch it.
    d = _fixture(work, "c26")
    rev = _head(d)
    outdir = _outdir(work)
    target = os.path.join(d, "extra.txt")
    with open(target, "wb") as f:
        f.write(b"u\n")
    out = os.path.join(outdir, "control.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 0 or not os.path.exists(out):
        raise AssertionError(f"untracked-file baseline control rc={r.returncode}: {r.stderr.strip()}")
    out2 = os.path.join(outdir, "append.txt")
    cmd = _py(f"open({target!r}, 'ab').write(b'forged\\n')")
    r = _run([*_base_args(d, rev, out2), "--allow-dirty", "--command", cmd])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"in-run untracked append rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-STATE-CHANGED-DURING-RUN: content extra.txt" not in r.stderr:
        raise AssertionError(f"wrong refusal: {r.stderr.strip()}")
    os.remove(target)
    _no_stray(outdir)


def case_27_mode_flip_refused(work: str) -> None:
    # r65 C1 (MOD): a mode-only in-run flip under --allow-dirty leaves both porcelain reads and the
    # content digest byte-identical; the mode byte in the snapshot payload must catch it.
    d = _fixture(work, "c27")
    rev = _head(d)
    outdir = _outdir(work)
    target = os.path.join(d, "tracked.txt")
    with open(target, "ab") as f:
        f.write(b"dirty\n")
    out = os.path.join(outdir, "control.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 0 or not os.path.exists(out):
        raise AssertionError(f"dirty baseline control rc={r.returncode}: {r.stderr.strip()}")
    out2 = os.path.join(outdir, "mode.txt")
    code = f"import os\nos.chmod({target!r}, 0o755)"
    r = _run([*_base_args(d, rev, out2), "--allow-dirty", "--command", _py(code)])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"in-run mode flip rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-STATE-CHANGED-DURING-RUN: mode tracked.txt" not in r.stderr:
        raise AssertionError(f"wrong mode-flip refusal: {r.stderr.strip()}")
    os.chmod(target, 0o644)
    with open(target, "wb") as f:
        f.write(b"clean\n")
    _no_stray(outdir)


def case_28_untracked_visibility(work: str) -> None:
    # r65 C1 (V1/V2): an operator-injected status.showUntrackedFiles=no must not hide untracked
    # entries from the dirty check; an honest clean tree under the same config still writes.
    d = _fixture(work, "c28")
    rev = _head(d)
    outdir = _outdir(work)
    _git_ok(d, "config", "status.showUntrackedFiles", "no")
    with open(os.path.join(d, "hidden.txt"), "wb") as f:
        f.write(b"u\n")
    out = os.path.join(outdir, "visible.txt")
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"])
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"hidden untracked accepted rc={r.returncode}: {r.stderr.strip()}")
    if "lane worktree is dirty" not in r.stderr:
        raise AssertionError(f"wrong visibility refusal: {r.stderr.strip()}")
    os.remove(os.path.join(d, "hidden.txt"))
    out2 = os.path.join(outdir, "honest.txt")
    r = _run([*_base_args(d, rev, out2), "--command", "/bin/echo hi"])
    if r.returncode != 0 or not os.path.exists(out2):
        raise AssertionError(f"clean tree under config refused rc={r.returncode}: {r.stderr.strip()}")
    _git_ok(d, "config", "--unset", "status.showUntrackedFiles")
    _no_stray(outdir)


def case_29_symlink_record_rule(work: str) -> None:
    # r65 C1 (SY1/SY2, M5 rule frozen): a symlink inside an untracked directory is recorded by name
    # and target, never followed; a stable symlink accepts under --allow-dirty and an in-run
    # retarget refuses on the recorded target bytes.
    d = _fixture(work, "c29")
    rev = _head(d)
    outdir = _outdir(work)
    extra = os.path.join(d, "extra")
    os.makedirs(extra)
    with open(os.path.join(extra, "seed.txt"), "wb") as f:
        f.write(b"seed\n")
    os.symlink("../tracked.txt", os.path.join(extra, "link"))
    out = os.path.join(outdir, "stable.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 0 or not os.path.exists(out):
        raise AssertionError(f"stable symlink accepted rc={r.returncode}: {r.stderr.strip()}")
    out2 = os.path.join(outdir, "retarget.txt")
    link = os.path.join(extra, "link")
    code = f"import os\nos.unlink({link!r})\nos.symlink('../instrument.sh', {link!r})"
    r = _run([*_base_args(d, rev, out2), "--allow-dirty", "--command", _py(code)])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"in-run symlink retarget rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-STATE-CHANGED-DURING-RUN: content extra/link" not in r.stderr:
        raise AssertionError(f"wrong retarget refusal: {r.stderr.strip()}")
    shutil.rmtree(extra)
    _no_stray(outdir)


def case_30_index_env_nonexistent(work: str) -> None:
    # r65 C1 (P13): a GIT_INDEX_FILE naming a path that does not exist is still "set" in the
    # writer's environment and refuses; the base writer read the missing index vacuously.
    d = _fixture(work, "c30")
    rev = _head(d)
    outdir = _outdir(work)
    env = dict(os.environ)
    env["GIT_INDEX_FILE"] = os.path.join(work, "no-such-index-c30")
    out = os.path.join(outdir, "missing.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"], env=env)
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"missing index env rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-INDEX-ENV-SET" not in r.stderr:
        raise AssertionError(f"wrong env refusal: {r.stderr.strip()}")
    _no_stray(outdir)


def case_31_env_config_refused(work: str) -> None:
    # r66 C1 (E1/E2): caller-injected config env routes refuse on presence, before any git call; names only.
    d = _fixture(work, "c31")
    rev = _head(d)
    outdir = _outdir(work)
    cases = (
        ({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.excludesFile",
          "GIT_CONFIG_VALUE_0": "/nonexistent-r66-secret"}, "GIT_CONFIG_COUNT, GIT_CONFIG_KEY_0, GIT_CONFIG_VALUE_0"),
        ({"GIT_CONFIG_PARAMETERS": ""}, "GIT_CONFIG_PARAMETERS"),
    )
    for i, (extra, names) in enumerate(cases):
        out = os.path.join(outdir, f"cfg{i}.txt")
        env = dict(os.environ)
        env.update(extra)
        r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"], env=env)
        if r.returncode != 2 or os.path.exists(out):
            raise AssertionError(f"config env {names} rc={r.returncode}: {r.stderr.strip()}")
        if "RECEIPT-ENV-CONFIG-SET" not in r.stderr or names not in r.stderr:
            raise AssertionError(f"wrong config-env refusal: {r.stderr.strip()}")
        if "/nonexistent-r66-secret" in r.stderr:
            raise AssertionError("config env value echoed")
    _no_stray(outdir)


def case_32_env_redirect_refused(work: str) -> None:
    # r66 C1 (E4-E6): object-redirect env routes refuse on presence, names only; the index env value is not echoed.
    d = _fixture(work, "c32")
    rev = _head(d)
    outdir = _outdir(work)
    cases = (
        ({"GIT_OBJECT_DIRECTORY": os.path.join(d, ".git", "objects")}, "GIT_OBJECT_DIRECTORY"),
        ({"GIT_ALTERNATE_OBJECT_DIRECTORIES": ""}, "GIT_ALTERNATE_OBJECT_DIRECTORIES"),
        ({"GIT_REPLACE_REF_BASE": "refs/replace-r66/"}, "GIT_REPLACE_REF_BASE"),
        ({"GIT_INDEX_FILE": "/nonexistent-r66-index"}, "RECEIPT-INDEX-ENV-SET"),
    )
    for i, (extra, token) in enumerate(cases):
        out = os.path.join(outdir, f"red{i}.txt")
        env = dict(os.environ)
        env.update(extra)
        r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"], env=env)
        if r.returncode != 2 or os.path.exists(out):
            raise AssertionError(f"redirect env {token} rc={r.returncode}: {r.stderr.strip()}")
        klass = "RECEIPT-INDEX-ENV-SET" if token == "RECEIPT-INDEX-ENV-SET" else "RECEIPT-ENV-REDIRECT-SET"
        if klass not in r.stderr or token not in r.stderr:
            raise AssertionError(f"wrong redirect-env refusal: {r.stderr.strip()}")
        if "/nonexistent-r66-index" in r.stderr:
            raise AssertionError("GIT_INDEX_FILE value echoed")
    _no_stray(outdir)


def case_33_mode_setuid_refused(work: str) -> None:
    # r66 C1 (MOD2): the snapshot mode byte keeps setuid; a mode-only in-run flip under --allow-dirty refuses.
    d = _fixture(work, "c33")
    rev = _head(d)
    outdir = _outdir(work)
    target = os.path.join(d, "tracked.txt")
    with open(target, "ab") as f:
        f.write(b"dirty\n")
    out = os.path.join(outdir, "control.txt")
    r = _run([*_base_args(d, rev, out), "--allow-dirty", "--command", "/bin/echo hi"])
    if r.returncode != 0 or not os.path.exists(out):
        raise AssertionError(f"dirty baseline control rc={r.returncode}: {r.stderr.strip()}")
    out2 = os.path.join(outdir, "setuid.txt")
    code = f"import os\nos.chmod({target!r}, 0o4644)"
    r = _run([*_base_args(d, rev, out2), "--allow-dirty", "--command", _py(code)])
    if r.returncode != 2 or os.path.exists(out2):
        raise AssertionError(f"in-run setuid flip rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-STATE-CHANGED-DURING-RUN: mode tracked.txt" not in r.stderr:
        raise AssertionError(f"wrong setuid-flip refusal: {r.stderr.strip()}")
    os.chmod(target, 0o644)
    with open(target, "wb") as f:
        f.write(b"clean\n")
    _no_stray(outdir)


def case_34_env_commondir_mismatch_refused(work: str) -> None:
    # r67 C1 (W1/W2): a caller-injected GIT_COMMON_DIR naming a copy of .git (not this repository's common dir) refuses
    # before any git call reads the caller value; the value is not echoed and no receipt is written.
    d = _fixture(work, "c34")
    rev = _head(d)
    outdir = _outdir(work)
    copy = os.path.join(work, "c34-commondir-copy")
    shutil.copytree(os.path.join(d, ".git"), copy, symlinks=True)
    out = os.path.join(outdir, "mismatch.txt")
    env = dict(os.environ)
    env["GIT_COMMON_DIR"] = copy
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"], env=env)
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"mismatched GIT_COMMON_DIR rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-ENV-COMMONDIR-MISMATCH" not in r.stderr or "GIT_COMMON_DIR" not in r.stderr:
        raise AssertionError(f"wrong common-dir refusal: {r.stderr.strip()}")
    if copy in r.stderr:
        raise AssertionError("GIT_COMMON_DIR value echoed")
    _no_stray(outdir)


def case_35_env_commondir_match_accepted(work: str) -> None:
    # r67 C1 (W3): a GIT_COMMON_DIR equal to this repository's own common dir is accepted, absolute or relative
    # (a relative value resolves against the writer's cwd: the repository is run from d).
    d = _fixture(work, "c35")
    rev = _head(d)
    outdir = _outdir(work)
    cases = (
        (os.path.realpath(os.path.join(d, ".git")), d),
        (".git", d),
    )
    for i, (value, cwd) in enumerate(cases):
        out = os.path.join(outdir, f"match{i}.txt")
        env = dict(os.environ)
        env["GIT_COMMON_DIR"] = value
        r = subprocess.run([sys.executable, WRITER_PATH, *_base_args(d, rev, out), "--command", "/bin/echo hi"],
                           capture_output=True, text=True, timeout=300, env=env, cwd=cwd)
        if r.returncode != 0 or not os.path.exists(out):
            raise AssertionError(f"equal GIT_COMMON_DIR={value!r} rc={r.returncode}: {r.stderr.strip()}")
    _no_stray(outdir)


def case_36_env_commondir_empty_refused(work: str) -> None:
    # r67 C1: an empty GIT_COMMON_DIR is still "set" and refuses; presence is the test.
    d = _fixture(work, "c36")
    rev = _head(d)
    outdir = _outdir(work)
    out = os.path.join(outdir, "empty.txt")
    env = dict(os.environ)
    env["GIT_COMMON_DIR"] = ""
    r = _run([*_base_args(d, rev, out), "--command", "/bin/echo hi"], env=env)
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"empty GIT_COMMON_DIR rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-ENV-COMMONDIR-MISMATCH" not in r.stderr:
        raise AssertionError(f"wrong empty common-dir refusal: {r.stderr.strip()}")
    _no_stray(outdir)


def case_37_env_commondir_unresolvable_refused(work: str) -> None:
    # r67 C1: GIT_COMMON_DIR set while --root is not inside any repository refuses (resolution failure). The
    # ceiling keeps repository discovery from climbing out of the scratch directory.
    nr = tempfile.mkdtemp(prefix="c37-norepo.", dir=work)
    d = _fixture(work, "c37")
    rev = _head(d)
    outdir = _outdir(work)
    out = os.path.join(outdir, "unresolvable.txt")
    env = dict(os.environ)
    env["GIT_COMMON_DIR"] = os.path.join(nr, ".git")
    env["GIT_CEILING_DIRECTORIES"] = work
    r = _run([*_base_args(nr, rev, out), "--command", "/bin/echo hi"], env=env)
    if r.returncode != 2 or os.path.exists(out):
        raise AssertionError(f"unresolvable GIT_COMMON_DIR rc={r.returncode}: {r.stderr.strip()}")
    if "RECEIPT-ENV-COMMONDIR-MISMATCH" not in r.stderr:
        raise AssertionError(f"wrong unresolvable refusal: {r.stderr.strip()}")
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
    ("in-run-flag: skip-worktree set by the wrapped command refused, --allow-dirty included", case_13_inrun_flag_refused),
    ("in-run-edit: tracked edit made by the wrapped command refused, --allow-dirty included", case_14_inrun_edit_refused),
    ("in-run-restore: edit reverted before the post-run read accepted (named limit)", case_15_inrun_transient_restore_accepted),
    ("fsmonitor-off: core.fsmonitor hook plus fsmonitor-valid bit cannot hide a dirty tree", case_16_fsmonitor_silenced),
    ("unmerged-class: stage 1+2 entry refused as RECEIPT-INDEX-UNMERGED", case_17_unmerged_class),
    ("gitlink-class: skip-worktree gitlink refused as RECEIPT-GITLINK-CONCEALED", case_18_gitlink_class),
    ("absent-class: skip-worktree file absent from worktree refused as RECEIPT-INDEX-CONCEALED-ABSENT", case_19_absent_class),
    ("generic-class: present S and h entries keep the r62 message byte for byte", case_20_generic_flag_byte_identical),
    ("in-run-append-to-dirty: --allow-dirty append to an already-dirty tracked file refused (r64 N1)", case_21_inrun_append_to_dirty_allow_dirty),
    ("in-run-untracked-dir: new or deleted file in a pre-existing untracked directory refused (r64 N2)", case_22_inrun_untracked_dir),
    ("in-run-restore-dirty: exact restore of the dirty baseline bytes before the post-run read accepted", case_23_inrun_restore_dirty_bytes),
    ("index-env: GIT_INDEX_FILE set in the writer environment refused before any git call (r64 N3)", case_24_git_index_file_env_refused),
    ("subdir-root: --root inside a subdirectory still refuses an out-of-subtree concealed flag (r64 N4)", case_25_subdir_root_full_index_scope),
    ("in-run-append-to-untracked: --allow-dirty append to an untracked file refused", case_26_inrun_append_to_untracked_file),
    ("mode-flip: mode-only in-run chmod under --allow-dirty refused via the snapshot mode byte (r65)", case_27_mode_flip_refused),
    ("untracked-visibility: status.showUntrackedFiles=no cannot hide untracked entries; clean tree still writes (r65)", case_28_untracked_visibility),
    ("symlink-record: stable symlink accepted, in-run retarget refused, never followed (r65)", case_29_symlink_record_rule),
    ("index-env-missing: GIT_INDEX_FILE naming a nonexistent path refused (r65 P13)", case_30_index_env_nonexistent),
    ("env-config: caller-injected GIT_CONFIG_* refused by name, empty value included (r66 E1/E2)", case_31_env_config_refused),
    ("env-redirect: GIT_OBJECT_DIRECTORY/ALTERNATE/REPLACE_REF_BASE refused by name; GIT_INDEX_FILE value not echoed (r66 E4-E6)", case_32_env_redirect_refused),
    ("mode-bits: setuid in-run flip refused via the full-mode snapshot byte (r66 MOD2)", case_33_mode_setuid_refused),
    ("env-commondir-mismatch: caller GIT_COMMON_DIR naming another common dir refused by name, value not echoed (r67 W1/W2)", case_34_env_commondir_mismatch_refused),
    ("env-commondir-match: GIT_COMMON_DIR equal to the repository's own common dir accepted, absolute and relative (r67 W3)", case_35_env_commondir_match_accepted),
    ("env-commondir-empty: empty GIT_COMMON_DIR refused, presence is the test (r67)", case_36_env_commondir_empty_refused),
    ("env-commondir-unresolvable: GIT_COMMON_DIR set with --root outside any repository refused (r67)", case_37_env_commondir_unresolvable_refused),
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
