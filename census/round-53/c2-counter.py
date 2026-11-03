#!/usr/bin/env python3
"""C2 counter v2 (souji round 53): committed census capture verifies, amended.

Frozen predicate: census/round-53/preregistration.txt, claim C2. A NEW frozen
version of census/round-52/c2-counter.py (whose bytes are never edited); the
capture, tool and run-receipt paths are explicit arguments, defaulting to
none — the prereg pins the real paths. The three named r52 limits become
three checks (finding-id -> the r52 limit closed):

  ROWS-UNSORTED           data rows must appear in ascending byte order of name
  COMMENT-AMBIGUOUS-NAME  a comment line shaped like a 6-field data row (the
                          `#`-leading-name emission) is refused: the grammar
                          defines no escaping for a `#`-leading name, so the
                          capture cannot carry one — it is refused, fail-closed
  CAPTURE-RECEIPT-MISMATCH / RECEIPT-MALFORMED
                          a capture verifies only against its RECEIPT_VERSION=1
                          run receipt: TOOL_SHA256, FLEET_HEAD, ENTRIES must
                          agree with the capture header, and CAPTURE_SHA256
                          must equal sha256 of the capture's committed bytes

All r52 checks carry over: header grammar (TOOL_SHA256 == sha256 of the tool
bytes at --rev, FLEET_HEAD 40-hex, ENTRIES == row count >= 1, one COUNT line
per class matching the recount), row grammar (6 tab-separated fields, unique
name without '/', name != '.git', frozen enumerations, frozen class rule,
disposition 'report-only' only for untracked-stray), removal_proposed == 0.

Exit 0: every check holds. Exit 1: any finding (including capture absent:
PRISTINE FAIL). Exit 2: could-not-evaluate (bad CLI, bad revision, tool
absent at rev). Reads committed bytes only; writes nothing outside --work
(selftest only); no network; every git call runs with a scrubbed environment
and fsmonitor/hooks neutralized.

Selftest: --selftest --work DIR [--expected TSV] builds the synthetic fixture
repos (fixtures/build-fixtures.py), runs every C2 fixture with the fixture's
capture/receipt paths, and asserts exit code + finding-id against the
committed expected file (records/c2-selftest-expected.tsv by default).
"""
import argparse
import hashlib
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEADER = ['name', 'kind', 'tracked', 'ignored', 'class', 'disposition']
KINDS = {'file', 'dir', 'symlink', 'other'}
CLASSES = ['tracked', 'ignored', 'untracked-stray', 'symlink']
HEX64 = re.compile(r'[0-9a-f]{64}')
HEX40 = re.compile(r'[0-9a-f]{40}')
RECEIPT_KEYS = ['RECEIPT_VERSION', 'TOOL_SHA256', 'FLEET_HEAD', 'CAPTURE_SHA256', 'ENTRIES']
DATA_LIKE_COMMENT = re.compile(r'^#\S*(\t\S+){5}$')
DEFAULT_EXPECTED = HERE / 'records' / 'c2-selftest-expected.tsv'
BUILDER = HERE / 'fixtures' / 'build-fixtures.py'


def git_env():
    return {
        'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
        'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
        'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
        'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1',
        'GIT_TERMINAL_PROMPT': '0',
    }


def git(root, *args):
    p = subprocess.run(['git', '-C', str(root),
                        '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null']
                       + list(args), capture_output=True, env=git_env(), timeout=120)
    return p


def git_show_bytes(root, rev, path):
    p = git(root, 'show', '%s:%s' % (rev, path))
    return p.stdout if p.returncode == 0 else None


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frozen_class(kind, tracked, ignored):
    if kind == 'symlink':
        return 'symlink'
    if tracked == 'yes':
        return 'tracked'
    if ignored == 'yes':
        return 'ignored'
    return 'untracked-stray'


