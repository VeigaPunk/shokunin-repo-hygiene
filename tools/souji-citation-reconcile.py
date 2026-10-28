#!/usr/bin/env python3
"""souji-citation-reconcile.py — r37 C1 self-assessment citation reconciler.

The r36 non-author spot-check routed one calibration defect class: cells in the
lane's own self-assessment quote after-values that never lived in any committed
receipt (`cases=11`/`cases=9`/`cases=8`/`cases=20` against receipts reading
21/12/9), and their measured-commit cells name a commit where the cited receipt
does not exist.

This counter re-derives one register row per routed cell over committed bytes
only. A row binds when, at the audit revision:

  citation  exactly one line of the named file contains the row's `anchor`;
            that line contains `expected` (as a whole token), names the row's
            `receipt`, and does not contain `stale` (whole token);
  receipt   a line of the receipt blob at `receipt_rev` starts with `SUMMARY`
            and carries `expected` (whole token); the receipt path must differ
            from the citation file.

Register schema (TSV, header line required, ids unique, `stale` mandatory):

  id<TAB>file<TAB>anchor<TAB>expected<TAB>stale<TAB>receipt<TAB>receipt_rev

`--register-rev REV` reads the register from the committed tree at REV instead
of the working file, so the audited register is revision-bound (r37 A1.1).

CLI:
  python3 -B tools/souji-citation-reconcile.py --root LANE --rev REV --register TSV
      [--register-rev REV]

Exit: 0 mismatches=0, 1 any mismatch (one MISMATCH line each), 2 usage /
malformed register / unresolvable revision. Read-only: git show only, no
working-tree reads of the audited files, no writes; the child git environment
is a whitelist with config discovery neutralised (r37 A1.4).
"""
import argparse
import os
import re
import subprocess
import sys

FIELDS = ("id", "file", "anchor", "expected", "stale", "receipt", "receipt_rev")
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


class RegisterError(Exception):
    pass


def git_show(root, rev, path):
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")}
    env.update(GIT_ENV)
    proc = subprocess.run(
        ["git", "-C", root, "show", "%s:%s" % (rev, path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace")


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


def parse_register_text(raw, path):
    rows = []
    seen = set()
    header = False
    for lineno, line in enumerate(raw.split("\n"), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if parts == list(FIELDS):
            header = True
            continue
        if not header:
            raise RegisterError("register %s has no header line before line %d" % (path, lineno))
        if len(parts) != len(FIELDS):
            raise RegisterError("register %s line %d has %d fields, expected %d" % (path, lineno, len(parts), len(FIELDS)))
        row = dict(zip(FIELDS, parts))
        if row["id"] in seen:
            raise RegisterError("register %s line %d duplicates id %s" % (path, lineno, row["id"]))
        if not REV.match(row["receipt_rev"]):
            raise RegisterError("register %s line %d receipt_rev is not 40-hex" % (path, lineno))
        if row["stale"] in ("", "-"):
            raise RegisterError("register %s line %d has no stale token" % (path, lineno))
        if os.path.normpath(row["receipt"]) == os.path.normpath(row["file"]):
            raise RegisterError("register %s line %d points receipt at the citation file" % (path, lineno))
        seen.add(row["id"])
        rows.append(row)
    if not header:
        raise RegisterError("register %s has no header line" % path)
    if not rows:
        raise RegisterError("register %s has no rows" % path)
    return rows


def parse_register(path):
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        raise RegisterError("unreadable register %s: %s" % (path, exc))
    return parse_register_text(raw, path)


def run(args):
    root = args.root
    if not REV.match(args.rev):
        sys.stderr.write("REFUSAL USAGE: --rev must be 40-hex\n")
        return 2
    try:
        # r37 A2.6 (revised, wave seat W1RevPredicate L1): the register is an
        # input, not audited evidence — the cheat W2CritC1 filed (an uncommitted
        # register) is closed by pinning `--register-rev` in every command
        # string, not by a root check that broke the fixture's sibling registers.
        if args.register_rev:
            text = git_show(root, args.register_rev, args.register)
            if text is None:
                raise RegisterError("register %s is not at %s" % (args.register, args.register_rev))
            rows = parse_register_text(text, args.register)
        else:
            rows = parse_register(args.register)
    except RegisterError as exc:
        sys.stderr.write("REFUSAL USAGE: %s\n" % exc)
        return 2
    mismatches = 0
    for row in rows:
        text = git_show(root, args.rev, row["file"])
        if text is None:
            print("MISMATCH %s FILE-ABSENT %s at %s" % (row["id"], row["file"], args.rev))
            mismatches += 1
        else:
            hits = [l for l in text.split("\n") if row["anchor"] in l]
            if len(hits) != 1:
                print("MISMATCH %s ANCHOR-COUNT %s anchor=%r hits=%d" % (row["id"], row["file"], row["anchor"], len(hits)))
                mismatches += 1
            elif not has_token(hits[0], row["expected"]):
                print("MISMATCH %s EXPECTED-MISSING %s expected=%r" % (row["id"], row["file"], row["expected"]))
                mismatches += 1
            elif ("`%s`" % row["receipt"]) not in hits[0]:
                # r37 A1.2 (wave seat W1CritC1): a corrected line that does not
                # name its receipt is prose, not a citation.
                print("MISMATCH %s RECEIPT-UNNAMED %s receipt=%r" % (row["id"], row["file"], row["receipt"]))
                mismatches += 1
            elif has_token(hits[0], row["stale"]):
                print("MISMATCH %s STALE-PRESENT %s stale=%r" % (row["id"], row["file"], row["stale"]))
                mismatches += 1
        receipt = git_show(root, row["receipt_rev"], row["receipt"])
        if receipt is None:
            print("MISMATCH %s RECEIPT-ABSENT %s at %s" % (row["id"], row["receipt"], row["receipt_rev"]))
            mismatches += 1
        else:
            summaries = [l for l in receipt.split("\n") if l.startswith("SUMMARY")]
            if not any(has_token(l, row["expected"]) for l in summaries):
                print("MISMATCH %s RECEIPT-DISAGREES %s expected=%r (no SUMMARY line carries it)" % (row["id"], row["receipt"], row["expected"]))
                mismatches += 1
    print("SUMMARY cells=%d mismatches=%d" % (len(rows), mismatches))
    return 0 if mismatches == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--register", required=True)
    ap.add_argument("--register-rev")
    args = ap.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
