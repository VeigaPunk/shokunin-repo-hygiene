STATUS: PASS — the exact no-harm guard is defined, grounded in the pinned decision code and frozen vectors, and its non-claims are separated from the original frozen18 portability result. Source-only review: no acceptance step, oracle, or probe was executed, no tools installed. Every claim below is file-read evidence unless marked [INFERENCE].

## 0. Byte provenance (supersedes earlier working-tree reads)

Parent notice (2026-10-21): L1 is integrating the current runner, so working-tree bytes may drift. Baseline claims here are anchored to `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`, read in full this session. Executed digest facts (the only executed commands in this review; byte-digest reads, not probes):

- `git show 41553adb…:census/round-21/run-acceptance.py | sha256sum` → `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`
- working-tree `census/round-21/run-acceptance.py` → `02e3b06dad7421d43f27b87a41568e6577c1ad64a89a933dc12ee8408f4bc32c` — **already diverged from base** (expected: L1 integration in flight). Earlier working-tree reads are superseded; where compared, the decision code quoted below was identical in both, but only the base bytes are authoritative for baseline claims.
- `git show 41553adb…:census/round-21/step-inventory.json | sha256sum` → `8b7b1cd8d19561d9f4e8f06e797038b03379350cb3f3932edf04bda7aa7d1310` = working-tree `census/round-21/step-inventory.json` digest — the frozen inventory is **byte-identical** to base; all inventory citations stand unchanged.

All code quotes in §1–§4 are verbatim from the base41553adb… bytes; anchors are symbol + quoted line, not line numbers (base and working-tree offsets differ).

Scope: round22 C1 calibration — the three admitted OPEN r21 predicate defects (JSON bool/int scalar confusion; summary stderr accepted despite success; cache checks counted rather than identified) — and the single question this seat owns: what exactly may the repair change without harm, and what does the no-harm guard NOT attest?

## 1. Objects the guard quantifies over

- **Frozen18** = `census/round-21/step-inventory.json` `steps` (18 rows; `EXPECTED_COMMANDS = 18`, enforced by the runner's inventory equality refusal, `run-acceptance.py` `main()`: "acceptance commands differ from the frozen r20 inventory"). It is a projection of expected shapes with `<ROOT>`/`<REV>`/`<BASELINE>` placeholders.
- **all18 real output records** = the 18 observed per-step execution rows retained by a baseline acceptance run in its exclusive JSON record (`schema: "souji-round21-replay-acceptance-v1"`): each `commands[]` row carries `returncode`, `stdout`, `stderr`, `stdout_sha256`, `stderr_sha256`, `matched`, plus `input_sha256_before/after` snapshot maps at record level.
- **Decision function**: `summarize_result(step, returncode, stdout_bytes, stderr_bytes, revision, root)` → `result["matched"]`, a conjunction of `returncode == 0`, empty `failure_lines(...)`, and the per-kind branch (`summary` / `counter` / `cache-demo`); `counter` and `cache-demo` additionally require `not stderr`; `cache-demo` also reads live environment inputs (`revision`, gate bytes under `root`).

These are distinct objects. The round-21 result the fleet already banked — clone-isolated, byte-bound replay parity against the frozen inventory from any local repository containing the revision (Q48, `census/round-21/run-acceptance.py` clone/fetch/detach-checkout/pin flow) — is a **portability result about the baseline harness**. It is not what round 22 must preserve, and preserving all18 records does not re-attest it.

## 2. The exact guard

Let `S18` be the 18 step names from the frozen inventory, `o_s` the real output record of step `s` retained in the baseline acceptance record, `E` the identical environment inputs (same `--rev`; cache-demo gate digest taken from the retained `input_sha256` snapshot, not re-read), `M_base` the baseline summarizer's `matched` (base bytes `41553adb139d06511dc386bb3ce4326aebfba675`), `M_new` the repaired summarizer's `matched`.

> **No-harm guard (exact):** for every `s ∈ S18`: `M_base(s, o_s, E) = true` implies `M_new(s, o_s, E) = true`.
> Equivalently: `A_base ∩ S18 ⊆ A_new ∩ S18`, where `A_*` is the accepted-row set of each implementation over the all18 real records.

One-directional, finite, over real records only. The repair tightens the predicate (removes false greens), so `M_new` may — and must — reject synthetic producer outputs that `M_base` accepted; that is the calibration goal, outside the guard's domain. If baseline accepted all 18 real rows, the guard collapses to "all 18 stay accepted"; if any real row was rejected at baseline, the guard says nothing about it (its stability is the calibration vectors' business, not no-harm).

