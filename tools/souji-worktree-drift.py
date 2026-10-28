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
and the live one. It never prunes, never writes inside the measured tree and
never consults the network.

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

Exit: 0 no drift rows, 1 drift rows found, 2 could-not-evaluate
(RECORD-MISSING / RECORD-MALFORMED / RECORD-EMPTY / usage).
"""
import argparse
import json
import os
import re
import subprocess
import sys

SCRUB = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_COMMON_DIR",
    "GIT_NAMESPACE",
    "GIT_PREFIX",
    "GIT_SHALLOW_FILE",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_EXTERNAL_DIFF",
    "GIT_TRACE",
    "GIT_TRACE2",
    "GIT_TRACE2_EVENT",
    "GIT_TRACE2_PERF",
    "GIT_TRACE_PACK_ACCESS",
    "GIT_TRACE_PACKET",
    "GIT_TRACE_PERFORMANCE",
    "GIT_TRACE_SETUP",
    "GIT_TRACE_SHALLOW",
    "GIT_FLUSH",
)
ROW = re.compile(r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d+)\tprunable=(?P<prunable>\d+)$")
TOTAL = re.compile(r"^TOTAL\trepos=(?P<repos>\d+)\tregs=(?P<regs>\d+)\tprunable=(?P<prunable>\d+)$")


class Refusal(Exception):
    pass


def git_env():
    env = dict(os.environ)
    for key in SCRUB:
        env.pop(key, None)
    env["LC_ALL"] = "C"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_TERMINAL_PROMPT"] = "0"
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
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        raise Refusal("RECORD-MISSING: %s" % exc)
    rows = []
    total = None
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
            continue
        raise Refusal("RECORD-MALFORMED: line %d does not match the census schema" % lineno)
    if not rows:
        raise Refusal("RECORD-EMPTY: no REPO rows in %s" % path)
    if total is not None:
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
        if not os.path.isdir(path):
            continue
        if os.path.isdir(os.path.join(path, ".git")) or os.path.isfile(os.path.join(path, ".git")):
            names.append(entry)
    if os.path.isdir(os.path.join(root, ".git")):
        names.insert(0, os.path.basename(root.rstrip("/")) or "root")
    return names


def run(args):
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        raise Refusal("USAGE: --root %s is not a directory" % root)
    if args.json:
        # r36 A2 (wave seat SwarmSentinel24 F1): an --json path inside the measured
        # tree truncated a file the run is supposed to observe. Refuse containment.
        target = os.path.realpath(os.path.abspath(args.json))
        root_real = os.path.realpath(root)
        try:
            inside = os.path.commonpath([target, root_real]) == root_real
        except ValueError:
            inside = False
        if inside:
            raise Refusal("JSON-INSIDE-MEASURED-TREE: %s is under %s" % (target, root_real))
    rows, total = parse_record(args.record)
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
    if args.json:
        try:
            with open(args.json, "w", encoding="utf-8") as handle:
                json.dump({"summary": summary, "drift": [{"class": c, "repo": n, "detail": d} for c, n, d in drift]}, handle, indent=1, sort_keys=True)
                handle.write("\n")
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
