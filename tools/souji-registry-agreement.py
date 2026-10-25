#!/usr/bin/env python3
"""souji-registry-agreement: declared-vs-observed agreement over COMMITTED bytes (r29 C1).

Two declared records are compared with what the committed tree at --rev shows:
  K1 registry<->entry: every `used-by` path of a SOURCES.md row must exist at REV and name the
     row id; every S### cited in the front-matter `source:` lines of a corpus/knowledge/*.md
     entry must be a row whose `used-by` lists that entry.
  K2 stale statements: every row of the stale list (TSV: file<TAB>line<TAB>phrase) must still
     carry the phrase at file:line at REV (append-only: an in-place edit is a mismatch) and the
     same file must carry, after that line, a line starting `R29-CORRECTION ` that names
     `file:line`.
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

def registry(root, rev):
    t = blob(root, rev, 'corpus/SOURCES.md')
    if t is None:
        raise RuntimeError('corpus/SOURCES.md absent at rev')
    rows = {}
    for l in t.splitlines():
        if ROW.match(l):
            c = [x.strip() for x in l.split('|')]
            if len(c) != 13:
                raise RuntimeError('malformed registry row: ' + l[:60])
            rows[c[1]] = [norm(p) for p in re.split(r'[,;]', c[11]) if p.strip() and p.strip() != '—']
    return rows

def k1(root, rev):
    rows = registry(root, rev)
    out = []
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
            if re.match(r'^#\s', l):
                break
            if re.match(r'^(- )?source:', l):
                ids.update(re.findall(r'\bS\d{3,}\b', l))
        for i in sorted(ids):
            if i not in rows:
                out.append(f'K1 cited-no-row {i} {p}')
            elif p not in rows[i]:
                out.append(f'K1 cited-not-in-used-by {i} {p}')
    return out

def k2(root, rev, list_rev, list_path):
    t = blob(root, list_rev, list_path)
    if t is None:
        raise RuntimeError(f'stale list {list_rev}:{list_path} unreadable')
    out = []
    for n, l in enumerate(t.splitlines(), 1):
        if not l.strip() or l.startswith('#'):
            continue
        f = l.split('\t')
        if len(f) != 3:
            raise RuntimeError(f'stale list line {n} not 3 TSV fields')
        path, ln, phrase = f[0], int(f[1]), f[2]
        body = blob(root, rev, path)
        if body is None:
            out.append(f'K2 file-missing {path}:{ln}')
            continue
        lines = body.splitlines()
        if ln > len(lines) or phrase not in lines[ln - 1]:
            out.append(f'K2 phrase-moved-or-edited {path}:{ln}')
            continue
        tag = f'{path}:{ln}'
        if not any(x.startswith('R29-CORRECTION ') and tag in x for x in lines[ln:]):
            out.append(f'K2 uncorrected {tag}')
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', required=True)
    ap.add_argument('--list-rev', help='revision to read the stale list from (default: --rev)')
    ap.add_argument('--stale-list', default='census/round-29/stale-statements.tsv')
    a = ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', a.rev):
        print('COULD-NOT-EVALUATE rev must be a full 40-hex revision', file=sys.stderr)
        return 2
    try:
        git(a.root, 'cat-file', '-e', a.rev + '^{commit}')
        f1 = k1(a.root, a.rev)
        f2 = k2(a.root, a.rev, a.list_rev or a.rev, a.stale_list)
    except (RuntimeError, ValueError) as e:
        print('COULD-NOT-EVALUATE ' + str(e), file=sys.stderr)
        return 2
    for x in f1 + f2:
        print(x)
    print(f'SUMMARY k1={len(f1)} k2={len(f2)} mismatches={len(f1) + len(f2)} rev={a.rev}')
    return 1 if f1 or f2 else 0

if __name__ == '__main__':
    sys.exit(main())
