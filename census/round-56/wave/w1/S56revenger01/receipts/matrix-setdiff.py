#!/usr/bin/env python3
"""S56revenger01: v4-v5 set comparison from committed dry-run matrices at the
freeze revision cce21b55 (read-only git show). Prints the exact-set targets."""
import subprocess

REV = 'cce21b555a617cadda782613ec1e9d3a0c12ac83'
LANE = '/home/vgpnk/Projects/shokunin/souji-shokunin'


def rows(rev, path):
    txt = subprocess.run(['git', '-C', LANE, 'show', '%s:%s' % (rev, path)],
                         capture_output=True, text=True, check=True).stdout
    out = []
    for ln in txt.split('\n')[1:]:
        if not ln.strip():
            continue
        f = ln.split('\t')
        out.append((f[0], f[4], f[5]))
    return out


for arm in ('c1', 'c2'):
    v4 = {r[0]: r for r in rows(REV, 'census/round-56/records/matrix-dryrun/%s-matrix-v4.tsv' % arm)}
    v5 = {r[0]: r for r in rows(REV, 'census/round-56/records/matrix-dryrun/%s-matrix-v5.tsv' % arm)}
    up = sorted(n for n in v5 if v4[n][1] == '0' and v5[n][1] != '0')
    down = sorted(n for n in v5 if v4[n][1] != '0' and v5[n][1] == '0')
    same = [n for n in v5 if (v4[n][1], v4[n][2]) == (v5[n][1], v5[n][2])]
    finding_changed = [(n, v4[n][1:], v5[n][1:]) for n in v5
                       if v4[n][1] == v5[n][1] and v4[n][2] != v5[n][2]]
    print('%s rows=%d' % (arm, len(v5)))
    print('%s v4-exit0 -> v5-nonzero: %s' % (arm, up))
    print('%s v4-nonzero -> v5-exit0: %s' % (arm, down))
    print('%s identical exit+finding: %d/%d' % (arm, len(same), len(v5)))
    print('%s same-exit finding-changed: %s' % (arm, finding_changed))
