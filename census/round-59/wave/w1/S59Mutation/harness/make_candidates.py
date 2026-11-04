#!/usr/bin/env python3
"""S59Mutation: build exact, unrun candidate selftest mutants for the frozen
round-59 controls harness (census/round-59/controls.py).

Constructs bytes and diffs only. Executes nothing. Every candidate is recorded
with status 'unrun'; no kill or survival verdict is asserted.
"""
import difflib
import hashlib
import json
import pathlib
import subprocess

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SCRATCH = pathlib.Path('/fast/scratch/hyaku/souji-r59/S59Mutation')
CONTROLS_REV = '74455b7209e04a2375c2084738a7b6fea59bf6d5'
BASE = 'da5af55b5ea0a2a38edea05635a13416c698e6e7'
PIN = '2c4d45aab440ef713f22a8d3b210e651d6e7047451cab26f9d4316f5a6451a6d'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def show(path):
    return subprocess.check_output(['git', '-C', str(LANE), 'show',
                                    CONTROLS_REV + ':' + path])


GUARD = 'passed=r.returncode==expected_rc and actual==expected'
ROW = "            ('duplicate-forgery',original+'\\n'+original.replace('| evidence |','| gate |'),2,['REGISTRY-ROW-SHAPE']),\n"

WITNESSES = {
    'rc-wrong-findings-right': (
        '    return int(bool(findings))\n', '    return 0\n',
        'frozen counter with a correct finding list but an always-zero exit code'),
    'findings-suppressed': (
        "    for finding in findings: print('FINDING '+finding)\n", '',
        'frozen counter with correct exit codes but no FINDING lines'),
    'ignore-duplicate-guard': (None, None,
        'executed S59Mutation mutant: first-row decision, row-shape guard lost'),
}


def main():
    controls = show('census/round-59/controls.py')
    counter = show('census/round-59/c1-counter.py')
    if sha(counter) != PIN:
        raise SystemExit('frozen counter digest mismatch')
    controls_text = controls.decode()
    counter_text = counter.decode()
    for anchor in (GUARD, ROW):
        if controls_text.count(anchor) != 1:
            raise SystemExit('controls anchor count %d for %r'
                             % (controls_text.count(anchor), anchor[:40]))
    out = SCRATCH / 'candidates'
    out.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.rmtree(out)
    out.mkdir()
    (out / 'selftest-pristine').mkdir()
    (out / 'selftest-pristine' / 'controls.py').write_bytes(controls)
    (out / 'witnesses').mkdir()
    (out / 'candidates').mkdir()

    witness_records = {}
    for name, (old, new, description) in WITNESSES.items():
        if old is None:
            witness_records[name] = {'status': 'executed',
                                     'sha256': '3abf9604f805584a9188b5415625354141b67355e490cf658b68c20cbf4ff7f6',
                                     'description': description,
                                     'discriminating_cases_observed': ['duplicate-forgery']}
            continue
        if counter_text.count(old) != 1:
            raise SystemExit('witness anchor count %d for %s'
                             % (counter_text.count(old), name))
        blob = counter_text.replace(old, new, 1)
        path = out / 'witnesses' / (name + '.py')
        path.write_text(blob)
        witness_records[name] = {
            'status': 'unrun', 'sha256': sha(blob.encode()),
            'description': description, 'anchor': old, 'replacement': new,
            'diff': ''.join(difflib.unified_diff(
                counter_text.splitlines(True), blob.splitlines(True),
                fromfile='pristine/c1-counter.py',
                tofile='witnesses/%s.py' % name))}

    candidates = [
        ('rc-ignored', GUARD, 'passed=actual==expected',
         'selftest drops the exit-code equality; only the finding list is compared',
         'rc-wrong-findings-right'),
        ('finding-ignored', GUARD, 'passed=r.returncode==expected_rc',
         'selftest drops the finding equality; only the exit code is compared',
         'findings-suppressed'),
        ('omitted-expected-row', ROW, '',
         'selftest inventory omits the only case that exercises the row-shape guard',
         'ignore-duplicate-guard'),
    ]
    records = []
    for name, old, new, description, witness in candidates:
        blob = controls_text.replace(old, new, 1)
        path = out / 'candidates' / (name + '.py')
        path.write_text(blob)
        diff = ''.join(difflib.unified_diff(
            controls_text.splitlines(True), blob.splitlines(True),
            fromfile='selftest-pristine/controls.py',
            tofile='candidates/%s.py' % name))
        (out / 'candidates' / (name + '.diff')).write_text(diff)
        records.append({
            'candidate': name,
            'target': 'census/round-59/controls.py',
            'target_sha256': sha(controls),
            'anchor': old, 'replacement': new,
            'description': description,
            'sha256': sha(blob.encode()),
            'bytes_equal_target': sha(blob.encode()) == sha(controls),
            'diff': diff,
            'status': 'unrun',
            'verdict_claimed': None,
            'escape_witness': witness,
            'witness_sha256': witness_records[witness]['sha256'],
            'witness_status': witness_records[witness]['status'],
            'runner': [
                'python3', '-B', 'candidates/%s.py' % name,
                '--root', str(LANE), '--rev', BASE,
                '--counter', 'witnesses/%s.py' % witness,
                '--work', '<scratch>/candidate-%s/work' % name],
        })
    (out / 'selftest-candidates.json').write_text(json.dumps(
        {'base': BASE, 'controls_rev': CONTROLS_REV,
         'target': 'census/round-59/controls.py',
         'target_sha256': sha(controls),
         'frozen_counter_sha256': PIN,
         'candidates': records,
         'witnesses': witness_records}, indent=2) + '\n')
    for rec in records:
        print(rec['candidate'], 'sha', rec['sha256'][:16],
              'witness', rec['escape_witness'], rec['witness_sha256'][:16],
              rec['status'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
