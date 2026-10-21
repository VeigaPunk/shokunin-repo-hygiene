# Round 20 Final Falsification Report: C1/C2 Causal Separability, Lowest Calibration Duty, and Independent Frozen Oracles

- **Seat**: `SoujiR20-2.FinalCausality`
- **Role**: UFO-FSD Connector
- **Pinned Commit**: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`
- **Baseline Commit**: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (round-19 non-author closure tip)
- **Judged on**: Calibration (lowest non-retired axis)
- **Scope**: Read-only source analysis; no target code execution; no directory recursion; no subagents.

---

## 1. Name the Axes

Under the shokunin fleet governance framework (`AXES.md`, `SCORECARD.md:12-20`):

1. **Calibration** (Score: **7**, lowest non-retired axis): Governed by the round-20 **C1** repair duty. Following the outside rejection of round 19 (`corpus/lessons/round-19-verifier-spotcheck.md:66-70`), calibration was harmed by overbroad wildcard sibling grants. The C1 repair duty demands exact explicit parsed-write grants, slot-qualified scratch allowances, and byte-bound audit receipts. Calibration 7 is the primary governing constraint of the round.
2. **Operability** (Score: **8**): Governed by the round-20 **C2** repair duty. Addresses un-migrated short-ID commands and incomplete working-tree input bindings across `r13`/`r14` callers, requiring fail-closed refusal on dirty or unlisted inputs before output generation.
3. **Coverage** (Score: **8**): **Held**. No C3/coverage claim is declared for round 20 (`preregistration.txt:2`). F5 process-residue observation remains Core for list-only nomination; reap authority and `NAMESPACE_SHA256` remain strictly HELD under operator round-18 requests (`PROVINCE.md:105-115`, `SKILL.md:210-215`).

---

## 2. Evidence and Context

### 2.1 Pinned Authority and Contract Declarations
- **Contractual Independence**: `.ufo/waves/round-20/preregistration.txt:2` expressly specifies:
  > *"Claims: C1 calibration (lowest 7, numerical delta0 legacy-unmapped)... C2 operability (8, numerical delta0)... C1 and C2 independently testable. No C3/coverage claim."*
- **Lowest Axis Duty**: `SCORECARD.md:14-16` records calibration at 7 (below operability 8 and coverage 8). Under shokunin principles, the lowest non-retired axis is the governing bottleneck. Higher-axis activity (C2) must not obscure, weaken, or serve as a proxy for the lowest-axis repair (C1).
- **No Numeric Gain from Test Count**:
  - `SCORECARD.md:15-18`: *"No runtime improvement is pre-claimed; numeric delta remains 0, legacy-unmapped."*
  - `corpus/lessons/round-20.md:11-13`: *"Numeric legacy scores have no new mapping and do not move from favorable fixture counts."*
  - `corpus/QUALITY.md`: Q18 establishes that gate passes and fragment counts do not certify safety; Q19 warns that shell spelling or marker counts are not enforcement; Q23 commands that capability wording must match the exact boundary exercised, forbidding extrapolation from aggregate volume.

### 2.2 The Two Independent Frozen Oracles
1. **C1 Frozen Oracle (`tests/fixtures/r20-audit-contract.py:1-40`)**:
   - Authored in response to `OracleAuditCases.md` and `FixtureOracle.md`.
   - Operates in complete isolation: creates synthetic specs, transcripts, and manifests in temporary scratch (`/var/tmp`); directly tests `tools/souji-seat-audit.py`'s `run()` API across 50 cases (38 self-tests + 12 baseline-comparison cases).
   - Discriminating witness: Exactly 11 `base_discriminating` cases reproduce the historical round-19 over-authorizations against baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`.
   - Substrate dependency: Zero Git repository checks, zero reliance on `tools/souji-rev-pin.py`, zero coupling to working-tree cleanliness.
2. **C2 Frozen Oracle (`tests/fixtures/r20-input-binding.py:1-45`)**:
   - Probes caller-level fail-closed refusal (`run-verification.py`, `run-targeted.py`, `cache-demonstration.py`, `souji-rev-pin.py`) across 43 cases (36 self-tests + 7 baseline pairs).
   - Injects mutations and untracked additions into isolated `/var/tmp` Git repositories, asserting exit code 2 and silent stderr refusal before any output record.