Draft checker (source-only, not executed; operates entirely on retained bytes — L1 runs it after all seats):

```python
def no_harm_guard(baseline_record, inventory, repaired_matched_by_name):
    """Empty list == guard holds. baseline_record: the exclusive JSON record of
    the baseline (base41553adb…) acceptance run (schema
    souji-round21-replay-acceptance-v1). inventory: frozen
    census/round-21/step-inventory.json. repaired_matched_by_name: the repaired
    summarizer's matched, recomputed from each retained row's identical
    (returncode, stdout, stderr) and identical environment inputs (--rev and
    the cache-demo gate digest read from the record's input_sha256 snapshot,
    never re-run)."""
    steps = inventory["steps"]
    if len(steps) != 18:
        raise ValueError("not the frozen 18-step all18 set")
    rows = {row["name"]: row for row in baseline_record["commands"]}
    violations = []
    for step in steps:
        name = step["name"]
        row = rows.get(name)
        if row is None:
            violations.append({"step": name, "reason": "missing from baseline record"})
        elif row["matched"] and not repaired_matched_by_name.get(name):
            violations.append({"step": name,
                               "reason": "baseline-accepted all18 record rejected after repair"})
    return violations
```

**Operability (offline decidability):** the guard is evaluable without re-running any step. Retained `stdout`/`stderr` are `decode_exact` (`utf-8`, `surrogateescape`) of the raw bytes, and `surrogateescape` encode is the exact inverse, so recomputation from the record reproduces the original bytes and the retained `stdout_sha256`/`stderr_sha256` verify the round-trip [INFERENCE from the codec semantics named in code, not executed]. The only environment-derived input, the cache-demo `gate_sha`, is recoverable from the record's `input_sha256_before` snapshot of `tools/souji-evidence-cache.py`.

## 3. What the guard does NOT claim (the confusion this seat forbids)

1. **Not universal implication** `∀(s,o): M_base ⇒ M_new` over arbitrary producer outputs. False by design: the committed synthetic result-oracle exists precisely to show outputs baseline accepted and the repair rejects. The guard quantifies over the 18 real records only.
2. **Not predicate portability** `M_base(s,·) ≡ M_new(s,·)` as decision functions on all inputs. The original frozen18 result attested portability of the *baseline* harness across clones; it never attested predicate equivalence, and no-harm inherits nothing of the kind.
3. **Not a correctness attestation on unseen/malicious producers.** Preregistration is explicit: "no arbitrary malicious-producer attestation or executed-command authentication is claimed". The repaired predicate's decisions are attested only on (a) the literal reviewed oracle vectors and (b) the all18 real records.
4. **Not portability of the repaired harness.** A Q48-style clone-isolated replay of the changed implementation is a separate exercise; passing no-harm does not imply it, and it is not claimed.
5. **Not executed-command authentication** for any historical projection.

## 4. Hazards — where each defect repair could breach the guard

All18 = 13 `summary` rows (auditor-selftest, revision-helper-selftest, r20-audit-contract, r20-input-binding, r19-seat-audit-shapes, r19-carry-wrap, landing-gate-selftest, r18-landing-pointers, r16-landing-gate, carry-invariant-probe, r19-revision-pin-fixture, agreement-pin-check, clean-cache-demonstration) + 5 `counter` rows (r13-counter-31984f4, r13-counter-6f8ee0f, r14-counter-a31642d, r14-counter-552cae4, r13-counter-b576341; the first four `exact_json: true`, b576341 partial-dict `exact_json: false`).

