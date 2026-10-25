#!/usr/bin/env python3
"""Wave-results counter for a dispatched UFO wave (souji round 26, wave w1).

Reads the results file the orchestrator's dispatcher writes beside the
dispatch file (`w1-dispatch.json` -> `w1-results.json`) and prints the three
numbers the L1 must report from it -- seats, dead seats, role mix -- plus one
line per seat and the last error text of every dead seat.

Dispatched results schema (kernel dispatcher, `run_wave` in the orchestrator
eval cell), written with `json.dump(..., indent=1)`:

    {"lane": "souji", "round": 26, "wave": "w1", "seats": 87, "dead": 2,
     "results": [
       {"name": "ExecFoo", "agent": "executor", "id": "SoujiR26.ExecFoo",
        "status": "done", "output": "<final output text>"},
       {"name": "ScoutBar", "agent": "scout", "id": null,
        "status": "dead", "error": "RuntimeError('...')"}   # repr(e)[:2000]
     ]}

`agent` is the role the dispatch task carried (executor, critic, ...), so the
role mix is counted from it. The older `ufo-swarm-results-v1` shape is also
accepted (`members` instead of `results`, `agentId`/`result` instead of
`id`/`output`) and a bare JSON array of seat objects.

Output (stdout), first line exactly the report line:

    seats=87 dead=2 roles=executor:31 reviewer:15 ...
    results=/abs/path/w1-results.json
    lane=souji round=26 wave=w1
    statuses=done:85 dead:2
    agreement=ok declared-seats=87 declared-dead=2
    seat name=... agent=... status=... id=...
    ...
    dead name=... agent=... status=... id=...
        error-last-line: <last non-empty error line, whitespace-collapsed>
        error-text:
        <verbatim error text, 8-space indent>

Exit codes: 0 parsed and consistent; 1 parsed but inconsistent (declared
seats/dead disagree with the rows, duplicate or missing names) -- the L1 must
reconcile before reporting; 2 unusable input (absent file, unreadable, invalid
JSON, no seat array, bad argv). A missing results file therefore never prints
a valid-looking `seats=0`.

Usage:
    python3 -B .ufo/waves/round-26/w1/results-count.py
    python3 -B .ufo/waves/round-26/w1/results-count.py --results /abs/other.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# Script lives at <round>/w1/results-count.py; the dispatcher writes the
# results file at <round>/w1-results.json.
DEFAULT_RESULTS = Path(__file__).resolve().parent.parent / "w1-results.json"

# Statuses that mean the seat returned. Every other status (dead, failed,
# error, cancelled, timeout, missing) is counted dead so a seat cannot hide.
ALIVE = frozenset({"done", "completed", "ok", "success"})

MAX_ERROR_CHARS = 4000
SEAT_LIST_KEYS = ("results", "members")
OUTPUT_KEYS = ("output", "result", "final", "finalOutput")
ERROR_KEYS = ("error", "lastError", "errorText")


def fail(message: str) -> int:
    """Input refusal: one greppable line, exit 2."""
    print(message)
    return 2


def seat_rows(doc) -> tuple[list, dict]:
    """Return (seat list, whole document when it is an object)."""
    if isinstance(doc, list):
        return doc, {}
    if not isinstance(doc, dict):
        raise ValueError("top level is neither an object nor an array")
    for key in SEAT_LIST_KEYS:
        rows = doc.get(key)
        if isinstance(rows, list):
            return rows, doc
    raise ValueError("no " + "/".join(SEAT_LIST_KEYS) + " array")


def first_str(row: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def seat_name(row: dict) -> str:
    return str(row.get("name") or "-")


def seat_role(row: dict) -> str:
    return str(row.get("agent") or row.get("role") or "?")


def seat_id(row: dict) -> str:
    for key in ("id", "agentId", "sessionId"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return "-"


def seat_status(row: dict) -> str:
    value = row.get("status")
    return str(value) if value not in (None, "") else "unknown"


def is_dead(status: str) -> bool:
    return status not in ALIVE


def dead_error_text(row: dict) -> str:
    """The dead seat's own error text; fall back to its last output line."""
    text = first_str(row, ERROR_KEYS)
    if text:
        return text
    output = first_str(row, OUTPUT_KEYS)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "-"
    return " ".join(lines[-1].split())


