#!/usr/bin/env python3
"""Review-routed no-overreach controls: URI case and documented read selectors."""
import argparse
import importlib.util
import sys
sys.dont_write_bytecode = True
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--tool', required=True)
a = p.parse_args()
s = importlib.util.spec_from_file_location('audit', a.tool)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
fleet = '/home/vgpnk/Projects/shokunin'
lane = fleet + '/souji-shokunin'
cases = [('uri-mixed', 'Skill://godspeed'), ('uri-upper', 'HTTPS://example.org/x'),
         ('conflicts', 'souji-shokunin:conflicts'), ('raw-conflicts', 'souji-shokunin:raw:conflicts')]
failed = 0
for name, target in cases:
    _, rows = m.audit_seat(f'→ read({target}) ⇒ ok', 'scout', '', [], lane, fleet)
    ok = not any(r['class'] == 'V-READ-ROOT' for r in rows)
    failed += not ok
    print(f'CASE\t{"pass" if ok else "FAIL"}\t{name}')
print(f'SUMMARY\ttotal=4\tpass={4-failed}\tfail={failed}')
raise SystemExit(int(bool(failed)))
