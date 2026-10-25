#!/usr/bin/env python3
"""souji-registry-agreement: declared-vs-observed agreement over COMMITTED bytes (r29 C1).

AMENDED v2 (r29, stricter-only; the frozen v1 bytes are blob b8cb4b31:tools/souji-registry-agreement.py,
sha256 51131fe7...; see census/round-29/records/amendments.txt). v2 never reads the stale list at the
measured revision: --list-rev is REQUIRED and is the prereg commit.

Two declared records are compared with what the committed tree at --rev shows:
  K1 registry<->entry: every `used-by` path of a SOURCES.md row must exist at REV and name the
     row id; every S### cited in the front-matter `source:` lines of a corpus/knowledge/*.md
     entry must be a row whose `used-by` lists that entry.
     v2 also flags a registry row id present at --list-rev and absent at REV (row-deleted), a row
     indented 4+ spaces or by a tab (indented-row, would be silently ignored), and reads `source:`
     lines of an entry to end of file, not only before the first heading.
  K2 stale statements: every row of the stale list (TSV: file<TAB>line<TAB>phrase) must be
     append-only by bytes (blob at REV starts with the blob at --list-rev), keep line `ln`
     byte-identical and unique, and carry after that line a line starting `R29-CORRECTION `
     that names the exact `file:line` tag, contains as delimited integers the r26 manifest
     `records=` and `failed=` values derived mechanically by running the digest-pinned frozen
     counter census/round-29/c2-counter.py at --list-rev (1382 and 152), and names at least one
     derivation-source path that resolves at REV.
Reads only `git cat-file`/`ls-tree`/`show`; never the working tree; never writes.
Exit 0 mismatches=0; 1 mismatches>0; 2 could-not-evaluate (usage, unresolvable rev, unparsable).
"""
import argparse, re, subprocess, sys

ROW = re.compile(r'^ {0,3}\|\s*(S\d{3,})\s*\|')

