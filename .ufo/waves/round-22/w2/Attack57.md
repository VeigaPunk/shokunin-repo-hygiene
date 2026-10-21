# Attack57 — critic: `cache/shape/gate/null` (want=False)

STATUS: PARTIAL (source-only). The expected decision `False` is correct, and the fixture really does feed the mutated input. On the changed code `4f83fd2`, the predicate rejects this input without crashing. On the base `41553ad`, the same input crashes with an AttributeError. So this vector moves base from "crash" to "False"; it never moves anything from True to False. One gap remains: none of the 214 vectors binds top-level `gate.sha256`. A mutant that keeps only the `isinstance(gate, dict)` guard and drops the digest check passes every vector. Separately, the paired positive depends on the working-tree bytes of `tools/souji-evidence-cache.py`, which the oracle never hashes, so I could not check that it passes. Nothing was executed. No tools were installed or updated.

## 1. Stored delta, rebuilt from the pinned inputs before reading the predicate
- The stored delta is in the oracle JSON at lines 2212–2224: `json_set: [[["gate"], null]]`, with `step_name: clean-cache-demonstration`. It carries no `stdout`, `stderr` or `returncode` override.
- The source record is `final-out-S1.json`, step `clean-cache-demonstration`:
  - Line 3380: `returncode: 0`.
  - Line 3381: `stderr: ""`.
  - Line 3383: `stdout` is the raw JSON. It has a top-level `"gate": {"exists": true, …, "sha256": "dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6", "sha256_after": …}`. The decoded copy is at lines 3149–3168.
  - The other top-level fields the predicate reads are all present: `harness_revision` and `measured_commit` are both `ff425ab…` (lines 3170 and 3271), `isolation.cleaned` is true (3248), `residue` is `[]` (3255), `producer_executions_new_policy` is 3 (3328), `status` is "ok" (3352), and `failed_checks` is `[]`.
- The frozen inventory (`step-inventory.json`, lines 187–206) gives `kind: cache-demo`. Its `expected_summary` has no gate field. The gate's identity comes only from the live `root/tools/souji-evidence-cache.py`, read at runner line 503.
- How the oracle applies the delta (`r22-result-oracle.py`, lines 67–82):
  - It takes the record's stdout, `json.loads` it, and walks `path[:-1] == []`, so `at` is the top-level dict.
  - `at["gate"] = None` replaces the existing key; it does not add a new one.
  - It then calls `json.dumps`. The whitespace changes, which doesn't matter because cache-demo re-parses the JSON.
  - Line 84 overwrites `expected_summary.measured_commit` with the revision, but `summarize_result` never reads that field (it uses `revision`).
- Result: the input differs from the real positive in exactly one place, top-level `gate`, which goes from a digest-bearing dict to `null`. The fixture does feed this input.
- The expected `False` is correct. A cache demonstration that records no gate object cannot identify which gate bytes were measured. That is the R22-M5 obligation in `corpus/lessons/round-22.md`, line 19.

## 2. The predicate on this vector
Base `41553ad` (from `git show` of the named path):
`and payload.get("gate", {}).get("sha256") == gate_sha`. Because the key exists with value `None`, the default `{}` is not used. This becomes `None.get`, which raises AttributeError. The oracle catches it at lines 94–96, records `observed=None`, and marks the vector `pass=False`. This confirms the R22-M5 claim that a malformed null gate "reaches .get and crashes".

Changed `4f83fd2`, which is byte-identical to the working tree for the runner, the oracle `.py` and the oracle `.json`:
- Line 500: `gate = payload.get("gate") if isinstance(payload, dict) else None` gives `None`.
- Line 522: `and isinstance(gate, dict) and gate.get("sha256") == gate_sha`. The first check fails and short-circuits, so `demo_match` is False. Line 536 then gives `matched=False`, a real bool, and the vector passes.
- Ordering detail: `gate_sha = sha256_bytes(read_regular(...))` (line 503) runs before the guard. If the gate file were missing or a symlink, a `Refusal` (a ValueError subclass) would be raised, giving `observed=None` and a vector failure. That fails loudly; it cannot produce a false pass.

## 3. Paired positive: `positive/clean-cache-demonstration`
The positive uses the unmutated record. Every conjunct on lines 507–526 holds against the stored values in section 1, except the gate digest check on line 522. That check passes only if the working-tree `tools/souji-evidence-cache.py` hashes to `dd279ba9…`.

- The oracle's `inputs()` (lines 29–37) hashes only the receipt and the inventory, not the gate file.
- `step-inventory.json` and `census/round-14/cache-demonstration.py` are byte-identical between `ff425ab` and the working tree. I did not inspect the gate file itself because it is not a named path. [INFERENCE] It may have changed after `ff425ab`.
- If it did, the positive becomes `False`. The null vector still passes, but then it no longer shows that the guard is what rejects it, because two conjuncts fail at once.

## 4. Counterexample: surviving mutant (drafted, not executed)
Mutation: on line 522, replace
`and isinstance(gate, dict) and gate.get("sha256") == gate_sha`
with `and isinstance(gate, dict)`.

Expected killing vector: none.
- `cache/shape/gate/null` and `cache/shape/gate/array` both still fail `isinstance`.
- The positives carry the correct digest.
- Every other `"gate"` path in the oracle (lines 2277–2785) is `cases[N].gate`, not the top-level gate.

So the oracle checks the gate's type but never its identity. The base already had the digest check, so this is a gap in the oracle's ability to catch regressions, not a new defect in `4f83fd2`.

Related: the predicate does not check `gate.sha256_after` or the top-level `gate_sha256_after` against the digest. Drift during the run is caught only by the producer's own `checks.gate_digest_recorded_and_unchanged`. This was not claimed this round; it is a tradeoff and does not block this vector.

## Impacted axes
- Calibration (claimed): this vector is valid. It shows only crash → False, not that the gate's identity is enforced.
- Operability (no-harm): improved. A malformed gate no longer raises.
- Coverage (no-harm): no regression, but the gate-digest binding has no killing vector.

## Smallest safe correction (for L1, not applied)
1. Add an oracle vector `cache/gate/sha256-mismatch`: `json_set [[["gate","sha256"], "0"*64]]`, want False. Optionally also `cache/gate/sha256-missing` with `json_set [[["gate"], {}]]`, want False.
2. Pin the gate file in `inputs()` by adding a `gate_sha256: dd279ba9…` check, so a working-tree drift returns exit 2 (bad input) instead of a silent positive failure or a vacuous negative pass.

## Limits
- Source-only review: no runs, probes or tests.
- Gate-file bytes were not inspected because the path is not named.
- `git show` and `diff` were used only on the named paths at the pinned revisions `41553ad`, `4f83fd2` and `ff425ab`.
- No admission or judgment is granted.
