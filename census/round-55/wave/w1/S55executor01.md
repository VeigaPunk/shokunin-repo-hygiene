# S55executor01 — round 55 w1, C1 reproduction (executor seat)

Verdict: **AGREE on all four steps.** No disagreement, no blocker, no edit of frozen
bytes, no commit, no mutating git/jj command. Lane HEAD at every measurement:
`3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f` (the dispatch tip; the measured revision
for step 3 is the pinned earlier `4b10ddd1741a`).

Every command below ran with cwd = `/home/vgpnk/Projects/shokunin/souji-shokunin`
(the lane root) and `TMPDIR=/fast/scratch/hyaku/souji-r55/S55executor01`
(scratch, deleted at the end; all receipts copied into this seat dir first).

## Pins verified before probing (all six match; re-verified unchanged after all runs)

| path | expected | measured |
|---|---|---|
| census/round-55/c1-counter.py | 944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2 | identical |
| census/round-55/c2-counter.py | e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c | identical |
| census/round-55/fixtures/build-fixtures.py | e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62 | identical |
| census/round-55/fixtures/run-matrix.sh | ce13d4fff4b66175071ccef2a808baf3b1f928c5ec9985343580524450ef8315 | identical |
| census/round-55/records/c1-selftest-expected.tsv | ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e | identical |
| census/round-55/records/c2-selftest-expected.tsv | 63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc | identical |

The v3-arm acceptance control used in step 2 is the frozen r54 counter
`census/round-54/c1-counter.py` sha256 `f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e`
(not a prereg pin; recorded so the matrix arm is reproducible).

## Step 1 — pinned selftest: AGREE

```
TMPDIR=$S python3 -B census/round-55/c1-counter.py --selftest --work $S/st \
  --builder-sha256 e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62 \
  --expected-sha256 ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e
```

Exit `0`. Last line: `SELFTEST pass cases=27`. All 27 `SELFTEST-CASE` lines report
`pass` (F1 … F23 in the recorded order, including the r55 additions F7-FF,
F12c-LOG-POINTER-EXEMPT, F8b-BT4-SHORT-RUN, F13 … F23).

Two independent equality checks on that output:

- `diff $S/c1-selftest.out census/round-55/records/c1-selftest.txt` → empty
  (byte-equal; both sha256 `5672ad9ad96c186018f7cded45b861f3fca8a437484d5c776452369a64cec725`).
- case-by-case extraction of `name / rc / finding` vs `c1-selftest-expected.tsv`
  → `TSV-AGREE 27/27 cases` (`diff` empty).

Receipt shape note (not a defect): `c1-selftest-expected.tsv` is the *data* table
(`name<TAB>expect_exit<TAB>expect_finding`), not the printed transcript, so it is
compared case-by-case; its byte-equal peer is `records/c1-selftest.txt`.

Wrong-builder-pin refusal (pin `0`*64):

```
TMPDIR=$S python3 -B census/round-55/c1-counter.py --selftest --work $S/st2 \
  --builder-sha256 0000000000000000000000000000000000000000000000000000000000000000 \
  --expected-sha256 ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e
```

Exit `2`, stderr:
`CANNOT-EVALUATE PIN-MISMATCH builder sha256 e629a2e9…fa8d62 != pinned 0000…0000`.
The refusal fires **before** any fixture work (nothing was created under `$S/st2`).

## Step 2 — fixture rebuild + four rows per arm: AGREE

Rebuild (committed builder bytes, imported/executed, never edited):

```
TMPDIR=$S python3 -B census/round-55/fixtures/build-fixtures.py --work $S/build --manifest $S/manifest.tsv
```

Exit `0`; `BUILT` lines for all 40 fixtures (27 C1 + 13 C2); wall time 0.38 s. The
pinned `GIT_AUTHOR_DATE/GIT_COMMITTER_DATE` reproduce the committed revs: all 27 C1
tip ids in `$S/manifest.tsv` equal the `rev` column of the committed matrices
(e.g. F7-FF `e163e0fa6689`, F13-DUAL-ANCHOR `097b943e80d8`, F17-INDENT4-FENCE
`9349495e9a5b`, F23-SOURCES-RECOMP `116864e88a4c`). Each fixture toplevel was
asserted to be its own directory before use (`git -C <dir> rev-parse --show-toplevel`).

