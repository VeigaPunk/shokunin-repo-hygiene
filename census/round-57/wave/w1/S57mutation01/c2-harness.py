#!/usr/bin/env python3
"""souji r57 seat S57mutation01: C2 gate mutation harness (scratch only).

Each mutant = exact single-occurrence text replacement over a scratch copy of
census/round-57/c2-counter.py. Never touches the frozen file. One fresh
--work dir per run; the committed expected TSV is passed explicitly.
"""
import difflib
import hashlib
import os
import subprocess
import sys
from pathlib import Path

BASE = Path('/fast/scratch/hyaku/souji-r57/S57mutation01/base/c2-counter.py')
ROOT = Path('/fast/scratch/hyaku/souji-r57/S57mutation01')
EXPECTED = Path('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/records/c2-selftest-expected.tsv')

MUTANTS = [
    ('M1-drop-exit-check', 'drop the EXIT= line requirement', [(
        "    if not EXIT_RE.search(text):\n"
        "        findings.append('RECEIPT-EXIT-MISSING %s' % rel)\n",
        "    if False:  # MUTANT M1: EXIT= line requirement dropped\n"
        "        findings.append('RECEIPT-EXIT-MISSING %s' % rel)\n",
    )]),
    ('M2-accept-short-rev', 'silently accept a short hex rev', [(
        "    elif HEXISH.fullmatch(tok) and re.fullmatch(r'[0-9a-f]{1,39}', tok):\n"
        "        findings.append('RECEIPT-REV-SHORT %s rev=%s' % (rel, tok))\n",
        "    elif HEXISH.fullmatch(tok) and re.fullmatch(r'[0-9a-f]{1,39}', tok):\n"
        "        pass  # MUTANT M2: a short hex rev is silently accepted\n",
    )]),
    ('M3-skip-durability', 'skip the durability classification of a full40 rev', [(
        "        kind = durable_kind(root, tok)\n"
        "        if kind == 'absent':\n"
        "            findings.append('RECEIPT-REV-ABSENT %s rev=%s' % (rel, tok))\n"
        "        elif kind == 'keep-only':\n"
        "            findings.append('RECEIPT-REV-KEEP-ONLY %s rev=%s' % (rel, tok))\n",
        "        pass  # MUTANT M3: durability of a full40 token never checked\n",
    )]),
    ('M4-skip-keep-only', 'skip only the jj keep-only branch', [(
        "        elif kind == 'keep-only':\n"
        "            findings.append('RECEIPT-REV-KEEP-ONLY %s rev=%s' % (rel, tok))\n",
        "        elif kind == 'keep-only':\n"
        "            pass  # MUTANT M4: jj keep-only reachability accepted as durable\n",
    )]),
    ('M5-skip-instrument-pin', 'skip the instrument pin / digest block entirely', [(
        "    if instrument and instrument != '-' and FULL40.fullmatch(tok):\n",
        "    if False:  # MUTANT M5: instrument pin check removed\n",
    )]),
    ('M6-skip-digest-compare', 'keep pin presence, drop the committed-blob comparison', [(
        "                if got != pm.group(1):\n"
        "                    findings.append('RECEIPT-INSTRUMENT-DIGEST-MISMATCH %s instrument=%s '\n"
        "                                    'pin=%s committed=%s' % (rel, instrument, pm.group(1), got))\n",
        "                if False:  # MUTANT M6: pin taken on faith, blob not compared\n"
        "                    findings.append('RECEIPT-INSTRUMENT-DIGEST-MISMATCH %s instrument=%s '\n"
        "                                    'pin=%s committed=%s' % (rel, instrument, pm.group(1), got))\n",
    )]),
    ('M7-first-finding-only', 'selftest asserts only the first finding', [(
        "        passed = (got == want)\n",
        "        passed = (got[:1] == want[:1])  # MUTANT M7: first finding only\n",
    )]),
    ('M8-accept-symlink', 'read through a symlinked receipt instead of refusing it', [(
        "    if p.is_symlink():\n"
        "        return ['RECEIPT-SYMLINK %s' % rel]\n",
        "    if p.is_symlink():\n"
        "        pass  # MUTANT M8: symlinked receipt read through the link\n",
    )]),
    ('M9-skip-column-check', 'tolerate a 1-column manifest row', [(
        "        if len(f) != 2:\n",
        "        if len(f) > 2:  # MUTANT M9: a 1-column manifest row tolerated\n",
    )]),
    ('M10-accept-symbolic-rev', 'silently accept a non-hex/symbolic rev token', [(
        "    else:\n"
        "        findings.append('RECEIPT-REV-NOT-FULL40 %s rev=%s' % (rel, tok))\n",
        "    else:\n"
        "        pass  # MUTANT M10: symbolic/non-hex rev silently accepted\n",
    )]),
    ('M11-skip-rev-missing', 'treat a receipt with no rev= token as clean', [(
        "        return ['RECEIPT-REV-MISSING %s' % rel]\n",
        "        return []  # MUTANT M11: a receipt with no rev= is treated as clean\n",
    )]),
    ('M12-rc-never-fails', 'findings never affect the gate exit code', [(
        "    return 0 if total == 0 else 1\n",
        "    return 0  # MUTANT M12: findings never affect the exit code\n",
    )]),
    ('M13-heads-only-durability', 'durability considers refs/heads only (tags/remotes ignored)', [(
        "               'refs/heads', 'refs/tags', 'refs/remotes').stdout.decode().split()\n",
        "               'refs/heads').stdout.decode().split()  # MUTANT M13: tags/remotes ignored\n",
    )]),
    ('M14-file-name-keyed', 'fake gate: finding chosen from the receipt basename, receipt never read', [(
        "def check_receipt(root: Path, rel: str, instrument: str):\n"
        "    findings = []\n",
        "def check_receipt(root: Path, rel: str, instrument: str):\n"
        "    findings = []\n"
        "    # MUTANT M14: filename-keyed fake (reads neither the receipt nor git)\n"
        "    fake = {'ok.txt': [], 'missing.txt': ['RECEIPT-REV-MISSING'],\n"
        "            'short.txt': ['RECEIPT-REV-SHORT'], 'head.txt': ['RECEIPT-REV-NOT-FULL40'],\n"
        "            'absent.txt': ['RECEIPT-REV-ABSENT'], 'keep.txt': ['RECEIPT-REV-KEEP-ONLY'],\n"
        "            'digest.txt': ['RECEIPT-INSTRUMENT-DIGEST-MISMATCH'],\n"
        "            'noexit.txt': ['RECEIPT-EXIT-MISSING']}\n"
        "    base_name = rel.rsplit('/', 1)[-1]\n"
        "    if base_name in fake:\n"
        "        return ['%s %s' % (fid, rel) for fid in fake[base_name]]\n",
    )]),
    ('M15-drop-keep-only-case', 'fixture builder stops building the KEEP-ONLY case', [(
        "    cases['KEEP-ONLY'] = receipt('keep.txt', honest.replace('rev=%s' % tip, 'rev=%s' % keep),\n"
        "                                 instrument=False)\n",
        "    # MUTANT M15: the KEEP-ONLY fixture case is never built\n",
    )]),
    ('M16-rev-no-boundary', 'rev= token matched without a word boundary before it', [(
        "REV_RE = re.compile(r'(?:^|\\s)rev=([^\\s]+)(?=\\s|$)')\n",
        "REV_RE = re.compile(r'rev=([^\\s]+)(?=\\s|$)')  # MUTANT M16: no left boundary\n",
    )]),
    ('M17-gate-first-finding-only', 'gate emits only the first finding per receipt', [(
        "    return findings\n",
        "    return findings[:1]  # MUTANT M17: only the first finding per receipt\n",
    )]),
    ('M18-drop-name-mismatch', 'drop the receipt-vs-manifest instrument name mismatch', [(
        "            im = INSTR_RE.search(text)\n"
        "            if im and im.group(1) != instrument:\n",
        "            im = INSTR_RE.search(text)\n"
        "            if False:  # MUTANT M18: receipt instrument= may disagree with the manifest\n",
    )]),
    ('M19-pin-working-tree', 'pin compared against working-tree bytes, not the blob at rev', [(
        "            blocked = git(root, 'show', '%s:%s' % (tok, instrument))\n",
        "            # MUTANT M19: working-tree bytes instead of rev:path\n"
        "            _wt = root / instrument\n"
        "            blocked = subprocess.CompletedProcess(\n"
        "                [], 0 if _wt.is_file() else 1, _wt.read_bytes() if _wt.is_file() else b'')\n",
    )]),
    ('M20-ref-tip-equality', 'durability = rev equals a ref tip, not reachability', [(
        "        if git(root, 'merge-base', '--is-ancestor', rev, r).returncode == 0:\n"
        "            return 'branch'\n",
        "        if git(root, 'rev-parse', r).stdout.decode().strip() == rev:\n"
        "            return 'branch'  # MUTANT M20: ref-tip equality, not reachability\n",
    )]),
    ('M21-always-refuse', 'mirror control: every receipt refuses, including the honest one', [(
        "def check_receipt(root: Path, rel: str, instrument: str):\n"
        "    findings = []\n",
        "def check_receipt(root: Path, rel: str, instrument: str):\n"
        "    findings = ['RECEIPT-ALWAYS-REFUSE %s' % rel]  # MUTANT M21: always-refuse gate\n",
    )]),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    base = BASE.read_bytes()
    print('# base sha256', sha(base), BASE)
    print('# expected  ', sha(EXPECTED.read_bytes()), EXPECTED)
    rows = []
    for name, desc, edits in MUTANTS:
        src = base.decode()
        for old, new in edits:
            n = src.count(old)
            if n != 1:
                print('ABORT %s: anchor count %d for %r' % (name, n, old[:60]))
                return 3
            src = src.replace(old, new)
        mdir = ROOT / 'mut' / name
        mdir.mkdir(parents=True, exist_ok=True)
        mf = mdir / 'c2-counter.py'
        mf.write_text(src)
        diff = ''.join(difflib.unified_diff(
            base.decode().splitlines(True), src.splitlines(True),
            fromfile='frozen/c2-counter.py', tofile=name + '/c2-counter.py'))
        (ROOT / 'diffs' / (name + '.diff')).write_text(diff)
        work = ROOT / 'work' / name
        env = dict(os.environ, TMPDIR=str(ROOT / 'tmp'))
        p = subprocess.run([sys.executable, '-B', str(mf), '--selftest', '--work', str(work),
                            '--expected', str(EXPECTED)],
                           capture_output=True, text=True, env=env, timeout=300)
        outp = p.stdout + (('\n[stderr]\n' + p.stderr) if p.stderr.strip() else '')
        (ROOT / 'out').mkdir(exist_ok=True)
        (ROOT / 'out' / (name + '.txt')).write_text(outp)
        cases = [ln for ln in p.stdout.splitlines() if ln.startswith('SELFTEST-CASE')]
        failed = [ln.split()[1] for ln in cases if ' fail ' in ln + ' ']
        final = [ln for ln in p.stdout.splitlines() if ln.startswith('SELFTEST ') and 'cases=' in ln]
        control = [ln for ln in p.stdout.splitlines() if 'control=' in ln]
        if not final:
            verdict = 'ERROR'
        elif p.returncode == 0:
            verdict = 'SURVIVED'
        else:
            verdict = 'KILLED'
        rows.append(dict(name=name, desc=desc, sha=sha(src.encode()), rc=p.returncode,
                         verdict=verdict, failed=failed, cases=len(cases),
                         control=(control[0].split('control=')[1].split()[0] if control else '?'),
                         final=(final[0] if final else 'NO-FINAL-LINE')))
        print('%s\t%s\trc=%d\t%s\tfailed=%s\t%s' % (
            name, verdict, p.returncode, ','.join(failed) or '-',
            ','.join('%s' % c for c in []), rows[-1]['final']))
    print()
    print('| mutant | edit | verdict | failing selftest cases |')
    for r in rows:
        print('| %s | %s | %s | %s |' % (r['name'], r['desc'], r['verdict'],
                                          ', '.join(r['failed']) or '-'))
    print()
    print('# survivors=%d killed=%d errors=%d' % (
        sum(r['verdict'] == 'SURVIVED' for r in rows),
        sum(r['verdict'] == 'KILLED' for r in rows),
        sum(r['verdict'] == 'ERROR' for r in rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
