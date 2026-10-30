#!/usr/bin/env python3
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import shutil
import subprocess

SEAT = Path('/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43reviewer04')
S = Path('/fast/scratch/hyaku/souji-r43/R43reviewer04')
S.mkdir(parents=True, exist_ok=True)
os.environ['TMPDIR'] = str(S)
spec = importlib.util.spec_from_file_location('hidden', SEAT / 'hidden.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
real_subprocess_run = subprocess.run
real_run = h.run
log = []

def guarded_run(args, *pos, **kw):
    if args[0] == 'git' and '-C' in args:
        d = args[args.index('-C') + 1]
        if any(x in args for x in ('add', 'commit')):
            root = real_subprocess_run(['git', '-C', d, 'rev-parse', '--show-toplevel'], capture_output=True, text=True, env=h.env(str(S)), check=True).stdout.strip()
            assert root == d, (root, d)
    return real_subprocess_run(args, *pos, **kw)

def observed_run(tool, args, cwd, work):
    d = args[args.index('--root') + 1]
    tip = args[args.index('--rev') + 1]
    path = args[args.index('--prereg') + 1]
    cid = Path(d).name
    def git(*a):
        return real_subprocess_run(['git', '-C', d, *a], capture_output=True, text=True, env=h.env(str(S)), check=True).stdout
    if cid == 'h6-duplicate-three-occurrences':
        freeze = git('log', '--diff-filter=A', '--no-renames', '--full-history', '--reverse', '--format=%H', tip, '--', path).splitlines()[0]
        old = git('show', freeze + ':' + path)
        new = git('show', tip + ':' + path)
        log.append('h6 freeze_Base_count=%d rev_Base_count=%d prereg_changed=%s freeze_is_tip=%s' % (old.count('\nBase: '), new.count('\nBase: '), old != new, freeze == tip))
    if cid == 'h5-control-symlink-exit0-text':
        log.append('h5 tree=' + git('ls-tree', tip, '--', 'census/control.txt').strip())
        log.append('h5 link_blob=' + repr(git('show', tip + ':census/control.txt')))
    if cid in ('h7-dispatch-notes-ready', 'h9-dispatch-depth-three'):
        log.append(cid + ' dispatch_tree=' + repr(git('ls-tree', '-r', '--name-only', tip, '--', '.ufo/waves/round-1729/')))
    if cid == 'h8-crlf-prereg':
        raw = real_subprocess_run(['git', '-C', d, 'show', tip + ':' + path], capture_output=True, env=h.env(str(S)), check=True).stdout
        log.append('h8 CRLF=%d LF=%d bare_LF=%d' % (raw.count(b'\r\n'), raw.count(b'\n'), raw.count(b'\n') - raw.count(b'\r\n')))
    p = real_run(tool, args, cwd, work)
    log.append(cid + ' rc=' + str(p.returncode) + ' stdout=' + repr(p.stdout.decode()) + ' stderr=' + repr(p.stderr.decode()))
    return p

try:
    subprocess.run = guarded_run
    h.run = observed_run
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        rc = h.main(['--tool', str(SEAT / 'freeze.py'), '--work', str(S / 'audit')])
    print('COMMAND: imported frozen hidden.main --tool <seat>/freeze.py --work <seat scratch>/audit; commit/add guarded by exact root assertion')
    print(stream.getvalue(), end='')
    print('audit_exit=%d' % rc)
    print('\n'.join(log))
    p = subprocess.CompletedProcess([], 1, stdout=(b'FINDING C0 HEADING-MALFORMED line=12\nFINDING C0 UNATTACHED-KEY line=13\n' + b'FINDING C2 FIELD-MISSING x\n' * 4))
    want = h.SCENARIOS[3][3]
    print('h4 normative_emission_classes=' + repr(h.classes(p)))
    print('h4 frozen_expected_classes=' + repr(sorted(want)))
    print('h4 normative_emission_accepted=' + repr(h.classes(p) == sorted(want)))
finally:
    subprocess.run = real_subprocess_run
    shutil.rmtree(S)
    print('scratch_removed=' + str(not S.exists()))
