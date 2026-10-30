import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SEAT = LANE / '.ufo/waves/round-43/w1/R43mutanchorS03'
S = Path('/fast/scratch/hyaku/souji-r43/R43mutanchorS03')
FROZEN = 'f8c805dbfa7f45814cf9a7270fa8bbffb41a8373'
PIN = '619a75034dd6324e1a725f73034c59f7bf9558ef'
commands = []
def run(args, **kwargs):
    commands.append(args)
    return subprocess.run(args, capture_output=True, timeout=90, check=True, **kwargs)
def show(rev, path):
    return run(['git', '-C', str(LANE), 'show', rev + ':' + path]).stdout
sha = lambda b: hashlib.sha256(b).hexdigest()
S.mkdir(parents=True, exist_ok=False)
try:
    env = {'PATH': os.environ['PATH'], 'TMPDIR': str(S), 'LC_ALL': 'C', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null', 'GIT_TERMINAL_PROMPT': '0'}
    original = show(PIN, 'tools/souji-worktree-drift.py')
    counter = show(FROZEN, 'census/round-43/c3-counter.py')
    population = show(FROZEN, 'census/round-43/c3-survivors.tsv').decode()
    row = next(line for line in population.splitlines() if line.startswith('S03\t'))
    tree = ast.parse(counter)
    mutants = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'MUTANTS' for t in n.targets))
    _, old, new = next(m for m in mutants if m[0] == 'S03')
    old, new = old.encode(), new.encode()
    assert original.count(old) == 1
    assert row.split('\t')[1:3] == [sha(old), sha(new)]
    tool = S / 'tool.py'
    root = S / 'root'
    root.mkdir()
    repo = root / 'r'
    repo.mkdir()
    run(['git', '-C', str(repo), 'init', '-q'], env=env, cwd=S)
    record = S / 'record.tsv'
    rec = ''.join('REPO\tx%04d\tregs=1\tprunable=0\n' % i for i in range(3000)).encode()
    record.write_bytes(rec)
    cmd = ['python3', '-B', str(tool), '--root', str(root), '--record', str(record), '--skip-unrecorded']
    results = {}
    for label, data in [('pristine', original), ('mutant', original.replace(old, new, 1)), ('restored', original)]:
        tool.write_bytes(data)
        commands.append(cmd)
        p = subprocess.run(cmd, capture_output=True, env=env, cwd=S, timeout=90, check=False)
        (SEAT / (label + '.stdout')).write_bytes(p.stdout)
        (SEAT / (label + '.stderr')).write_bytes(p.stderr)
        results[label] = {'rc': p.returncode, 'tool_sha256': sha(tool.read_bytes()), 'stdout_bytes': len(p.stdout), 'stdout_sha256': sha(p.stdout), 'stderr': p.stderr.decode(), 'absent_rows': sum(l.startswith(b'DRIFT\tABSENT\t') for l in p.stdout.splitlines()), 'summary': next((l.decode() for l in p.stdout.splitlines() if l.startswith(b'SUMMARY ')), '')}
    assert tool.read_bytes() == original
    baseline_ok = results['pristine']['rc'] == 1 and results['pristine']['absent_rows'] == 3000 and not results['pristine']['stderr']
    killed = baseline_ok and results['mutant']['rc'] == 2 and 'RECORD-MALFORMED: line 2260' in results['mutant']['stderr']
    receipt = {'axes': ['anchor fidelity', 'behavioral discrimination', 'exact restoration'], 'row': row, 'anchor_count': original.count(old), 'old_sha256': sha(old), 'new_sha256': sha(new), 'record_bytes': len(rec), 'chunk_tail': repr(rec[:65536][-40:]), 'commands': commands, 'results': results, 'verdict': 'killed' if killed else 'inconclusive' if not baseline_ok else 'survived', 'flip_holds': killed, 'restored_exact': tool.read_bytes() == original}
finally:
    shutil.rmtree(S)
receipt['scratch_removed'] = not S.exists()
(SEAT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
