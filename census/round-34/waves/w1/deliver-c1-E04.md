# C1 slice 5 — E04 (SCORECARD.md:21, landing-gate findings) 

## Counter ITEM line (base 9c76c7222a8abff027af42e37f0d160d52526bba)

```
ITEM	E04	MISMATCH	original	rc=1 expect_exit=2 predicate fails last=SUMMARY findings=19 checked_reg=52 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=19 status_lines=58 carry_heading=0 checked_reports=61 load=4.43
```
Same flocked run as G23 (loadavg before `2.84 2.72 1.92`, after `4.43 3.07 2.04`).

## Prior-correction grep (Q76) — none

`grep -n -E '\| (G23|G24|G26|E01|E04) \|'` and `grep -n 'Round 34 registry restatements'` over `git show 9c76c72:SCORECARD.md`: no match. `grep -n 'findings=0.*checked_reg=52'` finds only the original row itself (line 21). No binding row.

## Cause and executed readings

`where` = `SCORECARD.md:21`, and at 9c76c72 line 21 **is** the `C1 Q57/Q59 pointer findings` row — the where cell is correct for this item.

Value drift exists and is attributable: the gate was rewritten in round 30. But the frozen `same` branch cannot be used, because at the drift cause's parent the pre-r30 gate writes its COULD-NOT-EVALUATE line to **stderr**, and the counter concatenates `stdout + stderr`, so the "last digit-bearing line" is that warning, not the SUMMARY:

```
same-branch probe (engine run, row with run = same):
ITEM	E04	MISMATCH	restated	BAD-CAUSE(original at parent=False at cause=False; need True/False)
direct engine-path reproduction at the parent 7b16731fcd8ab9b95220b50603314aa8dc92b2ec:
  rc=2 ; stdout last digit line = "SUMMARY findings=0 checked_reg=52 ... checked_reports=0" ; stderr = "COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-28/ at de478b48..."
  combined last digit line -> the stderr warning -> frozen predicate fails -> holds=False
```

Executed readings (one fresh clone per commit, fresh TMPDIR, PATH=/usr/bin:/bin + jj, GIT_CONFIG_NOSYSTEM=1; load 10.5–55.8 during the runs):

| commit | role | reading |
|---|---|---|
| `de478b483db66a8d8ff2d627cde1ccce6e21a014` | round-28 landing (the row's measured rev) | `rc=2`, `SUMMARY findings=0 checked_reg=52 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=0 status_lines=0 carry_heading=0 checked_reports=0`, stderr warning present |
| `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb` | **cause**: first commit whose SCORECARD carries the row's exact line text (parent `de478b48` lacks it; checked over all 73 SCORECARD commits) | `rc=2`, same SUMMARY, stderr warning → the row's own argv already failed at the cause (predicate fails on the combined last line) |
| `7b16731fcd8ab9b95220b50603314aa8dc92b2ec` | parent of the drift | `rc=2`, same SUMMARY + warning |
| `68447afef62e4761249af55a2467657f04046537` | drift (r30 gate rewrite; touches `tools/souji-landing-gate.py`) | `rc=1`, `SUMMARY findings=19 checked_reg=52 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=19 status_lines=58 carry_heading=0 checked_reports=61` |
| `9c76c72…` (base) | measured rev | `rc=1`, identical SUMMARY (counter ITEM line above) |

The 19 findings are `LG-SEAT-UNCARRIED` lines over committed `census/round-28/waves/w1/*.md`; they derive from committed bytes at the pinned rev `de478b48`, not from live fleet state, so the reading is stable across tips.

## Proposed row (engine-validated: `ITEM E04 AGREE restated`)

| E04 | SCORECARD.md:21 | restated | 1 | `python3 -B tools/souji-landing-gate.py --root . --rev de478b483db66a8d8ff2d627cde1ccce6e21a014 --round 28 --fleet-root /home/vgpnk/Projects/shokunin` | `SUMMARY findings=19 checked_reg=52 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=19 status_lines=58 carry_heading=0 checked_reports=61` | fec846dd1781a414ae3a7d71d2d8fa2fb17900eb | the after-cell was measured by the pre-r30 gate, which printed COULD-NOT-EVALUATE to stderr over findings=0 rc 2; r30 made the gate resolve and count committed wave reports (68447af: rc 1 findings=19 on the same rev de478b48), so the command now exits 1 with 19 uncarried round-28 seat reports; the command text is unchanged because the value, not the command, drifted, and the value-drift branch cannot hold at 68447af's parent since the pre-r30 warning lands on stderr after SUMMARY |

The command cell is the row's own command (the row's own script `tools/souji-landing-gate.py`), the statement is the run's collapsed LAST digit-bearing line, and the cause is the commit that wrote the row's line. Engine check in a scratch clone (parent of the probe commit = lane tip 51acb5fb6fa38a6b593b3badb674cec559d7eb2c, row appended only):

```
ITEM	E04	AGREE	restated	rc=1 expect_exit=1 statement is the run's last digit-bearing line last=SUMMARY findings=19 checked_reg=52 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=19 status_lines=58 carry_heading=0 checked_reports=61 load=55.82
```
