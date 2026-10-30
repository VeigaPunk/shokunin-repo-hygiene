#!/usr/bin/env python3
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
OUT = LANE / '.ufo/waves/round-44/w1/S44reviewer26'
SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer26')
REV = 'd314fd6e85d62565344fa6c4b102f52f62297884'
CID = 'h10-missing-prereg-refusal'
os.chdir(SCRATCH)
os.environ['TMPDIR'] = str(SCRATCH)
sources = {}
for rel in ['tools/souji-freeze-check.py', 'census/round-44/c2-hidden-audit.py', 'census/round-43/c2-hidden-audit.py', 'census/round-44/c2-scenarios.tsv', 'census/round-44/c2-counter.py', 'census/round-44/preregistration.txt']:
    p = subprocess.run(['git', '-C', str(LANE), 'show', REV + ':' + rel], capture_output=True, check=True)
    sources[rel] = p.stdout.decode()
    (OUT / (rel.replace('/', '__'))).write_bytes(p.stdout)
(OUT / 'source-hashes.json').write_text(json.dumps({k: hashlib.sha256(v.encode()).hexdigest() for k,v in sources.items()}, indent=2) + '\n')
base = sources['tools/souji-freeze-check.py']
needle = '        if raw is None:\n            raise Refusal("%s is absent at %s" % (args.prereg, rev))'
assert base.count(needle) == 1
tools = {
    'baseline': base,
    'wrong-exit': base.replace(needle, '        if raw is None:\n            return 1'),
    'extra-finding': base.replace(needle, '        if raw is None:\n            print("FINDING C0 NO-CLAIMS spurious-on-refusal")\n            raise Refusal("%s is absent at %s" % (args.prereg, rev))'),
}
for name, source in tools.items():
    (SCRATCH / (name + '.py')).write_text(source)
    if name != 'baseline':
        (OUT / (name + '.py')).write_text(source)
results = []
for round_name, tool_name in [('round-44', 'baseline'), ('round-43', 'baseline'), ('round-44', 'wrong-exit'), ('round-44', 'extra-finding')]:
    source = sources['census/' + round_name + '/c2-hidden-audit.py']
    tree = ast.parse(source)
    assign = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SCENARIOS' for t in n.targets))
    # Only this literal row is retained in the copied audit.
    rows = source.splitlines(keepends=True)
    rows[assign.lineno-1:assign.end_lineno] = ['SCENARIOS = (("h10-missing-prereg-refusal", "REFUSAL", 2, []),)\n']
    copy_path = SCRATCH / (round_name + '-' + tool_name + '-audit.py')
    copy_path.write_text(''.join(rows))
    (OUT / copy_path.name).write_text(''.join(rows))
    spec = importlib.util.spec_from_file_location('audit_' + round_name + '_' + tool_name, copy_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    original_git, original_run = mod.git, mod.run
    guards, calls = [], []
    def guarded_git(d, scratch, *args):
        if args[0] in ('add', 'commit'):
            top = original_git(d, scratch, 'rev-parse', '--show-toplevel')
            assert top == str(Path(d).resolve()), (top, d)
            assert Path(d).resolve().is_relative_to(SCRATCH)
            guards.append({'command': ['git', '-C', d, *args], 'asserted_toplevel': top})
        return original_git(d, scratch, *args)
    def recorded_run(tool, args, cwd, work):
        p = original_run(tool, args, cwd, work)
        assert p is not None
        calls.append({'command': ['python3', '-B', tool, *args], 'cwd': cwd, 'rc': p.returncode, 'stdout': p.stdout.decode(), 'stderr': p.stderr.decode(), 'classes': mod.classes(p)})
        return p
    mod.git, mod.run = guarded_git, recorded_run
    buf = io.StringIO()
    work = SCRATCH / (round_name + '-' + tool_name + '-work')
    with contextlib.redirect_stdout(buf):
        rc = mod.main(['--tool', str(SCRATCH / (tool_name + '.py')), '--work', str(work)])
    results.append({'audit': round_name, 'tool': tool_name, 'selected_row': list(mod.SCENARIOS[0]), 'audit_rc': rc, 'audit_stdout': buf.getvalue(), 'tool_calls': calls, 'fixture_guards': guards})
(OUT / 'receipts.json').write_text(json.dumps({'python': sys.version, 'git': subprocess.run(['git','--version'], capture_output=True, text=True, check=True).stdout.strip(), 'results': results}, indent=2) + '\n')
for r in results:
    print(r['audit'], r['tool'], 'audit_rc=' + str(r['audit_rc']))
    print(r['audit_stdout'], end='')
    for p in r['tool_calls']:
        print('tool_rc=' + str(p['rc']), 'classes=' + repr(p['classes']))
        print('stdout=' + repr(p['stdout']))
        print('stderr=' + repr(p['stderr']))
shutil.rmtree(SCRATCH)
print('scratch_removed=' + str(not SCRATCH.exists()))
