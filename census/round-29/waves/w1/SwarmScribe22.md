# SwarmScribe22 — r29 w1: append-only corrections for the four frozen stale statements

## Status

STATUS: PASS — three append-only blocks drafted (`deliver-c1-corrections.md`); mechanically verified in a
scratch clone: `K2 4→0`, `k1=6` unchanged (K1 is another seat's surface), no lane file edited or committed by
this seat. All numbers re-derived from committed bytes at rev `691dd29211c53d0ef94fa072394cb9c8a69fe92e`.

## Evidence

1. Precondition — the four phrases still sit verbatim at their `file:line` at both `691dd29` and `b8cb4b3`
   (`git show <rev>:<file> | sed -n '<line>p'`), and the counter's own before state names them:
   ```
   python3 -B tools/souji-registry-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
     --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
   K2 uncorrected LOG.md:1758
   K2 uncorrected SCORECARD.md:23
   K2 uncorrected corpus/lessons/round-28.md:22
   K2 uncorrected corpus/lessons/round-28.md:40
   SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e   (rc 1)
   ```
2. r26 receipt over committed bytes (counter, independent of the capture tool):
   ```
   python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
     --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
   r26 records=1382 failed=152 uncovered=14 floor_violation=0
   r27 records=124 failed=0 uncovered=0 floor_violation=0
   r28 records=75 failed=0 uncovered=0 floor_violation=0
   SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e  (rc 1)
   ```
3. Independent recomputation (own GNU decoder + `git ls-tree -r` + `git cat-file blob` at the same rev):
   1382 records, 2 escaped, 1230 present with **0** sha256 mismatches, 152 absent; 1245 committed entries under
   the round-26 capture = 993 `100644` + 238 `100755` + 14 `120000`; recordless committed paths = the 14 symlinks
   (raw count 15 also catches `manifest.sha256` itself, which the counter excludes by contract).
4. Cause of the 152, re-derived: 17 `.gitignore` files at that rev; the 5 inside the capture copied at their
   committed paths into a scratch repo; `git check-ignore --no-index -v --stdin` over all 152 → 152 hits:
   138 `vadv-49/.gitignore:1 fixture/`, 4 `case-V6/.gitignore:6 /ledger*.tsv`, 4 root `.gitignore:3 __pycache__/`,
   2 `vadv-49/.gitignore:2 shims/`, 1 each `case-V6:5 /vault/`, `case-V6:4 /src/`, case-F7 and case-F8
   `.scratch/.gitignore:1 *` → 148 nested + 4 root.
5. Escaped records: both decode to committed blobs whose sha256 equals the record digest —
   `nl/first<LF>second.md` 23 bytes `1009b12ce1c85de0…`, `.scratch/old<LF>name.log` 31 bytes `ae599d14eab6d335…`.
   `/usr/bin/sha256sum` = `sha256sum 0.8.0` (uutils). Full manifest over the committed subset:
   `WARNING: 2 line(s) are improperly formatted`; two-line subset: `no properly formatted checksum lines found`,
   rc 1; mixed manifest (1 plain + 2 escaped): warning + rc 0 — so the frozen "(rc 0)" is reproducible on this
   consumer, while "malformed record" is not.
6. r27/r28 independently re-verified from their committed manifests: r27 124 records, 0 absent, 0 mismatch,
   0 uncovered; r28 75 / 0 / 0 / 0. Root `.gitignore` at the rev is exactly `.ufo/waves/`,
   `census/operator-sweep-*/`, `__pycache__/`.
7. Block acceptance test (scratch only, `git clone -q --no-local <lane> $D/c`):
   ```
   blocks found: 3 ; appended 4 lines LOG.md, 3 lines SCORECARD.md, 4 lines corpus/lessons/round-28.md
   commit 218ad0a31e26e67224c4ff72e2c5ce69001b7b65 (scratch, deleted)
   SUMMARY k1=6 k2=0 mismatches=6 rev=218ad0a31e26e67224c4ff72e2c5ce69001b7b65   (rc 1, K1 only)
   ```
   Every block line asserted to start `R29-CORRECTION ` and to contain no `|`; the four stale phrases stayed at
   their lines (K2 requires phrase-at-line, so K2=0 proves both halves).

## Findings

1. The frozen description "two malformed newline-path records" omits the real receipt defect: 152 records name
   paths absent from the committed tree (`census/round-26/waves/manifest.sha256`, rev `691dd29`). The two escaped
   rows are valid GNU escapes (F3 above) — the consumer, not the record, is deficient.
2. All 152 absences are ignore-rule casualties created by the capture copying the fixture `.gitignore` files with
   the tree: 148 by nested rules, 4 by root `__pycache__/`. No other cause remains after check-ignore matched 152/152.
3. 14 committed symlinks under `census/round-26/waves/` carry no manifest record; the receipt therefore cannot
   attest them, which is a separate (unrecorded-link) gap from the 152.
4. The `(rc 0)` figure in all four frozen statements is *reproducible* on this host's uutils 0.8.0 when any line
   parses, so the corrections target the "malformed/malformed-record" reading and the missing 152/14 counts, not
   the exit code. Stated in the blocks so a later reader does not over-correct.
5. Complementary, not conflicting, with sibling `SwarmExecutor06`'s `deliver-c2-152-classification.tsv`
   (`vault-component 146; dot-git-config 7; dot-git-info-exclude 7`): that file buckets by path family, this seat
   buckets by the ignore rule that suppressed each path; both cover the same 152.
6. Raw recordless-path count is 15 vs the counter's `uncovered=14` solely because `manifest.sha256` excludes
   itself by contract (`census/round-29/records/preregistration.txt`, C2 clause). Observation only; no counter
   change proposed.

## Limits

- Not re-derived, and marked as such inside the blocks: the dirty-`.ufo/waves` 163→0 count, the fixture line
  `cases=6 pass=6 control=TAMPER-REJECTED`, and the restore of 11 modified tracked r26 files — working-tree,
  tool-run and history facts, not committed-byte facts.
- K1 (6 SOURCES/knowledge rows) is untouched by this seat; until it lands, C1 reads `k1=6 k2=0`.
- Blocks are drafted, not landed: the L1 owns the append. Measured rev for every number is
  `691dd29211c53d0ef94fa072394cb9c8a69fe92e`.
- No tool installs; no lane commit, `jj` mutation, or write outside the two files named below.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-c1-corrections.md` (three fenced append blocks + evidence + landing notes)
- `.ufo/waves/round-29/w1/SwarmScribe22.md` (this report)
