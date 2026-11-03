#!/usr/bin/env python3
"""S56mutation02 runner: mutant selftest + real-lane probe, then restore.

Detectors
  D1 (selftest): mutant selftest with the committed builder/expected pins.
     PASS iff rc==0 and stdout ends with `SELFTEST pass cases=18`.
  D2 (real lane): mutant counter over census/round-55/records/fleet-root-census.tsv
     at rev cce21b55... with receipt + committed tool pin. PASS iff rc==0 and
     stdout is byte-identical to the pristine counter's output (rl-base.out).
After both runs the mutant counter file is overwritten with the frozen base
bytes and re-hashed; the restore sha256 must equal BASE_SHA.
"""
import hashlib
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path('/fast/scratch/hyaku/souji-r56/S56mutation02')
LANE = '/home/vgpnk/Projects/shokunin/souji-shokunin'
REV = 'cce21b555a617cadda782613ec1e9d3a0c12ac83'
TOOL_SHA = 'e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b'
BUILDER_SHA = '2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a'
EXPECTED_SHA = '90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3'
BASE_SHA = '5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8'
BASE_TREE = ROOT / 'base-tree' / 'census' / 'round-56'
RUN = ROOT / 'run'

MUTANTS = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N10',
           'N11', 'N3N4']


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def run_one(mid):
    tree = ROOT / 'mutants' / mid / 'census' / 'round-56'
    script = tree / 'c2-counter.py'
    env = dict(os.environ)
    env['TMPDIR'] = str(ROOT / 'tmp')
    rec = []
    mut_sha = sha256(script.read_bytes())

    # D1: selftest
    p = subprocess.run(
        [sys.executable, '-B', str(script), '--selftest',
         '--work', str(ROOT / ('st-' + mid)),
         '--builder-sha256', BUILDER_SHA, '--expected-sha256', EXPECTED_SHA],
        capture_output=True, text=True, env=env, cwd=str(ROOT), timeout=1800)
    (RUN / ('%s-selftest.out' % mid)).write_text(p.stdout + p.stderr + 'EXIT=%d\n' % p.returncode)
    d1_pass = (p.returncode == 0 and 'SELFTEST pass cases=18' in p.stdout)
    rec.append('D1 selftest rc=%d pass=%s' % (p.returncode, d1_pass))

    # D2: real lane
    p2 = subprocess.run(
        [sys.executable, '-B', str(script),
         '--root', LANE, '--rev', REV,
         '--capture', 'census/round-55/records/fleet-root-census.tsv',
         '--receipt', 'census/round-55/records/fleet-root-census-run.txt',
         '--tool-sha256', TOOL_SHA,
         '--scratch', str(ROOT / ('rl-' + mid))],
        capture_output=True, text=True, env=env, cwd=str(ROOT), timeout=600)
    real_out = p2.stdout + p2.stderr
    (RUN / ('%s-real.out' % mid)).write_text(real_out + 'EXIT=%d\n' % p2.returncode)
    pristine = (RUN / 'rl-base.out').read_text()
    same = real_out == pristine
    d2_pass = (p2.returncode == 0 and same)
    rec.append('D2 real rc=%d identical=%s pass=%s' % (p2.returncode, same, d2_pass))

    # Restore exact frozen bytes, then hash-check.
    shutil.copyfile(BASE_TREE / 'c2-counter.py', script)
    after = sha256(script.read_bytes())
    ok = (after == BASE_SHA)
    (RUN / ('%s-restore.txt' % mid)).write_text(
        'mutant_sha256=%s\nrestored_sha256=%s\nexpected=%s\nRESTORE %s\nEXIT=0\n'
        % (mut_sha, after, BASE_SHA, 'ok' if ok else 'FAIL'))
    rec.append('RESTORE %s' % ('ok' if ok else 'FAIL'))
    return mid, mut_sha, d1_pass, d2_pass, '; '.join(rec)


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    (ROOT / 'tmp').mkdir(exist_ok=True)
    rows = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for res in ex.map(run_one, MUTANTS):
            mid, mut_sha, d1, d2, rec = res
            verdict = 'KILLED' if not (d1 and d2) else 'SURVIVED'
            rows.append((mid, mut_sha, d1, d2, verdict, rec))
            print('%-5s d1=%-5s d2=%-5s %s  (%s)' % (mid, d1, d2, verdict, mut_sha))
    with open(RUN / 'results.tsv', 'w') as f:
        f.write('mutant\tsha256\tD1_selftest\tD2_real_lane\tverdict\tdetail\n')
        for r in rows:
            f.write('%s\t%s\t%s\t%s\t%s\t%s\n' % r)
    return 0


if __name__ == '__main__':
    sys.exit(main())
