#!/usr/bin/env python3
"""Synthetic output-boundary oracle for the clone replay runner; no live surfaces."""
import argparse
import importlib.util
from pathlib import Path
import sys
import tempfile
sys.dont_write_bytecode = True


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
    current, base = load(a.tool, 'r21_current'), load(a.base_tool, 'r21_before')
    cases = []
    with tempfile.TemporaryDirectory(prefix='souji-r21-replay-bounds-', dir='/var/tmp') as temp:
        top = Path(temp)
        source = top / 'source'
        source.mkdir()
        (source / '.git').mkdir()
        (top / 'actual').mkdir()
        (top / 'parent-link').symlink_to(top / 'actual', target_is_directory=True)
        (top / 'actual' / 'child').mkdir()
        existing = top / 'existing.json'
        existing.write_text('preserve')
        for name, target, expected in [
            ('source-root', source / 'new.json', False),
            ('source-git', source / '.git' / 'new.json', False),
            ('relative', Path('new.json'), False),
            ('outside', top / 'new.json', True),
            ('existing', existing, False),
            ('parent-symlink', top / 'parent-link' / 'new.json', False),
            ('ancestor-symlink', top / 'parent-link' / 'child' / 'new.json', False),
            ('missing-parent', top / 'missing' / 'new.json', False),
        ]:
            def accepted(module):
                try:
                    module.output_path(str(target), source)
                    return True
                except (OSError, ValueError, RuntimeError):
                    return False
            observed, before = accepted(current), accepted(base)
            ok = observed == expected
            cases.append((name, ok, before != expected))
            print(f'CASE\t{"pass" if ok else "FAIL"}\t{name}\texpected={expected}\tactual={observed}\tbase={before}')
        assert existing.read_text() == 'preserve'
        assert not (source / 'new.json').exists()
    failed = sum(not ok for _, ok, _ in cases)
    discriminating = sum(d for _, _, d in cases)
    print(f'SUMMARY\ttotal={len(cases)}\tpass={len(cases)-failed}\tfail={failed}\tbase_discriminating={discriminating}')
    return int(bool(failed))


if __name__ == '__main__':
    raise SystemExit(main())
