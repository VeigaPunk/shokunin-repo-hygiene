# SwarmExecutor09 — r34 w1, C1 slice 9/12 (items E16, E17a, E17b, E18, E19)

## Status

STATUS: PASS — all five slice items measured by execution at base `9c76c7222a8abff027af42e37f0d160d52526bba`
against list-rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: four AGREE as originals (E16, E17a, E17b, E19), one
MISMATCH (E18) traced to its executed cause and given one honest restatement row, which was itself verified end-to-end
in a scratch clone (counter reads `AGREE restated`, rc 0) and falsified against a wrong cause (`BAD-CAUSE`, rc 1).

## Evidence

Counter bytes at `--list-rev`: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`
(`git show 2b0171e2:census/round-34/c1-counter.py | sha256sum`). Lane HEAD at read time `51acb5fb…`; measurement at `--rev`.

Executed (scratch `/fast/scratch/hyaku/souji-r34/RestateC1s9`, `TMPDIR` set by hand; serialization is the counter's own
frozen Q77 flock at `<scratch>/c1.lock`):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s9/cnt --only E16,E17a,E17b,E18,E19
```

```
ITEM	E16	AGREE	original	rc=0 expect_exit=0 predicate holds last=cases=8 pass=8 refusals=2/2 regress=5/5 load=3.94
ITEM	E17a	AGREE	original	rc=0 expect_exit=0 predicate holds last=entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0 load=3.94
ITEM	E17b	AGREE	original	rc=0 expect_exit=0 predicate holds last=gitrepository-layout.5.txt: OK load=5.87
ITEM	E18	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=selftest=PASS ids=7/7 load=5.87
ITEM	E19	AGREE	original	rc=0 expect_exit=0 predicate holds last=keys=4 records=4 occurrences=17 mismatches=0 load=5.87
SUMMARY items=5 agree=4 mismatches=1 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
```

Exit 0. `/proc/loadavg` before/after: `3.94 3.11 2.10` / `5.87 3.52 2.24`.

E18 cause walk (one `--no-local` clone per revision, detached, origin removed, toplevel asserted = the clone;
`env -i PATH=<jj symlink>:/usr/bin:/bin TMPDIR=<fresh> GIT_CONFIG_NOSYSTEM=1 HOME LANG=C.UTF-8`, item argv from clone root):

```
=== rev=679e2d02f46e (728b2ce^1) rc=0 load=12.34   last line: selftest=PASS ids=5/5   → original HOLDS
=== rev=728b2ce71acb (cause)     rc=0 load=12.34   last line: selftest=PASS ids=7/7   → original FAILS
=== rev=2b0171e2071f (list-rev)  rc=0 load=6.21    last line: selftest=PASS ids=7/7
=== rev=9c76c7222a8a (base)      rc=0 load=6.21    last line: selftest=PASS ids=7/7
```

Row verification in a scratch clone of list-rev with the row appended (throwaway identity, commit `128fe31c…`):

```
ITEM	E18	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=selftest=PASS ids=7/7 load=7.84
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=128fe31c1299e6255b5ddd261ad54ede63a564f0
```

Negative control, same clone, cause replaced by the later file-touching commit `98e5203d45b4…`:

```
ITEM	E18	MISMATCH	restated	BAD-CAUSE(original at parent=False at cause=False; need True/False)
SUMMARY items=1 agree=0 mismatches=1 restated=1 partial=1 rev=798bee8cc7e363f3f91135b5f386735a8abea973
```

E17b non-vacuity, item argv re-executed directly at base: six `…: OK` lines, `RC=0`, load 11.08; `SHA256SUMS` at base has
exactly 6 entries, so `COUNT: OK$==6` is the whole file.

## Findings

1. **E18 is a genuinely stale cell** — `SCORECARD.md:71` (r24 "r13 structure entry recheck") states
   `selftest=PASS ids=5/5`, while its own argv prints `selftest=PASS ids=7/7` with exit 0 at base, at list-rev and at the
   r25 tip. Cause `728b2ce71acbe574ae3036b456724d0a3d6f8f08` (round-25) added the `SOUJI-R13-STRUCT-linked-common-dir`
   and `SOUJI-R13-STRUCT-colocated-vs-plain` probe cases to `tests/fixtures/r13-repo-structure.sh` (one of 181 paths in
   that commit) and renumbered the header comment to `ids=7/7`. Row drafted in `deliver-c1-E18.md`.
