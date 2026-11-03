#!/usr/bin/env python3
"""souji r57 seat S57mutation01: concrete probes for the surviving C2 mutants,
plus the always-clean-control check (frozen expected untouched).

Every git mutation happens in $S/probe-repo, created here. The frozen expected
file is only ever READ; the mutated copies live in $S/.
"""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

S = Path('/fast/scratch/hyaku/souji-r57/S57mutation01')
BASE = S / 'base' / 'c2-counter.py'
LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
FROZEN_EXP = LANE / 'census/round-57/records/c2-selftest-expected.tsv'
BEFORE_MF = LANE / 'census/round-57/manifests/before.tsv'
ENVV = dict(os.environ, TMPDIR=str(S / 'tmp'))


def sh(*args, cwd=None):
    p = subprocess.run(list(args), cwd=str(cwd) if cwd else None, capture_output=True,
                       text=True, env=ENVV)
    if p.returncode:
        raise SystemExit('probe setup failed: %r rc=%d %s' % (args, p.returncode, p.stderr))
    return p.stdout.strip()


def run(mut, *args):
    exe = BASE if mut == 'pristine' else S / 'mut' / mut / 'c2-counter.py'
    p = subprocess.run([sys.executable, '-B', str(exe)] + list(args),
                       capture_output=True, text=True, env=ENVV)
    body = [ln for ln in p.stdout.splitlines()
            if ln.startswith(('FINDING', 'SUMMARY', 'CANNOT-EVALUATE'))]
    tail = p.stderr.strip().splitlines()[-1:] if p.stderr.strip() else []
    return p.returncode, body, tail


