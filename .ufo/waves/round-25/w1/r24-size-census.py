#!/usr/bin/env python3
"""r24 C1 counter: F2 write-safety size census over the frozen 8-case set, extended by r25 C2.

Every case builds its own repo under a /var/tmp mkdtemp removed in a finally block; nothing here
reads or writes the lane. Manifest = sorted (relpath, type, mode, size, mtime_ns, sha256 of regular
files) over the resolved common git dir, directories included; atime/ctime excluded. Case 5 adds a
second manifest over the alternate object dir(s) named by objects/info/alternates (resolved per
git's alternates rule).
r25 C2 refusal surfaces (cases 9-12, frozen in .ufo/waves/round-25/preregistration.txt):
  9 bare-nonempty: rc 0, counts line, census.invoked_from=bare, manifest unchanged;
  10 bare-empty: rc 1, stderr has "git failure" and "No default references", no counts line;
  11 subdir: rc 2, stderr has "--repo must name the repository itself";
  12 partialClone-only: rc 2, stderr has "partial-clone repository".
Cases 10-12 report manifest_changed but do not gate on it (not in the frozen predicate).
Last line: cases=C pass=P control=FALSE-GREEN-REJECTED|FALSE-GREEN-ACCEPTED
lost_found=WRITE-DETECTED|NOT-DETECTED
0: P==C, control=FALSE-GREEN-REJECTED, lost_found=WRITE-DETECTED; 1: otherwise; 2: bad input.
Precondition: git >= 2.46.0 (git --version); else `precondition=FAIL git<2.46` and exit 2.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
SCRATCH_PARENT = '/var/tmp'
TIMEOUT = 120
COUNTS = re.compile(r'garbage=(\d+) size_garbage=(\d+) unreachable=(\d+) alternates=(\d+)')
STUB = ("#!/usr/bin/env python3\n"
        "print('garbage=0 size_garbage=0 unreachable=0 alternates=0')\n")


class Scratch:
    def __init__(self, root):
        self.root = Path(root)
        home = self.root / 'home'
        home.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith('GIT_')}
        self.env.update({'LC_ALL': 'C', 'HOME': str(home), 'GIT_CONFIG_NOSYSTEM': '1',
                         'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_TERMINAL_PROMPT': '0',
                         'GIT_AUTHOR_NAME': 'r24', 'GIT_AUTHOR_EMAIL': 'r24@fixture.invalid',
                         'GIT_COMMITTER_NAME': 'r24',
                         'GIT_COMMITTER_EMAIL': 'r24@fixture.invalid',
                         'PYTHONDONTWRITEBYTECODE': '1'})

    def git(self, *args, stdin=None, check=True):
        proc = subprocess.run(['git', *map(str, args)], cwd=self.root, env=self.env, input=stdin,
                              capture_output=True, text=True, timeout=TIMEOUT)
        if check and proc.returncode:
            raise RuntimeError('git %s exit %d: %s'
                               % (args[0 if args[0] != '-C' else 2], proc.returncode,
                                  proc.stderr.strip()))
        return proc

    def repo(self, name='repo'):
        path = self.root / name
        self.git('init', '-q', '-b', 'main', path)
        (path / 'f.txt').write_text('r24 ' + name + '\n')
        self.git('-C', path, 'add', 'f.txt')
        self.git('-C', path, 'commit', '-q', '-m', 'r24 ' + name)
        return path

    def dangling(self, repo):
        return self.git('-C', repo, 'hash-object', '-w', '--stdin',
                        stdin='r24 dangling blob\n').stdout.strip()

    def common_dir(self, path):
        return Path(self.git('-C', path, 'rev-parse', '--path-format=absolute',
                             '--git-common-dir').stdout.strip())

    def census(self, tool, gitdir, *argv):
        before = manifest(gitdir)
        proc = subprocess.run([sys.executable, '-B', str(tool), *map(str, argv)], cwd=self.root,
                              env=self.env, capture_output=True, text=True, timeout=TIMEOUT)
        lines = proc.stdout.splitlines()
        match = COUNTS.fullmatch(lines[-1]) if lines else None
        counts = tuple(map(int, match.groups())) if match else None
        return proc.returncode, counts, changed(before, manifest(gitdir))

    def invoke(self, tool, gitdir, *argv):
        before = manifest(gitdir)
        proc = subprocess.run([sys.executable, '-B', str(tool), *map(str, argv)], cwd=self.root,
                              env=self.env, capture_output=True, text=True, timeout=TIMEOUT)
        return proc, changed(before, manifest(gitdir))

    def bare(self, name='bare.git', commit=True):
        path = self.root / name
        self.git('init', '-q', '--bare', '-b', 'main', path)
        if commit:
            blob = self.git('--git-dir', path, 'hash-object', '-w', '--stdin',
                            stdin='r24 ' + name + '\n').stdout.strip()
            tree = self.git('--git-dir', path, 'mktree',
                            stdin='100644 blob %s\tf.txt\n' % blob).stdout.strip()
            oid = self.git('--git-dir', path, 'commit-tree', tree,
                           '-m', 'r24 ' + name).stdout.strip()
            self.git('--git-dir', path, 'update-ref', 'refs/heads/main', oid)
        return path


@contextlib.contextmanager
def scratch():
    root = tempfile.mkdtemp(prefix='souji-r24-census-', dir=SCRATCH_PARENT)
    try:
        yield Scratch(root)
    finally:
        shutil.rmtree(root)


def manifest(gitdir):
    rows = []

    def visit(path, rel):
        st = os.lstat(path)
        mode = st.st_mode
        kind = ('d' if stat.S_ISDIR(mode) else 'f' if stat.S_ISREG(mode)
                else 'l' if stat.S_ISLNK(mode) else 'o')
        digest = hashlib.sha256(Path(path).read_bytes()).hexdigest() if kind == 'f' else ''
        rows.append((rel, kind, stat.S_IMODE(mode), st.st_size, st.st_mtime_ns, digest))
        if kind == 'd':
            for name in os.listdir(path):
                visit(os.path.join(path, name), name if rel == '.' else rel + '/' + name)

    visit(str(gitdir), '.')
    return sorted(rows)


def resolve_alternates(gitdir):
    """Resolve every objects/info/alternates line against its enclosing directory."""
    info = Path(gitdir) / 'objects' / 'info'
    lines = (info / 'alternates').read_text().splitlines()
    paths = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        path = Path(line)
        if not path.is_absolute():
            path = info / path
        paths.append(path)
    return paths


def changed(before, after):
    old = {row[0]: row for row in before}
    new = {row[0]: row for row in after}
    return sorted(key for key in old.keys() | new.keys() if old.get(key) != new.get(key))


def describe(code, counts, delta):
    shown = 'none' if counts is None else ','.join(map(str, counts))
    return 'exit=%s counts=%s manifest_changed=%d%s' % (
        code, shown, len(delta), (' first=' + delta[0]) if delta else '')


def case_clean(tool):
    with scratch() as s:
        repo = s.repo()
        code, counts, delta = s.census(tool, s.common_dir(repo), '--repo', repo)
        return code == 0 and counts == (0, 0, 0, 0) and not delta, describe(code, counts, delta)


def case_dangling(tool):
    with scratch() as s:
        repo = s.repo()
        s.dangling(repo)
        gitdir = s.common_dir(repo)
        code, counts, delta = s.census(tool, gitdir, '--repo', repo)
        lost = (gitdir / 'lost-found').exists()
        ok = code == 0 and counts is not None and counts[2] == 1 and not delta and not lost
        return ok, describe(code, counts, delta) + ' lost_found_dir=%s' % lost


def case_garbage(tool):
    with scratch() as s:
        repo = s.repo()
        gitdir = s.common_dir(repo)
        (gitdir / 'objects' / 'pack').mkdir(parents=True, exist_ok=True)
        (gitdir / 'objects' / 'pack' / 'r24-junk').write_bytes(b'j' * 2048)
        code, counts, delta = s.census(tool, gitdir, '--repo', repo)
        main_ok = (code == 0 and counts is not None and counts[0] == 1
                   and counts[1] == 2 and not delta)

        linked_repo = s.repo('repo-link')
        linked = s.root / 'linked'
        s.git('-C', linked_repo, 'worktree', 'add', '-q', linked)
        ldir = s.common_dir(linked)
        (ldir / 'objects' / 'pack').mkdir(parents=True, exist_ok=True)
        (ldir / 'objects' / 'pack' / 'r24-junk').write_bytes(b'j' * 2048)
        code_l, counts_l, delta_l = s.census(tool, ldir, '--repo', linked)
        linked_ok = (code_l == 0 and counts_l is not None and counts_l[0] == 1
                     and counts_l[1] == 2 and not delta_l)
        return main_ok and linked_ok, 'main[%s] linked[%s]' % (
            describe(code, counts, delta), describe(code_l, counts_l, delta_l))


def case_linked(tool):
    with scratch() as s:
        repo = s.repo()
        linked = s.root / 'linked'
        s.git('-C', repo, 'worktree', 'add', '-q', linked)
        code, counts, delta = s.census(tool, s.common_dir(linked), '--repo', linked)
        raw = s.git('-C', linked, 'count-objects', '-v').stdout
        found = re.search(r'^garbage: (\d+)$', raw, re.M)
        witness = int(found.group(1)) if found else None
        ok = (code == 0 and counts is not None and counts[0] == 0 and not delta
              and witness == 1)
        return ok, describe(code, counts, delta) + ' raw_linked_garbage=%s' % witness


def case_alternates(tool):
    with scratch() as s:
        repo = s.repo()
        alt = s.repo('alt')
        gitdir = s.common_dir(repo)
        (gitdir / 'objects' / 'info').mkdir(parents=True, exist_ok=True)
        (gitdir / 'objects' / 'info' / 'alternates').write_text(
            str(s.common_dir(alt) / 'objects') + '\n')
        alt_dirs = resolve_alternates(gitdir)
        alt_before = [manifest(path) for path in alt_dirs]
        code, counts, delta = s.census(tool, gitdir, '--repo', repo)
        alt_delta = sum(len(changed(before, manifest(path)))
                        for before, path in zip(alt_before, alt_dirs))
        ok = (code == 0 and counts is not None and counts[3] == 1 and not delta
              and not alt_delta)
        return ok, describe(code, counts, delta) + ' alt_manifest_changed=%d' % alt_delta


def case_refusal(tool):
    with scratch() as s:
        repo = s.repo()
        s.dangling(repo)
        code_a, counts_a, delta_a = s.census(tool, s.common_dir(repo),
                                             '--repo', repo, '--lost-found')
        src = s.repo('src')
        s.git('-C', src, 'config', 'uploadpack.allowFilter', 'true')
        partial = s.root / 'partial'
        s.git('clone', '-q', '--no-checkout', '--filter=blob:none', 'file://%s' % src,
              partial)
        gitdir = s.common_dir(partial)
        packs = list((gitdir / 'objects' / 'pack').glob('pack-*.promisor'))
        if not packs:
            raise RuntimeError('setup: clone has no .promisor pack')
        promisor = s.git('-C', partial, 'config', '--get-regexp',
                         r'^(extensions\.partialclone|remote\..*\.promisor)$', check=False)
        if not promisor.stdout.strip():
            raise RuntimeError('setup: clone lacks promisor config')
        code_b, counts_b, delta_b = s.census(tool, gitdir, '--repo', partial)
        s.git('-C', partial, 'config', '--unset', 'remote.origin.promisor')
        code_c, counts_c, delta_c = s.census(tool, gitdir, '--repo', partial)
        ok = (code_a == 2 and not delta_a and code_b == 2 and not delta_b
              and code_c == 2 and not delta_c)
        return ok, 'lost_found_argv[%s] partial_clone[%s] promisor_unset[%s]' % (
            describe(code_a, counts_a, delta_a), describe(code_b, counts_b, delta_b),
            describe(code_c, counts_c, delta_c))


def case_detector(tool):
    with scratch() as s:
        repo = s.repo()
        oid = s.dangling(repo)
        gitdir = s.common_dir(repo)
        before = manifest(gitdir)
        code = s.git('-C', repo, 'fsck', '--lost-found', check=False).returncode
        delta = changed(before, manifest(gitdir))
        written = (gitdir / 'lost-found' / 'other' / oid).is_file()
        return bool(delta) and written, 'fsck_exit=%d manifest_changed=%d lost_found_other_oid=%s' % (
            code, len(delta), written)


def case_control(tool):
    with scratch() as s:
        stub = s.root / 'stub-emitter.py'
        stub.write_text(STUB)
        failed = [name for name, check in CASES[1:5] if not run(check, stub)[0]]
        return bool(failed), 'stub_failed=%s' % (','.join(failed) or 'none')


def has_counts(stdout):
    return any(COUNTS.search(line) for line in stdout.splitlines())


def describe_proc(proc, delta, **flags):
    shown = ' '.join('%s=%s' % item for item in flags.items())
    return 'exit=%d counts_line=%s manifest_changed=%d %s' % (
        proc.returncode, has_counts(proc.stdout), len(delta), shown)


def case_bare_nonempty(tool):
    with scratch() as s:
        bare = s.bare()
        proc, delta = s.invoke(tool, s.common_dir(bare), '--repo', bare)
        lines = proc.stdout.splitlines()
        counts_last = bool(lines) and COUNTS.fullmatch(lines[-1]) is not None
        invoked = 'census.invoked_from=bare' in lines
        ok = proc.returncode == 0 and counts_last and invoked and not delta
        return ok, describe_proc(proc, delta, counts_last=counts_last, invoked_from_bare=invoked)


def case_bare_empty(tool):
    with scratch() as s:
        bare = s.bare(commit=False)
        proc, delta = s.invoke(tool, s.common_dir(bare), '--repo', bare)
        failure = 'git failure' in proc.stderr
        no_refs = 'No default references' in proc.stderr
        ok = proc.returncode == 1 and failure and no_refs and not has_counts(proc.stdout)
        return ok, describe_proc(proc, delta, git_failure=failure, no_default_refs=no_refs)


def case_subdir(tool):
    with scratch() as s:
        repo = s.repo()
        sub = repo / 'sub'
        sub.mkdir()
        proc, delta = s.invoke(tool, s.common_dir(repo), '--repo', sub)
        named = '--repo must name the repository itself' in proc.stderr
        ok = proc.returncode == 2 and named
        return ok, describe_proc(proc, delta, must_name_repo=named)


def case_partial_only(tool):
    with scratch() as s:
        repo = s.repo()
        s.git('-C', repo, 'config', 'extensions.partialClone', 'origin')
        proc, delta = s.invoke(tool, s.common_dir(repo), '--repo', repo)
        named = 'partial-clone repository' in proc.stderr
        ok = proc.returncode == 2 and named
        return ok, describe_proc(proc, delta, partial_clone_refused=named)


CASES = [('clean', case_clean), ('dangling', case_dangling), ('garbage', case_garbage),
         ('linked', case_linked), ('alternates', case_alternates), ('refusal', case_refusal),
         ('detector', case_detector), ('control', case_control),
         ('bare-nonempty', case_bare_nonempty), ('bare-empty', case_bare_empty),
         ('subdir', case_subdir), ('partialClone-only', case_partial_only)]


def run(check, tool):
    try:
        return check(tool)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        return False, 'error=%s:%s' % (type(exc).__name__, exc)


def precondition():
    try:
        proc = subprocess.run(['git', '--version'], capture_output=True, text=True,
                              timeout=TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        proc = None
    if proc is None or proc.returncode != 0:
        print('precondition=FAIL git<2.46')
        return False
    match = re.search(r'(\d+)\.(\d+)', proc.stdout)
    if not match or tuple(map(int, match.groups())) < (2, 46):
        print('precondition=FAIL git<2.46')
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool', type=Path, required=True)
    args = parser.parse_args()
    if not precondition():
        return 2
    tool = args.tool.resolve()
    if not tool.is_file() or not os.path.isdir(SCRATCH_PARENT):
        print('r24-size-census: could-not-evaluate: tool not a regular file or no '
              + SCRATCH_PARENT, file=sys.stderr)
        return 2
    passed = {}
    for number, (name, check) in enumerate(CASES, 1):
        ok, detail = run(check, tool)
        passed[name] = ok
        print('CASE %d %s %s %s' % (number, name, 'PASS' if ok else 'FAIL',
                                    ' '.join(detail.split())), flush=True)
    control = 'FALSE-GREEN-REJECTED' if passed['control'] else 'FALSE-GREEN-ACCEPTED'
    lost_found = 'WRITE-DETECTED' if passed['detector'] else 'NOT-DETECTED'
    total, good = len(passed), sum(passed.values())
    print('cases=%d pass=%d control=%s lost_found=%s' % (total, good, control, lost_found))
    ok = good == total and passed['control'] and passed['detector']
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