def git(root, *a, check=True):
    p = subprocess.run(['git', '-C', root, '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null', *a],
                       capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError('git ' + ' '.join(a) + ': ' + p.stderr.decode('utf-8', 'replace').strip())
    return p

def blob(root, rev, path):
    p = git(root, 'cat-file', 'blob', f'{rev}:{path}', check=False)
    return None if p.returncode else p.stdout.decode('utf-8', 'replace')

def norm(p):
    p = p.strip()
    while p.startswith('./'):
        p = p[2:]
    return p

INDENTED = re.compile(r'^(?: {4,}|\t+)\|\s*(S\d{3,})\s*\|')

def registry(root, rev, indented=None):
    t = blob(root, rev, 'corpus/SOURCES.md')
    if t is None:
        raise RuntimeError('corpus/SOURCES.md absent at rev')
    rows = {}
    for l in t.splitlines():
        m = INDENTED.match(l)
        if m and indented is not None:
            indented.append(m.group(1))
        if ROW.match(l):
            c = [x.strip() for x in l.split('|')]
            if len(c) != 13:
                raise RuntimeError('malformed registry row: ' + l[:60])
            rows[c[1]] = [norm(p) for p in re.split(r'[,;]', c[11]) if p.strip() and p.strip() != '—']
    return rows

def k1(root, rev, list_rev):
    indented = []
    rows = registry(root, rev, indented)
    out = []
    for i in sorted(set(indented)):
        out.append(f'K1 indented-row {i}')
    for i in sorted(registry(root, list_rev)):
        if i not in rows:
            out.append(f'K1 row-deleted {i}')
    for i, paths in sorted(rows.items()):
        for p in paths:
            t = blob(root, rev, p)
            if t is None:
                out.append(f'K1 used-by-missing {i} {p}')
            elif not re.search(r'\b' + i + r'\b', t):
                out.append(f'K1 used-by-no-cite {i} {p}')
    ls = git(root, 'ls-tree', '-r', '--name-only', rev, '--', 'corpus/knowledge/').stdout.decode().splitlines()
    for p in sorted(x for x in ls if x.endswith('.md') and x.count('/') == 2):
        t = blob(root, rev, p) or ''
        ids = set()
        for l in t.splitlines():
            if re.match(r'^(- )?source:', l):
                ids.update(re.findall(r'\bS\d{3,}\b', l))
        for i in sorted(ids):
            if i not in rows:
                out.append(f'K1 cited-no-row {i} {p}')
            elif p not in rows[i]:
                out.append(f'K1 cited-not-in-used-by {i} {p}')
    return out

def blobbytes(root, rev, path):
    p = git(root, 'cat-file', 'blob', f'{rev}:{path}', check=False)
    return None if p.returncode else p.stdout

def facts(root, list_rev):
    import hashlib
    pins = blob(root, list_rev, 'census/round-29/records/frozen-digests.txt') or ''
    pinned = {}
    for l in pins.splitlines():
        f = l.split()
        if len(f) == 2:
            pinned[f[1]] = f[0]
    src = blobbytes(root, list_rev, 'census/round-29/c2-counter.py')
    if src is None:
        raise RuntimeError('c2-counter.py unreadable at list_rev')
    if pinned.get('census/round-29/c2-counter.py') != hashlib.sha256(src).hexdigest():
        raise RuntimeError('c2-counter.py digest differs from the frozen pin')
    p = subprocess.run([sys.executable, '-B', '-', '--root', root, '--rev', list_rev], input=src, capture_output=True)
    for l in p.stdout.decode().splitlines():
        m = re.match(r'r26 records=(\d+) failed=(\d+)', l)
        if m:
            if m.group(2) == '0' or m.group(1) == '0':
                raise RuntimeError('derived facts are trivial')
            return m.group(2), m.group(1)
    raise RuntimeError('frozen counter produced no r26 line at list_rev')

def TAGCHK(path, ln):
    return re.compile(r'(?<![0-9A-Za-z._/-])' + re.escape(f'{path}:{ln}') + r'(?![0-9])')

def NUMTOK(n):
    return re.compile(r'(?<![0-9])' + re.escape(n) + r'(?![0-9])')

PATHTOK = re.compile(r'[A-Za-z0-9._][A-Za-z0-9._/-]*\.(?:tsv|txt|md|sha256|json|py)(?![A-Za-z0-9._/-])')
DERSRC = {'census/round-29/c2-counter.py', 'census/round-29/records/frozen-digests.txt',
          'census/round-26/waves/manifest.sha256'}

def k2(root, rev, list_rev, list_path):
    t = blob(root, list_rev, list_path)
    if t is None:
        raise RuntimeError(f'stale list {list_rev}:{list_path} unreadable')
    out = []
    absent = total = None
    for n, l in enumerate(t.splitlines(), 1):
        if not l.strip() or l.startswith('#'):
            continue
        f = l.split('\t')
        if len(f) != 3:
            raise RuntimeError(f'stale list line {n} not 3 TSV fields')
        path, ln, phrase = f[0], int(f[1]), f[2]
        if ln < 1:
            raise RuntimeError(f'stale list line {n} has non-positive line number')
        bb, rb = blobbytes(root, list_rev, path), blobbytes(root, rev, path)
        if bb is None:
            raise RuntimeError(f'stale list file {path} absent at list_rev')
        if rb is None:
            out.append(f'K2 file-missing {path}:{ln}')
            continue
        base_lines = bb.decode('utf-8', 'replace').splitlines()
        if ln > len(base_lines) or phrase not in base_lines[ln - 1]:
            raise RuntimeError(f'stale list phrase not at list_rev {path}:{ln}')
        want = base_lines[ln - 1]
        if absent is None:
            absent, total = facts(root, list_rev)
        if not rb.startswith(bb):
            out.append(f'K2 rewrote-not-appended {path}')
        lines = rb.decode('utf-8', 'replace').splitlines()
        if ln > len(lines) or lines[ln - 1] != want:
            out.append(f'K2 statement-moved-or-edited {path}:{ln}')
            continue
        if sum(1 for x in lines if x == want) != 1:
            out.append(f'K2 statement-duplicated {path}:{ln}')
            continue
        if not any(x.startswith('R29-CORRECTION ') and TAGCHK(path, ln).search(x)
                   and NUMTOK(absent).search(x) and NUMTOK(total).search(x)
                   and any(c in DERSRC and blob(root, rev, c) is not None for c in PATHTOK.findall(x))
                   for x in lines[ln:]):
            out.append(f'K2 uncorrected-or-unevidenced {path}:{ln}')
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', required=True)
    ap.add_argument('--list-rev', required=True, help='prereg commit: stale list, frozen digests and the base registry are read here')
    ap.add_argument('--stale-list', default='census/round-29/stale-statements.tsv')
    a = ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', a.rev):
        print('COULD-NOT-EVALUATE rev must be a full 40-hex revision', file=sys.stderr)
        return 2
    try:
        git(a.root, 'cat-file', '-e', a.rev + '^{commit}')
        f1 = k1(a.root, a.rev, a.list_rev)
        f2 = k2(a.root, a.rev, a.list_rev, a.stale_list)
    except (RuntimeError, ValueError) as e:
        print('COULD-NOT-EVALUATE ' + str(e), file=sys.stderr)
        return 2
    for x in f1 + f2:
        print(x)
    print(f'SUMMARY k1={len(f1)} k2={len(f2)} mismatches={len(f1) + len(f2)} rev={a.rev}')
    return 1 if f1 or f2 else 0

if __name__ == '__main__':
    sys.exit(main())
