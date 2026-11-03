#!/usr/bin/env python3
"""souji round 54 fixture builder (frozen with the round-54 preregistration).

Builds the synthetic git repositories for the round-54 claim matrix:

  C1 (annotation-agreement counter v3; F1-F6 carry the r53 matrix over,
      F7-F12b are the r53 routed surfaces — corpus/lessons/round-53.md):
    F1-HONEST-TIP    stale (78) annotations, both sites filed by corrections
                     -> v2 exit 0, v3 exit 0 (discrimination control)
    F2-MULTI-ANNOT   a planted `-> 79` before the stale (78) in the zone
                     -> v2 kills MULTIPLE-ANNOTATIONS, v3 keeps the kill
    F3-INERT         site S1 now reads its recomputed value but a correction
                     still names it -> v2 kills INERT-CORRECTION, v3 keeps
    F4-FENCE         both correction lines inside a ```text fence
                     -> v2 kills CORRECTION-IN-FENCE, v3 keeps
    F5-REWRITE       the stale S1 annotation rewritten in place base->tip
                     -> v2 kills DELETED-LINES (--base), v3 keeps
    F6-RECORD-DRIFT  the recomputed record rewritten so the annotation matches
                     -> v2 kills RECORD-SHA-MISMATCH, v3 keeps
    F7-TILDE-FENCE   corrections inside a ~~~ tilde fence (r53 R1)
                     -> v2 accepts (exit 0), v3 CORRECTION-IN-FENCE
    F8-BT4-PARITY    corrections inside a 4-backtick fence past a 3-backtick
                     content line (r53 R1 parity) -> v2 accepts, v3 kills
    F9-HTML-COMMENT  corrections inside an <!-- HTML comment --> (r53 R1)
                     -> v2 accepts, v3 kills
    F10-STRADDLE     a `-> 79` token planted so it starts inside the frozen
                     32-char zone and ends beyond it (r53 R2)
                     -> v2 accepts (token invisible), v3
                     ZONE-TOKEN-STRADDLES-EDGE
    F11-BOGUS-RECOMP site already reads 79, correction claims recomputed=83 (r53 R3)
                     -> v2 accepts (exit 0), v3 BOGUS-RECOMPUTED
    F12-LOG-UNFILED  LOG.md carries `corpus/SOURCES.md 274 -> 275 rows` (the
                     r53 misread class) with no pair-form filing (r53 Mistakes
                     row 5) -> v2 accepts, v3 UNFILED-SOURCES-ANNOTATION
    F12b-LOG-FILED   the same class with a valid pair filing whose recomputed
                     pair equals the counts at the pinned revisions
                     -> v2 accepts, v3 exit 0 (honest-handling control)

  C2 (capture counter v3; FH/FA1-FA3 carry the r53 matrix over):
    FH-HONEST         sorted consistent capture + RECEIPT_VERSION=1 receipt
                      -> v2 exit 0, v3 exit 0
    FH2-SYMLINK-HONEST honest capture including a symlink-kind row
                      -> both exit 0 (branch coverage, r53 R7 M-F2)
    FA1-UNSORTED      rows reversed -> both kill ROWS-UNSORTED
    FA2-COMMENT       a `#odd` 6-field row struck from ENTRIES/COUNT
                      -> both kill COMMENT-AMBIGUOUS-NAME
    FA3-TAMPER        one name byte flipped, receipt binds original bytes
                      -> both kill CAPTURE-RECEIPT-MISMATCH
    FA4-SPACE-NAME    a `#odd name` (space in name) 6-field row struck from
                      ENTRIES/COUNT (r53 R4) -> v2 accepts (free-form
                      comment), v3 COMMENT-AMBIGUOUS-NAME
    FA5-EXTRA-KEY     receipt carries unknown `# GENERATOR=fixture` (r53 R5)
                      -> v2 accepts, v3 RECEIPT-UNKNOWN-KEY
    FA6-CRLF          honest capture with CRLF line endings (r53 R5)
                      -> v2 exit 1 generic (unnamed), v3 CAPTURE-CRLF
    FA7-RECEIPT-ENTRIES  receipt ENTRIES=4 against a 3-row capture (r53 R7
                      M-F1 branch coverage) -> both kill
                      CAPTURE-RECEIPT-MISMATCH
    FA8-SYMLINK-CLASS a symlink-kind row claiming class `tracked` (r53 R7
                      M-F2 branch coverage) -> both exit 1 (class rule)

Every repo is created under --work/<name>/ with `git init`, a repo-local
fixture identity, and a verified toplevel (`git rev-parse --show-toplevel`
must equal the fixture dir) before the first commit. Two commits: base, tip.
Writes nothing outside --work. No network. Honours --work (never /tmp).
Hardened per the r53 routed items R8/R10: every subprocess call carries a
timeout, every git call carries -c core.fsmonitor=false -c
core.hooksPath=/dev/null, and commits pin GIT_AUTHOR_DATE/GIT_COMMITTER_DATE
so a rebuild reproduces the fixture commit ids.

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

# Fixed fixture timestamps (r53 R10): identical content + identity + dates
# rebuild identical commit ids.
T0 = '2026-11-04T12:00:00+00:00'
T1 = '2026-11-04T12:01:00+00:00'

C1_FIXTURES = ['F1-HONEST-TIP', 'F2-MULTI-ANNOT', 'F3-INERT', 'F4-FENCE',
               'F5-REWRITE', 'F6-RECORD-DRIFT', 'F7-TILDE-FENCE',
               'F8-BT4-PARITY', 'F9-HTML-COMMENT', 'F10-STRADDLE',
               'F11-BOGUS-RECOMP', 'F12-LOG-UNFILED', 'F12b-LOG-FILED']
C2_FIXTURES = ['FH-HONEST', 'FH2-SYMLINK-HONEST', 'FA1-UNSORTED', 'FA2-COMMENT',
               'FA3-TAMPER', 'FA4-SPACE-NAME', 'FA5-EXTRA-KEY', 'FA6-CRLF',
               'FA7-RECEIPT-ENTRIES', 'FA8-SYMLINK-CLASS']

FLEET_HEAD = '0123456789abcdef0123456789abcdef01234567'

STUB_TOOL = (
    '#!/usr/bin/env python3\n'
    '# fixture stand-in for tools/souji-fleet-root-census.py (round-54 fixtures).\n'
    '# The counters only digest these bytes; they never execute the fixture tool.\n'
    'print("fixture tool; not executable for census purposes")\n'
)

REGISTRY_3ROWS = '\n'.join([
    '# fixture SOURCES registry (round-54 C1 LOG/README matrix)',
    '| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |',
    '|---|---|---|---|---|---|---|---|---|---|---|',
    '| S001 | fixture one | docs | A | fixture | §1 | one | queued | 2026-11-04 | 90d | — |',
    '| S002 | fixture two | docs | A | fixture | §2 | two | queued | 2026-11-04 | 90d | — |',
    '| S003 | fixture three | docs | A | fixture | §3 | three | queued | 2026-11-04 | 90d | — |',
]) + '\n'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd, cwd=None, env=None):
    e = dict(env or os.environ)
    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, timeout=120)
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
        'GIT_AUTHOR_DATE': T0, 'GIT_COMMITTER_DATE': T0,
        'HOME': os.environ.get('HYAKU_SCRATCH_HOME', os.environ.get('HOME', '/nonexistent')),
    }
    return e


def write(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode('utf-8')
    path.write_bytes(data)


def git(d: Path, *args, date=None):
    e = git_env()
    if date is not None:
        e['GIT_AUTHOR_DATE'] = date
        e['GIT_COMMITTER_DATE'] = date
    return run(['git', '-C', str(d),
                '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null'] + list(args), env=e)


def init_repo(workdir: Path, name: str) -> Path:
    d = workdir / name
    if d.exists():
        import shutil
        shutil.rmtree(d)
    d.mkdir(parents=True, exist_ok=False)
    git(d.parent, 'init', '-q', str(d))
    top = git(d, 'rev-parse', '--show-toplevel')
    if Path(top) != d:
        raise SystemExit('fixture toplevel mismatch %s != %s' % (top, d))
    for k, v in (('user.name', 'fixture'), ('user.email', 'fixture@invalid'),
                 ('commit.gpgsign', 'false'), ('core.fsmonitor', 'false')):
        git(d, 'config', k, v)
    return d


def commit_all(d: Path, msg: str, date: str) -> str:
    git(d, 'add', '-A', date=date)
    git(d, 'commit', '-q', '-m', msg, date=date)
    return git(d, 'rev-parse', 'HEAD', date=date)


def sc_base_lines(name):
    return [
        '# fixture SCORECARD (round-54 C1 matrix, %s)' % name,
        '',
        '| row | note |',
        '|---|---|',
        '| C1 | command `%s` (78) recomputed below |' % ANCHOR,
    ]


def pre_base_lines(name):
    return [
        '# fixture preregistration (round-54 C1 matrix, %s)' % name,
        'sites:',
        S2_LINE,
    ]


def base_corrections(s1_ln, s2_ln, recomputed='79'):
    return [
        '',
        'R52-CORRECTION SCORECARD.md:%d stale=78 recomputed=%s' % (s1_ln, recomputed),
        'R52-CORRECTION census/round-51/preregistration.txt:%d stale=78 recomputed=%s' % (s2_ln, recomputed),
        '',
    ]


def build_c1(name: str, workdir: Path):
    record_base = '\n'.join(RECORD_BODY) + '\n'
    record_tip = record_base
    sc_lines_base = sc_base_lines(name)
    s1_ln = 5
    pre_lines_base = pre_base_lines(name)
    s2_ln = 3
    corrections = base_corrections(s1_ln, s2_ln)
    sc_tip = list(sc_lines_base)
    pre_tip = list(pre_lines_base)
    log_tip = None
    registry_tip = None
    pair_filing = None
    sources_revs = None

    if name == 'F1-HONEST-TIP':
        pass
    elif name == 'F2-MULTI-ANNOT':
        sc_tip[4] = '| C1 | command `%s` → 79 then (78) stale pair planted |' % ANCHOR
    elif name == 'F3-INERT':
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
    elif name == 'F7-TILDE-FENCE':
        corrections = [
            '', '~~~',
            'R52-CORRECTION SCORECARD.md:%d stale=78 recomputed=79' % s1_ln,
            'R52-CORRECTION census/round-51/preregistration.txt:%d stale=78 recomputed=79' % s2_ln,
            '~~~', '',
        ]
    elif name == 'F8-BT4-PARITY':
        corrections = [
            '', '````', '```text',
            'R52-CORRECTION SCORECARD.md:%d stale=78 recomputed=79' % s1_ln,
            'R52-CORRECTION census/round-51/preregistration.txt:%d stale=78 recomputed=79' % s2_ln,
            '````', '',
        ]
    elif name == 'F9-HTML-COMMENT':
        corrections = [
            '', '<!-- hidden filing block',
            'R52-CORRECTION SCORECARD.md:%d stale=78 recomputed=79' % s1_ln,
            'R52-CORRECTION census/round-51/preregistration.txt:%d stale=78 recomputed=79' % s2_ln,
            '-->', '',
        ]
    elif name == 'F10-STRADDLE':
        # suffix after the anchor: '` (78) recomputed below |' is 25 chars, so
        # 5 spaces land `->` at zone offset 30 and its digits at 32-33 — the
        # token starts inside the 32-char zone and ends beyond it. v2 reads
        # only the truncated zone and stays green; v3 refuses the straddle.
        sc_tip[4] = '| C1 | command `%s` (78) recomputed below |     → 79' % ANCHOR
    elif name == 'F11-BOGUS-RECOMP':
        # The routed r53 R3 shape: the site ALREADY reads the recomputed value
        # (nothing left to correct) and the correction claims a bogus
        # recomputed=83. v2 counts the site matched and unfiled=0 -> exit 0
        # silently; v3 refuses with BOGUS-RECOMPUTED. S2 stays genuinely
        # stale with its honest filing.
        sc_tip[4] = '| C1 | command `%s` (79) recomputed below |' % ANCHOR
        corrections = [
            '',
            'R52-CORRECTION SCORECARD.md:%d stale=79 recomputed=83' % s1_ln,
            'R52-CORRECTION census/round-51/preregistration.txt:%d stale=78 recomputed=79' % s2_ln,
            '',
        ]
    elif name == 'F12-LOG-UNFILED':
        registry_tip = REGISTRY_3ROWS
        log_tip = [
            '# fixture log (round-54 C1 matrix, %s)' % name,
            '- the r52 note said corpus/SOURCES.md 274 -> 275 rows.',
            '',
        ]
    elif name == 'F12b-LOG-FILED':
        registry_tip = REGISTRY_3ROWS
        log_tip = [
            '# fixture log (round-54 C1 matrix, %s)' % name,
            '- the r52 note said corpus/SOURCES.md 3 -> 4 rows.',
            '',
        ]
        pair_filing = 'R53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3'
        sources_revs = 'SELF'  # resolved to (tip, tip) by build_one
    else:
        raise SystemExit('unknown C1 fixture %s' % name)

    if corrections is not None:
        sc_tip = sc_tip + corrections
    if pair_filing is not None:
        sc_tip = sc_tip + ['', pair_filing, '']
    sc_tip.append('')
    return record_base, record_tip, sc_lines_base, sc_tip, pre_lines_base, pre_tip, log_tip, registry_tip, sources_revs


def build_one(name: str, workdir: Path):
    if name in C1_FIXTURES:
        (record_base, record_tip, sc_base, sc_tip, pre_base, pre_tip,
         log_tip, registry_tip, sources_revs) = build_c1(name, workdir)
        d = init_repo(workdir, name)
        write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', record_base)
        write(d / 'SCORECARD.md', '\n'.join(sc_base) + '\n')
        write(d / 'census/round-51/preregistration.txt', '\n'.join(pre_base) + '\n')
        base = commit_all(d, 'fixture base', T0)
        write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', record_tip)
        write(d / 'SCORECARD.md', '\n'.join(sc_tip) + '\n')
        write(d / 'census/round-51/preregistration.txt', '\n'.join(pre_tip) + '\n')
        if log_tip is not None:
            write(d / 'LOG.md', '\n'.join(log_tip))
        if registry_tip is not None:
            write(d / 'corpus/SOURCES.md', registry_tip)
        tip = commit_all(d, 'fixture tip', T1)
        srevs = (tip, tip) if sources_revs == 'SELF' else None
        return {'name': name, 'dir': str(d), 'base': base, 'tip': tip,
                'record_sha256': sha256(record_base.encode()),
                'sources_revs': srevs, 'kind': 'C1'}
    if name in C2_FIXTURES:
        stub = STUB_TOOL.encode()
        tool_sha = sha256(stub)
        rows = [
            ('a.txt', 'file', 'yes', 'no', 'tracked', 'none'),
            ('b.md', 'file', 'yes', 'no', 'tracked', 'none'),
            ('zz', 'dir', 'no', 'yes', 'ignored', 'none'),
        ]
        counts = {'tracked': 2, 'ignored': 1, 'untracked-stray': 0, 'symlink': 0}
        entries = 3
        hidden = None
        capture_rows = list(rows)
        if name == 'FH2-SYMLINK-HONEST':
            capture_rows = sorted(capture_rows + [('lnk', 'symlink', 'no', 'no', 'symlink', 'none')],
                                  key=lambda r: r[0].encode())
            counts['symlink'] = 1
            entries = 4
        if name == 'FA1-UNSORTED':
            capture_rows = list(reversed(capture_rows))
        if name == 'FA2-COMMENT':
            hidden = ('#odd', 'file', 'no', 'no', 'untracked-stray', 'report-only')
            capture_rows = sorted(capture_rows + [hidden], key=lambda r: r[0].encode())
            counts['untracked-stray'] = 0  # struck from the declared counts
            entries = 3
        if name == 'FA4-SPACE-NAME':
            hidden = ('#odd name', 'file', 'no', 'no', 'untracked-stray', 'report-only')
            capture_rows = sorted(capture_rows + [hidden], key=lambda r: r[0].encode())
            counts['untracked-stray'] = 0
            entries = 3
        if name == 'FA3-TAMPER':
            capture_rows = [('ax.txt',) + tuple(r[1:]) if r[0] == 'a.txt' else r
                            for r in capture_rows]
        if name == 'FA8-SYMLINK-CLASS':
            capture_rows = sorted(capture_rows + [('lnk', 'symlink', 'no', 'no', 'tracked', 'none')],
                                  key=lambda r: r[0].encode())
            counts['tracked'] = 3  # the wrong class is declared consistently
            counts['symlink'] = 0
            entries = 4
        body_rows = []
        for r in capture_rows:
            if hidden is not None and r[0] == hidden[0]:
                body_rows.append('#%s\t%s\t%s\t%s\t%s\t%s' % r)  # raw emission, no escaping
                continue
            body_rows.append('%s\t%s\t%s\t%s\t%s\t%s' % r)
        def render(rows_, crlf=False):
            cap = '\n'.join(
                ['# fixture fleet-root census (round-54 C2 matrix, %s)' % name,
                 '# SCOPE=top-level entries, dotfiles included, .git excluded',
                 '# TOOL_SHA256=%s' % tool_sha,
                 '# FLEET_HEAD=%s' % FLEET_HEAD,
                 '# ENTRIES=%d' % entries,
                 '# COUNT tracked=%d' % counts['tracked'],
                 '# COUNT ignored=%d' % counts['ignored'],
                 '# COUNT untracked-stray=%d' % counts['untracked-stray'],
                 '# COUNT symlink=%d' % counts['symlink'],
                 'name\tkind\ttracked\tignored\tclass\tdisposition']
                + rows_) + '\n'
            return cap.replace('\n', '\r\n') if crlf else cap
        capture = render(body_rows, crlf=(name == 'FA6-CRLF'))
        receipt_entries = '4' if name == 'FA7-RECEIPT-ENTRIES' else str(entries)
        # The receipt always binds the ORIGINAL (untampered) capture bytes so
        # FA3-TAMPER demonstrates the byte flip; other fixtures' receipts bind
        # their own capture bytes.
        receipt_capture = capture
        if name == 'FA3-TAMPER':
            rows_o = [('a.txt',) + tuple(r[1:]) if r[0] == 'ax.txt' else r
                      for r in capture_rows]
            receipt_rows = ['%s\t%s\t%s\t%s\t%s\t%s' % r for r in rows_o]
            receipt_capture = render(receipt_rows)
        receipt_lines = [
            '# fixture run receipt (machine-readable block, RECEIPT_VERSION=1)',
            '# RECEIPT_VERSION=1',
            '# TOOL_SHA256=%s' % tool_sha,
            '# FLEET_HEAD=%s' % FLEET_HEAD,
            '# CAPTURE_SHA256=%s' % sha256(receipt_capture.encode()),
            '# ENTRIES=%s' % receipt_entries,
        ]
        if name == 'FA5-EXTRA-KEY':
            receipt_lines.insert(2, '# GENERATOR=fixture-builder')
        receipt_lines += [
            'command: fixture census run (synthetic); no live root was read',
            '']
        receipt = '\n'.join(receipt_lines)
        d = init_repo(workdir, name)
        write(d / 'census/round-52/records/fleet-root-census.tsv', capture)
        write(d / 'census/round-53/records/fleet-root-census-run.txt', receipt)
        write(d / 'tools/souji-fleet-root-census.py', stub)
        base = commit_all(d, 'fixture base', T0)
        tip = base  # single-commit fixtures; the counter reads --rev = tip
        return {'name': name, 'dir': str(d), 'base': base, 'tip': tip,
                'record_sha256': '-', 'sources_revs': None, 'kind': 'C2'}
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
