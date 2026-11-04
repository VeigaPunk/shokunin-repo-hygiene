#!/usr/bin/env python3
"""Assessment gate (souji round 59): two matrix-derived SCORECARD corrections.

Derivation: census/round-58/c1-counter.py, read-only source. Frozen predicate:
census/round-59/preregistration.txt claim C1 at
19f44552378d333f401ff2f0864c4e8b9c59ab1f; executed controls at
74455b7209e04a2375c2084738a7b6fea59bf6d5. This gate preserves the r58
counter's two exact note derivations and its --root/--rev result semantics,
and emits one stable finding id when either derived note is absent:

  ASSESSMENT-MISMATCH   SCORECARD.md at --rev does not contain at least one
                        matrix-derived note verbatim (mismatches>0).

Normal mode is read-only over --root: git blobs only (`git show`), never the
working tree, and no writes. Exit 0 both notes present; 1 any mismatch; 2
could-not-evaluate (usage, unresolvable revision/blob/matrix, malformed
matrix, or any evaluation error), with no traceback.

Selftest: --selftest --work DIR [--expected TSV] creates one unique fixture
directory under --work, copies the two r57 matrices from pinned base
da5af55b5ea0a2a38edea05635a13416c698e6e7 with `git show`, and commits five
SCORECARD variants at fixed dates. Each case invokes this file as an actual
CLI subprocess and asserts exit code, ordered finding ids, mismatch count,
carry_identical and exit_zero against the independent expected TSV
(assessment-selftest-expected.tsv by default). An always-clean stub is scored
over the same expected rows and must fail at least one case. Only the unique
fixture child is removed in finally.
"""
import argparse
import csv
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = Path(__file__).resolve()
DEFAULT_EXPECTED = HERE / 'assessment-selftest-expected.tsv'
PINNED_BASE = 'da5af55b5ea0a2a38edea05635a13416c698e6e7'
MATRIX_PATHS = (
    'census/round-57/records/c1-matrix-v5.tsv',
    'census/round-57/records/c1-matrix-v6.tsv',
)
SCORECARD = 'SCORECARD.md'
NOTE_PREFIX = 'R58-CALIBRATION '
FINDING = 'ASSESSMENT-MISMATCH'
FIXED_DATE = '2001-02-03T04:05:06 +0000'
SUMMARY_RE = re.compile(
    r'^SUMMARY assertions=2 mismatches=(\d+) carry_identical=(\d+) '
    r'exit_zero=(\d+),(\d+)$')
EXPECTED_HEADER = ['case', 'rc', 'findings', 'mismatches', 'carry_identical',
                   'exit_zero']


class CannotEvaluate(Exception):
    """Evaluation could not produce a verdict."""


def _git_env():
    """Scrubbed Git environment; fixed identity/dates for fixture commits."""
    return {
        'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
        'LC_ALL': 'C.UTF-8',
        'LANG': 'C.UTF-8',
        'HOME': os.environ.get('HOME', '/tmp'),
        'GIT_CONFIG_NOSYSTEM': '1',
        'GIT_CONFIG_GLOBAL': os.devnull,
        'GIT_CONFIG_SYSTEM': os.devnull,
        'GIT_NO_REPLACE_OBJECTS': '1',
        'GIT_OPTIONAL_LOCKS': '0',
        'GIT_TERMINAL_PROMPT': '0',
        'GIT_AUTHOR_NAME': 'souji-fixture',
        'GIT_AUTHOR_EMAIL': 'fixture@invalid',
        'GIT_COMMITTER_NAME': 'souji-fixture',
        'GIT_COMMITTER_EMAIL': 'fixture@invalid',
        'GIT_AUTHOR_DATE': FIXED_DATE,
        'GIT_COMMITTER_DATE': FIXED_DATE,
        'PYTHONDONTWRITEBYTECODE': '1',
    }


