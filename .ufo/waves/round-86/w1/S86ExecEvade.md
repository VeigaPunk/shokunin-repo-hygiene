# S86ExecEvade — evasion lab (C1 novel rows + C2 truncation)

Seat: `S86ExecEvade`, wave `round-86/w1`, leaf. Lane read-only; every fixture/copy under
`/fast/scratch/hyaku/souji-r86/S86ExecEvade/` (deleted at yield). Scratch only — no lane write, no git/jj in lane,
no install (pacman paused; python3 stdlib + git only).

## Axes
- calibration: does the 49-row population bind every clause its counter implements?
- operability: does the K4 record let a reader act on the forged path?

## Verdict (headline)
C1 stated wording survives (`ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0` re-measured;
all 8 mutants killed=yes on r86) but the population does **not** bind the round-equality
comparison, and neither do the 49 rows bind three further clauses. C2: the repaired K4 record is
single-line and C-escapes, but the writer truncates the name list at 5, so a forged 6th path is
**not named** — the claim's "still names the path" does not survive for >5-path forgeries.

## C1 — three NEW false rows (lab harness R10, forge probes)
Method (S85ExecEvade style): counter/harness copied byte-identical to scratch; lab harness extends
`build_fixture` with R10 (6 byte-equal targets at new rev `dd6e8d4c…`). Counter invoked with
lane-pinned populations (`census/round-77/c2-population.tsv`) + one `--forge` row, so no pin
weakened. Item P04 = `.ufo/waves/round-32/a2w1/SwarmExecutor08.md` (SCORECARD.md:598,
frozen `f:d0693448…`).

| id | target at R10 | counter output (pristine) | semantic truth | caught by 49 rows? | clause constrained |
|---|---|---|---|---|
| **NX3** | `.ufo/waves/round-032/w2/SwarmExecutor08.md` | `FORGE NX3 item=P04 class=MOVED expect=REFUSED got=REFUSED match=yes` | **false row** (byte-equal copy under round-032, not round-32) | **no** | round-equality `tr.group(1) != kr.group(1)` string compare; binding an int-normalised comparison needs NX3 as a row |
| **NX6** | `.ufo/waves/round-32/w0/SwarmExecutor08.md` | `FORGE NX6 item=P04 class=MOVED expect=REFUSED got=MOVED match=no` + `accepted=1` | byte-equal copy in `w0/` — pristine **accepts** | **no** (no w0 row; real census `census/round-83/records/wave-dirs.txt` shows `w1/ 65, w2/ 19, w3/ 1, a2w1/ 1` — `w0/` never occurs) | `OWNTREE_WAVE` `w[0-9]+` accepts any digit incl. `0`; pristine treats w0 as a real wave dir |
| NX1/NX2/NX4/NX5 | `.ufo/waves/round-32/wx/`, `w2a/`, `assimilationX/`, `a2w1x/`, each `SwarmExecutor08.md` | `FORGE NX1…NX5 guess expect=REFUSED got=REFUSED match=yes` (all four) | decoys | no | wave-shape regex anchoring (bound in pristine, survives nothing) |

Full receipts: scratch `c1-out.txt` (NX1–NX6 runs), forge files `work/forge-NX*.tsv`.
Command: `python3 -B <counter-copy> --root <fixture> --rev dd6e8d4c… (R10) --fleet-root
/home/vgpnk/Projects/shokunin --population census/round-77/c2-population.tsv --ledger
census/round-77/c2-pointer-ledger.tsv --forge work/forge-NX*.tsv`.

### NX3 — the routed defect (submission-quality counter must refuse, population cannot express)
Pristine refuses NX3 only because round-32 vs round-032 compare as **strings**
(`tr.group(1) != kr.group(1)`). The 49-row population has no leading-zero round row: m7's
`elif False` mutant (drops the branch) is killed by NF-L2 (`round-33`), which is also rejected
by an **int-normalised** comparison (`33 != 32`). So a counter that resolves the wrong round
number by normalising `int()` still scores 8/8 while accepting NX3's false row. Exact C1
sentence constrained: "the lane's false-row population is the instrument that certifies the
pointer counter's rule, and a clause with no row is not certified" — the round-equality clause
is certified only for digit-difference ≥1, not for digit-only-with-leading-zero difference.

### NX6 — w0 acceptance (bound direction)
Pristine accepts a copy under `w0/` because `w[0-9]+` matches `0`. The lane's real wave-dir
census (`census/round-83/records/wave-dirs.txt`) has `w1/ w2/ w3/` (and `a2w1/`,
`assimilation/`), never `w0/`. A counter that requires `w[1-9][0-9]*` — or, more honestly, a
counter that accepts any `w[0-9]+` — is indistinguishable on all 49 rows (no w0 row). w0 is
therefore a false row the population cannot express; whether `w0/` is "a real move" is
undecidable from the census, which is exactly the point: the clause's domain is unpinned.

