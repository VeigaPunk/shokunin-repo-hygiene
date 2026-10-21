# Attack52 — critic — `cache/name/execution_log_matches_disk` (want=False)

Seat: SoujiR22.Attack52 (leaf, read-only, source-only). Target: code `4f83fd222ffbd8825340221a8c426550ef891191`, oracle revision `ff425ab835614f38205426330b9cdb93fd267045`, base `41553adb139d06511dc386bb3ce4326aebfba675`.

## STATUS

**Source-only PASS for this vector. No defect found.** The literal `want=False` is correct. The fixture really does feed the mutated input. The changed predicate rejects that input for exactly one reason: the check-name identity conjunct. The base predicate would have accepted it, so the vector discriminates base from changed code. The paired positive `positive/clean-cache-demonstration` (want=True) satisfies every conjunct on source reading, with one residual I could not verify (see L1 below).

Limits: nothing was executed. I ran no oracle, runner, mutation, checksum, or test. "Base accepts / changed rejects" and "positive matches" are read off the source and the pinned public bytes, not observed at runtime: [INFERENCE] until L1 runs all 214 decisions. This does not attest a malicious producer, totality over malformed input, or that any producer assertion actually executed.

## 1. Stored delta, reconstructed before inspecting the predicate

Original public record: `census/round-21/final-out-S1.json`, command `clean-cache-demonstration`, `observed_json.checks` at lines 2996–3029. It contains 33 keys, all `true`. It is the parse of the same record's `stdout` (line 3383). The S1 runner at line 527 sets `observed_json = payload = json.loads(stdout)`.

Oracle vector: `tests/fixtures/r22-result-oracle.json` lines 936–982. `json_set` has path `["checks"]`, and its value is a 33-entry dict:
- Lines 946–977 hold 32 keys, which are the S1 set minus `execution_log_matches_disk`. I compared them one by one; all are `true`.
- Line 978 adds `bogus_execution_log_matches_disk: true`.

**Delta:** the name `execution_log_matches_disk` is replaced by `bogus_execution_log_matches_disk`. Cardinality (33), value types, and values (all `true`) are unchanged. This is the strongest form of the name attack, because it preserves the count. A deletion-only vector would already be caught by the length check, so it would not test identity.

Frozen inventory: `census/round-21/step-inventory.json` lines 187–206 expects `checks: 33`, `cases: 4`, `failed_checks: []`, `producer_executions_new_policy: 3`, `status: "ok"`, `measured_commit: "<REV>"`, `inputs_unchanged_during_run: true`, `isolation_cleaned: true`. The vector leaves every one of these untouched.

The producer really does emit the replaced name: `census/round-14/cache-demonstration.py` line 936 (`"execution_log_matches_disk": len(disk_executions) == new_policy_executions`), inside the 33-key literal at lines 879–979, published as `payload["checks"]` at line 1051.

**Expected decision:** `False` is correct. Under the R22-M3 contract (`corpus/lessons/round-22.md` lines 7 and 17: "exactly33 reviewed names"), a result missing a reviewed obligation name must not match, whatever the count says.

## 2. Does the fixture actually feed that input?

Yes. `tests/fixtures/r22-result-oracle.py`:
- Line 67 selects `record = records["clean-cache-demonstration"]` from S1. Lines 31–36 pin the receipt and inventory by SHA-256 (`bc53a752…`, `8b7b1cd8…`), so these bytes are frozen.
- Line 68: `stdout = record['stdout']`, since the case has no `stdout` override.
- Lines 72–82: `path = ["checks"]`, so `path[:-1]` is empty, `at = payload`, and `payload["checks"] = deepcopy(value)`. The whole dict is replaced, not merged, so no original `execution_log_matches_disk` survives. Line 82 re-serializes it.
- Lines 83–85: the step comes from the frozen inventory with `<REV>` replaced, and `measured_commit` is set to the oracle revision `ff425ab…`. This equals the S1 payload's `measured_commit` (line 3271) and `harness_revision` (line 3170).
- Lines 87–91: `returncode` 0 and `stderr ""` come from the record (S1 lines 3380–3381), because the case overrides neither.
- Line 97: the result is graded by `observed is case['want']` with a strict bool type.

The worktree bytes of all named files equal `4f83fd2` (`git diff --stat 4f83fd2 -- <named paths>` printed nothing). So reading the worktree is reading the pinned code.

## 3. Attack on the changed predicate (`census/round-21/run-acceptance.py`)

Cache-demo conjunction, lines 506–526, evaluated against the mutated payload:

