#!/usr/bin/env python3
"""Round22 L1 mutation-adequacy probe for the r22 result oracle.

Each mutant is one literal source replacement in census/round-21/run-acceptance.py,
compiled IN MEMORY (no file written) and graded by the unchanged
tests/fixtures/r22-result-oracle.py. Prints one JSON receipt on stdout.
0: pristine runner passes and every mutant marked expect=killed is killed;
1: otherwise; 2: bad input (a replacement anchor is missing or ambiguous).
--grade-stdin grades runner source read from stdin (e.g. `git show <rev>:<path>`)
in memory and prints the ordinary oracle receipt; exit codes follow the oracle.
--oracle FILE (first) grades against alternate oracle bytes, e.g. a historical
revision of tests/fixtures/r22-result-oracle.json exported by the caller.
No subprocess, scanner, /proc, private snapshot, or file write.
"""
from __future__ import annotations
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import types
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / 'census/round-21/run-acceptance.py'
ORACLE_PY = ROOT / 'tests/fixtures/r22-result-oracle.py'

RE = 'except (ValueError, TypeError, RecursionError):'
RE_OLD = 'except (ValueError, TypeError):'

# id, origin (r22-changed clause | pre-existing clause), expect, old, new, occurrence
MUTANTS = [
    ('summary-stderr', 'r22-changed', 'killed',
     'and pass_match and not stderr', 'and pass_match', None),
    ('json-exact-type', 'r22-changed', 'killed',
     '    if type(observed) is not type(expected):\n        return False\n', '', None),
    ('json-exact-dict-keys', 'r22-changed', 'killed',
     'return (observed.keys() == expected.keys()\n', 'return (True\n', None),
    ('json-exact-list-len', 'r22-changed', 'killed',
     'return (len(observed) == len(expected)\n', 'return (True\n', None),
    ('exact-json-to-eq', 'r22-changed', 'killed',
     'json_match = json_exact(observed, expected)', 'json_match = observed == expected', None),
    ('nonexact-to-eq', 'r22-changed', 'killed',
     'key in observed and json_exact(observed[key], value)', 'observed.get(key) == value', None),
    ('nonexact-keyin-get', 'r22-changed', 'equivalent',
     'key in observed and json_exact(observed[key], value)',
     'json_exact(observed.get(key), value)', None),
    ('producer-exec-to-eq', 'r22-changed', 'killed',
     'json_exact(payload.get("producer_executions_new_policy"),\n'
     '                           expected["producer_executions_new_policy"])',
     'payload.get("producer_executions_new_policy") == expected["producer_executions_new_policy"]', None),
    ('failed-checks-to-eq', 'r22-changed', 'equivalent',
     'json_exact(payload.get("failed_checks"), expected["failed_checks"])',
     'payload.get("failed_checks") == expected["failed_checks"]', None),
    ('cache-names', 'r22-changed', 'killed',
     '            and checks.keys() == CACHE_CHECK_NAMES\n', '', None),
    ('cache-phases', 'r22-changed', 'killed',
     '            and case_phases == list(CACHE_CASE_PHASES)\n', '', None),
    ('names-len-constant', 'r22-changed', 'equivalent',
     '            and len(CACHE_CHECK_NAMES) == expected["checks"]\n', '', None),
    ('phases-len-constant', 'r22-changed', 'equivalent',
     '            and len(CACHE_CASE_PHASES) == expected["cases"]\n', '', None),
    ('gate-isinstance', 'r22-changed', 'killed',
     'and isinstance(gate, dict) and gate.get', 'and gate.get', None),
    ('isolation-isinstance', 'r22-changed', 'killed',
     '            and isinstance(isolation, dict)\n', '', None),
    ('baseline-int-guard', 'r22-changed', 'killed',
     '                except ValueError:\n                    summary_match = False\n',
     '                except ValueError:\n                    raise\n', None),
    ('counter-recursion', 'r22-changed', 'killed', RE, RE_OLD, 0),
    ('cache-recursion', 'r22-changed', 'killed', RE, RE_OLD, 1),
    ('summary-last-only', 'pre-existing', 'killed',
     'summary_match = summary_lines == ([expected] if expected else [])',
     'summary_match = summary_lines[-1:] == ([expected] if expected else [])', None),
    ('counter-stderr', 'pre-existing', 'killed',
     'matched = matched and json_match and not stderr', 'matched = matched and json_match', None),
    ('cache-stderr', 'pre-existing', 'killed',
     'matched = matched and demo_match and not stderr', 'matched = matched and demo_match', None),
    ('gate-sha', 'pre-existing', 'killed',
     'and isinstance(gate, dict) and gate.get("sha256") == gate_sha', 'and isinstance(gate, dict)', None),
    ('isolation-cleaned-drop', 'pre-existing', 'killed',
     '            and isolation.get("cleaned") is expected["isolation_cleaned"]\n', '', None),
    ('isolation-cleaned-eq', 'pre-existing', 'killed',
     'isolation.get("cleaned") is expected', 'isolation.get("cleaned") == expected', None),
    ('isolation-residue', 'pre-existing', 'killed',
     '            and isolation.get("residue") == []\n', '', None),
]


