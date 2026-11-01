#!/usr/bin/env python3
"""Verify the filed R44 register against its declared historical referents.
This repairs measurement, not historical facts. No new correction credit.
Exit 0 exact complete agreement, 1 findings, 2 unavailable/malformed input.
--register-file selects a caller-owned discrimination fixture, never claim evidence.
--selftest --scratch DIR (r46 C2, prereg amendment): builds isolated synthetic
fixtures under the caller scratch only and asserts the frozen verification
semantics' exit codes and finding identifiers. Default path unchanged.
"""
import argparse
import collections
import contextlib
import hashlib
import io
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

BASE = '55d7af6f5a22340f7a3de1c386e514ababfaa75f'
POP = 'census/round-44/c1-population.tsv'
POP_SHA = '422875449468ae146ef029a4622d8f521f05f570a9b79f90286be03b7b0c1e2c'
REGISTER = 'corpus/lessons/round-44.md'

def git(root, *args):
    e = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL':'C',
         'GIT_CONFIG_NOSYSTEM':'1', 'GIT_CONFIG_GLOBAL':os.devnull,
         'GIT_CONFIG_SYSTEM':os.devnull, 'GIT_NO_REPLACE_OBJECTS':'1',
         'GIT_OPTIONAL_LOCKS':'0', 'GIT_NO_LAZY_FETCH':'1'}
    p = subprocess.run(['git','-C',str(root),*args], capture_output=True, env=e, timeout=60)
    if p.returncode:
        raise ValueError('git input unavailable')
    return p.stdout

def verify(root, rev, register, scratch, pop_sha=POP_SHA, base=BASE, pop_size=70):
    raw = git(root,'show',rev+':'+POP)
    if hashlib.sha256(raw).hexdigest() != pop_sha:
        raise ValueError('population digest')
    rows = [x.split('\t') for x in raw.decode().splitlines()[1:]]
    if len(rows)!=pop_size or any(len(x)!=4 for x in rows):
        raise ValueError('population shape')
    keys = {(int(n),t,c) for n,t,c,_ in rows}
    source = git(root,'show',base+':tools/souji-declared-evidence.py')
    with tempfile.TemporaryDirectory(dir=scratch, prefix='r45-instrument-') as td:
        tool=Path(td)/'instrument.py'; tool.write_bytes(source)
        p=subprocess.run([sys.executable,'-B',str(tool),'--root',str(root),'--rev',base,
                          '--file','SCORECARD.md','--format','tsv'],capture_output=True,
                         env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'TMPDIR':td},timeout=120)
        if p.returncode not in (0,1):
            raise ValueError('derivation instrument unavailable')
    facts={}
    for line in p.stdout.decode().splitlines():
        f=line.split('\t')
        if len(f)>=5 and f[3].startswith('mismatch:'):
            facts[(int(f[0]),f[1],f[3])]=f[4]
    if set(facts)!=keys:
        raise ValueError('population differs from historical instrument')
    files=git(root,'ls-tree','-rz','--name-only',base).decode().split('\0')[:-1]
    sc=git(root,'show',base+':SCORECARD.md').decode().splitlines()
    expected={}
    for n,t,c in keys:
        if c=='mismatch:path-absent':
            candidates=sorted(x for x in files if (x.endswith(t) if '/' in t else x.rsplit('/',1)[-1]==t))
            v=candidates[0] if len(candidates)==1 else ('multi:'+';'.join(candidates) if candidates else 'UNHELD')
        elif c=='mismatch:rev-unresolved':
            ds=[x for x in re.findall(r'[0-9a-f]{64}',sc[n-1]) if x.startswith(t)]
            v='sha256prefix:'+ds[0] if ds else 'UNRESOLVED'
        elif c=='mismatch:digest':
            m=re.fullmatch(r'sha256 is ([0-9a-f]{64})',facts[(n,t,c)])
            if not m: raise ValueError('digest derivation')
            v='sha256:'+m[1]
        else: raise ValueError('unknown class')
        expected[(n,t,c)]=v
    found=collections.defaultdict(list); ids=set(); junk=fenced=duplicate=retracted=0
    fence=None
    for line in register.splitlines():
        fm=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',line)
        if fm:
            run=fm[1]
            if fence is None: fence=(run[0],len(run))
            elif run[0]==fence[0] and len(run)>=fence[1] and not fm[2].strip(): fence=None
            continue
        if line.startswith('RETRACTED-R44 '): retracted+=1; continue
        if not line.lstrip().startswith('CORRECTION-R44 '): continue
        if fence or line[:1].isspace(): fenced+=1; continue
        fs=line.split(); fields={}
        for item in fs[1:]:
            k,sep,v=item.partition('=')
            if not sep or k in fields: junk+=1; break
            fields[k]=v
        else:
            required={'id','file','line','class','stale','derived','rev','scope'}
            if set(fields)!=required or fields['file']!='SCORECARD.md' or fields['rev']!=base or not fields['scope'] or not re.fullmatch(r'R44-\d{2,}',fields['id']) or not fields['line'].isdigit():
                junk+=1; continue
            if fields['id'] in ids: duplicate+=1
            ids.add(fields['id'])
            key=(int(fields['line']),fields['stale'],fields['class'])
            if key not in keys: junk+=1; continue
            found[key].append(fields['derived'])
    missing=sum(k not in found for k in keys)
    duplicate+=sum(len(v)-1 for v in found.values())
    mismatches=sum(any(v!=expected[k] for v in vs) for k,vs in found.items())
    matched=sum(len(found.get(k,[]))==1 and found[k][0]==expected[k] for k in keys)
    print('SUMMARY population=%d unique=%d registered=%d missing=%d derived_mismatches=%d junk=%d fenced=%d duplicate=%d retracted=%d historical_credit=0' %
          (pop_size,len(keys),matched,missing,mismatches,junk,fenced,duplicate,retracted))
    return int(not (matched==len(keys) and missing==mismatches==junk==fenced==duplicate==retracted==0))

