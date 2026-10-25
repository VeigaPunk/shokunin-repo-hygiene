#!/usr/bin/env python3
"""Runnable fixture for tools/souji-registry-agreement.py (souji round 29, C1 instrument, amended v2).

Each case is a throwaway git repo under /var/tmp/souji-r29-c1-fixture holding only committed bytes.
Commit 1 is the list-rev (prereg stand-in); commit 2 (optional) is the measured rev. The instrument is
run as `python3 -B <tool> --root <repo> --rev <full40> --list-rev <full40>`; verdicts are compared as
exact output line sets, exit code and SUMMARY counts. K2 cases carry the frozen counter bytes
(`census/round-29/c2-counter.py`, read from the lane next to this fixture), its digest pin and a
three-record r26 manifest, so the derived facts are absent=1 total=3.

Control: an always-zero emitter (`SUMMARY k1=0 k2=0 mismatches=0`, rc 0) passed as --tool must fail
every case that expects a nonzero verdict. Prints `cases=N pass=P control=FALSE-GREEN-REJECTED`;
exit 0 only when P==N and the emitter was rejected by every negative case.
"""
import argparse, hashlib, os, re, shutil, subprocess, sys, tempfile

LANE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
BASE = '/var/tmp/souji-r29-c1-fixture'
DEFAULT_TOOL = os.path.join(LANE, 'tools', 'souji-registry-agreement.py')
COUNTER = os.path.join(LANE, 'census', 'round-29', 'c2-counter.py')
STALE = 'census/round-29/stale-statements.tsv'
HDR = ('# SOURCES fixture\n\n| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |\n'
       '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n')

def srow(sid, used_by, indent=0, tab=False):
    line = f'| {sid} | fixture source | docs | A | scope | anchor | teaches | mined | 2026-10-25 | 365d | {used_by} |'
    return ('\t' if tab else ' ' * indent) + line + '\n'

def entry(sid, body='Body.\n'):
    return f'source: {sid}\n\n# Fixture entry\n\n{body}'

def tsv(path, n, phrase):
    return f'{path}\t{n}\t{phrase}\n'

K2BASE = '# LOG\nstale statement alpha\n'
FIX = 'absent 1 of 3 records, see census/round-26/waves/manifest.sha256'
OK = f'R29-CORRECTION LOG.md:2 {FIX}\n'

def k2case(name, log2, expect, k2n, rc, stale=None):
    return {'name': name, 'rows': [], 'files': {'LOG.md': K2BASE}, 'files2': {'LOG.md': log2},
            'stale': stale or tsv('LOG.md', 2, 'stale statement alpha'), 'expect_rc': rc, 'expect': expect,
            'k1': 0, 'k2': k2n}

