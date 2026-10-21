STATUS: PASS — source-only boundary analysis of the counter predicate's trailing-JSON-document behavior on baseline `41553adb139d06511dc386bb3ce4326aebfba675`. The boundary is already fail-closed at base; this lane's contribution to claim C1 is a retained control set (literal positive/negative vectors over a real counter expectation) that the admitted predicate repairs must not regress, plus explicit in-scope/rejected-scope dispositions. Nothing was executed; every decision below is source-derived from named bytes and cited public CPython authority.

Axes (godspeed): calibration (boundary truth of the counter predicate), operability (draft vectors L1 can lift verbatim into the synthetic result oracle), coverage (whitespace / extra-data / BOM / empty / second-document / lenient-parse-regression cases pinned). No trade; no additional axis claim.

## Baseline identity and method

- All `run-acceptance.py` citations are baseline-blob line numbers from the parent-authorized read `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` (blob sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`).
- During this seat's session the working-tree `census/round-21/run-acceptance.py` was observed to differ from that baseline (working sha256 `02e3b06dad7421d43f27b87a41568e6577c1ad64a89a933dc12ee8408f4bc32c`) — L1 integration is in flight. This report analyzes only the pinned baseline bytes; the changed implementation is not reviewed here.
- `census/round-21/step-inventory.json` was byte-identical between baseline blob and working tree at read time (both sha256 `8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310`).
- No LSP device is mounted in this session; checks are source reads with line citations, and no grep output is offered as semantic proof. No tools were installed. No probes, tests, or builds were run (contract).

## The actual counter expectations located

Runner `COUNTER_EXPECTATIONS`, baseline `census/round-21/run-acceptance.py:120-180`; mirrored as frozen inventory rows in `census/round-21/step-inventory.json` (`clean-cache-demonstration` at lines 186–206, counters at 207–337).

- `r13-counter-31984f4` (`exact_json: true`, line 121–132): `F2_entry: 0`, `admitted_entries: 4`, `evidence_gate: 0`, `measured_commit: "31984f473ce4bdab61a99b16cca194b28108cb81"`, `sources: 33`, `tiers: {A: 29, B: 3, C: 1}`, `statuses: {mined: 16, queued: 15, rejected: 2}`. This is the concrete expectation used for every vector below.
- `r13-counter-6f8ee0f` (`exact_json: true`, lines 133–144): `F2_entry: 1`, `admitted_entries: 5`, `evidence_gate: 1`, `sources: 37`, tiers `33/3/1`, statuses `20/15/2`.
- `r14-counter-a31642d` (`exact_json: true`, lines 145–157) and `r14-counter-552cae4` (`exact_json: true`, lines 158–170): cache_gate/cache_fixture/boundary_fixture 0 (resp. 1), `source_rows: 37` (resp. 40), tiers `33/3/1` (resp. `36/3/1`), statuses `20/15/2` (resp. `23/15/2`), `admitted_knowledge: 5`, `held_knowledge: 1`.
- `r13-counter-b576341` (`exact_json: false`, lines 171–179): sub-document expectation only `measured_commit: "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3"`, `admitted_entries: 6`.

## Counter predicate at base and the trailing-document boundary

Baseline `census/round-21/run-acceptance.py:420-445`:

```python
elif kind == "counter":
    try:
        observed = json.loads(stdout)
    except (ValueError, TypeError):
        observed = None
    expected = step["expected_summary"]
    if step["exact_json"]:
        json_match = observed == expected
        expected_fields = numeric_leaves(expected)
    else:
        json_match = (isinstance(observed, dict)
                      and all(observed.get(key) == value for key, value in expected.items()))
        expected_fields = numeric_leaves(expected)
    ...
    matched = matched and json_match and not stderr
```

`stdout` is the whole stream, decoded with `decode_exact` (`utf-8`/`surrogateescape`, lines 197–198). `matched` also requires `returncode == 0` and no `failure_lines` (line 367) and empty stderr (line 445); the `matched_counts` block (lines 435–444) is recorded diagnostics only and never gates.

Boundary behavior of `json.loads` (authority: CPython `Lib/json/decoder.py` `decode()`/`raw_decode()` and `Lib/json/__init__.py` `loads()`, read at tags `v3.12.7` and `v3.10.4`; docs `https://docs.python.org/3/library/json.html`):

- `decode()` allows leading/trailing whitespace matched by `WHITESPACE = re.compile(r'[ \t\n\r]*')`, then raises `JSONDecodeError("Extra data", s, end)` when `end != len(s)`.
- Empty or whitespace-only input raises `JSONDecodeError("Expecting value", ...)` (from `raw_decode`'s `StopIteration` conversion).
- A `str` beginning with U+FEFF raises `JSONDecodeError("Unexpected UTF-8 BOM (decode using utf-8-sig)", s, 0)` (verified present in the fetched v3.10.4 `loads()`; on any interpreter lacking the check a BOM is simply not a valid JSON start, so the decision is identical, only the message differs).
- `JSONDecodeError` subclasses `ValueError` (decoder.py), so both baseline `except (ValueError, TypeError)` handlers (lines 423–424, 449–450) swallow every malformed-document outcome into `observed = None` / `payload = None` — no crash path out of `summarize_result`.

**Verdict — no in-scope trailing-document defect exists at base.** For both counter branches, any trailing non-whitespace content makes `json.loads` raise; `observed` becomes `None`; `None == expected` is False (exact branch) and `isinstance(None, dict)` is False (non-exact branch); `json_match` is False; the step records `matched: false` with the raw stdout/stderr digests retained. The same whole-document `json.loads` guards the cache-demo branch (lines 446–450), so it is equally fail-closed at this boundary. This is consistent with the r21 attack, which found counter false greens in scalar equality (admitted defect 1), not at the document boundary.

## Draft literal positive/negative pair (for the synthetic result oracle)

Concrete step: `r13-counter-31984f4`, `kind: "counter"`, `exact_json: true`, assumed `returncode: 0`, `stderr: b""` (stderr and rc are separate gates; these vectors isolate the document boundary). Base decision = pinned `41553adb` bytes; calibrated decision = what claim C1 must preserve after the three admitted repairs.

```python
BASE = ("{" + ', '.join([
    '"F2_entry": 0',
    '"admitted_entries": 4',
    '"evidence_gate": 0',
    '"measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81"',
    '"sources": 33',
    '"statuses": {"mined": 16, "queued": 15, "rejected": 2}',
    '"tiers": {"A": 29, "B": 3, "C": 1}',
]) + "}")

CASES = [
    # id, stdout literal, base matched, calibrated matched
    ("POS-1 canonical+newline",  BASE + "\n",            True,  True),
    ("POS-2 ws-padded",          "\n\t" + BASE + " \r\n", True, True),
    ("NEG-1 trailing comment",   BASE + "\n# r13-counter-31984f4 end\n", False, False),
    ("NEG-2 second document",    BASE + "\n" + BASE,     False, False),
    ("NEG-3 trailing brace",     BASE + "}",             False, False),
    ("NEG-4 leading BOM",        "﻿" + BASE + "\n",       False, False),
    ("NEG-5 empty stdout",       "",                     False, False),
    ("NEG-5b whitespace only",   "\n \t",                False, False),
]
```

Mechanism per case: POS-1/POS-2 pass because `[ \t\n\r]*` is stripped at both ends by `decode()`; NEG-1/NEG-2/NEG-3 raise `Extra data` at the first trailing non-whitespace character; NEG-4 raises the BOM error (v3.10.4 source) or `Expecting value` on interpreters without the check; NEG-5/NEG-5b raise `Expecting value`. All negatives land in `observed = None` → `matched: false`, recorded without a crash — the preregistration's "Reject malformed producer data without a crash" obligation, already met at base and to be retained.

**NEG-6 (regression guard — rejected behavior, not a base case):** any calibrated implementation that switches to `JSONDecoder.raw_decode()` without re-checking `end != len(s)`, or trims stdout to a guessed document extent, returns the expected dict for the NEG-1/NEG-2/NEG-3 stdout and turns them into false greens. The oracle must keep those rows expecting `matched: false` so this class of "repair" fails the fixture.

**Interface with the scalar lane (admitted defect 1, not re-litigated here):** `NEG-SCALAR` = `BASE` with `"F2_entry": false` → base `matched: true` (`False == 0` under dict equality; docs `https://docs.python.org/3/library/stdtypes.html`: "Booleans are a subtype of integers", numeric comparison compares exact values), calibrated `matched: false`. The false-green fields are exactly those whose expected value is 0 or 1 — `F2_entry`/`evidence_gate` on `31984f4`/`6f8ee0f`, the three cache fixtures on `a31642d`/`552cae4`, `held_knowledge: 1` on `552cae4`; tier/status counts (≥ 2) cannot be bool-poisoned. `numeric_leaves` already excludes bools (lines 342–343) but that diagnostic never gates.

## In-scope vs rejected added scope

In scope for C1 (counter share):
1. Retain POS-1/POS-2 and NEG-1–NEG-5(b) as literal oracle rows on the real `31984f4` expectation, alongside all 18 original positive controls and exact historical projections (preregistration line 1).
2. Keep whole-document parsing semantics (or an equivalent explicit end-of-document check) so NEG-6 stays impossible; keep every malformed document a recorded unmatched step, never an exception.
3. Scalar bool/int strictness on counter equality — owned by the scalar draft seat; the boundary values above are this lane's handoff.

Rejected added scope (each would be a new claim; preregistration: "No additional axis claim"):
- Trailing-document leniency (accepting extra data) — a weakening, opposite of calibration.
- Duplicate-key rejection: `json.loads('{"sources": 0, ..., "sources": 33, ...}')` collapses last-wins (`dict(pairs)` in `JSONObject`, decoder.py) and the exact branch would match — a real residual exactness gap, but not one of the three admitted defects; left open deliberately.
- NaN/`Infinity` literals: the default decoder accepts them (`parse_constant` default `_CONSTANTS.__getitem__`; docs: "It also understands NaN, Infinity, and -Infinity ... which is outside the JSON spec"), but `"sources": NaN` fails equality against `33`, so exact counters stay fail-closed; rejecting them via `parse_constant` is unclaimed.
- Float/int confusion on the non-exact row: `r13-counter-b576341` accepts `"admitted_entries": 6.0` (`6.0 == 6` per cross-type numeric comparison, stdtypes) — residual, C1 makes no claim; flagged for L1 disposition with the literal negative vector `{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6.0}` → base `matched: true`.
- UTF-8 strictness: `decode_exact` maps invalid bytes to lone surrogates inside string values; exact rows then fail equality (expected contains no surrogates), and the non-exact row tolerates extra keys by declared sub-document design — unclaimed.
- Cache check-name identity and summary-stderr gaps — admitted defects 2 and 3, other seats; the boundary control rows should simply be mirrored for the cache-demo branch since it shares `json.loads`.

## Residual risk and verification gaps

- Source-only: no decision above was executed. Grounding is the pinned baseline blob (digest above), the frozen inventory (digest above), and public CPython docs/source at `v3.12.7`/`v3.10.4`; the interpreter version L1 will run is not sampled by this seat, and only the BOM error *message* varies across versions, never the decision.
- Working-tree drift during the session means this report cannot certify the integrated implementation; baseline claims only.
- Duplicate-key and non-exact float/int residuals remain open and unclaimed, as scoped above.

— Seat `SoujiR22.Counter20`, wave round-22/w1. Trailers relative to `souji-shokunin`.
