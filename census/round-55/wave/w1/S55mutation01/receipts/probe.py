#!/usr/bin/env python3
"""Scratch-only follow-up probes for S55mutation01.

1. C2-17b / C2-18b: the arm name stays in the list but the arm's distinguishing
   input is reverted (passes None instead of the wrong/malformed pin) -- the
   r54 M11 / NL-5 regressions the arms were added to catch.
2. C2-20: a KNOWN receipt key in lowercase (`# receipt_version=1`), the shape
   the frozen C2 prose says is "recognized and validated" (NL-4), has no
   committed fixture; probe pristine vs the C2-15b mutant on a scratch repo.
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
S = pathlib.Path('/fast/scratch/hyaku/souji-r55/S55mutation01')
BUILDER = LANE / 'census/round-55/fixtures/build-fixtures.py'
C2 = LANE / 'census/round-55/c2-counter.py'
EXP2 = LANE / 'census/round-55/records/c2-selftest-expected.tsv'
PIN_BUILDER = 'e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62'
PIN_EXP2 = '63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run_selftest(counter_path, work, tag):
    env = dict(os.environ, TMPDIR=str(S))
    cmd = [sys.executable, '-B', str(counter_path), '--selftest', '--work', str(work),
           '--expected', str(EXP2), '--builder-sha256', PIN_BUILDER,
           '--expected-sha256', PIN_EXP2]
    p = subprocess.run(cmd, capture_output=True, env=env, cwd=str(LANE), timeout=900)
    out = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
    (S / 'mut' / tag / 'selftest.txt').write_text(out)
    return p.returncode, out


def build_mutant(old, new, mid):
    src = C2.read_text()
    n = src.count(old)
    if n != 1:
        raise SystemExit('%s anchor count %d' % (mid, n))
    mdir = S / 'mut' / mid
    if mdir.exists():
        shutil.rmtree(mdir)
    (mdir / 'fixtures').mkdir(parents=True)
    mp = mdir / 'c2-counter.py'
    mp.write_text(src.replace(old, new))
    shutil.copyfile(BUILDER, mdir / 'fixtures' / 'build-fixtures.py')
    return mp


def fixture_probe(pristine_c2, mutant_c2):
    """Known lowercase receipt key on a scratch FH-HONEST clone."""
    spec = importlib.util.spec_from_file_location('r55build', BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src = mod.build_one('FH-HONEST', S / 'probe-fixtures')
    src_dir = pathlib.Path(src['dir'])
    clone = S / 'probe-known-lower'
    if clone.exists():
        shutil.rmtree(clone)
    shutil.copytree(src_dir, clone)
    rc_path = clone / 'census/round-53/records/fleet-root-census-run.txt'
    rec = rc_path.read_text()
    assert '# RECEIPT_VERSION=1' in rec
    rec = rec.replace('# RECEIPT_VERSION=1', '# receipt_version=1')
    # keep the receipt binding valid: recompute CAPTURE_SHA256 unchanged (capture untouched)
    rc_path.write_text(rec)
    e = dict(mod.git_env())
    subprocess.run(['git', '-C', str(clone), 'add', '-A'], env=e, check=True, capture_output=True)
    subprocess.run(['git', '-C', str(clone), 'commit', '-q', '-m', 'probe lowercase known key'],
                   env=e, check=True, capture_output=True)
    tip = subprocess.run(['git', '-C', str(clone), 'rev-parse', 'HEAD'], env=e,
                         check=True, capture_output=True).stdout.decode().strip()
    res = {}
    for label, cnt in (('pristine', pristine_c2), ('mutant-15b', mutant_c2)):
        env = dict(os.environ, TMPDIR=str(S))
        p = subprocess.run([sys.executable, '-B', str(cnt), '--root', str(clone), '--rev', tip,
                            '--capture', 'census/round-52/records/fleet-root-census.tsv',
                            '--receipt', 'census/round-53/records/fleet-root-census-run.txt',
                            '--scratch', str(S)],
                           capture_output=True, env=env, cwd=str(LANE), timeout=120)
        out = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
        (S / 'probe-known-lower' / ('%s-out.txt' % label)).write_text(out)
        res[label] = {'rc': p.returncode,
                      'finding': next((ln.split(' ')[1] for ln in out.splitlines()
                                       if ln.startswith('FINDING ')), '-'),
                      'out': out.strip().splitlines()[-2:]}
    return res


def main():
    out = {}
    # arm-name-removed survivors, recap from the first sweep
    out['sweep_survivors'] = ['C2-15b-key-upper', 'C2-17-fa9-arm-removed', 'C2-18-fb4-arm-removed']
    for mid, old, new in [
        ('C2-17b-fa9-pin-none',
         "            pin = '0' * 64 if name == 'FA9-WRONG-TOOL-PIN' else 'A' * 64",
         "            pin = None if name == 'FA9-WRONG-TOOL-PIN' else 'A' * 64"),
        ('C2-18b-fb4-pin-none',
         "            pin = '0' * 64 if name == 'FA9-WRONG-TOOL-PIN' else 'A' * 64",
         "            pin = '0' * 64 if name == 'FA9-WRONG-TOOL-PIN' else None"),
    ]:
        mp = build_mutant(old, new, mid)
        rc, text = run_selftest(mp, S / 'mut-work' / mid, mid)
        cases = {ln.split(' ')[1]: ln for ln in text.splitlines() if ln.startswith('SELFTEST-CASE ')}
        arm = 'FA9-WRONG-TOOL-PIN' if mid.startswith('C2-17') else 'FB4-PIN-SHAPE'
        out[mid] = {'selftest_rc': rc, 'arm_line': cases.get(arm, 'MISSING'),
                    'mutant_sha': sha(mp.read_bytes())}
        print(mid, 'rc=', rc)
        print('   ', cases.get(arm, 'MISSING'))

    m15b = S / 'mut' / 'C2-15b-key-upper' / 'c2-counter.py'
    probe = fixture_probe(C2, m15b)
    out['C2-20-known-lowercase-key-probe'] = probe
    print('PROBE pristine:', probe['pristine']['rc'], probe['pristine']['finding'])
    print('PROBE mutant  :', probe['mutant-15b']['rc'], probe['mutant-15b']['finding'])
    (S / 'results2.json').write_text(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
