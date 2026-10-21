#!/usr/bin/env python3
"""Regrade pinned public acceptance bytes and synthetic mutations, without children.

0: all literal oracle decisions agree; 1: result-contract mismatch; 2: bad input.
No scanner, child process, /proc, private snapshot, or historical rewrite.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
ORACLE = Path(__file__).with_suffix('.json')


def load_runner(path):
    spec = importlib.util.spec_from_file_location('souji_r22_acceptance', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inputs():
    oracle = json.loads(ORACLE.read_bytes())
    values = []
    for path_key, hash_key in [('source_receipt', 'source_receipt_sha256'),
                               ('frozen_inventory', 'frozen_inventory_sha256')]:
        raw = (ROOT / oracle[path_key]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != oracle[hash_key]:
            raise ValueError('R22-ORACLE-INPUT-TAMPERED: ' + path_key)
        values.append(json.loads(raw))
    return oracle, values[0], values[1]


def replace_revision(value, revision):
    if isinstance(value, str):
        return value.replace('<REVISION>', revision).replace('<REV>', revision)
    if isinstance(value, list):
        return [replace_revision(item, revision) for item in value]
    if isinstance(value, dict):
        return {key: replace_revision(item, revision) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runner', type=Path, required=True)
    parser.add_argument('--case', help='exact single vector id; default all')
    args = parser.parse_args()
    try:
        oracle, receipt, inventory = inputs()
        module = load_runner(args.runner)
        records = {item['name']: item for item in receipt['commands']}
        steps = {item['name']: replace_revision(item, oracle['revision'])
                 for item in inventory['steps']}
        cases = [case for case in oracle['cases']
                 if args.case is None or case['id'] == args.case]
        if not cases:
            raise ValueError('R22-ORACLE-UNKNOWN-CASE')
        results = []
        for case in cases:
            record = records[case['step_name']]
            stdout = case.get('stdout', record['stdout'])
            if 'stdout_nested_array_depth' in case:
                depth = case['stdout_nested_array_depth']
                stdout = '[' * depth + '0' + ']' * depth
            if 'json_set' in case:
                payload = json.loads(stdout)
                for path, value in case['json_set']:
                    if not path:
                        payload = copy.deepcopy(value)
                        continue
                    at = payload
                    for key in path[:-1]:
                        at = at[key]
                    at[path[-1]] = copy.deepcopy(value)
                stdout = json.dumps(payload)
            step = copy.deepcopy(steps[case['step_name']])
            if step.get('kind') == 'cache-demo':
                step['expected_summary']['measured_commit'] = oracle['revision']
            try:
                result = module.summarize_result(
                    step, case.get('returncode', record['returncode']),
                    stdout.encode('utf-8', 'surrogateescape'),
                    case.get('stderr', record['stderr']).encode('utf-8', 'surrogateescape'),
                    oracle['revision'], ROOT)
                observed = result['matched']
                error = None
            except Exception as exc:
                observed = None
                error = type(exc).__name__ + ': ' + str(exc)
            passed = type(observed) is bool and observed is case['want']
            results.append({'id': case['id'], 'group': case['group'],
                            'expected': case['want'], 'observed': observed,
                            'exception': error, 'pass': passed})
        failures = sum(not item['pass'] for item in results)
        output = {'schema': 'souji-r22-result-oracle-receipt-v1',
                  'finding_id': 'R22-RESULT-CONTRACT' if failures else None,
                  'runner_sha256': hashlib.sha256(args.runner.read_bytes()).hexdigest(),
                  'oracle_sha256': hashlib.sha256(ORACLE.read_bytes()).hexdigest(),
                  'source_receipt_sha256': oracle['source_receipt_sha256'],
                  'total': len(results), 'pass': len(results) - failures,
                  'fail': failures, 'results': results,
                  'scope': 'Pinned public outputs plus fabricated mutations; no command execution or process inspection.'}
        print(json.dumps(output, sort_keys=True, indent=2))
        return 1 if failures else 0
    except (OSError, ValueError, ImportError, KeyError) as exc:
        print('r22-result-oracle: could-not-evaluate: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
