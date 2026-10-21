STATUS: PASS — source-only lane analysis complete. Verdict: the baseline counter predicate already enforces the empty-stderr boundary; there is NO in-scope counter-stderr defect. The drafted positive/negative pair is a regression guard for the calibration rewrite, and a proposed counter-branch stderr "repair" is rejected added scope.

Basis: exact bytes of `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` (659 lines) and `...:census/round-21/step-inventory.json` (339 lines), per L1 steering after mid-review working-tree change (an earlier working-tree read showed a different line count and was discarded as citation basis). All findings below are source-inferred; nothing was executed. No `lsp` device is mounted in this session (not in the tool inventory; matches the prior seat's recorded unavailability), so pinned-byte text reading is the fallback and is not claimed as semantic proof. No tools installed; no files written except this report.

# Axes

- Calibration (primary): is the counter predicate's stderr boundary a real false-green, and what literal vectors pin it?
- Operability: can the pair be dropped into the committed synthetic result-oracle fixture without new machinery?
- Coverage: does the pair bound the exact zero-byte/nonzero-byte edge and every bypass path?

# Finding 1 (lane verdict) — counter predicate already rejects any nonempty stderr; no in-scope defect

Counter branch, baseline `census/round-21/run-acceptance.py`:

- L353: `failures = failure_lines(stdout + ("\n" if stdout and stderr else "") + stderr)` — stderr is also scanned for failure markers, with a newline separator guarding the stdout/stderr join at the no-trailing-newline boundary.
- L367: `matched = returncode == 0 and not failures` — common gate for all kinds.
- L445: `matched = matched and json_match and not stderr` — counter-specific conjunct.

`stderr` is `decode_exact(stderr_bytes)` (L351, L197–198: `.decode("utf-8", "surrogateescape")`), which is total over every byte string, so `not stderr` is True iff `stderr_bytes == b""` exactly. The boundary is therefore zero bytes: a lone `\n`, whitespace-only output, invalid UTF-8, or any diagnostic text all force `matched` False. Marker-vocabulary stderr (`FAIL\t…`, `CASE\t…FAIL…`) is rejected twice (L353/L367 and L445). The OSError path (L617–619) synthesizes nonempty stderr plus `returncode None`, so a failed invocation can never match a counter step. The cache-demo branch carries the identical conjunct (L480), corroborating that the summary-only stderr gap is the admitted r21 defect #2, not a counter one. Independent corroboration: `.ufo/waves/round-21/w2/AttackRunnerStepResults.md` HIGH finding 2 states "The counter and cache-demo branches explicitly reject non-empty stderr (lines 445 and 480), making this a summary-only gap."

Bypass audit: only five steps have `kind: "counter"`, all built from `COUNTER_EXPECTATIONS` in `make_steps` (L319–326); the counter branch never reads `pass_pattern`/`pass_count` (no KeyError path), and no other branch handles counter steps. No path reaches `result["matched"] = True` for a counter step with nonempty stderr.

Consequence for claim C1: the in-scope counter-branch defect is the JSON scalar type equality (L427 `observed == expected`, L431 `observed.get(key) == value`; `True == 1`, `False == 0`), not stderr. Any calibration rewrite of that comparison MUST preserve the L445 stderr conjunct byte-semantically. The summary-branch stderr repair (admitted defect #2) is in scope for C1 but belongs to the summary-lane seat.

# Finding 2 — actual counter expectation/value used for the drafted pair

`r14-counter-a31642d`, `exact_json: true` (pinned step-inventory L263–292; runner `COUNTER_EXPECTATIONS` L145–157), full expected object:

```json
{
  "measured_commit": "a31642d14006830ec62edf40b0354c3699728c4a",
  "cache_gate": 0, "cache_fixture": 0, "boundary_fixture": 0,
  "source_rows": 37,
  "tiers": {"A": 33, "B": 3, "C": 1},
  "statuses": {"mined": 20, "queued": 15, "rejected": 2},
  "admitted_knowledge": 5, "held_knowledge": 1
}
```

The other four rows: `r13-counter-31984f4` and `r13-counter-6f8ee0f` (`exact_json: true`, inventory L207–234/L235–262), `r14-counter-552cae4` (`exact_json: true`, L293–322), `r13-counter-b576341` (`exact_json: false`, L323–337). All five are among the 18 real acceptance-step positive controls that preregistration requires retained unchanged; the pair below is synthetic and additive.

# Finding 3 — drafted literal positive/negative pair (synthetic result-oracle fixture; draft only, no file, not executed)

```python
# Synthetic result-oracle case pair — counter predicate, stderr boundary.
# kind="counter", exact_json=True; expected = pinned r14-counter-a31642d
# (baseline 41553adb139d06511dc386bb3ce4326aebfba675,
#  census/round-21/run-acceptance.py COUNTER_EXPECTATIONS L145-157;
#  census/round-21/step-inventory.json L263-292).

EXPECTED_R14_A31642D = {
    "measured_commit": "a31642d14006830ec62edf40b0354c3699728c4a",
    "cache_gate": 0, "cache_fixture": 0, "boundary_fixture": 0,
    "source_rows": 37,
    "tiers": {"A": 33, "B": 3, "C": 1},
    "statuses": {"mined": 20, "queued": 15, "rejected": 2},
    "admitted_knowledge": 5, "held_knowledge": 1,
}
STDOUT_R14_A31642D = json.dumps(EXPECTED_R14_A31642D) + "\n"

# POSITIVE control — must stay matched. Empty-stderr boundary, zero bytes.
COUNTER_STDERR_POSITIVE = {
    "name": "synthetic-r14-counter-a31642d-stderr-empty",
    "kind": "counter", "exact_json": True,
    "expected_summary": EXPECTED_R14_A31642D,
    "returncode": 0,
    "stdout_bytes": STDOUT_R14_A31642D.encode("utf-8"),
    "stderr_bytes": b"",
    "expect": {"matched": True,
               "reason": "L445 conjunct `not stderr` holds; JSON exactly equal"},
}

# NEGATIVE control — must be unmatched. Identical stdout/returncode, single
# nonzero stderr byte: the weakest possible violator of the L445 conjunct.
# Whitespace-only and FAIL-marker stderr are stricter instances, rejected
# twice (failure_markers via L353/L367 AND `not stderr`).
COUNTER_STDERR_NEGATIVE = {
    "name": "synthetic-r14-counter-a31642d-stderr-nonempty",
    "kind": "counter", "exact_json": True,
    "expected_summary": EXPECTED_R14_A31642D,
    "returncode": 0,
    "stdout_bytes": STDOUT_R14_A31642D.encode("utf-8"),
    "stderr_bytes": b"\n",
    "expect": {"matched": False,
               "reason": "L445 conjunct `not stderr` fails on any nonzero byte"},
}

# Gate the calibration must preserve when rewriting L427/L431 for scalar-type
# equality (strict_types_json_match replaces json_match only):
#   matched = matched and strict_types_json_match and stderr_bytes == b""
# `stderr_bytes == b""` is the byte-exact equivalent of `not stderr` given
# decode_exact totality; assert both pair expectations against it.
```

Operability: both cases are plain `summarize_result` inputs (step dict + returncode + byte strings) and need no runner, fixture program, or environment change; they slot into the SAME committed synthetic result-oracle fixture preregistration requires for before→after.

# Finding 4 — in-scope vs rejected added scope

- In scope (this lane, C1): preserve the L445 empty-stderr gate through the scalar-equality rewrite; pin it with the drafted pair as regression controls.
- In scope (other seat, C1 defect #2): add the summary-branch stderr gate (L417 has no stderr term; only `failure_lines` marker vocabulary at L330–333 mediates stderr there). Not a counter-lane change; counter rows must not be touched to "fix" it.
- Rejected added scope: adding any new stderr check to the counter branch (duplicate of an existing conjunct — pure noise, risks double-count in `matched_counts`); stderr content allowlists or partial-stderr tolerance (weakens the pinned stricter-than-summary property); stderr signing/producer attestation or executed-command authentication (explicitly unclaimed by preregistration); changing `decode_exact`/surrogateescape handling (would alter `stderr`/`stderr_sha256` records for all 18 controls).

# Residual risk and verification gaps

- Source-inferred only: the pair's pass/fail decisions are derived from pinned bytes, not observed executions; L1 runs acceptance after integration.
- The pair pins the stderr conjunct, not the scalar-equality defect (Counter-scalar lane owns `True`/`1` vectors on the same `r14-counter-a31642d` shape); the two lanes share this expectation row, so integration should merge both vector sets on one fixture case where stdout differs, or keep separate named cases as drafted.
- `numeric_leaves` (L336–344) excludes bools; `matched_counts` would expose a bool-substituted field but does not gate `matched` (L435–444) — recorded here as context for the scalar lane, not re-adjudicated.
- No LSP verification (device not mounted); no grep-based semantic claims; no tools installed.

Report trailer: paths relative to souji-shokunin — census/round-21/run-acceptance.py; census/round-21/step-inventory.json; .ufo/waves/round-21/w2/AttackRunnerStepResults.md; .ufo/waves/round-22/preregistration.txt.
