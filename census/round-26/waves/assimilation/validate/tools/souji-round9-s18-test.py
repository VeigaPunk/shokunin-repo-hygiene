#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser()
parser.add_argument('--tool-dir', type=Path, default=Path(__file__).resolve().parent)
parser.add_argument('--suffix', default='.r9-s18')
parser.add_argument('--observe', action='store_true')
args = parser.parse_args()
root = Path(tempfile.mkdtemp(prefix='souji-r9-s18-battery.', dir='/var/tmp'))
env = dict(os.environ, TMPDIR='/var/tmp', GIT_AUTHOR_NAME='S18 fixture',
           GIT_AUTHOR_EMAIL='s18@fixture.invalid', GIT_COMMITTER_NAME='S18 fixture',
           GIT_COMMITTER_EMAIL='s18@fixture.invalid', GIT_CONFIG_NOSYSTEM='1',
           GIT_CONFIG_GLOBAL='/dev/null', GIT_OPTIONAL_LOCKS='0')
results = []


def run(argv, *, extra=None, data=None):
    return subprocess.run([str(x) for x in argv], env=env | (extra or {}),
                          input=data, text=True, capture_output=True, timeout=30)


def git(repo, *argv, data=None):
    p = run(['git', '-C', repo, *argv], data=data)
    if p.returncode:
        raise RuntimeError((argv, p.returncode, p.stderr))
    return p.stdout.strip()


def tool(name):
    return args.tool_dir.resolve() / f'souji-{name}{args.suffix}.sh'


def repo_case(name):
    fleet = root / name
    repo = fleet / 'case-shokunin'
    run(['git', 'init', '-q', '--initial-branch=main', repo]).check_returncode()
    (repo / 'keep').mkdir()
    (repo / 'keep' / 'file.txt').write_text('saved payload\n')
    sha = commit(repo)
    git(repo, 'update-ref', 'refs/remotes/origin/main', sha)
    git(repo, 'symbolic-ref', 'refs/remotes/origin/HEAD', 'refs/remotes/origin/main')
    return fleet, repo, sha


def commit(repo, parent=None, detached=False):
    git(repo, 'add', '-A')
    tree = git(repo, 'write-tree')
    opts = ['commit-tree', tree]
    if parent:
        opts.extend(['-p', parent])
    sha = git(repo, *opts, data='fixture commit\n')
    git(repo, 'update-ref', '--no-deref' if detached else 'HEAD', *(('HEAD', sha) if detached else (sha,)))
    return sha


def record(name, p, passed, **details):
    results.append(dict(case=name, passed=bool(passed), rc=p.returncode,
                        output=p.stdout.strip(), stderr=p.stderr.strip(), **details))


def verify_pair(name, fleet, repo, target, ledger=None, expected='NOT-SAFE'):
    for engine in ('verify', 'vault-verify'):
        extra = dict(SHOKUNIN_ROOT=str(fleet), SOUJI_LEDGER=str(ledger or fleet / 'empty.tsv'))
        argv = ['bash', tool(engine), '--json']
        if engine == 'vault-verify':
            argv += ['--fallback']
        argv += ['--', target]
        p = run(argv, extra=extra)
        try:
            verdict = json.loads(p.stdout)['verdict']
        except (json.JSONDecodeError, KeyError):
            verdict = 'INVALID-VERDICT'
        record(f'{name}/{engine}', p, p.returncode == 0 and verdict == expected,
               expected=expected, adversarial=expected == 'NOT-SAFE')


