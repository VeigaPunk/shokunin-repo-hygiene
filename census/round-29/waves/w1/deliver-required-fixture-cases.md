# Required fixture cases for v2 — mutation-test results, base capture tool

Source probe: `tools/souji-wave-evidence-capture.sh` @ lane HEAD `b8cb4b31ce80e2e3314b88e85d40ea9873180804`,
fixture `tests/fixtures/r28-wave-evidence-capture.sh` (6 cases + supplementary), run in scratch
`/var/tmp/souji-r29-MutateCaptureFixtureBase/`. Baseline before any mutant: `cases=6 pass=6 control=TAMPER-REJECTED`, rc 0.

12 tool mutants run through the base fixture. **8 survive**; 5 are real coverage gaps, 3 are equivalent
(unkillable by any black-box case). The 5 gap survivors + the r28-trio model define the required case set.

## Required cases (each verified: pristine passes, target mutant fails)

| id | kills (survivor) | case | pristine | mutant |
|----|------------------|------|----------|--------|
| RC1 | m02 "verify the disk copy" (r28 defect 1) | capture a receipt, flip one byte in a receipt **payload** file (not `manifest.sha256`), run `--verify` | rc 4 | m02 rc 0 |
| RC2 | m11 "ignore git's ignore rules" (r28 defect 2) | wave dir holds `__pycache__/junk.pyc` plus a root `.gitignore` naming it; capture | rc 0 and `__pycache__/junk.pyc` present in receipt | m11 rc 4, file absent |
| RC3 | m12 "drop symlink accounting" (r28 defect 3) | symlinks with absolute (`/etc/hostname`) and nested-relative (`sub/inner.txt`) targets; capture | rc 0 and `readlink` of each receipt link equals the source target verbatim | m12 target rewritten to basename |
| RC4 | m07 "skip the source-mismatch comparison" | wave dir already contains its own `summary.tsv`; capture must refuse (same for a source-provided `manifest.sha256`) | rc 4 | m07 rc 0, source bytes silently replaced |
| RC5 | m10 "drop round-argument validation" | `bash tool <lane> 26x` | rc 1 (usage) | m10 rc 2 (falls through to missing-source) |

Probe script (receipt of the above): scratch `killcases.sh`; pristine line:
`RC1_verify_payload_tamper=4 RC2_cap=0/file=0 RC3_cap=0/targets=0 RC4_source_summary=4 RC5_bad_round=1`.

## Retain unchanged (already load-bearing, proved by kills)

- Case 3 (tampered `manifest.sha256` -> rc 4, fixture lines 77-98): sole guard that kills manifest-blind
  verify mutants (m08 "verification-always-passes" killed: rc 0 vs want 4, control not set).
- Case 4 fifo refusal (m03 killed: rc 0 vs want 3) and case 5 traversal (m09 killed: rc 2 vs want 1).
- Promote the supplementary symlink check (fixture lines 126-147) to a numbered case: it is what kills
  m04 (`cp -a` -> `cp -rL` dereference, supplementary FAIL) but it sits outside `cases=6`.

## Equivalent mutants — NOT required cases (report-only)

- m01 drop manifest self-exclusion at the generation site (tool line 157): `find` runs before
  `manifest.sha256` exists and every capture clears the destination first — site unreachable.
- m05 drop inline `LC_ALL=C` on the manifest sort (tool line 157): global `export LC_ALL=C` (tool line 35)
  pins every sort anyway.
- m06 drop the nested src/dst refusal (tool lines 90-95): dead lexical branch — with both paths derived
  from the same validated absolute lane, neither prefix can match. Tool-owner simplification candidate,
  not a fixture matter.

## Verdict table

| mutant | mutation (tool line) | fixture rc | verdict | killed by |
|--------|----------------------|-----------|---------|-----------|
| m01 | self-exclusion off, generation (157) | 0 | SURVIVED (equivalent) | — |
| m02 | verify-only hashes source, never receipt payload (172-193) | 0 | SURVIVED | RC1 |
| m03 | special-file refusal dropped (82) | 1 | KILLED | case 4 |
| m04 | `cp -a` -> `cp -rL` (100) | 1 | KILLED | supplementary |
| m05 | inline LC_ALL=C off (157) | 0 | SURVIVED (equivalent) | — |
| m06 | nested src/dst refusal dropped (90-95) | 0 | SURVIVED (equivalent) | — |
| m07 | source-vs-receipt comparison dropped (192-195) | 0 | SURVIVED | RC4 |
| m08 | `verify_ok=0` -> `verify_ok=1` both sites | 1 | KILLED | case 3 |
| m09 | lane `..` traversal check dropped (57-59) | 1 | KILLED | case 5 |
| m10 | round numeric validation dropped (53-55) | 0 | SURVIVED | RC5 |
| m11 | silent `__pycache__` drop after copy (104-105) | 0 | SURVIVED | RC2 |
| m12 | receipt link targets rewritten to basename (104-105) | 0 | SURVIVED | RC3 |