Four-row matrix, logic copied verbatim from `run-matrix.sh` `c1_arm` (same
`--root/--rev/--base/--record-sha256/--sources-rev-before/--sources-rev-after`
argument set, same first-`FINDING`-token extraction), filtered to F7-FF,
F13-DUAL-ANCHOR, F17-INDENT4-FENCE, F23-SOURCES-RECOMP (`rows4.sh`, receipt in this
dir):

```
bash $S/rows4.sh $S $S/out        # runs v3 (census/round-54) then v4 (census/round-55)
```

`rows-v3=4 rows-v4=4`, exit 0. Byte comparison against the committed matrices
filtered to the same four fixtures:

| arm | my rows sha256 | committed rows sha256 | diff |
|---|---|---|---|
| v3-r54 | eee7c3ac52559c84ef4ecf3a9dd7940728d7fba10607efa86390182816d70b81 | identical | empty |
| v4-r55 | 3376201293fe991d3a88ff70fedb70a8cc27c40569873d68785181506dc8c2e2 | identical | empty |

Observed rows (verbatim, `c1-matrix-v4-4rows.tsv` / `c1-matrix-v3-4rows.tsv`):

- **F7-FF** — v3 `0 -` (`fenced=0`, the r54 sentinel-S1 blind spot) → v4 `1 CORRECTION-IN-FENCE` (`fenced=2`).
- **F13-DUAL-ANCHOR** — v3 `0 -` → v4 `1 ANCHOR-ALIAS-MISMATCH` (`alias=1`).
- **F17-INDENT4-FENCE** — v3 `1 CORRECTION-IN-FENCE` (over-hide) → v4 `0 -`.
- **F23-SOURCES-RECOMP** — v3 `1 SOURCES-RECOMPUTE-MISMATCH` → v4 `1 SOURCES-RECOMPUTE-MISMATCH` (`logrecomp=1`); both arms kill, exactly the prereg's disclosed "fixture coverage, not new kills".

Extra no-harm check (anti-cherry-pick, same taker unfiltered, all 27 C1 fixtures ×
both arms): `FULL v3 BYTE-EQUAL 27/27`, `FULL v4 BYTE-EQUAL 27/27`
(sha256 `bf760f4eda8bf65eaf99a3e3be64a37b85734ad92bafd1b9f6fa1a83b2bc1a90` and
`09ee1be66148251faf6fa8499ab47e4bc7d740522b67bb15dc8b892c7d017366`, each equal to
the committed file). So the four sampled rows are not a favourable subset.

Arm discrimination across all 27 rows (v3 exit/finding → v4 exit/finding), 11 rows
move, every one in the prereg's claimed direction:

```
F7-FF                 v3 0 -                            -> v4 1 CORRECTION-IN-FENCE
F13-DUAL-ANCHOR       v3 0 -                            -> v4 1 ANCHOR-ALIAS-MISMATCH
F14-PAIR-STALE-FILING v3 0 -                            -> v4 1 PAIR-FILING-INERT
F15-PAIR-NOROWS       v3 0 -                            -> v4 1 UNFILED-SOURCES-ANNOTATION
F16-PAIR-ARROW        v3 0 -                            -> v4 1 UNFILED-SOURCES-ANNOTATION
F20-R1-INDENT-SWALLOW v3 0 -                            -> v4 1 BOGUS-RECOMPUTED
F21-R1-ONELINE-SWALLOW v3 0 -                           -> v4 1 BOGUS-RECOMPUTED
F22-PTR-TIMESTAMP     v3 0 -                            -> v4 1 UNFILED-SOURCES-ANNOTATION
F17-INDENT4-FENCE     v3 1 CORRECTION-IN-FENCE           -> v4 0 -
F18-BTINFO-FENCE      v3 1 CORRECTION-IN-FENCE           -> v4 0 -
F19-PAIR-IN-FENCE     v3 1 UNFILED-SOURCES-ANNOTATION    -> v4 0 -
```

The eight acceptance attacks (F7-FF, F13, F14, F15, F16, F20, F21, F22) are all
`v3 exit 0` (the work is not vacuous) and all `v4 exit 1` with a named finding. No
carry-over row changed verdict (F1-F12, F12b, F12c, F8b hold their r54 states;
F12b/F12c/F17/F18/F19/F1 stay green).

