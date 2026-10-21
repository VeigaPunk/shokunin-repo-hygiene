# Attack58 — critic: vector `cache/shape/gate/array` (want=False)

Seat: SoujiR22.Attack58 (critic, leaf, source-only). Target: code `4f83fd222ffbd8825340221a8c426550ef891191`.
No tests, runs, probes, or edits were made outside this report. No tools were installed or updated.

## STATUS

**PARTIAL (source-only).** The vector's expected decision (`False`) is correct. The fixture really feeds the intended input (top-level `gate` replaced by `[]`). The current predicate rejects it with a typed `False` and does not crash. The positive control `positive/clean-cache-demonstration` reaches the same conjunct, so the vector is not vacuous.

Commit `4f83fd2`'s own changes do not affect this vector or its positive. Its only cache-demo change is the `RecursionError` catch, and this payload decodes normally.

The adjacent attack finds a real coverage gap. No one of the 214 vectors mutates `gate.sha256`, so a mutation that deletes the digest comparison while keeping the type guard survives the whole oracle (draft M58-c below).

**Evidence:** pinned bytes, hashes, and source line reads only.
**Limits:**
- No execution: all observed values below are derived by reading source.
- I did not read `tools/souji-evidence-cache.py` because it is not a named path. The positive's digest equality on the live tree is therefore `[INFERENCE]`.

## 1. Stored delta, reconstructed from public bytes before reading the predicate

- Oracle entry (`tests/fixtures/r22-result-oracle.json:2226-2238`): `step_name=clean-cache-demonstration`, `json_set=[[["gate"], []]]`, `group=malformed`, `want=false`.
- Input pins (`r22-result-oracle.json:3-6`) match the bytes on disk:
  - `final-out-S1.json` sha256 = `bc53a752…38fe`
  - `step-inventory.json` sha256 = `8b7b1cd8…1310`
- Pin versus tree (`git show 4f83fd2:<path>` compared with the working file) is byte-identical for `run-acceptance.py`, `r22-result-oracle.py`, and `r22-result-oracle.json`. The vector is present at the pin (1 match).
- Public original record (`final-out-S1.json`):
  - `commands[]` begins at line 28.
  - The `clean-cache-demonstration` record spans 2506–3383, with `returncode 0` (3380), `stderr ""` (3381), and `stdout` (3383).
  - Its decoded `observed_json` has a top-level `gate` **object** (3149–3168) with keys `exists`, `installed_default`, `matches_installed_default`, `path`, `reason`, `regular`, `sha256=dd279ba9…39d6`, `sha256_after`, `size_bytes`, and `symlink`. It matches `input_sha256["tools/souji-evidence-cache.py"]` (2495) and `gate_sha256_after` (3169).
  - Nested `cases[i].gate` values (for example 2619 `null`, and 2706/2789/2896 objects) are separate per-case keys and are not touched by this delta.
- Frozen inventory (`step-inventory.json:187-206`): `kind=cache-demo`, with `expected_summary` = `{status ok, measured_commit <REV>, cases 4, checks 33, failed_checks [], producer_executions_new_policy 3, inputs_unchanged_during_run true, isolation_cleaned true}`. There is no gate field. The gate binding comes from the runner, not from the inventory.
- **Reconstruction:** decode the original `stdout`, set `payload["gate"] = []`, and leave every other byte-derived field equal to the positive record.

### Feed check: does the fixture actually feed this input?

Yes:
- `r22-result-oracle.py:58` builds `records` from `receipt['commands']`.
- Line 67 selects the record.
- Line 68 takes the original `stdout` (the vector has no `stdout` override).
- Lines 69-71 do not apply (no `stdout_nested_array_depth` key).
- Lines 72-82: `path=["gate"]`, `path[:-1]=[]`, so `at = payload` and then `payload["gate"] = deepcopy([])`. This sets the top-level key, then re-serializes with compact `json.dumps`.
- `returncode` and `stderr` fall back to the record values (0 and `""`) at lines 88-90.
- Line 85 rewrites `expected_summary.measured_commit` to the oracle revision. The runner ignores that field and uses `revision` directly (`run-acceptance.py:509-510`).

### Is the expected decision correct?

Yes. A list carries no gate digest binding. The oracle contract (`json:8`, "case stable-field/shape mismatches") and lesson R22-M5 (`corpus/lessons/round-22.md:19`, "malformed cache gate/isolation null/list … crashes") both demand rejection. Literal `False` is right.

## 2. Predicate attack: this vector

The cache-demo path is `run-acceptance.py:493-536`.

- **Decode (495-497):** succeeds, so `payload` is a dict.
- **Line 500:** `gate = payload.get("gate")` gives `[]`.
- **Every conjunct before 522 holds.** All of these values come from the unmodified public payload:
  - `status "ok"` (3352).
  - `measured_commit` (3271) and `harness_revision` (3170) both equal `ff425ab…`, the oracle `revision`.
  - The 4 top-level `cases` phases are in `CACHE_CASE_PHASES` order (2625, 2732, 2819, 2926).
  - `checks` has exactly the 33 `CACHE_CHECK_NAMES` keys, all `true` (2997-3029, compared with runner lines 184-203).
  - `failed_checks` is `[]` (3148), `producer_executions_new_policy` is int `3` (3328), and `inputs_unchanged_during_run` is `true` (3245).
