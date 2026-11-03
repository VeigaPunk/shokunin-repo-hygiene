#!/usr/bin/env python3
"""C2 counter v5 (souji round 56): committed census capture verifies, amended.

Frozen predicate: census/round-56/preregistration.txt, claim C2. A NEW frozen
version of census/round-55/c2-counter.py (whose bytes are never edited); the
capture, tool and run-receipt paths are explicit arguments, defaulting to
none — the prereg pins the real paths and the tool digest pin.

v5 instruments the r55 routed receipt-grammar surfaces (corpus/lessons/
round-55.md ## Routed to r56 items 1 and 9, sentinel S55-S5):

  RECEIPT-UNKNOWN-KEY first character (RD-A repair) the receipt key class
                  is [A-Za-z0-9_] again — v3 refused keys beginning with a
                  digit or an underscore (`1KEY=x`, `_KEY=x`, `2=x`) and the
                  v4 narrowing ([A-Za-z]) let them pass silently (reviewer02
                  receipt-key-differential receipt). Case tolerance and the
                  no-space shape are unchanged.
  EMPTY-VALUE KEY (S55-S5) an unknown receipt key with an EMPTY value
                  (`# BUILDHOST=`) is refused; v4's value group required a
                  non-empty run of non-space characters so the line was
                  ignored silently. A KNOWN key with an
                  empty value still fails the grammar/comparison checks
                  (unchanged refusal path).
  SELFTEST-ROW-MISMATCH (mutation01 C2-17/C2-18) the selftest asserts that
                  every row of the expected TSV ran: deleting a fixture arm
                  from the run list no longer prints a passing `SELFTEST
                  pass cases=14`; the missing expected row fails the selftest
                  by name.

Every v4 check carries over (header grammar, tool-bytes digest, enumerations,
frozen class rule, disposition rule, COUNT recount, ENTRIES >= 1, ROWS-UNSORTED,
COMMENT-AMBIGUOUS-NAME, RECEIPT_VERSION=1 binding, CAPTURE-CRLF /
RECEIPT-CRLF, TOOL-SHA-ARG-MISMATCH). v4 instruments the r54 routed surfaces
(reviewer02 NL-1/NL-3/NL-4/NL-5, mutation01 M11, the r54 spot-check §5.2
unnamed-kill-row defect — corpus/lessons/round-54.md ## Named limits):

  COMMENT-AMBIGUOUS-NAME (widened, NL-1)  any `#`-leading capture line that
                          carries a TAB is refused as data-shaped, so a
                          `#`-leading row with four (or any number of) tabs
                          can no longer be silently dropped; v3's tab-count
                          rule only fired at five or more tabs and the field
                          count never saw `#`-leading lines at all. The
                          v3 DATA_LIKE_COMMENT fullmatch is removed: every
                          tab-bearing comment is already caught by the tab
                          rule, and the predicate was dead under v3 (subsumed
                          by the >=5-tab test)
  RECEIPT-UNKNOWN-KEY (widened, NL-3/NL-4) the receipt grammar now parses
                          `#KEY=VALUE`, `#  KEY=VALUE` and lowercase keys:
                          a known key in any of those shapes is recognized
                          (and validated), an unknown key in any of them is
                          refused; v3 anchored exactly `# ` + uppercase
  TOOL-SHA-ARG-MALFORMED (NL-5)   a `--tool-sha256` argument that is not
                          lowercase 64-hex is refused by name (still exit 2
                          could-not-evaluate); v3 printed a generic
                          `--tool-sha256 must be 64-hex`
  FA9-WRONG-TOOL-PIN (M11)        the selftest carries an arm that passes a
                          wrong digest for the honest fixture and asserts
                          TOOL-SHA-ARG-MISMATCH, rc 1 — the v3 selftest
                          passed None for the pin, so the branch had no
                          committed demonstration
  FB4-PIN-SHAPE                   a selftest arm that passes an uppercase
                          digest and asserts the named TOOL-SHA-ARG-MALFORMED
                          refusal, rc 2
  CLASS-MISMATCH (unnamed-kill-row fix)   the class branch's finding now
                          carries a named id, so a counted kill row (the r54
                          verifier §5.2 FA8 finding `-`) names its finding

The builder that produces the selftest fixtures keeps the r53/r54
hardening (per-call git flags, subprocess timeout, pinned
GIT_AUTHOR_DATE/GIT_COMMITTER_DATE for rev-deterministic fixtures), and the
selftest verifies optional --builder-sha256/--expected-sha256 pins BEFORE
exec. --scratch is an alias of --work (the r54 sentinel S6 routed fix).

Named limits (disclosed, not fixed): unknown `# KEY=VALUE` lines in the
CAPTURE header are still ignored (the routed items name the receipt only);
free-form comments without tabs are still accepted (NL-2 stays: the rule
cannot read intent); ENTRIES remains the tool's own count; the receipt binds
capture↔receipt consistency, not execution; FLEET_HEAD remains
format-checked, not resolved; the receipt binds bytes, not the capture's
path; only the FIRST unknown receipt key is reported.

Exit 0: every check holds. Exit 1: any finding (including capture absent:
PRISTINE FAIL). Exit 2: could-not-evaluate (bad CLI, bad revision, tool
absent at rev, pin malformed). Reads committed bytes only; writes nothing
outside --work (selftest only); no network; every git call runs with a
scrubbed environment and fsmonitor/hooks neutralized.

Selftest: --selftest --work DIR [--expected TSV] [--builder-sha256 HEX]
[--expected-sha256 HEX] builds the synthetic fixture repos
(fixtures/build-fixtures.py), runs every C2 fixture with the fixture's
capture/receipt paths plus the FA9/FB4 selftest arms, and asserts exit code +
finding-id against the committed expected file
(records/c2-selftest-expected.tsv by default).
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
# v5 (RD-A repair): the key's first character is [A-Za-z0-9_] again — v3
# refused digit/underscore-initial keys and the v4 narrowing ([A-Za-z]) let
# them pass. The value group is \S* (may be empty): an unknown key with an
# empty value is refused (v4 ignored it; sentinel S55-S5).
RECEIPT_KV = re.compile(r'\s*#\s*([A-Za-z0-9_][A-Za-z0-9_]*)\s*=\s*(\S*)\s*')
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


def measure(root, rev, capture_path, receipt_path, tool_sha_pin, out):
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
    if tool_sha_pin is not None:
        if not re.fullmatch(r'[0-9a-f]{64}', tool_sha_pin):
            out.append('CANNOT-EVALUATE TOOL-SHA-ARG-MALFORMED --tool-sha256 must be lowercase 64-hex')
            return 2
        if tool_sha_pin != tool_sha:
            finding('TOOL-SHA-ARG-MISMATCH', 'pinned=%s observed=%s'
                    % (tool_sha_pin[:12], tool_sha[:12]))
    receipt = git_show_bytes(root, rev, receipt_path)
    if receipt is None:
        finding('RECEIPT-MALFORMED', 'receipt absent at %s: %s' % (rev[:12], receipt_path))
        receipt = b''
    if b'\r' in cap:
        finding('CAPTURE-CRLF', 'capture bytes carry CR (carriage return)')
    if b'\r' in receipt:
        finding('RECEIPT-CRLF', 'receipt bytes carry CR (carriage return)')

    problems_pre = []
    lines = cap.decode('utf-8', 'replace').split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    header_kv, counts_decl, rows, body_header_seen = {}, {}, [], False
    for ln in lines:
        if ln.startswith('#'):
            if '\t' in ln:
                finding('COMMENT-AMBIGUOUS-NAME', 'comment shaped like a data row (carries tabs): %r'
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
            problems_pre.append('CLASS-MISMATCH class %r want %r for %r' % (cls, want, name))
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

    # Receipt binding (RECEIPT_VERSION=1). Grammar tolerant of key case and
    # of missing/extra whitespace around the key (r54 reviewer02 NL-3/NL-4).
    recv, malformed, unknown_key = {}, False, None
    for ln in receipt.decode('utf-8', 'replace').split('\n'):
        kv = RECEIPT_KV.fullmatch(ln)
        if kv:
            key = kv.group(1).upper()
            if key in RECEIPT_KEYS:
                if key in recv:
                    malformed = True
                recv[key] = kv.group(2)
                continue
            if unknown_key is None:
                unknown_key = kv.group(1)
    if unknown_key is not None:
        finding('RECEIPT-UNKNOWN-KEY', 'receipt carries unknown key %s' % unknown_key)
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
               'removal_proposed=%d receipt=%s sorted=%s tool_pin=%s rev=%s'
               % (entries, len(rows), unclassified, class_mismatch,
                  'ok' if all(counts_decl.get(c) == recount[c] for c in CLASSES) and set(counts_decl) == set(CLASSES) else 'FAIL',
                  'ok' if tool_ok else 'FAIL', removal_proposed,
                  'ok' if receipt_ok else 'FAIL',
                  'ok' if not unsorted else 'FAIL',
                  'n/a' if tool_sha_pin is None else ('ok' if tool_sha_pin == tool_sha else 'FAIL'),
                  rev[:12]))
    return 0 if ok else 1


def load_builder():
    if not BUILDER.exists():
        return None
    spec = importlib.util.spec_from_file_location('r54fixtures', BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_selftest(work: Path, expected_path: Path, out, builder_sha=None, expected_sha=None):
    if builder_sha is not None and sha256(BUILDER.read_bytes()) != builder_sha:
        out.append('CANNOT-EVALUATE PIN-MISMATCH builder sha256 %s != pinned %s'
                   % (sha256(BUILDER.read_bytes()), builder_sha))
        return 2
    if expected_sha is not None and sha256(expected_path.read_bytes()) != expected_sha:
        out.append('CANNOT-EVALUATE PIN-MISMATCH expected sha256 %s != pinned %s'
                   % (sha256(expected_path.read_bytes()), expected_sha))
        return 2
    mod = load_builder()
    if mod is None:
        out.append('CANNOT-EVALUATE builder missing: %s' % BUILDER)
        return 2
    fdir = work / 'c2-fixtures'
    fdir.mkdir(parents=True, exist_ok=True)
    exp = {}
    for row in expected_path.read_text().splitlines()[1:]:
        if not row.strip():
            continue
        f = row.split('\t')
        exp[f[0]] = (int(f[1]), f[2] if len(f) > 2 else '')
    names = [n for n in list(mod.C2_FIXTURES) if n != 'FC1-UNDERSCORE-KEY'] + ['FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE']
    ok = True
    for name in names:
        buf = []
        if name in ('FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE'):
            # M11/NL-5 routed arms: the pin branches, exercised from the selftest.
            info = mod.build_one('FH-HONEST', fdir)
            pin = '0' * 64 if name == 'FA9-WRONG-TOOL-PIN' else 'A' * 64
            rc = measure(Path(info['dir']), info['tip'],
                         'census/round-52/records/fleet-root-census.tsv',
                         'census/round-53/records/fleet-root-census-run.txt', pin, buf)
            if name == 'FB4-PIN-SHAPE':
                got_find = 'TOOL-SHA-ARG-MALFORMED' if any(
                    ln.startswith('CANNOT-EVALUATE TOOL-SHA-ARG-MALFORMED') for ln in buf) else '-'
            else:
                got_find = next((ln.split(' ')[1] for ln in buf if ln.startswith('FINDING ')), '-')
        else:
            info = mod.build_one(name, fdir)
            rc = measure(Path(info['dir']), info['tip'],
                         'census/round-52/records/fleet-root-census.tsv',
                         'census/round-53/records/fleet-root-census-run.txt', None, buf)
            got_find = next((ln.split(' ')[1] for ln in buf if ln.startswith('FINDING ')), '-')
        want_rc, want_find = exp.get(name, (None, ''))
        passed = (rc == want_rc) and (want_find in ('', '-') or got_find == want_find)
        ok = ok and passed
        out.append('SELFTEST-CASE %s %s rc=%d want_rc=%s finding=%s want_finding=%s'
                   % (name, 'pass' if passed else 'fail', rc, want_rc, got_find or '-', want_find or '-'))
    # v5 (mutation01 C2-17/C2-18): every expected row must have RUN. Deleting
    # an arm from the run list used to print a passing `SELFTEST pass
    # cases=14`; the missing expected row now fails the selftest by name.
    for r in sorted(exp):
        if r not in names:
            ok = False
            out.append('SELFTEST-ROW-MISMATCH expected row did not run: %s' % r)
    for n in names:
        if n not in exp:
            ok = False
            out.append('SELFTEST-ROW-MISMATCH ran without an expected row: %s' % n)
    out.append('SELFTEST %s cases=%d' % ('pass' if ok else 'fail', len(names)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root')
    ap.add_argument('--rev')
    ap.add_argument('--capture', default=None)
    ap.add_argument('--receipt', default=None)
    ap.add_argument('--tool-sha256', dest='tool_sha', default=None)
    ap.add_argument('--scratch', default=None,
                    help='alias of --work (r54 sentinel S6 routed fix: the argument steers writes)')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--work', default=None)
    ap.add_argument('--expected', default=None)
    ap.add_argument('--builder-sha256', dest='builder_sha', default=None)
    ap.add_argument('--expected-sha256', dest='expected_sha', default=None)
    ns = ap.parse_args()
    out = []
    if ns.selftest:
        work = ns.work or ns.scratch
        if not work:
            print('CANNOT-EVALUATE --selftest requires --work (or --scratch)', file=sys.stderr)
            return 2
        exp = Path(ns.expected) if ns.expected else DEFAULT_EXPECTED
        rc = run_selftest(Path(work), exp, out, ns.builder_sha, ns.expected_sha)
    else:
        missing = [a for a, v in (('--root', ns.root), ('--rev', ns.rev),
                                  ('--capture', ns.capture), ('--receipt', ns.receipt)) if not v]
        if missing:
            print('CANNOT-EVALUATE missing required args: %s' % ', '.join(missing), file=sys.stderr)
            return 2
        rc = measure(Path(ns.root).resolve(), ns.rev, ns.capture, ns.receipt, ns.tool_sha, out)
    print('\n'.join(out))
    return rc


if __name__ == '__main__':
    sys.exit(main())
