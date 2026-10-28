#!/usr/bin/env python3
"""census/round-40/c1-counter.py — r40 C1 evidence-bound closure counter.

The r39 counter closed an item when one line of the file carried the anchor and every `must` token.
The r39 non-author spot-check (`corpus/lessons/round-39-verifier-spotcheck.md`, defect R40-C1-FORGE)
showed that a line can carry the right tokens and cite nothing: the token predicate is satisfied by a
forged line. The r39 planned r40 row asked for exactly this repair ("bind the C1 items to *evidence*
rather than token presence") and for a register row whose `commit` is older than its `receipt_rev`, so
the commit arm's revision discrimination is exercised in the other direction.

Item rows (`--items`, TSV, header required) — six columns:

  id <TAB> file <TAB> anchor <TAB> must <TAB> mustnot <TAB> evidence

`evidence` is `PATH@REVISION`: a repo-relative path and a 40-hex commit. An item is CLOSED only when
ALL of the following hold at `--rev`:

  1. the file exists at `--rev`;
  2. some line of it carries the anchor, every comma-separated `must` token (whole token, alphanumeric
     boundaries) and no `mustnot` token;
  3. the evidence revision resolves to a commit;
  4. the evidence revision is an ancestor of `--rev` (`git merge-base --is-ancestor`, S251/S244);
  5. the evidence path exists at the evidence revision;
  6. the closing line itself cites the evidence revision (the 40-hex id appears on it).

A token-only line — one that satisfies (1) and (2) but carries no bound evidence pointer — is OPEN
with `EVIDENCE-NOT-BOUND`, and the forged control set (`--forged`) must stay OPEN.

Register leg (`--register`, TSV with the citation reconciler's 8-column schema): every row's `commit`
must be a STRICT DESCENDANT of its `receipt_rev` (resolves, differs from `receipt_rev`, and
`git merge-base --is-ancestor receipt_rev commit` succeeds) and an ancestor of `--rev`. An equal or
backwards commit is a violation, counted in `register_backwards` / `register_notancestor`. The frozen
`tools/souji-citation-reconcile.py` bytes at `--rev` are extracted into a private scratch directory and
run over the register; its `SUMMARY cells= mismatches=` line carries the token verdict.

CLI:
  python3 -B census/round-40/c1-counter.py --root LANE --rev REV --items TSV --register TSV
      [--forged TSV] [--register-rev REV] [--min-cells N] [--min-commit-rows N] [--scratch DIR]

Exit: 0 every real item CLOSED, every forged item OPEN, the register clean and the floors met;
1 any OPEN real item, any forged item that closed, a register mismatch or a backwards/equal commit;
2 usage, malformed input, or an unresolvable revision (could-not-evaluate).
Read-only: `git show`, `git merge-base` and a scratch extraction only; the child git environment is a
whitelist with config discovery neutralised.
"""
import argparse
import hashlib
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


def git(root, args):
    return subprocess.run(
        ["git", "-C", root] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=child_env(),
        check=False,
    )


def git_show(root, rev, path):
    proc = git(root, ["show", "%s:%s" % (rev, path)])
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace")


def git_resolves(root, rev):
    return git(root, ["cat-file", "-e", rev + "^{commit}"]).returncode == 0


def is_ancestor(root, older, newer):
    """True when `older` is an ancestor of `newer` (S251/S244: status 0 = true, 1 = not)."""
    return git(root, ["merge-base", "--is-ancestor", older, newer]).returncode == 0