# ---------------------------------------------------------------- selftest --
# r46 C2 (prereg census/round-46/preregistration.txt C2). Synthetic fixtures
# live only under the caller scratch: each case builds its own git repo whose
# committed bytes (population, SCORECARD, stub derivation instrument) drive
# the real verify() semantics; register text is passed directly, exactly like
# the --register-file discrimination path. No live lane tree, no network, no
# writes outside scratch. Expected exit codes and finding identifiers are
# pinned in census/round-46/records/c2-selftest-expected.tsv.

STUB_INSTRUMENT = '''#!/usr/bin/env python3
import sys
sep = chr(9); nl = chr(10)
rows = [
    sep.join(['7', 'ghost-a.log', 'S', 'mismatch:path-absent', 'data/ghost-a.log declared absent']),
    sep.join(['8', 'bee1', 'S', 'mismatch:rev-unresolved', 'sha256 prefix declared']),
    sep.join(['9', 'f00d', 'S', 'mismatch:digest', 'sha256 is ' + 'f' * 64]),
]
sys.stdout.write('assertions=3 resolved=0 skipped=0 mismatches=3' + nl)
for r in rows:
    sys.stdout.write(r + nl)
'''

def _syn_commit(repo, message):
    e = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
         'GIT_AUTHOR_NAME': 'selftest', 'GIT_AUTHOR_EMAIL': 'selftest@invalid',
         'GIT_COMMITTER_NAME': 'selftest', 'GIT_COMMITTER_EMAIL': 'selftest@invalid',
         'GIT_CONFIG_NOSYSTEM': '1'}
    p = subprocess.run(['git', '-C', str(repo), '-c', 'init.defaultBranch=master', 'init'],
                       capture_output=True, env=e)
    if p.returncode:
        raise ValueError('fixture init failed')
    for args in (['add', '-A'], ['commit', '-m', message]):
        p = subprocess.run(['git', '-C', str(repo)] + args, capture_output=True, env=e)
        if p.returncode:
            raise ValueError('fixture commit failed: %s' % args[0])
    p = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], capture_output=True, env=e)
    return p.stdout.decode().strip()

