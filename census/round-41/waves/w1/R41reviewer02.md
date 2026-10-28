# R41reviewer02 — independent re-derivation of C1 item I3 (calibration)

Seat: R41reviewer02 (reviewer, leaf). Read-only. No candidate file written, no git mutation, no tool installed.
Measured rev: `bffcc0f660ff36eb8add3f61582748a7af019a5b` (round-40 final receipts). Freeze: `e2a74312af4233963e44e4dbb38838ece07b8bd2`.

## Question
1. Which register file did each arm of the r40 C1 receipts read (receipt headers + round-40 counter)?
2. Does the SCORECARD r40 C1 row present the two arms as like-for-like?
3. Is the round-41 counter's derived string `before=6,after=3` the right thing to pin?

## Findings

### F1 — the two arms read different register files, at different revisions (verified)
Receipt headers at `bffcc0f`:
- `census/round-40/records/c1-before.txt`: `# measured_at: 0242085909fb6a4ee041c5443d76316ac6d59d4b`; `# command: ... --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b ... --register census/round-39/cells.tsv`. SUMMARY reads `register_cells=6`.
- `census/round-40/records/c1-after-h.txt`: `# measured_at: dc8bd47c693097a69ccaa39b514ce9689a642edc`; `# command: ... --rev dc8bd47c693097a69ccaa39b514ce9689a642edc ... --register census/round-40/cells.tsv`. SUMMARY reads `register_cells=3`.

Register files at `bffcc0f` (read with `git show`):
- `census/round-39/cells.tsv`, blob `6dae3ffb0d01c87f7edb7fd9d0d021cf910be7c3`: 6 data rows REG-07..REG-12, all `commit a8e6d75b3183849129fca01f959dbe5a69cf066c`. Unchanged between `0242085` and `bffcc0f` (`git diff --stat 0242085 bffcc0f -- census/round-39/cells.tsv` empty).
- `census/round-40/cells.tsv`, blob `8e37db34c0627fde2087554519fd9bcce728c678`: 3 data rows R40-CELL-01..03, all `commit 556c24a5cacf208c5144c459838712594a43e1f2`. Added at `549d9ec`. It does not contain the r39 rows.

The round-40 counter takes `--register` as a CLI argument (`census/round-40/c1-counter.py`, argparse near line 374); `register_leg` (line ~179) passes it to the reconciler; `parse_register` (line ~158) counts rows, which becomes `register_cells`. So `register_cells` is the row count of whichever file the arm was given, not a property of the instrument.

Independent re-run of the frozen round-40 counter at one common rev (`--rev bffcc0f...`, `--root` the lane, scratch under the seat scratch dir, which I removed afterward):
- Run A, `--register census/round-39/cells.tsv`: `REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok`; `SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=6 register_mismatches=0 register_violations=0 commit_rows=6 commit_hashes=1`; rc=0.
- Run B, `--register census/round-40/cells.tsv`: `REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok`; `SUMMARY ... register_cells=3 ... commit_rows=3 commit_hashes=1`; rc=0.

Same rev, same counter, different register file gives 6 vs 3. The before→after "6→3" therefore tracks the register input, not the rev or the code. Both arms' register legs are clean (`violations=0`, `mismatches=0`), so the register arm did not regress and did not improve; the number change is an input-size artefact. The receipts also differ in `--rev` (0242085 vs dc8bd47).

### F2 — the round-41 counter's I3 derivation is a readback of printed text, not a re-derivation of inputs
`census/round-41/c1-counter.py` lines 79-85: for `register-cells` it reads `register_cells=(\d+)` out of the two receipt blobs at MEASURED and returns `before=<a>,after=<b>` with mismatch = `vals[0] != vals[1]`. It never reads the `# command:` header, the `--register` path, or the `--rev`, and never looks at the register blobs. Its output at the freeze rev `e2a7431` (the items table is absent at `bffcc0f`, so this is the earliest rev where the counter can evaluate; the derivation itself reads MEASURED):
`ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=0 intact=yes`, `SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=0 rewritten=0 sourced=0`, rc=1. This matches the frozen control `census/round-41/controls/c1-control.txt`.

