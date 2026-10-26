# SwarmExecutor03 — round 30 wave 1, C1 corrections for rows R01-R06

## Status

STATUS: PASS — the four base MISMATCH rows in R01-R06 (R03, R04, R05, R06) each get an append-only
`R30-CORRECTION` line without `cmd=`, and every one reads `CORRECTED` in a scratch clone at rev
fb2b937ce87a93c9ab0a817f19232717c1ff4fff with `SUMMARY k1=0 k2=0 mismatches=0 rows=4 pointers=10
partial=1` and counter exit 0 (two identical runs). R01 and R02 already MATCH and need no line. The
lane was read-only for this seat: no lane file was written except the wave-1 deliverables, no git/jj
mutation in the lane, scratch only under /fast/scratch/hyaku/souji-r30/C1RowsA/.

## Evidence

Base state (census/round-30/records/c1-before.txt, rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b;
lane HEAD df6afe817d096e4ad71ba2b9cc21a83f126eb658, SCORECARD.md and SHONEN.md unchanged since base):

    ROW R01 SCORECARD.md:152 stated=6/6  rc=0 observed=selftest=PASS ids=6/6  MATCH
    ROW R02 SCORECARD.md:153 stated=36/36 rc=0 observed=selftest: 36/36 passed MATCH
    ROW R03 SCORECARD.md:154 stated=5/5  rc=0 observed=SUMMARY total=5 failed=0 hung=0   MISMATCH kind=value
    ROW R04 SCORECARD.md:155 stated=5/5  rc=0 observed=selftest=PASS ids=7/7              MISMATCH kind=value
    ROW R05 SCORECARD.md:158 stated=18/18 rc=0 observed=SELFTEST pass=65 fail=0           MISMATCH kind=value
    ROW R06 SCORECARD.md:158 stated=15/15 rc=0 observed=SUMMARY total=15 failed=0         MISMATCH kind=value

Stability — each MISMATCH row run twice at base; command shown for R03, the others differ only in
`--only` (receipt .ufo/waves/round-30/w1/c1-stability-R03-R06.txt):

    python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-agreement.py \
      --root /home/vgpnk/Projects/shokunin/souji-shokunin \
      --rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b \
      --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631 --only R03 \
      --scratch /fast/scratch/hyaku/souji-r30/C1RowsA/run

Both runs per row printed byte-identical `ROW` lines: R03 `observed=SUMMARY total=5 failed=0 hung=0`,
R04 `observed=selftest=PASS ids=7/7`, R05 `observed=SELFTEST pass=65 fail=0`, R06
`observed=SUMMARY total=15 failed=0`; every run rc=0, `MISMATCH kind=value`, k1=1 for that row.

History that decides the correction (all read this run, base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b):

- `git log -L154,155:SCORECARD.md` → both rows were created in 23014d4 (round 13), unchanged since
  except wording commits; the literals are r13 vintage.
- tests/fixtures/r13-quarantine-bounds.sh:302 at 23014d4 and at base (only SUMMARY printf in the
  file, `grep -c "printf 'SUMMARY"` = 1):
  `printf 'SUMMARY\ttotal=%d\tfailed=%d\thung=%d\n' "$RAN" "$FAILED" "$HANGED"`
- tests/fixtures/r13-repo-structure.sh:70-71 at 23014d4: "`selftest=PASS ids=5/5` (--probe mode)";
  census/round-13/verification.json:74 at base records a probe-mode stdout containing
  `selftest=PASS ids=5/5`.
- `git show --stat 728b2ce -- tests/fixtures/r13-repo-structure.sh` → 242 insertions, two new
  expected ids (SOUJI-R13-STRUCT-linked-common-dir, SOUJI-R13-STRUCT-colocated-vs-plain); the same
  header line 71 at base reads "`selftest=PASS ids=7/7` (--probe mode)".
- tools/souji-landing-gate.py:976 at 7a79dc2 and :2269 at base print the same format
  `print("SELFTEST\tpass=%d\tfail=%d" % (passed, failed))`.
- tests/fixtures/r16-landing-gate.py:528 at 7a79dc2 and at base:
  `print("SUMMARY\ttotal=%d\tfailed=%d" % (len(results), failed))`.
- corpus/lessons/round-19.md:20 states: "`python3 tools/souji-landing-gate.py --selftest` →
  `SELFTEST pass=65 fail=0` (61 before; four wrap cases added)."

