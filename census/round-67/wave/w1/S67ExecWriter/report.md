# S67ExecWriter — round 67 candidate receipt writer (C1 value-checked GIT_COMMON_DIR)

Seat: S67ExecWriter (executor). Lane: souji (L1 SoujiR67 integrates). Base: `3639087917eaeb28719d7603110a6ec22782100e`
(`tools/souji-receipt-write.py` sha256 `a8c47d36…97fc`, verified before editing). Instruments and freeze as in
`census/round-67/preregistration-attempt4.txt`.

## Candidate

- Bytes: `candidate/souji-receipt-write.py`
- sha256: `b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725` (`candidate/SHA256SUMS`, relative name; `sha256sum -c` ok)
- Diff vs base: `candidate/base-to-candidate.diff` (six hunks, all additions except two single-line replacements)

## Hunk summary (one per hunk; all within the frozen writer delta list)

1. **Module docstring (base lines 58-61, new lines 61-68).** Adds the r67 paragraph after the r66 paragraph: the value check
   (set at all, empty included; resolution via `git rev-parse --git-common-dir` with GIT_COMMON_DIR scrubbed; realpath on both
   sides; refuse `RECEIPT-ENV-COMMONDIR-MISMATCH` on mismatch, empty value, or unresolvable repository; name only; equal value
   proceeds; every git call scrubs GIT_COMMON_DIR). The r66 paragraph, refusal classes and pins are untouched.
2. **`git()` helper (base line 90-92).** Delta 2: `"GIT_COMMON_DIR"` added to the scrub tuple with GIT_DIR and GIT_WORK_TREE.
   The docstring's scrub list is updated to name it (see deviation D2).
