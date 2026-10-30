#!/usr/bin/env python3
"""Bounded h4-only audit reproduction; all fixture mutations stay in seat scratch."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
OUT = LANE / '.ufo/waves/round-44/w1/S44reviewer20'
SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer20')
REV = 'd314fd6e85d62565344fa6c4b102f52f62297884'

def blob(path):
    p = subprocess.run(['git', '-C', str(LANE), 'show', f'{REV}:{path}'], capture_output=True, check=True)
    raw = p.stdout
    (OUT / ('frozen-' + path.replace('/', '__'))).write_bytes(raw)
    return raw.decode()

def selected(source):
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SCENARIOS' for t in n.targets))
    lines = source.splitlines(keepends=True)
    # Keep the literal fourth tuple, not a synthetic reimplementation.
    row = ast.get_source_segment(source, node.value.elts[3])
    lines[node.lineno-1:node.end_lineno] = ['SCENARIOS = (' + row + ',)\n']
    source = ''.join(lines)
    guard = '''
_original_git = git
def git(d, scratch, *args):
    if args[0] != 'init':
        top = _original_git(d, scratch, 'rev-parse', '--show-toplevel')
        assert top == os.path.abspath(d), (top, d)
    return _original_git(d, scratch, *args)
_original_run = run
def run(tool, args, cwd, work):
    p = _original_run(tool, args, cwd, work)
    print('COMMAND ' + repr(['python3', '-B', tool] + args))
    print('RAW_RC ' + str(None if p is None else p.returncode))
    if p is not None:
        print('RAW_STDOUT_BEGIN\\n' + p.stdout.decode('utf-8', 'replace') + 'RAW_STDOUT_END')
        print('RAW_STDERR_BEGIN\\n' + p.stderr.decode('utf-8', 'replace') + 'RAW_STDERR_END')
        print('ACTUAL_MULTISET ' + repr(classes(p)))
    return p
print('EXPECTED ' + repr(SCENARIOS[0][2:]))
'''
    return source.replace('if __name__ == "__main__":', guard + '\nif __name__ == "__main__":')

SCRATCH.mkdir(parents=True, exist_ok=True)
os.chdir(SCRATCH)
tool = blob('tools/souji-freeze-check.py')
r44 = blob('census/round-44/c2-hidden-audit.py')
r43 = blob('census/round-43/c2-hidden-audit.py')
blob('census/round-44/c2-scenarios.tsv')
blob('census/round-44/c2-counter.py')
needle = 'if key not in f:'
assert tool.count(needle) == 1
mutant = tool.replace(needle, 'if key not in f and key != "Control":')
(OUT / 'mutant-omit-control-required.py').write_text(mutant)
(SCRATCH / 'tool.py').write_text(tool)
(SCRATCH / 'mutant.py').write_text(mutant)
results = []
for name, audit, checker in [('r44-canonical', r44, 'tool.py'), ('r43-canonical', r43, 'tool.py'), ('r44-mutant', r44, 'mutant.py')]:
    path = SCRATCH / (name + '-audit.py')
    src = selected(audit)
    path.write_text(src)
    (OUT / path.name).write_text(src)
    cmd = [sys.executable, '-B', str(path), '--tool', str(SCRATCH / checker), '--work', str(SCRATCH / (name + '-work'))]
    e = dict(os.environ, TMPDIR=str(SCRATCH), PYTHONDONTWRITEBYTECODE='1')
    p = subprocess.run(cmd, cwd=SCRATCH, env=e, capture_output=True, timeout=60)
    result = {'name': name, 'command': cmd, 'cwd': str(SCRATCH), 'returncode': p.returncode, 'stdout': p.stdout.decode(), 'stderr': p.stderr.decode()}
    results.append(result)
    print(json.dumps(result, indent=2))
(OUT / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('frozen-*')}
(OUT / 'frozen-sha256.json').write_text(json.dumps(manifest, indent=2) + '\n')
versions = {name: subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip() for name, cmd in [('python', [sys.executable, '--version']), ('git', ['git', '--version'])]}
(OUT / 'versions.json').write_text(json.dumps(versions, indent=2) + '\n')
print('VERSIONS ' + repr(versions))
