# deliver-c1-corrections — append-only corrections for the four frozen stale statements

Seat: SwarmScribe22 (souji round 29, wave 1). Target: `census/round-29/stale-statements.tsv` rows
`LOG.md:1758`, `SCORECARD.md:23`, `corpus/lessons/round-28.md:22`, `corpus/lessons/round-28.md:40`.

All numbers below are measured by this seat at
**rev `691dd29211c53d0ef94fa072394cb9c8a69fe92e`** (lane base, branch master) from committed bytes only.
No stale sentence is edited in place; each block is appended at the tail of its file, after the stale line,
so `tools/souji-registry-agreement.py` K2 keeps finding the phrase at its original `file:line`.
Land each block with one blank line before it (markdown separation); the block's own lines are exactly
the fenced lines, each starting `R29-CORRECTION <file>:<line>`.

## Block 1 — append to the tail of `LOG.md`

```
R29-CORRECTION LOG.md:1758 measured at rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e: the round-26 receipt holds 1382 records, 152 of them name paths absent from the committed tree, and 14 committed paths (all 14 symlinks) carry no record; command: python3 -B census/round-29/c2-counter.py --root <lane> --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e prints r26 records=1382 failed=152 uncovered=14 floor_violation=0 and SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 (rc 1).
R29-CORRECTION LOG.md:1758 the 152 absences are ignore-rule casualties inside the capture: rebuilding the committed .gitignore stack at the same rev and running git check-ignore matched 152 of 152 paths — 138 by vadv-49 `fixture/`, 4 by case-V6 `/ledger*.tsv`, 2 by vadv-49 `shims/`, one each by case-V6 `/src/` and `/vault/`, one each by the two `.scratch` rules (148 by .gitignore files copied into the capture with the tree), plus 4 by the root `__pycache__/` pattern.
R29-CORRECTION LOG.md:1758 the two backslash-escaped records are valid GNU escapes, not malformed rows: each decodes to a committed blob whose sha256 equals the recorded digest (23-byte `nl/first<LF>second.md` digest 1009b12c…, 31-byte `.scratch/old<LF>name.log` digest ae599d14…), while this host's sha256sum 0.8.0 (uutils) prints "WARNING: 2 line(s) are improperly formatted" and, when no other line parses, "no properly formatted checksum lines found" with rc 1.
R29-CORRECTION LOG.md:1758 the quoted sentence is superseded by this appended block, not edited in place; still true at the same rev: r27 (124 records) and r28 (75 records) verify with 0 absent, 0 digest mismatch and 0 uncovered, and the root `.gitignore` carries exactly `.ufo/waves/`, `census/operator-sweep-*/` and `__pycache__/`; not re-derived from committed bytes: the dirty-wave 163→0 count and the restore of 11 modified tracked r26 files, which are working-tree and history facts.
```

## Block 2 — append to the tail of `SCORECARD.md`

```
R29-CORRECTION SCORECARD.md:23 measured at rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e: the r26 receipt has 1382 records, 152 naming paths absent from the committed tree, and 14 committed symlinks with no record; command: python3 -B census/round-29/c2-counter.py --root <lane> --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e → SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 (rc 1).
R29-CORRECTION SCORECARD.md:23 the "2 malformed newline-path records" reading is superseded, not edited: the 152 absences are the defect — all 152 match ignore rules rebuilt from the committed .gitignore stack (148 nested inside the capture, 4 by root `__pycache__/`) — and the 2 escaped rows are valid GNU escapes whose digests equal the committed blobs, which this host's uutils sha256sum 0.8.0 rejects as improperly formatted.
R29-CORRECTION SCORECARD.md:23 still true at the same rev: r27 (124 records) and r28 (75 records) verify with failed=0 and uncovered=0; the dirty `.ufo/waves` 163→0 count and the fixture line `cases=6 pass=6 control=TAMPER-REJECTED` are working-tree and tool-run claims and are not re-derived here from committed bytes.
```

## Block 3 — append to the tail of `corpus/lessons/round-28.md`

