#!/usr/bin/env python3
"""Seat-only h1 replay; requires frozen audit/tool copies in explicit scratch."""
import concurrent.futures
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess

SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer17')
OUT = Path(__file__).resolve().parent

def probe(label, audit_name, tool_name):
    spec = importlib.util.spec_from_file_location(label, SCRATCH / audit_name)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    audit.SCENARIOS = (audit.SCENARIOS[0],)
    assert audit.SCENARIOS == (('h1-trailing-space-round', {'round_line': 'Round: 1729 '}, 0, []),)
    original_git, original_run = audit.git, audit.run
    receipt = {'label': label, 'independently_expected': {'exit': 0, 'classes': [], 'stdout': 'SUMMARY claims=1 findings=0\n', 'stderr': ''}, 'git_guards': []}
    def guarded_git(d, scratch, *args):
        # Bootstrap the minimal empty Git metadata without invoking Git mutation.
        # Thus even the audit's initial `git init` has an asserted fixture root.
        d = Path(d)
        if args[0] == 'init':
            (d / '.git/objects').mkdir(parents=True)
            (d / '.git/refs/heads').mkdir(parents=True)
            (d / '.git/HEAD').write_text('ref: refs/heads/main\n')
            (d / '.git/config').write_text('[core]\nrepositoryformatversion = 0\nbare = false\n')
        if args[0] in ('init', 'add', 'commit'):
            guard = subprocess.run(['git', '-C', str(d), 'rev-parse', '--show-toplevel'], env=audit.env(scratch), capture_output=True, text=True, check=True)
            assert guard.stdout.strip() == str(d.resolve()), guard.stdout
            receipt['git_guards'].append({'before': list(args), 'stdout': guard.stdout, 'exit': guard.returncode})
        return original_git(str(d), scratch, *args)
    def retained_run(tool, args, cwd, work):
        p = original_run(tool, args, cwd, work)
        assert p is not None, 'bounded timeout'
        receipt['command'] = ['python3', '-B', tool] + args
        receipt['cwd'] = cwd
        receipt['actual'] = {'exit': p.returncode, 'classes': audit.classes(p), 'stdout': p.stdout.decode(), 'stderr': p.stderr.decode()}
        fixture = Path(args[args.index('--root') + 1])
        receipt['preregistration'] = (fixture / 'prereg.txt').read_text()
        return p
    audit.git, audit.run = guarded_git, retained_run
    # Capture audit printing without global stdout redirection in parallel workers.
    logs = []
    audit.print = lambda *args, **kwargs: logs.append(' '.join(str(x) for x in args) + '\n')
    receipt['audit_command'] = ['python3', '-B', audit_name, '--tool', tool_name, '--work', str(SCRATCH / label)]
    receipt['audit_exit'] = audit.main(['--tool', str(SCRATCH / tool_name), '--work', str(SCRATCH / label)])
    receipt['audit_stdout'] = ''.join(logs)
    (OUT / (label + '.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    return label, receipt['audit_exit'], receipt['actual'], receipt['audit_stdout']

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(probe, *case) for case in [('r44-real', 'audit44.py', 'tool.py'), ('r43-real', 'audit43.py', 'tool.py'), ('r44-mutant', 'audit44.py', 'mutant.py')]]
        for future in futures:
            print(json.dumps(future.result()))
