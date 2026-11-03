#!/usr/bin/env python3
"""Scratch-only full-output differential: pristine vs each mutant over every
prebuilt committed fixture (the matrix shape run-matrix.sh records: exit code,
every FINDING line, the SUMMARY line).

Detector A (the committed one) is the counter's selftest, already run.
Detector B (this script) is the wider behavioural detector: it also catches a
mutant that leaves exit code and first finding intact but changes SUMMARY
counts or a later finding.
"""
import importlib.util
import json
import os
import pathlib
import sys
import traceback

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
S = pathlib.Path('/fast/scratch/hyaku/souji-r55/S55mutation01')
MAN = S / 'manifest-a2.tsv'


def load_counter(path, tag):
    spec = importlib.util.spec_from_file_location(tag, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows():
    out = []
    for ln in MAN.read_text().splitlines()[1:]:
        if not ln.strip():
            continue
        f = ln.split('\t')
        out.append(dict(name=f[0], kind=f[1], dir=f[2], base=f[3], tip=f[4], rec=f[5]))
    return out


def run_one(mod, r):
    buf = []
    try:
        if r['kind'] == 'C1':
            bb = r['base'] if r['name'] in ('F5-REWRITE', 'F6-RECORD-DRIFT') else r['tip']
            rc = mod.measure(pathlib.Path(r['dir']), r['tip'], bb, r['rec'],
                             r['tip'], r['tip'], buf)
        else:
            rc = mod.measure(pathlib.Path(r['dir']), r['tip'],
                             'census/round-52/records/fleet-root-census.tsv',
                             'census/round-53/records/fleet-root-census-run.txt', None, buf)
    except Exception:
        return ('EXC', traceback.format_exc().strip().splitlines()[-1], '')
    findings = tuple(ln for ln in buf if ln.startswith('FINDING '))
    summary = next((ln for ln in buf if ln.startswith('SUMMARY ') or ln.startswith('PRISTINE ')), '')
    return (rc, findings, summary)


def main():
    rs = rows()
    pristine = {}
    for kind, path in (('C1', LANE / 'census/round-55/c1-counter.py'),
                       ('C2', LANE / 'census/round-55/c2-counter.py')):
        mod = load_counter(path, 'pristine_' + kind)
        for r in rs:
            if r['kind'] == kind:
                pristine[r['name']] = run_one(mod, r)
    mu = sorted(p.name for p in (S / 'mut').iterdir() if p.is_dir())
    result = {}
    for mid in mu:
        d = sorted((S / 'mut' / mid).glob('*-counter.py'))[0]
        kind = 'C1' if d.name.startswith('c1') else 'C2'
        mod = load_counter(d, mid.replace('-', '_'))
        diffs = {}
        for r in rs:
            if r['kind'] != kind:
                continue
            got = run_one(mod, r)
            if got != pristine[r['name']]:
                diffs[r['name']] = {
                    'pristine': [pristine[r['name']][0], list(pristine[r['name']][1]),
                                 pristine[r['name']][2]],
                    'mutant': [got[0], list(got[1]), got[2]],
                }
        result[mid] = diffs
        print('%-26s full-output diffs: %s' % (mid, sorted(diffs)))
    (S / 'full-output-diffs.json').write_text(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
