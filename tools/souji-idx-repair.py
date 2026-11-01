#!/usr/bin/env python3
"""souji-idx-repair.py — receipted, fail-closed host-index repair (souji r48).

The round-47 lesson (## Mistakes row 1) mined the class: an integrator (or
index-free-helper) landing that enters HEAD while this host's frozen index
never gains the entry leaves the worktree outside the frozen Amendment-1
tolerance, so the standing landing-suite counter (census/round-46/
c1-counter.py) exits 2 could-not-evaluate at EVERY revision. Round 47
repaired that by hand (one targeted `git update-index --add --cacheinfo`
after sha256-verifying the worktree bytes equal to the HEAD blob; the r47
non-author verifier confirmed the operation honest). This tool automates
exactly that operation — no manual repair — and fail-closes on anything it
cannot prove:

  Row classes on `git status --porcelain` (LC_ALL=C):
    TOLERATED  — the frozen Amendment-1 set: staged deletions ('D  ') of
                 control-character-named HEAD paths at the measured rev.
                 Never touched, never widened.
    REPAIRABLE — staged 'D '/'M ' (or the paired '?? ') row for a
                 control-char-free path that (a) exists in the measured
                 rev's tree, (b) exists on disk, and (c) whose disk bytes
                 sha256-match the rev's blob bytes. Repaired with the rev's
                 OWN mode+blob via `git update-index --add --cacheinfo
                 <mode>,<blob>,<path>` (S271: the object is in the database;
                 this inserts it into the index without touching the object
                 database, the worktree, or any commit).
    UNEXPECTED — everything else (renames, conflicts, unquoted oddities,
                 missing files, byte mismatches, control-char names outside
                 the tolerated shape). ANY unexpected row refuses the run:
                 nothing is repaired, exit 1.

  python -B tools/souji-idx-repair.py --root LANE [--rev FULL40] [--receipt PATH]
  python -B tools/souji-idx-repair.py --selftest
  python -B tools/souji-idx-repair.py --root LANE --dry-run   (classify only)

Exit 0: worktree restored to the frozen tolerance (or already inside it);
1: findings — refusal, nothing repaired; 2: could-not-evaluate.
Mutating surface: `git update-index` on the host index ONLY. Never touches
commits, refs, the worktree, remotes, or history. Python stdlib only.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FULL40 = re.compile(r"^[0-9a-f]{40}$")

# Same short map the r46 counter uses for its Amendment-1 quote() form.
SHORT = {0x07: b'\\a', 0x08: b'\\b', 0x0c: b'\\f', 0x0a: b'\\n',
         0x0d: b'\\r', 0x09: b'\\t', 0x0b: b'\\v', 0x5c: b'\\\\',
         0x22: b'\\"'}
UNSHORT = {v: bytes([k]) for k, v in SHORT.items()}


def git(root, *args, timeout=120):
    e = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
         'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
         'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
         'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1'}
    p = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                       env=e, timeout=timeout)
    return p


def git_out(root, *args, timeout=120):
    p = git(root, *args, timeout=timeout)
    if p.returncode:
        raise ValueError('git %s failed: %s' % (
            args[0], p.stderr.decode(errors='replace').strip()[:200]))
    return p.stdout


def quote(raw: bytes) -> bytes:
    out = bytearray(b'"')
    for c in raw:
        if c in SHORT:
            out += SHORT[c]
        elif c < 0x20 or c == 0x7f:
            out += b'\\%03o' % c
        else:
            out.append(c)
    out += b'"'
    return bytes(out)


def unquote(raw: bytes):
    """C-unquote a porcelain path; None if malformed."""
    if len(raw) < 2 or not raw.startswith(b'"') or not raw.endswith(b'"'):
        return None
    body = raw[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        c = body[i]
        if c != 0x5c:
            out.append(c)
            i += 1
            continue
        if i + 1 >= len(body):
            return None
        nxt = body[i + 1:i + 2]
        if nxt in UNSHORT:
            out += UNSHORT[nxt]
            i += 2
            continue
        m = re.match(rb'\\([0-7]{3})', body[i:])
        if not m:
            return None
        out.append(int(m.group(1), 8) & 0xFF)
        i += 4
    return bytes(out)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def tree_of(root, rev):
    out = git_out(root, 'ls-tree', '-r', '-z', rev)
    entries = {}
    for rec in out.split(b'\x00'):
        if not rec:
            continue
        meta, name = rec.split(b'\t', 1)
        mode, typ, blob = meta.decode().split(' ')
        if typ == 'blob':
            entries[name.decode('utf-8', 'surrogateescape')] = (mode, blob)
    return entries


def tolerated_rows(root, rev):
    """The frozen Amendment-1 tolerated row set (counter-identical)."""
    tree = git_out(root, 'ls-tree', '-r', '--name-only', '-z', rev)
    tol = set()
    for raw in tree.split(b'\x00'):
        if raw and any(c < 0x20 or c == 0x7f for c in raw):
            tol.add(b'D  ' + quote(raw))
    return tol


def porcelain(root, untracked_all=False):
    args = ['status', '--porcelain']
    if untracked_all:
        # plain porcelain collapses a wholly-untracked directory into one
        # `?? dir/` row, which is not a path; enumeration needs per-file rows
        args += ['-uall']
    p = git(root, *args, timeout=60)
    if p.returncode:
        raise ValueError('status unavailable')
    return p.stdout.splitlines()


def classify(root, rev, rows, emit):
    tol = tolerated_rows(root, rev)
    tree = tree_of(root, rev)
    repair = {}   # path -> (mode, blob)
    unexpected = []
    ntol = 0
    for raw in rows:
        if raw in tol:
            ntol += 1
            emit('CLASS   TOLERATED-AMENDMENT1 %s' % raw.decode(errors='replace'))
            continue
        if len(raw) < 4:
            unexpected.append(raw)
            emit('CLASS   UNEXPECTED-SHORT %r' % raw)
            continue
        code, rest = raw[:3], raw[3:]
        pathb = rest
        if rest.startswith(b'"'):
            u = unquote(rest)
            if u is None:
                unexpected.append(raw)
                emit('CLASS   UNEXPECTED-QUOTE %r' % raw)
                continue
            pathb = u
        try:
            path = pathb.decode('utf-8')
        except UnicodeDecodeError:
            unexpected.append(raw)
            emit('CLASS   UNEXPECTED-DECODE %r' % raw)
            continue
        if any(ord(c) < 0x20 or ord(c) == 0x7f for c in path):
            unexpected.append(raw)
            emit('CLASS   UNEXPECTED-CONTROLCHAR %s' % path)
            continue
        kind = None
        if code == b'D  ' or code == b'M  ' or code == b'MM ' or code == b'?? ':
            kind = code[:1].decode() if code != b'?? ' else 'UNTRACKED'
        if kind is None:
            unexpected.append(raw)
            emit('CLASS   UNEXPECTED-CODE %r' % raw)
            continue
        if path not in tree:
            unexpected.append(raw)
            emit('CLASS   UNEXPECTED-NOT-IN-REV %s' % path)
            continue
        mode, blob = tree[path]
        if mode not in ('100644', '100755'):
            unexpected.append(raw)
            emit('CLASS   UNEXPECTED-MODE %s %s' % (mode, path))
            continue
        disk = Path(root) / path
        if not disk.is_file():
            unexpected.append(raw)
            emit('CLASS   UNEXPECTED-DISK-MISSING %s' % path)
            continue
        try:
            dbytes = disk.read_bytes()
        except OSError as exn:
            unexpected.append(raw)
            emit('CLASS   UNEXPECTED-DISK-READ %s %s' % (path, exn))
            continue
        blob_b = git_out(root, 'cat-file', 'blob', blob)
        if sha256(dbytes) != sha256(blob_b):
            unexpected.append(raw)
            emit('CLASS   UNEXPECTED-BYTES-DIFFER %s' % path)
            continue
        if code == b'?? ':
            # a stale landing shows the pair 'D  <p>' + '?? <p>'; require the
            # staged half somewhere in this run (checked after the loop).
            repair.setdefault(path, (mode, blob, []))[2].append(
                (b'?? ', sha256(dbytes)))
            emit('CLASS   REPAIRABLE-UNTRACKED %s sha256=%s' % (path, sha256(dbytes)))
        else:
            repair.setdefault(path, (mode, blob, []))[2].append(
                (code, sha256(dbytes)))
            emit('CLASS   REPAIRABLE-%s %s blob=%s sha256=%s'
                 % (kind, path, blob[:12], sha256(dbytes)))
    # a '??' arm without its staged 'D' partner is not a stale landing
    for path, (mode, blob, arms) in sorted(repair.items()):
        codes = {c for c, _ in arms}
        if b'?? ' in codes and not (b'D  ' in codes or b'M  ' in codes):
            unexpected.append(b'?? ' + path.encode())
            emit('CLASS   UNEXPECTED-UNPAIRED-UNTRACKED %s' % path)
    return ntol, repair, unexpected


def repair_path(root, path, mode, blob, emit):
    arg = '%s,%s,%s' % (mode, blob, path)
    p = git(root, 'update-index', '--add', '--cacheinfo', arg)
    if p.returncode:
        raise ValueError('update-index failed for %s: %s'
                         % (path, p.stderr.decode(errors='replace').strip()[:200]))
    emit('REPAIR  %s mode=%s blob=%s op=update-index--add--cacheinfo' % (path, mode, blob))


def run(root, rev, receipt_path, dry_run, emit):
    rows = porcelain(root, untracked_all=True)
    emit('REVT    %s' % rev)
    emit('BEFORE  rows=%d (porcelain -uall enumeration; the after-check below'
         ' reruns the plain form the frozen counter reads)' % len(rows))
    for r in rows:
        emit('BEFORE-ROW %s' % r.decode(errors='replace'))
    ntol, repair, unexpected = classify(root, rev, rows, emit)
    emit('CLASSES tolerated=%d repairable-paths=%d unexpected=%d'
         % (ntol, len(repair), len(unexpected)))
    if unexpected:
        for u in unexpected:
            emit('UNEXPECTED-ROW %s' % u.decode(errors='replace'))
        emit('REFUSAL fail-closed: %d unexpected row(s); nothing repaired'
             % len(unexpected))
        emit('EXIT=1')
        return 1
    if dry_run:
        emit('DRY-RUN no index write; %d path(s) would be repaired' % len(repair))
        emit('EXIT=0')
        return 0
    for path, (mode, blob, _arms) in sorted(repair.items()):
        repair_path(root, path, mode, blob, emit)
    after = porcelain(root)
    tol = tolerated_rows(root, rev)
    unexp_after = [r for r in after if r not in tol]
    emit('AFTER   rows=%d unexpected=%d' % (len(after), len(unexp_after)))
    for r in after:
        emit('AFTER-ROW %s' % r.decode(errors='replace'))
    if unexp_after:
        emit('REFUSAL post-repair state outside frozen tolerance')
        emit('EXIT=1')
        return 1
    emit('EXIT=0')
    return 0


def selftest(emit):
    """Four arms over synthetic plumbing-only repos under $TMPDIR."""
    cases = []
    base_env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
                'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
                'GIT_CONFIG_SYSTEM': os.devnull}

    def sh(repo, *args):
        p = subprocess.run(['git', '-C', repo, *args], capture_output=True,
                           env=base_env)
        if p.returncode:
            raise ValueError('git %s: %s' % (args[0], p.stderr.decode()[:200]))
        return p.stdout

    def mkrepo():
        td = tempfile.TemporaryDirectory(prefix='r48-idx-selftest-')
        repo = Path(td.name) / 'repo'
        repo.mkdir()
        sh(repo, 'init', '-q', '.')
        sh(repo, 'config', 'user.name', 'selftest')
        sh(repo, 'config', 'user.email', 'selftest@invalid')
        return td, repo

    def commit_plumbing(repo, files, parent, message):
        """Index-free commit: disk is truth, index is NOT updated."""
        tree = sh(repo, 'rev-parse', parent + '^{tree}').decode().strip() if parent \
            else '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

        def load(sha):
            entries = {}
            for rec in sh(repo, 'ls-tree', '-z', sha).split(b'\x00'):
                if not rec:
                    continue
                meta, name = rec.split(b'\t', 1)
                entries[name] = (meta, name)
            return entries

        def store(entries):
            inp = b'\x00'.join(m + b'\t' + n for n, (m, n) in entries.items()) + b'\x00'
            p = subprocess.run(['git', '-C', str(repo), 'mktree', '-z'],
                               input=inp, capture_output=True, env=base_env)
            assert p.returncode == 0, p.stderr
            return p.stdout.decode().strip()

        def insert(ents, comps, blob):
            head, rest = comps[0].encode(), comps[1:]
            if rest:
                if head in ents:
                    sub_sha = ents[head][0].split(b' ')[2].decode()
                    sub = load(sub_sha)
                else:
                    sub = {}
                insert(sub, rest, blob)
                ents[head] = (b'040000 tree ' + store(sub).encode(), head)
            else:
                ents[head] = (b'100644 blob ' + blob.encode(), head)

        for rel, data in files.items():
            p = subprocess.run(['git', '-C', str(repo), 'hash-object', '-w', '--stdin'],
                               input=data, capture_output=True, env=base_env)
            assert p.returncode == 0
            blob = p.stdout.decode().strip()
            ents = load(tree)
            insert(ents, rel.split('/'), blob)
            tree = store(ents)
        args = ['commit-tree', tree, '-m', message]
        if parent:
            args += ['-p', parent]
        p = subprocess.run(['git', '-C', str(repo)] + args, capture_output=True,
                           env=dict(base_env, GIT_AUTHOR_NAME='s', GIT_AUTHOR_EMAIL='s@i',
                                    GIT_COMMITTER_NAME='s', GIT_COMMITTER_EMAIL='s@i'))
        assert p.returncode == 0, p.stderr
        new = p.stdout.decode().strip()
        # move the branch HEAD names (the helper's compare-and-swap shape);
        # the index is never touched, which is exactly the host drift model.
        head = sh(repo, 'symbolic-ref', '-q', 'HEAD').decode().strip()
        sh(repo, 'update-ref', head, new)
        return new

    def check(name, ok, detail):
        cases.append((name, ok, detail))
        emit('SELFTEST-CASE %s %s %s' % ('pass' if ok else 'fail', name, detail))

    # Arm 1: stale-landing pair + modified-file drift -> repaired to clean.
    td, repo = mkrepo()
    try:
        c0 = commit_plumbing(repo, {'keep.txt': b'base\n'}, None, 'base')
        (repo / 'keep.txt').write_bytes(b'edited\n')
        (repo / 'new.txt').write_bytes(b'landed\n')
        c1 = commit_plumbing(repo, {'keep.txt': b'edited\n', 'new.txt': b'landed\n'},
                             c0, 'landing')
        rc = run(str(repo), c1, None, False, lambda s: None)
        st = sh(repo, 'status', '--porcelain')
        check('stale-landing-repaired', rc == 0 and st.strip() == b'',
              'rc=%d porcelain=%r' % (rc, st[:60]))
    except Exception as exn:  # noqa: BLE001
        check('stale-landing-repaired', False, 'exception %s' % exn)
    finally:
        td.cleanup()

    # Arm 2: an unrelated untracked file -> fail-closed, nothing repaired.
    td, repo = mkrepo()
    try:
        (repo / 'keep.txt').write_bytes(b'base\n')
        c0 = commit_plumbing(repo, {'keep.txt': b'base\n'}, None, 'base')
        (repo / 'new.txt').write_bytes(b'landed\n')
        c1 = commit_plumbing(repo, {'keep.txt': b'base\n', 'new.txt': b'landed\n'},
                             c0, 'landing')
        (repo / 'junk.txt').write_bytes(b'foreign\n')
        idx_before = sh(repo, 'ls-files')
        rc = run(str(repo), c1, None, False, lambda s: None)
        idx_after = sh(repo, 'ls-files')
        check('fail-closed-unexpected', rc == 1 and idx_before == idx_after,
              'rc=%d index-unchanged=%s' % (rc, idx_before == idx_after))
    except Exception as exn:  # noqa: BLE001
        check('fail-closed-unexpected', False, 'exception %s' % exn)
    finally:
        td.cleanup()

    # Arm 3: already-clean repo -> no-op exit 0.
    td, repo = mkrepo()
    try:
        (repo / 'keep.txt').write_bytes(b'base\n')
        c0 = commit_plumbing(repo, {'keep.txt': b'base\n'}, None, 'base')
        sh(repo, 'update-index', '--add', '--cacheinfo',
           '100644,' + sh(repo, 'rev-parse', c0 + ':keep.txt').decode().strip() + ',keep.txt')
        rc = run(str(repo), c0, None, False, lambda s: None)
        check('clean-noop', rc == 0, 'rc=%d' % rc)
    except Exception as exn:  # noqa: BLE001
        check('clean-noop', False, 'exception %s' % exn)
    finally:
        td.cleanup()

    # Arm 4: drift measured against an older rev (path absent there) -> refusal.
    td, repo = mkrepo()
    try:
        (repo / 'keep.txt').write_bytes(b'base\n')
        c0 = commit_plumbing(repo, {'keep.txt': b'base\n'}, None, 'base')
        (repo / 'new.txt').write_bytes(b'landed\n')
        c1 = commit_plumbing(repo, {'keep.txt': b'base\n', 'new.txt': b'landed\n'},
                             c0, 'landing')
        rc = run(str(repo), c0, None, False, lambda s: None)
        check('rev-bound-refusal', rc == 1, 'rc=%d (new.txt absent at c0)' % rc)
    except Exception as exn:  # noqa: BLE001
        check('rev-bound-refusal', False, 'exception %s' % exn)
    finally:
        td.cleanup()

    # Arm 5 (Amendment 1): a wholly-untracked landing directory — plain
    # porcelain collapses it to one `?? dir/` row, so enumeration runs -uall;
    # the landing must repair to clean.
    td, repo = mkrepo()
    try:
        (repo / 'keep.txt').write_bytes(b'base\n')
        c0 = commit_plumbing(repo, {'keep.txt': b'base\n'}, None, 'base')
        d = repo / 'newdir' / 'sub'
        d.mkdir(parents=True)
        (d / 'a.txt').write_bytes(b'aaa\n')
        (d / 'b.txt').write_bytes(b'bbb\n')
        c1 = commit_plumbing(repo, {'keep.txt': b'base\n',
                                    'newdir/sub/a.txt': b'aaa\n',
                                    'newdir/sub/b.txt': b'bbb\n'},
                             c0, 'landing')
        plain = sh(repo, 'status', '--porcelain')
        rc = run(str(repo), c1, None, False, lambda s: None)
        st = sh(repo, 'status', '--porcelain')
        check('collapsed-untracked-dir-repaired',
              rc == 0 and st.strip() == b'' and b'newdir' in plain,
              'rc=%d plain-had-collapse-row=%s after=%r'
              % (rc, b'newdir' in plain, st[:40]))
    except Exception as exn:  # noqa: BLE001
        check('collapsed-untracked-dir-repaired', False, 'exception %s' % exn)
    finally:
        td.cleanup()

    npass = sum(1 for _, ok, _ in cases if ok)
    emit('SELFTEST cases=%d pass=%d fail=%d' % (len(cases), npass, len(cases) - npass))
    return 0 if npass == len(cases) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root')
    ap.add_argument('--rev', default='HEAD')
    ap.add_argument('--receipt', default=None,
                    help='write the receipt to this path (also stdout)')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    ns = ap.parse_args()
    lines = []

    def emit(s):
        lines.append(s)
        print(s)

    try:
        if ns.selftest:
            rc = selftest(emit)
        else:
            if not ns.root:
                raise ValueError('--root required without --selftest')
            root = str(Path(ns.root).resolve())
            rev = ns.rev
            if rev != 'HEAD' and not FULL40.match(rev):
                raise ValueError('full 40-hex --rev (or HEAD) required')
            if rev == 'HEAD':
                rev = git_out(root, 'rev-parse', 'HEAD').decode().strip()
                if not FULL40.match(rev):
                    raise ValueError('HEAD unresolved')
            tool = Path(__file__).resolve()
            emit('TOOL    %s sha256=%s' % (tool.name, sha256(tool.read_bytes())))
            rc = run(root, rev, ns.receipt, ns.dry_run, emit)
    except (OSError, ValueError, subprocess.SubprocessError, UnicodeError) as exn:
        emit('COULD-NOT-EVALUATE %s' % exn)
        emit('EXIT=2')
        rc = 2
    if ns.receipt and not ns.selftest:
        Path(ns.receipt).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return rc


if __name__ == '__main__':
    sys.exit(main())