### 2.3 The Shared Aggregate Runner (`census/round-20/run-acceptance.py`)
- In `run-acceptance.py`, 18 separate commands are sequentially executed in a single monolithic script:
  - Step 1: `auditor-selftest` (103 passes)
  - Step 2: `revision-helper-selftest` (11 passes)
  - Step 3: `r20-audit-contract` (50 passes, 11 base-discriminating)
  - Step 4: `r20-input-binding` (43 passes, baseline mismatch tracking)
  - Step 5: `r19-seat-audit-shapes` (17 passes, 12 base-discriminating)
  - Step 6: `r19-carry-wrap` (4 passes, 2 base-discriminating)
  - Step 7: `landing-gate-selftest` (65 passes)
  - Step 8: `r18-landing-pointers` (11 passes)
  - Step 9: `r16-landing-gate` (15 passes)
  - Step 10: `carry-invariant-probe` (400 paragraphs)
  - Step 11: `r19-revision-pin-fixture` (13 passes, 6 base-discriminating)
  - Step 12: `agreement-pin-check` (1 check)
  - Step 13: `clean-cache-demonstration` (4 cases, 33 checks)
  - Steps 14–18: 5 historical counter verification commands
- Aggregate volume: Over 360 individual check assertions across 18 processes.

---

## 3. Explicit Contradictions

1. **Substrate Coupling vs Contractual Independence**:
   - `preregistration.txt:2` states: *"C1 and C2 independently testable."*
   - Yet in `run-acceptance.py:297-298`, the aggregate runner imports `tools/souji-rev-pin.py` (the primary C2 under-test subject) via `load_pin_helper(root)` and immediately calls `pin.resolve_durable()`.
   - At lines 323, 330, and 344, `combined_snapshot(pin, ...)` executes before and after *every* step, walking all 25+ files in `INPUT_PATHS`.
   - If C2's `tools/souji-rev-pin.py` suffers an import failure, traversal error (as analyzed in `InputR13Fixtures.md`), or working-tree drift in an unrelated file (e.g. `corpus/knowledge/`), `run-acceptance.py` refuses with exit code 2 *before running C1's `r20-audit-contract.py`*.
   - Consequently, C1 calibration verification is causally dependent on C2 operability infrastructure inside the aggregate runner.
2. **Lowest Calibration Duty Masked by Aggregate Conflation**:
   - `run-acceptance.py:375-388` computes a single boolean:
     `"all_matched": len(results) == EXPECTED_COMMANDS and all(item["matched"] for item in results)`
     and exits `0 if record["all_matched"] else 1`.
   - If C1 passes with zero defects (all 50 cases clean and 11 baseline discriminators verified), but an unrelated C2 counter in step 17 encounters a discrepancy, `run-acceptance.py` exits 1 with `all_matched: false`.
   - Conversely, a partial runner failure can obscure whether the lowest-axis duty (calibration 7) was discharged. Collapsing 18 heterogeneous commands into a single scalar exit code violates causal separability at the verification boundary.
3. **Test Count Inflation vs Calibration Proof**:
   - The aggregate runner accumulates over 360 passing assertions across 18 commands.
   - However, under shokunin scoring rules (`SCORECARD.md`), test count provides **zero numeric gain** (delta 0; calibration remains at 7).
   - In shokunin discipline, calibration is the exactness of boundary discrimination (falsifiability), not fixture volume. Accumulating unit tests (e.g., expanding internal selftests from 73 to 103 checks) does not improve calibration if the positive delivery path is unexercised at the caller level (`FixtureOracle.md:15-30`). The only true calibration evidence for C1 consists of the 11 baseline-discriminating cases in `r20-audit-contract.py`.

---

## 4. Proposed Move (Compatible Synthesis)

**Decouple C1 (Calibration 7) acceptance authority from C2 (Operability 8) infrastructure by establishing the independent frozen oracle (`tests/fixtures/r20-audit-contract.py`) as a sovereign, self-contained acceptance authority, while restructuring the aggregate runner (`run-acceptance.py`) to emit a decoupled per-claim verdict ledger (`c1_matched`, `c2_matched`, `legacy_matched`) rather than a monolithic binary pass/fail.**

