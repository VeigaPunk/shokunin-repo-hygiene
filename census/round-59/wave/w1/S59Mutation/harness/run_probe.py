#!/usr/bin/env python3
"""S59Mutation: bounded mutation probe over the frozen round-59 calibration counter.

Read-only over the lane repository. All fixture Git activity happens in a
uniquely created directory under this seat's own scratch, and the public
controls driver asserts its own rev-parse toplevel before any fixture write.
No production write, no ambient GIT_* inheritance.
"""
import difflib
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SCRATCH = pathlib.Path('/fast/scratch/hyaku/souji-r59/S59Mutation')
CONTROLS_REV = '74455b7209e04a2375c2084738a7b6fea59bf6d5'
COUNTER = 'census/round-59/c1-counter.py'
DRIVER = 'census/round-59/controls.py'
PIN = '2c4d45aab440ef713f22a8d3b210e651d6e7047451cab26f9d4316f5a6451a6d'
DRIVER_PIN = 'ba8af5cc5404eb4108ab15ee6386d15907c73abf04cda3b780e592b5d7d452b8'
BASE = 'da5af55b5ea0a2a38edea05635a13416c698e6e7'

KIND_LINE = "    if row[2] != 'gate': findings.append('REGISTRY-KIND-MISMATCH')\n"
SHAPE_LINE = "    if len(rows) != 1 or len(rows[0]) != 10:\n"

