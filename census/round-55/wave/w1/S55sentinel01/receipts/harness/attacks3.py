#!/usr/bin/env python3
"""S55sentinel01 probe: can a byte-level disguise DARKEN A COMMITTED KILL?

Takes the committed r55 fixture shapes (F11-BOGUS-RECOMP, F20-R1-INDENT-SWALLOW,
F21-R1-ONELINE-SWALLOW) and mutates only the correction file's bytes in the
tip commit, to measure whether the committed exit-1 kill survives the disguise.

The frozen builder is imported (never edited); the fixture repos are scratch.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
BUILDER = LANE / 'census/round-55/fixtures/build-fixtures.py'
WORK = Path(sys.argv[1])
OUT = Path(sys.argv[2])

spec = importlib.util.spec_from_file_location('bf', BUILDER)
bf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bf)

ANCHOR = bf.ANCHOR


def sc_lines(value):
    return [
        '# fixture SCORECARD (round-55 C1 matrix, sentinel01 probe)',
        '',
        '| row | note |',
        '|---|---|',
        '| C1 | command `%s` (%d) recomputed below |' % (ANCHOR, value),
    ]


def pre_lines(value):
    return [
        '# fixture preregistration (round-55 C1 matrix, sentinel01 probe)',
        'sites:',
        '`%s` (%d);' % (ANCHOR, value),
    ]


def build(name, sc_val, pre_val, corrections, mutate=None, sep='\n'):
    """base = clean; tip = corrections (optionally mutated)."""
    d = bf.init_repo(WORK, name)
    record = '\n'.join(bf.RECORD_BODY) + '\n'
    bf.write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', record)
    bf.write(d / 'SCORECARD.md', sep.join(sc_lines(sc_val)) + sep)
    bf.write(d / 'census/round-51/preregistration.txt', sep.join(pre_lines(pre_val)))
    base = bf.commit_all(d, 'fixture base', bf.T0)
    tip_corr = list(corrections)
    if mutate:
        tip_corr = mutate(tip_corr)
    text = sep.join(sc_lines(sc_val) + [''] + tip_corr + [''])
    bf.write(d / 'SCORECARD.md', text)
    tip = bf.commit_all(d, 'fixture tip', bf.T1)
    return {'name': name, 'dir': str(d), 'base': base, 'tip': tip,
            'record_sha256': bf.sha256(record.encode()), 'sources_revs': None}


CASES = []


def case(name, sc_val, pre_val, corrections, mutate=None, sep='\n'):
    CASES.append((name, sc_val, pre_val, corrections, mutate, sep))


# --- F11-BOGUS-RECOMP shape: site agrees (79), correction claims recomputed=83
f11 = ['R52-CORRECTION SCORECARD.md:5 stale=79 recomputed=83',
       'R52-CORRECTION census/round-51/preregistration.txt:3 stale=79 recomputed=83']
case('F11-CTRL', 79, 79, f11)
case('F11-NUL-TAIL', 79, 79, f11, lambda c: [x + '\x00' for x in c])
case('F11-NUL-MID', 79, 79, f11, lambda c: [x.replace(' recomputed', '\x00 recomputed') for x in c])

# --- F20-R1-INDENT-SWALLOW shape: 2-space indent, site agrees
f20 = ['  R52-CORRECTION SCORECARD.md:5 stale=79 recomputed=83',
       '  R52-CORRECTION census/round-51/preregistration.txt:3 stale=79 recomputed=83']
case('F20-CTRL', 79, 79, f20)
case('F20-INDENT4', 79, 79, f20, lambda c: ['  ' + x for x in c])
case('F20-TAB', 79, 99, f20, lambda c: ['\t' + x.lstrip(' ') for x in c])

# --- F21-R1-ONELINE-SWALLOW shape: one-line <!-- --> wrapper, site agrees
f21 = ['<!-- R52-CORRECTION SCORECARD.md:5 stale=79 recomputed=83 -->',
       '<!-- R52-CORRECTION census/round-51/preregistration.txt:3 stale=79 recomputed=83 -->']
case('F21-CTRL', 79, 79, f21)
case('F21-NESTED', 79, 99, f21, lambda c: [x.replace('<!-- ', '<!-- <!-- ', 1).replace(' -->', ' --> -->', 1) for x in c])

# --- F4-FENCE shape: corrections inside a fence, site stale (78)
f4 = ['```text',
      'R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79',
      'R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79',
      '```']
case('F4-CTRL', 78, 78, f4)
case('F4-NUL-TAIL', 78, 78, f4, lambda c: [x + '\x00' for x in c])


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name, sc_val, pre_val, corrections, mutate, sep in CASES:
        info = build(name, sc_val, pre_val, corrections, mutate, sep)
        for arm, script in (('v4-r55', 'census/round-55/c1-counter.py'),
                            ('v3-r54', 'census/round-54/c1-counter.py')):
            cmd = ['python3', '-B', script,
                   '--root', info['dir'], '--rev', info['tip'], '--base', info['base'],
                   '--record-sha256', info['record_sha256'], '--scratch', str(WORK)]
            env = dict(os.environ)
            env['TMPDIR'] = str(WORK)
            p = subprocess.run(cmd, cwd=str(LANE), capture_output=True, env=env, timeout=300)
            out = p.stdout.decode('utf-8', 'replace')
            findings = [ln for ln in out.splitlines() if ln.startswith('FINDING ')]
            first = findings[0].split(' ')[1] if findings else '-'
            summ = next((ln for ln in out.splitlines() if ln.startswith('SUMMARY')), '')
            results.append({'fixture': name, 'arm': arm, 'exit': p.returncode,
                            'first_finding': first, 'findings': findings, 'summary': summ,
                            'stdout': out, 'tip': info['tip'], 'base': info['base']})
            print('RESULT %-16s %-7s exit=%d first=%-24s n=%d' %
                  (name, arm, p.returncode, first, len(findings)))
            print('        SUMMARY: %s' % summ[:150])
    (OUT / 'kill-darkening.json').write_text(json.dumps(results, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
