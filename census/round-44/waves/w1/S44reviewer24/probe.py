#!/usr/bin/env python3
"""Run only frozen h8; all fixture mutations stay in the seat scratch."""
import ast
import concurrent.futures
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

ROOT = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
OUT = ROOT / '.ufo/waves/round-44/w1/S44reviewer24'
SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44reviewer24')
REV = 'd314fd6e85d62565344fa6c4b102f52f62297884'
CID = 'h8-crlf-prereg'
SCRATCH.mkdir(parents=True, exist_ok=True)
os.chdir(SCRATCH)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True
receipts = {'revision': REV, 'scenario': CID, 'expected': {'exit': 0, 'classes': [], 'stdout': 'SUMMARY claims=1 findings=0\n', 'stderr': ''}, 'sources': {}, 'runs': {}}

def frozen(rel):
    cmd = ['git', '-C', str(ROOT), 'show', REV + ':' + rel]
    p = subprocess.run(cmd, capture_output=True, check=True)
    receipts['sources'][rel] = {'command': cmd, 'sha256': hashlib.sha256(p.stdout).hexdigest()}
    (OUT / (rel.replace('/', '__'))).write_bytes(p.stdout)
    return p.stdout.decode()

try:
    tool_src = frozen('tools/souji-freeze-check.py')
    audit_src = {r: frozen('census/round-' + r + '/c2-hidden-audit.py') for r in ('44', '43')}
    frozen('census/round-44/c2-scenarios.tsv')
    frozen('census/round-44/c2-counter.py')
    frozen('census/round-44/preregistration.txt')
    tool = SCRATCH / 'checker.py'
    tool.write_text(tool_src)
    # One semantic defect: CRLF-aware claim splitting replaced with LF-only splitting.
    tree = ast.parse(tool_src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'parse_claims')
    class LfOnly(ast.NodeTransformer):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'splitlines' and isinstance(node.func.value, ast.Name) and node.func.value.id == 'text':
                return ast.copy_location(ast.Call(func=ast.Attribute(value=ast.Name(id='text', ctx=ast.Load()), attr='split', ctx=ast.Load()), args=[ast.Constant('\n')], keywords=[]), node)
            return self.generic_visit(node)
    LfOnly().visit(fn)
    mutant = SCRATCH / 'checker-lf-only.py'
    mutant.write_text(ast.unparse(ast.fix_missing_locations(tree)) + '\n')
    (OUT / 'mutant-description.txt').write_text("parse_claims only: text.splitlines() -> text.split('\\n'); every other checker AST node unchanged.\n")
    for r, src in audit_src.items():
        path = SCRATCH / ('audit-' + r + '.py')
        path.write_text(src)
    def exercise(label, r, candidate):
        spec = importlib.util.spec_from_file_location('audit_' + label, SCRATCH / ('audit-' + r + '.py'))
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        audit.SCENARIOS = tuple(row for row in audit.SCENARIOS if row[0] == CID)
        assert len(audit.SCENARIOS) == 1
        original_git, original_run = audit.git, audit.run
        checks = []
        def guarded_git(d, scratch, *args):
            if args[0] in ('add', 'commit'):
                top = original_git(d, scratch, 'rev-parse', '--show-toplevel')
                assert Path(top).resolve() == Path(d).resolve(), (top, d)
                checks.append({'before': list(args), 'toplevel': top})
            # git init creates the new fixture, before it has a toplevel to assert.
            return original_git(d, scratch, *args)
        observed = []
        def recording_run(tool, args, cwd, work):
            prereg = Path(args[args.index('--root') + 1]) / 'prereg.txt'
            raw = prereg.read_bytes()
            (OUT / (label + '.prereg.bin')).write_bytes(raw)
            result = original_run(tool, args, cwd, work)
            observed.append({'command': ['python3', '-B', tool] + args, 'cwd': cwd, 'exit': result.returncode, 'stdout': result.stdout.decode(), 'stderr': result.stderr.decode(), 'classes': audit.classes(result), 'crlf_count': raw.count(b'\r\n'), 'bare_lf_count': raw.count(b'\n') - raw.count(b'\r\n')})
            return result
        audit.git, audit.run = guarded_git, recording_run
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            rc = audit.main(['--tool', str(candidate), '--work', str(SCRATCH / label)])
        return {'audit_exit': rc, 'audit_stdout': capture.getvalue(), 'oracle_row': audit.SCENARIOS[0], 'actual': observed, 'fixture_root_checks': checks}
    # Audit main redirects Python stdout globally; use sequential calls to preserve exact receipts.
    for label, r, candidate in [('v2-real', '44', tool), ('r43-real', '43', tool), ('v2-lf-mutant', '44', mutant)]:
        receipts['runs'][label] = exercise(label, r, candidate)
    receipts['runtime'] = {'python': sys.version, 'git': subprocess.run(['git', '--version'], capture_output=True, text=True, check=True).stdout.strip()}
finally:
    (OUT / 'receipts.json').write_text(json.dumps(receipts, indent=2) + '\n')
    shutil.rmtree(SCRATCH)
print(json.dumps(receipts, indent=2))
