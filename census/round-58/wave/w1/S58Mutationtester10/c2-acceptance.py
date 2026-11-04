#!/usr/bin/env python3
"""Round 58 independent C2 acceptance: five literal refusals, three real receipts.

Run with Python -B. --work is caller-owned scratch; fixtures stay there for
inspection. JSON retains commands, outputs, exits, expected and actual findings.
No production writes, network, imports from the tool, or mutable expectation file.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zlib

REAL_ROWS = (
    ('census/round-57/records/c1-tip.txt', 'census/round-57/c1-counter.py'),
    ('census/round-57/records/c2-tip.txt', 'census/round-57/c2-counter.py'),
    ('census/round-57/records/standing.txt', 'census/round-46/c1-counter.py'),
)
REFUSALS = (
    ('abs', 'RECEIPT-PATH-UNCONFINED'),
    ('../', 'RECEIPT-PATH-UNCONFINED'),
    ('parent-symlink-escape', 'RECEIPT-PATH-UNCONFINED'),
    ('annotated-tag-OBJECT', 'RECEIPT-REV-ABSENT'),
    ('conflicting-rev', 'RECEIPT-REV-CONFLICT'),
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def environment(work):
    return {
        'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
        'HOME': str(work), 'TMPDIR': str(work), 'PYTHONDONTWRITEBYTECODE': '1',
        'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
        'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
        'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1',
        'GIT_TERMINAL_PROMPT': '0', 'GIT_AUTHOR_NAME': 'fixture',
        'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
        'GIT_COMMITTER_NAME': 'fixture',
        'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
        'GIT_AUTHOR_DATE': '2000-01-01T00:00:00+0000',
        'GIT_COMMITTER_DATE': '2000-01-01T00:00:00+0000',
    }


def command(argv, env, cwd):
    proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=120)
    return {'argv': argv, 'cwd': str(cwd), 'EXIT': proc.returncode,
            'stdout': proc.stdout, 'stderr': proc.stderr}


def fixture(work, env, evidence):
    base = Path(tempfile.mkdtemp(prefix='c2-independent-', dir=work))
    repo = base / 'repo'
    repo.mkdir()

    def git(*args, bootstrap=False):
        prefix = ['git', '-C', str(repo), '-c', 'core.fsmonitor=false',
                  '-c', 'core.hooksPath=/dev/null']
        if not bootstrap:
            guard = command(prefix + ['rev-parse', '--show-toplevel'], env, base)
            evidence.append(guard)
            if guard['EXIT'] or guard['stdout'].strip() != str(repo):
                raise RuntimeError('fixture toplevel mismatch')
        result = command(prefix + list(args), env, base)
        evidence.append(result)
        if result['EXIT']:
            raise RuntimeError('fixture command failed: ' + json.dumps(result))
        return result['stdout'].strip()

    # Bootstrap is explicitly -C into a newly-created directory, outside any repo.
    probe = command(['git', '-C', str(repo), 'rev-parse', '--show-toplevel'], env, base)
    evidence.append(probe)
    if probe['EXIT'] == 0:
        raise RuntimeError('scratch unexpectedly inside an existing repository')
    git('init', '-q', '-b', 'main', '--object-format=sha1', bootstrap=True)
    instrument = 'instrument.py'
    data = b'# deterministic receipt instrument\n'
    (repo / instrument).write_bytes(data)
    git('add', '--', instrument)
    git('commit', '-q', '-m', 'fixture base')
    rev = git('rev-parse', 'HEAD')
    (repo / 'second.txt').write_text('second reachable commit\n')
    git('add', '--', 'second.txt')
    git('commit', '-q', '-m', 'fixture second')
    second = git('rev-parse', 'HEAD')

    # A real annotated tag OBJECT, not its peeled commit. Construct immutable
    # loose fixture bytes without git tag/hash-object/update-ref mutation calls.
    tag_body = (f'object {rev}\ntype commit\ntag fixture-tag\n'
                'tagger fixture <fixture@example.invalid> 946684800 +0000\n\n'
                'annotated tag fixture\n').encode()
    tag_object = b'tag ' + str(len(tag_body)).encode() + b'\0' + tag_body
    tag = hashlib.sha1(tag_object).hexdigest()
    object_path = repo / '.git' / 'objects' / tag[:2] / tag[2:]
    object_path.parent.mkdir(exist_ok=True)
    object_path.write_bytes(zlib.compress(tag_object))
    if git('cat-file', '-t', tag) != 'tag':
        raise RuntimeError('tag fixture is not a tag object')
    if git('rev-parse', tag + '^{commit}') != rev:
        raise RuntimeError('annotated tag did not peel to fixture commit')

    honest = (f'rev={rev}\ninstrument={instrument}\n'
              f'instrument_sha256={digest(data)}\nCOMMAND fixture\n'
              'SUMMARY fixture clean\nEXIT=0\n')
    (base / 'outside.txt').write_text(honest)
    (repo / 'escape').symlink_to(base, target_is_directory=True)
    (repo / 'tag.txt').write_text(honest.replace(f'rev={rev}', f'rev={tag}'))
    (repo / 'conflict.txt').write_text(f'rev={rev}\nrev={second}\n' +
                                     honest.split('\n', 1)[1])
    paths = (str(base / 'outside.txt'), '../outside.txt', 'escape/outside.txt',
             'tag.txt', 'conflict.txt')
    cases = []
    for index, ((name, finding), receipt) in enumerate(zip(REFUSALS, paths)):
        manifest = base / f'case-{index}.tsv'
        manifest.write_text(f'receipt\tinstrument\n{receipt}\t{instrument}\n')
        cases.append((name, repo, manifest, 1, [finding]))
    return base, cases, {'revision': rev, 'second_revision': second,
                         'tag_object': tag, 'instrument_sha256': digest(data),
                         'honest_receipt': honest, 'tag_body': tag_body.decode()}


def score(tool, cases, env, cwd):
    rows = []
    for name, root, manifest, expected_rc, expected_findings in cases:
        result = command([sys.executable, '-B', str(tool), '--root', str(root),
                          '--manifest', str(manifest)], env, cwd)
        # Keep full finding lines as evidence; compare the entire ordered id list.
        lines = [line for line in result['stdout'].splitlines()
                 if line.startswith('FINDING ')]
        findings = [line.split()[1] if len(line.split()) > 1 else '<malformed>'
                    for line in lines]
        result.update(case=name, root=str(root), manifest=manifest.read_text(),
                      expected_EXIT=expected_rc, expected_findings=expected_findings,
                      findings=findings, full_findings=lines,
                      passed=(result['EXIT'] == expected_rc and findings == expected_findings))
        rows.append(result)
    return {'passed': len(rows) == 8 and all(row['passed'] for row in rows),
            'cases': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool', required=True, type=Path)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    root, work, tool = args.root.resolve(), args.work.resolve(), args.tool.resolve()
    work.mkdir(parents=True, exist_ok=True)
    env = environment(work)
    report = {'tool': str(tool), 'tool_sha256': digest(tool.read_bytes()),
              'root': str(root), 'fixture_commands': [], 'real_receipts': []}
    base, cases, details = fixture(work, env, report['fixture_commands'])
    report['fixture'] = details
    for index, (receipt, instrument) in enumerate(REAL_ROWS):
        manifest = base / f'real-{index}.tsv'
        manifest.write_text(f'receipt\tinstrument\n{receipt}\t{instrument}\n')
        original = (root / receipt).read_bytes()
        report['real_receipts'].append({'path': receipt, 'sha256': digest(original),
                                        'text': original.decode()})
        cases.append((f'real-{index + 1}', root, manifest, 0, []))
    report['target'] = score(tool, cases, env, base)
    if args.selftest:
        controls = {}
        for name, body in (
                ('always-clean', "print('SUMMARY receipts=1 findings=0')\n"),
                ('always-refuse', "print('FINDING RECEIPT-PATH-UNCONFINED stub')\n"
                                  "raise SystemExit(1)\n")):
            stub = base / (name + '.py')
            stub.write_text(body)
            observed = score(stub, cases, env, base)
            controls[name] = {'rejected': not observed['passed'], **observed}
        report['selftest'] = {'passed': all(c['rejected'] for c in controls.values()),
                              'controls': controls}
    rc = 0 if report['target']['passed'] else 1
    if args.selftest and not report['selftest']['passed']:
        rc = 1
    report['EXIT'] = rc
    print(json.dumps(report, indent=2))
    return rc


if __name__ == '__main__':
    sys.exit(main())