def error_block(text: str, indent: str = "        ") -> list[str]:
    if len(text) > MAX_ERROR_CHARS:
        text = text[:MAX_ERROR_CHARS] + " ... [error-text truncated]"
    lines = text.splitlines() or [text]
    return [indent + line for line in lines]


def count_line(seats: list[tuple[str, str, str]]) -> str:
    roles = Counter(role for _, role, _ in seats)
    mix = " ".join(
        f"{role}:{n}" for role, n in sorted(roles.items(), key=lambda kv: (-kv[1], kv[0]))
    )
    dead = sum(1 for _, _, status in seats if is_dead(status))
    return f"seats={len(seats)} dead={dead} roles={mix or 'none'}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Count seats, dead seats and role mix in a wave results file."
    )
    parser.add_argument(
        "--results",
        default=str(DEFAULT_RESULTS),
        help="results JSON (default: <round>/w1-results.json beside this script's parent)",
    )
    args = parser.parse_args(argv)

    path = Path(args.results).expanduser()
    shown = path.resolve()
    if not path.exists():
        return fail(f"results=absent path={shown}")
    if not path.is_file():
        return fail(f"results=not-a-file path={shown}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return fail(f"results=unreadable path={shown} error={type(exc).__name__}")
    except json.JSONDecodeError as exc:
        return fail(
            f"results=invalid path={shown} error=JSONDecodeError "
            f"line={exc.lineno} col={exc.colno}"
        )

    try:
        rows, whole = seat_rows(doc)
    except ValueError as exc:
        return fail(f"results=invalid path={shown} error={exc}")

    seats: list[tuple[str, str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            return fail(f"results=invalid path={shown} error=seat-row-not-an-object")
        seats.append((seat_name(row), seat_role(row), seat_status(row)))

    problems: list[str] = []

    names = [name for name, _, _ in seats]
    missing = names.count("-")
    if missing:
        problems.append(f"warn=missing-name:{missing}")
    duplicates = sorted(name for name, n in Counter(names).items() if n > 1 and name != "-")
    if duplicates:
        problems.append("warn=duplicate-name:" + ",".join(duplicates))

    print(count_line(seats))
    print(f"results={shown}")
    if whole:
        lane = whole.get("lane", "-")
        round_no = whole.get("round", "-")
        wave = whole.get("wave", "-")
        print(f"lane={lane} round={round_no} wave={wave}")

    statuses = Counter(status for _, _, status in seats)
    print(
        "statuses="
        + (" ".join(f"{s}:{n}" for s, n in sorted(statuses.items(), key=lambda kv: (-kv[1], kv[0]))) or "none")
    )

    dead_total = sum(1 for _, _, status in seats if is_dead(status))
    declared_seats = whole.get("seats")
    declared_dead = whole.get("dead")
    mismatch = False
    if declared_seats is not None and declared_seats != len(seats):
        mismatch = True
    if declared_dead is not None and declared_dead != dead_total:
        mismatch = True
    if declared_seats is None and declared_dead is None:
        print("agreement=undeclared (no seats/dead fields in the results file)")
    else:
        seats_shown = declared_seats if declared_seats is not None else "-"
        dead_shown = declared_dead if declared_dead is not None else "-"
        print(
            f"agreement={'mismatch' if mismatch else 'ok'} "
            f"declared-seats={seats_shown} declared-dead={dead_shown}"
        )
    for problem in problems:
        print(problem)

    for row in rows:
        print(
            f"seat name={seat_name(row)} agent={seat_role(row)} "
            f"status={seat_status(row)} id={seat_id(row)}"
        )

    for row in rows:
        status = seat_status(row)
        if not is_dead(status):
            continue
        name, role = seat_name(row), seat_role(row)
        text = dead_error_text(row)
        print(f"dead name={name} agent={role} status={status} id={seat_id(row)}")
        print(f"    error-last-line: {last_line(text)}")
        if text:
            print("    error-text:")
            for line in error_block(text):
                print(line)

    if mismatch or problems:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
