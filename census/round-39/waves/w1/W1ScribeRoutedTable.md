# W1ScribeRoutedTable — routed-defect disposition table (souji r39 w1)

Role: scribe (leaf member; no subagent dispatch). Scope: one row per r38 spot-check routed defect
R1–R16 with the spot-check's claim, the lane artifact that closes it, its carrier (C1 item, C2 leg,
or `errata` for fleet bytes) and a re-runnable verification command. Read-only git only; no
commit/stash/jj; no lane file written but this report. **No tool installed or upgraded** (none
needed; pacman untouched; no `uv tool`/`npx`/binary install).

Revisions cited (never `HEAD` — see F6):
`REV=d4c17557b92fd98044e4c8f0ddc79c6d75701b15`, `BASE=ed30b7f5b77939c9073348d810730bc4f355708d`.
Contract read first: `census/round-39/preregistration.txt` (freeze `b769bfb8…`, amendment A1).
Spot-check read: `corpus/lessons/round-38-verifier-spotcheck.md:136-211` (`## Routed defects`).
Scratch: `/fast/scratch/hyaku/souji-r39/W1ScribeRoutedTable` — **deleted at the end of this seat**
(`rm -rf`; nothing retained, no fixture tree, no `/tmp` root, no lane clone).

Command shorthand used by the table (every command below is run after `cd
/home/vgpnk/Projects/shokunin/souji-shokunin` with `TMPDIR=/fast/scratch/hyaku/souji-r39/W1ScribeRoutedTable`):

```
REV=d4c17557b92fd98044e4c8f0ddc79c6d75701b15
BASE=ed30b7f5b77939c9073348d810730bc4f355708d
CNT1='python3 -B census/round-39/c1-counter.py --root . --rev $REV --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv'
CNT2='python3 -B census/round-39/c2-counter.py --root . --rev $REV --base-rev $BASE'
CNT3='python3 -B census/round-39/c3-counter.py --root . --rev $REV --base-rev $BASE'
```

## 1. Deliverable — R1–R16 disposition table

`state` is my measured reading at `REV`, not the round's claim: `CLOSED` = the frozen C1 counter
prints `ITEM <id> CLOSED`; `OPEN` = it prints `ITEM <id> OPEN FILE-ABSENT …`.

