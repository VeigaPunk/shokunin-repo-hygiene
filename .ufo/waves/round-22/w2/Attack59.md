# Attack59 — vector `cache/shape/isolation/null` (want=False)

Seat: SoujiR22.Attack59 (critic, leaf, source-only). Target: changed runner at HEAD
`4f83fd222ffbd8825340221a8c426550ef891191`, base `41553adb139d06511dc386bb3ce4326aebfba675`.
Nothing was executed against the runner. No tests, mutations or oracle runs. Installs/updates: none.

## STATUS

Source-only **PASS** for this vector, with one **PARTIAL** coverage finding next to it.

- The expected decision `want=False` is correct.
- The fixture really does feed the null input.
- The changed predicate rejects it by returning `False`, not by raising.
- The base predicate raises `AttributeError` on it, so this vector separates base from changed.

The paired positive control isolates the isolation conjunct, but only if L1's actual run shows `positive/clean-cache-demonstration` as matched=True. See the dependency section below.

Limits: these are source and data readings, not runtime observations. Expected observed values are marked [INFERENCE] until L1 runs all 214 vectors. Reap, NAMESPACE and exposure stay HELD. Certification is OFF and K5 is HELD.

## 1. Delta reconstructed from the pinned record and frozen inventory (before reading the predicate)

**Stored delta.** `tests/fixtures/r22-result-oracle.json:2240-2252`:

- `id` is `cache/shape/isolation/null`, `want` is false, `group` is `malformed`.
- `step_name` is `clean-cache-demonstration`.
- `json_set` is `[[["isolation"], null]]`.
- No `returncode`, `stderr` or `stdout` override is set.

**Original record.** `census/round-21/final-out-S1.json`, the `commands[]` entry named `clean-cache-demonstration` (lines 2330-3383):

- `returncode` is 0 (l.3380) and `stderr` is `""` (l.3381).
- `stdout` (l.3383) is the pretty-printed JSON emitted by `cache-demonstration.py:emit` (l.1106-1108).
- I decoded the stored `stdout` string. It equals the record's `observed_json` exactly (`True`).
- In the decoded payload:
  - top-level `isolation` is `{"base": ".../souji-r14-cache-demo.4uavk4gp", "cleaned": true, "fixture_files": [...], "kept": false, "records": ..., "residue": [], "results": ..., "root": ..., "under_var_tmp": true}` (l.3246-3259);
  - `status` is `ok`;
  - `measured_commit` and `harness_revision` are both `ff425ab835614f38205426330b9cdb93fd267045`;
  - the case phases are `[initial-fresh, unchanged, dependency-modified, legacy-no-dependencies]`;
  - there are 33 checks, all true (l.2996-3030);
  - `failed_checks` is `[]`;
  - `producer_executions_new_policy` is 3;
  - `inputs_unchanged_during_run` is true;
  - `gate.sha256` is `dd279ba95eeb…08939d6` (l.3164).

**Frozen inventory.** `census/round-21/step-inventory.json:187-206`: `kind` is `cache-demo`, and `expected_summary` has `isolation_cleaned: true`, `cases: 4`, `checks: 33`, `measured_commit: "<REV>"`.

**How the fixture applies it.** `r22-result-oracle.py:67-82`:

1. `stdout = record['stdout']`.
2. `payload = json.loads(stdout)`.
3. The path is `["isolation"]`, so the loop over `path[:-1]` does nothing and the assignment is `payload["isolation"] = None`.
4. `stdout = json.dumps(payload)` re-serializes it compactly, which is harmless.
5. l.84-85 replaces `measured_commit` with the oracle revision `ff425ab…`, which matches the payload.
6. `returncode` stays 0 and `stderr` stays `""`, both taken from the record (l.88-90).

The reconstructed input is therefore the pinned green payload with exactly one change: the key `isolation` is present and its value is JSON `null`.

**Is the expected decision right?** Yes, `want=False` is correct. The producer always emits an `isolation` object: `cache-demonstration.py:1200-1201` runs `payload.setdefault("isolation", {})` and then `.update(state)`, where `state` comes from `cleanup()` (l.1083-1103). So a null value never comes from a legitimate run. A summary with no isolation-cleanup evidence must not match. The preregistration also requires rejecting malformed producer data without a crash.

## 2. Changed predicate on this vector

`census/round-21/run-acceptance.py`:

- l.501: `isolation = payload.get("isolation") if isinstance(payload, dict) else None`. The key exists with value None, so `isolation` is None.
- l.506-526 evaluates the `demo_match` conjunction from left to right. Every conjunct up to l.522 holds, using the same data as the positive control. l.523 `and isinstance(isolation, dict)` is False, so evaluation stops before l.524 `isolation.get("cleaned")` and l.525 `isolation.get("residue")`. No `AttributeError` is possible.
- l.527-535 never dereference `isolation`. They only touch `case_rows`, `checks` and `payload`, all of which are intact.
- l.536-537: `matched = False`, and `result["matched"] = bool(False)`.
- In the oracle (l.97), `type(False) is bool and False is False` gives pass=True. [INFERENCE: expected observation.]

**Base comparison** (`git show 41553adb:census/round-21/run-acceptance.py`):

- l.455: `isolation = payload.get("isolation", {})`. Because the key exists, this returns None, not `{}`.
- l.467 (`gate`) holds.
- l.468: `None.get("cleaned")` raises `AttributeError`.
- The oracle catches it (l.94-96), so observed is None and pass is False. [INFERENCE: expected base observation.]