- **Line 522:** `isinstance(gate, dict)` is `False`, so `demo_match` is `False`. Line 536 then gives `matched=False`, a bool.
  - Oracle line 97: `observed is case['want']`, so the vector **PASSES** in the changed implementation and raises no exception.
- **Base (`41553adb`, cache block ~446-479):** `payload.get("gate", {}).get("sha256")`. With the key present it returns `[]`, and `[].get` raises `AttributeError`.
  - Oracle lines 94-96 give `observed=None`, so the vector **FAILS** at base. It discriminates, but it discriminates a crash (operability), not a false green (calibration). `json_exact` and type-guard work do not convert a base false-accept here.
- **Origin of the guard:** line 522's guard came from `36c78ba` (`git show 36c78ba` hunk +132). The parent of `4f83fd2` already has it (line 520). `4f83fd2` changes only:
  - `numeric_leaves`, which is used by `counter` only, not cache-demo.
  - The `RecursionError` catch at 468 and 496.

  Neither is reachable with different behaviour for this shallow payload. The vector is neutral to the change under review.
- **Failure-line scan (396):** the re-serialized compact JSON is one line starting with `{`, so it has no `FAIL\t` prefix and the scan cannot short-circuit the result.

## 3. Paired positive: `positive/clean-cache-demonstration` (`json:587-591`, want=True)

- Same record, unmodified pretty `stdout`. All conjuncts listed in section 2 hold. Then:
  - Line 522 is `isinstance(dict)`, which is True.
  - It requires `gate["sha256"] (dd279ba9…) == sha256(ROOT/tools/souji-evidence-cache.py)`, read at line 503.
  - Lines 523-525: `isolation.cleaned` is `true` (3248) and `residue` is `[]` (3255).
- **Fragility (no-harm and operability axes):** `inputs()` (`oracle.py:28-37`) pins only the receipt and the inventory. The gate tool bytes that line 503 reads are **unpinned**.
  - Any later edit to `tools/souji-evidence-cache.py` flips the positive to `False` while this negative stays `False`.
  - The oracle receipt would report `R22-RESULT-CONTRACT` as if the summarizer had regressed.
  - The current tool digest was not read: `[INFERENCE]` that it is still `dd279ba9…`.
  - This vector's kill power against M58-a and M58-b does not depend on it.

## 4. Drafted mutations (not executed)

| id | edit at `run-acceptance.py:522` | expected oracle effect |
|---|---|---|
| M58-a (false-green) | `and (not isinstance(gate, dict) or gate.get("sha256") == gate_sha)` | **Killed** by `cache/shape/gate/array` (observed `True`, want `False`) and by `cache/shape/gate/null`. The positive is unchanged. |
| M58-b (revert to base) | `and payload.get("gate", {}).get("sha256") == gate_sha` | **Killed** by `cache/shape/gate/array` and `gate/null` (`AttributeError`, so observed `None`). |
| M58-c (drop binding) | `and isinstance(gate, dict)` (delete the `sha256` comparison) | **Survives all 214.** The positive stays `True` and null/array stay `False`. No vector sets `["gate","sha256"]`: the grep of `json_set` paths shows only `["gate"]` (2219, 2233) and per-case `["cases",i,"gate",…]`. |

## 5. Counterexample, impacted axes, and smallest safe correction

**Counterexample:** M58-c. A summarizer that accepts any dict gate, including `{}` or `{"sha256": "0"*64}`, passes the full frozen oracle. The changed implementation does compare the digest, so this is an oracle coverage gap, not a defect in the code under review.

**Impacted axes:**
- **Calibration:** the gate-identity half of the cache result contract is untested by the oracle.
- **Operability:** this vector only witnesses the base crash being fixed, which is consistent with R22-M5's operability class.
- **Coverage/no-harm:** the positive depends on unpinned live gate-tool bytes.

**Smallest safe corrections** (fixture-only; the oracle is append-only, so the existing 214 expectations stay untouched):

1. Append `cache/shape/gate/sha256-mismatch`: `json_set [[["gate","sha256"], "0000…0000" (64 zeros)]]`, want `false`. This kills M58-c. Optionally append `cache/shape/gate/empty-object` (`[["gate"], {}]`), want `false`.
2. Bind the gate-tool digest the positive depends on:
   - add `gate_tool` and `gate_tool_sha256 = dd279ba9…39d6` to the oracle header;
   - verify it in `inputs()` the same way as the receipt and inventory pins, so tool drift reports as input tampering (exit 2) rather than a result-contract failure (exit 1).

No change to `run-acceptance.py` is needed for this vector.

Report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/w2/Attack58.md
