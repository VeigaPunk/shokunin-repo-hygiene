#!/usr/bin/env python3
"""Revision-scoped calibration of two r57 SCORECARD assertions; no Markdown visibility claim."""
import argparse
import csv
import io
import subprocess

def measure(root, rev):
    def blob(path):
        return subprocess.check_output(['git', '-C', root, 'show', rev + ':' + path], text=True)
    tables = []
    for arm in ('5', '6'):
        rows = list(csv.DictReader(io.StringIO(blob('census/round-57/records/c1-matrix-v' + arm + '.tsv')), delimiter='\t'))
        tables.append(rows)
    # Positional columns match the committed matrix header, not prose claims.
    values = []
    for rows in tables:
        values.append(sum(list(row.values())[4] == '0' for row in rows))
    identical = sum(a['exit'] == b['exit'] and a['findings_all'] == b['findings_all'] for a, b in zip(*tables))
    text = blob('SCORECARD.md')
    notes = [
        'R58-CALIBRATION carry_identical=' + str(identical) + ' supersedes the r57 SCORECARD claim "all 33 carry-over rows".',
        'R58-CALIBRATION exit_zero=' + ','.join(map(str, values)) + ' counted separately per matrix; the r57 two-file awk command emits the combined total ' + str(sum(values)) + ', not the pair.',
    ]
    mismatches = sum(note not in text for note in notes)
    for note in notes:
        print(('MATCH ' if note in text else 'MISSING ') + note)
    print('SUMMARY assertions=2 mismatches=%d carry_identical=%d exit_zero=%s' % (mismatches, identical, ','.join(map(str, values))))
    return int(bool(mismatches))

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--rev', required=True)
    a = p.parse_args()
    raise SystemExit(measure(a.root, a.rev))
