STATUS: PASS — Source-only boundary analysis of the counter predicate on the pinned baseline. A nested **missing** key is already decided correctly (clean mismatch) on both `exact_json` paths; the real counter defects live at the same boundary but on the **scalar-identity** axis: Python `==` conflates `bool`↔`int` and `float`↔`int`, including inside nested objects. One latent `null`-presence defect and two malformed-container crash surfaces are bounded below. All claims are source-inferred; nothing was executed.

## Method and authority

- Baseline source read via `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` per L1 direction (worktree copy differs: `git diff` shows the in-flight r22 repair — `json_exact` helper, `key in observed` guard, summary `not stderr`, `CACHE_CHECK_NAMES`; diff output treated as context only, never as contract).
- Worktree sha256 `02e3b06dad7421d43f27b87a41568e6577c1ad64a89a933dc12ee8408f4bc32c` ≠ baseline blob sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b` (computed via `git show | sha256sum`). All line citations below are **baseline** line numbers.
- `xd://lsp` is not a mounted device in this session (same unavailability recorded by `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`); no LSP caller/definition/diagnostic claims are made. Semantics rest on the named source lines, not grep-as-proof.
- Read surfaces: `census/round-21/run-acceptance.py` (baseline + worktree diff), `census/round-21/step-inventory.json`, `census/round-14/cache-demonstration.py`, `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`, `.ufo/waves/round-22/preregistration.txt`, `corpus/QUALITY.md` (Q51 row). No tests, probes, or production edits. No tools installed or updated (pacman transactions paused host-wide).

## The named boundary: counter predicate, nested missing key

Baseline `summarize_result` counter branch, lines 420–445:

- L422–424: `observed = json.loads(stdout)`; `except (ValueError, TypeError): observed = None`.
- L427 (exact): `json_match = observed == expected`.
- L430–431 (non-exact): `json_match = isinstance(observed, dict) and all(observed.get(key) == value for key, value in expected.items())`.
- L445: `matched = matched and json_match and not stderr`.

**Verdict on the named boundary itself: no defect.** A missing nested key fails cleanly on both paths and crashes nothing:

- Exact path (all four r13/r14 counters carry `exact_json: true`, `census/round-21/step-inventory.json` lines 226/254/284/314): `{k: v}` dict equality requires identical key sets recursively — observed `"tiers": {"A": 33, "B": 3}` (C dropped) vs expected `{"A": 33, "B": 3, "C": 1}` → `False` → `json_match` false → `matched` false.
- Non-exact path (`r13-counter-b576341`, `exact_json: false`, inventory line 329): `observed.get("admitted_entries")` → `None`; `None == 6` → `False` → `all()` short-circuits → clean fail. A missing *nested* key under non-exact also fails: the shallow `all()` iterates only top-level keys, and a nested dict value compares by `==` — `{"mined": 20, "queued": 15}` ≠ `{"mined": 20, "queued": 15, "rejected": 2}`.

This is the "rejected added scope" line drawn below: presence checking is already correct; a repair that *adds* recursive subset tolerance, or that conflates missing-with-`null`, would be new behavior, not a fix.

## Findings by severity

### HIGH — Scalar `==` equality admits bool/float leaves at nested and top-level positions (in-scope defect #1, nested surface)

Python `==` binds `True == 1`, `False == 0`, `1.0 == 1`, `6.0 == 6`, `0.0 == 0`. Both counter comparisons use `==` (L427 whole-dict, L431 per-key), so a producer that preserves every key but mutates scalar **types** still greens. The r21 attack record (`AttackRunnerStepResults.md` lines 5–9) demonstrated this at top level (`F2_entry`, `evidence_gate` bools); the same defect bites **nested** leaves, which is this seat's boundary:

