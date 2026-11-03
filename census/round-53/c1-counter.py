#!/usr/bin/env python3
"""C1 counter v2 (souji round 53): declared-count annotation agreement, amended.

Frozen predicate: census/round-53/preregistration.txt, claim C1. This is a NEW
frozen version of census/round-52/c1-counter.py; the r52 counter's bytes are
never edited. The five named r52 limits become five checks (finding-id -> the
r52 limit they close):

  MULTIPLE-ANNOTATIONS   first-annotation reading (a planted annotation before
                         the stale one is no longer silently accepted)
  RECORD-SHA-MISMATCH    the recompute source is pinned by sha256 (--record-sha256)
  INERT-CORRECTION       a correction naming a line that no longer reads its
                         stale value (or naming a non-site path) kills
  CORRECTION-IN-FENCE    a correction line inside a fenced code block neither
                         files nor passes
  DELETED-LINES          the append-only check: zero deleted lines across the
                         record, the two sites and the correction file
                         between --base and --rev

Unchanged from v1: the enumerated site list (S1 SCORECARD.md, S2
census/round-51/preregistration.txt), the anchor, the record path, the filing
grammar `R52-CORRECTION <path>:<line> stale=<N> recomputed=<M>` in SCORECARD.md.
The annotation zone is the first ZONE=32 characters after the anchor (frozen;
the real S1 line's later `(1)` sits outside it; the planted r52 attack lands
inside it).

Exit 0: unfiled == 0 and no finding.
Exit 1: any finding or any unfiled mismatch (kill rule).
Exit 2: could-not-evaluate (bad CLI, missing file, zero or duplicate anchor,
        zero annotations in the zone).
Reads committed bytes only (git show / git diff --numstat) with a scrubbed
environment and fsmonitor/hooks neutralized; writes nothing outside --work
(selftest only). No network.

Selftest: --selftest --work DIR [--expected TSV] builds the synthetic fixture
repos (fixtures/build-fixtures.py, same directory), runs every C1 fixture,
and asserts exit code + finding-id against the committed expected file
(records/c1-selftest-expected.tsv by default).
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
ANCHOR = 'grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv'
RECORD = 'census/round-51/records/ws-drift-vs-r46.tsv'
SITES = ['SCORECARD.md', 'census/round-51/preregistration.txt']
CORR_FILE = 'SCORECARD.md'
ZONE = 32
CORR_RE = re.compile(r'^R52-CORRECTION (\S+):(\d+) stale=(\d+) recomputed=(\d+)\s*$', re.M)
ANNOT_RE = re.compile(r'(?:→|\()\s*(\d+)')
DEFAULT_EXPECTED = HERE / 'records' / 'c1-selftest-expected.tsv'
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
    e = git_env()
    p = subprocess.run(['git', '-C', str(root),
                        '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null']
                       + list(args), capture_output=True, env=e, timeout=120)
    return p


def git_show(root, rev, path):
    p = git(root, 'show', '%s:%s' % (rev, path))
    if p.returncode:
        return None
    return p.stdout


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fenced_lines(text: str):
    """1-based line numbers inside ``` fenced regions (delimiter lines excluded)."""
    fenced, inside = set(), False
    for i, ln in enumerate(text.splitlines(), 1):
        if ln.lstrip().startswith('```'):
            inside = not inside
            continue
        if inside:
            fenced.add(i)
    return fenced


def numstat_deletions(root, base, rev, paths):
    """[(path, deletions)] for the named paths between base and rev (int, or -1 binary)."""
    p = git(root, 'diff', '--numstat', '--no-renames', '%s..%s' % (base, rev), '--', *paths)
    if p.returncode:
        return None
    out = []
    for ln in p.stdout.decode('utf-8', 'replace').splitlines():
        f = ln.split('\t')
        if len(f) != 3:
            continue
        adds, dels, path = f
        out.append((path, -1 if dels == '-' else int(dels)))
    return out


