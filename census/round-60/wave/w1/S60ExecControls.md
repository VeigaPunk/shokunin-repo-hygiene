# S60ExecControls — round-60 pre-freeze controls (executed)

Seat: S60ExecControls (leaf executor, wave souji-r60-w1, lane `souji-shokunin` at
`1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`, lane HEAD at run time, tracked worktree clean).
Scratch `/fast/scratch/hyaku/souji-r60/S60ExecControls/` created, used, and fully removed after
receipts were copied into the delivery dir. No lane file outside `.ufo/waves/round-60/w1/`
(S60ExecControls/) and `S60ExecControls.md` was created or modified; no git/jj mutation anywhere;
read-only git only (`rev-parse`, `status`, `show`, `cat-file` on the lane).

## Verdict — do-nothing arm is RED in both claims (freeze gate satisfied)

| receipt | measured | result | EXIT |
|---|---|---|---|
| `do-nothing-c1.txt` | C1 counter, `--rev` = base rev, full 8-case matrix | `forgeries_accepted=5 honest_accepted=3 stubs=REJECTED` | **1 (RED)** |
| `positive-c1.txt` | honest cases only at base tool | `honest_accepted=3`, forgeries_accepted=0 | 0 |
| `forgery-c1.txt` | 5 forgery cases only, each named with its class | `forgeries_accepted=5` | 1 |
| `do-nothing-c2.txt` | C2 fixture vs base recorder | `pass=4 fail=4` (cases 3,4,6,7 pass), stubs REJECTED | **1 (RED)** |
| `positive-c2.txt` | base recorder re-run, fresh work dir | `pass=4`, passing cases named in header | 1 |

C1 is RED exactly as the freeze requires: both arms resolve to the base bytes
(`ARM base/new rev=1e8bf... sha256=d1ca06fd... substance-arm=absent`), the `Control:` receipt
bindings are unenforced, and all five forgeries are accepted while the three honest cases still
pass (no blanket refusal). Independent cross-check: the S60ExecMatrix seat's own `base-run.txt`
(finished minutes after mine) reports the identical verdict (`forgeries_accepted=5`,
`stubs=REJECTED`, `EXIT=1`).

C2 is RED: the base recorder passes only 4 of 8 cases, so the fixture exits 1. RED does not depend
on the 3-vs-4 question below.

## Finding for the L1 — reconcile before the freeze (claim number vs fixture spec)

The frozen C2 claim says base recorder = **3/8**. The fixture case spec as written in
`w1-spec.json` (S60ExecRecorderFix item), implemented literally, measures **4/8**: the base
recorder passes BOTH `3 atomic-in-flight` and `4 kill-residue`, because it creates no temp file and
writes OUT only after the wrapped command completes — exactly what those two cases check. My
receipts name all four passing cases (3, 4, 6, 7). Either the frozen fixture design must add a
check under which the base fails one of cases 3/4, or the claim's 3/8 number must be amended —
an L1 decision, not mine. Case-1 failure is genuine and matches the claim's intent (base receipt
has no `command=` line); cases 2, 5, 8 fail as claimed (no overwrite guard, no output bound, no
dirty-tree guard).

Secondary observation: the S60ExecRecorderFix candidate `r60-receipt-write.py` delivered mid-wave
currently mis-invokes the base recorder through its positional adapter (observed rc=127 with a
mangled relative OUT path, `pass=2`) — its own `base-run.txt` was not yet delivered at my final
check, so its numbers are not yet comparable.

## Finding for the L1 — C1 forgery `forgery-rev-at-freeze` is unconstructible as literally worded

The spec row says `rev = the freeze commit itself`. A commit cannot contain its own id
(self-referential sha256), and the substance check reads the receipt blob AT the freeze commit, so
no two-phase commit trick can embed it. My builder uses an orphan commit (`git commit-tree` on the
pre-freeze tree): it resolves, is full-40, and is NOT a strict ancestor of the freeze — the exact
condition `CONTROL-REV-NOT-BEFORE-FREEZE` exists to refuse. Disclosed in `build-matrix.py`'s
docstring and in the EXPECT-CLASS evidence; the S60ExecMatrix seat should confirm how their frozen
builder handles this row.

