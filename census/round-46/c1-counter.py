#!/usr/bin/env python3
"""C1 counter (souji round 46): tip landing-suite receipt — every
declared-evidence mismatch dispositioned, zero unfiled.
Frozen predicate: census/round-46/preregistration.txt (C1).
Exit 0: unfiled=0 (and sanity bounds hold); 1: findings/kill rule; 2: could-not-evaluate.
Never trusts a pre-written receipt: recomputes from the named revision.
"""
import argparse, hashlib, os, re, subprocess, sys
from pathlib import Path

INSTRUMENT = 'tools/souji-declared-evidence.py'
REGISTER_LESSON = 'corpus/lessons/round-44.md'
EXEMPTIONS = 'census/round-46/records/c1-exemptions.tsv'
SCORECARD = 'SCORECARD.md'

def git(root, *args):
    e = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
         'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
         'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
         'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1'}
    p = subprocess.run(['git', '-C', str(root), *args], capture_output=True, env=e, timeout=120)
    if p.returncode:
        raise ValueError('git input unavailable: %s' % args[0])
    return p.stdout

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', required=True)
    ap.add_argument('--work', default=None, help='caller scratch for the instrument run')
    ns = ap.parse_args()
    try:
        if not re.fullmatch(r'[0-9a-f]{40}', ns.rev):
            raise ValueError('full revision required')
        root = Path(ns.root).resolve()
        # dirty-tree kill rule
        st = subprocess.run(['git', '-C', str(root), 'status', '--porcelain'],
                            capture_output=True, env={'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C'},
                            timeout=60)
        if st.returncode or st.stdout.strip():
            raise ValueError('dirty worktree at run time')
        # instrument pin (bytes at the NAMED revision, not the worktree)
        ib = git(root, 'show', ns.rev + ':' + INSTRUMENT)
        pin = hashlib.sha256(ib).hexdigest()
        # run the pinned instrument from committed bytes in a private scratch
        import tempfile
        if ns.work:
            work = Path(ns.work).resolve()
            if not work.is_dir():
                raise ValueError('work dir missing')
            td = tempfile.TemporaryDirectory(dir=str(work), prefix='r46-c1-')
        else:
            td = tempfile.TemporaryDirectory(prefix='r46-c1-')
        with td:
            tool = Path(td.name) / 'instrument.py'
            tool.write_bytes(ib)
            env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
                   'TMPDIR': td.name, 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
                   'GIT_CONFIG_SYSTEM': os.devnull}
            p = subprocess.run([sys.executable, '-B', str(tool), '--root', str(root),
                                '--rev', ns.rev, '--file', SCORECARD, '--format', 'tsv'],
                               capture_output=True, env=env, timeout=300)
            if p.returncode not in (0, 1):
                raise ValueError('instrument could-not-evaluate rc=%d' % p.returncode)
            assertions = resolved = nmis = -1
            mismatches = []
            for line in p.stdout.decode(errors='replace').splitlines():
                f = line.split('\t')
                if len(f) >= 4 and f[1] in ('A', 'S'):
                    if f[2] == 'resolved':
                        resolved += 1
                m = re.match(r'^assertions=(\d+) resolved=(\d+) skipped=\d+ mismatches=(\d+)$', line)
                if m:
                    assertions, resolved, nmis = int(m[1]), int(m[2]), int(m[3])
                if len(f) >= 5 and f[3].startswith('mismatch:'):
                    mismatches.append((int(f[0]), f[1], f[3]))
            if assertions < 0:
                raise ValueError('instrument summary line absent')
            if nmis >= 0 and len(mismatches) != nmis:
                raise ValueError('mismatch row count disagrees with instrument summary')
        # register keys at the named revision
        reg = git(root, 'show', ns.rev + ':' + REGISTER_LESSON).decode()
        regids = {}
        for line in reg.splitlines():
            if line.startswith('CORRECTION-R44 '):
                d = dict(x.split('=', 1) for x in line.split()[1:] if '=' in x)
                regids.setdefault((d['stale'], d['class']), []).append(d['id'])
        # exemptions file (complete rows only)
        ex = {}
        try:
            exraw = git(root, 'show', ns.rev + ':' + EXEMPTIONS).decode()
        except ValueError:
            exraw = None
        if exraw:
            for line in exraw.splitlines():
                if not line or line.startswith('#'):
                    continue
                f = line.split('\t')
                if len(f) == 5 and all(x.strip() for x in f):
                    ex[(f[2], f[3])] = f[0]
        registered = corrected = exempted = unfiled = 0
        for n, t, c in mismatches:
            if (t, c) in regids:
                registered += 1
            elif (t, c) in ex:
                exempted += 1
            else:
                unfiled += 1
        corrected = 0  # no append-only SCORECARD corrections this round
        print('SUMMARY assertions=%d mismatches=%d registered=%d corrected=%d exempted=%d unfiled=%d instrument_sha256=%s'
              % (assertions, len(mismatches), registered, corrected, exempted, unfiled, pin))
        if not (len(mismatches) > 0 and assertions > 500):
            print('SANITY-FAIL', file=sys.stderr)
            return 1
        return 0 if unfiled == 0 else 1
    except (OSError, ValueError, subprocess.SubprocessError, UnicodeError) as exn:
        print('COULD-NOT-EVALUATE ' + str(exn), file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
