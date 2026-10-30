"""Seat-local, h7-only probe. Never imports or writes production sources."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer23')
OUT = LANE / '.ufo/waves/round-44/w1/S44reviewer23'
REV = 'd314fd6e85d62565344fa6c4b102f52f62297884'
case = sys.argv[1]
assert case in ('r44', 'r43', 'mutant')
work = SCRATCH / case
work.mkdir(parents=True, exist_ok=False)
os.chdir(work)
os.environ['TMPDIR'] = str(SCRATCH)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True

def blob(path):
    return subprocess.run(['git', '-C', str(LANE), 'show', REV + ':' + path], capture_output=True, check=True).stdout.decode()

audit_path = 'census/round-%s/c2-hidden-audit.py' % ('43' if case == 'r43' else '44')
source = blob(audit_path)
tree = ast.parse(source)
node = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SCENARIOS' for t in n.targets))
row = node.value.elts[6]
assert ast.literal_eval(row) == ('h7-dispatch-notes-ready', {'before': ['notes.ready']}, 1, ['C0:DISPATCH-BEFORE-FREEZE'])
lines = source.splitlines(keepends=True)
selected = ''.join(lines[:node.lineno-1]) + 'SCENARIOS = (' + ast.get_source_segment(source, row) + ',)\n' + ''.join(lines[node.end_lineno:])
(work / 'selected-audit.py').write_text(selected)
(OUT / (case + '-selected-audit.py')).write_text(selected)
tool = blob('tools/souji-freeze-check.py')
if case == 'mutant':
    old = '"-dispatch" in base or ".ready" in base or base.endswith'
    new = '"-dispatch" in base or False or base.endswith'
    assert tool.count(old) == 1
    tool = tool.replace(old, new)
(work / 'tool.py').write_text(tool)
if case == 'mutant':
    (OUT / 'mutant-tool.py').write_text(tool)
spec = importlib.util.spec_from_file_location('selected_audit', work / 'selected-audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
original_git = audit.git
guards = []

def guarded_git(d, scratch, *args):
    if args[0] in ('add', 'commit'):
        q = subprocess.run(['git', '-C', d, 'rev-parse', '--show-toplevel'], capture_output=True, text=True, env=audit.env(scratch), check=True)
        assert q.stdout.strip() == str(Path(d).resolve()), (d, q.stdout)
        assert Path(d).resolve().is_relative_to(SCRATCH)
        guards.append({'before': list(args), 'root': q.stdout.strip()})
    return original_git(d, scratch, *args)

audit.git = guarded_git
original_run = audit.run
actuals = []

def recording_run(tool, args, cwd, scratch):
    p = original_run(tool, args, cwd, scratch)
    assert p is not None, 'bounded probe timed out'
    (OUT / (case + '-actual.stdout')).write_bytes(p.stdout)
    (OUT / (case + '-actual.stderr')).write_bytes(p.stderr)
    actuals.append({'command': ['python3', '-B', tool] + args, 'cwd': cwd,
                    'exit': p.returncode, 'classes': audit.classes(p),
                    'stdout': p.stdout.decode(), 'stderr': p.stderr.decode()})
    return p

audit.run = recording_run
rc = audit.main(['--tool', str(work / 'tool.py'), '--work', str(work / 'fixtures')])
receipt = {'case': case, 'frozen_rev': REV, 'source': audit_path,
           'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
           'tool_sha256': hashlib.sha256(tool.encode()).hexdigest(),
           'expected': {'exit': 1, 'classes': ['C0:DISPATCH-BEFORE-FREEZE']},
           'actuals': actuals, 'git_mutation_root_guards': guards, 'audit_exit': rc}
(OUT / (case + '-receipt.json')).write_text(json.dumps(receipt, indent=2) + '\n')
sys.exit(rc)
