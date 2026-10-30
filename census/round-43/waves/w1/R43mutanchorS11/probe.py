import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SEAT = LANE / '.ufo/waves/round-43/w1/R43mutanchorS11'
S = Path('/fast/scratch/hyaku/souji-r43/R43mutanchorS11')
FROZEN = 'f8c805dbfa7f45814cf9a7270fa8bbffb41a8373'
PIN = '619a75034dd6324e1a725f73034c59f7bf9558ef'
results = {'commands': []}
def run(cmd, env):
    p = subprocess.run(cmd, cwd=S, env=env, capture_output=True, text=True, timeout=30)
    results['commands'].append({'argv': cmd, 'rc': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    return p

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

S.mkdir(parents=True, exist_ok=False)
env = {'PATH': os.environ['PATH'], 'TMPDIR': str(S), 'LC_ALL': 'C', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null', 'GIT_TERMINAL_PROMPT': '0'}
try:
    assert os.getuid() != 0
    counter = run(['git', '-C', str(LANE), 'show', FROZEN + ':census/round-43/c3-counter.py'], env)
    assert counter.returncode == 0
    tree = ast.parse(counter.stdout)
    mutants = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'MUTANTS' for t in n.targets))
    _, old, new = next(row for row in mutants if row[0] == 'S11')
    pop = run(['git', '-C', str(LANE), 'show', FROZEN + ':census/round-43/c3-survivors.tsv'], env)
    results['population_row'] = next(line for line in pop.stdout.splitlines() if line.startswith('S11\t'))
    base = run(['git', '-C', str(LANE), 'show', PIN + ':tools/souji-worktree-drift.py'], env)
    assert base.returncode == 0
    original = base.stdout.encode()
    results['anchor_count'] = base.stdout.count(old)
    assert results['anchor_count'] == 1
    results['old_anchor_sha256'] = sha(old.encode())
    results['new_anchor_sha256'] = sha(new.encode())
    tool = S / 'tool.py'
    tool.write_bytes(original)
    results['before_sha256'] = sha(tool.read_bytes())
    root = S / 'root'
    repo = root / 'r'
    repo.mkdir(parents=True)
    init = run(['git', '-C', str(repo), 'init', '-q'], env)
    assert init.returncode == 0
    top = run(['git', '-C', str(repo), 'rev-parse', '--show-toplevel'], env)
    assert top.returncode == 0 and top.stdout.strip() == str(repo)
    record = S / 'total-junk.tsv'
    record.write_text('REPO\tr\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0JUNK\n')
    results['record'] = record.read_text()
    cmd = ['python3', '-B', str(tool), '--root', str(root), '--record', str(record), '--timeout', '5', '--skip-unrecorded']
    def detect():
        p = run(cmd, env)
        return {'rc': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr, 'detector_pass': p.returncode == 2 and 'REFUSAL RECORD-MALFORMED:' in p.stderr}
    results['pristine'] = detect()
    try:
        tool.write_bytes(base.stdout.replace(old, new, 1).encode())
        results['mutant_sha256'] = sha(tool.read_bytes())
        results['mutant'] = detect()
    finally:
        tool.write_bytes(original)
        results['restored_sha256'] = sha(tool.read_bytes())
        results['restored_exact'] = tool.read_bytes() == original
    results['restored'] = detect()
    results['flip_holds'] = results['pristine']['detector_pass'] and results['mutant']['rc'] == 0 and 'drift_rows=0' in results['mutant']['stdout'] and results['restored']['detector_pass']
    results['verdict'] = 'killed' if results['flip_holds'] else 'inconclusive' if not results['pristine']['detector_pass'] else 'survived'
finally:
    shutil.rmtree(S)
    results['scratch_removed'] = not S.exists()
    (SEAT / 'receipt.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps({k: v for k, v in results.items() if k != 'commands'}, indent=2))