This is the R22-M5 crash class named in `corpus/lessons/round-22.md:19`. The vector discriminates correctly: base FAIL by crash, changed PASS by returning False.

**Strongest counterexamples I tried against the guard** (all from source reasoning):

- A dict subclass or other dict-like object: not reachable, because `json.loads` returns only plain `dict` or `list` containers.
- `isolation` as a non-empty list, string, number or bool: all fail the `isinstance(..., dict)` check, so they are rejected without a crash.
- `{}`: `None is True` is False, so it is rejected.

## 3. Paired positive control (`positive/clean-cache-demonstration`, want=True, oracle l.587-591)

This uses the same record with no delta. Every conjunct from l.506-525 holds on the pinned data:

- l.523 isinstance check: `isolation` is a dict.
- l.524 `cleaned`: `true is True`.
- l.525 `residue`: `[] == []`.

[INFERENCE] The positive therefore yields True, and the only difference between it and the null vector is the l.523 conjunct. That is what makes the False result attributable to isolation rather than to some other conjunct.

**Dependency L1 must observe, not assume.** l.503 sets `gate_sha = sha256(ROOT/tools/souji-evidence-cache.py)`, hashed from the *current working tree*. The payload's `gate.sha256` is `dd279ba…`. If that working-tree file differs, l.522 fails for every cache vector:

- the positive control becomes False, which is visible;
- the null vector still reports pass, but for the wrong reason.

That file is outside my named read scope, so I did not hash it. The only valid evidence that the null vector isolates the isolation check is the positive control's actual pass in L1's 214-vector receipt.

## 4. Findings

### F1 (PARTIAL, calibration and coverage; not a code defect)

The inner isolation leaves are not pinned by any of the 214 vectors.

- A grep for the keys `"cleaned"`, `"residue"`, `"under_var_tmp"` or `"kept"` in `r22-result-oracle.json` finds nothing.
- The only isolation vectors are `null` (l.2240) and `array` (l.2254), and both replace the whole object.
- The oracle does have a `checks.isolation_confined` name vector (l.1128). That is a check-name identity, not the isolation object.

Consequences:

- Deleting l.524 survives all 214 vectors. So does weakening `is` to `==`, which would admit `cleaned: 1`, or deleting l.525. [INFERENCE] The positive still passes and no vector sets `cleaned` or `residue`.
- So the bool/int-confusion fix that C1 claims is not exercised on this bool leaf, even though the code handles it correctly (`1 is True` is False).
- This is not a regression: base l.468-469 used the same `is` / `== []` form.

Impacted axes: calibration, as an overstated breadth of the claim. Operability and coverage are not harmed.

### F2 (residual, out of claim)

l.523-525 do not check `under_var_tmp` or `kept`. A payload with `under_var_tmp: false` or `kept: true`, together with `cleaned: true` and `residue: []`, would match. The subset contract permits this, and a real producer cannot emit `kept: true` with `cleaned: true` (`cleanup` l.1084-1090). I note it, but it is not a defect under C1.

## 5. Bounded mutations (drafted, NOT executed)

- **M-A.** Delete `and isinstance(isolation, dict)` at l.523. Expected to be killed by `cache/shape/isolation/null` (observed None, from `AttributeError`, instead of False) and by `cache/shape/isolation/array` (`[].get` raises).
- **M-B.** Delete l.524 (`isolation.get("cleaned") is ...`). Expected to survive all 214 vectors, which demonstrates F1.
- **M-C.** Change l.501 to `payload.get("isolation") or {}` and drop l.523. Behaviour is equivalent: the null and array vectors are still rejected without a crash. This is a benign equivalent mutant, not a gap.

## 6. Smallest safe correction

There is no code change needed for this vector.

For F1: if L1 wants the bool-leaf claim to cover isolation, it can append literal, independently reviewed vectors on the `clean-cache-demonstration` step:

- `json_set [[["isolation","cleaned"], 1]]` with want=false;
- `[[["isolation","cleaned"], false]]` with want=false;
- `[[["isolation","residue"], ["/var/tmp/x"]]]` with want=false.

Appending them changes the oracle digest and the vector count of 214. That makes it an L1 freeze decision, which must be disclosed in round-22.md the same way as the 212 to 214 append. The alternative is to state in the round-22 lesson file that the isolation leaves are not mutation-pinned.

## Evidence index

- `tests/fixtures/r22-result-oracle.json`: l.1-8 (bindings), 587-591 (positive control), 1128 (`isolation_confined` name vector), 2240-2266 (isolation null and array vectors).
- `tests/fixtures/r22-result-oracle.py`: l.29-37, 57-60, 66-100.
- `census/round-21/final-out-S1.json`: l.2330-2348, 2996-3030, 3149-3170, 3246-3259, 3380-3383.
- `census/round-21/step-inventory.json`: l.187-206.
- `census/round-21/run-acceptance.py` @4f83fd2: l.184-203, 223-224, 375-388, 493-537.
- `run-acceptance.py` @41553adb: l.446-470.
- `census/round-14/cache-demonstration.py`: l.1083-1108, 1197-1205.
- `corpus/lessons/round-22.md`: l.19, 33, 47-56.
- `.ufo/waves/round-22/preregistration.txt`.