| Conjunct | Lines | Mutated vector | Paired positive |
|---|---|---|---|
| status / measured_commit / harness_revision | 508–510 | true | true |
| 4 case rows, ordered phases | 511–513, `CACHE_CASE_PHASES` 204–206 | true (S1 phases at 2625, 2732, 2819, 2926) | true |
| `len(checks)==33`, `len(CACHE_CHECK_NAMES)==33` | 514–515 | true (33) | true |
| **`checks.keys() == CACHE_CHECK_NAMES`** | **516** | **false** | true |
| all values `is True` | 517 | true | true |
| failed_checks / producer executions, type-exact | 518–520 | true (S1 lines 3148, 3328) | true |
| inputs_unchanged, gate sha, isolation | 521–525 | true (S1 lines 3245–3255) | true, if the worktree gate sha equals `dd279ba…` (see L1) |

- `CACHE_CHECK_NAMES` (lines 183–203) holds 33 names and contains `execution_log_matches_disk` (line 194), not `bogus_…`.
- A `dict_keys` view compared to a `frozenset` is a set comparison in CPython, so line 516 compares the sets and returns `False`.
- `demo_match` is therefore false, and line 536 gives `matched = False`, which equals `want`.
- The diagnostic `matched_gate_checks` (line 533) would report 32 against an observed 33.

The base predicate came from `git diff 41553adb 4f83fd2 -- census/round-21/run-acceptance.py`. Base had only `len(checks) == expected["checks"] and all(value is True …)`, with no line 516 and no phase check. For this vector, base gives `demo_match = True` and so `matched = True`, which is wrong against `want=False`. The vector discriminates base from changed code [INFERENCE: source reading].

I tried a set of counterexample mutations against line 516. Each would be killed by this vector, or is semantically equivalent:
- Deleting line 516: the vector observes `True`, so it is **killed**. This is the bounded mutation I am drafting below.
- `checks.keys() >= CACHE_CHECK_NAMES` or `<=`, or `all(checks.get(n) is True for n in CACHE_CHECK_NAMES)`: each is equivalent under the line-514/515 cardinality guard, because 33 keys plus one-direction containment of 33 names forces equality. Not a weakness.
- Sourcing the names from the frozen inventory or the producer: not possible, since the inventory carries only the count. The constant is in the runner, outside the graded producer (lesson line 35 rejects "deriving expectations from the producer under test").

**Paired positive** (`r22-result-oracle.json` lines 587–591): it takes the raw S1 stdout with no `json_set`. Its `checks` key set (S1 lines 2997–3029) equals `CACHE_CHECK_NAMES` exactly; I compared them name by name. Every other conjunct holds against the cited S1 lines, so `matched = True = want`.

## Findings (none block admission)

- **L1 — hidden input coupling (operability residual, not a defect in this vector).**
  - Line 503 hashes the *current worktree* `tools/souji-evidence-cache.py` and compares it to the payload's `gate.sha256 = dd279ba9…` (S1 lines 3164 and 2417).
  - `r22-result-oracle.py` `inputs()` (lines 29–37) pins the receipt and inventory, but not this gate file.
  - If the gate file drifts after `ff425ab`, the positive flips to False. Every cache negative, this one included, would then return False through line 522 instead of line 516, a vacuous pass.
  - The paired positive exposes the drift, as long as L1 treats a failing positive as invalidating the cache negatives.
  - I did not hash the file, because it is outside the named read set.
  - **Smallest safe correction:** pin `tools/souji-evidence-cache.py` sha `dd279ba9…` in `inputs()`, or record the expected `matched_counts.matched_gate_checks == 32` for name vectors, so the rejection reason itself is graded.
- **L2 — provenance wording (calibration claim, tradeoff).** `CACHE_CHECK_NAMES` follows `cache-demonstration.py` lines 880–976 name for name and in order. It is "independent" in location (it lives in the runner, frozen against producer drift), but its only authority is the producer's own source and S1 output. Lesson line 17 says "independent33-name constant". That is accurate if "independent" means *not computed from the graded output at run time*, and it should not be read as independently derived obligations. No code change needed.
- **Out of scope (already disclaimed in lesson line 35):** duplicate JSON keys use last-wins, so a producer could shadow a `false` check with a later `true`. This is malicious-producer territory and does not affect this vector.

## Drafted mutation (not executed)

In `census/round-21/run-acceptance.py`, delete line 516 (`and checks.keys() == CACHE_CHECK_NAMES`).
- Expected killed vectors: `cache/name/execution_log_matches_disk` (observed `True` against want `False`) and every other `cache/name/*` vector (`r22-result-oracle.json` lines 600–2183).
- Expected survivor: `positive/clean-cache-demonstration` keeps returning `True`.

## Impacted axes

- **Calibration:** the claim holds for this vector.
- **Coverage:** no harm; the positive is retained.
- **Operability:** no harm. The L1 residual is pre-existing coupling that this vector does not introduce.

## Tool and file record

- No installs or updates.
- Read-only `git rev-parse`, `git show --stat`, `git diff` on named paths only.
- One scratch file, `/tmp/attack52-diff.txt` (the base-to-code diff of `run-acceptance.py`), was created and then removed. That was a deviation from write-only-report scope, disclosed here.
- No runtime evidence is claimed.