| # | spot-check claim (≤15 words) | lane artifact that closes it | carrier | state @ `REV` | verification command |
|---|---|---|---|---|---|
| R1 | Sources block reads 162→167, A×5, 44 W04; tip measures 170, +8, 47 W04. | `corpus/lessons/round-38.md:285` (`SOURCES-rows=170`, `SOURCES-added=8`, `W04=47`, `S246`) | R39-C1-01 | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-01'` |
| R2 | Opening says "4 + 0 dead"; disk shows 42/42 w1, 32/32 w2, one late seat. | `corpus/lessons/round-38.md:287` (`w1-reports=42/42`, `w2-reports=32/32`, `dead=0`); report-side half is fleet bytes | R39-C1-02 + **errata** | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-02'` |
| R3 | Report filed before WAVE-DONE; late-seat findings left unintegrated. | `census/round-39/records/waves-wait.txt` — **absent** at `REV` | R39-C1-03 (conduct) | **OPEN** | `$CNT1 \| grep 'ITEM R39-C1-03'` |
| R4 | Wave evidence untracked: `.ufo/waves/` gitignored, so 74 seat reports exist only locally. | `census/round-39/records/waves-capture.txt` — **absent** at `REV` | R39-C1-04 | **OPEN** | `$CNT1 \| grep 'ITEM R39-C1-04'` |
| R5 | Commit 068f75dc added `.ufo/prompts/souji-round-38.md` outside lane scope; ledger row denied it. | `corpus/lessons/round-39.md:49` (erratum naming `068f75dc`); the denied ledger row is fleet bytes | R39-C1-05 (**erratum**) | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-05'` |
| R6 | Four r38 claim counters carry no SKILL.md gate-registry row. | `SKILL.md:283` (all four stems named) | R39-C1-06 | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-06'` |
| R7 | Receipt base arm names a reaper-deleted `$HYAKU_SCRATCH` path; command not re-runnable. | `corpus/lessons/round-39.md:51` (`5f0dd45`, `cites-a-revision`, no literal scratch root) | R39-C1-07 | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-07'` |
| R8 | Prereg pointer stale (a7-counter-fixes.txt); r38-counter-arms.py missing from instrument table. | `census/round-38/preregistration.txt:229` (A10 names `a7-counter-fixes2.txt`, `r38-counter-arms.py`) | R39-C1-08 | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-08'` |
| R9 | Frozen prereg sentence rewritten in place, relaxing the tighter-only amendment rule. | `census/round-38/preregistration.txt:231` (A11 names the superseded sentence) | R39-C1-09 | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-09'` |
| R10 | Drift docstring says RECORD-MISSING means unreadable; a missing path raises RECORD-MALFORMED. | `tools/souji-worktree-drift.py:44-48` docstring + the classes the code raises | **C2 leg L4** (contract) | **PASS** | `$CNT2 \| grep 'LEG L4'`; direct: `python3 -B tools/souji-worktree-drift.py --root . --record nope.tsv` |
| R11 | Citation tool turns an unresolvable `--rev` into findings with exit 1, never exit 2. | `tools/souji-citation-reconcile.py` revision resolution + `tests/fixtures/r39-citation-rev.py` | **C2 legs L1/L2/L5** (contract) | **PASS** | `$CNT2 \| grep -E 'LEG L[125]'`; direct: `python3 -B tools/souji-citation-reconcile.py --root . --rev 0123456789abcdef0123456789abcdef01234567 --register census/round-38/cells.tsv` |
| R12 | SCORECARD "Final tip 99efe06" label measures two commits behind fcdecaa. | `SCORECARD.md:739` (`fcdecaa` named as `measured-revision`) | R39-C1-10 | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-10'` |
| R13 | Stale literals: LOG cases=9 fail=6, cells=9, and QUALITY "(0)" as escape count. | `LOG.md:1875`, `LOG.md:1877`, `corpus/QUALITY.md:222` | R39-C1-11, R39-C1-12, R39-C1-13 | **CLOSED** | `$CNT1 \| grep -E 'ITEM R39-C1-1[123]'` |
| R14 | Vacuity receipt claims a one-row substitution gives mismatches=9; faithful reading is 3. | `corpus/lessons/round-38.md:289` (`vacuity-operation=mismatches=3`, `three-rows`) | R39-C1-14 | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-14'` |
| R15 | Landed-changes table names 12 of 21 commits, ending on `<integration>` placeholder. | `corpus/lessons/round-39.md:53` (the nine unnamed hashes); report-side half is fleet bytes | R39-C1-15 + **errata** | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-15'` |
| R16 | r37 routed defect 4 still owed: no appended correction for round-36.md:23. | `corpus/lessons/round-36.md:176` (appended correction) | R39-C1-16 | **CLOSED** | `$CNT1 \| grep 'ITEM R39-C1-16'` |

Marking asked for by the seat: **R3 = conduct defect** (a filing-timing/process breach, not a value
mismatch; its carrier is the wave-wait receipt R39-C1-03, and it is the one conduct row that is still
open). **R10 and R11 = contract defects** (a docstring→class mismatch and a revision-resolution
contract), both carried by **C2 legs**, not by any C1 item row.

The three `errata` marks are the fleet-byte halves the prereg's `## Not claimed` section excludes from
the lane's write scope: R2's report opening line, R5's denied ledger row, R15's report table. The lane
records them in its own bytes; the fleet report itself is not corrected here.

## 2. Commands run and observed output

### 2.1 C1 counter at `REV` (the table's `state` column)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && TMPDIR=$S python3 -B census/round-39/c1-counter.py \
  --root . --rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 --items census/round-39/c1-items.tsv \
  --register census/round-39/cells.tsv --scratch $S
```

Output, verbatim (rc 1):

```
ITEM R39-C1-01 CLOSED
ITEM R39-C1-02 CLOSED
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
ITEM R39-C1-05 CLOSED
ITEM R39-C1-06 CLOSED
ITEM R39-C1-07 CLOSED
ITEM R39-C1-08 CLOSED
ITEM R39-C1-09 CLOSED
ITEM R39-C1-10 CLOSED
ITEM R39-C1-11 CLOSED
ITEM R39-C1-12 CLOSED
ITEM R39-C1-13 CLOSED
ITEM R39-C1-14 CLOSED
ITEM R39-C1-15 CLOSED
ITEM R39-C1-16 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```

Verdict: **C1 predicate NOT met at `REV`.** The frozen predicate requires `open=0`,
`register_cells>=6`, `commit_distinct>=2`; measured `open=2`, `register_cells=0`,
`commit_distinct=0`. 14 of 16 item rows are CLOSED. I claim closure for exactly those 14 and for
nothing else. (`items_sha=d892b74f8358` equals the value in `records/c1-before.txt`, so the item list
is the frozen one.)

### 2.2 C2 counter at `REV`

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && TMPDIR=$S python3 -B census/round-39/c2-counter.py \
  --root . --rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $S
```

