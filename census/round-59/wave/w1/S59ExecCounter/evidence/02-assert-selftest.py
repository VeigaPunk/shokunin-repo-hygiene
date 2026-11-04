#!/usr/bin/env python3
"""Independent assertion of the frozen public selftest receipt.

Does not trust controls.py's own `passed` field: re-derives the four expected
(rc, finding-id) pairs from the controls table read as text, and re-parses the
counter stdout captured by the public `c1-counter.py --selftest` path.
"""
import hashlib
import json
import pathlib
import re
import sys

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SCRATCH = pathlib.Path('/fast/scratch/hyaku/souji-r59/S59ExecCounter')
COUNTER = LANE / 'census/round-59/c1-counter.py'
CONTROLS = LANE / 'census/round-59/controls.py'
PREREG = LANE / 'census/round-59/preregistration.txt'
PREREG_COUNTER_SHA = '2c4d45aab440ef713f22a8d3b210e651d6e7047451cab26f9d4316f5a6451a6d'
BASE = 'da5af55b5ea0a2a38edea05635a13416c698e6e7'

# Literal expectations transcribed from the controls.py case table (name, expected_rc, expected findings).
EXPECTED = {
    'unchanged': (1, ['REGISTRY-KIND-MISMATCH']),
    'prose-forgery': (1, ['REGISTRY-KIND-MISMATCH']),
    'duplicate-forgery': (2, ['REGISTRY-ROW-SHAPE']),
    'positive': (0, []),
}


def findings(stdout):
    return [line[len('FINDING '):] for line in stdout.splitlines() if line.startswith('FINDING ')]


def main():
    failures = []
    checks = [0]

    def check(cond, label, detail=''):
        checks[0] += 1
        print(('ASSERT-OK   ' if cond else 'ASSERT-FAIL ') + label + ((' :: ' + detail) if detail else ''))
        if not cond:
            failures.append(label)

    counter_bytes = COUNTER.read_bytes()
    check(hashlib.sha256(counter_bytes).hexdigest() == PREREG_COUNTER_SHA,
          'counter byte-identical to prereg sha256', hashlib.sha256(counter_bytes).hexdigest())
    check(PREREG_COUNTER_SHA in PREREG.read_text(), 'counter sha256 named in preregistration')
    check(BASE in PREREG.read_text(), 'base revision named in preregistration')

    data = json.loads((SCRATCH / 'selftest.stdout').read_text())
    check(data['base'] == BASE, 'selftest base is the frozen base', data['base'])
    check(data['instrument_sha256'] == PREREG_COUNTER_SHA,
          'selftest instrument sha256 equals prereg', data['instrument_sha256'])
    check(data['passed'] == 4, 'controls self-report passed=4', str(data['passed']))
    check((SCRATCH / 'selftest.stderr').read_text() == '', 'public selftest stderr empty')
    check(sorted(c['case'] for c in data['cases']) == sorted(EXPECTED), 'exactly the four expected case ids')

    for case in data['cases']:
        name = case['case']
        exp_rc, exp_ids = EXPECTED[name]
        actual_ids = findings(case['stdout'])
        check(case['rc'] == exp_rc, name + ' actual rc', str(case['rc']))
        check(actual_ids == exp_ids, name + ' actual findings', repr(actual_ids))
        check(case['expected_rc'] == exp_rc, name + ' declared expected rc', str(case['expected_rc']))
        check(case['expected_findings'] == exp_ids, name + ' declared expected findings', repr(case['expected_findings']))
        check(case['passed'] is True, name + ' controls passed flag')
        check(case['stderr'] == '', name + ' child stderr empty')
        check(case['command'][0] == 'python3' and case['command'][1] == '-B'
              and case['command'][2] == str(COUNTER.resolve()),
              name + ' child command invokes the frozen counter through the public CLI')
        root = pathlib.Path(case['command'][4])
        check(str(root).startswith(str(SCRATCH) + '/controls-'), name + ' fixture root under own scratch', str(root))
        check(re.fullmatch(r'[0-9a-f]{40}', case['input_rev']) is not None,
              name + ' fixture input is a full commit id', case['input_rev'])

    # The same four expectations must literally occur in controls.py's table.
    controls = CONTROLS.read_text()
    for name, rc in [('unchanged', 1), ('prose-forgery', 1), ('duplicate-forgery', 2), ('positive', 0)]:
        pattern = r"\('%s',[^\n]*,\s*%d,\s*\[(.*?)\]\)" % (re.escape(name), rc)
        m = re.search(pattern, controls)
        check(m is not None, name + ' literal row present in controls.py table with rc', str(rc))
        if m:
            ids = re.findall(r"'([A-Z-]+)'", m.group(1))
            check(ids == EXPECTED[name][1], name + ' controls.py literal finding ids', repr(ids))
    check('shutil.rmtree(work)' in controls, 'controls.py removes only its own fixture child')
    check("mkdtemp(prefix='controls-',dir=parent)" in controls, 'controls.py fixture child confined to --work parent')

    print('SUMMARY assertions=%d failures=%d' % (checks[0], len(failures)))
    print('RESULT ' + ('SELFTEST-RECEIPT-CONFIRMED' if not failures else 'SELFTEST-RECEIPT-CONTRADICTED'))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
