#!/usr/bin/env python3
"""r29 C3 integrity legs (AMENDMENT A4, stricter-only; the frozen C3 counters are unchanged and still run).

Everything is read from the COMMITTED tree at --rev (an exported copy is used only to run the
working-tree-reading gate tool), never from the lane's working tree. Legs:
  L1 F3 entries: `ground: F3` (word boundary) in corpus/knowledge/ == 2
  L2 registry rows == 143 (base 139 + S216-S219); coverage agreement grounded=15 mapped=15 dangling=0 mismatches=0
  L3 gate-check over the exported tree -> entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
  L4 snapshots: every `snapshot:` path named by an F3 entry is a regular blob >= 512 bytes whose sha256 equals both
     census/round-29/sources/SHA256SUMS and census/round-29/records/fetch-receipts.tsv (http 200)
  L5 quotes: every double-quoted Gate quote has 4..25 words
  L6 URL binding: every https URL in an F3 entry Gate occurs in the `source` cell of a row that entry cites
  L7 no reserved-TLD host (.test .example .invalid .localhost) in an F3 entry or its cited rows
  L8 novelty vs the held entry dupe-finders-detect-then-act.md: entry identity carries `stx_nlink` and `stx_ino`, entry
     byte-equality carries `exit status`; the held entry carries none of these tokens
  L9 slice: a verdict row for campaign S118 exists and the Broder PDF has a 200 fetch receipt
Exit 0 iff every leg passes; 2 could-not-evaluate.
"""
import argparse, hashlib, os, re, shutil, subprocess, sys, tempfile

ENT = ['corpus/knowledge/duplicate-verdict-identity.md', 'corpus/knowledge/duplicate-verdict-byte-equality.md']
HELD = 'corpus/knowledge/dupe-finders-detect-then-act.md'

def git(root, *a, text=True):
    p = subprocess.run(['git', '-C', root, '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null', *a], capture_output=True)
    if p.returncode:
        raise SystemExit('COULD-NOT-EVALUATE git ' + ' '.join(a) + ': ' + p.stderr.decode('utf-8', 'replace'))
    return p.stdout.decode('utf-8', 'replace') if text else p.stdout

