#!/usr/bin/env python3
"""C2 counter (souji round 47): per-artifact receipts for the four r46
workspace-census candidates (three no-origin-master lane clones and the
foreign helpers-r74 root).

Frozen predicate: census/round-47/preregistration.txt (C2).
Exit 0: the receipt TSV carries exactly the four target rows, every verdict
is NOT-SAFE with a receipt class in the taxonomy's fail-closed/data set and
nonempty evidence. Exit 1: any finding (missing rows, unexpected rows, a
SAFE verdict, unknown class, empty evidence). Exit 2: could-not-evaluate
(usage, unresolvable revision, unreadable inputs).
Reads committed bytes at --rev by default; --file reads a disk TSV (the
junk-arm control mode, never claim evidence). A receipts TSV absent at a
resolvable revision is a finding (RECEIPTS rows=0), not exit 2.
"""
import argparse
import os
import re
import subprocess
import sys

RECEIPTS = 'census/round-47/records/per-artifact-receipts.tsv'
TARGETS = 'census/round-47/c2-targets.tsv'
ALLOWED_CLASSES = {
    'secrets-refusal', 'dirty', 'unpushed-commits-touching',
    'pushed-unverifiable', 'symlink-present', 'unreachable', 'none',
    'stale', 'unpushed-branch', 'metadata-prune',
}


def git(root, *args):
    e = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
         'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
         'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
         'GIT_OPTIONAL_LOCKS': '0'}
    p = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                       env=e, timeout=120)
    if p.returncode:
        raise ValueError('git input unavailable: %s' % args[0])
    return p.stdout


def rows_of(text):
    out = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        out.append(line.split('\t'))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', default=None)
    ap.add_argument('--file', default=None,
                    help='disk TSV (control arms only; never claim evidence)')
    ns = ap.parse_args()
    try:
        root = ns.root
        if ns.file:
            with open(ns.file, 'rb') as fh:
                raw = fh.read().decode('utf-8', 'replace')
            with open(os.path.join(root, TARGETS), 'rb') as fh:
                tgts_raw = fh.read().decode('utf-8', 'replace')
        else:
            if not ns.rev or not re.fullmatch(r'[0-9a-f]{40}', ns.rev):
                raise ValueError('full 40-hex --rev required without --file')
            try:
                raw = git(root, 'show', ns.rev + ':' + RECEIPTS).decode('utf-8', 'replace')
            except ValueError:
                print('RECEIPTS rows=0')
                return 1
            tgts_raw = git(root, 'show', ns.rev + ':' + TARGETS).decode('utf-8', 'replace')
        targets = rows_of(tgts_raw)
        if not targets:
            raise ValueError('targets empty')
        want = {r[1]: r[0] for r in targets[1:]}
        rows = rows_of(raw)
        findings = []
        by_path = {}
        for f in rows:
            if len(f) != 5 or f[0] != 'VERDICT':
                findings.append('MALFORMED-ROW ' + '\\t'.join(f)[:120])
                continue
            by_path[f[1]] = f
        for path, tid in sorted(want.items()):
            f = by_path.get(path)
            if f is None:
                findings.append('MISSING-ROW %s %s' % (tid, path))
                continue
            if f[2] != 'NOT-SAFE':
                findings.append('NOT-NOT-SAFE %s %s' % (tid, f[2]))
            if f[3] not in ALLOWED_CLASSES:
                findings.append('UNKNOWN-CLASS %s %s' % (tid, f[3]))
            if not f[4].strip():
                findings.append('EMPTY-EVIDENCE %s' % tid)
        for path in sorted(set(by_path) - set(want)):
            findings.append('UNEXPECTED-ROW ' + path)
        print('RECEIPTS rows=%d targets=%d findings=%d'
              % (len(rows), len(want), len(findings)))
        for x in findings:
            print('FINDING ' + x)
        return 0 if (not findings and len(rows) == len(want)) else 1
    except (OSError, ValueError, TypeError, subprocess.SubprocessError,
            UnicodeError) as exn:
        print('COULD-NOT-EVALUATE ' + str(exn), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