3. **New `_check_env_commondir(root)` (inserted before `write_receipt`, new lines 290-309).** Presence test via
   `"GIT_COMMON_DIR" not in os.environ`; empty value refuses; resolves through `git(root, "rev-parse", "--git-common-dir")`
   (so the r66 pins and the r67 scrub apply); a non-zero rc refuses; `os.path.realpath(os.path.join(root, out))` against
   `os.path.realpath(value)` (a relative value resolves against the writer's cwd, per L2). The refusal text is the frozen
   string and prints the variable name only.
4. **Call site in `write_receipt` (new line 338-339).** After the `GIT_INDEX_FILE` presence check and before the
   `REV_RE` rev-format check, as specified: `_check_env_commondir(root)`.
5. **Selftest cases 34-37 (new functions before `CASES`).**
   - 34 `env-commondir-mismatch` (W1/W2 shape): a copy of `.git` as the caller value refuses rc 2, no OUT, class token present, value not echoed.
   - 35 `env-commondir-match` (W3 shape): the equal absolute value and the relative `.git` run from the repository both accept.
   - 36 `env-commondir-empty`: empty value refuses.
   - 37 `env-commondir-unresolvable`: value set with `--root` in a directory outside any repository refuses (a
     `GIT_CEILING_DIRECTORIES` pin keeps discovery inside scratch).
6. **CASES table (new entries 34-37 appended after case 33).** Keeps all 33 r66 entries byte-identical.

Unchanged: all 33 r66 case functions, the r66 refusal classes (`RECEIPT-ENV-CONFIG-SET`, `RECEIPT-ENV-REDIRECT-SET`,
`RECEIPT-INDEX-ENV-SET`), the r66 pins in `git()`, and every other function.

## Deviations (each disclosed)

- **D1 — relative-value sub-check in case 35.** The spec names an equal-value accept. Case 35 also runs the relative value
  `.git` from the repository directory, because the frozen L2 rule canonicalizes a relative value against the writer's cwd
  and an equal-value test that only uses the absolute form would not exercise that rule. No new case number; no predicate changed.
- **D2 — `git()` docstring.** The docstring's scrub list now names GIT_COMMON_DIR. The spec asked for the tuple only; the
  docstring is updated so it does not lie about the scrub.
- **D3 — case 37 ceiling.** `GIT_CEILING_DIRECTORIES` is set to the scratch root in case 37 only, so repository discovery
  from the no-repository directory cannot climb into an ambient repository. Test-only environment; the writer does not
  read it and does not refuse or pin it (L3 unchanged).
- **D4 — blank-line hygiene.** Two extra blank lines introduced by the first edit pass were removed (before `write_receipt`
  and before `CASES`); the final bytes were re-measured (see Verification), so the receipts bind the final bytes.
- **D5 — SHA256SUMS.** Written with a relative file name so `sha256sum -c` runs inside `candidate/`.

## Verification (all run in scratch `/fast/scratch/hyaku/souji-r67/S67ExecWriter/`; receipts copied here)

- Writer selftest over the final candidate: `candidate/selftest.txt` → `SELFTEST cases=37 pass=37 fail=0`, EXIT=0.
  Cases 1-33 (the r66 set) are all `ok`; 34-37 are `ok`.
- C1 frozen trial, candidate in the new slot (`candidate/c1-trial.txt`, run from the lane cwd with `--new-tool` at the
  candidate path): `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS`,
  EXIT=0. Target met on the first run and again after the D4 blank-line fix (the receipt is from the final run).
  Row detail: W1 base accept / new refuse `RECEIPT-ENV-COMMONDIR-MISMATCH`; W2 base accept / new refuse `RECEIPT-ENV-COMMONDIR-MISMATCH`;
  W3 accept on both; E1-E6, MOD2, MOD3, SY3 and every other r66 row unchanged from the base slot.
- Do-nothing control, base bytes in the new slot (`candidate/c1-trial-control.txt`):
  `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=2 new_honest=6 class_mismatches=2 regress=PASS`, EXIT=1.
  This reproduces the frozen shape (`census/round-67/controls/c1-do-nothing.txt`): W1 and W2 accepted on the base writer.
- Non-vacuity of the new cases (round-66 M4 lesson). A scratch mutant of the final candidate with the
  `_check_env_commondir(root)` call replaced by `pass` (`candidate/selftest-mutant-nocall.txt`) gives
  `SELFTEST cases=37 pass=34 fail=3` (EXIT=1). The three failures are exactly 34, 36 and 37 (mismatch accepted rc 0; empty accepted
  rc 0; unresolvable reaches git and refuses only on the rev check). Case 35 passes on the mutant, as it must (it is an accept case).
- Base writer selftest (`candidate/selftest-base-slot.txt`): `SELFTEST cases=33 pass=33 fail=0`, EXIT=0 (the r66 suite on base bytes).

## Measurement notes

- The first no-call mutant was built from the base copy by mistake; it was discarded and the kill result was re-measured
  on a mutant built from the final candidate bytes (the `candidate/selftest-mutant-nocall.txt` file is that run).
- One scratch-mutant edit was mis-anchored by the edit tool's stale-line remap (a read cache returned an old view of the same
  path). The bad mutant was discarded; the final mutant was rebuilt on a fresh path, read fresh, and edited against the fresh tag.
  No edit to the candidate was affected: the candidate's last two edits were checked by the tool's returned view, and the
  final bytes were re-measured by selftest and the trial after them.
- Ambient environment: this shell has four `GIT_*` variables (`GIT_EDITOR`, `GIT_PAGER`, `GIT_SEQUENCE_EDITOR`,
  `GIT_TERMINAL_PROMPT`), none refused by the writer. The selftest inherits the ambient environment as the r66 cases already do; a
  caller running the selftest with `GIT_COMMON_DIR` set in the shell would see the pre-existing cases refuse. Not changed (convention).

## Not measured (named, not counted)

- Whether git itself exports `GIT_COMMON_DIR` into child processes (hooks, `git -c` children) was not probed in this seat. If it
  does, a writer launched that way with an equal value still accepts (W3 shape); a mismatched export refuses, which is the frozen behaviour.
- The honest-run cost of the r66 `git -c` refusal (L0 360) is unchanged by this delta and is not re-measured here.
- L3 (`GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES` on the writer's own calls) unchanged.
- Kill power of K3/K4/K6/K7 and the C2 counter are other seats' work; nothing here touches them.

## Tools

No tools were installed or upgraded by this seat. Python 3 and git were the host versions already on the system.

## Files delivered (all under `.ufo/waves/round-67/w1/S67ExecWriter/`)

- `candidate/souji-receipt-write.py`, `candidate/SHA256SUMS`
- `candidate/selftest.txt`, `candidate/selftest-mutant-nocall.txt`, `candidate/selftest-base-slot.txt`
- `candidate/c1-trial.txt`, `candidate/c1-trial-control.txt`
- `candidate/base-to-candidate.diff`
- `report.md` (this file), `S67ExecWriter.md` (same content, for the Report trailer)