```
R29-CORRECTION corpus/lessons/round-28.md:22 corpus/lessons/round-28.md:40 measured at rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e: r26 records=1382, of which 152 name paths absent from the committed tree, with 14 uncovered committed symlinks; command: python3 -B census/round-29/c2-counter.py --root <lane> --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e → SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 (rc 1).
R29-CORRECTION corpus/lessons/round-28.md:22 corpus/lessons/round-28.md:40 cause, re-derived by rebuilding the committed .gitignore stack and running git check-ignore (152 of 152 matched): 148 names are ignored by .gitignore files the capture copied in with the tree (vadv-49 `fixture/` 138 and `shims/` 2, case-V6 `/ledger*.tsv` 4, `/vault/` 1, `/src/` 1, two `.scratch` rules) and 4 by the root `__pycache__/` pattern.
R29-CORRECTION corpus/lessons/round-28.md:22 corpus/lessons/round-28.md:40 the two newline records are not malformed: they are GNU-escaped lines that decode to committed blobs whose sha256 equals the recorded digests, and this host's sha256sum 0.8.0 (uutils) cannot parse them, so "not independently consumable by this host's consumer" stands while "malformed record" does not.
R29-CORRECTION corpus/lessons/round-28.md:22 corpus/lessons/round-28.md:40 both quoted sentences are superseded by this appended block, not edited in place; still true at the same rev: r27 (124 records) and r28 (75 records) verify cleanly with failed=0 and uncovered=0, and the root `.gitignore` carries exactly `.ufo/waves/`, `census/operator-sweep-*/` and `__pycache__/`.
```

## Evidence behind every number in the blocks

All at rev `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, run by this seat from a `git archive` extraction in
`/var/tmp/souji-r29-SwarmScribe22.*` plus `git ls-tree`/`cat-file`; no working-tree read.

1. `python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e`
   → `r26 records=1382 failed=152 uncovered=14 floor_violation=0` … `SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0`, rc 1.
2. Independent parse of `census/round-26/waves/manifest.sha256` (GNU decoder) against `git ls-tree -r` at the same rev:
   1382 records, 2 escaped, 1230 present, **0** content-sha256 mismatches among present records, 152 absent,
   1245 committed entries under the round-26 capture = 993 regular + 238 executable + 14 symlinks; the 14
   recordless committed paths are exactly the 14 symlinks (a raw count of 15 also sees `manifest.sha256` itself,
   which the counter excludes by contract).
3. Cause: 17 `.gitignore` files at that rev, the 5 inside the round-26 capture copied into a scratch repo at their
   committed paths, `git check-ignore --no-index -v --stdin` over the 152 absent paths → 152 hits; breakdown
   138 `vadv-49/.gitignore:1 fixture/`, 4 `case-V6/.gitignore:6 /ledger*.tsv`, 4 root `.gitignore:3 __pycache__/`,
   2 `vadv-49/.gitignore:2 shims/`, 1 each `case-V6/.gitignore:5 /vault/`, `case-V6/.gitignore:4 /src/`,
   `case-F7/…/.scratch/.gitignore:1 *`, `case-F8/…/.scratch/.gitignore:1 *`.
4. Escapes: `git cat-file blob` on the two newline-named paths at that rev → sha256 `1009b12c…` (23 bytes) and
   `ae599d14…` (31 bytes), equal to the manifest digests; `/usr/bin/sha256sum` reports `sha256sum 0.8.0`,
   full-manifest run prints `WARNING: 2 line(s) are improperly formatted`, and a two-line subset prints
   `no properly formatted checksum lines found` (rc 1). With one parseable line present the same warning is
   printed at rc 0 — the check that the original "(rc 0)" observation is reproducible on this consumer, so the
   correction targets the "malformed record" reading and the missing 152/14, not the rc.
5. r27/r28 independently re-verified from their committed manifests: r27 records=124 absent=0 sha_mismatch=0
   uncovered=0; r28 records=75 absent=0 sha_mismatch=0 uncovered=0.
6. Root `.gitignore` at that rev is exactly `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/`.

## Landing notes for the L1

- Append order is free; K2 only requires the marker line to sit after the stale line in the same file.
- Nothing else in the lane was written by this seat; the four stale sentences stay byte-identical.
- After landing, re-run `python3 -B tools/souji-registry-agreement.py --root <lane> --rev <landing-commit> --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804`:
  K2 must fall 4→0 at the landing commit. K1 (6 rows) is another seat's surface and is untouched here.
