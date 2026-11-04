#!/usr/bin/env python3
"""S58Scout1 independent enumeration of r57 c1 matrices (read-only over dumped copies)."""
import csv, sys

def load(path):
    with open(path, newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh, delimiter='\t'))

v5 = load('/fast/scratch/hyaku/souji-r58/S58Scout1/matrix-v5.base.tsv')
v6 = load('/fast/scratch/hyaku/souji-r58/S58Scout1/matrix-v6.base.tsv')

print('header_v5_columns=%d header_v6_columns=%d' % (len(v5[0]) if v5 else 0, len(v6[0]) if v6 else 0))
print('rows_v5=%d rows_v6=%d' % (len(v5), len(v6)))

# exit=='0' two ways: positional index 4 (counter's method) and named column
for name, rows in (('v5', v5), ('v6', v6)):
    pos = sum(list(r.values())[4] == '0' for r in rows)
    named = sum(r.get('exit') == '0' for r in rows)
    keys = list(rows[0].keys()) if rows else []
    print('%s exit_zero_positional4=%d exit_zero_named=%d columns=%s' % (name, pos, named, keys))

combined = sum(list(r.values())[4] == '0' for r in v5) + sum(list(r.values())[4] == '0' for r in v6)
print('exit_zero_combined=%d' % combined)

# pairwise identical: exit and findings_all equal (counter predicate), plus full-row equality for context
ident_pair = sum(a['exit'] == b['exit'] and a['findings_all'] == b['findings_all'] for a, b in zip(v5, v6))
ident_full = sum(a == b for a, b in zip(v5, v6))
print('carry_identical_exit+findings_all=%d carry_identical_fullrow=%d' % (ident_pair, ident_full))

# sample mismatching rows for the report
diffs = [(i, a, b) for i, (a, b) in enumerate(zip(v5, v6))
         if not (a['exit'] == b['exit'] and a['findings_all'] == b['findings_all'])]
print('differing_pairwise_rows=%d' % len(diffs))
for i, a, b in diffs[:6]:
    print('  row%d v5.case=%s v5.exit=%s v6.case=%s v6.exit=%s findings_equal=%s' % (
        i, a.get('case'), a['exit'], b.get('case'), b['exit'],
        a['findings_all'] == b['findings_all']))
sys.exit(0)