MUTANTS = [
    ('always-clean', KIND_LINE, '    pass\n',
     'verdict always clean: kind mismatch can never be reported'),
    ('ignore-duplicate-guard',
     SHAPE_LINE, '    if not rows or len(rows[0]) != 10:\n',
     'duplicate registry rows accepted: first row decides, row-shape guard lost'),
    ('accept-prose-gate', KIND_LINE,
     "    if row[2] != 'gate' and 'gate' not in text: findings.append('REGISTRY-KIND-MISMATCH')\n",
     'prose occurrence of the word gate satisfies the kind field'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_show(rev, path):
    return subprocess.check_output(['git', '-C', str(LANE), 'show', rev + ':' + path])


def strip_git_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['LC_ALL'] = 'C'
    return env


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for entry in ('pristine', 'driver', 'stages', 'mutation-results.json',
                  'mutation-receipts.txt'):
        target = SCRATCH / entry
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    ENV = strip_git_env()
    receipts = []
    results = {'seat': 'S59Mutation', 'controls_rev': CONTROLS_REV, 'base': BASE,
               'counter_path': COUNTER, 'frozen_counter_sha256': PIN,
               'driver_path': DRIVER, 'driver_sha256_pin': DRIVER_PIN,
               'python': sys.version.split()[0], 'mutants': [], 'guards': []}

    def run(argv, cwd=None):
        return subprocess.run([str(a) for a in argv], cwd=str(cwd or SCRATCH),
                              env=ENV, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, timeout=300)

    # scratch confinement guard: scratch must not belong to any checkout
    pre = run(['git', '-C', SCRATCH, 'rev-parse', '--show-toplevel'])
    results['guards'].append({
        'check': 'scratch is not inside a checkout',
        'argv': ['git', '-C', str(SCRATCH), 'rev-parse', '--show-toplevel'],
        'exit': pre.returncode,
        'stdout': pre.stdout, 'stderr': pre.stderr,
        'ok': pre.returncode == 128})

    pristine = git_show(CONTROLS_REV, COUNTER)
    driver = git_show(CONTROLS_REV, DRIVER)
    if sha(pristine) != PIN:
        raise SystemExit('frozen counter digest mismatch: ' + sha(pristine))
    if sha(driver) != DRIVER_PIN:
        raise SystemExit('frozen driver digest mismatch: ' + sha(driver))
    (SCRATCH / 'pristine').mkdir()
    (SCRATCH / 'pristine' / 'c1-counter.py').write_bytes(pristine)
    (SCRATCH / 'driver').mkdir()
    (SCRATCH / 'driver' / 'controls-driver.py').write_bytes(driver)
    text = pristine.decode()

    for name, old, new, description in MUTANTS:
        if text.count(old) != 1:
            raise SystemExit('%s: mutation anchor count %d' % (name, text.count(old)))
        mutated = text.replace(old, new, 1).encode()
        stage_dir = SCRATCH / 'stages' / name
        for sub in ('pristine', 'mutant', 'restored'):
            (stage_dir / sub).mkdir(parents=True)
        (stage_dir / 'mutant' / 'c1-counter.py').write_bytes(mutated)
        entry = {'mutant': name, 'description': name + ': ' + description,
                 'anchor': old, 'replacement': new,
                 'sha256_pristine_source': sha(pristine),
                 'sha256_mutant': sha(mutated),
                 'diff': ''.join(difflib.unified_diff(
                     text.splitlines(True), mutated.decode().splitlines(True),
                     fromfile='pristine/c1-counter.py',
                     tofile='mutants/%s.py' % name)),
                 'stages': {}}
        triplets = []
        for stage, source in (('pristine', pristine), ('mutant', mutated),
                              ('restored', pristine)):
            counter_file = stage_dir / stage / 'c1-counter.py'
            # restored stage copies pristine bytes read back from disk
            payload = (stage_dir / 'pristine' / 'c1-counter.py').read_bytes() \
                if stage == 'restored' else source
            counter_file.write_bytes(payload)
            work = stage_dir / stage / 'work'
            argv = [sys.executable, '-B', SCRATCH / 'driver' / 'controls-driver.py',
                    '--root', LANE, '--rev', BASE,
                    '--counter', counter_file, '--work', work]
            proc = run(argv)
            parsed = None
            try:
                parsed = json.loads(proc.stdout)
            except json.JSONDecodeError:
                parsed = None
            record = {
                'stage': stage, 'argv': [str(a) for a in argv],
                'exit': proc.returncode, 'stderr': proc.stderr,
                'counter_sha256': sha(counter_file.read_bytes()),
                'bytes_equal_frozen': sha(counter_file.read_bytes()) == PIN,
                'driver_instrument_sha256': (parsed or {}).get('instrument_sha256'),
                'cases_passed': (parsed or {}).get('passed'),
                'case_detail': [{'case': c['case'], 'expected_rc': c['expected_rc'],
                                 'rc': c['rc'],
                                 'expected_findings': c['expected_findings'],
                                 'findings': [ln[len('FINDING '):] for ln in
                                              c['stdout'].splitlines()
                                              if ln.startswith('FINDING ')],
                                 'passed': c['passed']}
                                for c in (parsed or {}).get('cases', [])],
                'stdout_json_ok': parsed is not None,
            }
            (stage_dir / (stage + '.json')).write_text(json.dumps(parsed, indent=2) + '\n')
            (stage_dir / (stage + '.txt')).write_text(
                '$ ' + ' '.join(map(str, argv)) + '\nSTDOUT:\n' + proc.stdout +
                'STDERR:\n' + proc.stderr + 'EXIT %d\n' % proc.returncode)
            entry['stages'][stage] = record
            triplets.append(record)
        p, m, r = triplets
        baseline_ok = p['exit'] == 0 and p['cases_passed'] == 4
        restored_ok = r['exit'] == 0 and r['cases_passed'] == 4 and r['bytes_equal_frozen']
        if not baseline_ok:
            verdict = 'inconclusive-baseline'
        elif m['exit'] != 0:
            verdict = 'killed'
        else:
            verdict = 'survived'
        entry['verdict'] = verdict
        entry['discriminating_cases'] = [c['case'] for c in m['case_detail'] if not c['passed']]
        entry['baseline_ok'] = baseline_ok
        entry['restored_ok'] = restored_ok
        entry['triplet_exits'] = [p['exit'], m['exit'], r['exit']]
        results['mutants'].append(entry)
        receipts.append('%s verdict=%s exits=%s sha_pristine=%s sha_mutant=%s '
                        'sha_restored=%s discriminating=%s'
                        % (name, verdict, entry['triplet_exits'],
                           p['counter_sha256'], m['counter_sha256'],
                           r['counter_sha256'],
                           ','.join(entry['discriminating_cases']) or '-'))

    results['verdicts'] = {m['mutant']: m['verdict'] for m in results['mutants']}
    (SCRATCH / 'mutation-results.json').write_text(json.dumps(results, indent=2) + '\n')
    (SCRATCH / 'mutation-receipts.txt').write_text('\n'.join(receipts) + '\n')
    print('\n'.join(receipts))
    print('RESULTS ' + json.dumps(results['verdicts']))
    return 0 if all(v == 'killed' for v in results['verdicts'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
