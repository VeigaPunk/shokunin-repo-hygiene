# S57executor01 — C1 independent reproduction

Verdict: **AGREE for all six assigned steps.** No counter, fixture, expected matrix, or other implementation bytes changed. Axes addressed: calibration (C1 reproduction), operability (explicit commands, retained outputs and exit codes).

All evidence below is under `.ufo/waves/round-57/w1/S57executor01/` (relative to the lane). Each executed command and its observed rc is retained in `commands.json`; individual command receipts contain merged stdout/stderr and an explicit `EXIT=` trailer. The independent driver is `reproduce.py`; it does not invoke the frozen matrix runner.

## 1. Fresh fixture construction — AGREE

Command:
```sh
TMPDIR=/fast/scratch/hyaku/souji-r57/S57executor01 python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/fixtures/build-fixtures.py --work /fast/scratch/hyaku/souji-r57/S57executor01/f --manifest /fast/scratch/hyaku/souji-r57/S57executor01/f/fixture-manifest.tsv
```
Observed in `build.txt`:
```text
MANIFEST /fast/scratch/hyaku/souji-r57/S57executor01/f/fixture-manifest.tsv
EXIT=0
```
The copied manifest (`fixture-manifest.tsv`) yielded exactly 36 C1 rows. The builder also constructs its C2 fixtures; these were not measured in this seat.

Setup disclosure: the initial call found that `--work` must already exist (`--work must exist: .../f`, `EXIT=1`; retained in `build-initial-missing-work.txt`). The driver then created a fresh empty `f` before construction. No frozen code changed. Builder inspection confirmed its repository-toplevel guard before the first fixture commit.

## 2. Both arms, explicit per-fixture calls — AGREE

Executed 36 v5 and 36 v6 counter commands independently. Every fully expanded command, full output, and exit code is retained in `v5-<fixture>.txt` and `v6-<fixture>.txt`, and indexed by `commands.json`. Command form (actual concrete values are in those receipts):
```text
TMPDIR=<scratch> python3 -B <absolute-counter> --root <fixture-dir> --rev <tip> --base <chosen-base> --record-sha256 <manifest-sha> --sources-rev-before <tip> --sources-rev-after <tip> --scratch <scratch>
```
Counter paths were `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-56/c1-counter.py` and `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/c1-counter.py`. Only F5-REWRITE, F6-RECORD-DRIFT, and F27-BINARY-NUMSTAT used their manifest base; all other rows used tip as base.

Outputs: `c1-matrix-v5.tsv`, `c1-matrix-v6.tsv`, with full ordered finding IDs. B4 and C4 each had two v6 `CORRECTION-IN-FENCE` findings, both explicitly `hidden_by=inline` in their raw receipts. C6, F29, F17, F18 and F19 each exited 0 with no findings under both arms.

## 3. Byte-for-byte matrix comparisons — AGREE

Commands:
```sh
cmp -s /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57executor01/c1-matrix-v5.tsv /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/records/matrix-dryrun/c1-matrix-v5.tsv
cmp -s /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57executor01/c1-matrix-v6.tsv /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/records/matrix-dryrun/c1-matrix-v6.tsv
```
Both printed nothing and returned `EXIT=0` (`cmp-v5.txt`, `cmp-v6.txt`). No row-level reference diff was needed because both entire TSVs matched byte for byte.

## 4. Independently derived T3/T4 numbers — AGREE

Derivation command: `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57executor01/reproduce.py` (the same execution that produced the matrices; comparison uses each row's exit and ordered `findings_all`, not the arm label).

Observed (`derived.json`):
- Rows differing between arms: **2**, exactly B4-INLINE-NBSP-OPENER and C4-INLINE-CLOSED-COMMENT.
- v5 exit-0 count: **10/36**.
- v6 exit-0 count: **8/36**.
- Every non-B4/C4 row identical in exit and full ordered finding IDs: **true** (34 rows).

| Fixture | v5 exit / findings_all | v6 exit / findings_all |
|---|---|---|
| B4-INLINE-NBSP-OPENER | 0 / `-` | 1 / `CORRECTION-IN-FENCE,CORRECTION-IN-FENCE` |
| C4-INLINE-CLOSED-COMMENT | 0 / `-` | 1 / `CORRECTION-IN-FENCE,CORRECTION-IN-FENCE` |

These are expected arm differences, not disagreements with the frozen reference.

## 5. v6 selftest — AGREE

Command:
```sh
TMPDIR=/fast/scratch/hyaku/souji-r57/S57executor01 python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/c1-counter.py --selftest --work /fast/scratch/hyaku/souji-r57/S57executor01/st
```
Observed in `selftest.txt`:
```text
SELFTEST pass cases=36
EXIT=0
```
All per-case full ordered finding comparisons are retained in that receipt.

## 6. Real-lane freeze recompute — AGREE

Command:
```sh
TMPDIR=/fast/scratch/hyaku/souji-r57/S57executor01 python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d749f7ee081ec1b382b2f92577eb22bfba1c7761 --base b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch /fast/scratch/hyaku/souji-r57/S57executor01
```
Observed in `real-lane.txt`:
```text
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=d749f7ee081e base=b4ef0bc84ada
EXIT=0
```

## Bounds, risks and retained evidence

- Scratch deleted in the driver's `finally`; `cleanup.txt` records `scratch_exists=false`.
- No tool installation/update, background job, delegation, lane git mutation, or external-state remediation.
- No source symbol edits/refactors; no LSP facility is exposed in this seat's tool inventory.
- All retained writes are this report and the exclusive seat evidence directory: driver, manifest, two matrices, 72 raw arm receipts, build receipts, two cmp receipts, derivation JSON, selftest receipt, real-lane receipt, command index, cleanup receipt.
- No blockers or observed matrix mismatches. This is reproduction of the frozen fixture predicate, not an independent proof of all Markdown comment semantics or a C2 assessment. Full finding list means ordered finding IDs, matching the frozen TSV contract; detail labels are separately retained in raw receipts.

Self-evaluation: accuracy 5 (two byte-identical matrices plus raw outputs); completeness 5 (six assigned steps recorded); clarity 4 (command index/raw receipts require opening linked evidence); actionability 5 (durable expanded commands and driver); conciseness 4 (long real-lane command retained verbatim). Overall 4.6/5. Improvement: use the index to inspect any individual row without rerunning; user agreement expected within this stated reproduction scope.
