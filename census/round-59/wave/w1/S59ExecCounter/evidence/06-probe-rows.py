#!/usr/bin/env python3
"""Isolated-fixture probes of the frozen counter's registry-row selection.

Every git call names the fixture explicitly and the toplevel is asserted before
the first commit. The frozen counter is only read (public CLI), never edited.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
COUNTER = LANE / 'census/round-59/c1-counter.py'
SCRATCH = pathlib.Path('/fast/scratch/hyaku/souji-r59/S59ExecCounter')

B58 = ('| r58 assessment comparison | evidence | `python3 -B census/round-58/c1-counter.py --root LANE --rev FULL40` '
       '| 0 two corrections agree with committed matrix-derived values; 1 discrepancy data or unstructured input error; 2 CLI usage '
       '| external discrimination fixture supplied with the round; counter has no self-invocation certification '
       '| two historical r57 matrices and exact note templates in `census/round-58/c1-counter.py` '
       '| read-only git blobs; no writes | souji |')
G59 = ('| r59 assessment comparison | gate | `python3 -B census/round-59/assessment-gate.py --root LANE --rev FULL40` '
       '| 0 assessment notes agree; 1 mismatch; 2 could-not-evaluate '
       '| `python3 -B census/round-59/assessment-gate.py --selftest --work DIR` '
       '| `census/round-59/preregistration.txt` | read-only git blobs; caller scratch | souji |')

CASES = [
    # name, SKILL.md lines, expected rc, expected findings, intent
    ('dup-r59-identical', [G59, G59], 2, ['REGISTRY-ROW-SHAPE'],
     'two current r59 gate rows: unique-row shape guard fires'),
    ('dup-r59-mixed-kind', [G59, G59.replace('| gate |', '| evidence |')], 2, ['REGISTRY-ROW-SHAPE'],
     'current r59 row plus r59 evidence twin: duplicate still a shape failure, kind is not consulted'),
    ('r59-plus-r58', [G59, B58], 0, [],
     'r59 branch wins and the stale r58 row is not counted (branch precedence)'),
    ('prose-r58-gate-words', [B58 + '\nThis comparator is a gate, not evidence.'], 1, ['REGISTRY-KIND-MISMATCH'],
     'prose claiming gate beside an evidence-kind r58 row: prose is not the kind cell'),
    ('prose-r59-gate-words',
     [G59.replace('| gate |', '| evidence |') + '\nThe word gate appears here and this is called a gate.'], 1,
     ['REGISTRY-KIND-MISMATCH'], 'prose claiming gate beside an evidence-kind r59 row: same, on the current row'),
    ('padded-kind-gate', [G59.replace('| gate |', '|   gate   |')], 0, [],
     'whitespace-padded kind cell still normalizes to gate'),
    ('upper-kind-Gate', [G59.replace('| gate |', '| Gate |')], 1, ['REGISTRY-KIND-MISMATCH'],
     'case-sensitive kind match: Gate is not gate'),
    ('near-miss-prefix', ['|  r59 assessment comparison | gate | x | y | z | p | w | souji |',
                          '| r59 assessment comparison (gate) | gate | x | y | z | p | w | souji |', B58],
     1, ['REGISTRY-KIND-MISMATCH'],
     'near-miss prefixes are invisible: no exact r59 line, base r58 selected and still red'),
    ('short-row-9cells', ['| r59 assessment comparison | gate | x | y | z | p | w |'], 2, ['REGISTRY-ROW-SHAPE'],
     'row with one cell missing is a shape failure'),
    ('no-comparison-row', ['| unrelated | gate | x | y | z | p | w | souji |'], 2, ['REGISTRY-ROW-SHAPE'],
     'no assessment-comparison row at all is a shape failure, not a silent pass'),
    ('fenced-dup-r59', [G59, '```text', G59, '```'], 2, ['REGISTRY-ROW-SHAPE'],
     'a current-looking r59 row inside a fenced block still counts: line scan has no fence model'),
    ('dup-r58-mixed-kind', [B58, B58.replace('| evidence |', '| gate |')], 2, ['REGISTRY-ROW-SHAPE'],
     'fallback branch duplicate: r58 evidence plus r58 gate twin is a shape failure'),
    ('prose-row-wrong-kind', ['| r59 assessment comparison | evidence | `gate` | 0 gate; 1 gate; 2 gate '
                              '| gate | gate | gate | souji |'], 1, ['REGISTRY-KIND-MISMATCH'],
     'gate words saturating every other cell while kind stays evidence: mismatch'),
    ('forged-gate-row', ['| r59 assessment comparison | gate | not a real command | nonsense | unrelated '
                         '| unrelated | nowhere | souji |'], 0, [],
     'classification-only: a fabricated row whose kind cell says gate passes; no execution authentication'),
    ('malformed-r59-plus-valid-r58', ['| r59 assessment comparison | gate | x | y |', B58], 2, ['REGISTRY-ROW-SHAPE'],
     'no fallback rescue: one malformed exact-prefix r59 line poisons the check while a valid r58 row is present'),
]


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def main():
    parent = pathlib.Path(tempfile.mkdtemp(prefix='probes-', dir=SCRATCH))
    results = []
    try:
        r = run(['git', 'init', '-q', str(parent)])
        assert r.returncode == 0, r.stderr
        top = run(['git', '-C', str(parent), 'rev-parse', '--show-toplevel'])
        assert top.returncode == 0 and pathlib.Path(top.stdout.strip()).resolve() == parent.resolve(), top.stdout + top.stderr
        print('FIXTURE-TOPLEVEL ' + top.stdout.strip())
        for k, v in (('user.name', 'souji-fixture'), ('user.email', 'fixture@invalid')):
            assert run(['git', '-C', str(parent), 'config', k, v]).returncode == 0
        for name, lines, exp_rc, exp_ids, intent in CASES:
            (parent / 'SKILL.md').write_text('\n'.join(lines) + '\n')
            assert run(['git', '-C', str(parent), 'add', 'SKILL.md']).returncode == 0
            assert run(['git', '-C', str(parent), 'commit', '-qm', name]).returncode == 0
            rev = run(['git', '-C', str(parent), 'rev-parse', 'HEAD']).stdout.strip()
            cmd = ['python3', '-B', str(COUNTER), '--root', str(parent), '--rev', rev]
            r = run(cmd)
            actual = [ln[len('FINDING '):] for ln in r.stdout.splitlines() if ln.startswith('FINDING ')]
            ok = r.returncode == exp_rc and actual == exp_ids
            results.append(dict(case=name, intent=intent, input_rev=rev, input_skill='\n'.join(lines),
                                command=cmd, expected_rc=exp_rc, expected_findings=exp_ids,
                                rc=r.returncode, findings=actual, stdout=r.stdout, stderr=r.stderr, passed=ok))
            print('CASE %-24s rc=%d exp=%d findings=%s exp=%s %s'
                  % (name, r.returncode, exp_rc, ','.join(actual) or '-', ','.join(exp_ids) or '-',
                     'PASS' if ok else 'FAIL'))
        receipt = dict(fixture_top=str(parent), counter=str(COUNTER), passed=sum(x['passed'] for x in results),
                       total=len(results), cases=results)
        (SCRATCH / 'probe-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print('SUMMARY probes=%d passed=%d failures=%d'
              % (len(results), receipt['passed'], len(results) - receipt['passed']))
        return 0 if receipt['passed'] == len(results) else 1
    finally:
        shutil.rmtree(parent, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