def quarantine(name, fleet, repo, target, *, hook=None, ledger=None, outside=None,
               expect_deleted=False):
    assert repo.is_relative_to(root) and root.is_relative_to(Path('/var/tmp'))
    extra = dict(SOUJI_VERIFY_BIN=str(tool('verify')), SOUJI_Q_SHOKUNIN_ROOT=str(fleet),
                 SOUJI_Q_LEDGER=str(ledger or fleet / 'empty.tsv'),
                 SOUJI_QUARANTINE_ALLOW_LIVE='1')
    if hook:
        extra.update(SOUJI_Q_SELFTEST_ACTIVE='1', SOUJI_Q_TEST_HOOK=str(hook))
    p = run(['bash', tool('quarantine'), '--hold', '0', repo, target], extra=extra)
    deleted = any(line.startswith('RESULT\t') and '\tDELETED\t' in line for line in p.stdout.splitlines())
    outside_write = outside is not None and any(outside.iterdir())
    staged = repo / '.ufo-quarantine' / time.strftime('%Y-%m-%d', time.gmtime()) / target.relative_to(repo)
    preserved = target.exists() or staged.exists()
    if expect_deleted:
        passed = p.returncode == 0 and deleted and not preserved
    else:
        passed = p.returncode == 3 and not deleted and not outside_write and preserved
    record(name, p, passed, deleted=deleted, adversarial=not expect_deleted,
           outside_write=outside_write, source_exists=target.exists(), preserved=preserved)


fleet, repo, sha = repo_case('dirty')
target = repo / 'keep/file.txt'
target.write_text('uncommitted new payload\n')
verify_pair('dirty-pushed', fleet, repo, target)

fleet, repo, sha = repo_case('detached')
target = repo / 'keep/file.txt'
target.write_text('detached new payload\n')
commit(repo, sha, detached=True)
verify_pair('detached-unpushed', fleet, repo, target)

fleet, repo, sha = repo_case('dir-untracked')
(repo / 'keep/local-only.txt').write_text('only local copy\n')
verify_pair('directory-untracked-child', fleet, repo, repo / 'keep')
quarantine('directory-untracked-child/quarantine', fleet, repo, repo / 'keep')

fleet, repo, sha = repo_case('dir-ignored')
(repo / '.gitignore').write_text('keep/local-only.txt\n')
(repo / 'keep/local-only.txt').write_text('only ignored copy\n')
verify_pair('directory-ignored-child', fleet, repo, repo / 'keep')
quarantine('directory-ignored-child/quarantine', fleet, repo, repo / 'keep')

fleet, repo, sha = repo_case('hidden-ref')
(repo / '.scratch').mkdir()
target = repo / '.scratch/active.out'
target.write_text('old payload\n')
os.utime(target, (time.time() - 3 * 86400,) * 2)
(repo / '.active-reference').write_text('active.out is still required\n')
verify_pair('hidden-live-reference', fleet, repo, target)
quarantine('hidden-live-reference/quarantine', fleet, repo, target)

fleet, repo, sha = repo_case('fresh-child')
target = repo / '.scratch/bundle'
target.mkdir(parents=True)
(target / 'recent.txt').write_text('fresh work\n')
os.utime(target, (time.time() - 3 * 86400,) * 2)
verify_pair('stale-directory-fresh-child', fleet, repo, target)
quarantine('stale-directory-fresh-child/quarantine', fleet, repo, target)

fleet, repo, sha = repo_case('stale-unpushed')
(repo / '.scratch').mkdir()
target = repo / '.scratch/local.out'
target.write_text('unpushed work\n')
commit(repo, sha)
os.utime(target, (time.time() - 3 * 86400,) * 2)
verify_pair('stale-unpushed-fallback', fleet, repo, target)
quarantine('stale-unpushed-fallback/quarantine', fleet, repo, target)

fleet, repo, sha = repo_case('detached-worktree')
(repo / 'keep/file.txt').write_text('only detached commit\n')
detached = commit(repo, sha, detached=True)
git(repo, 'update-ref', '--no-deref', 'HEAD', sha)
admin = repo / '.git/worktrees/missing'
admin.mkdir(parents=True)
(admin / 'HEAD').write_text(detached + '\n')
(admin / 'commondir').write_text('../..\n')
(admin / 'gitdir').write_text(str(fleet / 'missing/.git') + '\n')
verify_pair('worktree-unique-detached-head', fleet, repo, fleet / 'missing')
(admin / 'HEAD').write_text('f' * 40 + '\n')
verify_pair('worktree-invalid-head', fleet, repo, fleet / 'missing')

fleet, repo, sha = repo_case('self-row')
target = repo / 'note.md'
target.write_text('sole copy\n')
hash_ = run(['sha256sum', target]).stdout.split()[0]
ledger = fleet / 'ledger.tsv'
ledger.write_text(f'{target}\t{hash_}\t{target}\t{hash_}\n')
verify_pair('ledger-self-copy', fleet, repo, target, ledger)

