#!/usr/bin/env python3
"""Independent recomputation of the frozen claim population at the base revision.

No import of the frozen counter; parses `git show BASE:SKILL.md` twice by
different methods and derives the mismatch count from the frozen target:
one unique current assessment-comparison registry row, kind == gate.
"""
import re
import subprocess
import sys

LANE = '/home/vgpnk/Projects/shokunin/souji-shokunin'
BASE = 'da5af55b5ea0a2a38edea05635a13416c698e6e7'


def main():
    raw = subprocess.check_output(['git', '-C', LANE, 'show', BASE + ':SKILL.md'], text=True)
    lines = raw.split('\n')

    # Method 1: exact-prefix line scan mirroring the frozen counter's selection order.
    r59 = [ln for ln in lines if ln.startswith('| r59 assessment comparison |')]
    selected = r59 if r59 else [ln for ln in lines if ln.startswith('| r58 assessment comparison |')]
    print('M1 r59-prefix-lines=%d r58-prefix-lines=%d selected=%d branch=%s'
          % (len(r59), sum(ln.startswith('| r58 assessment comparison |') for ln in lines),
             len(selected), 'r59' if r59 else 'r58'))

    # Method 2: independent full-line grammar over markdown table rows with that label.
    grammar = re.compile(r'^\|(?:\s*[^|]*\s*\|)+\s*$')
    labelled = []
    for no, ln in enumerate(lines, 1):
        if not ln.startswith('|'):
            continue
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        if cells and cells[0] in ('r59 assessment comparison', 'r58 assessment comparison'):
            labelled.append((no, cells[0], len(cells), cells))
    print('M2 labelled-rows=%d' % len(labelled))
    for no, label, n, cells in labelled:
        print('M2 row line=%d label=%s cells=%d kind=%r full-grammar=%s'
              % (no, label, n, cells[1] if n > 1 else None, bool(grammar.match(lines[no - 1]))))

    # Frozen target: one unique current row shaped as 8 cells (split('|') length 10) with kind gate.
    mismatches = []
    if len(selected) != 1:
        print('FINDING REGISTRY-ROW-SHAPE')
        shape_ok = False
    else:
        parts = selected[0].split('|')
        shape_ok = len(parts) == 10
        if not shape_ok:
            print('FINDING REGISTRY-ROW-SHAPE')
        else:
            cells = [c.strip() for c in parts]
            print('ROW line=%d cells=%d kind=%r' % (lines.index(selected[0]) + 1, len(cells) - 2, cells[2]))
            if cells[2] != 'gate':
                mismatches.append('REGISTRY-KIND-MISMATCH')
    for f in mismatches:
        print('FINDING ' + f)
    print('INDEPENDENT assertions=1 mismatches=%d row_shape_ok=%s rev=%s' % (len(mismatches), shape_ok, BASE))
    print('CROSSCHECK expected_from_frozen_before=mismatches=1 finding=REGISTRY-KIND-MISMATCH exit=1')
    return 1 if (mismatches or not shape_ok) else 0


if __name__ == '__main__':
    sys.exit(main())
