#!/usr/bin/env python3
"""souji-worktree-drift.py — F1 fleet worktree-registration drift detector (r36 C3).

The round-35 census (census/round-35/records/prune-census.tsv, knowledge entry
corpus/knowledge/fleet-prune-numerator-r35.md) recorded one dated numerator:
26 repositories, 27 registrations, 0 prunable. It was a one-off manual record;
nothing re-derived it, so the coverage map's F1 frontier item ("fleet exposure
numerator re-census") could only be answered by hand, and the r35 spot-check
found the record's own counting method wrong (dry-run candidates come out on
stderr, not stdout; four phantom paths).

This tool turns that record into a surface: it re-measures every repository the
record names, read-only, and reports the drift between the recorded numerator
and the live one. `--root` is a containment boundary: a record row that resolves
outside it is refused (RECORD-OUTSIDE-ROOT), and `--json` is refused when its
resolved path is inside the root or any measured repository, or when it is a
multi-link (hardlinked) file. It never prunes and
never consults the network. The child git process gets a whitelisted
environment (no inherited GIT_* variable; config discovery neutralised with
GIT_CONFIG_NOSYSTEM=1 and GIT_CONFIG_GLOBAL/SYSTEM=/dev/null), so a
path-valued trace variable or an env-injected config cannot make git write.

Record format (the r35 census TSV):
    REPO<TAB>name<TAB>regs=N<TAB>prunable=N
    TOTAL<TAB>repos=N<TAB>regs=N<TAB>prunable=N

Measurement per repository (S232, git-worktree(1) § LIST OUTPUT FORMAT at
git 2.56.0):
  regs      number of `worktree ` records in `git worktree list --porcelain`
  prunable  number of candidate lines `git worktree prune --dry-run -v`
            writes to stderr

Drift classes: REGS-CHANGED, PRUNABLE-CHANGED, ABSENT (recorded, not a git
work tree now), UNREACHABLE (git call failed or exceeded --timeout),
UNRECORDED (a git work tree under --root the record does not name).

CLI:
  python3 -B tools/souji-worktree-drift.py --root FLEET --record PATH
      [--timeout SECS] [--json OUT] [--skip-unrecorded]

Exit: 0 no drift rows, 1 drift rows found, 2 could-not-evaluate. Every
refusal class the code can raise is named here (r38 C2, r37 routed defect 6):

  RECORD-MISSING         EACCES or ELOOP opening the record path: the path
                         exists but cannot be opened or read
  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line
                         that does not match the schema, a duplicated name, or
                         a TOTAL row that disagrees (any TOTAL row, in any
                         position: every one is checked against the REPO rows)
  RECORD-EMPTY           no REPO rows
  RECORD-OUTSIDE-ROOT    a record row, or the gitdir it resolves to, escapes
                         --root
  JSON-INSIDE-MEASURED-TREE  the --json target lies under --root or under a
                         measured repository
  JSON-IS-RECORD         the --json target is the --record file (same path or
                         same inode, so the run would overwrite its input)
  JSON-NOT-REGULAR       the --json target exists and is not a regular file
                         (a FIFO would block a blocking open forever)
  JSON-HARDLINKED        the --json target has more than one link
  JSON-UNWRITABLE        the --json write failed (including a symlinked path
                         component, refused by the O_NOFOLLOW walk)
  USAGE                  --root is not a directory, or --timeout < 1
"""
import argparse
import errno
import json
import os
import re
import stat
import subprocess
import sys

# r37 C2 (r36 routed defect 3, W2/W3): a subtractive scrub let every variable
# not on the list through — GIT_TRACE_REFS wrote a trace file, and because the
# list *removed* GIT_CONFIG_NOSYSTEM / GIT_CONFIG_GLOBAL / GIT_CONFIG_SYSTEM,
# real and injected config (including env config) could set a trace2 target.
# The child environment is now a whitelist: no inherited GIT_* variable reaches
# git, and config discovery is neutralised explicitly.
CHILD_ENV = {
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_ATTR_NOSYSTEM": "1",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_TERMINAL_PROMPT": "0",
}
ROW = re.compile(r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d)\tprunable=(?P<prunable>\d+)$")
TOTAL = re.compile(r"^TOTAL\trepos=(?P<repos>\d+)\tregs=(?P<regs>\d+)\tprunable=(?P<prunable>\d+)$")


class Refusal(Exception):
    pass


def git_env():
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")}
    env.update(CHILD_ENV)
    if "TMPDIR" in os.environ:
        env["TMPDIR"] = os.environ["TMPDIR"]
    return env