fleet, repo, sha = repo_case('directory-empty-digests')
target = repo / 'bundle'
target.mkdir()
(target / 'local.txt').write_text('not preserved\n')
vault = fleet / 'vault'
vault.mkdir()
ledger = fleet / 'ledger.tsv'
content_hash = hashlib.sha256((target / 'local.txt').read_bytes()).hexdigest()
source_digest = hashlib.sha256(f'{content_hash}  ./local.txt\n'.encode()).hexdigest()
ledger.write_text(f'{target}\t{source_digest}\t{vault}\t\n')
verify_pair('ledger-missing-vault-directory-digest', fleet, repo, target, ledger)

fleet, repo, sha = repo_case('quarantine-symlink')
(repo / '.scratch').mkdir()
target = repo / '.scratch/old.out'
target.write_text('stale payload\n')
os.utime(target, (time.time() - 3 * 86400,) * 2)
outside = fleet / 'outside'
outside.mkdir()
(repo / '.ufo-quarantine').symlink_to(outside, target_is_directory=True)
quarantine('quarantine-root-symlink', fleet, repo, target, outside=outside)

fleet, repo, sha = repo_case('path-record-injection')
target = repo / 'fresh\tSAFE\tstale\tno-receipt.txt'
target.write_text('fresh non-scratch sole copy\n')
quarantine('tab-path-verdict-injection', fleet, repo, target)

fleet, repo, sha = repo_case('remote-changed')
target = repo / 'keep/file.txt'
other = git(repo, 'commit-tree', git(repo, 'write-tree'), data='unrelated root\n')
git(repo, 'update-ref', 'refs/remotes/backup/main', sha)
hook = fleet / 'change-ref.sh'
hook.write_text('#!/usr/bin/env bash\ngit -C ' + repr(str(repo)) + ' update-ref refs/remotes/origin/main ' + other + '\n')
quarantine('default-receipt-revoked-during-hold', fleet, repo, target, hook=hook)

fleet, repo, sha = repo_case('vault-alias')
target = repo / 'note.md'
target.write_text('preserved payload\n')
vault = fleet / 'vault.md'
vault.write_text(target.read_text())
hash_ = run(['sha256sum', target]).stdout.split()[0]
ledger = fleet / 'ledger.tsv'
ledger.write_text(f'{target}\t{hash_}\t{vault}\t{hash_}\n')
hook = fleet / 'replace-vault.sh'
hook.write_text('#!/usr/bin/env bash\nrm -- ' + repr(str(vault)) + '\nln -s -- "$1" ' + repr(str(vault)) + '\n')
quarantine('vault-replaced-with-quarantine-alias', fleet, repo, target, hook=hook, ledger=ledger)

fleet, repo, sha = repo_case('positive-pushed-directory')
verify_pair('positive-pushed-directory', fleet, repo, repo / 'keep', expected='SAFE')
quarantine('positive-pushed-directory/quarantine', fleet, repo, repo / 'keep', expect_deleted=True)

fleet, repo, sha = repo_case('positive-stale-directory')
target = repo / '.scratch/old-bundle'
target.mkdir(parents=True)
(target / 'old.txt').write_text('old scratch bytes\n')
os.utime(target / 'old.txt', (time.time() - 3 * 86400,) * 2)
os.utime(target, (time.time() - 3 * 86400,) * 2)
verify_pair('positive-stale-directory', fleet, repo, target, expected='SAFE')
quarantine('positive-stale-directory/quarantine', fleet, repo, target, expect_deleted=True)

print(json.dumps(dict(fixture_root=str(root), tools=str(args.tool_dir.resolve()),
                      suffix=args.suffix, total=len(results),
                      passed=sum(r['passed'] for r in results),
                      false_safe_or_delete=sum(r['adversarial'] and not r['passed'] for r in results),
                      compatibility_failures=sum(not r['adversarial'] and not r['passed'] for r in results),
                      cases=results), indent=2))
raise SystemExit(0 if args.observe or all(r['passed'] for r in results) else 1)
