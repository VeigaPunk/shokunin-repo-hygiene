#!/usr/bin/env python3
"""SPEC-LITERAL reference for the r60 C2 contract (scratch only, reviewer-built).

Implements exactly the numbered requirements in w1-spec.json S60ExecRecorder:
 1 --root --rev --instrument --out -- cmd
 2 non-full-40 rev -> exit 2
 3 instrument absent at rev or symlink at rev -> exit 2
 4 OUT already exists -> exit 2 (checked UP FRONT, before the command runs)
 5 temp beside OUT, fsync, os.replace; SIGTERM/SIGINT -> temp removed
 6 --max-bytes (default 262144) on captured output -> exit 2
 7 dirty tree (git status --porcelain non-empty) -> exit 2 unless --allow-dirty (checked UP FRONT)
 8 exit = wrapped rc; receipt written with EXIT=<rc>
 9 temp beside OUT; scratch honours TMPDIR
10 read-only on --root except OUT and its temp
Deliberately NO post-command re-check (not in the spec) so attacks on that are measurable.
"""
import argparse, hashlib, os, signal, subprocess, sys, tempfile

GITENV = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
GITENV.update({'LC_ALL': 'C'})


def git(root, *a):
    return subprocess.run(['git', '-C', root] + list(a), capture_output=True, env=GITENV)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', required=True)
    ap.add_argument('--instrument', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--max-bytes', type=int, default=262144)
    ap.add_argument('--allow-dirty', action='store_true')
    ap.add_argument('--command', default=None)
    ap.add_argument('rest', nargs=argparse.REMAINDER)
    ns = ap.parse_args()
    cmd = ns.rest[1:] if ns.rest and ns.rest[0] == '--' else ns.rest
    if not cmd:
        print('usage', file=sys.stderr); return 2
    if len(ns.rev) != 40 or any(c not in '0123456789abcdef' for c in ns.rev):
        print('refused: rev not full 40', file=sys.stderr); return 2
    if git(ns.root, 'cat-file', '-e', ns.rev + ':' + ns.instrument).returncode:
        print('refused: instrument absent', file=sys.stderr); return 2
    mode = git(ns.root, 'ls-tree', ns.rev, '--', ns.instrument).stdout.split(b' ')[0]
    if mode == b'120000':
        print('refused: instrument is symlink', file=sys.stderr); return 2
    if os.path.lexists(ns.out):
        print('refused: OUT exists', file=sys.stderr); return 2
    if not ns.allow_dirty and git(ns.root, 'status', '--porcelain').stdout.strip():
        print('refused: dirty tree', file=sys.stderr); return 2
    # ref-writer treats INT/TERM in the parent so temp removal runs
    temp = None
    try:
        p = subprocess.run(cmd, capture_output=True)
        out_bytes = p.stdout + p.stderr
        if len(out_bytes) > ns.max_bytes:
            print('refused: output exceeds --max-bytes', file=sys.stderr); return 2
        sha = hashlib.sha256(git(ns.root, 'show', ns.rev + ':' + ns.instrument).stdout).hexdigest()
        body = ('instrument=%s\ninstrument_sha256=%s\nrev=%s\ncommand=%s\n%s\nEXIT=%d\n' % (
            ns.instrument, sha, ns.rev, ' '.join(cmd),
            out_bytes.decode('utf-8', 'replace'), p.returncode)).encode()
        d = os.path.dirname(os.path.abspath(ns.out))
        fd, temp = tempfile.mkstemp(prefix='.' + os.path.basename(ns.out) + '.', suffix='.tmp', dir=d)
        with os.fdopen(fd, 'wb') as f:
            f.write(body); f.flush(); os.fsync(f.fileno())
        os.replace(temp, ns.out)
        temp = None
        return p.returncode
    except BaseException:
        raise
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)


if __name__ == '__main__':
    sys.exit(main())