Acceptance — scratch clone /fast/scratch/hyaku/souji-r30/C1RowsA/r.YHgmfY/c, cloned `--no-local`
from the lane with `remote remove origin` immediately, toplevel asserted equal to the clone,
identity set with `git -C` inside scratch only, branch r30corr at parent
9420341d9a814cb6089c25fb03a4cc9b23dc0d1b, the correction block appended to SCORECARD.md (verified
byte-identical to the delivered block, 4 correction lines, file still begins with the base bytes) and
committed as fb2b937ce87a93c9ab0a817f19232717c1ff4fff:

    python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-agreement.py \
      --root /fast/scratch/hyaku/souji-r30/C1RowsA/r.YHgmfY/c \
      --rev fb2b937ce87a93c9ab0a817f19232717c1ff4fff \
      --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b \
      --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631 --only R03,R04,R05,R06 \
      --scratch /fast/scratch/hyaku/souji-r30/C1RowsA/accept

    ROW	R03	SCORECARD.md:154	stated=5/5	rc=0	observed=SUMMARY total=5 failed=0 hung=0	CORRECTED
    ROW	R04	SCORECARD.md:155	stated=5/5	rc=0	observed=selftest=PASS ids=7/7	CORRECTED
    ROW	R05	SCORECARD.md:158	stated=18/18	rc=0	observed=SELFTEST pass=65 fail=0	CORRECTED
    ROW	R06	SCORECARD.md:158	stated=15/15	rc=0	observed=SUMMARY total=15 failed=0	CORRECTED
    SUMMARY k1=0 k2=0 mismatches=0 rows=4 pointers=10 partial=1 rev=fb2b937ce87a93c9ab0a817f19232717c1ff4fff
    KINDS value=0 shape=0 rc=0 (diagnostic; not part of the target)

Run twice with identical output; a third run captured the counter's own exit code 0 under
`set -o pipefail`. All 10 SHONEN pointer rows stayed `RESOLVES` in every run. Receipt:
.ufo/waves/round-30/w1/c1-corrections-acceptance.txt

## Findings

1. **R03 (SCORECARD.md:154)** — the `5/5` is the table's N/N notation for the fixture's only summary
   form; the same command still prints `SUMMARY total=5 failed=0 hung=0` (5 cases, 0 failed, 0 hung,
   rc 0). Correction: observed line as is, no `cmd=`.
2. **R04 (SCORECARD.md:155)** — `5/5` was exact at r13 (23014d4 fixture header and
   census/round-13/verification.json:74 both carry `selftest=PASS ids=5/5`); commit 728b2ce (r25) added
   two expected ids, so the identical command now prints `selftest=PASS ids=7/7` (rc 0). Stale count,
   not a different invocation: no `cmd=`.
3. **R05 (SCORECARD.md:158)** — `18/18` was the r16 suite size printed in the same
   `SELFTEST pass=N fail=M` token form; the suite grew to 61 and then 65 checks by r19
   (corpus/lessons/round-19.md:20), and the base tool under the identical command prints
   `SELFTEST pass=65 fail=0` (rc 0). Stale count: no `cmd=`.
4. **R06 (SCORECARD.md:158)** — `15/15` is the table's N/N notation for
   `SUMMARY total=15 failed=0`, the fixture's only summary form since r16; case total and failure
   count unchanged. Correction: observed line as is, no `cmd=`.
5. **No `cmd=` anywhere** — the assignment allows a substituted argv only when the stated command is
   not the invocation that produced the stated count. For all four rows the stated command is exactly
   the invocation (same script, same flags) at the round that wrote the literal, so substituting an
   argv would misrepresent history; the honest record is what the command prints now.
6. **k2 untouched** — no SHONEN line is involved; the 10 pointer rows read `RESOLVES` at both base and
   the acceptance rev, so C1's pointer half is unchanged by this seat.
7. **Integration note for the L1** — `git diff --stat 9420341..HEAD -- SCORECARD.md SHONEN.md` is empty
   on the current lane tip df6afe8, so the delivered block appends identically at the tip and at the
   base; base..HEAD otherwise adds only round-30 files plus the counter itself. Rows R07-R18 are
   outside this seat's scope and carry no line from me.
8. **Risk — acceptance is at a scratch commit, not the lane.** The four observed strings are the
   deterministic last digit-bearing line of each command (5 runs produced identical strings), and the
   commands read tools/fixtures blobs that base..HEAD does not modify, so the L1's landing run at its
   own `--rev` should reproduce them; if the C1 landing commit changed those tools or fixtures the
   observed strings would have to be re-measured before integration.
9. **Risk — junk-control interaction, no control weakened as committed.** The C1 controls build their
   trees from the base (census/round-30/controls.sh), so these appended lines do not reach them.
   If a control were rebased onto a tree already carrying this block, C1-junk1's R05 arm would read
   `CORRECTED` (its k1 would drop from 2 to 1, the R10 arm still failing) because the invented
   observed value in that control contradicts the real output; C1-junk2 stays rejected by append-only
   and C1-junk3 by first-path identity. Not an ATTACK: the mechanism accepts only real printed output.
10. **No tooling installed, no pacman transaction, no host service touched.**

## Deliveries

- .ufo/waves/round-30/w1/deliver-c1-corrections-R01-R06.txt — the four exact lines with `##`-free
  block, per-row reasons, stability summary and acceptance output.
- .ufo/waves/round-30/w1/c1-stability-R03-R06.txt — two base runs per MISMATCH row.
- .ufo/waves/round-30/w1/c1-corrections-acceptance.txt — two acceptance runs plus counter exit code.
- .ufo/waves/round-30/w1/SwarmExecutor03.md — this report.

Scratch /fast/scratch/hyaku/souji-r30/C1RowsA (clone r.YHgmfY, block, logs) was removed with
`rm -rf` after the receipts were copied into this wave directory; no scratch tree is left on disk.