CASES = [
    {'name': 'consistent', 'rows': [srow('S001', 'corpus/knowledge/entry-one.md')],
     'files': {'corpus/knowledge/entry-one.md': entry('S001')}, 'expect_rc': 0, 'expect': [], 'k1': 0, 'k2': 0},
    {'name': 'used-by-missing', 'rows': [srow('S002', 'corpus/knowledge/missing.md')], 'files': {},
     'expect_rc': 1, 'expect': ['K1 used-by-missing S002 corpus/knowledge/missing.md'], 'k1': 1, 'k2': 0},
    {'name': 'used-by-no-cite', 'rows': [srow('S003', 'corpus/knowledge/no-cite.md')],
     'files': {'corpus/knowledge/no-cite.md': 'related work, no registry id here\n'},
     'expect_rc': 1, 'expect': ['K1 used-by-no-cite S003 corpus/knowledge/no-cite.md'], 'k1': 1, 'k2': 0},
    {'name': 'cited-not-in-used-by', 'rows': [srow('S004', 'corpus/knowledge/holder.md')],
     'files': {'corpus/knowledge/holder.md': entry('S004'), 'corpus/knowledge/citer.md': entry('S004')},
     'expect_rc': 1, 'expect': ['K1 cited-not-in-used-by S004 corpus/knowledge/citer.md'], 'k1': 1, 'k2': 0},
    {'name': 'cited-no-row', 'rows': [], 'files': {'corpus/knowledge/ghost.md': entry('S005')},
     'expect_rc': 1, 'expect': ['K1 cited-no-row S005 corpus/knowledge/ghost.md'], 'k1': 1, 'k2': 0},
    {'name': 'indent-3-parsed', 'rows': [srow('S008', 'corpus/knowledge/indented-three.md', indent=3)],
     'files': {'corpus/knowledge/indented-three.md': entry('S008')}, 'expect_rc': 0, 'expect': [], 'k1': 0, 'k2': 0},
    {'name': 'indent-4-flagged', 'rows': [srow('S009', 'corpus/knowledge/x.md', indent=4)],
     'files': {'corpus/knowledge/indented-four.md': entry('S009')}, 'expect_rc': 1,
     'expect': ['K1 cited-no-row S009 corpus/knowledge/indented-four.md', 'K1 indented-row S009'], 'k1': 2, 'k2': 0},
    {'name': 'tab-indent-flagged', 'rows': [srow('S010', 'corpus/knowledge/x.md', tab=True)],
     'files': {'corpus/knowledge/tabbed.md': entry('S010')}, 'expect_rc': 1,
     'expect': ['K1 cited-no-row S010 corpus/knowledge/tabbed.md', 'K1 indented-row S010'], 'k1': 2, 'k2': 0},
    {'name': 'source-below-heading-still-counted', 'rows': [srow('S011', 'corpus/knowledge/holder2.md')],
     'files': {'corpus/knowledge/holder2.md': entry('S011'),
               'corpus/knowledge/hider.md': '# Hider\n\nsource: S011\n'},
     'expect_rc': 1, 'expect': ['K1 cited-not-in-used-by S011 corpus/knowledge/hider.md'], 'k1': 1, 'k2': 0},
    {'name': 'row-deleted', 'rows': [srow('S012', 'corpus/knowledge/e12.md'), srow('S013', 'corpus/knowledge/e13.md')],
     'files': {'corpus/knowledge/e12.md': entry('S012'), 'corpus/knowledge/e13.md': entry('S013')},
     'rows2': [srow('S012', 'corpus/knowledge/e12.md')], 'files2': {'corpus/knowledge/e13.md': 'no citation now\n'},
     'expect_rc': 1, 'expect': ['K1 row-deleted S013'], 'k1': 1, 'k2': 0},
    k2case('k2-uncorrected', K2BASE, ['K2 uncorrected-or-unevidenced LOG.md:2'], 1, 1),
    k2case('k2-corrected', K2BASE + OK, [], 0, 0),
    k2case('k2-empty-marker', K2BASE + 'R29-CORRECTION LOG.md:2\n', ['K2 uncorrected-or-unevidenced LOG.md:2'], 1, 1),
    k2case('k2-denial-without-facts', K2BASE + 'R29-CORRECTION LOG.md:2 the statement is fine, see census/round-26/waves/manifest.sha256\n',
           ['K2 uncorrected-or-unevidenced LOG.md:2'], 1, 1),
    k2case('k2-facts-without-source-path', K2BASE + 'R29-CORRECTION LOG.md:2 absent 1 of 3 records\n',
           ['K2 uncorrected-or-unevidenced LOG.md:2'], 1, 1),
    k2case('k2-tag-substring', K2BASE + f'R29-CORRECTION LOG.md:20 {FIX}\n', ['K2 uncorrected-or-unevidenced LOG.md:2'], 1, 1),
    k2case('k2-phrase-edited', '# LOG\nstale statement ALPHA-fixed\n' + OK,
           ['K2 rewrote-not-appended LOG.md', 'K2 statement-moved-or-edited LOG.md:2'], 2, 1),
    {'name': 'k2-marker-before-line', 'rows': [], 'files': {'LOG.md': '# LOG\nstale statement alpha\n'},
     'files2': {'LOG.md': '# LOG\nstale statement alpha\n'}, 'stale': tsv('LOG.md', 2, 'stale statement alpha'),
     'prefix_marker': True, 'expect_rc': 1, 'expect': ['K2 rewrote-not-appended LOG.md', 'K2 statement-moved-or-edited LOG.md:2'],
     'k1': 0, 'k2': 2},
    k2case('k2-statement-duplicated', K2BASE + 'stale statement alpha\n' + OK,
           ['K2 statement-duplicated LOG.md:2'], 1, 1),
    {'name': 'rev-not-40-hex', 'rows': [srow('S001', 'corpus/knowledge/entry-one.md')],
     'files': {'corpus/knowledge/entry-one.md': entry('S001')}, 'rev': 'deadbeef', 'expect_rc': 2, 'expect': [],
     'k1': None, 'k2': None},
]

SUMMARY = re.compile(r'^SUMMARY k1=(\d+) k2=(\d+) mismatches=(\d+)')
EMITTER = '#!/usr/bin/env python3\nimport sys\nprint("SUMMARY k1=0 k2=0 mismatches=0")\nsys.exit(0)\n'

