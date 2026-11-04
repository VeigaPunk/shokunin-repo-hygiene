# S59Connector — Sibling-Overlap Scan & Synthesis Report

## 1. Evidence

### Bounded Sibling-Overlap Scan (Read-Only)
A scan of named tools and gate directories across sibling repositories (`kaidoku-shokunin` and `kumitate-shokunin`) revealed clear, mature self-invocation patterns:

1. **`kaidoku-shokunin/tools/`**:
   - `tools/round-83/source-bind.py`:
     - Invokes own script as a clean subprocess CLI: `argv = [sys.executable, "-I", "-B", script, "--entry", entry, "--sid", sid, "--json-out", out]; completed = subprocess.run(argv, cwd=root)`.
     - Creates isolated fixture scratch via `tempfile.mkdtemp(prefix="source-bind-selftest-")` and guarantees cleanup in a `finally` block.
     - Executes each fixture case twice (`for run in (0, 1):`) to prove execution stability and determinism (`stable = len(findings) == 2 and findings[0] == findings[1]`).
     - Directly verifies that the process working directory was preserved: `working_root_preserved: os.getcwd() == root`.
   - `tools/round-83/attribution-audit.py`:
     - Enforces a mandatory caller scratch directory under `--selftest`: `if a.selftest and not a.work: raise ValueError('WORK_REQUIRED')`.
     - Executes own script via `[sys.executable, '-I', '-B', str(Path(__file__).resolve()), ...]`.
     - Validates both return code and structured findings: `child.returncode != expected_rc or (expected_id is not None and expected_id not in receipt.get('mismatches', []))`.
   - `tools/round-82/conjunction-gate.py` & `printed-command.py`:
     - Explicitly bifurcates internal in-memory unit tests from public `--cli-selftest` over isolated scratch fixtures.
     - Enforces negative controls that prove stub rejection / false-green rejection.
   - `tools/round-80/guard-battery.py`:
     - Mutates copies of the gate to prove that deleted guard clauses fail the gate's own selftest, satisfying the K43 mutant kill standard: *a clause exercised but not pinned is not covered*.

2. **`kumitate-shokunin`**:
   - *Directory Audit Finding*: `kumitate-shokunin` does *not* possess a directory named `tools/` (verified via glob and git log). Its gate, probe, and counter machinery is housed entirely in `scripts/`.
   - `scripts/control-replay.mjs`:
     - Self-invokes via `spawnSync(process.execPath, [process.argv[1], ...a], ...)`.
     - Builds hermetic fixture directories per case; asserts granular exit status mapping (`0` pass, `1` control-failed, `3` output-exists refusal, `4` frozen-drift refusal, `64` usage).
   - `scripts/counter-rerun.mjs`:
     - Embeds explicit mutation control seams (`AGREE_ALWAYS`, `PASS_STUB`).
     - Copies itself, flips seams, runs `spawnSync(process.execPath, [mutantPath, '--selftest'], ...)`, and asserts that mutants FAIL their own selftest, preventing false-green stubs.
   - `scripts/cite-check.mjs`:
     - Strictly bifurcates hermetic fixture checks (`--selftest`, touching zero live trees) from live integration tests (`--integrations`).
     - Implements child self-observation: spawns child `--selftest` with injected failure (`INJECT41=1`) and verifies it prints `VERDICT: FAIL` and exits 1.
   - `scripts/gate-mutants.mjs`:
     - Standardizes the K43 mutant kill contract: non-zero exit, `VERDICT: FAIL`, and stable case failure ordering.

### Cross-Lane Reuse & Ownership Limits
- Under `PROTOCOL.md` (§Invariants, local-first) and `AXES.md` (adjacency), each shokunin lane owns its internal codebase and repository boundaries. Cross-lane runtime execution or module importing (`import ... from kaidoku`) violates domain boundaries and creates untracked dependencies.
- Consequently, sibling tools serve as **architectural design patterns**, not direct code dependencies.
- Souji should adopt Kaidoku and Kumitate's proven patterns: public subprocess CLI execution (`sys.executable -I -B`), mandatory caller scratch directory (`--work DIR`), stable finding id matching against committed TSVs, and false-green stub rejection.

