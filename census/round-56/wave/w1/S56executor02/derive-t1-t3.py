#!/usr/bin/env python3
"""Plain-python re-derivation of C2 T1-T3 from two committed matrix TSVs (not the counter)."""
import sys

def rows(path):
    lines = open(path, encoding='utf-8').read().splitlines()
    hdr = lines[0].split('\t')
    out = []
    for ln in lines[1:]:
        if not ln.strip():
            continue
        f = ln.split('\t')
        assert len(f) == 7, (path, ln)
        out.append(dict(zip(hdr, f)))
    return out

def main(base):
    v4 = {r['fixture']: r for r in rows(base + '/c2-matrix-v4.tsv')}
    v5 = {r['fixture']: r for r in rows(base + '/c2-matrix-v5.tsv')}
    print('rows v4=%d v5=%d same-fixture-set=%s' % (len(v4), len(v5), set(v4) == set(v5)))
    t1 = sorted(k for k in v4 if v4[k]['exit'] == '0' and v5[k]['exit'] != '0')
    print('T1 (v4 exit 0, v5 exit != 0): %s' % t1)
    for k in t1:
        print('  T1-FINDING %s v4-finding=%s v5-first-finding=%s' % (k, v4[k]['finding'], v5[k]['finding']))
    t2 = sorted(k for k in v4 if v4[k]['exit'] != '0' and v5[k]['exit'] == '0')
    print('T2 (v4 exit != 0, v5 exit 0): %s' % (t2 if t2 else 'EMPTY'))
    others = sorted(k for k in v4 if k not in t1 and k not in t2)
    bad = [k for k in others if (v4[k]['exit'], v4[k]['finding']) != (v5[k]['exit'], v5[k]['finding'])]
    print('T3 carry-over rows=%d mismatches=%s' % (len(others), bad if bad else 'NONE'))
    allbad = [k for k in v4 if (v4[k]['exit'], v4[k]['finding']) != (v5[k]['exit'], v5[k]['finding'])]
    print('all rows whose (exit, first finding) differ: %s' % allbad)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