def main():
    repo = S / 'probe-repo'
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    sh('git', '-C', str(repo), 'init', '-q', '-b', 'main')
    assert sh('git', '-C', str(repo), 'rev-parse', '--show-toplevel') == str(repo), 'toplevel'
    sh('git', '-C', str(repo), 'config', 'user.name', 'probe')
    sh('git', '-C', str(repo), 'config', 'user.email', 'probe@example.invalid')
    (repo / 'tools').mkdir()
    (repo / 'tools' / 'instr.py').write_text('# probe instrument v1\n')
    sh('git', '-C', str(repo), 'add', 'tools/instr.py')
    sh('git', '-C', str(repo), 'commit', '-q', '-m', 'A')
    a = sh('git', '-C', str(repo), 'rev-parse', 'HEAD')
    sha_a = hashlib.sha256((repo / 'tools' / 'instr.py').read_bytes()).hexdigest()
    (repo / 'tools' / 'instr.py').write_text('# probe instrument v2\n')
    sh('git', '-C', str(repo), 'add', 'tools/instr.py')
    sh('git', '-C', str(repo), 'commit', '-q', '-m', 'B')
    b = sh('git', '-C', str(repo), 'rev-parse', 'HEAD')
    sh('git', '-C', str(repo), 'tag', 'v1', b)
    sh('git', '-C', str(repo), 'reset', '-q', '--hard', a)
    refs = sh('git', '-C', str(repo), 'for-each-ref', '--format=%(refname)')
    print('# probe repo %s HEAD=%s tag-only rev B=%s refs:' % (repo, a[:12], b[:12]))
    for r in refs.splitlines():
        print('#   ref', r)
    short = a[:12]
    rec = repo / 'receipts'
    rec.mkdir()

    def one(name, body, instrument='-'):
        (rec / name).write_text(body)
        mf = S / 'probe-mf' / (name + '.tsv')
        mf.parent.mkdir(parents=True, exist_ok=True)
        mf.write_text('receipt\tinstrument\nreceipts/%s\t%s\n' % (name, instrument))
        return mf

    # 1. rev reachable only from refs/tags/v1 (durable, no branch)
    mf_tag = one('tag-only.txt', 'rev=%s\nEXIT=0\n' % b)
    # 2. decoy token: sourcerev=<40hex>, no standalone rev=
    mf_decoy = one('decoy.txt', 'sourcerev=%s\nEXIT=0\n' % a)
    # 3. symlink receipt pointing at a clean receipt (manifest names the link,
    #    the link is never written as a file)
    (rec / 'clean.txt').write_text('rev=%s\nEXIT=0\n' % a)
    (rec / 'link.txt').symlink_to('clean.txt')
    mf_link = S / 'probe-mf' / 'link.txt.tsv'
    mf_link.write_text('receipt\tinstrument\nreceipts/link.txt\t-\n')
    # 4. one receipt with TWO findings (short rev + no EXIT line)
    mf_two = one('two.txt', 'rev=%s\nSUMMARY no exit line\n' % short)
    # 5. receipt instrument= disagrees with the manifest instrument column
    mf_name = one('name.txt',
                  'rev=%s\ninstrument=tools/other.py\ninstrument_sha256=%s\nEXIT=0\n' % (a, sha_a),
                  instrument='tools/instr.py')
    # 6. manifest with a 1-column row
    mf_bad = S / 'probe-mf' / 'onecol.tsv'
    mf_bad.write_text('receipt\tinstrument\nreceipts/clean.txt\n')

    probes = [
        ('P1 tag-only rev durable', 'M13-heads-only-durability', mf_tag),
        ('P2 decoy sourcerev= token', 'M16-rev-no-boundary', mf_decoy),
        ('P3 symlinked receipt', 'M8-accept-symlink', mf_link),
        ('P4 two findings in one receipt', 'M17-gate-first-finding-only', mf_two),
        ('P5 instrument name mismatch', 'M18-drop-name-mismatch', mf_name),
        ('P6 one-column manifest row', 'M9-skip-column-check', mf_bad),
    ]
    print()
    for label, mut, mf in probes:
        for arm in ('pristine', mut):
            rc, body, tail = run(arm, '--root', str(repo), '--manifest', str(mf))
            print('PROBE %-32s arm=%-26s rc=%d %s' % (label, arm, rc,
                                                      ' | '.join(body) or '(no lines)'))
            if tail:
                print('        tail: %s' % tail[-1])
    # P7: the frozen before manifest, pristine vs M12 (read-only over the lane)
    print()
    for arm in ('pristine', 'M12-rc-never-fails'):
        rc, body, _ = run(arm, '--root', str(LANE), '--manifest', str(BEFORE_MF))
        print('PROBE P7 before.tsv (frozen manifest)      arm=%-26s rc=%d %s'
              % (arm, rc, ' | '.join(body) or '(no lines)'))

    # control-line check: mutate the EXPECTED file in scratch only
    print()
    exp_orig = FROZEN_EXP.read_text()
    for tag, mut, repl in (
            ('one-nonclean-row-marked-clean', S / 'expected-one-row-clean.tsv',
             exp_orig.replace('MISSING-REV\tRECEIPT-REV-MISSING', 'MISSING-REV\t-')),
            ('all-rows-marked-clean', S / 'expected-all-clean.tsv',
             '\n'.join([ln.split('\t')[0] + '\t-' if i else ln
                        for i, ln in enumerate(exp_orig.splitlines())]))):
        mut.write_text(repl)
        p = subprocess.run([sys.executable, '-B', str(BASE), '--selftest',
                            '--work', str(S / 'work' / ('ctl-' + tag)),
                            '--expected', str(mut)],
                           capture_output=True, text=True, env=ENVV)
        lines = [ln for ln in p.stdout.splitlines() if 'control=' in ln or ln.startswith('SELFTEST fail')]
        print('CONTROL-MUT %-32s expected=%s rc=%d' % (tag, mut.name, p.returncode))
        for ln in lines:
            print('        ' + ln)
    print()
    print('# frozen expected sha256 now', hashlib.sha256(FROZEN_EXP.read_bytes()).hexdigest())
    print('# frozen gate     sha256 now',
          hashlib.sha256((LANE / 'census/round-57/c2-counter.py').read_bytes()).hexdigest())
    return 0


if __name__ == '__main__':
    sys.exit(main())