def has_token(text, token):
    """Whole-token containment: `subcases=21` and `cases=210` are not `cases=21`.

    The boundary rule applies only to an alphanumeric EDGE of the token. A token that ends in
    punctuation (`records=`) must match `records=79`.
    """
    edge_before = token[0].isalnum()
    edge_after = token[-1].isalnum()
    start = 0
    while True:
        idx = text.find(token, start)
        if idx < 0:
            return False
        before = text[idx - 1] if idx > 0 else " "
        after = text[idx + len(token)] if idx + len(token) < len(text) else " "
        if (not edge_before or not before.isalnum()) and (not edge_after or not after.isalnum()):
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
        if parts[:6] == ["id", "file", "anchor", "must", "mustnot", "evidence"]:
            header = True
            continue
        if not header:
            raise ValueError("items %s has no header before line %d" % (path, lineno))
        if len(parts) != 6:
            raise ValueError(
                "items %s line %d has %d fields, expected 6" % (path, lineno, len(parts)))
        row = dict(zip(("id", "file", "anchor", "must", "mustnot", "evidence"), parts))
        if row["id"] in seen:
            raise ValueError("items %s line %d duplicates id %s" % (path, lineno, row["id"]))
        row["must"] = [t for t in row["must"].split(",") if t]
        row["mustnot"] = [] if row["mustnot"] in ("", "-") else [t for t in row["mustnot"].split(",") if t]
        if not row["anchor"] or not row["must"]:
            raise ValueError("items %s line %d has no anchor or no must token" % (path, lineno))
        if "@" not in row["evidence"]:
            raise ValueError(
                "items %s line %d evidence %r is not PATH@REVISION" % (path, lineno, row["evidence"]))
        path_part, _, rev_part = row["evidence"].rpartition("@")
        if not path_part or not REV.match(rev_part):
            raise ValueError(
                "items %s line %d evidence %r has no 40-hex revision" % (path, lineno, row["evidence"]))
        row["evidence_path"] = path_part
        row["evidence_rev"] = rev_part
        seen.add(row["id"])
        rows.append(row)
    if not rows:
        raise ValueError("items %s has no rows" % path)
    return rows


def parse_register(raw):
    """(cell count, commit rows distinct from receipt_rev, distinct commit hashes, rows)."""
    cells = 0
    rows = []
    for line in raw.split("\n"):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if parts[:7] == ["id", "file", "anchor", "expected", "stale", "receipt", "receipt_rev"]:
            continue
        if len(parts) < 7:
            raise ValueError("register row with %d fields" % len(parts))
        cells += 1
        receipt_rev = parts[6]
        commit = parts[7] if len(parts) > 7 else ""
        rows.append((parts[0], receipt_rev, commit))
    distinct_rows = sum(1 for _, receipt_rev, commit in rows if commit and commit != receipt_rev)
    distinct_hashes = len({commit for _, _, commit in rows if commit})
    return cells, distinct_rows, distinct_hashes, rows


def register_leg(root, rev, register, register_rev, scratch):
    """Token verdict from the frozen reconciler bytes at REV, plus the strict-descendant verdict."""
    tool_src = git_show(root, rev, "tools/souji-citation-reconcile.py")
    if tool_src is None:
        raise ValueError("tools/souji-citation-reconcile.py absent at %s" % rev)
    reg_src = git_show(root, register_rev, register)
    if reg_src is None:
        return 0, 0, 0, 0, 0, "REGISTER-ABSENT"
    cells, distinct_rows, distinct_hashes, rows = parse_register(reg_src)
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
        raise ValueError(
            "register leg produced no SUMMARY (rc=%d stderr=%r)"
            % (proc.returncode, proc.stderr[-200:]))
    backwards = 0
    notancestor = 0
    for row_id, receipt_rev, commit in rows:
        if not commit:
            backwards += 1
            print("REGISTER %s BACKWARDS no-commit" % row_id)
            continue
        if not REV.match(commit) or not git_resolves(root, commit):
            backwards += 1
            print("REGISTER %s BACKWARDS commit-unresolvable %s" % (row_id, commit))
            continue
        if commit == receipt_rev:
            backwards += 1
            print("REGISTER %s BACKWARDS commit-equals-receipt_rev %s" % (row_id, commit))
            continue
        if not is_ancestor(root, receipt_rev, commit):
            backwards += 1
            print("REGISTER %s BACKWARDS commit-not-descendant %s" % (row_id, commit))
            continue
        if not is_ancestor(root, commit, rev):
            notancestor += 1
            print("REGISTER %s NOT-ANCESTOR-OF-REV %s" % (row_id, commit))
    return int(match.group(1)), int(match.group(2)), distinct_rows, distinct_hashes, backwards + notancestor, "ok"


