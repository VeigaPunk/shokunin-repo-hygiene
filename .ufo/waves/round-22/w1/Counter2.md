STATUS: PASS — Counter predicate boundary located: a single JSON scalar leaf differing only in *type* (bool↔int, float↔int) flips `json_match` to the wrong side of "exact one → true". Baseline defect confirmed at source and closed by the in-flight `json_exact` repair; the deliberately-tolerated non-exact superset is preserved, not a defect. Source-only review; nothing executed.

## Scope and identity

- Baseline authority (per L1 directive): `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`, sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`. All "base:" line cites are this blob.
- Working tree `census/round-21/run-acceptance.py` sha256 `02e3b06dad7421d43f27b87a41568e6577c1ad64a89a933dc12ee8408f4bc32c` — differs from base as expected (L1 integrating). Repair cites use current worktree lines.
- `census/round-21/step-inventory.json` sha256 `8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310` — **byte-identical at base and worktree**: all 18 frozen positive controls and counter expectations are pinned (Q51 requirement observed at source).
- Axes: calibration (claim C1 target), operability, coverage; no trade.

## Predicate location (base blob)

`kind == "counter"` branch of `summarize_result`, base `census/round-21/run-acceptance.py:420-445`:

- `matched` seed: `returncode == 0 and not failures` (base:367).
- Exact mode: `json_match = observed == expected` (base:427) — Python `==`, not JSON-type equality.
- Non-exact mode: `all(observed.get(key) == value for key, value in expected.items())` (base:430-431) — same `==` per top-level field; extra observed keys tolerated (declared design: `r13-counter-b576341` is the one `exact_json=False` row, base:171-179 / step-inventory.json:323-336).
- `matched = matched and json_match and not stderr` (base:445) — counter stderr gate already present; the r21 stderr defect is summary-kind only (base:417).
- Malformed stdout: `json.loads` guarded, `observed = None` (base:421-424) → `json_match` False without crash (exact) or via `isinstance(observed, dict)` (non-exact).
- Expectation values: `COUNTER_EXPECTATIONS` (base:120-180), wired verbatim into steps at base:319-327; frozen projection check at base:600-602.

## Findings (by severity)

### F1 HIGH — scalar type equality: one wrong-typed leaf still yields `matched=True` (base defect; repaired in worktree)

The boundary case "exactly one leaf differs" currently returns true at **both** predicate sites because Python's numeric tower equates across JSON types:

- `True == 1`, `False == 0` (bool is an int subclass)
- `1.0 == 1` (int/float equality)

Literal vectors (verbatim expectation leaf → observed stdout leaf; all other fields identical, returncode 0, empty stderr):

| vector | step / expectation site | observed | base `json_match` | correct |
|---|---|---|---|---|
| P (positive control) | `r13-counter-6f8ee0f` `"F2_entry": 1` (base:138) | `{"F2_entry": 1, …}` | True | True |
| N1 (bool) | same expectation | `{"F2_entry": true}` | **True** | False |
| N2 (0/false) | `r14-counter-a31642d` `"cache_gate": 0` (base:151) | `{"cache_gate": false}` | **True** | False |
| N3 (float) | `r13-counter-b576341` `"admitted_entries": 6` (base:177, non-exact) | `{"admitted_entries": 6.0}` | **True** | False |
| N4 (nested) | any `"tiers": {"A": 33}` | `{"tiers": {"A": 33.0}}` | **True** | False |

N2 is the class already admitted HIGH in `.ufo/waves/round-21/w2/AttackRunnerStepResults.md:5-9`; N3 extends it to the non-exact path and to float, which Q51 (`corpus/QUALITY.md:120`) names explicitly ("bool/float … rejected"). `[INFERENCE]` on Python `==` semantics — grounded in Python data-model docs, not executed.

**Repair check (worktree, read not run):** `json_exact` (worktree:373-385) enforces `type(observed) is not type(expected) → False` before recursion, so `bool`/`float`/`null`/`list` leaves all fail; dict key-set equality at :378 keeps exact mode exact; the list branch's `len` guard at :382 makes `zip` truncation impossible. Counter call sites: exact `:471`, non-exact `key in observed and json_exact(observed[key], value)` `:474-476`. Every N1–N4 flips to False; P stays True. Boundary verdict: predicate now distinguishes "one scalar differs in type" correctly.

**Latent boundary also closed:** base `.get(key) == value` conflated *absent* key with *explicit JSON null* (`observed.get("x") is None == expected None` → True). No current expectation contains `null`, so latent, not a live false green; repaired `key in observed` closes it at zero cost. Retain as a synthetic negative only if a null-bearing expectation is ever added to the oracle.

### F2 LOW — `matched_expected_fields` diagnostic retains `==` semantics (cosmetic only)

Worktree :483-486 still sums `observed_fields.get(key) == value` over `numeric_leaves`, and `numeric_leaves` (worktree:362-370, unchanged) drops bool and float leaves entirely. Non-authoritative: the verdict no longer depends on `==`, and post-repair `matched=True` implies full expected-field equality, so the base's contradictory green (matched True while the count showed a miss, per r21 attack report :9) can no longer occur — undercount now appears only alongside `matched=False`. No action needed; noted so the diagnostic is not cited as independent confirmation.

### F3 — boundary checks with no defect found (counter predicate)

- rc≠0, `FAIL`-marker lines, non-empty stderr already gate the verdict (base:367,445).
- Whole-stdout JSON contract: trailing/leading non-JSON junk fails closed via `json.loads` (observed=None) — strict by design.
- Python `json.loads` extensions (`NaN`, `Infinity`): parse succeeds but `float` type + never-equal values fail closed under both base `==` and `json_exact`; no expectation is non-finite.
- Duplicate keys → decoder last-wins; mismatches every current expectation → fail closed.
- >4300-digit integers → `json.loads` `ValueError` → caught → mismatch, no crash (Q51 "retained mismatch, not a crash").
- Unicode-equivalent-but-distinct keys → `str` equality, no normalization → fail closed (conservative).
- `measured_commit` leaf is plain `str` equality — exact string required in both modes.

### F3-rejected — out-of-scope items explicitly NOT defects

- **Extra top-level keys in non-exact mode**: `r13-counter-b576341` is the single deliberately `exact_json=False` row; Q51 requires "subset-extra-fields … accepted". The repair preserves `key in observed` subset semantics. Any push for full-keyset equality on this row is rejected added scope (would change a pinned historical projection).
- **Summary-kind stderr gap** (base:417 lacked `not stderr`; worktree:461 adds it): preregistered defect #2, owned by the Stderr scouts — counter branch was already gated.
- **Cache check-name identity** (base:462-463 count+`is True` only; worktree adds `CACHE_CHECK_NAMES`/`CACHE_CASE_PHASES` at :502-531): preregistered defect #3, owned by the Cache critics.
- **Producer authentication, duplicate-key attestation, key-order/Unicode canonicalization**: outside "scalar type equality"; preregistration excludes malicious-producer attestation.

## Residual risk

- Source-inference only: `json_exact`'s recursion on adversarially deep input is bounded by Python's recursion limit; a hostile depth could raise `RecursionError` mid-predicate. `json.loads` itself would hit its own limit first on real input, and `RecursionError` is not in the `except (ValueError, TypeError)` guard — on base it cannot occur either (short-circuit `==`). Classified malformed-producer edge, low probability; worth one synthetic depth case in the result-oracle fixture if coverage allows, otherwise disclosed limit.
- `json_exact` reused by cache-demo (`:516-518`) — consistent strictness, no counter impact.

## Verification gaps

- No execution per contract: all verdicts are source-inferred from the named base blob and current worktree; no test, probe, or fixture was run.
- `xd://lsp` probed this session: device not mounted ("No such tool"), so no LSP caller/definition/diagnostics evidence; predicate analysis rests on direct reads of the named runner only (no broad grep used or needed).
- Counter stderr gate at base:445 means the summary-stderr defect does not reach this predicate; verified at source.
- Process note: one scratch file `/tmp/lsp_probe.json` was created and removed during the lsp probe; no tools installed, no other writes.

Report: `.ufo/waves/round-22/w1/Counter2.md`
