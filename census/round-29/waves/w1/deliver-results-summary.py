#!/usr/bin/env python3
"""Summarize a dispatched wave `<wave>-results.json` for a round report (souji round 29).

Usage:
    python3 -B deliver-results-summary.py --results census/round-28/waves/w1-results.json \
        [--spec census/round-28/waves/w1-spec.json] [--report-dir census/round-28/waves/w1]

Sections (all tab-separated; `SECTION<TAB>name` opens each section, fixed order):

    SECTION seats      count<TAB>N, declared<TAB>N (top-level `seats`, "-" when absent)
    SECTION roles      <role><TAB><count>, most frequent first (ties by role name)
    SECTION status     <bucket><TAB><count>, fixed bucket order, empty buckets omitted
    SECTION not-completed
                       name<TAB>role<TAB>status<TAB>detail -- every seat whose bucket is not
                       `completed`, detail = first 200 chars of its last error/output
    SECTION reports    name<TAB>role<TAB>issue -- issue in {wait, missing-report,
                       wait+missing-report}; one `report-dir-unset` row when --report-dir is
                       not given

Status resolution, in order:
  1. the row's own `status` field when non-empty (dispatcher shape);
  2. the seat's final output: `output` -> `text` (the same chain
     tools/souji-wave-evidence-capture.sh uses for summary.tsv), then `text` parsed as JSON with
     nested string payloads unwrapped up to three times, taking its `status` member;
  3. the last `"status": "..."` pair found in that text (covers prose-prefixed or paged output);
  4. no status anywhere: a non-empty JSON object payload with no `aborted` truthy and no `error`
     string counts `completed` (the seat returned a result object); a dict carrying `aborted` or
     `error` counts `failed`; anything else (prose, thinking-only, paged fragment, empty) counts
     `unknown` and is listed as not completed, because no readable result backs it.
Buckets: completed (PASS.../done/completed/ok/success), partial (PARTIAL...), failed
(FAIL.../ERROR.../BLOCKED.../failed/cancelled), waiting ([WAIT].../wait.../pending), unknown.

Exit: 0 on any readable input (including zero seats); 2 when --results or --spec cannot be read
or the results document carries no seat array.
"""
import argparse
import ast
import json
import os
import re
import sys
from collections import Counter

SEAT_LIST_KEYS = ('results', 'members')
OUTPUT_KEYS = ('output', 'result', 'final', 'finalOutput')
ERROR_KEYS = ('error', 'lastError', 'errorText')
BUCKET_ORDER = ('completed', 'partial', 'failed', 'waiting', 'unknown')
DETAIL_CHARS = 200
STATUS_CHARS = 80
STATUS_PAIR = re.compile(r'"status"\s*:\s*"((?:[^"\\]|\\.)*)"')


def die(message):
    print(message, file=sys.stderr)
    return 2


def load_json(path, label):
    try:
        with open(path, encoding='utf-8') as handle:
            return json.load(handle), None
    except OSError as exc:
        return None, f'error: cannot read {label} {path}: {exc}'
    except ValueError as exc:
        return None, f'error: cannot parse {label} {path}: {exc}'


def seat_rows(doc):
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict):
        for key in SEAT_LIST_KEYS:
            value = doc.get(key)
            if isinstance(value, list):
                return value
    return None


def first_text(row, keys):
    for key in keys:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ''


def final_text(row):
    """The seat's final output text, or its raw output when the payload is not a dict repr."""
    raw = None
    for key in OUTPUT_KEYS:
        value = row.get(key)
        if value not in (None, '', [], {}):
            raw = value
            break
    if raw is None:
        return ''
    if isinstance(raw, dict):
        text = raw.get('text')
        return text if isinstance(text, str) else ''
    if not isinstance(raw, str):
        return ''
    try:
        parsed = ast.literal_eval(raw)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        return raw
    if isinstance(parsed, dict):
        text = parsed.get('text')
        return text if isinstance(text, str) else ''
    return parsed if isinstance(parsed, str) else ''


def output_status(text):
    """(status, payload object or None) from the final output text."""
    payload_text = text
    parsed_payload = None
    for _ in range(3):
        if not isinstance(payload_text, str) or not payload_text.strip():
            break
        try:
            parsed = json.loads(payload_text)
        except ValueError:
            break
        if isinstance(parsed, str):
            payload_text = parsed
            continue
        parsed_payload = parsed
        break
    status = ''
    if isinstance(parsed_payload, dict):
        value = parsed_payload.get('status')
        status = '' if value is None else str(value)
    if not status:
        found = STATUS_PAIR.findall(text)
        if not found:
            # Paged or double-encoded output carries \"status\": \"...\".
            found = STATUS_PAIR.findall(text.replace('\\"', '"'))
        if found:
            status = found[-1]
            if not isinstance(parsed_payload, dict):
                parsed_payload = None
    return status, parsed_payload if isinstance(parsed_payload, dict) else None


