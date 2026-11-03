#!/usr/bin/env python3
"""S56mutation02: build single-defect mutants of the frozen v5 C2 counter.

Every replacement is an exact, single-occurrence edit of the committed bytes
(sha256 5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8).
Each mutant tree mirrors census/round-56 so the counter's HERE-relative
fixtures/ and records/ resolve; builder and expected TSV are byte-identical
copies (never edited).
"""
import hashlib
import shutil
import sys
import difflib
from pathlib import Path

ROOT = Path('/fast/scratch/hyaku/souji-r56/S56mutation02')
BASE_TREE = ROOT / 'base-tree' / 'census' / 'round-56'
BASE_SHA = '5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8'

M = {}

M['N1'] = ('RECEIPT_KV first key class reverted to [A-Za-z] (r55 RD-A regression)', [
    ("RECEIPT_KV = re.compile(r'\\s*#\\s*([A-Za-z0-9_][A-Za-z0-9_]*)\\s*=\\s*(\\S*)\\s*')",
     "RECEIPT_KV = re.compile(r'\\s*#\\s*([A-Za-z][A-Za-z0-9_]*)\\s*=\\s*(\\S*)\\s*')"),
])

M['N2'] = ('RECEIPT_KV value group back to \\S+ (empty value ignored, S55-S5)', [
    ("RECEIPT_KV = re.compile(r'\\s*#\\s*([A-Za-z0-9_][A-Za-z0-9_]*)\\s*=\\s*(\\S*)\\s*')",
     "RECEIPT_KV = re.compile(r'\\s*#\\s*([A-Za-z0-9_][A-Za-z0-9_]*)\\s*=\\s*(\\S+)\\s*')"),
])

M['N3'] = ('SELFTEST-ROW-MISMATCH assertion loops removed (row-set check off)', [
    ("""    for r in sorted(exp):
        if r not in names:
            ok = False
            out.append('SELFTEST-ROW-MISMATCH expected row did not run: %s' % r)
    for n in names:
        if n not in exp:
            ok = False
            out.append('SELFTEST-ROW-MISMATCH ran without an expected row: %s' % n)
""",
     """    # N3 mutant: the SELFTEST-ROW-MISMATCH loops are removed.
"""),
])

M['N4'] = ('FA9-WRONG-TOOL-PIN arm removed from the selftest run list', [
    ("names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE']",
     "names = list(mod.C2_FIXTURES) + ['FB4-PIN-SHAPE']"),
])

M['N5'] = ('FB4-PIN-SHAPE arm removed from the selftest run list', [
    ("names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE']",
     "names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN']"),
])

M['N6'] = ('COMMENT-AMBIGUOUS-NAME rule back to v3 (>=5 tabs only)', [
    ("""            if '\\t' in ln:""",
     """            if ln.count('\\t') >= 5:"""),
])

M['N7'] = ('unknown-receipt-key check dropped entirely', [
    ("""    if unknown_key is not None:
        finding('RECEIPT-UNKNOWN-KEY', 'receipt carries unknown key %s' % unknown_key)
""",
     """    # N7 mutant: the unknown-key check is dropped.
"""),
])

M['N8'] = ('ROWS-UNSORTED check dropped', [
    ("""    if unsorted:
        finding('ROWS-UNSORTED', 'data rows are not in ascending byte order of name')
""",
     """    # N8 mutant: the ROWS-UNSORTED check is dropped.
"""),
])

M['N9'] = ('CAPTURE-CRLF check dropped', [
    ("""    if b'\\r' in cap:
        finding('CAPTURE-CRLF', 'capture bytes carry CR (carriage return)')
""",
     """    # N9 mutant: the CAPTURE-CRLF check is dropped.
"""),
])