def mutate(src, old, new, occurrence):
    count = src.count(old)
    if occurrence is None:
        if count != 1:
            raise ValueError(f'anchor count {count}: {old!r}')
        return src.replace(old, new)
    parts = src.split(old)
    if len(parts) - 1 <= occurrence:
        raise ValueError(f'anchor occurrence {occurrence} missing: {old!r}')
    return old.join(parts[:occurrence + 1]) + new + old.join(parts[occurrence + 1:])


def grade(oracle_mod, source):
    def load_runner(_path):
        name = 'souji_r22_mutant'
        module = types.ModuleType(name)
        module.__file__ = str(RUNNER)
        sys.modules[name] = module
        exec(compile(source, '<r22-mutant>', 'exec'), module.__dict__)
        return module
    oracle_mod.load_runner = load_runner
    out = io.StringIO()
    argv = sys.argv
    sys.argv = ['r22-result-oracle.py', '--runner', str(RUNNER)]
    try:
        with contextlib.redirect_stdout(out):
            code = oracle_mod.main()
    finally:
        sys.argv = argv
    receipt = json.loads(out.getvalue())
    return code, receipt


def main():
    spec = importlib.util.spec_from_file_location('souji_r22_oracle', ORACLE_PY)
    oracle_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle_mod)
    args = sys.argv[1:]
    if args[:1] == ['--oracle'] and len(args) >= 2:
        # Alternate oracle bytes, e.g. a historical revision exported by the caller.
        oracle_mod.ORACLE = Path(args[1])
        args = args[2:]
    if args == ['--grade-stdin']:
        source = sys.stdin.read()
        code, receipt = grade(oracle_mod, source)
        receipt['runner_sha256'] = hashlib.sha256(source.encode('utf-8')).hexdigest()
        receipt['runner_source'] = 'stdin, graded in memory'
        print(json.dumps(receipt, sort_keys=True, indent=2))
        return code
    if args:
        print('usage: mutation-adequacy.py [--oracle FILE] [--grade-stdin]', file=sys.stderr)
        return 2
    src = RUNNER.read_text(encoding='utf-8')
    try:
        sources = [(m, mutate(src, m[3], m[4], m[5])) for m in MUTANTS]
    except ValueError as exc:
        print('r22-mutation-adequacy: could-not-evaluate: ' + str(exc), file=sys.stderr)
        return 2
    code, pristine = grade(oracle_mod, src)
    rows = []
    for (mid, origin, expect, _old, _new, _occ), source in sources:
        mcode, receipt = grade(oracle_mod, source)
        killers = [r['id'] for r in receipt['results'] if not r['pass']]
        observed = 'killed' if killers else 'survived'
        rows.append({'id': mid, 'origin': origin, 'expect': expect, 'observed': observed,
                     'oracle_exit': mcode, 'killing_vectors': killers,
                     'mutant_sha256': hashlib.sha256(source.encode()).hexdigest(),
                     'agrees': (observed == 'killed') if expect == 'killed' else (observed == 'survived')})
    ok = code == 0 and pristine['fail'] == 0 and all(r['agrees'] for r in rows)
    print(json.dumps({
        'schema': 'souji-r22-mutation-adequacy-v1',
        'python': sys.version.split()[0],
        'runner_sha256': hashlib.sha256(src.encode()).hexdigest(),
        'oracle_sha256': pristine['oracle_sha256'],
        'oracle_total': pristine['total'],
        'pristine': {'exit': code, 'pass': pristine['pass'], 'fail': pristine['fail']},
        'mutants': rows,
        'summary': {
            'mutants': len(rows),
            'killed': sum(r['observed'] == 'killed' for r in rows),
            'survived': sum(r['observed'] == 'survived' for r in rows),
            'disagreeing_with_expect': [r['id'] for r in rows if not r['agrees']],
        },
        'scope': 'In-memory literal mutants graded by pinned public outputs plus fabricated mutations; no child process, file write or process inspection. Equivalent marks are L1 reasoning, not proof.',
    }, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
