# SwarmExecutor03 — r34 w1, C1 slice 3/12 (G13, G14, G15, G16, G17a)

## Status

STATUS: PARTIAL — G13, G14, G15, G16 AGREE at the base and at the tip (no restatement needed). G17a is
genuinely stale but its honest restatement is **not admissible** under the frozen item data: the executed
drift cause (98e5203d, round-32 C2) touches neither file named in the item's `files` column, so the counter
returns `BAD-ROW(cause touches none of the item files)`; the only row the frozen counter *does* accept is
causally false, because the item's `where` (SKILL.md:241) is off by one and binds the neighbouring row's
line. Both states are reproduced below and raised as attacks; no dishonest row was delivered.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `9c76c7222a8abff027af42e37f0d160d52526bba`,
list-rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`, tip at measurement `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.
Scratch `/fast/scratch/hyaku/souji-r34/RestateC1s3` (removed after the receipts were copied out).

Counter, one item at a time, under `flock <scratch>/tmp/c1s3.lock`, `TMPDIR` exported into scratch:

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s3/cnt --only <id>
```

Base readings (each line printed by the counter; load is the host 1-min load the counter recorded):

```
ITEM	G13	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160 load=4.29
ITEM	G14	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=4 pass=4 fail=0 load=4.43
ITEM	G15	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=8 pass=8 fail=0 base_discriminating=4 load=4.47
ITEM	G16	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=3 pass=3 fail=0 base_discriminating=1 load=4.36
ITEM	G17a	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=SUMMARY total=1 pass=0 fail=1 load=4.15
```

Tip readings, `--rev 51acb5fb6fa38a6b593b3badb674cec559d7eb2c --only G13,G14,G15,G16,G17a` (exit 1):

```
ITEM	G13	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160 load=32.04
ITEM	G14	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=4 pass=4 fail=0 load=32.04
ITEM	G15	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=8 pass=8 fail=0 base_discriminating=4 load=32.04
ITEM	G16	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=3 pass=3 fail=0 base_discriminating=1 load=33.64
ITEM	G17a	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=SUMMARY total=1 pass=0 fail=1 load=38.86
```

G17a cause walk — one private clone per commit (`git clone -q --no-local`, origin removed, detached,
`git rev-parse --show-toplevel` asserted, fresh TMPDIR each, `env -i PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1`):

```
7a6667cd27652baf8d704b5cdb8e3200bd6e27a1  CASE pass refs/remotes/synthetic/main runner_exit=0 matched=18 / SUMMARY total=1 pass=1 fail=0 / EXIT=0      (load 11.53)
98e5203d45b4e419a9e72801733d93303acc7ebd  CASE FAIL ... runner_exit=1 matched=16 / SUMMARY total=1 pass=0 fail=1 / EXIT=1                             (load 11.65)
                                          stderr: bwrap: Can't chdir to /var/tmp/souji-r21-replay-pxvgwvzs/src: No such file or directory
