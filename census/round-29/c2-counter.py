#!/usr/bin/env python3
"""r29 C2 frozen counter: do committed wave-evidence manifests verify over COMMITTED bytes?

For every `census/round-<N>/waves/manifest.sha256` present at --rev (enumerated by ls-tree):
  failed    = manifest records whose path is absent from the committed tree or whose committed
              blob sha256 differs (GNU `\\`-escaped records decoded; never the working tree).
  uncovered = committed regular-file or symlink paths under that waves dir, other than
              `manifest.sha256` itself, with no manifest record and not listed in the committed
              `census/round-<N>/waves/symlinks.tsv` (col1 = path relative to the waves dir,
              col2 = link target; the committed symlink blob must equal col2).
Floors: a manifest may not hold fewer records than FLOORS (r26 1230, r27 124, r28 75) and those three must exist.
Prints one line per round and SUMMARY. Exit 0 failed=0 uncovered=0 floor_violations=0 manifests>=1; 1 otherwise.
"""
import argparse, hashlib, re, subprocess, sys

def git(root, *a, inp=None):
    p = subprocess.run(['git', '-C', root, '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null', *a],
                       capture_output=True, input=inp)
    if p.returncode:
        raise SystemExit('COULD-NOT-EVALUATE git ' + ' '.join(a) + ': ' + p.stderr.decode('utf-8', 'replace'))
    return p.stdout

FLOORS = {'26': 1230, '27': 124, '28': 75}  # frozen: base-verifying record counts a manifest may not drop below

def unescape(s):
    return re.sub(r'\\([\\n])', lambda m: '\n' if m.group(1) == 'n' else '\\', s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', required=True)
    a = ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', a.rev):
        raise SystemExit('COULD-NOT-EVALUATE rev must be a full 40-hex revision')
    ents = {}
    for rec in git(a.root, 'ls-tree', '-r', '-z', a.rev, '--', 'census').split(b'\0'):
        if not rec:
            continue
        meta, path = rec.split(b'\t', 1)
        mode, typ, sha = meta.decode().split()
        ents[path.decode('utf-8', 'surrogateescape')] = (mode, sha)
    mans = sorted(p for p in ents if re.fullmatch(r'census/round-\d+/waves/manifest\.sha256', p))
    tf = tu = tfl = 0
    for m in mans:
        d = m[:-len('manifest.sha256')]
        rn = re.search(r'round-(\d+)', m).group(1)
        text = git(a.root, 'cat-file', 'blob', ents[m][1]).decode('utf-8', 'surrogateescape')
        recs = {}
        bad = 0
        for l in text.split('\n'):
            if not l:
                continue
            esc = l.startswith('\\')
            mm = re.match(r'^([0-9a-f]{64})  (.*)$', l[1:] if esc else l)
            if not mm:
                bad += 1
                continue
            name = mm.group(2)
            if esc:
                name = unescape(name)
            if name.startswith('./'):
                name = name[2:]
            recs[name] = mm.group(1)
        failed = bad
        for name, h in recs.items():
            e = ents.get(d + name)
            if e is None or e[0] == '120000':
                failed += 1
                continue
            if hashlib.sha256(git(a.root, 'cat-file', 'blob', e[1])).hexdigest() != h:
                failed += 1
        links = {}
        lt = d + 'symlinks.tsv'
        if lt in ents:
            for l in git(a.root, 'cat-file', 'blob', ents[lt][1]).decode('utf-8', 'surrogateescape').split('\n'):
                if l.strip() and not l.startswith('#'):
                    f = l.split('\t')
                    if len(f) >= 2:
                        links[f[0]] = f[1]
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
        fl = 1 if len(recs) < FLOORS.get(rn, 1) else 0
        print(f'r{rn} records={len(recs)} failed={failed} uncovered={unc} floor_violation={fl}')
        tf += failed
        tu += unc
        tfl += fl
    missing = [r for r in FLOORS if f'census/round-{r}/waves/manifest.sha256' not in mans]
    tfl += len(missing)
    print(f'SUMMARY manifests={len(mans)} failed={tf} uncovered={tu} floor_violations={tfl} rev={a.rev}')
    return 0 if (tf == 0 and tu == 0 and tfl == 0 and mans) else 1

if __name__ == '__main__':
    sys.exit(main())