## Step 3 — real-lane leg: AGREE

```
TMPDIR=$S python3 -B census/round-55/c1-counter.py --root . \
  --rev 4b10ddd1741a948c89d283358affd1da2ab3fd95 \
  --base f056aaa031bb65de27e7fa5daa38b0d4a443aedc \
  --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 \
  --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 \
  --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch $S
```

Exit `0`, stdout verbatim:

```
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=4b10ddd1741a base=f056aaa031bb
```

Every frozen field value is present as claimed (`unfiled=0 record_sha=ok appended=ok
multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0
pairinert=0`). `diff` vs `census/round-55/records/c1-tip.txt` → empty (byte-equal;
both sha256 `593bac6de2c3036dd55dee7c9ffc1feda8f620c020b4f87cbd509448efbc72bf`).

Determinism: the same command re-run into a *fresh* scratch dir produced an
identical file (`c1-tip-rerun.out`, same sha256) — no state carried in scratch.

Extra datapoint at the later lane tip `3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f`
(the dispatch tip, records + S278 sources only): exit `0` with every frozen field
identical; the only byte difference is the echoed `rev=3ce0ba036275` in SUMMARY
(`c1-later-tip.out`). The claim is pinned at `4b10ddd1` and reproduces there exactly.

## Step 4 — AGREE/DISAGREE

| step | claim | verdict |
|---|---|---|
| 1a | selftest pass cases=27, exit 0 | **AGREE** (byte-equal to records/c1-selftest.txt; 27/27 vs expected TSV) |
| 1b | wrong builder pin → exit 2 `CANNOT-EVALUATE PIN-MISMATCH` | **AGREE** |
| 2 | four rows per arm over F7-FF/F13/F17/F23 byte-equal to committed v3+v4 matrices | **AGREE** (4/4 both arms; 27/27 both arms unfiltered) |
| 3 | real-lane leg exit 0, frozen fields, byte-equal c1-tip.txt | **AGREE** |

## Named limits / observations (no edit of frozen bytes, nothing routed as a defect)

1. **F23-SOURCES-RECOMP discriminates no arm**: v3 and v4 both exit 1 with
   `SOURCES-RECOMPUTE-MISMATCH`. That is exactly the prereg's disclosure ("both arms
   kill, disclosed as fixture coverage, not new kills"), so it is consistent, but it
   contributes nothing to the v3→v4 contrast; the contrast rests on the other 11 rows.
2. **Receipt-shape clarification** for future takers: `c1-selftest-expected.tsv` is a
   data table, not a transcript; the byte-equal peer of the printed selftest is
   `records/c1-selftest.txt`. Both checks were run, so neither reading is left ambiguous.
3. No attack beyond the assigned reproduction was mounted by this seat (the wave's
   reviewer/critic/mutation-tester/sentinel seats own that surface), so this report
   asserts no new counter defect. Everything observed matched the frozen claim.
4. No stray writes: zero files under `census/round-55/` were modified after this
   session's first write (`find … -newer <scratch>` → count 0); the six pins re-hash
   identical after all runs; lane HEAD is still `3ce0ba03`.

## Bounds and tooling

- Read-only to the lane repo; wrote only this seat directory
  (`.ufo/waves/round-55/w1/S55executor01/`) and `/fast/scratch/hyaku/souji-r55/S55executor01/`
  (deleted before yield). No commit, no push, no mutating git/jj command; fixture
  toplevels asserted before use; no write outside `--work`/`--scratch`.
- No tool installed or upgraded this seat (nothing needed).
- `bash scripts/hyaku/disk-guard.sh status` before the heavy pass: `/fast` 50 % used,
  408.7 G free; `/tmp` 26 % used. No ENOSPC.

## Receipts (this directory, sha256 in `receipt-sha256.txt`)

`c1-selftest.out`, `c1-wrongpin.out`, `c1-matrix-v3-4rows.tsv`,
`c1-matrix-v4-4rows.tsv`, `c1-matrix-v3-full27.tsv`, `c1-matrix-v4-full27.tsv`,
`c1-tip.out`, `c1-tip-rerun.out`, `c1-later-tip.out`, `fixture-manifest.tsv`,
`rows4.sh`, `allrows.sh`.