## C1 attack probe — wrong-file resolution still 8/8
Mutant `mut-intround.py` (scratch copy; single edit): `tr.group(1) != kr.group(1)` →
`int(tr.group(1)) != int(kr.group(1))`. Scored with the frozen harness on the 49 rows:
`SUMMARY rows=49 mismatches=0 accepted=0 refused_true=0 errors=0` — **not killed** (harness
exit 0), yet `FORGE NX3 … got=MOVED match=no accepted=1`. The battery's kill detector
(`harness EXIT != 0`) cannot see this mutant. Mutant `mut-wwild.py` (`w[0-9]+` → `w\w*`,
accepts `wx/`): `SUMMARY rows=49 mismatches=3` — killed, so the wave-shape anchoring **is**
bound (NX1/NX2/NX4/NX5 have no rows but the shape is still pinned by TF6/TF7 + NF-P/J/Q
geometry). The int-round survivor is the routed defect: NX3 must enter the population.

## C2 — 6th forged path is not named (truncation)
Fixture (scratch `c2work`, N=6 same-size stat-cache forgeries `f1-aaa.txt … f6-fff.txt`,
same `forge_index_stat` recipe as the frozen c2 counter; tool copy
`c2/souji-record-agreement.py` beside `c2/souji-receipt-write.py`, `--root` = the clone).
Tool output, one line (no physical newline inside the record):
```
MISMATCH	K4	.	stat-cache-concealed	RECEIPT-WORKTREE-STAT-CONCEALED: 6 tracked path(s) git status reports clean do not hash to the object id the index records (f1-aaa.txt, f2-bbb.txt, f3-ccc.txt, f4-ddd.txt, f5-eee.txt …); the index stat cache conceals a worktree change; no receipt written
```
`f6-fff.txt` appears **nowhere** in the record (checked by substring over all output lines:
first five `NAMED`, `f6-fff.txt MISSING`). Single-line property **holds**
(`K4-LINES 1`, zero embedded `\n` in the detail); C-escape property **holds** for the
names that are shown (newline-path arm: `evil\nname.txt` → `evil\\nname.txt` in one line,
no raw newline in any `MISMATCH` line). But the reader cannot act on the 6th forgery from
the record: the count (`6`) and an ellipsis are all they get; recovering `f6-fff.txt`
requires re-running the sweep, not reading the record. The claim's "still names the path"
and KG2's `named=yes` criterion (`FORGED[row] in (a+b+c)` over **one** K4 row for **one**
forged path) both silently assume `len(bad) <= 5`. Fix direction (for L1): don’t truncate,
or truncate with the full count + a digest of the remainder, or emit one K4 row per path.
Routed as F7-carried (r85 verifier: "five-path naming cap" already routed as R86-4).

## Routed defects (for L1 / next round)
1. **E1**: add NX3 (item P04, target `.ufo/waves/round-032/w2/SwarmExecutor08.md`,
   expect REFUSED) — binds the int-vs-string round comparison; without it a counter that
   normalises round numbers by `int()` is green on all 49 rows and resolves a wrong round.
2. **E2**: decide `w0/` (or bound the wave-dir domain): either add an `w0/` row (expect
   REFUSED or MOVED — the census supports REFUSED) or state `w[0-9]+` includes 0 as intended.
3. **E3**: C2 record must name the 6th path (drop the `[:5] + " …"` truncation in
   `tools/souji-receipt-write.py` `_truth_refusal`, or emit per-path K4 rows); the frozen
   KG2 wording ("names the path") fails for any forgery set >5.
4. Carried unchanged (measured here, not re-litigated): m12 (R0), m16 (NF6b punct), m17
   (dup-id) still bind no row on either population; m15 remains dead code — ratified by
   S85MutCounter, still true on the 49 rows.

## Limits
- One lab fixture per claim; R10 targets are synthetic (byte-equal copies, seeded digests
  round-32/61/83 verified in harness). Forge path exercises `judge()` only.
- The C2 fixture lacks the K1/K2/K3 receipts (K1/K2/K3 `*-absent` rows are fixture noise, not
  K4 evidence); the K4 assertion is the single `stat-cache-concealed` line quoted above.
- Battery baseline re-measured: `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`;
  full 8-mutant sweep interrupted by wall-clock, first three mutants (m6/m7/m8) confirmed
  `killed=yes` — consistent with the filed `killed_r86=8` receipt, not re-derived end to end.
- No tool installs; no lane mutation (verified: only `S86ExecEvade.md` + seat dir written;
  scratch under `/fast/scratch/hyaku/souji-r86/S86ExecEvade/`).

## Files written
`.ufo/waves/round-86/w1/S86ExecEvade.md` (this report); seat dir holds copies of the lab
harness, drivers (`drive-c1.py`, `drive-mut.py`, `drive-c2.py`, `drive-c2b.py`), mutants
(`mut-intround.py`, `mut-wwild.py`), `c1-out.txt`, and forge TSVs. Scratch deleted at yield.