M['N10'] = ('--tool-sha256 pin branch dropped (malformed + mismatch checks)', [
    ("""    if tool_sha_pin is not None:
        if not re.fullmatch(r'[0-9a-f]{64}', tool_sha_pin):
            out.append('CANNOT-EVALUATE TOOL-SHA-ARG-MALFORMED --tool-sha256 must be lowercase 64-hex')
            return 2
        if tool_sha_pin != tool_sha:
            finding('TOOL-SHA-ARG-MISMATCH', 'pinned=%s observed=%s'
                    % (tool_sha_pin[:12], tool_sha[:12]))
""",
     """    # N10 mutant: the tool-sha256 pin branch is dropped.
"""),
])

M['N11'] = ('over-strict name rule: a leading dot is a bad name (real-lane-only defect)', [
    ("""        if (not name or name != name.strip() or '/' in name or name == '.git'
                or name in names or name.startswith('#')):""",
     """        if (not name or name != name.strip() or '/' in name or name == '.git'
                or name in names or name.startswith('#') or name.startswith('.')):"""),
])

# Composed probe (not a single defect): N3 + N4 — proves the row-set check is
# the ONLY detector of an arm removal, and that N3 disables it.
M['N3N4'] = ('composed: row-set loops removed AND FA9 arm removed', [
    ("""    for r in sorted(exp):
        if r not in names:
            ok = False
            out.append('SELFTEST-ROW-MISMATCH expected row did not run: %s' % r)
    for n in names:
        if n not in exp:
            ok = False
            out.append('SELFTEST-ROW-MISMATCH ran without an expected row: %s' % n)
""",
     """    # N3 mutant: the SELFTEST-ROW-MISMATCH loops are removed.
"""),
    ("names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE']",
     "names = list(mod.C2_FIXTURES) + ['FB4-PIN-SHAPE']"),
])


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def main():
    base = (BASE_TREE / 'c2-counter.py').read_bytes()
    assert sha256(base) == BASE_SHA, 'base copy drifted: %s' % sha256(base)
    outdir = ROOT / 'mutants'
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    log = []
    for mid, (desc, edits) in M.items():
        text = base.decode()
        for old, new in edits:
            n = text.count(old)
            assert n == 1, '%s: snippet occurs %d times, need exactly 1:\n%r' % (mid, n, old[:80])
            text = text.replace(old, new)
        mut = text.encode()
        tree = outdir / mid / 'census' / 'round-56'
        (tree / 'fixtures').mkdir(parents=True)
        (tree / 'records').mkdir(parents=True)
        (tree / 'c2-counter.py').write_bytes(mut)
        shutil.copyfile(BASE_TREE / 'fixtures' / 'build-fixtures.py',
                        tree / 'fixtures' / 'build-fixtures.py')
        shutil.copyfile(BASE_TREE / 'records' / 'c2-selftest-expected.tsv',
                        tree / 'records' / 'c2-selftest-expected.tsv')
        assert sha256((tree / 'fixtures' / 'build-fixtures.py').read_bytes()) == \
            '2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a'
        assert sha256((tree / 'records' / 'c2-selftest-expected.tsv').read_bytes()) == \
            '90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3'
        diff = ''.join(difflib.unified_diff(
            base.decode().splitlines(True), text.splitlines(True),
            fromfile='base/c2-counter.py', tofile='%s/c2-counter.py' % mid))
        (ROOT / 'run' / ('%s.diff' % mid)).write_text(diff)
        log.append('%s\t%s\t%s\t%s' % (mid, sha256(mut), len(edits), desc))
        print('%s sha256=%s edits=%d %s' % (mid, sha256(mut), len(edits), desc))
    (ROOT / 'run' / 'mutants.tsv').write_text(
        'mutant\tsha256\tedits\tdescription\n' + '\n'.join(log) + '\n')
    # base tree untouched?
    assert sha256((BASE_TREE / 'c2-counter.py').read_bytes()) == BASE_SHA
    print('BASE %s intact' % BASE_SHA)
    return 0


if __name__ == '__main__':
    sys.exit(main())