def _build_fixture(root):
    root.mkdir(parents=True)
    (root / 'tools').mkdir()
    (root / 'tools' / 'souji-declared-evidence.py').write_text(STUB_INSTRUMENT)
    sha64 = 'bee1' + '234567890abcdef' * 4  # 64 hex, starts with token bee1
    score = ['unused line %d' % i for i in range(1, 7)]
    score.append('line seven references data/ghost-a.log as absent')
    score.append('line eight pins sha256 ' + sha64)
    score.append('unused line 9')
    (root / 'SCORECARD.md').write_text('\n'.join(score) + '\n')
    (root / 'data').mkdir()
    (root / 'data' / 'ghost-a.log').write_text('payload\n')
    (root / 'census').mkdir()
    (root / 'census' / 'round-44').mkdir()
    pop = '\t'.join(['line', 'stale_token', 'class', 'derived']) + '\n'
    pop += '\t'.join(['7', 'ghost-a.log', 'mismatch:path-absent', 'x']) + '\n'
    pop += '\t'.join(['8', 'bee1', 'mismatch:rev-unresolved', 'x']) + '\n'
    pop += '\t'.join(['9', 'f00d', 'mismatch:digest', 'x']) + '\n'
    (root / 'census' / 'round-44' / 'c1-population.tsv').write_text(pop)
    return _syn_commit(root, 'fixture')

def _regrow(ident, line, cls, stale, derived):
    return ('CORRECTION-R44 id=R44-%s file=SCORECARD.md line=%d class=%s '
            'stale=%s derived=%s rev=PENDING scope=selftest'
            % (ident, line, cls, stale, derived))

def _base_rows():
    return [
        _regrow('91', 7, 'mismatch:path-absent', 'ghost-a.log', 'data/ghost-a.log'),
        _regrow('92', 8, 'mismatch:rev-unresolved', 'bee1', 'sha256prefix:' + 'bee1' + '234567890abcdef' * 4),
        _regrow('93', 9, 'mismatch:digest', 'f00d', 'sha256:' + 'f' * 64),
    ]

def _summary_of(stdout_text):
    for line in stdout_text.splitlines():
        if line.startswith('SUMMARY '):
            return line
    return None

def _check(case, expect_exit, expect_summary, got_exit, got_summary, fails):
    if got_exit != expect_exit or (expect_summary is not None and got_summary != expect_summary):
        fails.append('%s: exit %r != %r or summary %r != %r'
                     % (case, got_exit, expect_exit, got_summary, expect_summary))