- **H1 — bool/int scalar equality (`counter` branch).** Baseline compares `json_match = observed == expected` (verbatim, `summarize_result`, `counter` branch, `exact_json` path — base41553adb… bytes) where expected values are JSON ints; Python evaluates `True == 1`, `False == 0`, so a real output with `true`/`false` at an int-expected position is accepted at baseline. Note `numeric_leaves` already excludes bools (`isinstance(value, int) and not isinstance(value, bool)`), so only the equality itself is type-loose — the repair must fix the scalar comparison, not the leaf counter. Guard conflict arises **iff** a real counter record carries booleans at int-expected positions; all expected fields are counts (`F2_entry: 0`, `tiers.A: 29`, `admitted_entries: 6`, …) produced by count-claims programs [INFERENCE: real outputs are genuine ints; decidable offline from the retained `observed_json`]. If a real record does carry a boolean, guard and repair collide and L1 must surface the collision — never reinterpret the guard to hide it.
- **H2 — summary stderr.** The `summary` branch gates on `matched = matched and summary_match and pass_match` with no stderr condition; `counter`/`cache-demo` already require `not stderr` (the r21 asymmetry). `failure_lines` recognizes only `FAIL\t`/`CASE\tFAIL` vocabulary, so arbitrary stderr text slips through. Repair adds a stderr gate to the summary branch. Guard conflict arises **iff** a real summary record has nonempty stderr — decidable offline from retained `stderr`/`stderr_sha256` without execution.
- **H3 — cache checks identified, not counted (sharpest surface).** The frozen inventory row for `clean-cache-demonstration` records only `checks: 33`, `cases: 4`, `failed_checks: []`; the baseline `demo_match` checks `len(checks) == 33` and `all(value is True …)`, never names. The repair must compare the identified check-name set. **The source of the expected-name set decides the guard's strength for this step:** if the set is read out of the real baseline record itself, the guard is tautological for this row (cannot fail; must be disclosed as a limit); if it comes from the committed, independently reviewed oracle vectors, the guard genuinely tests that the reviewed names equal the real 33 names produced by `census/round-14/cache-demonstration.py` at the measured revision. The review requires the latter; deriving expectations from the observed record would be circular.
- **H4 — totality.** "Reject malformed producer data without a crash" (preregistration). Baseline wraps `json.loads` in `except (ValueError, TypeError)` per branch; the repair's added type validation must keep every malformed input on the per-step `matched = False` path, never convert it into a process-level refusal (`exit 2`, no record) or an uncaught exception. This is adjacent to but not contained in the record-set guard; a crash regression is harm even though no all18 record flips.
- **H5 — frozen-bytes discipline.** The pinned r21 runner/inventory bytes live at the measured revision; `inventory_projection(...) == frozen["steps"]` is a runner-internal refusal. The repaired predicate must therefore be the round-22 artifact evaluated over retained records and oracle vectors — never an edit to `make_steps`/`step-inventory.json` that would trip the inventory-equality refusal or mutate pinned bytes.
- **H6 — comparison medium.** The r21 matrix's `summaries_equal` compares selected summary fields and omits stderr and raw stdout — the exact class the stderr defect lives in. Before→after calibration must be per-record decision vectors from the result-oracle (literal reviewed pass/fail per case), never matrix-signature equality; signature parity can hide an stderr regression.
- **H7 — baseline-record provenance (new, from base bytes).** The base runner self-binds: `combined_snapshot` computes `runtime_runner = read_regular(Path(__file__))` vs `committed_runner = read_regular(root / "census/round-21/run-acceptance.py")` and raises `"running acceptance runner differs from committed measured bytes"`. Two consequences for the guard's evidentiary basis: (a) a valid baseline record can only be produced by runner bytes equal to the committed bytes at the replayed revision — a drifted working-tree runner (current state, digest `02e3b06d…`) cannot run a base-revision replay of itself; (b) the guard must therefore consume a baseline record either already retained from the r21 run or produced by a clone at a revision whose committed runner bytes are the executed ones. L1 must name which record the guard is evaluated against; a guard evaluated against a record of unknown byte provenance attests nothing.

## 5. Verification status

- Read (named files/paths only): `census/round-21/run-acceptance.py` — working tree first, then **in full via `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py` after the parent notice (§0 authoritative)**; `census/round-21/step-inventory.json` (all 18 rows, both working tree and base — byte-identical); `census/round-14/cache-demonstration.py` (skeleton; check names intentionally not enumerated — see H3); `.ufo/waves/round-21/w2/AttackRunnerStepResults.md`; `.ufo/waves/round-22/preregistration.txt`; `corpus/QUALITY.md` (Q24, Q39, Q41, Q45 contexts).
- Executed (declared, byte-digest reads only — no acceptance step, oracle, test, or probe): the three sha256 comparisons in §0. No LSP available in this session, so no semantic-reference results are claimed; no tools installed (nothing to record under the tooling directive).
- Decidable later, offline, by L1 from committed bytes alone: guard evaluation per §2 (retained records + repaired predicate recomputation), H1/H2 real-record shapes from retained `observed_json`/`stderr` fields, H3 expected-name-set provenance, H7 named baseline-record identity.