def _git(root, *args):
    command = ['git', '-C', str(root),
               '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null']
    command.extend(args)
    try:
        return subprocess.run(command, capture_output=True, text=True,
                              env=_git_env(), timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise CannotEvaluate('git unavailable: %s' % exc)


def _blob(root, rev, path):
    result = _git(root, 'show', rev + ':' + path)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        suffix = (' ' + detail[-1]) if detail else ''
        raise CannotEvaluate('git show %s:%s rc=%d%s'
                             % (rev, path, result.returncode, suffix))
    return result.stdout


def derive(root, rev):
    """The r58 counter's exact two note derivations, unchanged."""
    tables = []
    for path in MATRIX_PATHS:
        rows = list(csv.DictReader(io.StringIO(_blob(root, rev, path)),
                                   delimiter='\t'))
        tables.append(rows)
    # Positional columns match the committed matrix header, not prose claims.
    values = []
    for rows in tables:
        values.append(sum(list(row.values())[4] == '0' for row in rows))
    identical = sum(a['exit'] == b['exit']
                    and a['findings_all'] == b['findings_all']
                    for a, b in zip(*tables))
    text = _blob(root, rev, SCORECARD)
    notes = [
        'R58-CALIBRATION carry_identical=' + str(identical)
        + ' supersedes the r57 SCORECARD claim "all 33 carry-over rows".',
        'R58-CALIBRATION exit_zero=' + ','.join(map(str, values))
        + ' counted separately per matrix; the r57 two-file awk command emits '
        + 'the combined total ' + str(sum(values)) + ', not the pair.',
    ]
    return notes, text, identical, values


def assess(root, rev):
    notes, text, identical, values = derive(root, rev)
    present = [note in text for note in notes]
    mismatches = sum(not matched for matched in present)
    for note, matched in zip(notes, present):
        print(('MATCH ' if matched else 'MISSING ') + note)
    if mismatches:
        print('FINDING ' + FINDING)
    print('SUMMARY assertions=2 mismatches=%d carry_identical=%d exit_zero=%s'
          % (mismatches, identical, ','.join(map(str, values))))
    return int(bool(mismatches))


def _fixture_git(repo, *args):
    result = _git(repo, *args)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        suffix = (' ' + detail[-1]) if detail else ''
        raise CannotEvaluate('fixture git %r rc=%d%s'
                             % (args, result.returncode, suffix))
    return result.stdout.strip()


def _assert_toplevel(repo):
    top = _fixture_git(repo, 'rev-parse', '--show-toplevel')
    if os.path.realpath(top) != os.path.realpath(str(repo)):
        raise CannotEvaluate('fixture toplevel %r is not %r'
                             % (top, str(repo)))


def _lane_root():
    result = _git(HERE, 'rev-parse', '--show-toplevel')
    if result.returncode:
        raise CannotEvaluate('assessment-gate.py is not inside a Git worktree')
    return Path(result.stdout.strip())


def build_fixture(base):
    """Build the unique fixture repository and its five committed cases."""
    lane = _lane_root()
    scorecard = _blob(lane, PINNED_BASE, SCORECARD)
    matrices = [(path, _blob(lane, PINNED_BASE, path)) for path in MATRIX_PATHS]
    repo = base / 'fixture'
    repo.mkdir()
    _fixture_git(repo, 'init', '-q', '-b', 'main')
    _assert_toplevel(repo)
    for path, data in matrices:
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data, encoding='utf-8')
    lines = scorecard.splitlines()
    note_rows = [i for i, line in enumerate(lines) if line.startswith(NOTE_PREFIX)]
    if len(note_rows) != 2:
        raise CannotEvaluate('pinned SCORECARD has %d %s lines, want 2'
                             % (len(note_rows), NOTE_PREFIX.strip()))

    def variant(drop=(), replace=None):
        out = []
        for index, line in enumerate(lines):
            if index in drop:
                continue
            if replace is not None and index == replace[0]:
                changed = line.replace(replace[1], replace[2])
                if changed == line:
                    raise CannotEvaluate('pinned note lacks literal %r'
                                         % replace[1])
                line = changed
            out.append(line)
        return '\n'.join(out) + '\n'

    honest = scorecard if scorecard.endswith('\n') else scorecard + '\n'
    variants = [
        ('HONEST', honest),
        ('OMIT-FIRST', variant(drop={note_rows[0]})),
        ('OMIT-SECOND', variant(drop={note_rows[1]})),
        ('BOTH-MISSING', variant(drop=set(note_rows))),
        ('WRONG-VALUE', variant(replace=(note_rows[0],
                                         'carry_identical=34',
                                         'carry_identical=35'))),
    ]
    cases = {}
    for name, text in variants:
        (repo / SCORECARD).write_text(text, encoding='utf-8')
        _assert_toplevel(repo)
        _fixture_git(repo, 'add', '-A')
        _assert_toplevel(repo)
        _fixture_git(repo, 'commit', '-q', '-m', 'fixture ' + name)
        rev = _fixture_git(repo, 'rev-parse', 'HEAD')
        if len(rev) != 40:
            raise CannotEvaluate('fixture rev is not full40: %r' % rev)
        cases[name] = rev
    return repo, cases


