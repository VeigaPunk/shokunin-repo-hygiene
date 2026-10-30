import ast
from collections import Counter
import json
from pathlib import Path
import sys
from types import SimpleNamespace

out = Path(__file__).resolve().parent
tree = ast.parse((out / 'frozen-c2-hidden-audit.py').read_text())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'classes')
ns = {}
exec(compile(ast.Module(body=[fn], type_ignores=[]), '<frozen classes-only>', 'exec'), ns)
sc = next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SCENARIOS' for t in n.targets))
want = ast.literal_eval(sc.elts[3].elts[3])
def parsed(items):
    data = '\n'.join('FINDING ' + value.replace(':', ' ', 1) + ' detail' for value in items).encode()
    return ns['classes'](SimpleNamespace(stdout=data))
cases = {'reordered': list(reversed(want)), 'one_missing': want[:-1], 'one_extra': want + [want[-1]], 'literal_star': [v for v in want if v != 'C2:FIELD-MISSING'] + ['C2:FIELD-MISSING*4']}
results = {key: {'sorted_equality': parsed(value) == sorted(want), 'counter_equality': Counter(parsed(value)) == Counter(want)} for key, value in cases.items()}
print(json.dumps({'python': sys.version, 'method': 'AST-extract frozen classes only and h4 want literal; no audit main/build/run invoked', 'expected_counts': dict(Counter(want)), 'cases': results}, indent=2))