def selftest(scratch):
    scratch = Path(scratch).resolve()
    if not scratch.is_dir():
        print('REFUSAL external scratch directory required', file=sys.stderr)
        return 2
    cases = 0
    fails = []
    work = Path(tempfile.mkdtemp(prefix='r46-c2-selftest-', dir=str(scratch)))
    expect_ok = ('SUMMARY population=3 unique=3 registered=3 missing=0 '
                 'derived_mismatches=0 junk=0 fenced=0 duplicate=0 retracted=0 '
                 'historical_credit=0')
    # (population=/unique= now derive from pop_size/len(keys); defaults 70/66
    #  keep the frozen default-path stdout byte-identical.)
    # cases 1-7: real verify() in-process over synthetic repos (exit 0/1 semantics)
    plans = [
        ('agreement-exact', None, 0, expect_ok),
        ('missing-one', lambda rows: rows[:2], 1,
         expect_ok.replace('registered=3 missing=0', 'registered=2 missing=1')),
        ('wrong-derived', lambda rows: rows[:2] + [rows[2].replace('sha256:' + 'f' * 64, 'sha256:' + 'e' * 64)], 1,
         expect_ok.replace('registered=3 missing=0 derived_mismatches=0',
                           'registered=2 missing=0 derived_mismatches=1')),
        ('junk-field', lambda rows: rows + [_regrow('94', 7, 'mismatch:path-absent', 'ghost-a.log', 'data/ghost-a.log') + ' EXTRA=x'], 1,
         expect_ok.replace('junk=0', 'junk=1')),
        ('fenced-block', lambda rows: ['```text'] + rows + ['```'], 1,
         expect_ok.replace('registered=3 missing=0', 'registered=0 missing=3').replace('fenced=0', 'fenced=3')),
        ('duplicate-id', lambda rows: rows + [rows[0]], 1,
         expect_ok.replace('registered=3', 'registered=2').replace('duplicate=0', 'duplicate=2')),
        ('retracted-line', lambda rows: ['RETRACTED-R44 id=R44-99'] + rows, 1,
         expect_ok.replace('retracted=0', 'retracted=1')),
    ]
    for name, mutate, expect_exit, expect_summary in plans:
        cases += 1
        repo = work / ('repo-' + name)
        sha = _build_fixture(repo)
        rows = _base_rows() if mutate is None else mutate(_base_rows())
        register_text = '\n'.join(rows).replace('rev=PENDING', 'rev=' + sha)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = verify(repo, sha, register_text, str(work),
                            pop_sha=hashlib.sha256((repo / 'census' / 'round-44' / 'c1-population.tsv').read_bytes()).hexdigest(),
                            base=sha, pop_size=3)
        except (OSError, ValueError, subprocess.SubprocessError, UnicodeError) as ex:
            rc, buf = 2, io.StringIO('REFUSAL ' + str(ex))
        got = _summary_of(buf.getvalue())
        _check(name, expect_exit, expect_summary, rc, got, fails)
    # case 8: population-shape refusal (in-process, frozen 70-shape vs 3-row fixture)
    cases += 1
    repo = work / 'repo-population-shape'
    sha = _build_fixture(repo)
    rows = _base_rows()
    register_text = chr(10).join(rows).replace('rev=PENDING', 'rev=' + sha)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rc = verify(repo, sha, register_text, str(work),
                        pop_sha=hashlib.sha256((repo / 'census' / 'round-44' / 'c1-population.tsv').read_bytes()).hexdigest(),
                        base=sha)
    except (OSError, ValueError, subprocess.SubprocessError, UnicodeError):
        rc = 2
    _check('population-shape', 2, None, rc, 'REFUSAL', fails)
    # case 9: default-path population-digest refusal (subprocess, real main())
    cases += 1
    repo = work / 'repo-digest-refusal'
    sha = _build_fixture(repo)
    p = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--root', str(repo),
                        '--rev', sha, '--scratch', str(work)], capture_output=True, timeout=120)
    _check('digest-refusal', 2, None, p.returncode,
           'REFUSAL' if p.stderr.strip() else None, fails)
    # case 10: malformed rev refusal
    cases += 1
    p = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--root', str(repo),
                        '--rev', 'nope', '--scratch', str(work)], capture_output=True, timeout=120)
    _check('bad-rev', 2, None, p.returncode, 'REFUSAL' if p.stderr.strip() else None, fails)
    # case 11: missing scratch refusal
    cases += 1
    p = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--root', str(repo),
                        '--rev', sha, '--scratch', str(work / 'absent-dir')], capture_output=True, timeout=120)
    _check('scratch-missing', 2, None, p.returncode, 'REFUSAL' if p.stderr.strip() else None, fails)
    print('SUMMARY cases=%d pass=%d fail=%d' % (cases, cases - len(fails), len(fails)))
    for f in fails:
        print('FAIL ' + f)
    return 0 if not fails else 1

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root'); ap.add_argument('--rev')
    ap.add_argument('--scratch'); ap.add_argument('--register-file')
    ap.add_argument('--selftest', action='store_true')
    ns=ap.parse_args()
    if ns.selftest:
        if not ns.scratch:
            print('REFUSAL --selftest requires --scratch', file=sys.stderr); return 2
        return selftest(ns.scratch)
    if not ns.root or not ns.rev or not ns.scratch:
        ap.error('--root, --rev and --scratch are required without --selftest')
    try:
        if not re.fullmatch('[0-9a-f]{40}',ns.rev): raise ValueError('full revision required')
        root=Path(ns.root).resolve(); scratch=Path(ns.scratch).resolve()
        if not scratch.is_dir() or root==scratch or root in scratch.parents:
            raise ValueError('external scratch directory required')
        git(root,'rev-parse','--verify',ns.rev+'^{commit}')
        text=Path(ns.register_file).read_text() if ns.register_file else git(root,'show',ns.rev+':'+REGISTER).decode()
        return verify(root,ns.rev,text,str(scratch))
    except (OSError,ValueError,subprocess.SubprocessError,UnicodeError) as ex:
        print('REFUSAL '+str(ex),file=sys.stderr); return 2

if __name__=='__main__': sys.exit(main())