### F3 — the SCORECARD r40 C1 row presents the arms as a before→after pair without disclosing the input difference
`SCORECARD.md` line 791 at `bffcc0f`, row "C1 evidence-bound closures + strict-descendant register | calibration 7":
- before cell: `SUMMARY items=3 open=3 register_cells=6 ...` rc 1 at the frozen base (`c1-before.txt`). The `...` elides the arguments, which carry `--register census/round-39/cells.tsv` and the 0242085 rev. Neither is named in the row.
- after cell: `... register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1` rc 0 (`c1-after-d.txt`).
- counting command cell names only the after command (`--register census/round-40/cells.tsv`, `--rev <full40>`).
- measured-commit cell: `549d9ec...` and cites `c1-after-d.txt`, not the later `c1-after-h.txt` (the SCORECARD's own line 811 names h as the final instrument measurement; the fixture count in the row reads `cases=8`, h reads `cases=11`).

The row sits in a before/after table with a shared claim name and a shared "counting command" column, and nothing in it says the register inputs or revs differ. So it presents the pair as like-for-like. The spot-check that routed this, `corpus/lessons/round-40-verifier-spotcheck.md` (committed at `7eebc18`, after `bffcc0f`; lines 33 and 73, routed defect R40-D-C1-BEFORE: "state per-arm like-for-like inputs or run the before arm on the same register file"), was not applied to the row at `bffcc0f`. Filed item I3 ("like-for-like") is therefore a fair statement to mark MISMATCHED.

### F4 — is `before=6,after=3` the right thing to pin?
Verdict: the verdict (MISMATCHED) and the values are right; the derivation is a weak proxy, and the pin should be reported as a limit, not as proof of the cause.
- Values: correct. Both independently reproduced (F1 Runs A/B; the receipts print 6 and 3).
- What it proves: that the two printed numbers differ. It does not prove the cause. The cause is the register path (`round-39` vs `round-40`) and the rev. Neither appears in the pinned string, and the CORRECTION regex (`LINE` in the round-41 counter, `source=(\S+)\s*$`) forbids any trailing explanation on the CORRECTION line itself. A reader of the correction gets "6 vs 3" with no reason.
- Predicate is a proxy. `vals[0] != vals[1]` (line 85) is the mismatch test. Two different register files with the same row count would read mismatch=no (false negative: a like-for-like failure goes unflagged). The same file read at two revs with different row counts would read mismatch=yes (false positive). I did not execute these two synthetic cases; this is from reading line 85.
- Better derivation (for the L1 to record as a finding, not an edit to the frozen counter): read the `--register` path and `--rev` from each receipt's `# command:` header, and compare the register blob ids at MEASURED (`6dae3ff...` vs `8e37db3...`). That derivation would state the cause.
- Recommendation for the lesson prose (not the CORRECTION line, which the counter parses strictly): keep the CORRECTION line exactly `derived=before=6,after=3`, and add a prose line elsewhere in `corpus/lessons/round-41.md` naming the two register files and the two revs. The counter ignores non-CORRECTION lines, so the cause can be stated without breaking the frozen parse.

## Commands run (verbatim, exit codes observed)
1. `git -C L cat-file -t bffcc0f...` -> `commit`; `merge-base --is-ancestor 0242085... bffcc0f...` -> ANC_OK.
2. `git -C L show bffcc0f:census/round-40/records/c1-before.txt | head -3` and the same for `c1-after-h.txt`: headers as in F1.
3. `git -C L show bffcc0f:census/round-39/cells.tsv | grep -vc '^#'` -> `7` (6 rows + header); `census/round-40/cells.tsv` -> `4` (3 rows + header). Data-row counts with `grep -c '^REG-'` / `grep -c '^R40-CELL-'`: `6` / `3`.
4. `git -C L diff --stat 0242085 bffcc0f -- census/round-39/cells.tsv census/round-40/cells.tsv` -> only `census/round-40/cells.tsv | 4 ++++` (new file).
5. `python3 -B census/round-40/c1-counter.py --root L --rev bffcc0f --items ... --forged ... --register census/round-39/cells.tsv --min-cells 3 --min-commit-rows 3 --scratch <seat scratch>` -> `REGISTER cells=6 ... ok`, `SUMMARY items=3 open=0 ... register_cells=6 register_mismatches=0 register_violations=0 commit_rows=6 commit_hashes=1`, rc=0.
6. Same with `--register census/round-40/cells.tsv` -> `REGISTER cells=3 ... ok`, `SUMMARY ... register_cells=3 ... commit_rows=3 commit_hashes=1`, rc=0.
7. `python3 -B census/round-41/c1-counter.py --root L --rev bffcc0f...` -> `REFUSAL COULD-NOT-EVALUATE: items table absent or differs from the pinned digest` (rc 2): the items table `census/round-41/c1-items.tsv` is absent at `bffcc0f` (present at `e2a7431`).
8. `python3 -B census/round-41/c1-counter.py --root L --rev e2a74312af4233963e44e4dbb38838ece07b8bd2 --scratch <seat scratch>` -> `ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=0 intact=yes`; `SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=0 rewritten=0 sourced=0`; rc=1.
9. `git -C L show bffcc0f:SCORECARD.md | sed -n 791p | awk -F'|' ...` -> the row cells quoted in F3.
10. `git -C L log --oneline -1 -- corpus/lessons/round-40-verifier-spotcheck.md` -> `7eebc18`; `git -C L show bffcc0f:corpus/lessons/round-40-verifier-spotcheck.md` -> fatal (absent at bffcc0f).
11. `git -C L log --oneline -- census/round-40/c1-counter.py` -> `42e18ed`, `994de3b`, `128e412`; `git diff --stat 128e412 bffcc0f -- census/round-40/c1-counter.py` -> 28 insertions, 6 deletions. Counter bytes changed between the first counter commit and the measured rev; the `c1-before.txt` receipt header does not record a counter blob id, so I cannot prove which counter version produced it. (Noted as an unpinned second difference between the arms.)

Scratch dir `/fast/scratch/hyaku/souji-r41/R41reviewer02` removed (verified). No tools installed. Nothing written outside this report.

## Verdict
- I3 is **MISMATCHED**: correct. The two arms read different register files (`census/round-39/cells.tsv`, 6 rows; `census/round-40/cells.tsv`, 3 rows) at different revs (0242085, dc8bd47). The SCORECARD r40 C1 row (`bffcc0f`, line 791) presents them as a before→after pair without disclosing either difference; it is not like-for-like.
- Derived string `before=6,after=3`: values correct and reproducible; it is the frozen counter's own value and should be the pinned CORRECTION value. It is a proxy for the cause (register input), not a derivation of it; report that as a limit. Recommend the prose of the round-41 lesson name the register files and revs, since the CORRECTION line cannot.
- Residual / not verified: the two synthetic counter cases in F4 (equal-count/different-file and same-file/different-count) were reasoned from line 85, not executed. The before receipt's counter version is not pinned in its header (F-command 11).