a416d0b26495ce78b76ea82316533bd8a9ef368c  matched=16, same two steps red                                                                    (load 7.91)
a7c35c24bdd8bae5cff9766ace02a81915756701  matched=16, same two steps red                                                                    (load 7.83)
4eb2fda51c9917abd734c7e411f98cbb59c5c0fe  matched=18, EXIT=0 (row text author)                                                             (load 16.19)
54eb2d0fb81e9cb5cf5b30430bcfa4b67ddc84ec  EXIT=2, fixture absent at that commit (line-241 text author)                                     (load 30.82)
--keep-only arm at base                   SUMMARY total=1 pass=1 fail=0 / EXIT=0                                                          (load 26.50)
```

Admissibility probes (throwaway clone of the lane at 2b0171e2, candidate row appended, throwaway identity):

```
honest row (cause 98e5203d)              ITEM G17a MISMATCH restated BAD-ROW(cause touches none of the item files)          rev c083dd70e4c4a82bcf8877fcb6b168e0812ffec6
r33 cause (a7c35c24)                     ITEM G17a MISMATCH restated BAD-CAUSE(original at parent=False at cause=False; need True/False) rev d2a1c5fb38be002079f6303ee56e53df63b682de
argv-correction, cause 4eb2fda5          ITEM G17a MISMATCH restated BAD-CAUSE(cause did not write the row's line)                    rev 4d693806620fd7eb49ed6ff1f040e2344040b1df
argv-correction --keep-only, cause 54eb2d0f  ITEM G17a AGREE restated ... last=SUMMARY total=1 pass=1 fail=0                              rev d72724aaa60c2f50dbe3bc35548da41b52b4943c
```

Prior-correction sweep (SCORECARD.md @ base, `git show 9c76c722...:SCORECARD.md | grep -c`):
`G13`=0 `G14`=0 `G15`=0 `G16`=0 `G17a`=0, `SKILL.md:237..241`=0 each, `r21-read-render-edges`=0,
`r21-replay-boundaries`=0, `r21-source-head`=0, `r21-source-refs`=0; `r21-reason-canary`=1 (line 13,
coverage capability row, not a correction). `grep -n '^###.*restate'` on SCORECARD@base → no match, so no
restatement section existed to bind any of these cells at the base reading.

## Findings

1. **G13** — `SKILL.md:238` (frozen where 237), `r21-reason-canary`. Exit 0 and the frozen predicate hold at
   base and at the tip. No correction exists or is needed.
2. **G14** — `SKILL.md:239`, `r21-read-render-edges`. Exit 0, `SUMMARY total=4 pass=4 fail=0` at both points.
3. **G15** — `SKILL.md:240`, `r21-replay-boundaries`. Exit 0; observed last line
   `SUMMARY total=8 pass=8 fail=0 base_discriminating=4` contains the frozen regex, so it matches on the
   LAST digit-bearing line as required. Same at the tip.
4. **G16** — `SKILL.md:241`, `r21-source-head`. Exit 0, `SUMMARY total=3 pass=3 fail=0 base_discriminating=1`
   at both points.
5. **G17a** — `SKILL.md:242` (frozen where 241), `r21-source-refs`. Stale at base and at the tip: the row's
   remote-only arm reads `SUMMARY total=1 pass=0 fail=1`, exit 1. Two of the eighteen replay steps
   (`r20-audit-contract`, `r20-input-binding`) die in their own `_private_var_tmp()` bwrap re-exec because the
   r21 runner stages its replay clone under `/var/tmp` and the private bind replaces that path
   (`census/round-21/run-acceptance.py:629`, `tests/fixtures/r20-audit-contract.py:664-681`,
   `tests/fixtures/r20-input-binding.py:1292-1309`). The row's second documented arm (`--keep-only`,
   exit 2 / no result) is still green.
6. **Item-table line numbers are one low for every registry item I read** — `SKILL.md:201`→202,
   `:215`→216, `:237`→238, `:241`→242 etc. Harmless for the value-drift path, but load-bearing for the
   argv-correction path (see Attack 1). Location: `census/round-34/c1-items.tsv` `line` column vs
   `git show 9c76c722...:SKILL.md`.
7. **G17a's `files` column is incomplete relative to the drift** — the cause named by history is
   `98e5203d45b4e419a9e72801733d93303acc7ebd`, which changes `tests/fixtures/r20-audit-contract.py` and
   `tests/fixtures/r20-input-binding.py`; neither is in the item's `files`
   (`tests/fixtures/r21-source-refs.py,census/round-21/run-acceptance.py`). Location:
   `census/round-34/c1-items.tsv` G17a row, `git show --name-only 98e5203d`.

## Attack log

**ATTACK-1 — argv-correction binding is gameable through the off-by-one `where` (reproduced AGREE).**
`judge()` binds an argv-correction cause to the text of the line at `item["where"]`
(`c1-counter.py`: `line_text = blob(root, list_rev, src_file)[lineno - 1]`). For G17a that line is the
`r21-source-head` row (written by `54eb2d0f`), not the `r21-source-refs` row (line 242, written by
`4eb2fda5`). Because `54eb2d0f` predates the fixture, the row's own argv "already failed" there (exit 2,
missing file), so a corrected argv `... --keep-only` with cause `54eb2d0f` is accepted:
`ITEM G17a AGREE restated ... last=SUMMARY total=1 pass=1 fail=0` at scratch rev
`d72724aaa60c2f50dbe3bc35548da41b52b4943c`. That row credits an unrelated commit (which touched a different
row) and leaves the row's red remote-only claim and its `18/18` wording untouched; it can convert any
registry item whose row documents a green alternate arm to AGREE without a fix. Not delivered.

**ATTACK-2 — the honest cause is unsatisfiable (reproduced BAD-ROW).** The genuine value drift is fully
executed — original holds at `7a6667cd` (18/18) and fails at `98e5203d` (16/18) — but `98e5203d` touches
none of the item's `files`, so `judge()` returns
`BAD-ROW(cause touches none of the item files)` (scratch rev `c083dd70e4c4a82bcf8877fcb6b168e0812ffec6`).
The r33 writer of the item's runner (`a7c35c24`) is no substitute:
`BAD-CAUSE(original at parent=False at cause=False; need True/False)` (rev `d2a1c5fb38be002079f6303ee56e53df63b682de`).
Consequence for the round: with the item data frozen as written, G17a can only reach AGREE through
Attack 1's false row, so the frozen target `SUMMARY items=60 agree=60 mismatches=0` is not reachable honestly
for this cell. Raising, not amending. Underlying defect worth a fix independent of the restatement:
the r21 runner stages under `/var/tmp` while its child fixtures now bind a private `/var/tmp` and
`--chdir os.getcwd()` into it; setting `SOUJI_PRIVATE_VARTMP` (the guard the fixtures already honour) or
skipping the re-exec when the cwd is under the bind would restore 18/18.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-c1-G13.md`
- `.ufo/waves/round-34/w1/deliver-c1-G14.md`
- `.ufo/waves/round-34/w1/deliver-c1-G15.md`
- `.ufo/waves/round-34/w1/deliver-c1-G16.md`
- `.ufo/waves/round-34/w1/deliver-c1-G17a.md` (honest row + both reproduced admissibility outcomes)

No lane file other than these five was written; no `git`/`jj` mutation in the lane; no tool installed
(no pacman transaction — the host-wide pause was respected); scratch removed after the receipts above were
copied out.
