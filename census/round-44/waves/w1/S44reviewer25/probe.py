#!/usr/bin/env python3
"""Run only frozen h9, preserving raw tool results; no production writes."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys

S = Path('/fast/scratch/hyaku/souji-r44/S44reviewer25')
O = Path(__file__).resolve().parent
CASE = 'h9-dispatch-depth-three'
receipts = []
for version, tool in [('44', 'tool.py'), ('43', 'tool.py'), ('44-mutant', 'mutant.py')]:
    audit = S / ('audit43.py' if version == '43' else 'audit44.py')
    spec = importlib.util.spec_from_file_location('audit_' + version, audit)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCENARIOS = tuple(row for row in m.SCENARIOS if row[0] == CASE)
    assert len(m.SCENARIOS) == 1
    original_git = m.git
    guards = []
    def guarded_git(d, work, *args):
        top = subprocess.run(['git', '-C', d, 'rev-parse', '--show-toplevel'],
                             capture_output=True, text=True, env=m.env(work))
        if args[0] == 'init':
            assert top.returncode != 0, (d, top.stdout)
            result = original_git(d, work, *args)
            top = subprocess.run(['git', '-C', d, 'rev-parse', '--show-toplevel'],
                                 capture_output=True, text=True, env=m.env(work))
            assert top.returncode == 0 and Path(top.stdout.strip()).resolve() == Path(d).resolve()
            guards.append({'bootstrap_init': d, 'top': top.stdout.strip()})
            return result
        assert top.returncode == 0 and Path(top.stdout.strip()).resolve() == Path(d).resolve()
        if args[0] in ('add', 'commit'):
            guards.append({'mutation': list(args), 'top': top.stdout.strip()})
        return original_git(d, work, *args)
    m.git = guarded_git
    original_run = m.run
    runs = []
    def captured_run(tool_path, args, cwd, work):
        p = original_run(tool_path, args, cwd, work)
        assert p is not None
        runs.append({'command': ['python3', '-B', tool_path] + args, 'cwd': cwd,
                     'returncode': p.returncode, 'stdout': p.stdout.decode(),
                     'stderr': p.stderr.decode(), 'actual_classes': m.classes(p)})
        return p
    m.run = captured_run
    buf = io.StringIO()
    args = ['--tool', str(S / tool), '--work', str(S / ('work-' + version))]
    with contextlib.redirect_stdout(buf):
        rc = m.main(args)
    row = m.SCENARIOS[0]
    receipt = {'version': version, 'audit': str(audit), 'audit_args': args,
               'expected_exit': row[2], 'expected_classes': row[3],
               'audit_exit': rc, 'audit_stdout': buf.getvalue(),
               'runs': runs, 'guards': guards}
    receipts.append(receipt)
    print(json.dumps(receipt, indent=2))
(O / 'receipts.json').write_text(json.dumps(receipts, indent=2) + '\n')
assert [r['audit_exit'] for r in receipts] == [0, 0, 1]
assert [r['runs'][0]['returncode'] for r in receipts] == [1, 1, 0]
