#!/usr/bin/env python3
"""C1 counter (souji round 52): declared-count annotation agreement.

Frozen predicate: census/round-52/preregistration.txt, claim C1.
Counts, over an enumerated site list, the pasteable count annotations (`(N)` or
`→ N` after the frozen counting command) whose stated value differs from the
value the command recomputes at the named revision. A mismatch is FILED only when
an append-only correction line `R52-CORRECTION <path>:<line> stale=<N> recomputed=<M>`
exists in SCORECARD.md at the same revision, naming that exact site, the stale
value it reads at that line, and the recomputed value. Anything else is unfiled.

Exit 0: unfiled == 0 and every site resolved.
Exit 1: at least one unfiled mismatch (kill rule / do-nothing control).
Exit 2: could-not-evaluate (bad revision, missing anchor, duplicate anchor).
Reads committed bytes only (git show <rev>:<path>); writes nothing.
"""
import argparse, os, re, subprocess, sys
from pathlib import Path

ANCHOR = 'grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv'
RECORD = 'census/round-51/records/ws-drift-vs-r46.tsv'
SITES = ['SCORECARD.md', 'census/round-51/preregistration.txt']
CORR_FILE = 'SCORECARD.md'
CORR_RE = re.compile(r'^R52-CORRECTION (\S+):(\d+) stale=(\d+) recomputed=(\d+)\s*$', re.M)
ANNOT_RE = re.compile(r'(?:→|\()\s*(\d+)')


def git_show(root, rev, path):
    e = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
         'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
         'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
         'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1'}
    p = subprocess.run(['git', '-C', str(root), 'show', '%s:%s' % (rev, path)],
                       capture_output=True, env=e, timeout=120)
    if p.returncode:
        return None
    return p.stdout.decode('utf-8', 'replace')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', required=True)
    ap.add_argument('--scratch', default=None, help='accepted for interface uniformity; nothing is written')
    ns = ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', ns.rev):
        print('CANNOT-EVALUATE full 40-hex revision required')
        return 2
    root = Path(ns.root).resolve()

    record = git_show(root, ns.rev, RECORD)
    if record is None:
        print('PRISTINE FAIL RECORD-ABSENT %s:%s' % (ns.rev[:12], RECORD))
        return 2
    recomputed = sum(1 for ln in record.splitlines() if ln.startswith('ADDED'))

    corr = git_show(root, ns.rev, CORR_FILE)
    if corr is None:
        print('CANNOT-EVALUATE %s absent at rev' % CORR_FILE)
        return 2
    corr_tuples = {(m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)))
                   for m in CORR_RE.finditer(corr)}

    sites, mism, filed = [], 0, 0
    for path in SITES:
        text = git_show(root, ns.rev, path)
        if text is None:
            print('CANNOT-EVALUATE site absent: %s' % path)
            return 2
        lines = text.splitlines()
        hits = [i for i, ln in enumerate(lines) if ANCHOR in ln]
        if len(hits) != 1:
            print('CANNOT-EVALUATE anchor count %d in %s (want 1)' % (len(hits), path))
            return 2
        idx = hits[0]
        ln = lines[idx]
        window = ln[ln.index(ANCHOR) + len(ANCHOR):][:16]
        m = ANNOT_RE.search(window)
        if not m:
            print('CANNOT-EVALUATE no annotation after anchor in %s:%d' % (path, idx + 1))
            return 2
        stated = int(m.group(1))
        status = 'match' if stated == recomputed else 'mismatch'
        is_filed = (path, idx + 1, stated, recomputed) in corr_tuples
        if status == 'mismatch':
            mism += 1
            if is_filed:
                filed += 1
        print('SITE path=%s line=%d stated=%d recomputed=%d status=%s filed=%s'
              % (path, idx + 1, stated, recomputed, status,
                 'yes' if is_filed else 'no'))
    unfiled = mism - filed
    print('SUMMARY sites=%d mismatches=%d filed=%d unfiled=%d record=%s recomputed=%d rev=%s'
          % (len(SITES), mism, filed, unfiled, RECORD, recomputed, ns.rev[:12]))
    return 0 if unfiled == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