def bucket_of(status):
    word = status.strip().upper()
    if not word:
        return 'unknown'
    if word.startswith('PASS') or word in ('DONE', 'COMPLETED', 'OK', 'SUCCESS'):
        return 'completed'
    if word.startswith('PARTIAL'):
        return 'partial'
    if word.startswith(('FAIL', 'ERROR', 'BLOCKED')) or word in ('FAILED', 'CANCELLED', 'TIMEOUT', 'DEAD'):
        return 'failed'
    if word.startswith(('[WAIT]', 'WAIT', 'PENDING')):
        return 'waiting'
    return 'unknown'


def derive(text, row_status, payload):
    """(status, bucket) for a seat, and whether the payload carried an abort signal."""
    status = row_status.strip()
    if status:
        return status, bucket_of(status)
    if payload:
        aborted = payload.get('aborted')
        if aborted not in (None, False, '', 0, 'false', 'False'):
            return '', 'failed'
        if first_text(payload, ERROR_KEYS):
            return '', 'failed'
        return '', 'completed'
    return '', 'unknown'


def one_line(text, limit):
    flat = ' '.join(str(text).split()).replace('\t', ' ')
    return flat[:limit]


def spec_roles(doc):
    """item id / seat name -> role from a wave spec document."""
    roles = {}
    items = doc.get('items') if isinstance(doc, dict) else None
    if not isinstance(items, list):
        return roles
    for entry in items:
        if not isinstance(entry, dict):
            continue
        role = entry.get('role') or entry.get('agent')
        if not role:
            continue
        for key in ('item', 'name', 'id'):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                roles.setdefault(value, str(role))
    return roles


def seat_name(row, index):
    for key in ('name', 'id'):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return f'seat{index:02d}'


def seat_role(row, roles):
    for key in ('agent', 'role'):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    for key in ('item', 'id', 'name'):
        value = row.get(key)
        if isinstance(value, str) and value in roles:
            return roles[value]
    return '?'


def main(argv=None):
    parser = argparse.ArgumentParser(description='Summarize a wave results JSON file.')
    parser.add_argument('--results', required=True, help='<wave>-results.json')
    parser.add_argument('--spec', help='<wave>-spec.json for item-id -> role lookup')
    parser.add_argument('--report-dir', help='directory holding <name>.md seat reports')
    args = parser.parse_args(argv)

    doc, error = load_json(args.results, 'results')
    if error:
        return die(error)
    rows = seat_rows(doc)
    if rows is None:
        return die(f'error: no {" / ".join(SEAT_LIST_KEYS)} array in {args.results}')

    roles = {}
    if args.spec:
        spec, error = load_json(args.spec, 'spec')
        if error:
            return die(error)
        roles = spec_roles(spec)

    seats = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            continue
        name = seat_name(row, index)
        text = final_text(row)
        status, payload = output_status(text)
        row_status = row.get('status')
        if isinstance(row_status, str) and row_status.strip():
            status = row_status.strip()
        status, bucket = derive(text, status, payload)
        detail = first_text(row, ERROR_KEYS) or text
        seats.append({
            'name': name,
            'role': seat_role(row, roles),
            'status': status,
            'bucket': bucket,
            'detail': one_line(detail, DETAIL_CHARS) or '(no output)',
            'text': text,
        })

    out = ['SECTION\tseats', f'count\t{len(seats)}']
    declared = doc.get('seats') if isinstance(doc, dict) else None
    out.append(f'declared\t{declared if declared is not None else "-"}')

    out.append('SECTION\troles')
    role_counts = Counter(seat['role'] for seat in seats)
    for role, count in sorted(role_counts.items(), key=lambda pair: (-pair[1], pair[0])):
        out.append(f'{role}\t{count}')

    out.append('SECTION\tstatus')
    bucket_counts = Counter(seat['bucket'] for seat in seats)
    for bucket in BUCKET_ORDER:
        if bucket_counts[bucket]:
            out.append(f'{bucket}\t{bucket_counts[bucket]}')

    out.append('SECTION\tnot-completed')
    out.append('name\trole\tstatus\tdetail')
    for seat in sorted(seats, key=lambda item: item['name']):
        if seat['bucket'] != 'completed':
            status = one_line(seat['status'], STATUS_CHARS) or '-'
            out.append(f'{seat["name"]}\t{seat["role"]}\t{status}\t{seat["detail"]}')

    out.append('SECTION\treports')
    out.append('name\trole\tissue')
    for seat in sorted(seats, key=lambda item: item['name']):
        issues = []
        if seat['status'].lstrip().startswith('[WAIT]') or seat['text'].lstrip().startswith('[WAIT]'):
            issues.append('wait')
        if args.report_dir and not os.path.isfile(os.path.join(args.report_dir, seat['name'] + '.md')):
            issues.append('missing-report')
        if issues:
            out.append(f'{seat["name"]}\t{seat["role"]}\t{"+".join(issues)}')
    if not args.report_dir:
        out.append('-\t-\treport-dir-unset')

    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
