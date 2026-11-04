#!/usr/bin/env python3
"""Independent acceptance trial of the r58 assessment comparator public CLI.

Runs the registered public command (`--tool PATH --root LANE --rev FULL40`) as a
subprocess only: no lane helper is imported, no counter module is called.  The
matrix-derived numbers (pairwise identical rows, per-matrix exit-zero counts) are
recomputed here from committed TSV bytes, and every fixture is a fresh isolated
Git repository whose toplevel is asserted before any commit.

Cases:
  committed-honest           both matrix-derived notes present at --rev      rc 0
  one-correction-omitted     exact SCORECARD minus the exit_zero note         rc 1, 1 MISSING
  prose-wrong-count-forgery  template-shaped notes carrying wrong counts      rc 1, 2 MISSING
  both-missing               neither required note present                    rc 1, 2 MISSING
  prose-contradiction-adjacent (observation, not authentication) exact notes
                             plus contradicting wrong-count prose             rc 0

Exit 0 only when every asserted case matches; 1 on any mismatch; 2 on CLI or
input failure.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

MATRIX = 'census/round-57/records/c1-matrix-v{}.tsv'
CARRY_PREFIX = 'R58-CALIBRATION carry_identical='
EXIT_PREFIX = 'R58-CALIBRATION exit_zero='


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args, check=True):
    return subprocess.run(['git', '-C', str(repo), *args], check=check,
                          capture_output=True, text=True)


def blob(root, rev, path):
    return subprocess.run(['git', '-C', str(root), 'show', '%s:%s' % (rev, path)],
                          check=True, capture_output=True).stdout


def parse_matrix(data, label):
    lines = data.decode('utf-8').splitlines()
    header = ['fixture', 'counter', 'rev', 'base', 'exit', 'finding', 'findings_all', 'SUMMARY']
    if not lines or lines[0].split('\t') != header:
        raise SystemExit('FATAL matrix %s header mismatch' % label)
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        fields = line.split('\t')
        if len(fields) != 8:
            raise SystemExit('FATAL matrix %s row has %d fields' % (label, len(fields)))
        rows.append(fields)
    if not rows:
        raise SystemExit('FATAL matrix %s has no rows' % label)
    return rows


def derive(root, rev):
    v5 = parse_matrix(blob(root, rev, MATRIX.format(5)), 'v5')
    v6 = parse_matrix(blob(root, rev, MATRIX.format(6)), 'v6')
    if len(v5) != len(v6):
        raise SystemExit('FATAL matrix row counts differ: %d vs %d' % (len(v5), len(v6)))
    identical = sum(a[4] == b[4] and a[6] == b[6] for a, b in zip(v5, v6))
    zero5 = sum(a[4] == '0' for a in v5)
    zero6 = sum(b[4] == '0' for b in v6)
    nonidentical = [a[0] for a, b in zip(v5, v6)
                    if not (a[4] == b[4] and a[6] == b[6])]
    return {
        'rows_v5': len(v5), 'rows_v6': len(v6),
        'identical': identical,
        'exit_zero': [zero5, zero6],
        'nonidentical_fixtures': nonidentical,
        'matrix_sha256': {'v5': sha(blob(root, rev, MATRIX.format(5))),
                          'v6': sha(blob(root, rev, MATRIX.format(6)))},
    }


def notes_for(d):
    return [
        CARRY_PREFIX + '%d supersedes the r57 SCORECARD claim "all 33 carry-over rows".' % d['identical'],
        EXIT_PREFIX + '%d,%d counted separately per matrix; the r57 two-file awk command '
                      'emits the combined total %d, not the pair.'
                      % (d['exit_zero'][0], d['exit_zero'][1], sum(d['exit_zero'])),
    ]


def labels(stdout):
    """Map required-note subject -> MATCH/MISSING exactly as the tool printed."""
    out = {}
    for line in stdout.splitlines():
        for verb in ('MATCH ', 'MISSING '):
            if line.startswith(verb):
                rest = line[len(verb):]
                if rest.startswith(CARRY_PREFIX):
                    out['carry'] = verb.strip()
                elif rest.startswith(EXIT_PREFIX):
                    out['exit_zero'] = verb.strip()
    return out


def make_fixture(work, root, rev):
    fixture = pathlib.Path(tempfile.mkdtemp(prefix='fixture-', dir=str(work)))
    git(fixture, 'init', '-q')
    top = pathlib.Path(git(fixture, 'rev-parse', '--show-toplevel').stdout.strip()).resolve()
    if top != fixture.resolve():
        raise SystemExit('FATAL fixture toplevel %s != %s' % (top, fixture))
    git(fixture, 'config', 'user.name', 'souji-acceptance')
    git(fixture, 'config', 'user.email', 'fixture@invalid')
    for arm in (5, 6):
        target = fixture / MATRIX.format(arm)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob(root, rev, MATRIX.format(arm)))
    git(fixture, 'add', '-A')
    git(fixture, 'commit', '-qm', 'matrices')
    return fixture


def commit_scorecard(fixture, content, message):
    (fixture / 'SCORECARD.md').write_bytes(content)
    git(fixture, 'add', 'SCORECARD.md')
    git(fixture, 'commit', '-qm', message)
    return git(fixture, 'rev-parse', 'HEAD').stdout.strip()


def run_tool(tool, root, rev):
    cmd = ['python3', '-B', str(tool), '--root', str(root), '--rev', rev]
    r = subprocess.run(cmd, text=True, capture_output=True)
    return {
        'command': cmd, 'rc': r.returncode,
        'stdout': r.stdout, 'stderr': r.stderr,
        'stdout_sha256': sha(r.stdout.encode()), 'stderr_sha256': sha(r.stderr.encode()),
    }


def summary_line(stdout):
    for line in stdout.splitlines():
        if line.startswith('SUMMARY '):
            return line
    return None


def check(case, run, expected_rc, expected_labels, expected_summary):
    got = labels(run['stdout'])
    ok = (run['rc'] == expected_rc and got == expected_labels
          and summary_line(run['stdout']) == expected_summary
          and run['stderr'] == '')
    return dict(case=case, expected_rc=expected_rc, expected_labels=expected_labels,
                expected_summary=expected_summary, observed_rc=run['rc'],
                observed_labels=got, observed_summary=summary_line(run['stdout']),
                passed=ok, run=run)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool', required=True)
    p.add_argument('--work', required=True)
    p.add_argument('--root', required=True)
    p.add_argument('--rev', required=True)
    a = p.parse_args()

    tool = pathlib.Path(a.tool).resolve()
    root = pathlib.Path(a.root).resolve()
    if not tool.is_file():
        p.error('tool not found: %s' % tool)
    if not (root / '.git').exists():
        p.error('root is not a Git repository: %s' % root)
    if len(a.rev) != 40 or any(c not in '0123456789abcdef' for c in a.rev):
        p.error('--rev must be a full 40-hex revision')
    subprocess.run(['git', '-C', str(root), 'cat-file', '-e', a.rev + '^{commit}'],
                   check=True, capture_output=True)

    work = pathlib.Path(a.work).resolve()
    work.mkdir(parents=True, exist_ok=True)

    derived = derive(root, a.rev)
    expected_notes = notes_for(derived)
    base_card = blob(root, a.rev, 'SCORECARD.md')
    kept = [line for line in base_card.split(b'\n')
            if not (line.startswith(CARRY_PREFIX.encode()) or line.startswith(EXIT_PREFIX.encode()))]
    carry_line = next((line for line in base_card.split(b'\n')
                       if line.startswith(CARRY_PREFIX.encode())), None)
    exit_line = next((line for line in base_card.split(b'\n')
                      if line.startswith(EXIT_PREFIX.encode())), None)
    if carry_line is None or exit_line is None:
        raise SystemExit('FATAL committed SCORECARD lacks a required note at %s' % a.rev)

    honest_expected = 'SUMMARY assertions=2 mismatches=0 carry_identical=%d exit_zero=%d,%d' % (
        derived['identical'], derived['exit_zero'][0], derived['exit_zero'][1])
    both_match = {'carry': 'MATCH', 'exit_zero': 'MATCH'}

    cases = []
    honest = run_tool(tool, root, a.rev)
    cases.append(check('committed-honest', honest, 0, both_match, honest_expected))

    fixture = make_fixture(work, root, a.rev)
    total = len(base_card.split(b'\n'))

    # one correction omitted: keep carry note, drop exit_zero note
    one = b'\n'.join(line for line in base_card.split(b'\n') if line != exit_line)
    one_rev = commit_scorecard(fixture, one, 'one-correction-omitted')
    one_run = run_tool(tool, fixture, one_rev)
    cases.append(check('one-correction-omitted', one_run, 1,
                       {'carry': 'MATCH', 'exit_zero': 'MISSING'},
                       'SUMMARY assertions=2 mismatches=1 carry_identical=%d exit_zero=%d,%d' % (
                           derived['identical'], derived['exit_zero'][0], derived['exit_zero'][1])))

    # prose wrong-count forgery: template-shaped lines carrying the superseded / combined counts
    forged_lines = [
        (CARRY_PREFIX + '33 supersedes the r57 SCORECARD claim "all 33 carry-over rows".').encode(),
        (EXIT_PREFIX + '18 counted separately per matrix; the r57 two-file awk command '
                       'emits the combined total 18, not the pair.').encode(),
    ]
    forged = b'\n'.join(line for line in base_card.split(b'\n')
                        if not (line.startswith(CARRY_PREFIX.encode()) or line.startswith(EXIT_PREFIX.encode()))
                        ) + b'\n' + forged_lines[0] + b'\n' + forged_lines[1]
    forged_rev = commit_scorecard(fixture, forged, 'prose-wrong-count-forgery')
    forged_run = run_tool(tool, fixture, forged_rev)
    cases.append(check('prose-wrong-count-forgery', forged_run, 1,
                       {'carry': 'MISSING', 'exit_zero': 'MISSING'},
                       'SUMMARY assertions=2 mismatches=2 carry_identical=%d exit_zero=%d,%d' % (
                           derived['identical'], derived['exit_zero'][0], derived['exit_zero'][1])))

    # both missing
    none_rev = commit_scorecard(fixture, b'\n'.join(kept), 'both-missing')
    none_run = run_tool(tool, fixture, none_rev)
    cases.append(check('both-missing', none_run, 1,
                       {'carry': 'MISSING', 'exit_zero': 'MISSING'},
                       'SUMMARY assertions=2 mismatches=2 carry_identical=%d exit_zero=%d,%d' % (
                           derived['identical'], derived['exit_zero'][0], derived['exit_zero'][1])))

    # observation: exact notes survive a contradicting wrong-count prose line -> rc 0
    contradiction = base_card + (b'\ncarry-over rows confirmed: all 33, exit zero combined = 18.\n')
    contra_rev = commit_scorecard(fixture, contradiction, 'prose-contradiction-adjacent')
    contra_run = run_tool(tool, fixture, contra_rev)
    cases.append(check('prose-contradiction-adjacent', contra_run, 0, both_match, honest_expected))
    cases[-1]['note'] = ('presence predicate only: adjacent contradictory prose is not parsed; '
                         'this is recorded behavior, not execution authentication')

    asserted = [c for c in cases if 'note' not in c]
    report = {
        'tool': str(tool), 'tool_sha256': sha(tool.read_bytes()),
        'root': str(root), 'rev': a.rev,
        'root_toplevel': git(root, 'rev-parse', '--show-toplevel').stdout.strip(),
        'work': str(work), 'fixture': str(fixture),
        'derived': derived,
        'expected_notes': expected_notes,
        'scorercard_sha256': {'committed': sha(base_card), 'one-correction-omitted': sha(one),
                              'prose-wrong-count-forgery': sha(forged),
                              'both-missing': sha(b'\n'.join(kept)),
                              'prose-contradiction-adjacent': sha(contradiction)},
        'scorercard_lines': {'committed': total,
                             'one-correction-omitted': len(one.split(b'\n')),
                             'both-missing': len(b'\n'.join(kept).split(b'\n'))},
        'fixture_revisions': {'one-correction-omitted': one_rev,
                              'prose-wrong-count-forgery': forged_rev,
                              'both-missing': none_rev,
                              'prose-contradiction-adjacent': contra_rev},
        'cases': cases,
        'passed': sum(c['passed'] for c in asserted),
        'asserted_cases': len(asserted),
    }
    report['accepted'] = all(c['passed'] for c in asserted)
    print(json.dumps(report, indent=2))
    return 0 if report['accepted'] else 1


if __name__ == '__main__':
    sys.exit(main())
