import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
OUT = LANE / '.ufo/waves/round-44/w1/S44reviewer57'
SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer57')
REVS = {'base': '55d7af6f5a22340f7a3de1c386e514ababfaa75f', 'frozen': 'd314fd6e85d62565344fa6c4b102f52f62297884'}
CASES = ('dangling', 'existing', 'directory', 'regular', 'parent-symlink', 'parent-file', 'parent-loop')

def command(args):
    p = subprocess.run(args, cwd=SCRATCH, capture_output=True, text=True, timeout=15,
                       env={**os.environ, 'TMPDIR': str(SCRATCH), 'PYTHONDONTWRITEBYTECODE': '1'})
    return {'argv': [str(a) for a in args], 'rc': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}

pins = {}
for label, rev in REVS.items():
    p = subprocess.run(['git', '-C', str(LANE), 'show', rev + ':tools/souji-worktree-drift.py'], capture_output=True, check=True)
    tool = OUT / (label + '-tool.py')
    tool.write_bytes(p.stdout)
    pins[label] = {'rev': rev, 'sha256': hashlib.sha256(p.stdout).hexdigest()}

def probe(pair):
    label, case = pair
    work = SCRATCH / ('valid-' + label + '-' + case)
    work.mkdir()
    root = work / 'root'
    root.mkdir()
    record = work / 'record.tsv'
    record_text = 'REPO\tabsent\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n'
    record.write_text(record_text)
    target = work / 'out.json'
    victim = work / 'victim'
    if case == 'dangling':
        target.symlink_to(victim)
    elif case == 'existing':
        victim.write_text('keep\n')
        target.symlink_to(victim)
    elif case == 'directory':
        victim.mkdir()
        target.symlink_to(victim)
    elif case == 'parent-symlink':
        victim.mkdir()
        (work / 'parent').symlink_to(victim)
        target = work / 'parent' / 'out.json'
    elif case == 'parent-file':
        victim.write_text('keep\n')
        target = victim / 'out.json'
    elif case == 'parent-loop':
        victim.symlink_to(victim)
        target = victim / 'out.json'
    args = [sys.executable, '-B', str(OUT / (label + '-tool.py')), '--root', str(root), '--record', str(record), '--skip-unrecorded', '--json', str(target)]
    result = command(args)
    result.update(label=label, case=case, record_unchanged=record.read_text() == record_text, leaf_is_symlink=target.is_symlink(), victim_regular_bytes=victim.read_text() if victim.is_file() else None)
    return result

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(probe, [(label, case) for label in REVS for case in CASES]))
receipt = {'pins': pins, 'python': sys.version, 'probes': results}
(OUT / 'probe-receipt-valid.json').write_text(json.dumps(receipt, indent=2) + '\n')
for r in results:
    print(r['label'], r['case'], 'rc=' + str(r['rc']), 'record_unchanged=' + str(r['record_unchanged']), 'traceback=' + str('Traceback' in r['stderr']), 'stderr=' + repr(r['stderr'].splitlines()[-1:] ))
print('receipt=' + str(OUT / 'probe-receipt-valid.json'))
