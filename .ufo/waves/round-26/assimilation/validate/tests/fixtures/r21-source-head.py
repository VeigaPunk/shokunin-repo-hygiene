#!/usr/bin/env python3
"""Source HEAD is sampled information, not a prerequisite for revision replay."""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool', required=True)
    p.add_argument('--base-tool', required=True)
    args = p.parse_args()
    changed, base = load(args.tool, 'changed'), load(args.base_tool, 'baseline')
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_AUTHOR_NAME': 'synthetic',
           'GIT_AUTHOR_EMAIL': 'synthetic@invalid', 'GIT_COMMITTER_NAME': 'synthetic',
           'GIT_COMMITTER_EMAIL': 'synthetic@invalid'}
    with tempfile.TemporaryDirectory(prefix='souji-r21-head-', dir='/var/tmp') as temp:
        root = Path(temp)
        repo = root / 'source.git'
        def git(*argv, data=None):
            proc = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(repo), *argv],
                                  env=env, input=data, capture_output=True, check=True)
            return proc.stdout.decode().strip()
        subprocess.run(['git', 'init', '--quiet', '--bare', str(repo)], env=env, check=True)
        tree = git('mktree', data=b'')
        commit = git('commit-tree', tree, data=b'synthetic commit\n')
        git('update-ref', 'refs/heads/measurement', commit)
        git('symbolic-ref', 'HEAD', 'refs/heads/not-created')
        failed = discriminating = 0
        def check(name, source, expected):
            nonlocal failed, discriminating
            def result(module):
                try:
                    return module.source_state(source)
                except (OSError, ValueError, RuntimeError):
                    return 'REFUSED'
            now, before = result(changed), result(base)
            ok = now == expected
            failed += not ok
            discriminating += before != expected
            print(f'CASE\t{"pass" if ok else "FAIL"}\t{name}\tbase_discriminating={before != expected}')
        check('advertised-commit-without-head', repo, {'head': None, 'bare': True, 'status': ''})
        git('symbolic-ref', 'HEAD', 'refs/heads/measurement')
        check('advertised-commit-with-head', repo, {'head': commit, 'bare': True, 'status': ''})
        not_repo = root / 'not-repo'
        not_repo.mkdir()
        check('not-a-repository', not_repo, 'REFUSED')
        print(f'SUMMARY\ttotal=3\tpass={3-failed}\tfail={failed}\tbase_discriminating={discriminating}')
        return int(bool(failed))


if __name__ == '__main__':
    raise SystemExit(main())