Output, verbatim (rc 0):

```
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
```

Verdict: **PASS** — `legs=6 pass=6 fail=0 harm=0`, and the base arm discriminates (`L5` new 8/8 vs
base 4 pass / 4 fail, `L1`/`L2` base rc 1 class=False). This is the carrier for **R10 (L4)** and
**R11 (L1/L2/L5)**. See F3 for the `fixture_sha` field.

### 2.3 C3 counter at `REV`

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && TMPDIR=$S python3 -B census/round-39/c3-counter.py \
  --root . --rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $S
```

Output, verbatim (rc 0):

```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
```

Verdict: **PASS** — every field of the frozen C3 predicate is met, `cases=7 >= 6`. C3 carries no
routed defect row (it answers the r38 *limit*, not a routed defect), so it appears in this table only
as context.

### 2.4 Direct probes for R11 (revision resolution)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && BLOB=$(git rev-parse 2201778e7736af82e7d8a42dec2494f115bf3923:LOG.md)
out=$(python3 -B tools/souji-citation-reconcile.py --root . --rev 0123456789abcdef0123456789abcdef01234567 \
        --register census/round-38/cells.tsv 2>&1); rc=$?
out2=$(python3 -B tools/souji-citation-reconcile.py --root . --rev "$BLOB" --register census/round-38/cells.tsv 2>&1); rc2=$?
```

Observed:

```
BOGUS rc=2 first=REFUSAL REV-UNRESOLVED: --rev 0123456789abcdef0123456789abcdef01234567 does not resolve to a commit
BLOB rc=2 first=REFUSAL REV-UNRESOLVED: --rev e02a09766b4add57a80e687b90122a00baba1db6 does not resolve to a commit
```

Verdict: **PASS for R11** — both an unresolvable and a blob `--rev` exit **2** with the class
`REFUSAL REV-UNRESOLVED`, which is what the base bytes did not do (`LEG L1`/`L2` `old rc=1
class=False`).

### 2.5 Direct probe for R10 (docstring vs raised class)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "RECORD-MISSING\|RECORD-MALFORMED" tools/souji-worktree-drift.py | head -12
out3=$(python3 -B tools/souji-worktree-drift.py --root . --record nope.tsv 2>&1); rc3=$?
```

Observed (docstring, lines 44-48):

```
  RECORD-MISSING         EACCES or ELOOP opening the record path: the path
                         exists but cannot be opened or read
  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line
                         that does not match the schema, a duplicated name, or
                         a TOTAL row that disagrees
```

Observed (behaviour): `DRIFT-MISSING rc=2 first=REFUSAL RECORD-MALFORMED: nope.tsv is not a regular file`

Verdict: **PASS for R10** — the docstring's `RECORD-MISSING` trigger is now EACCES/ELOOP and
`RECORD-MALFORMED` names the missing/non-regular path, matching the class the tool raises (code lines
135-136: missing/non-regular → `RECORD-MALFORMED`, `OSError` → `RECORD-MISSING`).

### 2.6 Artifact-existence probes (R3, R4 and the register arm)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && R=d4c17557b92fd98044e4c8f0ddc79c6d75701b15
for f in census/round-39/records/waves-wait.txt census/round-39/records/waves-capture.txt \
         census/round-39/cells.tsv census/round-39/cells-lines.md; do
  printf '%s: ' "$f"; git cat-file -e "$R:$f" 2>/dev/null && echo TRACKED || echo ABSENT; done
git grep -c -E "R39-REG-0[1-6]" "$R" -- SCORECARD.md LOG.md corpus/QUALITY.md; echo "REG_GREP_RC=$?"
```

Observed:

```
census/round-39/records/waves-wait.txt: ABSENT
census/round-39/records/waves-capture.txt: ABSENT
census/round-39/cells.tsv: ABSENT
census/round-39/cells-lines.md: ABSENT
REG_GREP_RC=1
```

Verdict: **R3 and R4 are OPEN at `REV`** (their closing receipts do not exist in lane bytes), and the
**citation register is unbuilt** (`cells.tsv` absent, no `R39-REG-0N` anchor line in `SCORECARD.md`,
`LOG.md` or `corpus/QUALITY.md`), which is why `register_cells=0` and `commit_distinct=0`.

