#!/usr/bin/env python3
"""Runnable fixture for tools/souji-registry-agreement.py (souji round 29, C1 instrument).

Each case is a throwaway git repo under /var/tmp/souji-r29-C1Fixture holding only committed
bytes: corpus/SOURCES.md rows in the 11-column schema, corpus/knowledge/*.md entries with a
front-matter `source:` line, and a stale-list TSV passed through --list-rev/--stale-list. The
instrument is executed as `python3 -B <tool> --root <repo> --rev <full40> --list-rev <full40>
--stale-list census/round-29/stale-statements.tsv`; verdicts are compared as exact output line
sets, exit code and SUMMARY counts.

Cases: (1) consistent -> rc0 mismatches=0; (2) used-by path missing -> used-by-missing;
(3) used-by file without the row id -> used-by-no-cite; (4) entry cites an id whose row does not
list the entry -> cited-not-in-used-by; (5) entry cites an id with no row -> cited-no-row;
(6) 3-space indented row is parsed; (7) 4-space indented row is ignored (indented code);
(8) K2 phrase present without marker -> uncorrected; (9) K2 marker after the line, phrase intact
-> clean; (10) K2 phrase edited in place -> phrase-moved-or-edited; (11) non-40-hex rev -> rc2
COULD-NOT-EVALUATE; (12) marker placed before the stale line does not count.

Control: an always-zero emitter script (`SUMMARY k1=0 k2=0 mismatches=0`, rc 0) is run against
every case that expects a nonzero verdict; if any of those cases tolerates it, the case set is
vacuously green and the fixture fails. Prints
`cases=N pass=P control=FALSE-GREEN-REJECTED` and exits 0 only when P==N and the emitter was
rejected by all negative cases.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

BASE = '/var/tmp/souji-r29-C1Fixture'
DEFAULT_TOOL = '/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-registry-agreement.py'
STALE = 'census/round-29/stale-statements.tsv'

REG_HEADER = (
    '# SOURCES fixture\n\n'
    '| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |\n'
    '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
)


def srow(sid, used_by, indent=0):
    line = (f'| {sid} | fixture source | docs | A | fixture scope | fixture anchor | fixture teaches '
            f'| mined | 2026-10-25 | 365d | {used_by} |')
    return ' ' * indent + line + '\n'


def entry(sid, body='Body.\n'):
    return f'source: {sid}\n\n# Fixture entry\n\n{body}'


def tsv(path, lineno, phrase):
    return f'{path}\t{lineno}\t{phrase}\n'


CASES = [
    {
        'name': 'consistent',
        'rows': [srow('S001', 'corpus/knowledge/entry-one.md')],
        'files': {'corpus/knowledge/entry-one.md': entry('S001')},
        'stale': '',
        'expect_rc': 0,
        'expect': [],
        'k1': 0, 'k2': 0,
    },
    {
        'name': 'used-by-missing',
        'rows': [srow('S002', 'corpus/knowledge/missing.md')],
        'files': {},
        'stale': '',
        'expect_rc': 1,
        'expect': ['K1 used-by-missing S002 corpus/knowledge/missing.md'],
        'k1': 1, 'k2': 0,
    },
    {
        'name': 'used-by-no-cite',
        'rows': [srow('S003', 'corpus/knowledge/no-cite.md')],
        'files': {'corpus/knowledge/no-cite.md': 'related work, no registry id here\n'},
        'stale': '',
        'expect_rc': 1,
        'expect': ['K1 used-by-no-cite S003 corpus/knowledge/no-cite.md'],
        'k1': 1, 'k2': 0,
    },
    {
        'name': 'cited-not-in-used-by',
        'rows': [srow('S004', 'corpus/knowledge/holder.md')],
        'files': {
            'corpus/knowledge/holder.md': entry('S004'),
            'corpus/knowledge/citer.md': entry('S004'),
        },
        'stale': '',
        'expect_rc': 1,
        'expect': ['K1 cited-not-in-used-by S004 corpus/knowledge/citer.md'],
        'k1': 1, 'k2': 0,
    },
    {
        'name': 'cited-no-row',
        'rows': [],
        'files': {'corpus/knowledge/ghost.md': entry('S005')},
        'stale': '',
        'expect_rc': 1,
        'expect': ['K1 cited-no-row S005 corpus/knowledge/ghost.md'],
        'k1': 1, 'k2': 0,
    },
    {
        'name': 'indent-3-parsed',
        'rows': [srow('S008', 'corpus/knowledge/indented-three.md', indent=3)],
        'files': {'corpus/knowledge/indented-three.md': entry('S008')},
        'stale': '',
        'expect_rc': 0,
        'expect': [],
        'k1': 0, 'k2': 0,
    },
    {
        'name': 'indent-4-ignored',
        'rows': [srow('S009', 'corpus/knowledge/does-not-exist.md', indent=4)],
        'files': {'corpus/knowledge/indented-four.md': entry('S009')},
        'stale': '',
        'expect_rc': 1,
        'expect': ['K1 cited-no-row S009 corpus/knowledge/indented-four.md'],
        'k1': 1, 'k2': 0,
    },
    {
        'name': 'k2-uncorrected',
        'rows': [],
        'files': {'LOG.md': '# LOG\nstale statement alpha\n'},
        'stale': tsv('LOG.md', 2, 'stale statement alpha'),
        'expect_rc': 1,
        'expect': ['K2 uncorrected LOG.md:2'],
        'k1': 0, 'k2': 1,
    },
    {
        'name': 'k2-corrected',
        'rows': [],
        'files': {'LOG.md': '# LOG\nstale statement alpha\nR29-CORRECTION LOG.md:2 correction appended, phrase retained\n'},
        'stale': tsv('LOG.md', 2, 'stale statement alpha'),
        'expect_rc': 0,
        'expect': [],
        'k1': 0, 'k2': 0,
    },
    {
        'name': 'k2-phrase-edited',
        'rows': [],
        'files': {'LOG.md': '# LOG\nstale statement ALPHA-fixed\nR29-CORRECTION LOG.md:2 attempted in-place repair\n'},
        'stale': tsv('LOG.md', 2, 'stale statement alpha'),
        'expect_rc': 1,
        'expect': ['K2 phrase-moved-or-edited LOG.md:2'],
        'k1': 0, 'k2': 1,
    },
    {
        'name': 'rev-not-40-hex',
        'rows': [srow('S001', 'corpus/knowledge/entry-one.md')],
        'files': {'corpus/knowledge/entry-one.md': entry('S001')},
        'stale': '',
        'rev': 'deadbeef',
        'expect_rc': 2,
        'expect': [],
        'k1': None, 'k2': None,
    },
    {
        'name': 'k2-marker-before-line',
        'rows': [],
        'files': {'LOG.md': 'R29-CORRECTION LOG.md:3 early marker\n\nstale statement beta\n'},
        'stale': tsv('LOG.md', 3, 'stale statement beta'),
        'expect_rc': 1,
        'expect': ['K2 uncorrected LOG.md:3'],
        'k1': 0, 'k2': 1,
    },
]

SUMMARY = re.compile(r'^SUMMARY k1=(\d+) k2=(\d+) mismatches=(\d+)')
EMITTER = '#!/usr/bin/env python3\nimport sys\nprint("SUMMARY k1=0 k2=0 mismatches=0")\nsys.exit(0)\n'


def git(repo, *args):
    p = subprocess.run(['git', '-C', repo, '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                        *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError('git ' + ' '.join(args) + ': ' + p.stderr.strip())
    return p.stdout


def build_repo(workdir, case):
    repo = os.path.join(workdir, case['name'])
    os.makedirs(repo)
    files = {'corpus/SOURCES.md': REG_HEADER + ''.join(case['rows']), STALE: case['stale']}
    files.update(case['files'])
    for rel, body in files.items():
        dest = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(dest) or repo, exist_ok=True)
        with open(dest, 'w', encoding='utf-8') as fh:
            fh.write(body)
    subprocess.run(['git', '-C', repo, 'init', '-q'], check=True)
    git(repo, 'config', 'user.name', 'r29-c1-fixture')
    git(repo, 'config', 'user.email', 'r29-c1-fixture@invalid')
    git(repo, 'add', '-A')
    git(repo, 'commit', '-q', '-m', 'fixture: ' + case['name'])
    return repo, git(repo, 'rev-parse', 'HEAD').strip()


def run_tool(tool, repo, rev):
    cmd = [sys.executable, '-B', tool, '--root', repo, '--rev', rev,
           '--list-rev', rev, '--stale-list', STALE]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE)
    lines = [x for x in p.stdout.splitlines() if x and not x.startswith('SUMMARY ')]
    summary = None
    for x in p.stdout.splitlines():
        m = SUMMARY.match(x)
        if m:
            summary = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return p.returncode, sorted(lines), summary, p.stderr


def check(case, result):
    rc, lines, summary, stderr = result
    if rc != case['expect_rc']:
        return False
    if sorted(case['expect']) != lines:
        return False
    if case['k1'] is None:
        return 'COULD-NOT-EVALUATE' in stderr and summary is None
    return summary == (case['k1'], case['k2'], case['k1'] + case['k2'])


NEGATIVES = [c['name'] for c in CASES if c['expect_rc'] != 0 or c['expect']]


def control_rejected(emitter):
    """Run this fixture as a child with the always-zero emitter as --tool; the emitter must be
    rejected by every case that expects a nonzero verdict."""
    p = subprocess.run([sys.executable, '-B', os.path.abspath(__file__), '--tool', emitter, '--no-control'],
                       capture_output=True, text=True, cwd=BASE)
    failed = set(re.findall(r'^FAIL ([a-z0-9-]+):', p.stderr, re.M))
    summary = re.search(r'^cases=(\d+) pass=(\d+)', p.stdout, re.M)
    if not summary:
        print('CONTROL child produced no case summary: ' + (p.stdout + p.stderr).strip()[:200],
              file=sys.stderr)
        return False
    total, passed = int(summary.group(1)), int(summary.group(2))
    missed = [n for n in NEGATIVES if n not in failed]
    if missed:
        print('CONTROL FALSE GREEN tolerated by: ' + ', '.join(missed), file=sys.stderr)
    return p.returncode != 0 and total == len(CASES) and passed == len(CASES) - len(NEGATIVES) and not missed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tool', default=DEFAULT_TOOL)
    ap.add_argument('--keep', action='store_true', help='keep the scratch tree')
    ap.add_argument('--no-control', action='store_true', help='skip the false-green control (child mode)')
    a = ap.parse_args()
    if not os.path.isfile(a.tool):
        print('fixture error: tool not found: ' + a.tool, file=sys.stderr)
        return 2
    os.makedirs(BASE, exist_ok=True)
    workdir = tempfile.mkdtemp(prefix='c1-fixture.', dir=BASE)
    passed = 0
    try:
        emitter = os.path.join(workdir, 'false-green-emitter.py')
        with open(emitter, 'w', encoding='utf-8') as fh:
            fh.write(EMITTER)
        os.chmod(emitter, 0o755)
        results = {}
        for case in CASES:
            repo, rev = build_repo(workdir, case)
            use_rev = case.get('rev', rev)
            results[case['name']] = run_tool(a.tool, repo, use_rev)
        for case in CASES:
            if check(case, results[case['name']]):
                passed += 1
            else:
                rc, lines, summary, stderr = results[case['name']]
                print(f'FAIL {case["name"]}: rc={rc} summary={summary} lines={lines} '
                      f'stderr={stderr.strip()[:120]}', file=sys.stderr)
        control_ok = control_rejected(os.path.abspath(emitter)) if not a.no_control else False
        state = 'FALSE-GREEN-REJECTED' if control_ok else 'TOLERATED'
        print(f'cases={len(CASES)} pass={passed} control={state}')
        if a.no_control:
            return 0 if passed == len(CASES) else 1
        return 0 if passed == len(CASES) and control_ok else 1
    finally:
        if a.keep:
            print('scratch kept: ' + workdir, file=sys.stderr)
        else:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