- `r14-counter-552cae4` (inventory lines 294–321): expected `tiers.C: 1`, `cache_gate: 1`. Observed `{"tiers": {"A": 36, "B": 3, "C": true}, "statuses": {"mined": 23, "queued": 15, "rejected": 2}, "cache_gate": true, ...rest unchanged}` → nested `{... "C": True} == {... "C": 1}` is `True`, `True == 1` is `True` → whole-dict `==` green. Same for `1.0` in place of `1` anywhere (`float` confusion is equally admitted by `==`; Q51's "bool/float" wording covers both).
- `r13-counter-31984f4` (inventory lines 208–233): expected `F2_entry: 0`, `evidence_gate: 0` → observed `false`/`false` green (attack doc's canonical vector).
- Non-exact `r13-counter-b576341`: observed `admitted_entries: 6.0` → `6.0 == 6` is `True` → float greens; observed `true` → `true == 6` is `False` → still fails, because a `bool` substitute only equals expected ints 0/1. The non-exact path shares the scalar defect via `==` at L431 — **floats pass at any expected integer value, bools only where the expectation is 0 or 1**. Actual 0/1 leaves in `COUNTER_EXPECTATIONS`: `F2_entry` (0, 1), `evidence_gate` (0, 1), `tiers.C` (1 in all four rows), `cache_gate`/`cache_fixture`/`boundary_fixture` (0, 1), `held_knowledge` (1).

Diagnostic divergence already visible: `numeric_leaves` (L336–344) excludes `bool` (`not isinstance(value, bool)`), so under the `r14-counter-552cae4` `tiers.C→true` vector `observed_fields` loses that leaf and `matched_expected_fields` (L438–441) records 11 against `expected_field_count` 12 — the record **sees** the anomaly while `matched` stays `True`. (Same vector on `r13-counter-31984f4` with both `F2_entry`/`evidence_gate → false`: 8 of 10.) The defect is in `json_match`, not the counts; keep `numeric_leaves` as-is so the diagnostic contrast survives repair.

### HIGH — Malformed nested containers crash instead of mismatching (boundary-adjacent, cache-demo path)

Not the counter branch, but the same boundary question one branch down, and it bears on the third admitted defect's repair:

- `payload.get("gate", {}).get("sha256")` (L467): the `{}` default fires only on **absent** key. Observed `"gate": null` (or `"gate": "x"`, `"gate": [1]`) → `.get("sha256")` on `None`/`str`/`list` → `AttributeError`.
- `isolation = payload.get("isolation", {})` (L455) + `isolation.get("cleaned")` (L468): `"isolation": null` → same `AttributeError`.
- `summarize_result` is invoked unwrapped at L623 (the only `try` in the step loop, L613–617, covers `subprocess.run` `OSError`); the exception propagates out of the run — observed inference: unhandled `AttributeError` → nonzero exit and lost step records rather than a retained per-step mismatch.

Asymmetry worth one line in the oracle: `"gate"` **missing** → `{}.get("sha256")` → `None` → clean fail; `"gate": null` → crash. Same absent-vs-null confusion class as the counter predicate's latent defect below, but here it detonates. Q51's "null/list nested-container negatives" and preregistration's "reject malformed producer data without a crash" make this in-scope for the cache repair; the integrated diff's `isinstance` guards on `gate`/`isolation` are the correct shape.

### LOW — Latent null-presence conflation on the non-exact counter path

`observed.get(key) == value` cannot distinguish **missing** from **present-but-null**: if any expectation ever contains a JSON `null` value, a producer that omits the key entirely satisfies `None == None` → green. No shipped expectation uses `null` today (all five `COUNTER_EXPECTATIONS` rows, L120–180, carry int/str/dict leaves only), so this is latent, not a live false-green — but the boundary fix (`key in observed and json_exact(...)`) closes it silently; flagging so the ledger records it as *repaired-without-oracle*, not *repaired-and-proven*. The exact path never had this confusion (`{...} == {...}` requires the key with value `None`).

### LOW — Depth-bounded "malformed" is not rejected without a crash

`json.loads` (L422) and `numeric_leaves` recursion (L338–341) both hit `RecursionError` on input nested past the interpreter limit (json's own C scanner raises at depth ≈ recursion limit; `except (ValueError, TypeError)` does not catch `RecursionError`). A deeply nested counter payload crashes the step loop the same way as the cache `.get` chains. Whether ≈1000-deep JSON counts as "malformed producer data" under the claim is the preregistration's call — it says "reject malformed producer data without a crash" without a depth bound, so this is bounded as LOW latent rather than asserted in-scope.

## Literal oracle vectors (counter steps)

Expected decisions under the **pinned claim** (`json_exact` semantics): P = must stay green, N = must stay/turn red. All assume returncode 0, empty stderr, single-line JSON stdout.

```json
// P1 — exact identity, nested objects (r14-counter-552cae4). Baseline: PASS. Repaired: PASS.
{"measured_commit": "552cae4204b3ab818419ad8adbfef3a4da29a3e0", "cache_gate": 1, "cache_fixture": 1, "boundary_fixture": 1, "source_rows": 40, "tiers": {"A": 36, "B": 3, "C": 1}, "statuses": {"mined": 23, "queued": 15, "rejected": 2}, "admitted_knowledge": 5, "held_knowledge": 1}

// P2 — non-exact subset tolerance, top-level extras (r13-counter-b576341). Baseline: PASS. Repaired: PASS.
{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6, "sources": 41, "tiers": {"A": 38, "B": 3, "C": 1}}

// N1 — nested missing key, boundary under test (r14-counter-552cae4). Baseline: FAIL (already correct). Repaired: FAIL.
{"measured_commit": "552cae4204b3ab818419ad8adbfef3a4da29a3e0", "cache_gate": 1, "cache_fixture": 1, "boundary_fixture": 1, "source_rows": 40, "tiers": {"A": 36, "B": 3}, "statuses": {"mined": 23, "queued": 15, "rejected": 2}, "admitted_knowledge": 5, "held_knowledge": 1}

// N2 — nested container type swap (r13-counter-6f8ee0f). Baseline: FAIL. Repaired: FAIL.
{"F2_entry": 1, "admitted_entries": 5, "evidence_gate": 1, "measured_commit": "6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6", "sources": 37, "tiers": null, "statuses": {"mined": 20, "queued": 15, "rejected": 2}}

// N3 — nested bool substitution, the false-green (r14-counter-552cae4). Baseline: FALSE GREEN. Repaired: FAIL.
{"measured_commit": "552cae4204b3ab818419ad8adbfef3a4da29a3e0", "cache_gate": 1, "cache_fixture": 1, "boundary_fixture": 1, "source_rows": 40, "tiers": {"A": 36, "B": 3, "C": true}, "statuses": {"mined": 23, "queued": 15, "rejected": 2}, "admitted_knowledge": 5, "held_knowledge": 1}

// N4 — top-level bool substitution (r13-counter-31984f4; AttackRunnerStepResults canonical). Baseline: FALSE GREEN. Repaired: FAIL.
{"F2_entry": false, "admitted_entries": 4, "evidence_gate": false, "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81", "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1}, "statuses": {"mined": 16, "queued": 15, "rejected": 2}}

// N5 — non-exact float substitution (r13-counter-b576341). Baseline: FALSE GREEN. Repaired: FAIL.
{"measured_commit": "b5763415cc67ecff1e8fe56c58c39a6fb106d7a3", "admitted_entries": 6.0}

// N6 — observed non-dict / unparseable / JSON null (any counter). Baseline: FAIL. Repaired: FAIL.
["measured_commit", "admitted_entries"]        // list
"not json {{{"                                // ValueError -> observed None
null                                          // valid JSON, observed None
```

The N3/N4/N5 rows are the ones that turn red under repair; N1/N2/N6 are regression controls proving the repair did not open the presence boundary it was fixing the scalar boundary next to.

## Distinguishing in-scope defect from rejected added scope

In scope (admitted r21 defects + the malformed-container clause):

1. Scalar type equality — `==` at L427/L431 admits bool and float leaves, top-level and nested (this report's HIGH #1; extends the attack doc's top-level demonstration to nested leaves).
2. Summary stderr — L417 lacks `not stderr` (counter/cache branches already require it at L445/L480); attack doc HIGH #2. Not re-derived here beyond confirming the line.
3. Cache checks counted, not identified — L462–463 count 33 all-`True` values without binding check names (attack doc MEDIUM); adjacent crash defect in the same expression is this report's HIGH #2.

Rejected as added scope (must not ride along with the repair):

- **Presence checking**: nested-missing-key rejection is already correct; adding recursive *subset* tolerance (missing nested keys green under `exact_json: false`) would change semantics, not fix them. No seat finding supports it.
- **`null`-expected conflation** (LOW #1): fixable for free by `key in observed`, but no oracle vector and no live expectation — record as opportunistically closed, not proven.
- **NaN/Infinity non-JSON tokens**: Python `json.loads` accepts `NaN`/`Infinity`; none is `==` to any pinned integer leaf (NaN≠NaN, inf≠37), so they already fail — no action needed, noted only to bound the scalar surface.
- **Producer attestation / executed-command authentication / `/proc` or process-scanner checks / F5 parser changes**: explicitly disclaimed by preregistration.
- **Deep-nesting `RecursionError`** (LOW #2): report it, don't claim it fixed unless the oracle covers it.

## Residual risk and verification gaps

- All findings are source-inferred from baseline lines; no step, fixture, or `summarize_result` was executed (contract). Verdict labels "Baseline: FALSE GREEN/FAIL" in the vectors are `==`-semantics derivations, not observed exit codes.
- The crash findings describe propagation past the unwrapped L623 call; whether `main` catches anything further up was not chased beyond the shown grep window — bounded as "exception leaves the step loop", which alone violates "mismatch, not crash".
- Non-exact nested semantics stay *shallow-subset at top level, exact below* — the repair preserves this asymmetry; the oracle should not assert nested-superset acceptance for `exact_json: false` (rejected scope, above).
- The worktree repair visible in `git diff` (`json_exact`, `key in observed`, `CACHE_CHECK_NAMES`/`CACHE_CASE_PHASES`, `int()` guard, `not stderr`) matches the direction these findings require; integration-seat verification belongs to L1, not this seat.
- No LSP device mounted; grep used only for line-number pinning on `git show` output, never as semantic evidence.

Report: .ufo/waves/round-22/w1/Counter14.md
Baseline: census/round-21/run-acceptance.py@41553adb139d06511dc386bb3ce4326aebfba675 (blob sha256 1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b)
Fixture: census/round-21/step-inventory.json (counter rows lines 207–337)
Prior: .ufo/waves/round-21/w2/AttackRunnerStepResults.md (r21 false-green record)
Claim: .ufo/waves/round-22/preregistration.txt; corpus/QUALITY.md Q51
Tools installed: none.