### 2.7 `fixture_sha` provenance probe (finding F3)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "fixture_sha =" census/round-39/c2-counter.py census/round-39/c3-counter.py
for r in 2201778 d4c1755; do printf '%s fixture=%s\n' "$r" "$(git show $r:tests/fixtures/r39-citation-rev.py | sha256sum | cut -c1-12)"; done
sha256sum tests/fixtures/r39-citation-rev.py | cut -c1-12
```

Observed:

```
census/round-39/c2-counter.py:170: fixture_sha = hashlib.sha256(open(os.path.join(os.path.abspath(root), "tests/fixtures/r39-citation-rev.py"), encoding="utf-8").read().encode()).hexdigest()[:12]
census/round-39/c3-counter.py:130:        fixture_sha = hashlib.sha256(candidate_src.encode()).hexdigest()[:12]
2201778 fixture=7ab7c3d85a81
d4c1755 fixture=e555d8281484
worktree e555d8281484
```

An earlier C2 run in this seat used `--rev 2201778e…` and printed
`SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484`,
while `census/round-39/records/c2-after.txt` records `fixture_sha=7ab7c3d85a81` for that revision.
`diff` of the two readings:

```
7c7
< SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
---
> SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
```

Verdict: the C2 predicate fields reproduce; **`fixture_sha` does not**, because `c2-counter.py:170`
hashes the *working-tree* fixture instead of the `--rev` bytes. `c3-counter.py:130` hashes the mutant
source it constructs, so C3's field is reproducible (`diff` against `records/c3-after.txt` → identical).

## 3. Verdicts per check

| check | verdict |
|---|---|
| Frozen contract read before any row was written | **PASS** — `census/round-39/preregistration.txt` (incl. amendment A1) and the spot-check's `## Routed defects` read first |
| R1–R16 rows carry claim / artifact / carrier / command | **PASS** — 16 rows; every command re-runnable from committed bytes except the R10/R11 legs' `fixture_sha` field (F3) |
| R3 marked as a conduct defect | **PASS** — marked, and it is OPEN (F2) |
| R10, R11 marked as contract defects | **PASS** — marked, carried by C2 L4 and L1/L2/L5 |
| No closure claimed beyond the receipts | **PASS** — 14 item rows CLOSED by my own counter run; R3/R4 declared OPEN; the register arm declared unbuilt; no C1 predicate claim |
| C1 predicate `open=0 register_cells>=6 commit_distinct>=2` | **FAIL at `REV`** — `open=2 register_cells=0 commit_distinct=0`, rc 1 |
| C2 predicate `legs=6 pass=6 fail=0 harm=0` | **PASS at `REV`** — reproduced, rc 0 |
| C3 predicate `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6` | **PASS at `REV`** — reproduced (`cases=7`), rc 0 |
| Base controls unchanged by this seat | **PASS (not re-run to confirm)** — `c1-before.txt` `items_sha` matches my run; `c2-before`/`c3-before` cited, not re-executed |
| Lane bytes written by this seat | only this report; scratch deleted |

## 4. Findings

**F1 — the C1 predicate is not met at the current lane tip, on the two conduct/evidence rows.**
`open=2` (`R39-C1-03` = R3, `R39-C1-04` = R4), both `OPEN FILE-ABSENT`; `register_cells=0` and
`commit_distinct=0` because no `cells.tsv` exists. So the C1 claim as frozen (`open=0`,
`register_cells>=6`, `commit_distinct>=2`) is **false at `REV`**, and the table must not say
otherwise. The 14 remaining rows do read CLOSED.

**F2 — R3 and R4 are owed, not closed.** R3 is the round's only **conduct** defect: its closure is
the `waves-wait.txt` receipt proving the report was filed after WAVE-DONE, and that file does not
exist at `REV`. R4's `waves-capture.txt` is likewise absent, which is the same class as the defect it
answers.

**F3 — `c2-counter.py:170` makes one receipt field non-derivable from committed bytes.** The C2
receipt's `fixture_sha` is computed over the working-tree fixture, so a re-run at the *receipt's own*
revision printed `e555d8281484` against the receipt's `7ab7c3d85a81` while all six `LEG` lines and
`tool_sha` matched. This is the r38 R7/R14 class (a receipt describing an operation it did not
perform) reproduced inside the r39 instrument. It does not touch the C2 predicate, which has no
`fixture_sha` clause; it does mean `c2-after.txt` cannot be byte-reproduced from committed bytes
alone. Reported, not fixed (I am advisory; the L1 integrates).