def git(args, path, timeout):
    cmd = [
        "git",
        "--no-optional-locks",
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.hooksPath=/dev/null",
        "-C",
        path,
    ] + args
    return subprocess.run(
        cmd,
        env=git_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def parse_record(path):
    # r37 A2.4 (wave seat W1SentinelEnv S1): a FIFO record blocked forever in
    # open().read() — the run never terminated and never reported. r38 A4 (wave seat
    # W1SentEnvelope F1/R3): the isfile-then-open pair was still a TOCTOU — a path
    # swapped to a FIFO between the check and the open blocked forever. The open is
    # now O_NONBLOCK and the descriptor is checked with fstat before any read, so no
    # special file can be waited on; a missing path keeps its RECORD-MALFORMED class.
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            raise Refusal("RECORD-MALFORMED: %s is not a regular file" % path)
        raise Refusal("RECORD-MISSING: %s" % exc)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise Refusal("RECORD-MALFORMED: %s is not a regular file" % path)
        os.set_blocking(fd, True)
        chunks = []
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        raw = b"".join(chunks).decode("utf-8", "replace")
    finally:
        os.close(fd)
    rows = []
    total = None
    totals = []
    for lineno, line in enumerate(raw.splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        m = ROW.match(line)
        if m:
            name = m.group("name")
            if name in [r["name"] for r in rows]:
                raise Refusal("RECORD-MALFORMED: line %d duplicates %s" % (lineno, name))
            rows.append({"name": name, "regs": int(m.group("regs")), "prunable": int(m.group("prunable"))})
            continue
        m = TOTAL.match(line)
        if m:
            total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), "prunable": int(m.group("prunable"))}
            # r41 (R40-D-TOTAL): every TOTAL row is kept and checked below, so a
            # disagreeing TOTAL is refused wherever it sits (r40 M40-4: the loop
            # used to keep only the last row, accepting a first-disagreeing,
            # last-agreeing pair that the docstring calls malformed).
            totals.append(total)
            continue
        raise Refusal("RECORD-MALFORMED: line %d does not match the census schema" % lineno)
    if not rows:
        raise Refusal("RECORD-EMPTY: no REPO rows in %s" % path)
    for total in totals:
        if total["repos"] != len(rows):
            raise Refusal("RECORD-MALFORMED: TOTAL repos=%d but %d REPO rows" % (total["repos"], len(rows)))
        if total["regs"] != sum(r["regs"] for r in rows):
            raise Refusal("RECORD-MALFORMED: TOTAL regs=%d but REPO rows sum to %d" % (total["regs"], sum(r["regs"] for r in rows)))
        if total["prunable"] != sum(r["prunable"] for r in rows):
            raise Refusal(
                "RECORD-MALFORMED: TOTAL prunable=%d but REPO rows sum to %d"
                % (total["prunable"], sum(r["prunable"] for r in rows))
            )
    return rows, total


def measure(path, timeout):
    """Return (regs, prunable, None) or (None, None, class)."""
    try:
        listed = git(["worktree", "list", "--porcelain"], path, timeout)
    except subprocess.TimeoutExpired:
        return None, None, "UNREACHABLE:list-timeout"
    if listed.returncode != 0:
        return None, None, "UNREACHABLE:list-rc=%d" % listed.returncode
    regs = sum(1 for line in listed.stdout.decode("utf-8", "replace").splitlines() if line.startswith("worktree "))
    try:
        dry = git(["worktree", "prune", "--dry-run", "-v"], path, timeout)
    except subprocess.TimeoutExpired:
        return None, None, "UNREACHABLE:prune-timeout"
    if dry.returncode != 0:
        return None, None, "UNREACHABLE:prune-rc=%d" % dry.returncode
    prunable = sum(1 for line in dry.stderr.decode("utf-8", "replace").splitlines() if line.strip())
    return regs, prunable, None


def repo_path(root, name):
    direct = os.path.join(root, name)
    if os.path.isdir(os.path.join(direct, ".git")) or os.path.isfile(os.path.join(direct, ".git")):
        return direct
    if name == os.path.basename(root.rstrip("/")) and os.path.isdir(os.path.join(root, ".git")):
        return root
    return None


def discover(root):
    names = []
    try:
        entries = sorted(os.listdir(root))
    except OSError:
        return names
    for entry in entries:
        path = os.path.join(root, entry)
        if os.path.islink(path):
            # r37 A2.7: a symlinked child would be measured (and could be the
            # --json target's repository) without residing under --root.
            continue
        if not os.path.isdir(path):
            continue
        if os.path.isdir(os.path.join(path, ".git")) or os.path.isfile(os.path.join(path, ".git")):
            names.append(entry)
    if os.path.isdir(os.path.join(root, ".git")):
        names.insert(0, os.path.basename(root.rstrip("/")) or "root")
    return names


