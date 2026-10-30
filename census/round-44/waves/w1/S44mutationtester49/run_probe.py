import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys

scratch = Path('/fast/scratch/hyaku/souji-r44/S44mutationtester49').resolve()
phase = sys.argv[1]
os.chdir(scratch)
real_run = subprocess.run

def guarded_run(args, *a, **kw):
    if isinstance(args, list) and args and args[0] == 'git':
        target = Path(args[2]).resolve() if len(args) > 2 and args[1] == '-C' else Path(kw.get('cwd', os.getcwd())).resolve()
        if not target.is_relative_to(scratch):
            raise RuntimeError('git escaped assigned scratch: ' + str(target))
        if any(x in args for x in ('add', 'commit')):
            top = real_run(['git', '-C', str(target), 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()
            if Path(top).resolve() != target:
                raise RuntimeError('fixture top-level mismatch: ' + top)
    return real_run(args, *a, **kw)

subprocess.run = guarded_run

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, scratch / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

audit = load('frozen_audit', 'audit.py')
counter = load('frozen_counter', 'counter.py')
stdout = io.StringIO()
stderr = io.StringIO()
with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
    rc = audit.main(['--tool', str(scratch / 'tool.py'), '--work', str(scratch / ('fixtures-' + phase))])
p = subprocess.CompletedProcess([], rc, stdout.getvalue().encode(), stderr.getvalue().encode())
v = counter.audit_verdict(p)
print(json.dumps({'phase': phase, 'audit_exit': rc, 'stdout': stdout.getvalue(), 'stderr': stderr.getvalue(), 'counter_audit_verdict': v, 'counter_stub_rejected': v is not None and v[1] > 0 and v[0] < v[2]}, indent=2))
