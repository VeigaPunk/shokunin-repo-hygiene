#!/usr/bin/env python3
"""souji round 53 fixture builder (frozen with the round-53 preregistration).

Builds the synthetic git repositories for the round-53 claim matrix:

  C1 (annotation-agreement counter v2, five named r52 limits):
    F1-HONEST-TIP   stale (78) annotations, both sites filed by corrections
                    -> v1 exit 0, v2 exit 0 (discrimination control)
    F2-MULTI-ANNOT  a planted `-> 79` before the stale (78) in the annotation
                    zone -> v1 accepts the first annotation (exit 0),
                    v2 kills MULTIPLE-ANNOTATIONS (exit 1)
    F3-INERT        site S1 now reads its recomputed value but a correction
                    still names it -> v1 exit 0, v2 kills INERT-CORRECTION
    F4-FENCE        both correction lines inside a fenced code block
                    -> v1 exit 0, v2 kills CORRECTION-IN-FENCE
    F5-REWRITE      the stale S1 annotation rewritten in place base->tip
                    -> v1 exit 0 at the tip, v2 kills DELETED-LINES (--base)
    F6-RECORD-DRIFT the recomputed record rewritten so the annotation matches
                    the drifted count -> v1 exit 0, v2 kills RECORD-SHA-MISMATCH

  C2 (capture counter v2, three named r52 limits); each repo carries the
  capture at the v1-counter path so the frozen v1 counter reads it:
    FH-HONEST       sorted consistent capture + RECEIPT_VERSION=1 run receipt
                    -> v1 exit 0, v2 exit 0
    FA1-UNSORTED    same rows, reversed order -> v1 exit 0, v2 ROWS-UNSORTED
    FA2-COMMENT     a `#`-leading data row left in the file but struck from
                    ENTRIES/COUNT -> v1 exit 0, v2 COMMENT-AMBIGUOUS-NAME
    FA3-TAMPER      honest capture with one name byte flipped, receipt still
                    binds the original bytes -> v1 exit 0,
                    v2 CAPTURE-RECEIPT-MISMATCH

Every repo is created under --work/<name>/ with `git init`, a repo-local
fixture identity, and a verified toplevel (`git rev-parse --show-toplevel`
must equal the fixture dir) before the first commit. Two commits: base, tip.
Writes nothing outside --work. No network. Honours --work (never /tmp).

Usage:
  python3 -B build-fixtures.py --work DIR [--manifest OUT.tsv] [--list]
"""
import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ANCHOR = 'grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv'
S2_LINE = '`%s` (78);' % ANCHOR  # census/round-51/preregistration.txt line 125 shape

RECORD_BODY = (
    ['# souji round-51 workspace-census drift vs r46 (fixture copy)']
    + ['ADDED\trow-%02d' % i for i in range(1, 80)]   # 79 ADDED lines
    + ['REMOVED\trow-a', 'REMOVED\trow-b']
)

FENCE_OPEN = '```text'
FENCE_CLOSE = '```'

C1_FIXTURES = ['F1-HONEST-TIP', 'F2-MULTI-ANNOT', 'F3-INERT', 'F4-FENCE',
               'F5-REWRITE', 'F6-RECORD-DRIFT']
C2_FIXTURES = ['FH-HONEST', 'FA1-UNSORTED', 'FA2-COMMENT', 'FA3-TAMPER']

FLEET_HEAD = '0123456789abcdef0123456789abcdef01234567'

STUB_TOOL = (
    '#!/usr/bin/env python3\n'
    '# fixture stand-in for tools/souji-fleet-root-census.py (round-53 fixtures).\n'
    '# The counters only digest these bytes; they never execute the fixture tool.\n'
    'print("fixture tool; not executable for census purposes")\n'
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd, cwd=None, env=None):
    e = dict(env or os.environ)
    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True)
    if p.returncode:
        raise RuntimeError('fixture cmd failed: %r\n%s\n%s'
                           % (cmd, p.stdout.decode('utf-8', 'replace'),
                              p.stderr.decode('utf-8', 'replace')))
    return p.stdout.decode('utf-8', 'replace').strip()


