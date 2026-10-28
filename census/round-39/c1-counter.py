#!/usr/bin/env python3
"""census/round-39/c1-counter.py — r39 C1 routed-defect closure counter.

The r38 non-author spot-check routed 16 defects (`corpus/lessons/round-38-verifier-spotcheck.md`
## Routed defects). Fifteen are calibration defects: a self-assessment cell states a value or a
completion the observed repo state contradicts. This counter re-derives one predicate per routed
defect from committed bytes only, plus the register arm the r38 limit named (its ten rows all
carried `commit == receipt_rev`, so the live register never exercised the commit arm's revision
discrimination).

Item rows (`--items`, TSV, header required):

  id <TAB> file <TAB> anchor <TAB> must <TAB> mustnot

A row is CLOSED when, at `--rev`, at least one line of `file` contains `anchor`, carries every
comma-separated `must` token (whole token, alphanumeric boundaries) and no `mustnot` token
(`-` = none). A missing file is OPEN FILE-ABSENT.

Register leg (`--register`, TSV with the citation reconciler's 8-column schema): the register blob
at `--register-rev` (default `--rev`) is parsed for its row count and for the rows whose `commit`
differs from `receipt_rev`, and the frozen `tools/souji-citation-reconcile.py` bytes at `--rev` are
extracted into a private scratch directory and run over `--rev`; its `SUMMARY cells=`
`mismatches=` line carries the register verdict.

CLI:
  python3 -B census/round-39/c1-counter.py --root LANE --rev REV --items TSV --register TSV
      [--register-rev REV] [--min-cells N] [--min-commit-distinct N] [--scratch DIR]

Exit: 0 every item CLOSED, register clean and the two register floors met; 1 any OPEN item or
register mismatch/floor; 2 usage, malformed input, or an unresolvable revision (could-not-evaluate).
Read-only: `git show` and a scratch extraction only; the child git environment is a whitelist with
config discovery neutralised.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV = re.compile(r"^[0-9a-f]{40}$")
GIT_ENV = {
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_ATTR_NOSYSTEM": "1",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_TERMINAL_PROMPT": "0",
}


def child_env():
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")}
    env.update(GIT_ENV)
    return env


def git_show(root, rev, path):
    proc = subprocess.run(
        ["git", "-C", root, "show", "%s:%s" % (rev, path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=child_env(),
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace")


def git_resolves(root, rev):
    return (
        subprocess.run(
            ["git", "-C", root, "cat-file", "-e", rev + "^{commit}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=child_env(),
            check=False,
        ).returncode
        == 0
    )


def has_token(text, token):
    """Whole-token containment: `subcases=21` and `cases=210` are not `cases=21`."""
    start = 0
    while True:
        idx = text.find(token, start)
        if idx < 0:
            return False
        before = text[idx - 1] if idx > 0 else " "
        after = text[idx + len(token)] if idx + len(token) < len(text) else " "
        if not before.isalnum() and not after.isalnum():
            return True
        start = idx + 1


def parse_items(raw, path):
    rows = []
    seen = set()
    header = False
    for lineno, line in enumerate(raw.split("\n"), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if parts[:5] == ["id", "file", "anchor", "must", "mustnot"]:
            header = True
            continue
        if not header:
            raise ValueError("items %s has no header before line %d" % (path, lineno))
        if len(parts) != 5:
            raise ValueError("items %s line %d has %d fields, expected 5" % (path, lineno, len(parts)))
        row = dict(zip(("id", "file", "anchor", "must", "mustnot"), parts))
        if row["id"] in seen:
            raise ValueError("items %s line %d duplicates id %s" % (path, lineno, row["id"]))
        row["must"] = [t for t in row["must"].split(",") if t]
        row["mustnot"] = [] if row["mustnot"] in ("", "-") else [t for t in row["mustnot"].split(",") if t]
        if not row["anchor"] or not row["must"]:
            raise ValueError("items %s line %d has no anchor or no must token" % (path, lineno))
        seen.add(row["id"])
        rows.append(row)
    if not rows:
        raise ValueError("items %s has no rows" % path)
    return rows


def parse_register(raw):
    """Row count and the rows whose commit differs from receipt_rev (8-column schema)."""
    cells = 0
    distinct = 0
    for line in raw.split("\n"):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if parts[:7] == ["id", "file", "anchor", "expected", "stale", "receipt", "receipt_rev"]:
            continue
        if len(parts) < 7:
            raise ValueError("register row with %d fields" % len(parts))
        cells += 1
        commit = parts[7] if len(parts) > 7 else ""
        if commit and commit != parts[6]:
            distinct += 1
    return cells, distinct


def register_leg(root, rev, register, register_rev, scratch):
    """Run the frozen citation reconciler bytes at REV over the register; return (cells, mismatches)."""
    tool_src = git_show(root, rev, "tools/souji-citation-reconcile.py")
    if tool_src is None:
        raise ValueError("tools/souji-citation-reconcile.py absent at %s" % rev)
    reg_src = git_show(root, register_rev, register)
    if reg_src is None:
        return 0, 0, "REGISTER-ABSENT"
    cells, distinct = parse_register(reg_src)
    tool = os.path.join(scratch, "citation-reconcile.py")
    with open(tool, "w", encoding="utf-8") as handle:
        handle.write(tool_src)
    proc = subprocess.run(
        [
            "python3", "-B", tool,
            "--root", root,
            "--rev", rev,
            "--register", register,
            "--register-rev", register_rev,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        env={"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch},
    )
    match = re.search(r"^SUMMARY cells=(\d+) mismatches=(\d+)$", proc.stdout, re.M)
    if not match:
        raise ValueError("register leg produced no SUMMARY (rc=%d stderr=%r)" % (proc.returncode, proc.stderr[-200:]))
    return int(match.group(1)), int(match.group(2)), "ok:%d" % distinct


def run(args):
    root = args.root
    if not os.path.isdir(root):
        sys.stderr.write("REFUSAL USAGE: --root %s is not a directory\n" % root)
        return 2
    if not REV.match(args.rev):
        sys.stderr.write("REFUSAL USAGE: --rev must be 40-hex\n")
        return 2
    if not git_resolves(root, args.rev):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev %s does not resolve to a commit\n" % args.rev)
        return 2
    register_rev = args.register_rev or args.rev
    if not REV.match(register_rev) or not git_resolves(root, register_rev):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --register-rev %s does not resolve\n" % register_rev)
        return 2
    try:
        with open(args.items, encoding="utf-8") as handle:
            items_raw = handle.read()
        items = parse_items(items_raw, args.items)
    except ValueError as exc:
        sys.stderr.write("REFUSAL USAGE: %s\n" % exc)
        return 2
    items_sha = __import__("hashlib").sha256(items_raw.encode("utf-8")).hexdigest()[:12]
    try:
        scratch = tempfile.mkdtemp(
            prefix="souji-r39-c1.", dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp")
    except OSError as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: scratch root unavailable: %s\n" % exc)
        return 2
    open_count = 0
    try:
        for row in items:
            text = git_show(root, args.rev, row["file"])
            if text is None:
                print("ITEM %s OPEN FILE-ABSENT %s" % (row["id"], row["file"]))
                open_count += 1
                continue
            hits = [l for l in text.split("\n") if row["anchor"] in l]
            if not hits:
                print("ITEM %s OPEN ANCHOR-ABSENT %s anchor=%r" % (row["id"], row["file"], row["anchor"]))
                open_count += 1
                continue
            good = [
                l for l in hits
                if all(has_token(l, t) for t in row["must"])
                and not any(has_token(l, t) for t in row["mustnot"])
            ]
            if not good:
                missing = [t for t in row["must"] if not any(has_token(l, t) for l in hits)]
                print("ITEM %s OPEN PREDICATE-MISSING %s missing=%r hits=%d" % (
                    row["id"], row["file"], missing, len(hits)))
                open_count += 1
            else:
                print("ITEM %s CLOSED" % row["id"])
        try:
            cells, mismatches, note = register_leg(
                root, args.rev, args.register, register_rev, scratch)
        except ValueError as exc:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
            return 2
        distinct = int(note.split(":")[1]) if note.startswith("ok:") else 0
        print("REGISTER cells=%d mismatches=%d commit_distinct=%d" % (cells, mismatches, distinct))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("SUMMARY items=%d open=%d register_cells=%d register_mismatches=%d commit_distinct=%d items_sha=%s" % (
        len(items), open_count, cells, mismatches, distinct, items_sha))
    ok = (
        open_count == 0
        and cells >= args.min_cells
        and mismatches == 0
        and distinct >= args.min_commit_distinct
    )
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--register", required=True)
    ap.add_argument("--register-rev")
    ap.add_argument("--min-cells", type=int, default=6)
    ap.add_argument("--min-commit-distinct", type=int, default=2)
    ap.add_argument("--scratch")
    args = ap.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
