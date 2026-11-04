#!/usr/bin/env python3
"""C2 gate (souji round 58): receipt path confinement, revision typing, header conflict.

Derivation: census/round-57/c2-counter.py (frozen bytes, never edited). Predicate:
census/round-58/preregistration.txt claim C2, freeze commit
e7f64f30324e8ddb3f2266302daa9066054cdbb3. This gate repairs five independently
discriminated refusal cases of the r57 receipt interface and preserves the three
honest r57 after-manifest receipts clean:

  absolute receipt path            -> RECEIPT-PATH-UNCONFINED (refused before read)
  ../ traversal                    -> RECEIPT-PATH-UNCONFINED (refused before read)
  intermediate symlink escape      -> RECEIPT-PATH-UNCONFINED (refused before read)
  exact OID whose cat-file type is tag
                                   -> RECEIPT-REV-ABSENT
  conflicting standalone rev headers -> RECEIPT-REV-CONFLICT; identical duplicate
                                   headers allowed. SUMMARY rev fields are body
                                   data. If no standalone header exists, the
                                   legacy whitespace-token grammar is retained.

Preserved r57 behaviour: RECEIPT-REV-MISSING / RECEIPT-REV-SHORT /
RECEIPT-REV-NOT-FULL40 / RECEIPT-REV-ABSENT (missing object) /
RECEIPT-REV-KEEP-ONLY (refs/jj/keep only) / RECEIPT-SYMLINK (final component,
never read through one) / RECEIPT-MISSING / RECEIPT-EXIT-MISSING /
RECEIPT-INSTRUMENT-PIN-MISSING / RECEIPT-INSTRUMENT-DIGEST-MISMATCH /
RECEIPT-INSTRUMENT-NAME-MISMATCH. Commits reachable from refs/heads, refs/tags
or refs/remotes stay accepted; only the exact tag OBJECT OID is refused.

Selftest: --selftest --work DIR [--expected TSV] rebuilds the synthetic
repository and receipt fixtures in a uniquely created directory under --work.
Only that created directory is cleaned in finally; caller subtrees are untouched.
asserts, per case: exit code AND the full ordered canonical finding list, plus
exact case-set identity between fixtures and the expected TSV. Findings are
canonicalised for comparison: the fixtures directory prefix becomes <work> and
every hex run of 7..64 chars becomes <hex>, so the expected TSV is host
independent. A do-nothing stub (always rc=0, no findings) is scored over the
same cases: it must fail at least one case or the fixture set cannot
discriminate (`control=FALSE-GREEN-ACCEPTED` is the failure outcome).

Exit 0: clean (or passing selftest). Exit 1: any finding (or failed selftest).
Exit 2: could-not-evaluate. Read-only over the named repositories (git plumbing
only, scrubbed environment, fsmonitor/hooks neutralised). Writes nothing outside
--work (selftest only). No network.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
DEFAULT_EXPECTED = HERE / 'c2-selftest-expected.tsv'
REV_RE = re.compile(r'(?:^|\s)rev=([^\s]+)(?=\s|$)')
HEADER_REV_RE = re.compile(r'(?m)^[ \t]*rev=([^\s]+)[ \t]*\r?$')
PIN_RE = re.compile(r'(?:^|\s)instrument_sha256=([0-9a-f]{64})(?=\s|$)')
INSTR_RE = re.compile(r'(?:^|\s)instrument=([^\s]+)(?=\s|$)')
EXIT_RE = re.compile(r'(?m)^EXIT=(\d+)\s*$')
FULL40 = re.compile(r'[0-9a-f]{40}')
HEXISH = re.compile(r'[0-9A-Za-z._/\-]+')
HEXRUN = re.compile(r'[0-9a-f]{7,64}')


def git_env():
    return {
        'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
        'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
        'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
        'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1',
        'GIT_TERMINAL_PROMPT': '0',
    }


def git(root, *args):
    return subprocess.run(['git', '-C', str(root),
                           '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null']
                          + list(args), capture_output=True, env=git_env(), timeout=120)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def path_finding(root_real: str, rel: str):
    """Confinement verdict BEFORE any content read. None when confined."""
    try:
        if not rel:
            return 'RECEIPT-PATH-UNCONFINED %s' % rel
        pp = PurePosixPath(rel)
        if pp.is_absolute() or rel.startswith('/'):
            return 'RECEIPT-PATH-UNCONFINED %s' % rel
        parts = pp.parts
        if any(part == '..' for part in parts):
            return 'RECEIPT-PATH-UNCONFINED %s' % rel
        cur = root_real
        for i, part in enumerate(parts):
            cur = os.path.join(cur, part)
            if os.path.islink(cur):
                if i == len(parts) - 1:
                    return 'RECEIPT-SYMLINK %s' % rel
                real = os.path.realpath(cur)
                if real != root_real and not real.startswith(root_real + os.sep):
                    return 'RECEIPT-PATH-UNCONFINED %s' % rel
        real = os.path.realpath(cur)
        if real != root_real and not real.startswith(root_real + os.sep):
            return 'RECEIPT-PATH-UNCONFINED %s' % rel
    except (OSError, ValueError):
        return 'RECEIPT-PATH-UNCONFINED %s' % rel
    return None


def durable_kind(root, rev):
    """'branch' when the exact object is a commit reachable from a non-jj ref;
    'keep-only' when reachable from refs/jj/keep only; 'absent' when the object
    is missing or is not a commit object (an annotated tag object OID names no
    commit: RECEIPT-REV-ABSENT by the r58 contract)."""
    t = git(root, 'cat-file', '-t', rev)
    if t.returncode:
        return 'absent'
    if t.stdout.decode('utf-8', 'replace').strip() != 'commit':
        return 'absent'
    refs = git(root, 'for-each-ref', '--format=%(refname)',
               'refs/heads', 'refs/tags', 'refs/remotes').stdout.decode().split()
    for r in refs:
        if git(root, 'merge-base', '--is-ancestor', rev, r).returncode == 0:
            return 'branch'
    keeps = git(root, 'for-each-ref', '--format=%(refname)', 'refs/jj/keep').stdout.decode().split()
    for r in keeps:
        if git(root, 'merge-base', '--is-ancestor', rev, r).returncode == 0:
            return 'keep-only'
    return 'absent'




def check_receipt(root_real: str, rel: str, instrument: str):
    unconfined = path_finding(root_real, rel)
    if unconfined:
        return [unconfined]                    # refused BEFORE reading
    p = Path(root_real) / rel
    if p.is_symlink():
        return ['RECEIPT-SYMLINK %s' % rel]    # never read through one
    if not p.is_file():
        return ['RECEIPT-MISSING %s' % rel]
    text = p.read_bytes().decode('utf-8', 'replace')
    toks = []
    matches = list(HEADER_REV_RE.finditer(text)) or list(REV_RE.finditer(text))
    for m in matches:
        if m.group(1) not in toks:
            toks.append(m.group(1))
    if not toks:
        return ['RECEIPT-REV-MISSING %s' % rel]
    if len(toks) > 1:
        return ['RECEIPT-REV-CONFLICT %s rev=%s' % (rel, '|'.join(toks))]
    tok = toks[0]
    findings = []
    if FULL40.fullmatch(tok):
        kind = durable_kind(root_real, tok)
        if kind == 'absent':
            findings.append('RECEIPT-REV-ABSENT %s rev=%s' % (rel, tok))
        elif kind == 'keep-only':
            findings.append('RECEIPT-REV-KEEP-ONLY %s rev=%s' % (rel, tok))
    elif HEXISH.fullmatch(tok) and re.fullmatch(r'[0-9a-f]{1,39}', tok):
        findings.append('RECEIPT-REV-SHORT %s rev=%s' % (rel, tok))
    else:
        findings.append('RECEIPT-REV-NOT-FULL40 %s rev=%s' % (rel, tok))
    if not EXIT_RE.search(text):
        findings.append('RECEIPT-EXIT-MISSING %s' % rel)
    if instrument and instrument != '-' and FULL40.fullmatch(tok):
        pm = PIN_RE.search(text)
        if not pm:
            findings.append('RECEIPT-INSTRUMENT-PIN-MISSING %s instrument=%s' % (rel, instrument))
        else:
            blocked = git(root_real, 'show', '%s:%s' % (tok, instrument))
            if blocked.returncode:
                findings.append('RECEIPT-INSTRUMENT-PIN-MISSING %s instrument=%s absent at rev'
                                % (rel, instrument))
            else:
                got = sha256(blocked.stdout)
                if got != pm.group(1):
                    findings.append('RECEIPT-INSTRUMENT-DIGEST-MISMATCH %s instrument=%s '
                                    'pin=%s committed=%s' % (rel, instrument, pm.group(1), got))
            im = INSTR_RE.search(text)
            if im and im.group(1) != instrument:
                findings.append('RECEIPT-INSTRUMENT-NAME-MISMATCH %s receipt=%s manifest=%s'
                                % (rel, im.group(1), instrument))
    return findings


def run_manifest(root: Path, manifest: Path, out):
    rows = []
    try:
        lines = manifest.read_text().splitlines()
    except OSError as exc:
        out.append('CANNOT-EVALUATE manifest unreadable: %s' % exc)
        return 2
    if not lines or not lines[0].strip():
        out.append('CANNOT-EVALUATE empty manifest')
        return 2
    for n, ln in enumerate(lines[1:], 2):
        if not ln.strip():
            continue
        f = ln.split('\t')
        if len(f) != 2:
            out.append('CANNOT-EVALUATE manifest line %d: %d columns' % (n, len(f)))
            return 2
        rows.append((f[0].strip(), f[1].strip()))
    root_real = os.path.realpath(str(root))
    total = 0
    for rel, instrument in rows:
        for f in check_receipt(root_real, rel, instrument):
            total += 1
            out.append('FINDING ' + f)
    out.append('SUMMARY receipts=%d findings=%d' % (len(rows), total))
    return 0 if total == 0 else 1


def build_fixtures(work: Path):
    """Synthetic repository + receipts, rebuilt from scratch each call.
    Returns (repo, base, {case: manifest})."""
    base = work.resolve()
    repo = base / 'repo'
    repo.mkdir(exist_ok=True)
    env = dict(git_env())
    env['GIT_AUTHOR_DATE'] = '2026-11-01T00:00:00+0000'
    env['GIT_COMMITTER_DATE'] = '2026-11-01T00:00:00+0000'

    def run(*args):
        command = ['git', '-C', str(repo), '-c', 'core.hooksPath=/dev/null',
                   '-c', 'core.fsmonitor=false'] + list(args[1:])
        if args[1] != 'init':
            top = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--show-toplevel'],
                                 capture_output=True, env=env, timeout=120)
            if top.returncode or Path(top.stdout.decode().strip()).resolve() != repo:
                raise SystemExit('fixture toplevel mismatch')
        p = subprocess.run(command, cwd=str(repo), capture_output=True, env=env, timeout=120)
        if p.returncode:
            raise SystemExit('fixture build failed: %r %s' % (args, p.stderr.decode()))
        return p.stdout.decode().strip()

    run('git', 'init', '-q', '-b', 'main')
    run('git', 'config', 'user.name', 'fixture')
    run('git', 'config', 'user.email', 'fixture@example.invalid')
    top = run('git', 'rev-parse', '--show-toplevel')
    if os.path.realpath(top) != os.path.realpath(repo):
        raise SystemExit('fixture build failed: toplevel %r is not %r' % (top, str(repo)))
    (repo / 'tools').mkdir(exist_ok=True)
    (repo / 'tools' / 'fixture-instrument.py').write_text('# fixture instrument v1\n')
    run('git', 'add', 'tools/fixture-instrument.py')
    run('git', 'commit', '-q', '-m', 'fixture base')
    tip = run('git', 'rev-parse', 'HEAD')
    instr_sha = sha256((repo / 'tools' / 'fixture-instrument.py').read_bytes())
    # a second commit reachable only from a jj keep ref
    (repo / 'tools' / 'fixture-instrument.py').write_text('# fixture instrument keep-only\n')
    run('git', 'add', 'tools/fixture-instrument.py')
    run('git', 'commit', '-q', '-m', 'keep-only commit')
    keep = run('git', 'rev-parse', 'HEAD')
    keepref = repo / '.git/refs/jj/keep/fixture'
    keepref.parent.mkdir(parents=True, exist_ok=True)
    keepref.write_text(keep + '\n')
    (repo / '.git/refs/heads/main').write_text(tip + '\n')
    # Construct the annotated tag as a loose Git object without tag/update-ref.
    tagbody = ('object %s\ntype commit\ntag vannot\ntagger fixture '
               '<fixture@example.invalid> 1793491200 +0000\n\nfixture tag\n' % tip).encode()
    tagobject = b'tag ' + str(len(tagbody)).encode() + b'\0' + tagbody
    tagoid = hashlib.sha1(tagobject).hexdigest()
    objpath = repo / '.git/objects' / tagoid[:2] / tagoid[2:]
    objpath.parent.mkdir(parents=True, exist_ok=True)
    objpath.write_bytes(zlib.compress(tagobject))
    (repo / '.git/refs/tags/vannot').write_text(tagoid + '\n')
    absent = '0' * 40
    short = tip[:12]
    receipts = repo / 'receipts'
    receipts.mkdir(exist_ok=True)

    def honest_body(rev):
        return ('rev=%s\ninstrument=tools/fixture-instrument.py\ninstrument_sha256=%s\n'
                'SUMMARY fixture clean\nEXIT=0\n' % (rev, instr_sha))

    def receipt(name, body, instrument=True):
        (receipts / name).write_text(body)
        mf = base / (name + '.manifest.tsv')
        col = 'tools/fixture-instrument.py' if instrument else '-'
        mf.write_text('receipt\tinstrument\n%s\t%s\n' % ('receipts/' + name, col))
        return mf

    honest = honest_body(tip)
    cases = {}
    cases['REV-OK'] = receipt('ok.txt', honest)
    cases['MISSING-REV'] = receipt('missing.txt', honest.replace('rev=%s\n' % tip, ''))
    cases['SHORT-REV'] = receipt('short.txt', honest.replace('rev=%s' % tip, 'rev=%s' % short))
    cases['NOT-FULL40'] = receipt('head.txt', honest.replace('rev=%s' % tip, 'rev=HEAD'))
    cases['ABSENT'] = receipt('absent.txt', honest.replace('rev=%s' % tip, 'rev=%s' % absent),
                              instrument=False)
    cases['KEEP-ONLY'] = receipt('keep.txt', honest.replace('rev=%s' % tip, 'rev=%s' % keep),
                                 instrument=False)
    cases['DIGEST-MISMATCH'] = receipt('digest.txt',
                                       honest.replace('instrument_sha256=%s' % instr_sha,
                                                      'instrument_sha256=%s' % ('f' * 64)))
    cases['NO-EXIT'] = receipt('noexit.txt', honest.replace('EXIT=0\n', ''))
    cases['TAG-OID'] = receipt('tagobj.txt', honest.replace('rev=%s' % tip, 'rev=%s' % tagoid),
                               instrument=False)
    cases['REV-CONFLICT'] = receipt('conflict.txt',
                                    honest.replace('rev=%s' % tip,
                                                   'rev=%s\nrev=%s' % (tip, absent)),
                                    instrument=False)
    dup = honest.replace('rev=%s\n' % tip, 'rev=%s\nrev=%s\n' % (tip, tip), 1)
    cases['DUP-REV'] = receipt('dup.txt', dup)
    # A SUMMARY short rev is body data, not another binding header.
    prefix_dup = honest.replace('SUMMARY fixture clean', 'SUMMARY fixture clean rev=' + short)
    cases['PREFIX-DUP'] = receipt('prefixdup.txt', prefix_dup)
    # final-component symlink: refused without reading (r57 behaviour kept)
    (receipts / 'ok-target.txt').write_text(honest)
    os.symlink('ok-target.txt', receipts / 'sym.txt')
    mf = base / 'sym.txt.manifest.tsv'
    mf.write_text('receipt\tinstrument\nreceipts/sym.txt\ttools/fixture-instrument.py\n')
    cases['SYMLINK'] = mf
    # intermediate symlink resolving INSIDE the root: allowed
    inner = receipts / 'inner'
    inner.mkdir(exist_ok=True)
    (inner / 'ok2.txt').write_text(honest)
    os.symlink('inner', receipts / 'inlink')
    mf = base / 'inlink.manifest.tsv'
    mf.write_text('receipt\tinstrument\nreceipts/inlink/ok2.txt\ttools/fixture-instrument.py\n')
    cases['LINK-INTERNAL'] = mf
    # escapes OUTSIDE the root carrying honest content: a gate that reads them
    # would return clean; the contract refuses them before reading
    escape = base / 'escape'
    escape.mkdir(exist_ok=True)
    abs_target = escape / 'abs-target.txt'
    abs_target.write_text(honest)
    (escape / 'trav.txt').write_text(honest)
    (escape / 'esc.txt').write_text(honest)
    mf = base / 'abs.manifest.tsv'
    mf.write_text('receipt\tinstrument\n%s\t-\n' % str(abs_target))
    cases['ABSOLUTE-PATH'] = mf
    mf = base / 'trav.manifest.tsv'
    mf.write_text('receipt\tinstrument\n../escape/trav.txt\t-\n')
    cases['TRAVERSAL'] = mf
    os.symlink(str(escape), receipts / 'linkdir')
    mf = base / 'linkdir.manifest.tsv'
    mf.write_text('receipt\tinstrument\nreceipts/linkdir/esc.txt\t-\n')
    cases['LINK-ESCAPE'] = mf
    return repo, base, cases


def canon(text: str, base: str) -> str:
    return HEXRUN.sub('<hex>', text.replace(base, '<work>'))


def run_selftest(work: Path, expected_path: Path, out):
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix='c2-fixtures-', dir=work))
    try:
        repo, base, cases = build_fixtures(base)
        return score_selftest(repo, base, cases, expected_path, out)
    finally:
        shutil.rmtree(base)


def score_selftest(repo, base, cases, expected_path, out):
    observed = {}
    for name in sorted(cases):
        buf = []
        rc = run_manifest(repo, cases[name], buf)
        raw = [ln[len('FINDING '):] for ln in buf if ln.startswith('FINDING ')]
        observed[name] = (rc, [canon(f, str(base)) for f in raw])
    try:
        rows = expected_path.read_text().splitlines()
    except OSError as exc:
        out.append('CANNOT-EVALUATE expected unreadable: %s' % exc)
        return 2
    exp = {}
    for row in rows[1:]:
        if not row.strip():
            continue
        f = row.split('\t')
        if len(f) != 3:
            out.append('CANNOT-EVALUATE expected line malformed: %r' % row)
            return 2
        if f[0] in exp:
            out.append('CANNOT-EVALUATE duplicate expected case: ' + f[0])
            return 2
        want = [x for x in f[2].split(',') if x and x != '-']
        try:
            want_rc = int(f[1])
        except ValueError:
            out.append('CANNOT-EVALUATE expected rc malformed: %r' % f[1])
            return 2
        exp[f[0]] = (want_rc, want)
    ok = True
    extra = sorted(set(exp) - set(cases))
    missing = sorted(set(cases) - set(exp))
    if extra or missing:
        ok = False
    out.append('SELFTEST-EXPECTED-SET cases=%d expected=%d extra=%s missing=%s'
               % (len(cases), len(exp), ','.join(extra) or '-', ','.join(missing) or '-'))
    stub_meets = 0
    for name in sorted(cases):
        rc, got = observed[name]
        want_rc, want = exp.get(name, (None, ['<missing-expected>']))
        passed = (want_rc is not None and rc == want_rc and got == want)
        ok = ok and passed
        if want_rc == 0 and not want:
            stub_meets += 1
        out.append('SELFTEST-CASE %s %s rc=%d want_rc=%s findings=%s want_findings=%s'
                   % (name, 'pass' if passed else 'fail', rc, want_rc,
                      ','.join(got) or '-', ','.join(want) or '-'))
    # the do-nothing stub (rc=0, no findings) must fail at least one case,
    # otherwise the fixture set cannot discriminate the gate from a stub
    if stub_meets == len(cases):
        ok = False
        out.append('SELFTEST control=FALSE-GREEN-ACCEPTED stub_meets=%d cases=%d'
                   % (stub_meets, len(cases)))
    else:
        out.append('SELFTEST control=FALSE-GREEN-REJECTED stub_meets=%d discriminated=%d cases=%d'
                   % (stub_meets, len(cases) - stub_meets, len(cases)))
    out.append('SELFTEST %s cases=%d' % ('pass' if ok else 'fail', len(cases)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root')
    ap.add_argument('--manifest')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--work', default=None)
    ap.add_argument('--scratch', default=None, help='alias of --work')
    ap.add_argument('--expected', default=None)
    ns = ap.parse_args()
    out = []
    if ns.selftest:
        work = ns.work or ns.scratch
        if not work:
            print('CANNOT-EVALUATE --selftest requires --work (or --scratch)', file=sys.stderr)
            return 2
        exp = Path(ns.expected) if ns.expected else DEFAULT_EXPECTED
        rc = run_selftest(Path(work), exp, out)
    else:
        missing = [a for a, v in (('--root', ns.root), ('--manifest', ns.manifest)) if not v]
        if missing:
            print('CANNOT-EVALUATE missing required args: %s' % ', '.join(missing), file=sys.stderr)
            return 2
        root = Path(ns.root).resolve()
        if not root.is_dir():
            print('CANNOT-EVALUATE --root is not a directory: %s' % root, file=sys.stderr)
            return 2
        rc = run_manifest(root, Path(ns.manifest), out)
    print('\n'.join(out))
    return rc


if __name__ == '__main__':
    sys.exit(main())
