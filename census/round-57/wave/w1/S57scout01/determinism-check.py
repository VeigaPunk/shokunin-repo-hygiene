#!/usr/bin/env python3
"""S57scout01 receipt: fixture-build determinism + base/tip columns vs the v5 dry-run.

Usage: python3 -B determinism-check.py <manifest-a> <manifest-b> <c1-matrix-v5.tsv>
Reads three TSVs; writes nothing. Columns of a build manifest:
    name kind dir base tip record_sha256
C1 matrix columns: fixture counter rev base exit finding findings_all SUMMARY
Rule (census/round-57/fixtures/run-matrix.sh): the matrix `rev` is tip[:12];
the matrix `base` is base[:12] for F5-REWRITE/F6-RECORD-DRIFT/F27-BINARY-NUMSTAT
and tip[:12] otherwise.
"""
import sys

BASE_ARM = {'F5-REWRITE', 'F6-RECORD-DRIFT', 'F27-BINARY-NUMSTAT'}


def rows(path):
    lines = open(path).read().splitlines()
    return [ln.split('\t') for ln in lines[1:] if ln.strip()]


def main(a, b, matrix):
    ma, mb = rows(a), rows(b)
    print('rows a=%d b=%d' % (len(ma), len(mb)))
    assert len(ma) == len(mb)
    diffs = []
    content_diffs = []
    for ra, rb in zip(ma, mb):
        if ra[0] != rb[0]:
            diffs.append((ra[0], rb[0], 'row order/name'))
            continue
        if ra[2] != rb[2]:
            pass  # the dir column is the scratch path by construction
        for i in (1, 3, 4, 5):
            if ra[i] != rb[i]:
                content_diffs.append((ra[0], i, ra[i], rb[i]))
    print('rows whose name/kind/base/tip/record_sha256 differ: %d' % len(content_diffs))
    for d in content_diffs:
        print('CONTENT-DIFF', d)
    m = {r[0]: r for r in rows(matrix)}
    bad = []
    for r in ma:
        if r[1] != 'C1':
            continue
        mr = m.get(r[0])
        if mr is None:
            bad.append((r[0], 'missing in matrix'))
            continue
        want_rev = r[4][:12]
        want_base = (r[3] if r[0] in BASE_ARM else r[4])[:12]
        if mr[2] != want_rev:
            bad.append((r[0], 'rev matrix=%s manifest=%s' % (mr[2], want_rev)))
        if mr[3] != want_base:
            bad.append((r[0], 'base matrix=%s manifest=%s' % (mr[3], want_base)))
    c1 = sum(1 for r in ma if r[1] == 'C1')
    print('C1 rows compared=%d differing=%d' % (c1, len(bad)))
    for x in bad:
        print('BASE-TIP-DIFF', x)
    print('PASS' if not (content_diffs or bad) else 'FAIL')


if __name__ == '__main__':
    main(*sys.argv[1:4])
