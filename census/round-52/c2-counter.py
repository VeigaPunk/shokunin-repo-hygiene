#!/usr/bin/env python3
"""C2 counter (souji round 52): committed fleet-root census capture verifies.

Frozen predicate: census/round-52/preregistration.txt, claim C2.
Reads ONLY committed bytes at --rev: the capture census/round-52/records/fleet-root-census.tsv
and the tool tools/souji-fleet-root-census.py. Verifies:
  - header: TOOL_SHA256 equals sha256 of the tool's bytes at --rev; FLEET_HEAD is 40-hex;
    ENTRIES equals the data-row count; one COUNT line per class with the recomputed count.
  - every data row: 6 tab-separated fields, unique name without '/', name != '.git',
    kind/tracked/ignored in the frozen enumerations, class recomputed by the frozen rule,
    disposition exactly 'report-only' for untracked-stray and 'none' otherwise.
  - removal_proposed: rows whose disposition is anything else (must be 0).
Frozen class rule (first match wins): kind=symlink -> symlink; tracked=yes -> tracked;
ignored=yes -> ignored; otherwise untracked-stray.

Exit 0: all checks hold and ENTRIES >= 1.
Exit 1: any check fails, or the capture is absent (PRISTINE FAIL).
Exit 2: could-not-evaluate (bad revision, tool absent at rev).
Writes nothing; scratch argument accepted for interface uniformity.
"""
import argparse, hashlib, os, re, subprocess, sys
from pathlib import Path

CAPTURE = 'census/round-52/records/fleet-root-census.tsv'
TOOL = 'tools/souji-fleet-root-census.py'
HEADER = ['name', 'kind', 'tracked', 'ignored', 'class', 'disposition']
KINDS = {'file', 'dir', 'symlink', 'other'}
CLASSES = ['tracked', 'ignored', 'untracked-stray', 'symlink']
HEX64 = re.compile(r'[0-9a-f]{64}')
HEX40 = re.compile(r'[0-9a-f]{40}')


def git_show_bytes(root, rev, path):
    e = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
         'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
         'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
         'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1'}
    p = subprocess.run(['git', '-C', str(root), 'show', '%s:%s' % (rev, path)],
                       capture_output=True, env=e, timeout=120)
    return p.stdout if p.returncode == 0 else None


def frozen_class(kind, tracked, ignored):
    if kind == 'symlink':
        return 'symlink'
    if tracked == 'yes':
        return 'tracked'
    if ignored == 'yes':
        return 'ignored'
    return 'untracked-stray'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', required=True)
    ap.add_argument('--scratch', default=None, help='accepted for interface uniformity; nothing is written')
    ns = ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', ns.rev):
        print('CANNOT-EVALUATE full 40-hex revision required')
        return 2
    root = Path(ns.root).resolve()

    cap = git_show_bytes(root, ns.rev, CAPTURE)
    if cap is None:
        print('PRISTINE FAIL FLEET-CENSUS-ABSENT %s:%s' % (ns.rev[:12], CAPTURE))
        return 1
    tool = git_show_bytes(root, ns.rev, TOOL)
    if tool is None:
        print('CANNOT-EVALUATE tool absent at rev: %s' % TOOL)
        return 2
    tool_sha = hashlib.sha256(tool).hexdigest()

    problems = []
    lines = cap.decode('utf-8', 'replace').split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    header_kv, counts_decl, rows, body_header_seen = {}, {}, [], False
    for ln in lines:
        if ln.startswith('#'):
            m = re.fullmatch(r'# (TOOL_SHA256|FLEET_HEAD|ENTRIES)=(\S+)', ln)
            if m:
                if m.group(1) in header_kv:
                    problems.append('duplicate header %s' % m.group(1))
                header_kv[m.group(1)] = m.group(2)
                continue
            m = re.fullmatch(r'# COUNT (\S+)=(\d+)', ln)
            if m:
                if m.group(1) in counts_decl:
                    problems.append('duplicate COUNT %s' % m.group(1))
                counts_decl[m.group(1)] = int(m.group(2))
                continue
            continue  # free-form scope comment
        if not body_header_seen:
            if ln.split('\t') != HEADER:
                problems.append('column header mismatch')
            body_header_seen = True
            continue
        f = ln.split('\t')
        if len(f) != 6:
            problems.append('row field count %d: %r' % (len(f), ln[:60]))
            continue
        rows.append(f)

    for k in ('TOOL_SHA256', 'FLEET_HEAD', 'ENTRIES'):
        if k not in header_kv:
            problems.append('missing header %s' % k)
    tool_ok = header_kv.get('TOOL_SHA256') == tool_sha
    if not tool_ok:
        problems.append('TOOL_SHA256 %s != tool bytes %s' % (header_kv.get('TOOL_SHA256'), tool_sha))
    if not HEX40.fullmatch(header_kv.get('FLEET_HEAD', '')):
        problems.append('FLEET_HEAD not 40-hex')
    if not HEX64.fullmatch(header_kv.get('TOOL_SHA256', '')):
        problems.append('TOOL_SHA256 not 64-hex')

    names, class_mismatch, unclassified, removal_proposed = set(), 0, 0, 0
    recount = {c: 0 for c in CLASSES}
    for f in rows:
        name, kind, tracked, ignored, cls, disp = f
        if not name or '/' in name or name == '.git' or name in names:
            problems.append('bad or duplicate name %r' % name)
            unclassified += 1
            continue
        names.add(name)
        if kind not in KINDS or tracked not in ('yes', 'no') or ignored not in ('yes', 'no'):
            problems.append('enumeration violation for %r' % name)
            unclassified += 1
            continue
        want = frozen_class(kind, tracked, ignored)
        if cls not in CLASSES:
            unclassified += 1
        if cls != want:
            class_mismatch += 1
            problems.append('class %r want %r for %r' % (cls, want, name))
        want_disp = 'report-only' if want == 'untracked-stray' else 'none'
        if disp != want_disp:
            removal_proposed += 1
            problems.append('disposition %r for %r' % (disp, name))
        if cls in recount:
            recount[cls] += 1

    entries = len(rows)
    if 'ENTRIES' in header_kv and header_kv['ENTRIES'] != str(entries):
        problems.append('ENTRIES %s != rows %d' % (header_kv['ENTRIES'], entries))
    if entries < 1:
        problems.append('ENTRIES < 1 (empty capture is not a census)')
    for c in CLASSES:
        if counts_decl.get(c) != recount[c]:
            problems.append('COUNT %s declared %s recomputed %d' % (c, counts_decl.get(c), recount[c]))
    if set(counts_decl) != set(CLASSES):
        problems.append('COUNT class set %s != %s' % (sorted(counts_decl), sorted(CLASSES)))

    for p in problems[:20]:
        print('FINDING %s' % p)
    ok = not problems
    print('SUMMARY entries=%d rows=%d unclassified=%d class_mismatch=%d counts=%s tool_sha=%s '
          'removal_proposed=%d receipt=%s rev=%s'
          % (entries, len(rows), unclassified, class_mismatch,
             'ok' if all(counts_decl.get(c) == recount[c] for c in CLASSES) else 'FAIL',
             'ok' if tool_ok else 'FAIL', removal_proposed,
             'ok' if ok else 'FAIL', ns.rev[:12]))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
