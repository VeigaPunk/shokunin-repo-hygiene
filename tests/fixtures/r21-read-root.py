#!/usr/bin/env python3
"""Synthetic, independently specified V-READ-ROOT expectations (r21 C1)."""
import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path
sys.dont_write_bytecode = True
FLEET = '/home/vgpnk/Projects/shokunin'
LANE = FLEET + '/souji-shokunin'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool', required=True)
    p.add_argument('--base-tool', required=True)
    a = p.parse_args()
    if hashlib.sha256(Path(a.base_tool).read_bytes()).hexdigest() != 'b2fa68e2e98dae9d046c11775737337fb99b0db94fb5042017e4c8a56fc83389':
        print('read-root: --base-tool must match the exact 6ff3413 auditor', file=sys.stderr)
        return 2
    tool, base = load(a.tool, 'changed'), load(a.base_tool, 'baseline')
    # Expectations are literal, not computed by the implementation predicate.
    cases = [
        ('relative-read', 'read', 'corpus/QUALITY.md', True),
        ('relative-range', 'read', 'corpus/x.md:2-4', True),
        ('relative-raw', 'read', '.ufo/x.md:raw:2-4', True),
        ('relative-comma', 'read', 'corpus/x.md:2,9:raw', True),
        ('implicit-grep', 'grep', 'a pattern', True),
        ('relative-grep', 'grep', 'pattern @ corpus/lessons', True),
        ('relative-glob', 'glob', '**/*.py', True),
        ('dot-glob', 'glob', '.', True),
        ('semicolon', 'grep', 'pattern @ ' + LANE + '/x;corpus/x', True),
        ('escape-read', 'read', 'souji-shokunin/../x', True),
        ('parent-read', 'read', '../x', True),
        ('dot-read', 'read', '.', True),
        ('attempt-error', 'read', 'corpus/x', True),
        ('lane-relative', 'read', 'souji-shokunin/tools/x.py', False),
        ('lane-relative-range', 'read', 'souji-shokunin/tools/x.py:3-5:raw', False),
        ('lane-normalized', 'glob', 'souji-shokunin/x/../tools/*.py', False),
        ('absolute-lane', 'read', LANE + '/tools/x.py', False),
        ('absolute-fleet', 'read', FLEET + '/AXES.md', False),
        ('absolute-scratch', 'glob', '/var/tmp/souji-r21-X/*', False),
        ('home', 'read', '~/x', False),
        ('skill', 'read', 'skill://godspeed', False),
        ('agent', 'read', 'agent://A', False),
        ('artifact', 'grep', 'pattern @ artifact://4', False),
        ('https', 'read', 'https://example.org/a', False),
        ('uri-plus', 'glob', 'scheme+v1://x', False),
        ('truncated-grep', 'grep', 'pattern…', False),
        ('truncated-relative', 'read', 'corpus/lo…', False),
        ('truncated-target', 'grep', 'pattern @ corpus/lo…', False),
        ('truncated-pattern-visible-target', 'grep', 'pat… @ corpus/x', True),
        ('absolute-root-control', 'read', LANE, False),
        ('forbidden-control', 'read', LANE + '/census/operator-sweep-20261019/x', False),
        ('historical-renderer', 'grep', 'pattern in ' + LANE, False),
    ]
    failed = discriminating = 0
    for name, kind, args, expected in cases:
        status = 'error' if name == 'attempt-error' else 'ok'
        text = f'→ {kind}({args}) ⇒ {status}'
        def rows(mod):
            return mod.audit_seat(text, 'scout', LANE + '/report.md', [], LANE, FLEET)[1]
        now, old = rows(tool), rows(base)
        actual = any(r['class'] == 'V-READ-ROOT' for r in now)
        old_actual = any(r['class'] == 'V-READ-ROOT' for r in old)
        preserved = [(r['class'], r['severity']) for r in now if r['class'] != 'V-READ-ROOT'] == [(r['class'], r['severity']) for r in old]
        ok = actual == expected and preserved and all(r['severity'] == 'minor' for r in now if r['class'] == 'V-READ-ROOT')
        discriminating += old_actual != expected
        failed += not ok
        print('CASE\t%s\t%s\texpected=%s observed=%s preserved=%s' % ('pass' if ok else 'FAIL', name, expected, actual, preserved))
    print(f'SUMMARY\ttotal={len(cases)}\tpass={len(cases)-failed}\tfail={failed}\tbase_discriminating={discriminating}')
    return int(bool(failed))


if __name__ == '__main__':
    raise SystemExit(main())
