#!/usr/bin/env python3
"""Only frozen scenario h6; guard every fixture git mutation and retain exact I/O."""
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer22')
OUT = Path(__file__).resolve().parent
ORIGINAL_RUN = subprocess.run
RECORDS = []

def guarded_run(argv, *args, **kwargs):
    if argv and argv[0] == 'git' and '-C' in argv:
        d = Path(argv[argv.index('-C') + 1]).resolve()
        assert d.is_relative_to(SCRATCH), d
        op = argv[argv.index('-C') + 2]
        if op in ('add', 'commit'):
            identity = ORIGINAL_RUN(['git', '-C', str(d), 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True)
            assert identity.stdout.strip() == str(d), identity.stdout
    p = ORIGINAL_RUN(argv, *args, **kwargs)
    if argv and argv[0] == 'python3' and '--root' in argv:
        RECORDS.append({'argv': argv, 'cwd': str(kwargs.get('cwd')), 'exit': p.returncode,
                        'stdout': p.stdout.decode(), 'stderr': p.stderr.decode()})
    return p

subprocess.run = guarded_run

def exercise(label, audit_name, tool_name):
    spec = importlib.util.spec_from_file_location(label, SCRATCH / audit_name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    selected = mod.SCENARIOS[5]
    assert selected[0] == 'h6-duplicate-three-occurrences'
    mod.SCENARIOS = (selected,)
    work = SCRATCH / label
    argv = ['--tool', str(SCRATCH / tool_name), '--work', str(work)]
    print('COMMAND: copied ' + audit_name + ' SCENARIOS=(SCENARIOS[5],); main(' + repr(argv) + ')', flush=True)
    rc = mod.main(argv)
    print(label + ' EXIT=' + str(rc), flush=True)
    return {'label': label, 'expected_exit': selected[2], 'expected_classes': selected[3], 'audit_exit': rc}

os.chdir(SCRATCH)
cases = [('v2-real', 'audit-v2.py', 'tool.py'), ('r43-real', 'audit-r43.py', 'tool.py'), ('v2-mutant', 'audit-v2.py', 'mutant.py')]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(lambda args: exercise(*args), cases))
(OUT / 'results.json').write_text(json.dumps({'results': results, 'invocations': RECORDS}, indent=2) + '\n')
for record in RECORDS:
    print('EXACT_TOOL_RESULT ' + json.dumps(record, sort_keys=True))
assert [r['audit_exit'] for r in results] == [0, 1, 1]