def open_nofollow(path):
    """Open path for writing with every component resolved O_NOFOLLOW.

    r37 A2 (wave seat W1SentinelContain): O_NOFOLLOW on the leaf still re-followed
    a parent directory swapped after the guard; a per-component walk refuses any
    symlinked ancestor (the resolved target has no `..` components).

    r38 C2 (r37 named limit: the `--json` FIFO hang): a plain O_WRONLY open of an
    existing FIFO blocks until a reader appears, so the run never terminates and
    never reports. O_NONBLOCK makes that open return at once (ENXIO with no
    reader), and the fstat below refuses any non-regular target, so no special
    file can be written or waited on.
    """
    parts = [p for p in path.split("/") if p not in ("", ".")]
    if not path.startswith("/") or not parts:
        raise OSError("path is not absolute")
    dirfd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dirfd)
            os.close(dirfd)
            dirfd = nxt
        try:
            fd = os.open(
                parts[-1],
                os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,
                0o644,
                dir_fd=dirfd,
            )
        except OSError as exc:
            # ENXIO: a FIFO with no reader. EISDIR: a directory. Both are "exists
            # and is not a regular file"; ELOOP/EACCES stay JSON-UNWRITABLE.
            if exc.errno in (errno.ENXIO, errno.EISDIR):
                raise Refusal("JSON-NOT-REGULAR: %s is not a regular file" % path)
            raise
        mode = os.fstat(fd).st_mode
        if not stat.S_ISREG(mode):
            os.close(fd)
            raise Refusal("JSON-NOT-REGULAR: %s is not a regular file" % path)
        os.set_blocking(fd, True)
        return fd
    finally:
        os.close(dirfd)