### Core Elements of the Move:
1. **Sovereign C1 Authority**:
   - Recognize `python3 tests/fixtures/r20-audit-contract.py --tool tools/souji-seat-audit.py --base-tool <baseline>` as the primary, stand-alone proof of C1 calibration.
   - This command runs without Git working-tree dependencies, without `tools/souji-rev-pin.py`, and without multi-file snapshot checks, directly proving the removal of the 11 round-19 broad-authorization defects.
2. **Decoupled Reporting in Aggregate Acceptance**:
   - In `census/round-20/run-acceptance.py`, structure the output JSON record to partition command results into explicit claim facets:
     - `c1_calibration`: steps 1 (`auditor-selftest`), 3 (`r20-audit-contract`), 5 (`r19-seat-audit-shapes`).
     - `c2_operability`: steps 2 (`revision-helper-selftest`), 4 (`r20-input-binding`), 11 (`r19-rev-pin`), 13 (`clean-cache-demonstration`), 14–18 (historical counters).
     - `legacy_carry_governance`: steps 6 (`r19-carry-wrap`), 7–9 (landing gates), 10 (`carry-invariant-probe`), 12 (`agreement-pin`).
   - Retain `all_matched` for total round integration, but provide independent booleans (`c1_all_matched`, `c2_all_matched`) so that external verifiers have non-conflated evidence for each axis.
3. **Strict Adherence to Calibration Duty**:
   - Explicitly bar any claim of score elevation (7 → 8) based on test count (the 360+ checks).
   - Ground calibration closure solely upon the exact removal of over-authorizations evidenced by the 11 baseline-discriminating cases.

---

## 5. Second-Order Effects Across Surfaces

- **Runtime Surface**: Outside verifiers (spotcheckers) can run the C1 oracle instantly in isolation without setting up clean Git worktrees, avoiding the 36 full-directory snapshot hashing passes required by `run-acceptance.py`.
- **Contract Surface**: Resolves the contradiction between `preregistration.txt:2` ("independently testable") and `run-acceptance.py` (monolithically coupled). Both claims retain their independent verification paths.
- **Substrate Surface**: Eliminates the circular dependency where testing C1's seat-audit parser required importing and executing C2's revision helper.
- **Verification Surface**: Prevents higher-axis (operability) failures or fixture noise from masking whether the lowest-axis duty (calibration 7) was genuinely discharged. Maintains clean auditability under `corpus/QUALITY.md` Q18, Q23, and Q39.

---

## 6. Risks and Scoped Trade-Offs

- **Risk of Verification Divergence**: If two separate verification commands exist, an outside auditor might run only one.
  - *Mitigation*: `run-acceptance.py` retains step 3 (`r20-audit-contract`) in its sequence. The aggregate runner still checks everything, but the structured JSON output prevents misattributing a C2 counter failure to a C1 calibration defect.
- **Risk of Premature Admission**: Treating the independent oracle pass as a self-declared score increase.
  - *Mitigation*: Strictly enforce the rule that numeric scores do not move from fixture counts (`SCORECARD.md:15-18`). Calibration remains at 7 until an independent, non-author round-closure verdict is rendered.

---

## 7. Verification

Verification of this move requires confirming the following read-only properties:

1. **Standalone Execution of C1 Oracle**:
   - `tests/fixtures/r20-audit-contract.py` does not import `tools/souji-rev-pin.py` or execute Git commands.
   - It requires only `tools/souji-seat-audit.py` and the extracted baseline auditor, successfully evaluating all 50 cases (38 pass, 11 base-discriminating).
2. **Standalone Execution of C2 Oracle**:
   - `tests/fixtures/r20-input-binding.py` does not import `tools/souji-seat-audit.py`.
   - It evaluates all 43 cases (36 pass, 7 baseline pairs) against `tools/souji-rev-pin.py` and caller scripts independently.
3. **Structural Independence in Aggregate Schema**:
   - `census/round-20/run-acceptance.py` records per-command details in its `commands` list, allowing unambiguous separation of C1 and C2 results without altering the underlying acceptance contract.

---

Report: .ufo/waves/round-20/final/FinalCausality.md
