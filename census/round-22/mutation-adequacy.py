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
import resource
import sys
import types
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / 'census/round-21/run-acceptance.py'
ORACLE_PY = ROOT / 'tests/fixtures/r22-result-oracle.py'
# Decoder RecursionError thresholds depend on the C stack (and environment size), so the soft
# limit alone does not predict them: record it AND whether this process's decoder raises on the
# oracle's 100000-deep array, which decides the depth-100000 vectors and both recursion mutants.
_SOFT_STACK = resource.getrlimit(resource.RLIMIT_STACK)[0]
STACK = 'unlimited' if _SOFT_STACK == resource.RLIM_INFINITY else _SOFT_STACK


def _depth_100000_raises():
    try:
        json.loads('[' * 100000 + '0' + ']' * 100000)
    except RecursionError:
        return True
    return False


DEPTH_100000_RAISES = _depth_100000_raises()
PROBE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

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
    # Residual review (CritMutation F1, ResidAdequacyB B3, SoujiR22-2): unlisted mutants.
    ('json-exact-leaf-true', 'r22-changed', 'killed',
     '    return observed == expected\n', '    return True\n', None),
    ('case-row-isinstance-drop', 'r22-changed', 'killed',
     'row.get("phase") if isinstance(row, dict) else None', 'row.get("phase")', None),
    # Equivalent under the pinned inventory: the only baseline_mismatch_group step also sets
    # baseline_mismatch_count, so None == int already forces summary_match False.
    ('baseline-guard-pass', 'r22-changed', 'equivalent',
     '                except ValueError:\n                    summary_match = False\n',
     '                except ValueError:\n                    pass\n', None),
    ('nonexact-isinstance-drop', 'pre-existing', 'killed',
     'json_match = (isinstance(observed, dict)\n                          and all(',
     'json_match = (all(', None),
    ('gate-self-consistency', 'pre-existing', 'killed',
     'gate.get("sha256") == gate_sha', 'gate.get("sha256") == gate.get("sha256_after")', None),
    ('status-drop', 'pre-existing', 'killed',
     '            and payload.get("status") == expected["status"]\n', '', None),
    ('measured-commit-drop', 'pre-existing', 'killed',
     '            and payload.get("measured_commit") == revision\n', '', None),
    ('harness-revision-drop', 'pre-existing', 'killed',
     '            and payload.get("harness_revision") == revision\n', '', None),
    ('inputs-unchanged-drop', 'pre-existing', 'killed',
     '            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]\n',
     '', None),
    ('inputs-unchanged-eq', 'pre-existing', 'killed',
     'payload.get("inputs_unchanged_during_run") is expected',
     'payload.get("inputs_unchanged_during_run") == expected', None),
    ('isolation-residue-falsy', 'pre-existing', 'killed',
     'and isolation.get("residue") == []\n', 'and not isolation.get("residue")\n', None),
    ('checks-all-true-drop', 'pre-existing', 'killed',
     '            and all(value is True for value in checks.values())\n', '', None),
    # Equivalent: implied by the reviewed-constant length plus exact name/phase identity.
    ('checks-len-drop', 'pre-existing', 'equivalent',
     'and isinstance(checks, dict) and len(checks) == expected["checks"]\n',
     'and isinstance(checks, dict)\n', None),
    ('caserows-len-drop', 'pre-existing', 'equivalent',
     'and isinstance(case_rows, list) and len(case_rows) == expected["cases"]\n',
     'and isinstance(case_rows, list)\n', None),
    ('failures-drop', 'pre-existing', 'killed',
     'matched = returncode == 0 and not failures', 'matched = returncode == 0', None),
    ('returncode-drop', 'pre-existing', 'killed',
     'matched = returncode == 0 and not failures', 'matched = not failures', None),
    ('aux-drop', 'pre-existing', 'killed',
     'summary_match = summary_match and auxiliary_match', 'summary_match = summary_match', None),
    ('bm-count-drop', 'pre-existing', 'killed',
     '                and reported_baseline_mismatches == baseline_mismatch_lines\n', '', None),
    ('pass-match-drop', 'pre-existing', 'killed',
     'matched = matched and summary_match and pass_match and not stderr',
     'matched = matched and summary_match and not stderr', None),
    ('violation-drop', 'pre-existing', 'killed',
     'matched = matched and not any(line.startswith("VIOLATION\\t")',
     'matched = matched and not any(False', None),
    # Diff-enumerated survivors from residual CritAdequacy245 (N1-N4 r22-changed; R1-R5 re-asserted).
    ('numeric-leaves-recursive-base', 'r22-changed', 'killed',
     '    pending = [(value, prefix)]\n'
     '    while pending:\n'
     '        current, path = pending.pop()\n'
     '        if isinstance(current, dict):\n'
     '            for key, item in reversed(current.items()):\n'
     '                pending.append((item, key if not path else path + "." + key))\n'
     '        elif isinstance(current, int) and not isinstance(current, bool):\n'
     '            found[path] = current\n',
     '    if isinstance(value, dict):\n'
     '        for key, item in value.items():\n'
     '            child = key if not prefix else prefix + "." + key\n'
     '            found.update(numeric_leaves(item, child))\n'
     '    elif isinstance(value, int) and not isinstance(value, bool):\n'
     '        found[prefix] = value\n', None),
    ('cache-phases-sorted', 'r22-changed', 'killed',
     'case_phases == list(CACHE_CASE_PHASES)',
     'sorted(map(str, case_phases)) == sorted(CACHE_CASE_PHASES)', None),
    ('cache-phases-set', 'r22-changed', 'killed',
     'case_phases == list(CACHE_CASE_PHASES)', 'set(case_phases) == set(CACHE_CASE_PHASES)', None),
    ('json-exact-keys-subset', 'r22-changed', 'killed',
     'return (observed.keys() == expected.keys()\n', 'return (observed.keys() <= expected.keys()\n', None),
    ('counter-except-no-valueerror', 'r22-changed', 'killed', RE, 'except (TypeError, RecursionError):', 0),
    ('cache-except-no-valueerror', 'r22-changed', 'killed', RE, 'except (TypeError, RecursionError):', 1),
    ('summary-group-guard-drop', 'pre-existing', 'killed',
     'if group is not None and summary_match:', 'if group is not None:', None),
    ('cache-caserows-isinstance-drop', 'pre-existing', 'killed',
     'and isinstance(case_rows, list) and len(case_rows) == expected["cases"]\n',
     'and len(case_rows) == expected["cases"]\n', None),
    ('cache-gate-sha-default', 'pre-existing', 'killed',
     'gate.get("sha256") == gate_sha', 'gate.get("sha256", gate_sha) == gate_sha', None),
    ('cache-cleaned-default', 'pre-existing', 'killed',
     'isolation.get("cleaned") is expected', 'isolation.get("cleaned", True) is expected', None),
    ('cache-residue-default', 'pre-existing', 'killed',
     'and isolation.get("residue") == []\n', 'and isolation.get("residue", []) == []\n', None),
    ('cache-status-default', 'pre-existing', 'killed',
     'payload.get("status") == expected["status"]', 'payload.get("status", "ok") == expected["status"]', None),
    ('counter-stderr-strip', 'pre-existing', 'killed',
     'matched = matched and json_match and not stderr', 'matched = matched and json_match and not stderr.strip()', None),
    ('cache-stderr-strip', 'pre-existing', 'killed',
     'matched = matched and demo_match and not stderr', 'matched = matched and demo_match and not stderr.strip()', None),
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
        receipt['stack_soft_limit'] = STACK
        receipt['depth_100000_decode_raises'] = DEPTH_100000_RAISES
        receipt['python'] = sys.version.split()[0]
        receipt['probe_sha256'] = PROBE_SHA256
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
        'stack_soft_limit': STACK,
        'depth_100000_decode_raises': DEPTH_100000_RAISES,
        'probe_sha256': PROBE_SHA256,
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