def evaluate_item(root, rev, row):
    """Return (closed, reason). `reason` names the first unmet condition."""
    text = git_show(root, rev, row["file"])
    if text is None:
        return False, "FILE-ABSENT"
    hits = [line for line in text.split("\n") if row["anchor"] in line]
    if not hits:
        return False, "ANCHOR-ABSENT"
    good = [
        line for line in hits
        if all(has_token(line, t) for t in row["must"])
        and not any(has_token(line, t) for t in row["mustnot"])
    ]
    if not good:
        missing = [t for t in row["must"] if not any(has_token(line, t) for line in hits)]
        return False, "PREDICATE-MISSING missing=%r hits=%d" % (missing, len(hits))
    evidence_rev = row["evidence_rev"]
    if not git_resolves(root, evidence_rev):
        return False, "EVIDENCE-REV-UNRESOLVED %s" % evidence_rev
    if not is_ancestor(root, evidence_rev, rev):
        return False, "EVIDENCE-NOT-ANCESTOR %s" % evidence_rev
    if git_show(root, evidence_rev, row["evidence_path"]) is None:
        return False, "EVIDENCE-PATH-ABSENT %s@%s" % (row["evidence_path"], evidence_rev)
    if not any(evidence_rev.lower() in line.lower() for line in good):
        return False, "EVIDENCE-NOT-BOUND %s" % evidence_rev
    return True, "CLOSED"


def run(args):
    root = args.root
    if not os.path.isdir(root):
        sys.stderr.write("REFUSAL USAGE: --root %s is not a directory\n" % root)
        return 2
    if not REV.match(args.rev):
        sys.stderr.write("REFUSAL USAGE: --rev must be 40-hex\n")
        return 2
    if not git_resolves(root, args.rev):
        sys.stderr.write(
            "REFUSAL COULD-NOT-EVALUATE: --rev %s does not resolve to a commit\n" % args.rev)
        return 2
    register_rev = args.register_rev or args.rev
    if not REV.match(register_rev) or not git_resolves(root, register_rev):
        sys.stderr.write(
            "REFUSAL COULD-NOT-EVALUATE: --register-rev %s does not resolve\n" % register_rev)
        return 2
    try:
        with open(args.items, encoding="utf-8") as handle:
            items_raw = handle.read()
        items = parse_items(items_raw, args.items)
        forged_raw = ""
        forged = []
        if args.forged:
            with open(args.forged, encoding="utf-8") as handle:
                forged_raw = handle.read()
            forged = parse_items(forged_raw, args.forged)
    except (OSError, ValueError) as exc:
        sys.stderr.write("REFUSAL USAGE: %s\n" % exc)
        return 2
    items_sha = hashlib.sha256(items_raw.encode("utf-8")).hexdigest()[:12]
    forged_sha = hashlib.sha256(forged_raw.encode("utf-8")).hexdigest()[:12] if forged_raw else "-"
    try:
        scratch = tempfile.mkdtemp(
            prefix="souji-r40-c1.", dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp")
    except OSError as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: scratch root unavailable: %s\n" % exc)
        return 2
    open_count = 0
    forged_open = 0
    forged_closed = 0
    try:
        for row in items:
            closed, reason = evaluate_item(root, args.rev, row)
            if closed:
                print("ITEM %s CLOSED" % row["id"])
            else:
                print("ITEM %s OPEN %s" % (row["id"], reason))
                open_count += 1
        for row in forged:
            closed, reason = evaluate_item(root, args.rev, row)
            if closed:
                print("FORGED %s CLOSED (must stay OPEN) %s" % (row["id"], reason))
                forged_closed += 1
            else:
                print("FORGED %s OPEN %s" % (row["id"], reason))
                forged_open += 1
        try:
            cells, mismatches, commit_rows, commit_hashes, violations, note = register_leg(
                root, args.rev, args.register, register_rev, scratch)
        except ValueError as exc:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
            return 2
        print("REGISTER cells=%d mismatches=%d commit_rows=%d commit_hashes=%d violations=%d %s" % (
            cells, mismatches, commit_rows, commit_hashes, violations, note))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("SUMMARY items=%d open=%d forged=%d forged_open=%d forged_closed=%d "
          "register_cells=%d register_mismatches=%d register_violations=%d "
          "commit_rows=%d commit_hashes=%d items_sha=%s forged_sha=%s" % (
              len(items), open_count, len(forged), forged_open, forged_closed,
              cells, mismatches, violations, commit_rows, commit_hashes, items_sha, forged_sha))
    ok = (
        open_count == 0
        and forged_closed == 0
        and cells >= args.min_cells
        and mismatches == 0
        and violations == 0
        and commit_rows >= args.min_commit_rows
    )
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--forged")
    ap.add_argument("--register", required=True)
    ap.add_argument("--register-rev")
    ap.add_argument("--min-cells", type=int, default=1)
    ap.add_argument("--min-commit-rows", type=int, default=1)
    ap.add_argument("--scratch")
    args = ap.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