def run(args):
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        raise Refusal("USAGE: --root %s is not a directory" % root)
    root_real = os.path.realpath(root)
    rows, total = parse_record(args.record)
    # r37 C2 (r36 routed defect 3, W1): --root is a containment boundary. A record
    # row naming an absolute path or `../sibling` escaped it, so the same run could
    # observe a repository the caller's root does not govern.
    measured = [root_real]
    for row in rows:
        resolved = os.path.realpath(os.path.join(root, row["name"]))
        try:
            inside = os.path.commonpath([resolved, root_real]) == root_real
        except ValueError:
            inside = False
        if not inside:
            raise Refusal("RECORD-OUTSIDE-ROOT: %s resolves outside %s" % (row["name"], root_real))
        measured.append(resolved)
        # r37 A2.7 (wave seat W2CritC2): the repository actually measured is the
        # one the gitdir resolves to (a `.git` *file* can point outside --root);
        # feed that realpath to the --json guard too.
        if os.path.isdir(resolved) and (os.path.isdir(os.path.join(resolved, ".git")) or os.path.isfile(os.path.join(resolved, ".git"))):
            try:
                got = git(["rev-parse", "--absolute-git-dir"], resolved, args.timeout)
            except subprocess.TimeoutExpired:
                got = None
            if got is not None and got.returncode == 0:
                gitdir = os.path.realpath(got.stdout.decode("utf-8", "replace").strip())
                try:
                    gitdir_inside = os.path.commonpath([gitdir, root_real]) == root_real
                except ValueError:
                    gitdir_inside = False
                if not gitdir_inside:
                    raise Refusal("RECORD-OUTSIDE-ROOT: %s gitdir resolves outside %s" % (row["name"], root_real))
                measured.append(gitdir)
    json_target = None
    if args.json:
        # r36 A2 + r37 C2 (W1/W4): the guard resolved one path while the writer
        # opened another, and it compared only the root — not the record's
        # repositories. Check every measured path, then write the resolved path
        # with every component opened O_NOFOLLOW (open_nofollow); a leaf or
        # ancestor symlink cannot redirect it, and a multi-link fd is refused.
        json_target = os.path.realpath(os.path.abspath(args.json))
        # r38 C2 (r37 named limit: `--record X --json X` overwrote the record when
        # the record lay outside --root): the output must not be the input. Resolved
        # path equality and inode identity both refuse, so a hardlink alias is
        # covered as well as the same spelling.
        record_abs = os.path.realpath(os.path.abspath(args.record))
        alias = record_abs == json_target
        if not alias:
            try:
                rec_st = os.stat(record_abs)
                out_st = os.stat(json_target)
                alias = (rec_st.st_dev, rec_st.st_ino) == (out_st.st_dev, out_st.st_ino)
            except OSError:
                alias = False
        if alias:
            raise Refusal("JSON-IS-RECORD: %s is the record file" % json_target)
        for base in measured:
            try:
                inside = os.path.commonpath([json_target, base]) == base
            except ValueError:
                inside = False
            if inside:
                raise Refusal("JSON-INSIDE-MEASURED-TREE: %s is under %s" % (json_target, base))
        # r37 A2 (wave seat W1CritC2): a hardlink outside --root names an inode
        # inside a measured repository; realpath cannot see it. The fd-level
        # check at write time is race-free (see open_nofollow).
    drift = []
    live_regs = live_prunable = unreachable = 0
    # r36 A4 (wave seat SwarmExecutor22 F1): the old formula len(rows) - absent - unreachable
    # subtracted discovery-only unreachable rows from the recorded count and could go negative.
    live_recorded = 0
    recorded = set()
    for row in rows:
        name = row["name"]
        recorded.add(name)
        path = repo_path(root, name)
        if path is None:
            drift.append(("ABSENT", name, "recorded regs=%d" % row["regs"]))
            continue
        regs, prunable, error = measure(path, args.timeout)
        if error:
            unreachable += 1
            drift.append(("UNREACHABLE", name, error))
            continue
        live_recorded += 1
        live_regs += regs
        live_prunable += prunable
        if regs != row["regs"]:
            drift.append(("REGS-CHANGED", name, "record=%d live=%d" % (row["regs"], regs)))
        if prunable != row["prunable"]:
            drift.append(("PRUNABLE-CHANGED", name, "record=%d live=%d" % (row["prunable"], prunable)))
    if not args.skip_unrecorded:
        for name in discover(root):
            if name not in recorded:
                path = repo_path(root, name)
                if path is None:
                    continue
                regs, prunable, error = measure(path, args.timeout)
                if error:
                    unreachable += 1
                    drift.append(("UNREACHABLE", name, error))
                    continue
                # A6: live_regs/live_prunable describe the RECORD's repositories, exactly like
                # live_repos; an unrecorded repo's figures live on its UNRECORDED row only.
                drift.append(("UNRECORDED", name, "live regs=%d prunable=%d" % (regs, prunable)))
    for cls, name, detail in sorted(drift):
        print("DRIFT\t%s\t%s\t%s" % (cls, name, detail))
    summary = {
        "record": args.record,
        "record_repos": len(rows),
        "record_regs": sum(r["regs"] for r in rows),
        "record_prunable": sum(r["prunable"] for r in rows),
        "live_repos": live_recorded,
        "live_regs": live_regs,
        "live_prunable": live_prunable,
        "drift_rows": len(drift),
        "unreachable": unreachable,
    }
    print(
        "SUMMARY record=%s record_repos=%d record_regs=%d record_prunable=%d live_repos=%d live_regs=%d"
        " live_prunable=%d drift_rows=%d unreachable=%d"
        % (
            summary["record"],
            summary["record_repos"],
            summary["record_regs"],
            summary["record_prunable"],
            summary["live_repos"],
            summary["live_regs"],
            summary["live_prunable"],
            summary["drift_rows"],
            summary["unreachable"],
        )
    )
    if json_target is not None:
        try:
            fd = open_nofollow(json_target)
            st = os.fstat(fd)
            if st.st_nlink > 1:
                os.close(fd)
                raise Refusal("JSON-HARDLINKED: %s has %d links" % (json_target, st.st_nlink))
            # truncate only after the multi-link check: O_TRUNC at open would
            # destroy the very inode the check is meant to protect.
            os.ftruncate(fd, 0)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump({"summary": summary, "drift": [{"class": c, "repo": n, "detail": d} for c, n, d in drift]}, handle, indent=1, sort_keys=True)
                handle.write("\n")
        except Refusal:
            raise
        except OSError as exc:
            raise Refusal("JSON-UNWRITABLE: %s" % exc)
    return 0 if not drift else 1


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--record", required=True)
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--json")
    ap.add_argument("--skip-unrecorded", action="store_true")
    args = ap.parse_args(argv)
    if args.timeout < 1:
        sys.stderr.write("REFUSAL USAGE: --timeout must be >= 1\n")
        return 2
    try:
        return run(args)
    except Refusal as exc:
        sys.stderr.write("REFUSAL %s\n" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