## Sibling candidate state

At first inspection (2026-11-04 ~23:46 UTC) all four sibling delivery dirs were empty/absent, so
per assignment I wrote minimal equivalents and ran the base-only arm. By run time (23:52–23:54 UTC)
S60ExecMatrix, S60ExecRecorder, and S60ExecRecorderFix had delivered candidates; S60ExecFreezeArm
(the `--substance` arm itself) had not. None of my six receipts depends on any sibling candidate:
C1 receipts run both arms from git blobs at the base rev; C2 receipts run the base recorder. The L1
can re-run my counter/fixture unchanged against the integrated candidates later — my `--rev`
parameter already accepts any revision.

## Delivered (absolute paths)

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecControls/c1-counter.py` — C1 counter (minimal equivalent of the S60ExecMatrix runner; blob-driven arms, spec-format CASE/SUMMARY lines, stub controls)
- `.../S60ExecControls/build-matrix.py` — 8-case builder (synthetic git repos under scratch; fixture rule enforced: toplevel asserted before first commit, throwaway env-scoped identity)
- `.../S60ExecControls/c1-matrix.tsv` — frozen 8-row matrix (`case/expect/control_receipt/class`)
- `.../S60ExecControls/c2-fixture.py` — C2 fixture (minimal equivalent of the S60ExecRecorderFix fixture; 8 cases + always-write/always-refuse stub controls; dual ABI adapter)
- `.../S60ExecControls/do-nothing-c1.txt`, `positive-c1.txt`, `forgery-c1.txt`, `do-nothing-c2.txt`, `positive-c2.txt`, `digests.txt`

## Exact commands (all observed; full argv in each receipt header)

```
python3 -B .../S60ExecControls/c1-counter.py --root <lane> --matrix .../S60ExecControls/c1-matrix.tsv \
  --base-tool-rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 \
  --work <scratch>/work-c1-donothing                            # EXIT=1
#   + --only ^honest-   -> positive-c1, EXIT=0
#   + --only ^forgery-  -> forgery-c1,  EXIT=1
python3 -B .../S60ExecControls/c2-fixture.py --tool <lane>/census/round-57/record-receipt.sh \
  --work <scratch>/work-c2-donothing                            # EXIT=1
#   fresh --work work-c2-positive                                 # EXIT=1 (positive-c2)
```

Observed key lines: C1 `SUMMARY matrix=8 forgeries_accepted=5 honest_accepted=3 stubs=REJECTED`;
C1 honest-only `SUMMARY matrix=3 forgeries_accepted=0 honest_accepted=3 stubs=REJECTED`;
C2 `SUMMARY cases=8 pass=4 fail=4 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`.

## Tooling

No installs (none needed): python3 3.14.8 and git 2.56.0 already present. Nothing written to
PATH directories. Fixtures run only inside scratch; every fixture commit preceded by
`git rev-parse --show-toplevel` equality assert; throwaway identity env-scoped.

## Named limits

1. Base-only arm by design (candidates absent at control time); the "new arm" column equals the
   base tool bytes — evidenced per-run by `ARM ... substance-arm=absent`.
2. `forgery-rev-at-freeze` uses the orphan-commit stand-in (see finding above).
3. My C2 fixture measures base = 4/8 vs the frozen claim's 3/8 — L1 reconciliation required before
   freeze (see finding above); RED verdict unaffected.
4. First C2 run used a fixture with an incorrect expected `instrument_sha256` (helper stripped the
   blob); fixed, C2 receipts re-run; the c2-fixture.py digest in digests.txt covers the bytes of
   the delivered runs; case verdicts were identical in both runs (case 1 fails on `command=`, the
   genuine defect).
5. Instrument digests for the two production files are the committed blobs at the base rev,
   verified byte-identical to the worktree before running.
6. Lane worktree carried untracked files placed by other actors during the wave
   (`census/round-60/`, `corpus/knowledge/freeze-record-substance-binding.md`,
   `corpus/lessons/round-60.md`); untouched by me; no tracked file dirty at run time.