### Causal Independence & Risk of Thin Bookkeeping
- In `souji-shokunin/census/round-59/c1-counter.py`:
  - The counter measures only `SKILL.md` table syntax: `if row[2] != 'gate': findings.append('REGISTRY-KIND-MISMATCH')`.
  - The counter never executes `assessment-gate.py`, nor does it verify that `assessment-gate.py` has a functioning `--selftest`.
- **Causal Independence**:
  - The classification edit (`evidence → gate` in `SKILL.md`) and the underlying selftest repair (`assessment-gate.py --selftest` with CLI subprocess invocation and discrimination) are causally independent:
    1. Editing `SKILL.md` alone flips `c1-counter.py` to `assertions=1 mismatches=0` (PASS), even if `assessment-gate.py` is absent, broken, or a dummy stub.
    2. Implementing a flawless `assessment-gate.py` with full self-invocation leaves `c1-counter.py` failing with `REGISTRY-KIND-MISMATCH` (FAIL) if `SKILL.md` is unchanged.
- **Risk of Thin Bookkeeping**:
  - A documentation-only table cell modification satisfies the claim metric without providing executable gate substance.
  - Registering a tool as `gate` without an operable, discriminating `--selftest` violates `PROTOCOL.md` Gate standard (*"Every gate exposes a self-invocation mode over isolated fixtures ... a helper-only or model-only self-check does not satisfy this clause"*), introducing unverified claims and harming both `calibration` and `operability`.
  - To prevent thin bookkeeping, the round's declared milestone couples the classification edit with executable selftest substance: `S59ExecGate` (implements `assessment-gate.py` with CLI self-test and expected TSV) and `S59ExecDomain` (proves baseline domain discrimination via `acceptance.py`).

---

## 2. Affected Axes

1. **`calibration`** (current score: 7; lowest owned legacy score):
   - **Improved**: The registry row becomes truthful under the PROTOCOL Gate standard. By superseding the historical comparator with an operable gate and explicitly citing historical debt rather than papering over it, self-assessment quality is strictly preserved.
2. **`operability`** (current score: 8):
   - **Improved**: The new `assessment-gate.py` provides genuine CLI subprocess self-invocation over isolated caller scratch (`--work DIR`), deterministic exit codes (`0`, `1`, `2`), stable finding IDs (`FINDING ASSESSMENT-MISMATCH`), and false-green stub rejection.
3. **`coverage`** (current score: 8):
   - **Unharmed**: Scope remains strictly bounded to the two r57 matrix-derived SCORECARD calibration notes without expanding into unverified Markdown parser repairs (which remain explicitly listed under inherited debts).

---

## 3. Proposed Move: Dual-Arm Gate Conformance Binding

Synthesize the round's proposals (`S59ExecGate`'s gate implementation, `S59ExecDomain`'s independent acceptance trial, `S59ExecCounter`'s counter controls, and `S59Scribe`'s subprocess return-code sources) into a **Dual-Arm Gate Conformance Binding**:

1. **Registry Demarcation in `SKILL.md`**:
   - Retain `r58 assessment comparison` as a historical gate with its explicit conformance debt noted (`self-test: external discrimination fixture; counter has no self-invocation certification; conformance debt disclosed`).
   - Register `r59 assessment comparison` as the active, superseding row:
     `| r59 assessment comparison | gate | python3 -B census/round-59/assessment-gate.py --root LANE --rev FULL40 | 0 two corrections agree with committed matrix-derived values; 1 discrepancy data or unstructured input error; 2 CLI usage | python3 -B census/round-59/assessment-gate.py --selftest --work DIR | census/round-59/assessment-selftest-expected.tsv | read-only git blobs; isolated selftest under caller work | souji |`
