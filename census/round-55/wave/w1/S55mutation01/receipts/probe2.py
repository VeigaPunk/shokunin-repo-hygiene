#!/usr/bin/env python3
"""Re-run the GAP-1 probe with the host-guard toplevel assertion recorded.

Every git mutation in this script runs only inside a scratch fixture repo, and
the repo's toplevel is asserted to equal that directory before the commit.
"""
import hashlib
import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
S = pathlib.Path('/fast/scratch/hyaku/souji-r55/S55mutation01')
BUILDER = LANE / 'census/round-55/fixtures/build-fixtures.py'
C2 = LANE / 'census/round-55/c2-counter.py'


def load_builder():
    spec = importlib.util.spec_from_file_location('r55build2', BUILDER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    mod = load_builder()
    src = mod.build_one('FH-HONEST', S / 'probe-fixtures')
    src_dir = pathlib.Path(src['dir'])
    clone = S / 'probe-known-lower'
    if clone.exists():
        shutil.rmtree(clone)
    shutil.copytree(src_dir, clone)
    env = dict(mod.git_env())
    top = subprocess.run(['git', '-C', str(clone), 'rev-parse', '--show-toplevel'],
                         env=env, check=True, capture_output=True).stdout.decode().strip()
    assert pathlib.Path(top) == clone, (top, clone)
    (S / 'probe-toplevel.txt').write_text(
        'git rev-parse --show-toplevel -> %s\nclone dir               -> %s\nEQUAL\n'
        'source fixture toplevel (builder-asserted) -> %s\n' % (top, clone, src_dir))
    rc_path = clone / 'census/round-53/records/fleet-root-census-run.txt'
    rec = rc_path.read_text()
    assert '# RECEIPT_VERSION=1' in rec
    rc_path.write_text(rec.replace('# RECEIPT_VERSION=1', '# receipt_version=1'))
    subprocess.run(['git', '-C', str(clone), 'add', '-A'], env=env, check=True, capture_output=True)
    subprocess.run(['git', '-C', str(clone), 'commit', '-q', '-m', 'probe lowercase known key'],
                   env=env, check=True, capture_output=True)
    tip = subprocess.run(['git', '-C', str(clone), 'rev-parse', 'HEAD'], env=env,
                         check=True, capture_output=True).stdout.decode().strip()
    # mutant C2-15b rebuilt from committed bytes (scratch only)
    mdir = S / 'mut-probe'
    (mdir / 'fixtures').mkdir(parents=True, exist_ok=True)
    s = C2.read_text()
    old = '            key = kv.group(1).upper()'
    assert s.count(old) == 1
    mp = mdir / 'c2-counter.py'
    mp.write_text(s.replace(old, '            key = kv.group(1)'))
    shutil.copyfile(BUILDER, mdir / 'fixtures' / 'build-fixtures.py')
    print('mutant sha256', hashlib.sha256(mp.read_bytes()).hexdigest())
    for label, cnt in (('pristine', C2), ('mutant-15b', mp)):
        e = dict(os.environ, TMPDIR=str(S))
        p = subprocess.run([sys.executable, '-B', str(cnt), '--root', str(clone), '--rev', tip,
                            '--capture', 'census/round-52/records/fleet-root-census.tsv',
                            '--receipt', 'census/round-53/records/fleet-root-census-run.txt',
                            '--scratch', str(S)],
                           capture_output=True, env=e, cwd=str(LANE), timeout=120)
        out = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
        (S / ('probe-known-lower-%s.txt' % label)).write_text(out)
        f = next((ln.split(' ')[1] for ln in out.splitlines() if ln.startswith('FINDING ')), '-')
        print(label, 'rc=', p.returncode, 'finding=', f)


if __name__ == '__main__':
    main()