def measure(root, rev, capture_path, receipt_path, out):
    findings = []

    def finding(fid, detail):
        findings.append(fid)
        out.append('FINDING %s %s' % (fid, detail))

    if not re.fullmatch(r'[0-9a-f]{40}', rev):
        out.append('CANNOT-EVALUATE full 40-hex revision required')
        return 2
    cap = git_show_bytes(root, rev, capture_path)
    if cap is None:
        out.append('PRISTINE FAIL FLEET-CENSUS-ABSENT %s:%s' % (rev[:12], capture_path))
        return 1
    tool = git_show_bytes(root, rev, 'tools/souji-fleet-root-census.py')
    if tool is None:
        out.append('CANNOT-EVALUATE tool absent at rev: tools/souji-fleet-root-census.py')
        return 2
    tool_sha = sha256(tool)
    receipt = git_show_bytes(root, rev, receipt_path)
    if receipt is None:
        finding('RECEIPT-MALFORMED', 'receipt absent at %s: %s' % (rev[:12], receipt_path))
        receipt = b''

    problems_pre = []
    lines = cap.decode('utf-8', 'replace').split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    header_kv, counts_decl, rows, body_header_seen = {}, {}, [], False
    for ln in lines:
        if ln.startswith('#'):
            if DATA_LIKE_COMMENT.fullmatch(ln):
                finding('COMMENT-AMBIGUOUS-NAME', 'comment shaped like a data row: %r'
                        % ln[:60])
                continue
            m = re.fullmatch(r'# (TOOL_SHA256|FLEET_HEAD|ENTRIES)=(\S+)', ln)
            if m:
                if m.group(1) in header_kv:
                    problems_pre.append('duplicate header %s' % m.group(1))
                header_kv[m.group(1)] = m.group(2)
                continue
            m = re.fullmatch(r'# COUNT (\S+)=(\d+)', ln)
            if m:
                if m.group(1) in counts_decl:
                    problems_pre.append('duplicate COUNT %s' % m.group(1))
                counts_decl[m.group(1)] = int(m.group(2))
                continue
            continue  # free-form scope comment
        if not body_header_seen:
            if ln.split('\t') != HEADER:
                problems_pre.append('column header mismatch')
            body_header_seen = True
            continue
        f = ln.split('\t')
        if len(f) != 6:
            problems_pre.append('row field count %d: %r' % (len(f), ln[:60]))
            continue
        rows.append(f)

    names, class_mismatch, unclassified, removal_proposed = set(), 0, 0, 0
    recount = {c: 0 for c in CLASSES}
    prev = None
    unsorted = False
    for f in rows:
        name, kind, tracked, ignored, cls, disp = f
        if prev is not None and name.encode() < prev:
            unsorted = True
        prev = name.encode()
        if (not name or name != name.strip() or '/' in name or name == '.git'
                or name in names or name.startswith('#')):
            problems_pre.append('bad or duplicate name %r' % name)
            unclassified += 1
            continue
        names.add(name)
        if kind not in KINDS or tracked not in ('yes', 'no') or ignored not in ('yes', 'no'):
            problems_pre.append('enumeration violation for %r' % name)
            unclassified += 1
            continue
        want = frozen_class(kind, tracked, ignored)
        if cls not in CLASSES:
            unclassified += 1
        if cls != want:
            class_mismatch += 1
            problems_pre.append('class %r want %r for %r' % (cls, want, name))
        want_disp = 'report-only' if want == 'untracked-stray' else 'none'
        if disp != want_disp:
            removal_proposed += 1
            problems_pre.append('disposition %r for %r' % (disp, name))
        if cls in recount:
            recount[cls] += 1
    if unsorted:
        finding('ROWS-UNSORTED', 'data rows are not in ascending byte order of name')

    for k in ('TOOL_SHA256', 'FLEET_HEAD', 'ENTRIES'):
        if k not in header_kv:
            problems_pre.append('missing header %s' % k)
    tool_ok = header_kv.get('TOOL_SHA256') == tool_sha
    if not tool_ok:
        problems_pre.append('TOOL_SHA256 %s != tool bytes %s'
                            % (header_kv.get('TOOL_SHA256'), tool_sha))
    if not HEX40.fullmatch(header_kv.get('FLEET_HEAD', '')):
        problems_pre.append('FLEET_HEAD not 40-hex')
    if not HEX64.fullmatch(header_kv.get('TOOL_SHA256', '')):
        problems_pre.append('TOOL_SHA256 not 64-hex')
    entries = len(rows)
    if 'ENTRIES' in header_kv and header_kv['ENTRIES'] != str(entries):
        problems_pre.append('ENTRIES %s != rows %d' % (header_kv['ENTRIES'], entries))
    if entries < 1:
        problems_pre.append('ENTRIES < 1 (empty capture is not a census)')
    for c in CLASSES:
        if counts_decl.get(c) != recount[c]:
            problems_pre.append('COUNT %s declared %s recomputed %d'
                                % (c, counts_decl.get(c), recount[c]))
    if set(counts_decl) != set(CLASSES):
        problems_pre.append('COUNT class set %s != %s' % (sorted(counts_decl), sorted(CLASSES)))

    # Receipt binding (RECEIPT_VERSION=1).
    recv, malformed = {}, False
    for ln in receipt.decode('utf-8', 'replace').splitlines():
        m = re.fullmatch(r'# (RECEIPT_VERSION|TOOL_SHA256|FLEET_HEAD|CAPTURE_SHA256|ENTRIES)=(\S+)', ln)
        if m:
            if m.group(1) in recv:
                malformed = True
            recv[m.group(1)] = m.group(2)
    if sorted(recv) != sorted(RECEIPT_KEYS):
        malformed = True
    elif recv.get('RECEIPT_VERSION') != '1':
        malformed = True
    elif not HEX64.fullmatch(recv.get('TOOL_SHA256', '')) or not HEX64.fullmatch(recv.get('CAPTURE_SHA256', '')):
        malformed = True
    elif not HEX40.fullmatch(recv.get('FLEET_HEAD', '')) or not recv.get('ENTRIES', '').isdigit():
        malformed = True
    receipt_ok = True
    if malformed:
        finding('RECEIPT-MALFORMED', 'receipt %s does not carry the RECEIPT_VERSION=1 grammar'
                % receipt_path)
        receipt_ok = False
    else:
        if recv['TOOL_SHA256'] != tool_sha or recv['TOOL_SHA256'] != header_kv.get('TOOL_SHA256'):
            finding('CAPTURE-RECEIPT-MISMATCH', 'TOOL_SHA256 receipt=%s tool=%s capture=%s'
                    % (recv['TOOL_SHA256'][:12], tool_sha[:12], header_kv.get('TOOL_SHA256', '-')[:12]))
            receipt_ok = False
        cap_sha = sha256(cap)
        if recv['CAPTURE_SHA256'] != cap_sha:
            finding('CAPTURE-RECEIPT-MISMATCH', 'CAPTURE_SHA256 receipt=%s observed=%s'
                    % (recv['CAPTURE_SHA256'][:12], cap_sha[:12]))
            receipt_ok = False
        if recv['FLEET_HEAD'] != header_kv.get('FLEET_HEAD'):
            finding('CAPTURE-RECEIPT-MISMATCH', 'FLEET_HEAD receipt=%s capture=%s'
                    % (recv['FLEET_HEAD'][:12], header_kv.get('FLEET_HEAD', '-')))
            receipt_ok = False
        if recv['ENTRIES'] != header_kv.get('ENTRIES') or recv['ENTRIES'] != str(entries):
            finding('CAPTURE-RECEIPT-MISMATCH', 'ENTRIES receipt=%s capture=%s rows=%d'
                    % (recv['ENTRIES'], header_kv.get('ENTRIES', '-'), entries))
            receipt_ok = False

    for p in problems_pre[:20]:
        out.append('FINDING %s' % p)
    ok = (not findings) and (not problems_pre)
    out.append('SUMMARY entries=%d rows=%d unclassified=%d class_mismatch=%d counts=%s tool_sha=%s '
               'removal_proposed=%d receipt=%s sorted=%s rev=%s'
               % (entries, len(rows), unclassified, class_mismatch,
                  'ok' if all(counts_decl.get(c) == recount[c] for c in CLASSES) and set(counts_decl) == set(CLASSES) else 'FAIL',
                  'ok' if tool_ok else 'FAIL', removal_proposed,
                  'ok' if receipt_ok else 'FAIL',
                  'ok' if not unsorted else 'FAIL', rev[:12]))
    return 0 if ok else 1


