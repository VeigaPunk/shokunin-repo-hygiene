#!/usr/bin/env python3
"""C2 counter (souji round 57): receipt revision binding gate.

Frozen predicate: census/round-57/preregistration.txt, claim C2. The r56
non-author closure routed one operability defect to this round
(corpus/lessons/round-56-verifier-spotcheck.md, routed defect 1, Q109): the
standing-suite receipts name no measured revision, so a reader cannot tell the
tree a receipt graded from the tree it is filed against. This gate reads a
manifest of receipts and refuses every receipt that does not bind a durable
full-40-hex revision:

  RECEIPT-REV-MISSING              no `rev=<token>` token in the receipt
  RECEIPT-REV-SHORT                a hex token shorter than 40 characters
  RECEIPT-REV-NOT-FULL40           a token that is not hex at all (HEAD, a
                                   branch name, `<short>…`)
  RECEIPT-REV-ABSENT               a full40 token that names no commit object
  RECEIPT-REV-KEEP-ONLY            a commit reachable only from refs/jj/* —
                                   jj keep refs are not durable (r17/r19)
  RECEIPT-INSTRUMENT-PIN-MISSING   the manifest names an instrument and the
                                   receipt carries no instrument_sha256=
  RECEIPT-INSTRUMENT-DIGEST-MISMATCH  instrument_sha256= differs from the
                                   committed blob of that instrument at the
                                   receipt's revision
  RECEIPT-EXIT-MISSING             no `EXIT=<int>` line (an unconditional
                                   pass claim, not a counter receipt)
  RECEIPT-SYMLINK                  the receipt path is a symlink (never read
                                   through one; QUALITY-scope refusal)

Manifest: a TSV with a header line, then `receipt<TAB>instrument` rows. Both
paths are relative to --root; `-` means "no instrument pin required".

Exit 0: every receipt clean. Exit 1: any finding. Exit 2: could-not-evaluate
(bad CLI, unreadable manifest, a row with the wrong column count, a missing
root, or `--selftest` without --work).

Read-only over the named repositories (git plumbing only, scrubbed
environment, fsmonitor/hooks neutralized). Writes nothing outside --work
(selftest only). No network. Scratch honours TMPDIR/--scratch.

Selftest: --selftest --work DIR [--expected TSV] builds the synthetic
repository and receipt fixtures (this file's own builder, no network) and
asserts the exit code and the full ordered finding list of every case against
`--expected` (records/c2-selftest-expected.tsv by default). A discarded
always-clean stub is scored over the same cases: if the stub meets the
expectations the selftest fails (`control=FALSE-GREEN-REJECTED` is the green
outcome).
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_EXPECTED = HERE / 'records' / 'c2-selftest-expected.tsv'
REV_RE = re.compile(r'(?:^|\s)rev=([^\s]+)(?=\s|$)')
PIN_RE = re.compile(r'(?:^|\s)instrument_sha256=([0-9a-f]{64})(?=\s|$)')
INSTR_RE = re.compile(r'(?:^|\s)instrument=([^\s]+)(?=\s|$)')
EXIT_RE = re.compile(r'(?m)^EXIT=(\d+)\s*$')
FULL40 = re.compile(r'[0-9a-f]{40}')
HEXISH = re.compile(r'[0-9A-Za-z._/\-]+')


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


def durable_kind(root, rev):
    """'branch' when rev is reachable from a non-jj ref; 'keep-only' when it is
    reachable from refs/jj/* only; 'absent' when the object is missing."""
    if git(root, 'cat-file', '-e', rev + '^{commit}').returncode:
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


def check_receipt(root: Path, rel: str, instrument: str):
    findings = []
    p = root / rel
    if p.is_symlink():
        return ['RECEIPT-SYMLINK %s' % rel]
    if not p.is_file():
        return ['RECEIPT-MISSING %s' % rel]
    text = p.read_bytes().decode('utf-8', 'replace')
    m = REV_RE.search(text)
    if not m:
        return ['RECEIPT-REV-MISSING %s' % rel]
    tok = m.group(1)
    if FULL40.fullmatch(tok):
        kind = durable_kind(root, tok)
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
            blocked = git(root, 'show', '%s:%s' % (tok, instrument))
            if blocked is None or blocked.returncode:
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
    total = 0
    for rel, instrument in rows:
        for f in check_receipt(root, rel, instrument):
            total += 1
            out.append('FINDING ' + f)
    out.append('SUMMARY receipts=%d findings=%d' % (len(rows), total))
    return 0 if total == 0 else 1


def build_fixtures(work: Path):
    """Synthetic repository + receipts. Returns {case: (root, manifest)}."""
    base = work / 'c2-fixtures'
    base.mkdir(parents=True, exist_ok=True)
    repo = base / 'repo'
    repo.mkdir(exist_ok=True)
    env = dict(os.environ, **git_env())

    def run(*args):
        p = subprocess.run(list(args), cwd=str(repo), capture_output=True, env=env, timeout=120)
        if p.returncode:
            raise SystemExit('fixture build failed: %r %s' % (args, p.stderr.decode()))
        return p.stdout.decode().strip()

    run('git', 'init', '-q', '-b', 'main')
    run('git', 'config', 'user.name', 'fixture')
    run('git', 'config', 'user.email', 'fixture@example.invalid')
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
    run('git', 'update-ref', 'refs/jj/keep/fixture', keep)
    run('git', 'reset', '-q', '--hard', tip)
    absent = '0' * 40
    short = tip[:12]
    receipts = repo / 'receipts'
    receipts.mkdir(exist_ok=True)

    def receipt(name, body, instrument=True):
        (receipts / name).write_text(body)
        mf = base / (name + '.manifest.tsv')
        col = 'tools/fixture-instrument.py' if instrument else '-'
        mf.write_text('receipt\tinstrument\n%s\t%s\n' % ('receipts/' + name, col))
        return mf

    honest = ('rev=%s\ninstrument=tools/fixture-instrument.py\n'
              'instrument_sha256=%s\nSUMMARY fixture clean\nEXIT=0\n' % (tip, instr_sha))
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
    return repo, cases


def run_selftest(work: Path, expected_path: Path, out):
    repo, cases = build_fixtures(work)
    exp = {}
    for row in expected_path.read_text().splitlines()[1:]:
        if not row.strip():
            continue
        f = row.split('\t')
        want = [x for x in (f[1] if len(f) > 1 else '').split(',') if x and x != '-']
        exp[f[0]] = want
    ok = True
    stub_meets = 0
    for name in sorted(cases):
        buf = []
        rc = run_manifest(repo, cases[name], buf)
        got = [ln.split(' ')[1] for ln in buf if ln.startswith('FINDING ')]
        want = exp.get(name, ['<missing-expected>'])
        passed = (got == want)
        ok = ok and passed
        stub_meets += 1 if want == [] else 0
        out.append('SELFTEST-CASE %s %s rc=%d want_rc=%s findings=%s want_findings=%s'
                   % (name, 'pass' if passed else 'fail', rc,
                      0 if want == [] else 1,
                      ','.join(got) or '-', ','.join(want) or '-'))
    # the always-clean stub: exit 0 plus an empty finding list. If it meets
    # every non-clean case the fixture cannot discriminate.
    if stub_meets > 1:
        ok = False
        out.append('SELFTEST control=FALSE-GREEN-ACCEPTED stub_meets=%d' % stub_meets)
    else:
        out.append('SELFTEST control=FALSE-GREEN-REJECTED stub_meets=%d cases=%d'
                   % (stub_meets, len(cases)))
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
