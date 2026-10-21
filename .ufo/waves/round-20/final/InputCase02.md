# InputCase02: `r13-helper-syntax-invalid` (C2 caller-case falsifier)

Seat: SoujiR20-2.InputCase02. Read-only, source-only leaf. Judged on operability.
Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` (lane HEAD equals pin).
Applicable caller: `census/round-13/run-verification.py` only. The `r13-` case prefix maps to `ROUND13`. The r14, targeted and demo callers were not read.

Blocking findings: none, so no STATUS: PARTIAL marker. The pinned caller refuses the case correctly. The defects below concern falsifier strength and diagnosability.

## Answers

- **Behavioral or wiring?** Behavioral for the dirty-bytes predicate: the real entrypoint runs as a subprocess and a real refusal is observed. Vacuous for the syntax dimension: the outcome is identical to `r13-helper-dirty` and would be identical for any helper bytes that differ from HEAD.
- **Prerequisite masquerade?** For this mutation, none. The only refusal reached is the binding check. In general, yes: the path-substring predicate also accepts prerequisite refusals. A bounded counterexample is in section 5.
- **Input consumed by this caller?** Yes, as bytes only, at caller line 131. The helper is never compiled or executed in this case.
- **Inert changed byte?** No. The byte is `def r20_invalid(:`.
- **Exit 2 / no stdout / no output?** Source-derived to hold at caller lines 132, 144 and 146 (expected, not executed).
- **Baseline producer witness?** None for this case (section 6).

Axes:

| Axis | Result |
|---|---|
| A1 reason fidelity | Fails the name. The pass comes from line 132. The `exec_module` compile (135) and the `SyntaxError` handler (143) are unreachable. |
| A2 mutation fidelity | Fails the contract. The byte is non-inert, contrary to fixture docstring line 7. |
| A3 predicate specificity | Fails. `changed_path in combined` admits prerequisite refusals (section 5). |
| A4 witness coverage | Fails. No red-before witness for this case (section 6). |
| A5 diagnosability | Weak. Fixture detail line 696 drops the refusal text. |

## 1. Entrypoint trace (pinned)

Harness, `tests/fixtures/r20-input-binding.py`:
- `caller_command` 660-671 builds `python -B census/round-13/run-verification.py --round 20 --output census/round-20/r20-r13-helper-syntax-invalid.json --retry-failed --previous census/round-13/verification.json`.
- `caller_refusal` 673-697 runs it with cwd set to the synthetic sandbox. The env sets `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` to an ambient decoy repo (676-679).
- `mutation_plan` 742 has `("helper-syntax-invalid", HELPER, False)`. `run_caller_matrix` 781 sets `invalid_syntax`. `mutate_and_call` 718-719 appends `b"\ndef r20_invalid(:\n"` to `tools/souji-rev-pin.py`. The original bytes are restored in `finally` after line 724.

Caller, `census/round-13/run-verification.py`:
- `main` 405. Argparse 408-413 accepts `--retry-failed` and `--previous`. `validate_output` 342 passes: round floor is 20 from the sandbox `census/round-20`, and the output is absent. `validate_previous` 384 passes. `execute` 445 calls `resolve_revision()` at 448.
- `resolve_revision` 121:
  - 124: `git rev-parse HEAD`. The `GIT_*` filter at 57-61 strips the decoy env.
  - 127-128: nonregular check, not triggered (regular file).
  - 129-130: `git show HEAD:tools/souji-rev-pin.py`, which yields the clean committed bytes.
  - 131-132: `helper.read_bytes() != committed` raises `ValueError("tools/souji-rev-pin.py differs from measured commit")`.
  - 143-146: prints `run-verification: refused: tools/souji-rev-pin.py differs from measured commit (no record written)` to stderr, then `SystemExit(2)`.
- Not reached for this mutation: 133-135 (`spec_from_file_location`, `exec_module`, i.e. compile), 136-141 (`resolve_durable`, `input_snapshot`), the `SyntaxError` member of the except tuple at 143, and the record write in `execute`.

Expected harness line (source-derived, not executed): `CASE pass r13-helper-syntax-invalid changed=tools/souji-rev-pin.py; exit=2 changed_path_named=1 output_absent=1 suite_stdout_absent=1`.

## 2. Changed byte

Not inert. `inert_suffix` (651-657) feeds every other helper, wrapper and sources mutation in the r13 matrix. This case alone writes `def r20_invalid(:`. Fixture docstring line 7 promises "an inert comment/whitespace mutation (or one valid added knowledge record)". The same branch (718-719) serves the r14, targeted and demo `*-helper-syntax-invalid` cases. I did not read those callers, so whether they share the early refusal is unverified.

## 3. Input closure

- Caller `MEASURED_PATHS` (92-) contains `tools/souji-rev-pin.py` (line 105). The fixture reads that literal via AST (`parse_path_list`) and adds `census/round-13/verification.json` as the previous-evidence extra.
- All 23 closure paths exist at the pin (`git cat-file -t`): 22 measured paths, three of them directories, plus the previous file.
- The fixture copies closure bytes from the working tree (`expand_closure` 212-220 reads `root`), not from the pin. Lane HEAD equals the pin, so no divergence is present now. The fixture never asserts it.

## 4. Predicate and exit semantics

- Fixture 687-696 (r13 branch): `returncode == 2 and changed_path in combined and output_absent and stdout == ""`. All four hold through lines 132 and 144 for this mutation.
- Harness-level blocked runs also exit 2 (`summary(blocked=True)` at 109, called at 978 and 1033). Only the `SUMMARY ... blocked=1` line tells them apart.

## 5. Masquerade analysis and bounded counterexample

- Masquerade for this mutation: none. Only the binding refusal at 132 is reached.
- Masquerade in general: the predicate accepts any refusal whose text contains `tools/souji-rev-pin.py`. Two prerequisite paths do this:
  - (a) Line 128: symlinked or nonregular helper.
  - (b) Lines 129-130: any failure of `git show HEAD:tools/souji-rev-pin.py`. The `CalledProcessError` text embeds the command list, including the path, and line 144 prints it. This is stdlib behavior, not executed.

**Bounded counterexample (source-derived, not executed).** Remove the `GIT_*` filter at caller lines 57-61. The harness sets `GIT_DIR` to the decoy (fixture 677), so line 124 returns the decoy's HEAD. Lines 129-130 then run `git show <decoy-HEAD>:tools/souji-rev-pin.py`, which fails before the compare at 131. The result is exit 2, stderr naming `tools/souji-rev-pin.py`, empty stdout and no output. The case PASSES whatever the helper bytes are, including an unmodified helper. So `r13-helper-syntax-invalid` and `r13-helper-dirty` cannot detect the ambient-repository regression the decoy exists to catch. The regression is still caught across the matrix: the other r13 cases (wrapper, frozen, sources, knowledge, prior) name files other than the helper, so they should FAIL on the helper-named refusal.

Secondary counterexample (source-derived): replacing the helper with a symlink triggers line 128 and passes the same predicate.

## 6. Witness coverage

- `BASELINE_PAIR_CASE_IDS` (110) and the pairs list in `run_baseline_pairs` (818 onward) contain no `*-helper-syntax-invalid` entry.
- The only r13 helper pair is `baseline-r13-helper` (825). It applies the inert suffix through `apply_pair_mutation` (801) and `inert_suffix`.
- So this case has no red-before witness. Only the inert byte predicate has one.

## 7. Non-blocking findings and smallest corrections (for L1; not applied)

- **N1 Label overclaims (A1).** Rename the four `*-helper-syntax-invalid` cases to a dirty-before-compile name. Or add a committed-invalid variant that passes line 132 and asserts the compile-path refusal at 143-146 with a SyntaxError-specific predicate. No fixture code loads a syntax-invalid helper; `helper_controls` (595-) has no such control. [INFERENCE: CPython renders `str(SyntaxError)` with the basename, so `tools/souji-rev-pin.py` would be absent from that message and the path predicate would FAIL a correct refusal.]
- **N2 Predicate too weak (A3).** Replace `changed_path in combined` with an exact expected fragment per case. For helper-dirty that is `tools/souji-rev-pin.py differs from measured commit`. For helper cases, reject `Command '` (CalledProcessError text).
- **N3 Docstring drift (A2).** Fixture line 7 must name the non-inert syntax probe, or the probe moves out of the inert matrix.
- **N4 No witness (A4).** Add a baseline pair for each syntax variant kept as a distinct predicate. Otherwise document the case as green-only.
- **N5 Diagnosability (A5).** Put the first stderr line into `caller_refusal`'s detail (line 696). Without it, neither a FAIL nor a masquerade PASS can be audited from the report.
- **N6 Working-tree source (minor).** Assert `HEAD == pin` in the harness, or read closure bytes with `git show <pin>:<path>`, so the falsifier tests the pinned build.

## 8. Execution log and tooling

Read-only at the pin. No runtime, no code import, no builds or tests. Commands run:
- `git show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path>` for `tests/fixtures/r20-input-binding.py`, `tools/souji-rev-pin.py` and `census/round-13/run-verification.py`.
- `git rev-parse --verify <pin>^{commit}`, and `git rev-parse HEAD` in the lane.
- `git grep -n <pattern> <pin> -- <named file>` on the three named files above.
- `git cat-file -t <pin>:<path>` for 23 named closure paths.

Not read: the other three callers, census roots, the operator-sweep tree, corpus knowledge bodies, working-tree file contents. Tool installs or updates: none. Subagent dispatch: none.

Checks for L1 to run once at the pin: `python3 -B tests/fixtures/r20-input-binding.py`, then read the `CASE ... r13-helper-syntax-invalid` line. The section 5 regression may be rehearsed only in a throwaway clone; if it is, expect `r13-helper-syntax-invalid` and `r13-helper-dirty` to still pass.
