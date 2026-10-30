#!/usr/bin/env python3
"""Replay only frozen C2 scenario h5; all fixtures live in seat scratch."""
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
OUT = LANE / '.ufo/waves/round-44/w1/S44reviewer21'
SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer21')
REV = 'd314fd6e85d62565344fa6c4b102f52f62297884'
CID = 'h5-control-symlink-exit0-text'

def frozen(rel):
    p = subprocess.run(['git', '-C', str(LANE), 'show', f'{REV}:{rel}'], capture_output=True, check=True)
    return p.stdout

def load_audit(data, name):
    tree = ast.parse(data)
    selected = False
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SCENARIOS' for t in node.targets):
            node.value.elts = [row for row in node.value.elts if isinstance(row.elts[0], ast.Constant) and row.elts[0].value == CID]
            assert len(node.value.elts) == 1
            selected = True
    assert selected
    path = SCRATCH / f'{name}.py'
    path.write_text(ast.unparse(tree) + '\n')
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    original_git = mod.git
    def guarded_git(d, scratch, *args):
        d = str(Path(d).resolve())
        assert Path(d).is_relative_to(SCRATCH)
        if args[0] != 'init':
            top = original_git(d, scratch, 'rev-parse', '--show-toplevel')
            assert top == d, (top, d)
        result = original_git(d, scratch, *args)
        if args[0] == 'init':
            assert original_git(d, scratch, 'rev-parse', '--show-toplevel') == d
        return result
    mod.git = guarded_git
    return mod

def exercise(mod, tool, name):
    runs = []
    original_run = mod.run
    def capture(tool, args, cwd, work):
        p = original_run(tool, args, cwd, work)
        assert p is not None
        runs.append({'command': ['python3', '-B', tool] + args, 'cwd': cwd,
                     'exit': p.returncode, 'stdout': p.stdout.decode(), 'stderr': p.stderr.decode(),
                     'classes': mod.classes(p)})
        return p
    mod.run = capture
    stream = io.StringIO()
    args = ['--tool', str(tool), '--work', str(SCRATCH / name)]
    with contextlib.redirect_stdout(stream):
        rc = mod.main(args)
    result = {'scenario': CID, 'expected_exit': 1, 'expected_classes': ['C1:CONTROL-SYMLINK'],
              'audit_args': args, 'audit_exit': rc, 'audit_stdout': stream.getvalue(), 'runs': runs}
    (OUT / f'{name}.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result

def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    os.chdir(SCRATCH)
    hashes = {}
    data = {}
    for name, rel in [('tool', 'tools/souji-freeze-check.py'), ('v2', 'census/round-44/c2-hidden-audit.py'),
                      ('r43', 'census/round-43/c2-hidden-audit.py'), ('population', 'census/round-44/c2-scenarios.tsv'),
                      ('counter', 'census/round-44/c2-counter.py')]:
        data[name] = frozen(rel)
        hashes[rel] = hashlib.sha256(data[name]).hexdigest()
    (OUT / 'frozen-sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    tool = SCRATCH / 'tool.py'
    tool.write_bytes(data['tool'])
    versions = {'python': sys.version, 'git': subprocess.run(['git', '--version'], capture_output=True, text=True, check=True).stdout.strip()}
    print(json.dumps({'revision': REV, 'versions': versions, 'hashes': hashes}, indent=2))
    a = exercise(load_audit(data['v2'], 'v2_selected'), tool, 'v2-baseline')
    b = exercise(load_audit(data['r43'], 'r43_selected'), tool, 'r43-baseline')
    # Single branch defect: regress the Control-symlink classification only.
    old = b'found.append((label, "CONTROL-SYMLINK", "%s is a symlink at freeze" % path))'
    new = b'found.append((label, "CONTROL-NOT-RED", "%s is a symlink at freeze" % path))'
    assert data['tool'].count(old) == 1
    mutant = SCRATCH / 'mutant.py'
    mutant.write_bytes(data['tool'].replace(old, new))
    (OUT / 'mutant-change.txt').write_text('Single replacement in tools/souji-freeze-check.py:229\n- ' + old.decode() + '\n+ ' + new.decode() + '\n')
    c = exercise(load_audit(data['v2'], 'v2_mutant_selected'), mutant, 'v2-mutant')
    assert a['audit_exit'] == b['audit_exit'] == 0
    assert c['audit_exit'] == 1
    assert c['runs'][0]['classes'] == ['C1:CONTROL-NOT-RED']
    shutil.rmtree(SCRATCH)
    print('SCRATCH_REMOVED=' + str(not SCRATCH.exists()))

if __name__ == '__main__':
    main()