def measure(root, rev, base, record_sha, out):
    """Run the amended measurement; return exit code. Findings print as FINDING lines."""
    findings = []
    fatal = []

    def finding(fid, detail):
        findings.append((fid, detail))
        out.append('FINDING %s %s' % (fid, detail))

    record = git_show(root, rev, RECORD)
    if record is None:
        out.append('CANNOT-EVALUATE record absent at %s: %s' % (rev[:12], RECORD))
        return 2
    record_sha_obs = sha256(record)
    record_sha_ok = record_sha_obs == record_sha
    if not record_sha_ok:
        finding('RECORD-SHA-MISMATCH', 'pinned=%s observed=%s' % (record_sha[:12], record_sha_obs[:12]))
    recomputed = sum(1 for ln in record.decode('utf-8', 'replace').splitlines() if ln.startswith('ADDED'))

    corr_b = git_show(root, rev, CORR_FILE)
    if corr_b is None:
        out.append('CANNOT-EVALUATE %s absent at rev' % CORR_FILE)
        return 2
    corr = corr_b.decode('utf-8', 'replace')
    corr_tuples = []
    for m in CORR_RE.finditer(corr):
        corr_line_no = corr.count('\n', 0, m.start()) + 1
        corr_tuples.append((m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), corr_line_no))
    fences = fenced_lines(corr)

    site_text, site_zone_stated, zone_multi = {}, {}, []
    for path in SITES:
        tb = git_show(root, rev, path)
        if tb is None:
            out.append('CANNOT-EVALUATE site absent: %s' % path)
            return 2
        text = tb.decode('utf-8', 'replace')
        site_text[path] = text
        lines = text.splitlines()
        hits = [i for i, ln in enumerate(lines) if ANCHOR in ln]
        if len(hits) != 1:
            out.append('CANNOT-EVALUATE anchor count %d in %s (want 1)' % (len(hits), path))
            return 2
        ln = lines[hits[0]]
        zone = ln[ln.index(ANCHOR) + len(ANCHOR):][:ZONE]
        matches = ANNOT_RE.findall(zone)
        if not matches:
            out.append('CANNOT-EVALUATE no annotation in zone at %s' % path)
            return 2
        if len(matches) > 1:
            finding('MULTIPLE-ANNOTATIONS', '%s line %d zone tokens %s'
                    % (path, hits[0] + 1, ','.join(matches)))
            zone_multi.append(path)
        site_zone_stated[path] = (hits[0] + 1, int(matches[0]))

    filed_paths = {t[0] for t in corr_tuples}
    inert = fenced = 0
    for (cpath, cline, stale, m_val, corr_no) in corr_tuples:
        bad = None
        if cpath not in SITES:
            bad = 'names non-site path %s' % cpath
        else:
            lines = site_text[cpath].splitlines()
            if cline < 1 or cline > len(lines):
                bad = 'line %d absent in %s' % (cline, cpath)
            else:
                ln = lines[cline - 1]
                if ANCHOR not in ln:
                    bad = 'line %d of %s carries no anchor' % (cline, cpath)
                else:
                    zone = ln[ln.index(ANCHOR) + len(ANCHOR):][:ZONE]
                    matches = ANNOT_RE.findall(zone)
                    if len(matches) != 1:
                        bad = 'line %d of %s annotation count %d' % (cline, cpath, len(matches))
                    else:
                        stated = int(matches[0])
                        if stated != stale or stale == m_val:
                            bad = 'line %d of %s reads %d, correction claims stale=%d recomputed=%d' % (
                                cline, cpath, stated, stale, m_val)
        if bad is not None:
            inert += 1
            finding('INERT-CORRECTION', '%s:%d %s' % (cpath, cline, bad))
        if corr_no in fences:
            fenced += 1
            finding('CORRECTION-IN-FENCE', 'correction at %s:%d (site %s:%d)' % (CORR_FILE, corr_no, cpath, cline))

    dels = numstat_deletions(root, base, rev, [RECORD] + SITES + [CORR_FILE])
    if dels is None:
        out.append('CANNOT-EVALUATE numstat failed')
        return 2
    deleted = [(p, d) for (p, d) in dels if d != 0]
    for (p, d) in deleted:
        finding('DELETED-LINES', '%s deletions=%s between %s..%s' % (p, d, base[:12], rev[:12]))

    mism, filed = 0, 0
    for path in SITES:
        s_line, stated = site_zone_stated[path]
        status = 'match' if stated == recomputed else 'mismatch'
        tup = (path, s_line, stated, recomputed)
        # A fenced correction neither files nor passes (CORRECTION-IN-FENCE);
        # filedness looks at the correction's own line number.
        corr_nos = [t[4] for t in corr_tuples if t[:4] == tup]
        is_filed = bool(corr_nos) and all(n not in fences for n in corr_nos)
        if status == 'mismatch':
            mism += 1
            if is_filed:
                filed += 1
        out.append('SITE path=%s line=%d stated=%d recomputed=%d status=%s filed=%s'
                   % (path, s_line, stated, recomputed, status, 'yes' if is_filed else 'no'))
    unfiled = mism - filed
    out.append('SUMMARY sites=%d mismatches=%d filed=%d unfiled=%d record_sha=%s appended=%s '
               'multi=%d inert=%d fenced=%d recomputed=%d rev=%s base=%s'
               % (len(SITES), mism, filed, unfiled,
                  'ok' if record_sha_ok else 'MISMATCH',
                  'ok' if not deleted else 'DELETED',
                  len(zone_multi), inert, fenced, recomputed, rev[:12], base[:12]))
    if findings or unfiled > 0:
        return 1
    return 0


