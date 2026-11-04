#!/usr/bin/env python3
"""S59Critic: read-only probes of the FROZEN census/round-59/c1-counter.py.

Every case builds a throwaway git repo under --work, writes a SKILL.md
variant, commits it, and runs the frozen counter by exact public path.
The frozen counter bytes are never modified; --root/--rev point at the
throwaway repo, so no production surface is read or written.
"""
import argparse, pathlib, subprocess, sys

LANE = '/home/vgpnk/Projects/shokunin/souji-shokunin'
BASE = 'da5af55b5ea0a2a38edea05635a13416c698e6e7'
COUNTER = LANE + '/census/round-59/c1-counter.py'

R59_GATE = '| r59 assessment comparison | gate | cmd | v | s | p | w | souji |'
R59_EVID = '| r59 assessment comparison | evidence | cmd | v | s | p | w | souji |'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', required=True)
    a = ap.parse_args()
    work = pathlib.Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    repo = work / 'fixture'
    if not repo.exists():
        repo.mkdir()
    g = lambda *args: subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()
    subprocess.check_call(['git', 'init', '-q', str(repo)])
    assert pathlib.Path(g('rev-parse', '--show-toplevel')) == repo, 'fixture toplevel mismatch'
    g('config', 'user.name', 's59critic')
    g('config', 'user.email', 's59critic@invalid')
    raw = subprocess.check_output(['git', '-C', LANE, 'show', BASE + ':SKILL.md'], text=True)
    orig = next(l for l in raw.splitlines() if l.startswith('| r58 assessment comparison |'))
    gate58 = orig.replace('| evidence |', '| gate |')
    cases = [
        ('A-flip-r58-cell-only', [gate58],
         'CHEAPEST SKIP-WORK CONTROL: one kind cell edited, no r59 row, no gate file, no selftest'),
        ('B-r58-evidence+r59-gate', [orig, R59_GATE],
         'SUBJECT DRIFT: population item R58-KIND still says evidence, counter green'),
        ('C-r58-gate+r59-evidence', [gate58, R59_EVID],
         'SUBJECT DRIFT: counter scores the r59 row, r58 row untouched'),
        ('D-r58-gate+r59-gate', [gate58, R59_GATE],
         'both rows gate: counter green'),
        ('E-r59-row-9-columns', [orig, R59_GATE.replace('| souji |', '| souji | extra |')],
         'wrong column count -> REGISTRY-ROW-SHAPE rc2'),
        ('F-pipe-inside-verdict-cell', [orig, '| r59 assessment comparison | gate | c | 0 clean | 1 failed | s | p | w | souji |'],
         'literal pipe in a cell -> REGISTRY-ROW-SHAPE rc2'),
        ('G-r59-row-empty-cells', [orig, '| r59 assessment comparison | gate | | | | | | | |'],
         'all other cells blank -> 9 cells, not 8 -> REGISTRY-ROW-SHAPE rc2'),
        ('H-fabricated-nonexistent-gate', [orig, '| r59 assessment comparison | gate | `python3 -B census/round-59/NONEXISTENT-gate.py --root LANE` | 0 clean | `python3 -B census/round-59/NONEXISTENT-gate.py --selftest` | census/round-59/missing-expected.tsv | read-only | souji |'],
         'cited gate file and pinned-value path do not exist -> counter green'),
        ('I-r59-row-inside-fenced-block', [orig, '```\n' + R59_GATE + '\n```'],
         'row inside a fenced code block -> counter green'),
        ('J-r59-row-inside-html-comment', [orig, '<!--\n' + R59_GATE + '\n-->'],
         'row inside a multi-line HTML comment -> counter green'),
        ('K-r59-row-misnamed-case', [orig, R59_GATE.replace('r59 assessment', 'r59 Assessment')],
         'row name case changed -> not selected; falls back to r58'),
        ('L-two-r59-rows', [orig, R59_GATE, R59_GATE.replace('| gate |', '| probe |')],
         'duplicate r59 rows -> REGISTRY-ROW-SHAPE rc2'),
        ('M-r59-row-list-item', [orig, '- ' + R59_GATE],
         'row as a list item -> not selected'),
        ('O-r59-gate-empty-other-cells', [orig, '| r59 assessment comparison | gate | | | | | | |'],
         'kind=gate with entry command, verdict map, self-test, pinned path, write scope ALL BLANK -> counter green'),
        ('P-r58-row-gate-with-stale-selftest-cell', [gate58, R59_GATE],
         'r58 kind flipped to gate while its self-test cell still admits no self-invocation certification; counter cannot see the stale cell'),
        ('N-r59-row-trailing-spaces', [orig, R59_GATE + '   '],
         'trailing whitespace -> still selected'),
    ]
    for name, lines, note in cases:
        (repo / 'SKILL.md').write_text('\n'.join(lines) + '\n')
        g('add', 'SKILL.md')
        g('commit', '-qm', name)
        rev = g('rev-parse', 'HEAD')
        r = subprocess.run(['python3', '-B', COUNTER, '--root', str(repo), '--rev', rev],
                           text=True, capture_output=True)
        print('CASE %-30s rc=%d :: %s' % (name, r.returncode, r.stdout.strip().replace('\n', ' | ')))
        print('     note: %s' % note)
    return 0


if __name__ == '__main__':
    sys.exit(main())
