# Round 20 once-only acceptance runner

## Deliverable and behavior

Added `/var/tmp/souji-r20-fixtures-12516f7/census/round-20/run-acceptance.py` only. It requires `--root`, `--rev` (full 40-hex), and `--output`; rejects a non-durable revision, a working-tree input mismatch, a root other than the lane used by the bounded r16/r18 fixtures, a HEAD/revision mismatch, or an existing output. It checks the current `input_snapshot`/`resolve_durable` contract against explicit r13/r14 measured closures and the acceptance source set. The selected input SHA-256 maps are recorded before and after each command and at the whole-run boundary. It records each command's argv, shell-quoted command, actual return code, exact UTF-8/surrogateescaped stdout/stderr, their raw-byte SHA-256 digests, expected summary, observed summary, and matched counts. It creates the result with `O_EXCL`; it never overwrites.

The audit baseline is extracted from the full preregistered baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` into a runner-owned `/var/tmp` temporary directory, then hashed and passed as `--base-tool`; the runner does not depend on a separate baseline worktree. Both r20 oracles and the tracked runner itself are included in the revision-bound input set, and the invoking runner bytes must equal the tracked copy. Only the extracted baseline auditor is separately hashed as an external input. The r14 cache demonstration runs only after the supplied revision is the committed current HEAD. The command list contains no broad legacy runner, live census/proc, signal action, private input, or host-state probe.

## Literal invocation and expected count

Run only after L1 commits the integrated bytes. Replace `<integrated-full40>` with that commit ID; the output path is a new exclusive artifact path:

```sh
python3 -B /var/tmp/souji-r20-fixtures-12516f7/census/round-20/run-acceptance.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev <integrated-full40> \
  --output /var/tmp/souji-r20-fixtures-12516f7/census/round-20/final-once.json
```

Expected command inventory: **18 commands**, with **18 matched** for a clean integrated run. The JSON retains each command result rather than only an aggregate. Commands 1–13 and their static expected summaries/case counts are fixed in `run-acceptance.py:269-322`; the five explicit counter commands are appended from the full-ID table at `:118-193`.

The five literal counter commands are the current replacements documented at `corpus/README.md:303-308`:

```sh
python3 -B census/round-13/count-claims.py 31984f473ce4bdab61a99b16cca194b28108cb81
python3 -B census/round-13/count-claims.py 6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6
python3 -B census/round-14/count-claims.py a31642d14006830ec62edf40b0354c3699728c4a
python3 -B census/round-14/count-claims.py 552cae4204b3ab818419ad8adbfef3a4da29a3e0
python3 -B census/round-13/count-claims.py b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
```

The first four expected complete JSON inventories are copied from the retained count receipts (`census/round-13/counts.json:1-20` and `census/round-14/counts.json:1-23`). For the fifth, the expected assertion is its exact measured full ID and `admitted_entries=6`, as documented at `corpus/README.md:284-288`; the actual complete JSON and every numeric leaf are still retained in the output.

Static expected summaries (not execution results):

- Auditor selftest: `SELFTEST pass=101 fail=0` by static AST expansion of the current 81-case list, two run-level controls, and 18 grant-matrix cases; revision helper selftest: `SUMMARY total=11 failed=0`.
- R20 auditor contract: `SUMMARY total=50 pass=50 fail=0 base_discriminating=11`. Its committed source lists 37 required primary case IDs and the summary (`tests/fixtures/r20-audit-contract.py:35-53, 482-484`); the 11 baseline discriminators are included because the baseline auditor is explicitly supplied.
- R20 caller binding runs with `--baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. Its expected inventory is 43 exact cases, with `INVENTORY\texact\texpected=43\tobserved=43\tmissing=-\tunexpected=-\tduplicates=0`; the summary requires 43 passes, 0 failures, 0 blocked, and a numeric baseline-mismatch count which the runner cross-checks against `BASELINE_MISMATCH` records.
- Migrated r19 audit-shapes preservation: 16 primary cases, with source-review expectation `SUMMARY total=16 failed=0 base_discriminating=11`; this is not substituted by the new r20 audit oracle. The expanded killpg, signal and live-census boundary cases are at `tests/fixtures/r19-seat-audit-shapes.py:71-91`. This is a static expected result, not an observation.
- R19 carry-wrap fixture: 4/0, 2 base discriminators; landing-gate selftest: 65/0; r18 pointer fixture: 11/0; r16 landing fixture: 15/0; carry invariant probe: 400 paragraphs, 562 boundary cuts, 842 mid-line cuts, 0 violations; r19 revision-pin fixture: 13/0, 6 base discriminators.
- Agreement-pin check: exit 0, no success text, one record checked. The checker prints only failures and returns zero when no problem exists (`census/round-19/verify-agreement-pin.py:177-187`).
- Clean cache demonstration: JSON `status=ok`, supplied revision recorded, 4 cases, 33 checks all true, no failed checks, 3 new-policy producer executions, unchanged inputs, and cleaned synthetic `/var/tmp` isolation. The source defines the 33 checks at `census/round-14/cache-demonstration.py:879-979` and emits the result at `:1204-1225`.

## Evidence and status

Source analysis confirms the runner delegates full-ID/durable-ref and exact regular-file/directory-byte checks to `tools/souji-rev-pin.py:94-179,182-222`. The five committed full-ID replacements are documented at `corpus/README.md:299-315`; the first four expected inventory receipts are retained in the count JSON files cited above. The r20 oracle source and tracked runner are revision-bound; the baseline auditor is the only temporary code artifact hashed separately. `tests/fixtures/r18-proc-census.sh` is included in `INPUT_PATHS` only for SHA-256 binding of the F5 source/fixture/counter read set; it is never executed. All expected summaries and counts are authored/static contracts, not fresh runs. No acceptance command, selftest, fixture, build, lint, formatter, or smoke was run while authoring this runner. No fresh acceptance output file has been created.

No tools were installed. No LSP route was exposed in the connected tool inventory; source references were located with bounded reads/grep, not a cold LSP response. No implementation blocker remains for this scoped deliverable; L1's post-integration run is intentionally deferred to the parent gate.
