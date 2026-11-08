#!/usr/bin/env python3
"""S86ScoutShapes: shape census for NF-W and NF-Y, worktree + committed HEAD."""
import os, re, subprocess, hashlib, sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
OWNTREE_WAVE = re.compile(r'^(?:w[0-9]+|a2w1|assimilation)$')
CAPTURE = re.compile(r'^(?:waves/|wave/|records/wave-[^/]+/)(.+)$')

def wt_files():
    s = {}
    for root in ('census', '.ufo/waves'):
        for dp, ds, fs in os.walk(os.path.join(LANE, root)):
            ds[:] = [x for x in ds if x != '__pycache__']
            for f in fs:
                fp = os.path.join(dp, f)
                if os.path.islink(fp) or not os.path.isfile(fp):
                    continue
                rel = os.path.relpath(fp, LANE)
                s[rel] = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
    return s

def cm_files():
    s = {}
    out = subprocess.run(['git', '-C', LANE, 'ls-tree', '-r', 'HEAD', '--', 'census/', '.ufo/waves/'],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        meta, p = line.split('\t', 1)
        mode, typ, oid = meta.split()
        if typ != 'blob':
            continue
        data = subprocess.run(['git', '-C', LANE, 'cat-file', 'blob', oid], capture_output=True).stdout
        s[p] = hashlib.sha256(data).hexdigest()
    return s

def census(d, label, out):
    files = set(d)
    print(f"=== {label} : {len(files)} files under census/ + .ufo/waves/ ===", file=out)

    # --- census/round-N immediate children, by kind ---
    kids = {}
    for p in files:
        parts = p.split('/')
        if len(parts) >= 3 and parts[0] == 'census' and parts[1].startswith('round-'):
            kids.setdefault(parts[1], set()).add(parts[2])
    kinds = {}
    for r, ks in kids.items():
        for k in ks:
            kinds.setdefault(k, []).append(r)
    print("  census/round-<N> immediate child names (count of rounds holding it):", file=out)
    for k in sorted(kinds, key=lambda x: (-len(kinds[x]), x)):
        print(f"    {k}\t{len(kinds[k])}\t{','.join(sorted(kinds[k], key=lambda s:int(s.split('-')[1])))}", file=out)

    # --- .ufo/waves/round-N immediate children, by kind ---
    wkids = {}
    for p in files:
        parts = p.split('/')
        if len(parts) >= 3 and parts[0] == '.ufo' and parts[1] == 'waves':
            wkids.setdefault(parts[2], set()).add(parts[3])
    wkinds = {}
    for r, ks in wkids.items():
        for k in ks:
            wkinds.setdefault(k, []).append(r)
    print("  .ufo/waves/round-<N> immediate child names (count of rounds holding it):", file=out)
    for k in sorted(wkids, key=lambda x: (-len(wkids[x]), x)):
        print(f"    {k}\t{len(wkids[k])}\t{','.join(sorted(wkids[k]))}", file=out)

    # --- NF-W shape: token census/round-N/<A>/<rest...> (>=2 comps below round),
    #     target census/round-N/<wdir>/<rest...> where wdir in OWNTREE_WAVE and rest identical.
    nfw = []
    for p in files:
        parts = p.split('/')
        if len(parts) < 4 or parts[0] != 'census' or not parts[1].startswith('round-'):
            continue
        if not OWNTREE_WAVE.match(parts[2]):
            continue
        rest = parts[3:]
        for q in files:
            qp = q.split('/')
            if len(qp) != len(parts) or qp[:2] != parts[:2] or qp[2] == parts[2]:
                continue
            if qp[3:] != rest:
                continue
            nfw.append((q, p, d.get(q) == d.get(p)))
    print(f"  NF-W shape instances (census token -> same-round wave-dir landing, identical tail): {len(nfw)}", file=out)
    for a, b, be in sorted(nfw):
        print(f"    TOKEN {a} -> LANDING {b}  byte_equal={be}", file=out)

    # --- NF-Y shape: token census/round-N/<file> EXACTLY one component below its round;
    #     target census/round-N/<capture>/<file> where capture is waves/ wave/ records/wave-*/
    nfy = []
    for p in files:
        parts = p.split('/')
        if len(parts) != 4 or parts[0] != 'census' or not parts[1].startswith('round-'):
            continue
        if parts[2] not in ('waves', 'wave') and not (parts[2] == 'records' and parts[3].startswith('wave-')):
            continue
        tok = '/'.join(parts[:2] + [parts[-1]])
        if tok in files:
            nfy.append((tok, p, d.get(tok) == d.get(p)))
    print(f"  NF-Y shape instances (one-component census token -> same-round wave-capture landing): {len(nfy)}", file=out)
    for a, b, be in sorted(nfy):
        print(f"    TOKEN {a} -> LANDING {b}  byte_equal={be}", file=out)
    print(file=out)

with open(sys.argv[1], 'w') as out:
    census(wt_files(), 'WORKTREE (lane working tree)', out)
    census(cm_files(), 'COMMITTED HEAD (2acbbfc8)', out)
