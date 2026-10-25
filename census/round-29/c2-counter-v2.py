#!/usr/bin/env python3
"""r29 C2 counter v2 (AMENDMENT, stricter-only; the frozen v1 `c2-counter.py` is unchanged).

Everything v1 checks (failed / uncovered / floor) plus, read over COMMITTED bytes only:
  decode   GNU escapes `\\\\`, `\\n` and `\\r` (the host's uutils sha256sum also escapes CR)
  lost     a record path present in the --base-rev manifest and absent from the REV manifest that is
           not accounted for in the REV `excluded.tsv` (col1 = path) or `renames.tsv` (col1 = path)
  fidelity a record whose source path `.ufo/waves/round-N/<rel>` (renamed `.captured` files mapped
           back via renames.tsv) is tracked at REV but whose committed source blob has a different
           sha256 than the record
  floors   r26 >= 1378 (= 1382 base records - 4 `__pycache__` records the lane root .gitignore
           legitimately excludes: `git show <base>:census/round-26/waves/manifest.sha256 | grep -c __pycache__`),
           r27 >= 124, r28 >= 75, and --require-rounds must all have a manifest
  tool     `tools/souji-wave-evidence-capture.sh` blob at REV must differ from the blob at --base-rev
Prints per round and `SUMMARY manifests= failed= uncovered= lost= fidelity= floor_violations= tool_unchanged= rev=`.
Exit 0 iff all of those are zero (and manifests>=1).
"""
import argparse, hashlib, re, subprocess, sys

FLOORS = {'26': 1378, '27': 124, '28': 75}
TOOL = 'tools/souji-wave-evidence-capture.sh'

def git(root, *a):
    p = subprocess.run(['git', '-C', root, '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null', *a], capture_output=True)
    if p.returncode:
        raise SystemExit('COULD-NOT-EVALUATE git ' + ' '.join(a) + ': ' + p.stderr.decode('utf-8', 'replace'))
    return p.stdout

def unescape(s):
    return re.sub(r'\\([\\nr])', lambda m: {'n': '\n', 'r': '\r', '\\': '\\'}[m.group(1)], s)

def tree(root, rev, *paths):
    ents = {}
    for rec in git(root, 'ls-tree', '-r', '-z', rev, '--', *paths).split(b'\0'):
        if rec:
            meta, path = rec.split(b'\t', 1)
            mode, typ, sha = meta.decode().split()
            ents[path.decode('utf-8', 'surrogateescape')] = (mode, sha)
    return ents

def records(root, ents, m):
    text = git(root, 'cat-file', 'blob', ents[m][1]).decode('utf-8', 'surrogateescape')
    recs, bad = {}, 0
    for l in text.split('\n'):
        if not l:
            continue
        esc = l.startswith('\\')
        mm = re.match(r'^([0-9a-f]{64})  (.*)$', l[1:] if esc else l)
        if not mm:
            bad += 1
            continue
        name = unescape(mm.group(2)) if esc else mm.group(2)
        recs[name[2:] if name.startswith('./') else name] = mm.group(1)
    return recs, bad

def tsv_col(root, ents, p, col=0):
    out = {}
    if p in ents:
        for l in git(root, 'cat-file', 'blob', ents[p][1]).decode('utf-8', 'surrogateescape').split('\n'):
            if l.strip() and not l.startswith('#'):
                f = l.split('\t')
                if len(f) > col:
                    out[f[0]] = f
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', required=True)
    ap.add_argument('--base-rev', required=True)
    ap.add_argument('--require-rounds', default='26,27,28')
    a = ap.parse_args()
    for r in (a.rev, a.base_rev):
        if not re.fullmatch(r'[0-9a-f]{40}', r):
            raise SystemExit('COULD-NOT-EVALUATE revisions must be full 40-hex')
    ents = tree(a.root, a.rev, 'census', '.ufo/waves')
    base = tree(a.root, a.base_rev, 'census')
    mans = sorted(p for p in ents if re.fullmatch(r'census/round-\d+/waves/manifest\.sha256', p))
    tf = tu = tl = tfi = tfl = 0
    for m in mans:
        d = m[:-len('manifest.sha256')]
        rn = re.search(r'round-(\d+)', m).group(1)
        recs, bad = records(a.root, ents, m)
        failed = bad
        for name, h in recs.items():
            e = ents.get(d + name)
            if e is None or e[0] == '120000' or hashlib.sha256(git(a.root, 'cat-file', 'blob', e[1])).hexdigest() != h:
                failed += 1
        links = {k: v[1] for k, v in tsv_col(a.root, ents, d + 'symlinks.tsv', 1).items()}
        unc = 0
        for p, (mode, sha) in ents.items():
            if not p.startswith(d) or p == m:
                continue
            rel = p[len(d):]
            if rel in recs:
                continue
            if mode == '120000' and rel in links and git(a.root, 'cat-file', 'blob', sha).decode('utf-8', 'surrogateescape') == links[rel]:
                continue
            unc += 1
        lost = 0
        if m in base:
            brecs, _ = records(a.root, base, m)
            acct = set(tsv_col(a.root, ents, d + 'excluded.tsv')) | set(tsv_col(a.root, ents, d + 'renames.tsv'))
            lost = sum(1 for n in brecs if n not in recs and n not in acct)
        ren = {v[1]: v[0] for v in tsv_col(a.root, ents, d + 'renames.tsv', 1).values()}
        fid = 0
        for name, h in recs.items():
            src = ren.get(name, name)
            e = ents.get(f'.ufo/waves/round-{rn}/{src}')
            if e is not None and e[0] != '120000' and hashlib.sha256(git(a.root, 'cat-file', 'blob', e[1])).hexdigest() != h:
                fid += 1
        fl = 1 if len(recs) < FLOORS.get(rn, 1) else 0
        print(f'r{rn} records={len(recs)} failed={failed} uncovered={unc} lost={lost} fidelity={fid} floor_violation={fl}')
        tf += failed; tu += unc; tl += lost; tfi += fid; tfl += fl
    need = {r for r in a.require_rounds.split(',') if r} | set(FLOORS)
    tfl += len([r for r in need if f'census/round-{r}/waves/manifest.sha256' not in mans])
    def tool(rev):
        p = subprocess.run(['git', '-C', a.root, 'cat-file', 'blob', f'{rev}:{TOOL}'], capture_output=True)
        return p.stdout if p.returncode == 0 else b''
    tu_ = 1 if tool(a.rev) == tool(a.base_rev) else 0
    print(f'SUMMARY manifests={len(mans)} failed={tf} uncovered={tu} lost={tl} fidelity={tfi} floor_violations={tfl} tool_unchanged={tu_} rev={a.rev}')
    return 0 if (tf == tu == tl == tfi == tfl == tu_ == 0 and mans) else 1

if __name__ == '__main__':
    sys.exit(main())