def run_selftest(work: Path, expected_path: Path, out):
    if not BUILDER.exists():
        out.append('CANNOT-EVALUATE builder missing: %s' % BUILDER)
        return 2
    spec = importlib.util.spec_from_file_location('r53fixtures', BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fdir = work / 'c2-fixtures'
    fdir.mkdir(parents=True, exist_ok=True)
    exp = {}
    for row in expected_path.read_text().splitlines()[1:]:
        if not row.strip():
            continue
        f = row.split('\t')
        exp[f[0]] = (int(f[1]), f[2] if len(f) > 2 else '')
    ok = True
    for name in mod.C2_FIXTURES:
        info = mod.build_one(name, fdir)
        buf = []
        rc = measure(Path(info['dir']), info['tip'],
                     'census/round-52/records/fleet-root-census.tsv',
                     'census/round-53/records/fleet-root-census-run.txt', buf)
        want_rc, want_find = exp.get(name, (None, ''))
        got_find = next((ln.split(' ')[1] for ln in buf if ln.startswith('FINDING ')), '')
        passed = (rc == want_rc) and (want_find in ('', '-') or got_find == want_find)
        ok = ok and passed
        out.append('SELFTEST-CASE %s %s rc=%d want_rc=%s finding=%s want_finding=%s'
                   % (name, 'pass' if passed else 'fail', rc, want_rc, got_find or '-', want_find or '-'))
    out.append('SELFTEST %s cases=%d' % ('pass' if ok else 'fail', len(mod.C2_FIXTURES)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root')
    ap.add_argument('--rev')
    ap.add_argument('--capture', default=None)
    ap.add_argument('--receipt', default=None)
    ap.add_argument('--scratch', default=None, help='accepted; nothing is written outside --work')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--work', default=None)
    ap.add_argument('--expected', default=None)
    ns = ap.parse_args()
    out = []
    if ns.selftest:
        if not ns.work:
            print('CANNOT-EVALUATE --selftest requires --work', file=sys.stderr)
            return 2
        exp = Path(ns.expected) if ns.expected else DEFAULT_EXPECTED
        rc = run_selftest(Path(ns.work), exp, out)
    else:
        missing = [a for a, v in (('--root', ns.root), ('--rev', ns.rev),
                                  ('--capture', ns.capture), ('--receipt', ns.receipt)) if not v]
        if missing:
            print('CANNOT-EVALUATE missing required args: %s' % ', '.join(missing), file=sys.stderr)
            return 2
        rc = measure(Path(ns.root).resolve(), ns.rev, ns.capture, ns.receipt, out)
    print('\n'.join(out))
    return rc


if __name__ == '__main__':
    sys.exit(main())
