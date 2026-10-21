#!/usr/bin/env python3
"""Read-only r21 census of committed r20 transcript calls and exact oracle set."""
import argparse
import collections
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool', required=True)
    p.add_argument('--transcripts', action='append', required=True)
    p.add_argument('--oracle')
    p.add_argument('--json')
    a = p.parse_args()
    spec = importlib.util.spec_from_file_location('auditor', a.tool)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fleet = '/home/vgpnk/Projects/shokunin'
    lane = fleet + '/souji-shokunin'
    classes = collections.Counter()
    selected = set()
    inputs = {str(Path(a.tool)): hashlib.sha256(Path(a.tool).read_bytes()).hexdigest()}
    calls = files = 0
    for directory in a.transcripts:
        d = Path(directory)
        for path in sorted(d.glob('*.txt')):
            data = path.read_bytes()
            inputs[str(path)] = hashlib.sha256(data).hexdigest()
            count, rows = mod.audit_seat(data.decode('utf-8'), 'scout', '', [], lane, fleet)
            calls += count
            files += 1
            for row in rows:
                classes[row['class']] += 1
                if row['class'] == 'V-READ-ROOT':
                    key = (d.name + '/' + path.name, row['line'], row['tool'])
                    selected.add(key)
                    print('ROW\t%s\t%d\t%s\t%s' % (*key, row.get('target', '')))
    record = {'files': files, 'calls': calls, 'read_root': len(selected), 'classes': dict(sorted(classes.items())), 'inputs': inputs, 'rows': sorted(selected)}
    failed = False
    if a.oracle:
        oracle_bytes = Path(a.oracle).read_bytes()
        inputs[str(Path(a.oracle))] = hashlib.sha256(oracle_bytes).hexdigest()
        rows = list(csv.DictReader(oracle_bytes.decode().splitlines(), delimiter='\t'))
        keys = [(r['path'], int(r['line']), r['tool']) for r in rows]
        if len(set(keys)) != len(keys):
            raise ValueError('duplicate oracle call')
        expected = {k for k, r in zip(keys, rows) if r['label'] == 'FLAG'}
        for row in rows:
            if row['label'] not in ('FLAG', 'OK', 'UNSEEN'):
                raise ValueError('bad oracle label')
        # Every visible read/grep/glob call must be labelled, not only positives.
        observed_calls = set()
        for directory in a.transcripts:
            d = Path(directory)
            for path in sorted(d.glob('*.txt')):
                for n, line in enumerate(path.read_text().splitlines(), 1):
                    m = mod.CALL_RE.match(mod.LINE_NO_RE.sub('', line, count=1))
                    if m and m.group(1) in ('read', 'grep', 'glob'):
                        observed_calls.add((d.name + '/' + path.name, n, m.group(1)))
        missing = observed_calls - set(keys)
        extra = set(keys) - observed_calls
        for k in sorted(selected - expected): print('FP\t%s\t%d\t%s' % k)
        for k in sorted(expected - selected): print('FN\t%s\t%d\t%s' % k)
        for k in sorted(missing): print('UNLABELLED\t%s\t%d\t%s' % k)
        for k in sorted(extra): print('EXTRA-LABEL\t%s\t%d\t%s' % k)
        record['oracle'] = {'tp': len(selected & expected), 'fp': len(selected - expected), 'fn': len(expected - selected), 'labelled': len(keys), 'missing': len(missing), 'extra': len(extra)}
        print('ORACLE\t' + '\t'.join(f'{k}={v}' for k, v in record['oracle'].items()))
        failed = bool(selected ^ expected or missing or extra)
    for name, count in sorted(classes.items()): print(f'CLASS\t{name}\t{count}')
    print(f'SUMMARY\tfiles={files}\tcalls={calls}\tread_root={len(selected)}')
    if a.json:
        with open(a.json, 'x') as out: json.dump(record, out, indent=2, sort_keys=True)
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