def git_env():
    e = {
        'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
        'LC_ALL': 'C', 'GIT_TERMINAL_PROMPT': '0',
        'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
        'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
        'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1',
        'HOME': os.environ.get('HYAKU_SCRATCH_HOME', os.environ.get('HOME', '/nonexistent')),
    }
    return e


def write(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode('utf-8')
    path.write_bytes(data)


def build_c1(name: str, root: Path):
    """Return (record_sha_base, scorecard_tip_lines) for the fixture kind."""
    record_base = '\n'.join(RECORD_BODY) + '\n'
    record_tip = record_base
    # Site line numbers inside THIS fixture's files (1-based).
    sc_lines_base = [
        '# fixture SCORECARD (round-53 C1 matrix, %s)' % name,
        '',
        '| row | note |',
        '|---|---|',
        '| C1 | command `%s` (78) recomputed below |' % ANCHOR,
    ]
    s1_ln = sc_lines_base.index(sc_lines_base[4]) + 1  # == 5
    pre_lines_base = [
        '# fixture preregistration (round-53 C1 matrix, %s)' % name,
        'sites:',
        S2_LINE,
    ]
    s2_ln = 3
    corr_scorecard = [
        '',
        'R52-CORRECTION SCORECARD.md:%d stale=78 recomputed=79' % s1_ln,
        'R52-CORRECTION census/round-51/preregistration.txt:%d stale=78 recomputed=79' % s2_ln,
        '',
    ]
    sc_tip = list(sc_lines_base)
    pre_tip = list(pre_lines_base)
    corrections = list(corr_scorecard)

    if name == 'F1-HONEST-TIP':
        pass
    elif name == 'F2-MULTI-ANNOT':
        sc_tip[4] = '| C1 | command `%s` → 79 then (78) stale pair planted |' % ANCHOR
    elif name == 'F3-INERT':
        # S1 no longer stale: it now reads the recomputed 79, but a correction
        # still names it. S2 stays genuinely stale and filed.
        sc_tip[4] = '| C1 | command `%s` (79) recomputed below |' % ANCHOR
        corrections = [
            '',
            'R52-CORRECTION SCORECARD.md:%d stale=79 recomputed=79' % s1_ln,
            'R52-CORRECTION census/round-51/preregistration.txt:%d stale=78 recomputed=79' % s2_ln,
            '',
        ]
    elif name == 'F4-FENCE':
        corrections = [
            '', FENCE_OPEN,
            'R52-CORRECTION SCORECARD.md:%d stale=78 recomputed=79' % s1_ln,
            'R52-CORRECTION census/round-51/preregistration.txt:%d stale=78 recomputed=79' % s2_ln,
            FENCE_CLOSE, '',
        ]
    elif name == 'F5-REWRITE':
        # The tip rewrites the stale S1 annotation in place (base and tip both
        # committed; --base catches the deletion); S2 stays stale and filed.
        sc_tip[4] = '| C1 | command `%s` (79) rewritten in place |' % ANCHOR
        corrections = [
            '',
            'R52-CORRECTION census/round-51/preregistration.txt:%d stale=78 recomputed=79' % s2_ln,
            '',
        ]
    elif name == 'F6-RECORD-DRIFT':
        drifted = list(RECORD_BODY)
        drifted.append('ADDED\trow-80')
        record_tip = '\n'.join(drifted) + '\n'
        sc_tip[4] = '| C1 | command `%s` (80) matches the drifted record |' % ANCHOR
        pre_tip[2] = '`%s` (80);' % ANCHOR
        corrections = None
    else:
        raise SystemExit('unknown C1 fixture %s' % name)

    if corrections is not None:
        sc_tip = sc_tip + corrections
    sc_tip.append('')
    return record_base, record_tip, sc_lines_base, sc_tip, pre_lines_base, pre_tip


def init_repo(workdir: Path, name: str) -> Path:
    d = workdir / name
    if d.exists():
        import shutil
        shutil.rmtree(d)
    d.mkdir(parents=True, exist_ok=False)
    run(['git', 'init', '-q', str(d)], env=git_env())
    top = run(['git', '-C', str(d), 'rev-parse', '--show-toplevel'], env=git_env())
    if Path(top) != d:
        raise SystemExit('fixture toplevel mismatch %s != %s' % (top, d))
    for k, v in (('user.name', 'fixture'), ('user.email', 'fixture@invalid'),
                 ('commit.gpgsign', 'false'), ('core.fsmonitor', 'false')):
        run(['git', '-C', str(d), 'config', k, v], env=git_env())
    return d


def commit_all(d: Path, msg: str) -> str:
    run(['git', '-C', str(d), 'add', '-A'], env=git_env())
    run(['git', '-C', str(d), 'commit', '-q', '-m', msg], env=git_env())
    return run(['git', '-C', str(d), 'rev-parse', 'HEAD'], env=git_env())


def build_one(name: str, workdir: Path):
    genv = git_env()
    if name in C1_FIXTURES:
        record_base, record_tip, sc_base, sc_tip, pre_base, pre_tip = build_c1(name, workdir)
        d = init_repo(workdir, name)
        write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', record_base)
        write(d / 'SCORECARD.md', '\n'.join(sc_base) + '\n')
        write(d / 'census/round-51/preregistration.txt', '\n'.join(pre_base) + '\n')
        base = commit_all(d, 'fixture base')
        write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', record_tip)
        write(d / 'SCORECARD.md', '\n'.join(sc_tip) + '\n')
        write(d / 'census/round-51/preregistration.txt', '\n'.join(pre_tip) + '\n')
        tip = commit_all(d, 'fixture tip')
        return {'name': name, 'dir': str(d), 'base': base, 'tip': tip,
                'record_sha256': sha256(record_base.encode()),
                'kind': 'C1'}
    if name in C2_FIXTURES:
        stub = STUB_TOOL.encode()
        tool_sha = sha256(stub)
        rows = [
            ('a.txt', 'file', 'yes', 'no', 'tracked', 'none'),
            ('b.md', 'file', 'yes', 'no', 'tracked', 'none'),
            ('zz', 'dir', 'no', 'yes', 'ignored', 'none'),
        ]
        # FA2-COMMENT adds a '#'-leading data row: present in the file, struck
        # from ENTRIES/COUNT (the v1 grammar silently reads it as a comment).
        hidden = ('#odd', 'file', 'no', 'no', 'untracked-stray', 'report-only')
        capture_rows = list(rows)
        counts = {'tracked': 2, 'ignored': 1, 'untracked-stray': 0, 'symlink': 0}
        entries = 3
        if name == 'FA2-COMMENT':
            capture_rows = sorted(capture_rows + [hidden], key=lambda r: r[0].encode())
            counts['untracked-stray'] = 0  # struck from the declared counts
            entries = 3
        if name == 'FA1-UNSORTED':
            capture_rows = list(reversed(capture_rows))
        if name == 'FA3-TAMPER':
            capture_rows = [('ax.txt',) + tuple(r[1:]) if r[0] == 'a.txt' else r
                            for r in capture_rows]
        body_rows = []
        for r in capture_rows:
            if name == 'FA2-COMMENT' and r[0] == '#odd':
                body_rows.append('#%s\t%s\t%s\t%s\t%s\t%s' % r)  # raw emission, no space
                continue
            body_rows.append('%s\t%s\t%s\t%s\t%s\t%s' % r)
        capture = '\n'.join(
            ['# fixture fleet-root census (round-53 C2 matrix, %s)' % name,
             '# SCOPE=top-level entries, dotfiles included, .git excluded',
             '# TOOL_SHA256=%s' % tool_sha,
             '# FLEET_HEAD=%s' % FLEET_HEAD,
             '# ENTRIES=%d' % entries,
             '# COUNT tracked=%d' % counts['tracked'],
             '# COUNT ignored=%d' % counts['ignored'],
             '# COUNT untracked-stray=%d' % counts['untracked-stray'],
             '# COUNT symlink=%d' % counts['symlink'],
             'name\tkind\ttracked\tignored\tclass\tdisposition']
            + body_rows) + '\n'
        # The receipt always binds the ORIGINAL (untampered) capture bytes so
        # FA3-TAMPER demonstrates the byte flip; other fixtures' receipts bind
        # their own capture bytes.
        receipt_capture = capture
        if name == 'FA3-TAMPER':
            rows_o = [('a.txt',) + tuple(r[1:]) if r[0] == 'ax.txt' else r
                      for r in capture_rows]
            receipt_rows = ['%s\t%s\t%s\t%s\t%s\t%s' % r for r in rows_o]
            receipt_capture = '\n'.join(
                ['# fixture fleet-root census (round-53 C2 matrix, %s)' % name,
                 '# SCOPE=top-level entries, dotfiles included, .git excluded',
                 '# TOOL_SHA256=%s' % tool_sha,
                 '# FLEET_HEAD=%s' % FLEET_HEAD,
                 '# ENTRIES=%d' % entries,
                 '# COUNT tracked=%d' % counts['tracked'],
                 '# COUNT ignored=%d' % counts['ignored'],
                 '# COUNT untracked-stray=%d' % counts['untracked-stray'],
                 '# COUNT symlink=%d' % counts['symlink'],
                 'name\tkind\ttracked\tignored\tclass\tdisposition']
                + receipt_rows) + '\n'
        receipt = '\n'.join(
            ['# fixture run receipt (machine-readable block, RECEIPT_VERSION=1)',
             '# RECEIPT_VERSION=1',
             '# TOOL_SHA256=%s' % tool_sha,
             '# FLEET_HEAD=%s' % FLEET_HEAD,
             '# CAPTURE_SHA256=%s' % sha256(receipt_capture.encode()),
             '# ENTRIES=%d' % entries,
             'command: fixture census run (synthetic); no live root was read',
             '']) 
        d = init_repo(workdir, name)
        write(d / 'census/round-52/records/fleet-root-census.tsv', capture)
        write(d / 'census/round-53/records/fleet-root-census-run.txt', receipt)
        write(d / 'tools/souji-fleet-root-census.py', stub)
        base = commit_all(d, 'fixture base')
        tip = base  # single-commit fixtures; the counter reads --rev = tip
        return {'name': name, 'dir': str(d), 'base': base, 'tip': tip,
                'record_sha256': '-', 'kind': 'C2'}
    raise SystemExit('unknown fixture %s' % name)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', required=True, help='existing scratch dir (never /tmp defaults)')
    ap.add_argument('--manifest', default=None)
    ap.add_argument('--list', action='store_true')
    ns = ap.parse_args()
    work = Path(ns.work)
    if not work.is_dir():
        raise SystemExit('--work must exist: %s' % work)
    names = C1_FIXTURES + C2_FIXTURES
    if ns.list:
        print('\n'.join(names))
        return 0
    lines = ['name\tkind\tdir\tbase\ttip\trecord_sha256']
    for n in names:
        info = build_one(n, work)
        lines.append('%(name)s\t%(kind)s\t%(dir)s\t%(base)s\t%(tip)s\t%(record_sha256)s' % info)
        print('BUILT %s tip=%s' % (n, info['tip']), file=sys.stderr)
    out = ns.manifest or str(work / 'fixture-manifest.tsv')
    Path(out).write_text('\n'.join(lines) + '\n')
    print('MANIFEST %s' % out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