def git(repo, *a):
    p = subprocess.run(['git', '-C', repo, '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false', *a],
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError('git ' + ' '.join(a) + ': ' + p.stderr.strip())
    return p.stdout.strip()

def write(repo, files):
    for rel, body in files.items():
        d = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        with open(d, 'w', encoding='utf-8') as fh:
            fh.write(body)

def build(workdir, case):
    repo = os.path.join(workdir, case['name'])
    os.makedirs(repo)
    subprocess.run(['git', '-C', repo, 'init', '-q'], check=True)
    if git(repo, 'rev-parse', '--show-toplevel') != repo:
        raise RuntimeError('toplevel mismatch for ' + repo)
    git(repo, 'config', 'user.name', 'r29-c1-fixture')
    git(repo, 'config', 'user.email', 'r29-c1-fixture@invalid')
    cbytes = open(COUNTER, 'rb').read()
    files = {'corpus/SOURCES.md': HDR + ''.join(case['rows']), STALE: case.get('stale', ''),
             'census/round-29/c2-counter.py': cbytes.decode(),
             'census/round-29/records/frozen-digests.txt': hashlib.sha256(cbytes).hexdigest() + '  census/round-29/c2-counter.py\n'}
    m = ''.join(f'{"0" * 63}{i}  ./f{i}\n' for i in (1, 2, 3))
    files['census/round-26/waves/manifest.sha256'] = m
    files['census/round-26/waves/f1'] = ''
    files.update(case['files'])
    write(repo, files)
    git(repo, 'add', '-A'); git(repo, 'commit', '-q', '-m', 'fixture list-rev')
    first = git(repo, 'rev-parse', 'HEAD')
    if 'rows2' in case or 'files2' in case:
        f2 = dict(case.get('files2', {}))
        if 'rows2' in case:
            f2['corpus/SOURCES.md'] = HDR + ''.join(case['rows2'])
        if case.get('prefix_marker'):
            f2['LOG.md'] = f'R29-CORRECTION LOG.md:3 {FIX}\n' + '# LOG\nstale statement alpha\n'
        write(repo, f2)
        git(repo, 'add', '-A'); git(repo, 'commit', '-q', '--allow-empty', '-m', 'fixture rev')
    return repo, first, git(repo, 'rev-parse', 'HEAD')

def run(tool, repo, list_rev, rev):
    p = subprocess.run([sys.executable, '-B', tool, '--root', repo, '--rev', rev, '--list-rev', list_rev,
                        '--stale-list', STALE], capture_output=True, text=True, cwd=BASE)
    lines = sorted(x for x in p.stdout.splitlines() if x and not x.startswith('SUMMARY '))
    s = None
    for x in p.stdout.splitlines():
        m = SUMMARY.match(x)
        if m:
            s = tuple(map(int, m.groups()))
    return p.returncode, lines, s, p.stderr

def check(case, r):
    rc, lines, s, err = r
    if rc != case['expect_rc'] or sorted(case['expect']) != lines:
        return False
    if case['k1'] is None:
        return 'COULD-NOT-EVALUATE' in err and s is None
    return s == (case['k1'], case['k2'], case['k1'] + case['k2'])

NEG = [c['name'] for c in CASES if c['expect_rc'] != 0 or c['expect']]

def control(emitter):
    p = subprocess.run([sys.executable, '-B', os.path.abspath(__file__), '--tool', emitter, '--no-control'],
                       capture_output=True, text=True, cwd=BASE)
    failed = set(re.findall(r'^FAIL ([a-z0-9-]+):', p.stderr, re.M))
    m = re.search(r'^cases=(\d+) pass=(\d+)', p.stdout, re.M)
    if not m:
        return False
    missed = [n for n in NEG if n not in failed]
    if missed:
        print('CONTROL FALSE GREEN tolerated by: ' + ', '.join(missed), file=sys.stderr)
    return p.returncode != 0 and int(m.group(1)) == len(CASES) and int(m.group(2)) == len(CASES) - len(NEG) and not missed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tool', default=DEFAULT_TOOL)
    ap.add_argument('--no-control', action='store_true')
    a = ap.parse_args()
    if not os.path.isfile(a.tool):
        print('fixture error: tool not found: ' + a.tool, file=sys.stderr)
        return 2
    os.makedirs(BASE, exist_ok=True)
    work = tempfile.mkdtemp(prefix='c1.', dir=BASE)
    try:
        emitter = os.path.join(work, 'emitter.py')
        open(emitter, 'w').write(EMITTER)
        passed = 0
        for case in CASES:
            repo, first, last = build(work, case)
            r = run(a.tool, repo, first, case.get('rev', last))
            if check(case, r):
                passed += 1
            else:
                print(f'FAIL {case["name"]}: rc={r[0]} summary={r[2]} lines={r[1]} stderr={r[3].strip()[:140]}', file=sys.stderr)
        ok = control(emitter) if not a.no_control else False
        print(f'cases={len(CASES)} pass={passed} control={"FALSE-GREEN-REJECTED" if ok else "TOLERATED"}')
        if a.no_control:
            return 0 if passed == len(CASES) else 1
        return 0 if passed == len(CASES) and ok else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)

if __name__ == '__main__':
    sys.exit(main())