def read_expected(path):
    try:
        text = path.read_text(encoding='utf-8')
    except OSError as exc:
        raise CannotEvaluate('expected unreadable: %s' % exc)
    rows = text.splitlines()
    if not rows or rows[0].split('\t') != EXPECTED_HEADER:
        raise CannotEvaluate('expected header must be: %s'
                             % '\\t'.join(EXPECTED_HEADER))
    expected = {}
    for row in rows[1:]:
        if not row.strip():
            continue
        fields = row.split('\t')
        if len(fields) != len(EXPECTED_HEADER):
            raise CannotEvaluate('expected row has %d fields: %r'
                                 % (len(fields), row))
        name, rc_text, findings_text, mismatches_text, carry_text, zero_text = fields
        if name in expected:
            raise CannotEvaluate('duplicate expected case: ' + name)
        try:
            rc = int(rc_text)
            mismatches = int(mismatches_text)
            carry = int(carry_text)
        except ValueError:
            raise CannotEvaluate('expected numeric field malformed: %r' % row)
        zero_parts = zero_text.split(',')
        if len(zero_parts) != 2 or not all(part.isdigit() for part in zero_parts):
            raise CannotEvaluate('expected exit_zero malformed: %r' % row)
        findings = ([] if findings_text.strip() in ('', '-')
                    else [item for item in findings_text.split(',') if item])
        expected[name] = {
            'rc': rc, 'findings': findings, 'mismatches': mismatches,
            'carry': carry, 'exit_zero': zero_text,
        }
    if not expected:
        raise CannotEvaluate('expected TSV has no cases')
    return expected


def invoke(fixture, rev):
    """Actual CLI subprocess self-invocation of this file."""
    command = [sys.executable or 'python3', '-B', str(GATE),
               '--root', str(fixture), '--rev', rev]
    env = _git_env()
    env['HOME'] = str(fixture)
    env['PYTHONUTF8'] = '1'
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                cwd=str(fixture), env=env, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise CannotEvaluate('gate subprocess failed: %s' % exc)
    lines = result.stdout.splitlines()
    findings = [line[len('FINDING '):] for line in lines
                if line.startswith('FINDING ')]
    summaries = [line for line in lines if line.startswith('SUMMARY ')]
    verdicts = [line for line in lines
                if line.startswith('MATCH ') or line.startswith('MISSING ')]
    summary = None
    if len(summaries) == 1:
        match = SUMMARY_RE.match(summaries[0])
        if match:
            summary = {
                'mismatches': int(match.group(1)),
                'carry': int(match.group(2)),
                'exit_zero': match.group(3) + ',' + match.group(4),
            }
    return result.returncode, findings, summary, verdicts, result.stdout, result.stderr


def score_case(observed, want):
    rc, findings, summary, verdicts = observed[:4]
    problems = []
    if rc != want['rc']:
        problems.append('rc')
    if findings != want['findings']:
        problems.append('findings')
    if summary is None:
        problems.append('summary')
    else:
        if summary['mismatches'] != want['mismatches']:
            problems.append('mismatches')
        if summary['carry'] != want['carry']:
            problems.append('carry_identical')
        if summary['exit_zero'] != want['exit_zero']:
            problems.append('exit_zero')
    if len(verdicts) != 2:
        problems.append('note_verdicts')
    elif summary is not None:
        missing = sum(line.startswith('MISSING ') for line in verdicts)
        if missing != summary['mismatches']:
            problems.append('verdict_count')
    return problems


