#!/usr/bin/env python3
"""S56mutation02: run the same detectors on the RESTORED copies.

Every mutant tree's c2-counter.py was overwritten with the frozen base bytes
(sha256 560820...). This pass runs D1 (selftest, committed pins) and D2 (real
lane) on each restored copy and requires output byte-identical to the pristine
baseline (st-base selftest output / rl-base.out).
"""
import hashlib
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path('/fast/scratch/hyaku/souji-r56/S56mutation02')
RUN = ROOT / 'run'
LANE = '/home/vgpnk/Projects/shokunin/souji-shokunin'
REV = 'cce21b555a617cadda782613ec1e9d3a0c12ac83'
TOOL_SHA = 'e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b'
BUILDER_SHA = '2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a'
EXPECTED_SHA = '90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3'
BASE_SHA = '5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8'

MUTANTS = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N10',
           'N11', 'N3N4']


def check(mid):
    tree = ROOT / 'mutants' / mid / 'census' / 'round-56'
    script = tree / 'c2-counter.py'
    env = dict(os.environ)
    env['TMPDIR'] = str(ROOT / 'tmp')
    pre = hashlib.sha256(script.read_bytes()).hexdigest()
    p1 = subprocess.run(
        [sys.executable, '-B', str(script), '--selftest',
         '--work', str(ROOT / ('rst-' + mid)),
         '--builder-sha256', BUILDER_SHA, '--expected-sha256', EXPECTED_SHA],
        capture_output=True, text=True, env=env, cwd=str(ROOT), timeout=1800)
    base_self = (RUN / 'base-selftest.out').read_text()
    base_self = base_self.rsplit('EXIT=', 1)[0]
    d1 = (p1.returncode == 0 and p1.stdout == base_self)
    p2 = subprocess.run(
        [sys.executable, '-B', str(script),
         '--root', LANE, '--rev', REV,
         '--capture', 'census/round-55/records/fleet-root-census.tsv',
         '--receipt', 'census/round-55/records/fleet-root-census-run.txt',
         '--tool-sha256', TOOL_SHA,
         '--scratch', str(ROOT / ('rrl-' + mid))],
        capture_output=True, text=True, env=env, cwd=str(ROOT), timeout=600)
    base_real = (RUN / 'rl-base.out').read_text()
    d2 = (p2.returncode == 0 and p2.stdout == base_real)
    line = ('%s pre_sha=%s sha_ok=%s D1_restored=%s D2_restored=%s'
            % (mid, pre, pre == BASE_SHA, d1, d2))
    (RUN / ('%s-postrestore.txt' % mid)).write_text(line + '\nEXIT=0\n')
    return line


def main():
    rows = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(check, MUTANTS):
            rows.append(r)
            print(r)
    (RUN / 'postrestore.tsv').write_text('\n'.join(rows) + '\n')
    return 0 if all('sha_ok=True D1_restored=True D2_restored=True' in r for r in rows) else 1


if __name__ == '__main__':
    sys.exit(main())