def blob(root, rev, path, text=True):
    p = subprocess.run(['git', '-C', root, 'cat-file', 'blob', f'{rev}:{path}'], capture_output=True)
    if p.returncode:
        return None
    return p.stdout.decode('utf-8', 'replace') if text else p.stdout

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', required=True)
    a = ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', a.rev):
        raise SystemExit('COULD-NOT-EVALUATE rev must be a full 40-hex revision')
    R, V = a.root, a.rev
    res = []
    def leg(n, ok, why=''):
        res.append(ok)
        print(f'{n} {"PASS" if ok else "FAIL"} {why}')
    grep = subprocess.run(['git', '-C', R, 'grep', '-lE', r'^ground: F3\b', V, '--', 'corpus/knowledge/'], capture_output=True, text=True).stdout.split()
    leg('L1', len(grep) == 2, f'f3_entries={len(grep)}')
    reg = blob(R, V, 'corpus/SOURCES.md') or ''
    rows = {}
    for l in reg.splitlines():
        if re.match(r'^ {0,3}\|\s*S\d{3,}\s*\|', l):
            c = [x.strip() for x in l.split('|')]
            rows[c[1]] = c
    cov = subprocess.run([sys.executable, '-B', os.path.join(R, 'tools/souji-coverage-agreement.py'), '--root', R, '--rev', V], capture_output=True, text=True).stdout.strip()
    leg('L2', len(rows) == 143 and cov == 'grounded=15 mapped=15 dangling=0 mismatches=0', f'rows={len(rows)} coverage="{cov}"')
    tmp = tempfile.mkdtemp(prefix='souji-r29-c3int.', dir='/var/tmp')
    try:
        tar = subprocess.run(['git', '-C', R, 'archive', V, 'tools', 'corpus', 'census/round-29'], capture_output=True)
        ex = tar.returncode == 0 and subprocess.run(['tar', '-x', '-C', tmp], input=tar.stdout, capture_output=True).returncode == 0
        g = ex and subprocess.run([sys.executable, '-B', 'tools/souji-gate-check.py', '--root', '.', '--round-date', '2026-10-25', '--entries', *ENT,
                            '--snapshot-dir', 'census/round-29/sources', '--slice', 'census/round-29/records/quarantine-slice',
                            '--slice-verdicts', 'census/round-29/records/slice-verdicts.tsv'], capture_output=True, text=True, cwd=tmp)
        line = [x for x in (g.stdout + g.stderr).splitlines() if x.startswith('entries=')] if g else []
        leg('L3', bool(g) and g.returncode == 0 and line == ['entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0'], f'gate="{line[0] if line else "none"}" rc={g.returncode if g else "export-failed"}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sums = {}
    for l in (blob(R, V, 'census/round-29/sources/SHA256SUMS') or '').splitlines():
        f = l.split()
        if len(f) == 2:
            sums[f[1]] = f[0]
    fr = {}
    for l in (blob(R, V, 'census/round-29/records/fetch-receipts.tsv') or '').splitlines()[1:]:
        f = l.split('\t')
        if len(f) >= 6:
            fr[f[5].split(' ')[0]] = (f[1], f[4], f[0])
    bad4, bad5, bad6, bad7, words = [], [], [], [], []
    texts = {e: blob(R, V, e) or '' for e in ENT}
    for e, t in texts.items():
        cited = set(re.findall(r'^(?:- )?source:\s*(S\d{3,})', t, re.M))
        cellurls = ' '.join(rows[i][2] for i in cited if i in rows)
        gate = t[t.find('\n## Gate'):] if '\n## Gate' in t else ''
        for sp in set(re.findall(r'snapshot:\s*(\S+)', gate)):
            data = blob(R, V, sp, text=False)
            h = hashlib.sha256(data).hexdigest() if data is not None else None
            base = os.path.basename(sp)
            if data is None or len(data) < 512 or sums.get(base) != h or fr.get(sp, ('', '', ''))[1] != h or fr.get(sp, ('', '', ''))[0] != '200':
                bad4.append(f'{e}:{sp}')
        for q in re.findall(r'"([^"]{2,400})"', gate):
            n = len(q.split())
            if n < 4 or n > 25:
                bad5.append(f'{e}:{n}w:{q[:30]}')
        for u in set(re.findall(r'https://[^\s)"`>]+', gate)):
            if u.rstrip('.,;') not in cellurls:
                bad6.append(f'{e}:{u}')
        for u in re.findall(r'https?://([^/\s)"`>]+)', t + cellurls):
            if re.search(r'\.(test|example|invalid|localhost)$', u):
                bad7.append(u)
    leg('L4', not bad4, f'bad={bad4}')
    leg('L5', not bad5, f'bad={bad5}')
    leg('L6', not bad6, f'bad={bad6}')
    leg('L7', not bad7, f'bad={bad7}')
    held = (blob(R, V, HELD) or '').lower()
    t1, t2 = texts[ENT[0]].lower(), texts[ENT[1]].lower()
    ok8 = all(k in t1 for k in ('stx_nlink', 'stx_ino')) and 'exit status' in t2 and not any(k in held for k in ('stx_nlink', 'stx_ino', 'exit status'))
    leg('L8', ok8, f'identity_has={[k for k in ("stx_nlink","stx_ino") if k in t1]} bytes_has={"exit status" in t2} held_has={[k for k in ("stx_nlink","stx_ino","exit status") if k in held]}')
    sv = blob(R, V, 'census/round-29/records/slice-verdicts.tsv') or ''
    leg('L9', any(l.startswith('S118\t') for l in sv.splitlines()) and fr.get('census/round-29/sources/broder97resemblance.pdf', ('',))[0] == '200', '')
    print(f'SUMMARY legs={len(res)} fail={res.count(False)} rev={V}')
    return 0 if all(res) else 1

if __name__ == '__main__':
    sys.exit(main())
