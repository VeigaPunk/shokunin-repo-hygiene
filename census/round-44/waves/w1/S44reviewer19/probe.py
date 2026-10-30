#!/usr/bin/env python3
"""Bounded frozen h3 audit + one malformed-heading mutant; all trees seat-local."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
OUT = LANE / '.ufo/waves/round-44/w1/S44reviewer19'
SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer19')
REV = 'd314fd6e85d62565344fa6c4b102f52f62297884'
CID = 'h3-two-unattached-keys'
EXPECTED = ['C0:HEADING-MALFORMED', 'C0:UNATTACHED-KEY', 'C0:UNATTACHED-KEY']

def frozen(rel):
    return subprocess.run(['git', '-C', str(LANE), 'show', f'{REV}:{rel}'], check=True, capture_output=True).stdout

SCRATCH.mkdir(parents=True, exist_ok=True)
os.chdir(SCRATCH)
receipts = {'revision': REV, 'scenario': CID, 'expected_exit': 1, 'expected_classes': EXPECTED,
            'versions': {cmd[0]: subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
                         for cmd in (['python3', '--version'], ['git', '--version'])}, 'sources': {}, 'runs': []}
try:
    paths = ['tools/souji-freeze-check.py', 'census/round-44/c2-hidden-audit.py',
             'census/round-43/c2-hidden-audit.py', 'census/round-44/c2-scenarios.tsv',
             'census/round-44/c2-counter.py']
    for rel in paths:
        data = frozen(rel)
        name = rel.replace('/', '__')
        (SCRATCH / name).write_bytes(data)
        (OUT / name).write_bytes(data)
        receipts['sources'][rel] = hashlib.sha256(data).hexdigest()
    tool = SCRATCH / 'tools__souji-freeze-check.py'
    source = tool.read_text()
    old = 'BADHEAD = re.compile(r"^##(?!#) *[Cc] *\\d")'
    new = 'BADHEAD = re.compile(r"^##(?!#) +[Cc] *\\d")'
    assert source.count(old) == 1
    mutant = SCRATCH / 'mutant.py'
    mutant.write_text(source.replace(old, new))
    (OUT / 'mutant.patch.txt').write_text('-' + old + '\n+' + new + '\n')
    for label, audit_name, candidate in (
        ('r44-real', 'census__round-44__c2-hidden-audit.py', tool),
        ('r43-real', 'census__round-43__c2-hidden-audit.py', tool),
        ('r44-mutant', 'census__round-44__c2-hidden-audit.py', mutant)):
        spec = importlib.util.spec_from_file_location(label, SCRATCH / audit_name)
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        audit.SCENARIOS = tuple(row for row in audit.SCENARIOS if row[0] == CID)
        assert len(audit.SCENARIOS) == 1
        row = audit.SCENARIOS[0]
        assert row[2] == 1 and sorted(row[3]) == EXPECTED
        original_git = audit.git
        def guarded_git(d, scratch, *args):
            if args[0] in ('add', 'commit'):
                top = subprocess.run(['git', '-C', d, 'rev-parse', '--show-toplevel'],
                                     env=audit.env(scratch), check=True, capture_output=True, text=True).stdout.strip()
                assert top == str(Path(d).resolve()), (top, d)
                assert Path(d).resolve().is_relative_to(SCRATCH)
            return original_git(d, scratch, *args)
        audit.git = guarded_git
        original_run = audit.run
        run_data = {'label': label, 'audit_expected_classes': row[3], 'audit_expected_exit': row[2]}
        def captured_run(candidate_tool, args, cwd, work):
            p = original_run(candidate_tool, args, cwd, work)
            assert p is not None
            run_data.update(command=['python3', '-B', str(candidate_tool)] + args,
                            cwd=cwd, tool_exit=p.returncode, tool_stdout=p.stdout.decode(),
                            tool_stderr=p.stderr.decode(), actual_classes=audit.classes(p))
            (OUT / (label + '.prereg.txt')).write_bytes((Path(args[1]) / 'prereg.txt').read_bytes())
            return p
        audit.run = captured_run
        stream = io.StringIO()
        work = str(SCRATCH / label)
        with contextlib.redirect_stdout(stream):
            rc = audit.main(['--tool', str(candidate), '--work', work])
        run_data.update(audit_exit=rc, audit_stdout=stream.getvalue())
        receipts['runs'].append(run_data)
    assert [r['audit_exit'] for r in receipts['runs']] == [0, 0, 1]
    assert receipts['runs'][0]['actual_classes'] == EXPECTED
finally:
    shutil.rmtree(SCRATCH)
    receipts['scratch_removed'] = not SCRATCH.exists()
    (OUT / 'receipts.json').write_text(json.dumps(receipts, indent=2) + '\n')
print(json.dumps(receipts, indent=2))