2. **Q76 does not bind this cell** — every existing correction of the same claim (`R30-CORRECTION SCORECARD.md:155 R04`,
   `| L05 | SCORECARD.md:155 | ids=7/7`, `| K04 | SCORECARD.md:155 | restated | … ids=7/7`) names
   **SCORECARD.md:155**, the r13 capability row, not :71. The (argv, statement) dedup in `c1-items.tsv` therefore left the
   r24 literal `ids=5/5` uncorrected; nothing in the base file names `SCORECARD.md:69|70|71|101` (plain and cell-form greps).
3. **The restatement section is absent** — `grep -n 'Round 34 registry restatements' SCORECARD.md SKILL.md` (worktree) and
   the blob at tip both return nothing; the L1 must append the heading with the rows, else `load_restatements` sees no section.
4. **Cause uniqueness verified, not assumed** — the item's two files have three commits; the r13 addition cannot be a cause
   (its parent has no fixture), and the only later file-touching commit (`98e5203d…`) is refused by the counter as
   `BAD-CAUSE` because the original already fails at its parent, so `728b2ce` is the first failing commit.
5. **E19's reading is revision-pinned** — the argv fixes `--rev eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a` and the tool reads
   committed bytes at that revision, so the AGREE does not depend on which commit the clone is checked out at
   (only a change to the tool bytes at `--rev` could move it). E16/E17a/E17b are checkout-dependent but hold at base.
6. **E17b's predicate is a count, not the last line** — `COUNT: OK$==6` matched 6 lines while the run's last digit-bearing
   line carries no count; I recorded that explicitly in the delivery file so the `last=` field is not misread as the carrier.

No frozen predicate, target, item, leg or counter is proposed for change. No ATTACK is filed: nothing in this slice is
gameable or wrong — E18 is value drift, the class the frozen machinery is built for.

## Attack log

Not applicable: this seat's item is a C1 slice, not an attack item.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-c1-E16.md` — AGREE, no row.
- `.ufo/waves/round-34/w1/deliver-c1-E17a.md` — AGREE, no row.
- `.ufo/waves/round-34/w1/deliver-c1-E17b.md` — AGREE, no row (count non-vacuity shown).
- `.ufo/waves/round-34/w1/deliver-c1-E18.md` — MISMATCH; verbatim row, cause full40, parent/cause/tip readings, row
  verification and negative control.
- `.ufo/waves/round-34/w1/deliver-c1-E19.md` — AGREE, no row.
- `.ufo/waves/round-34/w1/SwarmExecutor09.md` — this report.

No tool installs or upgrades this wave. Scratch `/fast/scratch/hyaku/souji-r34/RestateC1s9` removed after the receipts
above were copied; no lane file written beyond the six paths above, no git/jj mutation in the lane.

## State note (L1 coordination, 2026-10-27)

The E18 row stays byte-identical to the form verified at scratch commit `128fe31c1299e6255b5ddd261ad54ede63a564f0`
(quoted verbatim in `deliver-c1-E18.md`); I have not touched it since.

Confirmed on the committed controls: `census/round-34/records/controls.txt` carries the C1 do-nothing control, the C1 junk
control (its third line records the E18 probe cause `728b2ce71acbe574ae3036b456724d0a3d6f8f08`, parent `ids=5/5`, cause
`ids=7/7`) and the C2 controls — but **no landing-row control**: no committed reading exercises an appended
`### Round 34 registry restatements` row before landing. Consequence for integration: the first counter reading that
covers the landed row is the C1 landing measurement itself, so any transcription drift (cell count, backticks, statement
not equal to the run's last digit-bearing line, wrong cause) will surface there as `BAD-ROW` / `BAD-CAUSE` / `MISMATCH`
rather than in a pre-landing control. The landing commit must therefore be measured with `--only E18` (or the full 60)
before the target line `SUMMARY items=60 agree=60 mismatches=0` is claimed, and the heading must be appended in the same
commit as the row.
