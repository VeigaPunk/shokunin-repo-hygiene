import csv
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
OUT = LANE / '.ufo/waves/round-57/w1/S57executor01'
S = Path('/fast/scratch/hyaku/souji-r57/S57executor01')
FREEZE = 'd749f7ee081ec1b382b2f92577eb22bfba1c7761'
env = dict(os.environ, TMPDIR=str(S))
commands = []

def run(args, receipt):
    cmd = shlex.join([str(a) for a in args])
    p = subprocess.run([str(a) for a in args], cwd=S, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (OUT / receipt).write_text('COMMAND TMPDIR=' + str(S) + ' ' + cmd + '\n' + p.stdout + 'EXIT=' + str(p.returncode) + '\n')
    commands.append({'command': cmd, 'receipt': receipt, 'rc': p.returncode})
    return p

try:
    if (S / 'f').exists():
        raise RuntimeError('fresh fixture directory already exists')
    (S / 'f').mkdir(parents=True)
    p = run(['python3', '-B', LANE / 'census/round-57/fixtures/build-fixtures.py', '--work', S / 'f', '--manifest', S / 'f/fixture-manifest.tsv'], 'build.txt')
    if p.returncode:
        raise RuntimeError('fixture build failed')
    shutil.copyfile(S / 'f/fixture-manifest.tsv', OUT / 'fixture-manifest.tsv')
    with (S / 'f/fixture-manifest.tsv').open() as f:
        manifest = list(csv.DictReader(f, delimiter='\t'))
    print('MANIFEST_HEADER', list(manifest[0]))
    # The frozen manifest has fixture/kind/dir/base/tip/record_sha256 columns.
    fixtures = [list(r.values()) for r in manifest if list(r.values())[1] == 'C1']
    if len(fixtures) != 36:
        raise RuntimeError('expected 36 C1 fixtures, got ' + str(len(fixtures)))
    results = {}
    for label, version, roundno in [('v5-r56', 'v5', 56), ('v6-r57', 'v6', 57)]:
        rows = []
        for name, kind, directory, base, tip, record_sha in fixtures:
            chosen_base = base if name in {'F5-REWRITE', 'F6-RECORD-DRIFT', 'F27-BINARY-NUMSTAT'} else tip
            args = ['python3', '-B', LANE / ('census/round-%s/c1-counter.py' % roundno), '--root', directory, '--rev', tip, '--base', chosen_base, '--record-sha256', record_sha, '--sources-rev-before', tip, '--sources-rev-after', tip, '--scratch', S]
            p = run(args, version + '-' + name + '.txt')
            findings = [line.split()[1] for line in p.stdout.splitlines() if line.startswith('FINDING ')]
            summaries = [line for line in p.stdout.splitlines() if line.startswith('SUMMARY')]
            rows.append(dict(zip(['fixture','counter','rev','base','exit','finding','findings_all','SUMMARY'], [name,label,tip[:12],chosen_base[:12],str(p.returncode),findings[0] if findings else '-',','.join(findings) if findings else '-', '\n'.join(summaries)])))
        results[version] = rows
        target = OUT / ('c1-matrix-' + version + '.tsv')
        with target.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        reference = LANE / ('census/round-57/records/matrix-dryrun/c1-matrix-' + version + '.tsv')
        p = run(['cmp', '-s', target, reference], 'cmp-' + version + '.txt')
        if p.returncode:
            with reference.open() as f:
                expected = {r['fixture']: r for r in csv.DictReader(f, delimiter='\t')}
            differences = [{'fixture': r['fixture'], 'observed': {k:r[k] for k in ['exit','findings_all']}, 'expected': {k:expected[r['fixture']][k] for k in ['exit','findings_all']}} for r in rows if any(r[k] != expected[r['fixture']][k] for k in ['exit','findings_all'])]
            (OUT / ('row-diff-' + version + '.json')).write_text(json.dumps(differences, indent=2) + '\n')
    changes = []
    for before, after in zip(results['v5'], results['v6']):
        if (before['exit'], before['findings_all']) != (after['exit'], after['findings_all']):
            changes.append({'fixture': before['fixture'], 'v5': {k:before[k] for k in ['exit','findings_all']}, 'v6': {k:after[k] for k in ['exit','findings_all']}})
    facts = {'fixtures': len(fixtures), 'changed_rows': len(changes), 'changes': changes, 'v5_exit0': sum(r['exit']=='0' for r in results['v5']), 'v6_exit0': sum(r['exit']=='0' for r in results['v6']), 'non_B4_C4_identical': all(c['fixture'] in {'B4-INLINE-NBSP-OPENER','C4-INLINE-CLOSED-COMMENT'} for c in changes)}
    (OUT / 'derived.json').write_text(json.dumps(facts, indent=2) + '\n')
    print(json.dumps(facts, indent=2))
    p = run(['python3','-B',LANE / 'census/round-57/c1-counter.py','--selftest','--work',S / 'st'], 'selftest.txt')
    print('SELFTEST_RC', p.returncode)
    print('\n'.join(line for line in p.stdout.splitlines() if line.startswith('SELFTEST')))
    p = run(['python3','-B',LANE / 'census/round-57/c1-counter.py','--root',LANE,'--rev',FREEZE,'--base','b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd','--record-sha256','2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30','--sources-rev-before','f778b9d131574d3ff09c0cc8a077643c0fc84bb4','--sources-rev-after','9bf9234ae4d11c7b31706354302a9e95ad0d1f81','--scratch',S], 'real-lane.txt')
    print('REAL_LANE_RC', p.returncode)
    print('\n'.join(line for line in p.stdout.splitlines() if line.startswith('SUMMARY')))
finally:
    (OUT / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    shutil.rmtree(S)
    (OUT / 'cleanup.txt').write_text('scratch_exists=' + str(S.exists()).lower() + '\n')