def run_selftest(work, expected_path):
    try:
        work.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise CannotEvaluate('--work unusable: %s' % exc)
    expected = read_expected(expected_path)
    try:
        base = Path(tempfile.mkdtemp(prefix='assessment-fixtures-',
                                     dir=str(work)))
    except OSError as exc:
        raise CannotEvaluate('cannot create fixture child: %s' % exc)
    out = []
    ok = True
    try:
        fixture, cases = build_fixture(base)
        extra = sorted(set(expected) - set(cases))
        missing = sorted(set(cases) - set(expected))
        if extra or missing:
            ok = False
        out.append('SELFTEST-EXPECTED-SET cases=%d expected=%d extra=%s missing=%s'
                   % (len(cases), len(expected), ','.join(extra) or '-',
                      ','.join(missing) or '-'))
        for name in sorted(cases):
            observed = invoke(fixture, cases[name])
            want = expected.get(name)
            if want is None:
                ok = False
                out.append('SELFTEST-CASE %s fail rc=%d findings=%s detail=missing-expected'
                           % (name, observed[0],
                              ','.join(observed[1]) or '-'))
                continue
            problems = score_case(observed, want)
            passed = not problems
            ok = ok and passed
            out.append('SELFTEST-CASE %s %s rc=%d want_rc=%d findings=%s '
                       'want_findings=%s mismatches=%s want_mismatches=%d detail=%s'
                       % (name, 'pass' if passed else 'fail', observed[0],
                          want['rc'], ','.join(observed[1]) or '-',
                          ','.join(want['findings']) or '-',
                          observed[2]['mismatches'] if observed[2] else '-',
                          want['mismatches'], ','.join(problems) or '-'))
        # A discarded always-clean stub must fail at least one expected case.
        stub = {'rc': 0, 'findings': [], 'mismatches': 0, 'carry': 34,
                'exit_zero': '10,8'}
        stub_meets = sum(
            1 for want in expected.values()
            if (want['rc'], want['findings'], want['mismatches'],
                want['carry'], want['exit_zero'])
            == (stub['rc'], stub['findings'], stub['mismatches'],
                stub['carry'], stub['exit_zero']))
        if stub_meets == len(expected):
            ok = False
            out.append('SELFTEST control=FALSE-GREEN-ACCEPTED stub_meets=%d cases=%d'
                       % (stub_meets, len(expected)))
        else:
            out.append('SELFTEST control=FALSE-GREEN-REJECTED stub_meets=%d '
                       'discriminated=%d cases=%d'
                       % (stub_meets, len(expected) - stub_meets,
                          len(expected)))
        out.append('SELFTEST %s cases=%d' % ('pass' if ok else 'fail',
                                             len(expected)))
        print('\n'.join(out))
        return 0 if ok else 1
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='souji r59 assessment gate over two matrix-derived '
                    'SCORECARD notes')
    parser.add_argument('--root')
    parser.add_argument('--rev')
    parser.add_argument('--selftest', action='store_true')
    parser.add_argument('--work')
    parser.add_argument('--expected', default=None)
    args = parser.parse_args(argv)
    if args.selftest:
        if not args.work:
            parser.error('--selftest requires --work')
        expected = Path(args.expected) if args.expected else DEFAULT_EXPECTED
        try:
            return run_selftest(Path(args.work), expected)
        except CannotEvaluate as exc:
            print('CANNOT-EVALUATE ' + str(exc))
            return 2
        except Exception as exc:  # no traceback by contract
            print('CANNOT-EVALUATE %s: %s' % (type(exc).__name__, exc))
            return 2
    if not args.root or not args.rev:
        parser.error('--root and --rev are required')
    try:
        return assess(args.root, args.rev)
    except CannotEvaluate as exc:
        print('CANNOT-EVALUATE ' + str(exc))
        return 2
    except Exception as exc:  # no traceback by contract
        print('CANNOT-EVALUATE %s: %s' % (type(exc).__name__, exc))
        return 2


if __name__ == '__main__':
    sys.exit(main())
