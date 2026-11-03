#!/usr/bin/env python3
"""S55sentinel01 attack harness v2 (scratch only, never touches frozen bytes).

Two fixture shapes so that the git-numstat deletion check cannot mask a
lexing observation:

  shape L ("lexing isolation"): SCORECARD.md and the preregistration are
    byte-identical in base and tip; the two commits differ only in the
    record file (one extra REMOVED line, ADDED count unchanged). The
    counter's numstat window therefore reports no deletions and no binary
    entry, so any FINDING observed is purely the lexing/judging surface.

  shape N ("normal"): base is clean, tip carries the probe; a NUL byte makes
    git treat SCORECARD.md as binary, which is itself an observation.
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
SC_SITE_LN = 5
PRE_SITE_LN = 3


def sc_body(value=79):
    return [
        '# fixture SCORECARD (sentinel01 attack surface)',
        '',
        '| row | note |',
        '|---|---|',
        '| C1 | command `%s` (%d) recomputed below |' % (ANCHOR, value),
    ]


def pre_body(value=79):
    return [
        '# fixture preregistration (sentinel01 attack surface)',
        'sites:',
        '`%s` (%d);' % (ANCHOR, value),
    ]


def corr_sc(value=79, recomputed=83, indent='', wrapper=None, inject=None, tail=None):
    body = 'R52-CORRECTION SCORECARD.md:%d stale=%d recomputed=%d' % (SC_SITE_LN, value, recomputed)
    return assemble(body, indent, wrapper, inject, tail)


def corr_pre(value=79, recomputed=83, indent='', wrapper=None, inject=None, tail=None):
    body = 'R52-CORRECTION census/round-51/preregistration.txt:%d stale=%d recomputed=%d' % (
        PRE_SITE_LN, value, recomputed)
    return assemble(body, indent, wrapper, inject, tail)


def assemble(body, indent, wrapper, inject, tail):
    if inject:
        where, what = inject
        body = body.replace(where, where + what, 1)
    line = indent + (wrapper[0] if wrapper else '') + body + (wrapper[1] if wrapper else '')
    if tail:
        line += tail
    return line


def build(name, corrections, shape='L', sep='\n', sc_value=79, pre_value=79, empty_filing=False):
    d = bf.init_repo(WORK, name)
    record_base = '\n'.join(bf.RECORD_BODY) + '\n'
    record_tip = record_base + 'REMOVED\trow-c\n'
    sc_text = sep.join(sc_body(sc_value) + ([''] + corrections + [''] if corrections else ['']))
    pre_text = sep.join(pre_body(pre_value))
    bf.write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', record_base)
    if shape == 'L':
        bf.write(d / 'SCORECARD.md', sc_text)
    else:  # shape N: the probe lands only in the tip commit
        bf.write(d / 'SCORECARD.md', sep.join(sc_body(sc_value) + ['']))
    bf.write(d / 'census/round-51/preregistration.txt', pre_text)
    base = bf.commit_all(d, 'fixture base', bf.T0)
    if shape == 'L':
        # only the record changes; SCORECARD.md is byte-identical base->tip
        bf.write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', record_tip)
    else:  # shape N: the probe lands in the tip commit
        bf.write(d / 'SCORECARD.md', sc_text)
    tip = bf.commit_all(d, 'fixture tip', bf.T1)
    tip_record = record_tip if shape == 'L' else record_base
    return {'name': name, 'dir': str(d), 'base': base, 'tip': tip,
            'record_sha256': bf.sha256(tip_record.encode()), 'sources_revs': None,
            'kind': 'C1'}


CASES = []


def case(name, corrections, **kw):
    CASES.append((name, corrections, kw))


# controls: the shapes v4 is claimed to judge
case('CTL-INDENT2', [corr_sc(indent='  '), corr_pre(indent='  ')])
case('CTL-INDENT3', [corr_sc(indent='   '), corr_pre(indent='   ')])
case('CTL-WRAPPER', [corr_sc(wrapper=('<!-- ', ' -->')), corr_pre(wrapper=('<!-- ', ' -->'))])

# (a) NUL bytes in a correction file
case('P-NUL-TRAILING', [corr_sc(tail='\x00'), corr_pre(tail='\x00')])
case('P-NUL-AFTER-LITERAL', [corr_sc(inject=('R52-CORRECTION', '\x00')),
                              corr_pre(inject=('R52-CORRECTION', '\x00'))])
case('P-NUL-IN-PATH', [corr_sc(inject=('SCORECARD.md', '\x00')),
                       corr_pre(inject=('preregistration.txt', '\x00'))])
case('P-NUL-BEFORE-STALE', [corr_sc(inject=(' stale', '\x00')),
                            corr_pre(inject=(' stale', '\x00'))])
case('P-NUL-SHAPE-N', [corr_sc(tail='\x00'), corr_pre(tail='\x00')], shape='N')

# (b) CR-only correction file (CR line endings, no LF)
case('P-CR-ONLY', [corr_sc(), corr_pre()], sep='\r')
case('P-CR-ONLY-EMPTY', [], sep='\r')

# (c) 4+ leading spaces on the one-line wrapper (outside the {0,3} tolerance)
case('P-INDENT4-WRAPPER', [corr_sc(indent='    ', wrapper=('<!-- ', ' -->')),
                           corr_pre(indent='    ', wrapper=('<!-- ', ' -->'))])
case('P-INDENT4-PLAIN', [corr_sc(indent='    '), corr_pre(indent='    ')])
case('P-TAB-WRAPPER', [corr_sc(indent='\t', wrapper=('<!-- ', ' -->')),
                       corr_pre(indent='\t', wrapper=('<!-- ', ' -->'))])

# (d) one-line wrapper with a nested <!--
case('P-NESTED-COMMENT', [corr_sc(wrapper=('<!-- <!-- ', ' --> -->')),
                           corr_pre(wrapper=('<!-- <!-- ', ' --> -->'))])
case('P-NESTED-COMMENT-3SP', [corr_sc(indent='   ', wrapper=('<!-- <!-- ', ' --> -->')),
                              corr_pre(indent='   ', wrapper=('<!-- <!-- ', ' --> -->'))])

# unnamed-kill-row probe: a stale site with no filing at all
case('P-UNFILED-NO-FINDING', [], sc_value=78, pre_value=78)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name, corrections, kw in CASES:
        info = build(name, corrections, **kw)
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
                            'first_finding': first, 'n_findings': len(findings),
                            'findings': findings, 'summary': summ, 'stdout': out,
                            'stderr': p.stderr.decode('utf-8', 'replace'),
                            'tip': info['tip'], 'base': info['base'], 'dir': info['dir']})
            print('RESULT %-22s %-7s exit=%d first=%-26s n=%d' %
                  (name, arm, p.returncode, first, len(findings)))
    (OUT / 'attack-results.json').write_text(json.dumps(results, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
