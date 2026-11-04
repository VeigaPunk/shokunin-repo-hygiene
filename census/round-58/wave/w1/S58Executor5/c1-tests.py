#!/usr/bin/env python3
"""Pinned C1 behavioral probes; stdlib only. Run with python -B.

Writes only this seat's delivery and scratch, removes scratch after evidence save.
No production mutation. No Markdown parsing claim.
"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

SOURCE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SCRATCH = Path('/fast/scratch/hyaku/souji-r58/S58Executor5')
DELIVERY = SOURCE / '.ufo/waves/round-58/w1/S58Executor5'
FROZEN = 'e7f64f30324e8ddb3f2266302daa9066054cdbb3'
PATHS = ('SCORECARD.md', 'census/round-57/records/c1-matrix-v5.tsv',
         'census/round-57/records/c1-matrix-v6.tsv', 'census/round-58/c1-counter.py')
ENV = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
ENV.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
           GIT_AUTHOR_NAME='C1 fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid',
           GIT_COMMITTER_NAME='C1 fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid',
           PYTHONDONTWRITEBYTECODE='1')
TRANSCRIPT = []
RESULTS = []


def run(argv, expected=0):
    result = subprocess.run(list(map(str, argv)), cwd=SCRATCH, env=ENV,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    TRANSCRIPT.append('$ ' + shlex.join(list(map(str, argv))) + '\nSTDOUT:\n'
                      + result.stdout.decode() + '\nSTDERR:\n'
                      + result.stderr.decode() + f'\nEXIT {result.returncode}\n')
    if expected is not None and result.returncode != expected:
        raise AssertionError(f'{argv}: expected EXIT {expected}, got {result.returncode}')
    return result


def guard(root):
    observed = run(['git', '-C', root, 'rev-parse', '--show-toplevel']).stdout.decode().strip()
    if observed != str(root):
        raise AssertionError(f'Fixture toplevel mismatch: {observed!r} != {str(root)!r}')


def commit(root, message):
    guard(root)
    run(['git', '-C', root, 'add', '--', *PATHS])
    guard(root)
    run(['git', '-C', root, '-c', 'core.hooksPath=/dev/null', 'commit', '--no-gpg-sign', '-m', message])
    return run(['git', '-C', root, 'rev-parse', 'HEAD']).stdout.decode().strip()


def fixture(name, blobs):
    root = SCRATCH / name
    root.mkdir()
    # A pre-existing enclosing checkout must never receive fixture mutations.
    pre = run(['git', '-C', root, 'rev-parse', '--show-toplevel'], expected=None)
    if pre.returncode != 128:
        raise AssertionError('Fixture unexpectedly belongs to an existing checkout')
    run(['git', '-C', root, 'init', '--initial-branch=fixture'])
    guard(root)
    for path, content in blobs.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return root


def probe(name, root, revision, mismatches, notes=None):
    result = run([sys.executable, '-B', root / PATHS[3], '--root', root,
                  '--rev', revision], expected=int(bool(mismatches)))
    lines = result.stdout.decode().splitlines()
    summary = (f'SUMMARY assertions=2 mismatches={mismatches} '
               'carry_identical=34 exit_zero=10,8')
    if len(lines) != 3 or lines[-1] != summary:
        raise AssertionError(f'{name}: unexpected complete output {lines!r}')
    if sum(line.startswith('MISSING ') for line in lines[:2]) != mismatches:
        raise AssertionError(f'{name}: inconsistent missing-note count')
    if notes is not None:
        expected_lines = [('MATCH ' if note in (root / 'SCORECARD.md').read_text() else 'MISSING ') + note
                          for note in notes]
        if lines[:2] != expected_lines:
            raise AssertionError(f'{name}: wrong individual note findings')
    RESULTS.append({'case': name, 'revision': revision, 'exit': result.returncode,
                    'stdout': result.stdout.decode(), 'mismatches': mismatches})
    return lines


def main():
    if SCRATCH.exists():
        raise RuntimeError('Refusing to overwrite existing scratch')
    SCRATCH.mkdir(parents=True)
    DELIVERY.mkdir(parents=True, exist_ok=True)
    try:
        run([sys.executable, '--version'])
        run(['git', '--version'])
        blobs = {}
        for path in PATHS:
            blobs[path] = run(['git', '-C', SOURCE, 'show', FROZEN + ':' + path]).stdout
            retained = DELIVERY / 'inputs' / path
            retained.parent.mkdir(parents=True, exist_ok=True)
            retained.write_bytes(blobs[path])
        hashes = {p: hashlib.sha256(b).hexdigest() for p, b in blobs.items()}
        base = fixture('base-and-remedy', blobs)
        base_rev = commit(base, 'Frozen C1 base fixture')
        missing = probe('base', base, base_rev, 2)
        notes = [line.removeprefix('MISSING ') for line in missing[:2]]
        if not all(line.startswith('MISSING ') for line in missing[:2]):
            raise AssertionError('Base did not emit two exact MISSING notes')
        original = blobs['SCORECARD.md']
        appended = ('\n' + '\n'.join(notes) + '\n').encode()
        (base / 'SCORECARD.md').write_bytes(original + appended)
        target_rev = commit(base, 'Append two measured calibration notes')
        probe('append-two-notes', base, target_rev, 0, notes)
        if not (base / 'SCORECARD.md').read_bytes().startswith(original):
            raise AssertionError('Remedy was not append-only')
        for removed in range(2):
            amended = dict(blobs)
            amended['SCORECARD.md'] = original + ('\n' + notes[1 - removed] + '\n').encode()
            root = fixture(f'delete-note-{removed + 1}', amended)
            revision = commit(root, f'Delete correction note {removed + 1} from remedy')
            probe(f'delete-note-{removed + 1}', root, revision, 1, notes)
        junk = dict(blobs)
        junk['SCORECARD.md'] = original + b'\nR58-CALIBRATION unrelated junk note; all fixed.\n'
        root = fixture('junk-note', junk)
        revision = commit(root, 'Append unrelated calibration junk')
        probe('junk-note', root, revision, 2, notes)
        (DELIVERY / 'results.json').write_text(json.dumps(
            {'frozen': FROZEN, 'input_sha256': hashes, 'notes': notes,
             'results': RESULTS, 'append_only': True}, indent=2) + '\n')
        TRANSCRIPT.append('PASS all five assigned C1 legs; append-only prefix preserved.\n')
        print('PASS base=2 append=0 delete-note-1=1 delete-note-2=1 junk=2')
    finally:
        (DELIVERY / 'receipts.txt').write_text('\n'.join(TRANSCRIPT))
        shutil.rmtree(SCRATCH)
        with (DELIVERY / 'receipts.txt').open('a') as receipt:
            receipt.write('\nCLEANUP removed own scratch after saving evidence.\n')


if __name__ == '__main__':
    main()
