#!/usr/bin/env python3
"""Read-only frozen-code review probes; mocks are explicitly labelled."""
import contextlib
import io
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile
import types
from unittest.mock import patch

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SEAT = LANE / '.ufo/waves/round-43/w1/R43reviewer01'
REV = 'f8c805dbfa7f45814cf9a7270fa8bbffb41a8373'
S = Path('/fast/scratch/hyaku/souji-r43/R43reviewer01')
S.mkdir(parents=True, exist_ok=True)
os.environ['TMPDIR'] = str(S)
tempfile.tempdir = str(S)

def blob(rev, path):
    p = subprocess.run(['git', '-C', str(LANE), 'show', rev + ':' + path], capture_output=True)
    return p.stdout if p.returncode == 0 else None

def load(name):
    return runpy.run_path(str(SEAT / name), run_name='review_import')

def capture_main(g, scratch):
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            rc = g['main'](['--root', str(LANE), '--rev', REV, '--scratch', str(scratch)])
        print('return=', rc, 'stdout=', out.getvalue().strip())
    except Exception as exc:
        print('exception=', type(exc).__name__, str(exc), 'stdout=', out.getvalue().strip())
    print('leftovers=', sorted(p.name.split('-')[0] for p in scratch.iterdir()))

try:
    c1, c2, c3, fx = [load(n) for n in ('c1-counter.py', 'c2-counter.py', 'c3-counter.py', 'r43-correction-prose.py')]
    print('AXES calibration / operability / coverage')
    print('PROBE wrapper compile (literal frozen WRAPPER):')
    try:
        compile(c3['WRAPPER'], 'shim_wrapper.py', 'exec')
        print('compile=ok')
    except SyntaxError as exc:
        print('compile=SyntaxError line=%d text=%s' % (exc.lineno, exc.text.strip()))
    tool = blob(REV, c3['TOOL']).decode()
    print('PROBE SNIFF over all EQUIV substitutions (real frozen tool bytes):')
    for mid, old, new in c3['EQUIV']:
        text = tool.replace(old, new)
        absent = [m for m, o, _ in c3['MUTANTS'] if o not in text]
        print(mid, 'absent_MUTANTS_anchors=', absent)
    print('PROBE c1 candidate-derived mismatch (real committed rederive blobs; mocked append evaluator success):')
    original_show = c1['show']
    req = blob(REV, c1['REQUIRED'])
    lesson = fx['GOOD43'].replace('derived=rows=174', 'derived=rows=999')
    needed = {(REV, c1['REQUIRED']): req, (REV, c1['LESSON']): lesson.encode(),
              (c1['BASE'], c1['SCORECARD']): blob(c1['BASE'], c1['SCORECARD']),
              (c1['BASE'], c1['TOOL']): blob(c1['BASE'], c1['TOOL'])}
    for row in req.decode().splitlines()[1:]:
        f = row.split('\t')
        for path in (f[1], c1['SOURCES']):
            needed[(f[5], path)] = blob(f[5], path)
    g1 = c1['main'].__globals__
    g1['show'] = lambda root, rev, path, scratch: needed.get((rev, path))
    actual_git = g1['git']
    g1['git'] = lambda *args: types.SimpleNamespace(returncode=0, stdout=b'')
    g1['subprocess'] = types.SimpleNamespace(PIPE=subprocess.PIPE, run=lambda *a, **kw: types.SimpleNamespace(returncode=0, stdout=b'', stderr=b''))
    d = S / 'c1-derived'; d.mkdir()
    capture_main(c1, d)
    print('PROBE c1 evaluator refusal rc=2 (mock injection):')
    g1['subprocess'] = types.SimpleNamespace(PIPE=subprocess.PIPE, run=lambda *a, **kw: types.SimpleNamespace(returncode=2, stdout=b'', stderr=b'REFUSAL injected'))
    d = S / 'c1-refusal'; d.mkdir()
    capture_main(c1, d)
    print('PROBE exception cleanup c1/c2/c3 (mock operational failures after work creation):')
    def timeout(*a, **kw):
        raise subprocess.TimeoutExpired('injected evaluator', 600)
    g1['subprocess'] = types.SimpleNamespace(PIPE=subprocess.PIPE, run=timeout)
    d = S / 'c1-exception'; d.mkdir(); capture_main(c1, d)
    def failure(*a, **kw):
        raise OSError('injected scratch I/O failure')
    g2 = c2['main'].__globals__
    g2['build'] = failure
    d = S / 'c2-exception'; d.mkdir(); capture_main(c2, d)
    g3 = c3['main'].__globals__
    g3['run_fixture'] = failure
    old_show3 = g3['show']
    g3['show'] = lambda root, rev, path, scratch: b'# injected fixture' if path == g3['FIXTURE'] else old_show3(root, rev, path, scratch)
    d = S / 'c3-exception'; d.mkdir(); capture_main(c3, d)
    print('PROBE actual CLI scratch-file errors (unmodified frozen copies):')
    bad = S / 'not-a-directory'; bad.write_text('x')
    for n in ('c1-counter.py', 'c2-counter.py', 'c3-counter.py'):
        p = subprocess.run(['python3', '-B', str(SEAT/n), '--root', str(LANE), '--rev', REV, '--scratch', str(bad)], capture_output=True, env=dict(os.environ, TMPDIR=str(S)))
        print(n, 'rc=', p.returncode, 'summary=', 'SUMMARY' in p.stdout.decode(), 'error=', p.stderr.decode().splitlines()[-1])
    print('PROBE fixture r42 lesson actual strip victims:')
    lesson42 = blob(fx['R42_TIP'], 'corpus/lessons/round-42.md').decode()
    for i, line in enumerate(lesson42.splitlines(), 1):
        if line.startswith('CORRECTION-'):
            print('line=%d %s' % (i, line))
    print('PROBE synthetic non-correction prose strip:')
    prose = 'CORRECTION-DE is the literal marker described here, not a record.'
    print('input=', prose, 'kept=', not prose.startswith('CORRECTION-DE') and not prose.startswith('CORRECTION-'))
finally:
    shutil.rmtree(S)
    print('scratch_removed=', not S.exists())