2. **Subprocess Self-Invocation & Discrimination in `assessment-gate.py`**:
   - Adopt Kaidoku/Kumitate patterns: require `--work DIR` (fail-closed exit 2 if omitted).
   - In `--selftest`, create a unique temporary child directory under `--work DIR` and reap only that child in `finally`.
   - Invoke self CLI using `subprocess.run([sys.executable, '-I', '-B', str(Path(__file__).resolve()), ...], capture_output=True, text=True)`.
   - Assert exit codes and stable finding `FINDING ASSESSMENT-MISMATCH` against `assessment-selftest-expected.tsv`.
   - Enforce false-green stub rejection: confirm that an always-clean stub (`rc=0`, no findings) fails negative fixtures, emitting `control=FALSE-GREEN-REJECTED`.
3. **Decoupled Verification Protocol**:
   - Integration requires both arms to verify independently:
     - **Arm A (Classification)**: `c1-counter.py` passes the 1->0 kind check.
     - **Arm B (Executable Substance)**: `assessment-gate.py --selftest --work <scratch>` passes subprocess self-test with false-green discrimination.
     - **Arm C (Domain Acceptance)**: `acceptance.py` passes 4/4 public CLI cases over base and fixtures.

---

## 4. Risks & Mitigations

1. **Registry row collision or parsing ambiguity**:
   - *Risk*: Multiple rows matching `assessment comparison` could cause `c1-counter.py` to fail with `REGISTRY-ROW-SHAPE`.
   - *Mitigation*: `c1-counter.py` employs prioritized row selection: it matches `r59 assessment comparison` first, falling back to `r58` only if absent. The new row must be registered exactly once.
2. **Scratch directory residue / filesystem leakage**:
   - *Risk*: Self-test fixtures could leak temporary folders under system `/tmp` or write into the repository tree.
   - *Mitigation*: Enforce mandatory `--work DIR`; build all fixture Git repositories inside `tempfile.mkdtemp(prefix='assessment-fixtures-', dir=work)` and remove only the created directory in a `finally` block.
3. **Scope creep / false parser repair**:
   - *Risk*: Treating note-presence matching as a general Markdown parser repair.
   - *Mitigation*: Retain explicit debt boundaries in `assessment-gate.py` docstrings, `preregistration.txt`, and round notes. Note presence is verified against exact strings, preserving inherited parser debts.

---

## 5. Verification

The integration owner (`SoujiR59`) can verify the complete move with the following bounded sequence:

1. **Counter Controls Verification**:
   ```bash
   python3 -B census/round-59/c1-counter.py --selftest --work /fast/scratch/hyaku/souji-r59/check/
   ```
   *Expected outcome*: 4/4 cases pass (`unchanged`, `prose-forgery`, `duplicate-forgery`, `positive`), exit 0.

2. **Classification Check over Candidate Revision**:
   ```bash
   python3 -B census/round-59/c1-counter.py --root . --rev <candidate-rev>
   ```
   *Expected outcome*: `SUMMARY assertions=1 mismatches=0`, exit 0.

3. **Gate Subprocess Self-Test & Discrimination**:
   ```bash
   python3 -B census/round-59/assessment-gate.py --selftest --work /fast/scratch/hyaku/souji-r59/check/
   ```
   *Expected outcome*: Subprocess CLI execution passes all cases against `assessment-selftest-expected.tsv`, reports `control=FALSE-GREEN-REJECTED`, and exits 0.

4. **Domain Acceptance Trial**:
   ```bash
   python3 -B .ufo/waves/round-59/w1/S59ExecDomain/acceptance.py --tool census/round-59/assessment-gate.py --work /fast/scratch/hyaku/souji-r59/check/ --root . --rev <candidate-rev>
   ```
   *Expected outcome*: 4/4 asserted domain cases match (`committed-honest`, `one-correction-omitted`, `prose-wrong-count-forgery`, `both-missing`), exit 0.

---

## 6. Inventory & Receipts

- Delivery directory: `.ufo/waves/round-59/w1/S59Connector/`
  - `scan-inventory.json`: Machine-readable audit of Kaidoku and Kumitate self-invocation patterns.
  - `causal-independence-receipt.json`: Formal analysis of classification edit vs. selftest substance independence.
  - `synthesis-recommendation.json`: Detailed specification of Dual-Arm Gate Conformance Binding.
- Owned scratch directory `/fast/scratch/hyaku/souji-r59/S59Connector/` was cleaned before completion.
- No production edits, fleet edits, or git mutations were made.