**F4 — the after-receipts and the register generator are uncommitted at `REV`.** `git status
--porcelain` at `REV` reads exactly:

```
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
```

My C2/C3 readings reproduce those two receipts' predicate fields, but as bytes they are working-tree
only — the R4-class condition R4 itself routes. Only the L1 can land them.

**F5 — contract wording carried verbatim.** The prereg's C1 paragraph says "R3 and R10 are
conduct/contract defects carried by the same register". Measured: R3's carrier is the C1 item row
`R39-C1-03` (a wave receipt, not the citation register) and R10's carrier is **C2 leg L4** (no C1
row exists for it — `c1-items.tsv` has 16 rows, none anchored in the drift tool's docstring). I record
the discrepancy and do not resolve it.

**F6 — the lane is jj-colocated and `HEAD` moved during this seat** (`2201778e…` → `d4c1755…`,
"round-39: C3/scratch — honour the caller's TMPDIR …"). Every reading above is cited by literal
40-hex revision; `HEAD` appears nowhere as a measurement anchor.

## 5. Verdict

The table is delivered with 16 rows, 14 measured CLOSED, R3/R4 measured OPEN, R10/R11 verified
through C2, and three `errata` marks for the fleet-byte halves. **The round's C1 claim does not
verify at `REV`** (F1/F2/F4: two items open, register unbuilt, after-receipts uncommitted); C2 and C3
predicates do verify. No closure is claimed that a receipt does not show.

Scratch `/fast/scratch/hyaku/souji-r39/W1ScribeRoutedTable` deleted (`rm -rf`) at seat end; no tree
retained, no `/tmp` root used, no lane clone made. No tool installed or upgraded.

## 6. Addendum (written after §5; live worktree state, not a re-run of any check)

While confirming that this seat wrote nothing but this report, `git status --porcelain` at `REV`
listed four modified tracked files that this seat did not touch, one of them a **frozen receipt**:

```
 M LOG.md
 M SKILL.md
 M census/round-39/records/c2-before.txt
 M corpus/QUALITY.md
```

`git diff -- census/round-39/records/c2-before.txt` (verbatim):

```
@@ -1,7 +1,11 @@
+# C2 control — command:
+#   python3 -B census/round-39/c2-counter.py --root . --rev ed30b7f5b77939c9073348d810730bc4f355708d --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $S
+# instrument bytes: counter at d4c17557b92fd98044e4c8f0ddc79c6d75701b15, fixture tests/fixtures/r39-citation-rev.py (sha below)
 LEG L1 FAIL new rc=1 class=False old rc=1 class=False
 ...
-LEG L5 FAIL new=(8, 5, 3, 1) old=(8, 5, 3, 1)
+LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
 ...
-SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=c142c1bc28b8
+SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=e555d8281484
+# rc=1
```

Two observations, reported and not acted on:

1. **A frozen control receipt is being rewritten in place.** The seat hard rules forbid editing any
   frozen receipt; the r38 R9 routed defect is exactly "the frozen prereg was rewritten in place", and
   this is the same class one round later, in a `records/*-before.txt` control. The `SUMMARY` numbers
   (`pass=2 fail=4`) are unchanged, so the predicate value is not harmed — the bytes are.
2. **The rewritten `LEG L5` line is what F3 predicts.** `census/round-39/c2-counter.py:64` states its
   own design: "Instrument (fixture) bytes come from the working tree; audited tool bytes come from
   `--rev`." The fixture was amended (A1) after the control was frozen, so re-running the control
   today reads the amended fixture (`new=(8,4,4,1)`, `fixture_sha=e555d8281484`) where the frozen
   control recorded `(8,5,3,1)` / `c142c1bc28b8`. The frozen control is therefore **not reproducible
   from committed bytes alone** — the receipt's own disclosure (F3) makes that unavoidable, and the
   correct repair is a disclosed, appended re-derivation, not an in-place edit.

Register state at the same moment (checked because `make-cells.py` and the four modified files above
look like the register landing): `census/round-39/cells.tsv` and `cells-lines.md` are still **absent**
and `grep -c "R39-REG-0" SCORECARD.md LOG.md corpus/QUALITY.md` reads `0` for each, so the C1
register arm remained unbuilt at the time of writing and F1 stands.
