#!/usr/bin/env python3
"""S55sentinel01 final probe set: exact exploit paths for the NUL-byte and
indented/nested-comment surfaces, plus git-numstat binary-marker evidence."""
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
results = []


def rec(arm, name, p, out, extra=None):
    f = [ln for ln in out.splitlines() if ln.startswith('FINDING ')]
    summ = next((ln for ln in out.splitlines() if ln.startswith('SUMMARY')), '')
    results.append({'probe': name, 'arm': arm, 'exit': p.returncode,
                    'first': f[0].split(' ')[1] if f else '-', 'n': len(f),
                    'findings': f, 'summary': summ, 'stdout': out, 'extra': extra})
    print('RESULT %-30s %-7s exit=%d first=%-26s n=%d' %
          (name, arm, p.returncode, results[-1]['first'], len(f)))
    for ln in f:
        print('      ', ln[:200])
    print('       SUM:', summ[:180])


def build(name, sc_corr, sc_at_base, log_lines=None, registry=True, sc_val=79, pre_val=79):
    """sc_corr = corrections text (may contain NUL). sc_at_base = True -> the
    same SCORECARD.md content is committed in base AND tip (unchanged file)."""
    d = bf.init_repo(WORK, name)
    record = '\n'.join(bf.RECORD_BODY) + '\n'
    bf.write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', record)
    sc = '\n'.join(['# fixture SCORECARD', '', '| row | note |', '|---|---|',
                    '| C1 | command `%s` (%d) recomputed below |' % (ANCHOR, sc_val)]
                   + ([''] + sc_corr + [''] if sc_corr else [''])) + '\n'
    pre = '\n'.join(['# fixture preregistration', 'sites:',
                     '`%s` (%d);' % (ANCHOR, pre_val)]) + '\n'
    bf.write(d / 'SCORECARD.md', sc)
    bf.write(d / 'census/round-51/preregistration.txt', pre)
    if log_lines is not None:
        bf.write(d / 'LOG.md', '\n'.join(log_lines))
    if registry:
        bf.write(d / 'corpus/SOURCES.md', bf.REGISTRY_3ROWS)
    base = bf.commit_all(d, 'fixture base', bf.T0)
    if not sc_at_base:  # rewrite SCORECARD.md so it changes base->tip
        bf.write(d / 'SCORECARD.md', sc.replace('# fixture SCORECARD',
                                                '# fixture SCORECARD (tip)'))
        tip = bf.commit_all(d, 'fixture tip', bf.T1)
    else:
        # unchanged correction file: an EMPTY tip commit, so base..tip has no
        # numstat entry at all and the deletion check cannot speak.
        bf.git(d, 'commit', '-q', '--allow-empty', '-m', 'fixture tip', date=bf.T1)
        tip = bf.git(d, 'rev-parse', 'HEAD', date=bf.T1)
    return d, base, tip, record


def arm_c1(d, base, tip, record, name):
    for arm, script in (('v4-r55', 'census/round-55/c1-counter.py'),
                        ('v3-r54', 'census/round-54/c1-counter.py')):
        cmd = ['python3', '-B', script, '--root', str(d), '--rev', tip, '--base', base,
               '--record-sha256', bf.sha256(record.encode()), '--scratch', str(WORK)]
        env = dict(os.environ); env['TMPDIR'] = str(WORK)
        p = subprocess.run(cmd, cwd=str(LANE), capture_output=True, env=env, timeout=300)
        rec(arm, name, p, p.stdout.decode('utf-8', 'replace'))


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    bogus = ['R52-CORRECTION SCORECARD.md:5 stale=79 recomputed=83',
             'R52-CORRECTION census/round-51/preregistration.txt:3 stale=79 recomputed=83']
    nul = [x + '\x00' for x in bogus]

    # A: bogus correction + NUL, correction file UNCHANGED base->tip
    d, base, tip, rec_ = build('A-NUL-UNCHANGED', nul, True)
    arm_c1(d, base, tip, rec_, 'A-NUL-UNCHANGED')

    # B: same, but SCORECARD.md changes base->tip (git sees it as binary)
    d, base, tip, rec_ = build('B-NUL-CHANGED', nul, False)
    arm_c1(d, base, tip, rec_, 'B-NUL-CHANGED')

    # C: git numstat binary marker, verbatim
    p = subprocess.run(['git', '-C', str(d), 'diff', '--numstat', '--no-renames',
                        '%s..%s' % (base, tip), '--', 'SCORECARD.md'],
                       capture_output=True, text=True)
    print('NUMSTAT-RAW %r' % p.stdout)
    results.append({'probe': 'NUMSTAT-RAW', 'arm': 'git', 'stdout': p.stdout})

    # D: control, no NUL, correction file unchanged base->tip
    d, base, tip, rec_ = build('D-CONTROL-UNCHANGED', bogus, True)
    arm_c1(d, base, tip, rec_, 'D-CONTROL-UNCHANGED')

    # E: NUL byte in LOG.md hiding an overstating SOURCES pair (pair-scan escape)
    d, base, tip, rec_ = build('E-NUL-IN-LOG', [], True,
                               log_lines=['# fixture log',
                                          '- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.\x00',
                                          ''])
    arm_c1(d, base, tip, rec_, 'E-NUL-IN-LOG')

    # F: 4-space-indented <!-- hiding an overstating pair (v4 hidden-pair scan)
    d, base, tip, rec_ = build('F-INDENT4-PAIR-HIDE', [], True,
                               log_lines=['# fixture log', '    <!--',
                                          '- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.', ''])
    arm_c1(d, base, tip, rec_, 'F-INDENT4-PAIR-HIDE')

    # G: control for F (no hidden opener)
    d, base, tip, rec_ = build('G-PAIR-CONTROL', [], True,
                               log_lines=['# fixture log',
                                          '- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.', ''])
    arm_c1(d, base, tip, rec_, 'G-PAIR-CONTROL')

    # H: nested <!-- <!-- hiding an overstating pair
    d, base, tip, rec_ = build('H-NESTED-PAIR-HIDE', [], True,
                               log_lines=['# fixture log', '<!-- <!--',
                                          '- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.', ''])
    arm_c1(d, base, tip, rec_, 'H-NESTED-PAIR-HIDE')

    (OUT / 'probe5.json').write_text(json.dumps(results, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
