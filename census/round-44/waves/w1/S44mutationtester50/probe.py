#!/usr/bin/env python3
"""Bounded frozen-audit always-findings probe; writes only seat-owned paths."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import types

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
OUT = LANE / '.ufo/waves/round-44/w1/S44mutationtester50'
SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44mutationtester50')
REV = 'd314fd6e85d62565344fa6c4b102f52f62297884'
real_run = subprocess.run

def digest(data):
    return hashlib.sha256(data).hexdigest()

def frozen(path):
    return real_run(['git', '-C', str(LANE), 'show', REV + ':' + path], capture_output=True, check=True).stdout

# Load frozen instruments unmodified, without importing production worktree code.
def load(name, source):
    mod = types.ModuleType(name)
    exec(compile(source, name, 'exec'), mod.__dict__)
    return mod

SCRATCH.mkdir(parents=True, exist_ok=False)
receipts = {'revision': REV, 'axes': ['calibration', 'operability', 'coverage'], 'runs': []}
tool_path = SCRATCH / 'candidate.py'
try:
    audit_bytes = frozen('census/round-44/c2-hidden-audit.py')
    counter_bytes = frozen('census/round-44/c2-counter.py')
    original = frozen('tools/souji-freeze-check.py')
    counter = load('frozen_counter', counter_bytes)
    audit = load('frozen_audit', audit_bytes)
    mutant = counter.STUB_FINDINGS.encode()
    for name, data in [('frozen-audit.py', audit_bytes), ('frozen-counter.py', counter_bytes), ('original-tool.py', original), ('always-findings.py', mutant)]:
        (OUT / name).write_bytes(data)
    receipts['hashes'] = {'audit': digest(audit_bytes), 'counter': digest(counter_bytes), 'before': digest(original), 'mutant': digest(mutant)}
    # Fixture git operations are guarded without modifying frozen audit bytes.
    guards = []
    def guarded_run(argv, *args, **kwargs):
        if isinstance(argv, list) and len(argv) >= 4 and argv[0] == 'git' and argv[1] == '-C':
            d = Path(argv[2]).resolve()
            command = argv[3]
            if command in ('init', 'add', 'commit'):
                assert d.is_relative_to(SCRATCH.resolve()), str(d)
                if command != 'init':
                    top = real_run(['git', '-C', str(d), 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()
                    assert top == str(d), (top, str(d))
                    guards.append({'operation': command, 'root': top})
        return real_run(argv, *args, **kwargs)
    subprocess.run = guarded_run
    def run_audit(label, data):
        tool_path.write_bytes(data)
        stdout, stderr = io.StringIO(), io.StringIO()
        work = SCRATCH / (label + '-work')
        args = ['--tool', str(tool_path), '--work', str(work)]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = audit.main(args)
        text = stdout.getvalue()
        parsed = counter.audit_verdict(subprocess.CompletedProcess(args, rc, text.encode(), stderr.getvalue().encode()))
        item = {'label': label, 'command': ['python3', '-B', str(OUT / 'frozen-audit.py')] + args,
                'exit': rc, 'stdout': text, 'stderr': stderr.getvalue(), 'counter_audit_verdict': parsed,
                'candidate_sha256': digest(tool_path.read_bytes())}
        receipts['runs'].append(item)
        (OUT / (label + '.stdout.txt')).write_text(text)
        (OUT / (label + '.stderr.txt')).write_text(stderr.getvalue())
        return item
    baseline = run_audit('pristine', original)
    try:
        mutation = run_audit('mutated', mutant)
        # Direct invocation proves the control executes and emits its claimed finding.
        command = [sys.executable, '-B', str(tool_path), '--root', str(SCRATCH), '--prereg', 'absent.txt', '--rev', REV]
        direct = real_run(command, capture_output=True, cwd=SCRATCH, timeout=30)
        receipts['direct_control'] = {'command': command, 'exit': direct.returncode, 'stdout': direct.stdout.decode(), 'stderr': direct.stderr.decode()}
    finally:
        tool_path.write_bytes(original)
        restored = run_audit('restored', original)
        receipts['hashes']['restored'] = digest(tool_path.read_bytes())
        receipts['restored_exact'] = tool_path.read_bytes() == original
    receipts['guarded_mutations'] = len(guards)
    receipts['guard_roots'] = sorted({g['root'] for g in guards})
    receipts['verdict'] = ('inconclusive' if baseline['exit'] != 0 or restored['exit'] != 0 else
                           'killed' if mutation['exit'] == 1 and mutation['counter_audit_verdict'] is not None and mutation['counter_audit_verdict'][1] > 0 else 'survived')
finally:
    subprocess.run = real_run
    shutil.rmtree(SCRATCH)
    receipts['scratch_removed'] = not SCRATCH.exists()
    (OUT / 'receipts.json').write_text(json.dumps(receipts, indent=2) + '\n')
print(json.dumps(receipts, indent=2))