def run_selftest(work: Path, expected_path: Path, out):
    if not BUILDER.exists():
        out.append('CANNOT-EVALUATE builder missing: %s' % BUILDER)
        return 2
    spec = importlib.util.spec_from_file_location('r53fixtures', BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fdir = work / 'c1-fixtures'
    fdir.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name in mod.C1_FIXTURES:
        info = mod.build_one(name, fdir)
        manifest[name] = info
    exp = {}
    for row in expected_path.read_text().splitlines()[1:]:
        if not row.strip():
            continue
        f = row.split('\t')
        exp[f[0]] = (int(f[1]), f[2] if len(f) > 2 else '')
    ok = True
    for name in mod.C1_FIXTURES:
        info = manifest[name]
        buf = []
        base = info['tip'] if name not in ('F5-REWRITE', 'F6-RECORD-DRIFT') else info['base']
        rc = measure(Path(info['dir']), info['tip'], base, info['record_sha256'], buf)
        want_rc, want_find = exp.get(name, (None, ''))
        got_find = next((ln.split(' ')[1] for ln in buf if ln.startswith('FINDING ')), '')
        passed = (rc == want_rc) and (want_find in ('', '-') or got_find == want_find)
        ok = ok and passed
        out.append('SELFTEST-CASE %s %s rc=%d want_rc=%s finding=%s want_finding=%s'
                   % (name, 'pass' if passed else 'fail', rc, want_rc, got_find or '-', want_find or '-'))
    out.append('SELFTEST %s cases=%d' % ('pass' if ok else 'fail', len(mod.C1_FIXTURES)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root')
    ap.add_argument('--rev')
    ap.add_argument('--base')
    ap.add_argument('--record-sha256', dest='record_sha')
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
                                  ('--base', ns.base), ('--record-sha256', ns.record_sha)) if not v]
        if missing:
            print('CANNOT-EVALUATE missing required args: %s' % ', '.join(missing), file=sys.stderr)
            return 2
        if not re.fullmatch(r'[0-9a-f]{40}', ns.rev) or not re.fullmatch(r'[0-9a-f]{40}', ns.base):
            print('CANNOT-EVALUATE full 40-hex revisions required', file=sys.stderr)
            return 2
        if not re.fullmatch(r'[0-9a-f]{64}', ns.record_sha):
            print('CANNOT-EVALUATE record pin must be 64-hex', file=sys.stderr)
            return 2
        rc = measure(Path(ns.root).resolve(), ns.rev, ns.base, ns.record_sha, out)
    print('\n'.join(out))
    return rc


if __name__ == '__main__':
    sys.exit(main())
