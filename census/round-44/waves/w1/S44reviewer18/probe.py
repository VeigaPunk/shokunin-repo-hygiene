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
OUT = LANE / '.ufo/waves/round-44/w1/S44reviewer18'
SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer18')
REV = 'd314fd6e85d62565344fa6c4b102f52f62297884'
CID = 'h2-round-spelled-x'
assert SCRATCH.is_dir()
os.chdir(SCRATCH)
receipts = {'axes': ['calibration', 'operability', 'coverage'], 'rev': REV, 'scenario': CID, 'sources': {}, 'runs': []}

def blob(rel):
    p = subprocess.run(['git', '-C', str(LANE), 'show', REV + ':' + rel], capture_output=True, check=True)
    receipts['sources'][rel] = hashlib.sha256(p.stdout).hexdigest()
    return p.stdout

try:
    tool_src = blob('tools/souji-freeze-check.py')
    (OUT / 'tool-frozen.py').write_bytes(tool_src)
    tool = SCRATCH / 'tool.py'
    tool.write_bytes(tool_src)
    # One defect: accept an optional x suffix on a decimal Round value.
    before = b'ROUND = re.compile(r"^\\ufeff?Round:[ \\t]*([1-9][0-9]*)[ \\t]*$")'
    after = b'ROUND = re.compile(r"^\\ufeff?Round:[ \\t]*([1-9][0-9]*x?)[ \\t]*$")'
    assert tool_src.count(before) == 1
    mutant_src = tool_src.replace(before, after)
    mutant = SCRATCH / 'tool-mutant.py'
    mutant.write_bytes(mutant_src)
    (OUT / 'tool-mutant.py').write_bytes(mutant_src)
    receipts['mutation'] = {'before': before.decode(), 'after': after.decode(), 'sha256': hashlib.sha256(mutant_src).hexdigest()}
    tsv = blob('census/round-44/c2-scenarios.tsv')
    (OUT / 'c2-scenarios-frozen.tsv').write_bytes(tsv)
    receipts['tsv_row'] = [line for line in tsv.decode().splitlines() if line.startswith(CID + '\t')][0]
    for round_no in (44, 43):
        rel = f'census/round-{round_no}/c2-hidden-audit.py'
        src = blob(rel)
        copied = SCRATCH / f'audit-r{round_no}.py'
        copied.write_bytes(src)
        (OUT / copied.name).write_bytes(src)
        spec = importlib.util.spec_from_file_location(f'audit{round_no}', copied)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        chosen = [row for row in mod.SCENARIOS if row[0] == CID]
        assert len(chosen) == 1
        mod.SCENARIOS = tuple(chosen)
        receipts[f'r{round_no}_expected'] = list(chosen[0])
        original_git = mod.git
        def guarded_git(d, scratch, *args):
            if args[0] in ('add', 'commit'):
                top = original_git(d, scratch, 'rev-parse', '--show-toplevel')
                assert top == str(Path(d).resolve()), (d, top)
                assert Path(d).resolve().is_relative_to(SCRATCH)
            result = original_git(d, scratch, *args)
            if args[0] == 'init':
                top = original_git(d, scratch, 'rev-parse', '--show-toplevel')
                assert top == str(Path(d).resolve()), (d, top)
            return result
        mod.git = guarded_git
        for kind, target in (('real', tool), ('mutant', mutant)):
            work = SCRATCH / f'r{round_no}-{kind}'
            actuals = []
            original_run = mod.run
            def observed_run(tool_path, args, cwd, work_path):
                p = original_run(tool_path, args, cwd, work_path)
                assert p is not None
                actuals.append({'command': ['python3', '-B', tool_path] + args, 'cwd': str(cwd), 'returncode': p.returncode, 'stdout': p.stdout.decode(), 'stderr': p.stderr.decode(), 'classes': mod.classes(p)})
                return p
            mod.run = observed_run
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                rc = mod.main(['--tool', str(target), '--work', str(work)])
            mod.run = original_run
            receipts['runs'].append({'audit': round_no, 'tool': kind, 'selection': CID, 'main_args': ['--tool', str(target), '--work', str(work)], 'returncode': rc, 'stdout': stdout.getvalue(), 'stderr': stderr.getvalue(), 'actual': actuals})
    receipts['versions'] = {}
    for args in (['python3', '--version'], ['git', '--version']):
        p = subprocess.run(args, capture_output=True, text=True)
        receipts['versions'][args[0]] = p.stdout.strip()
finally:
    shutil.rmtree(SCRATCH)
    receipts['scratch_removed'] = not SCRATCH.exists()
    (OUT / 'receipts.json').write_text(json.dumps(receipts, indent=2) + '\n')
print(json.dumps(receipts, indent=2))
