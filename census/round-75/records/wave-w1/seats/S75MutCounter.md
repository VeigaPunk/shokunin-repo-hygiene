# S75MutCounter — souji r75 w1: mutation test of the C2 instruments (lane @1ad737b, base 52d3f07d)
VERDICT: the r75 C2 numbers RE-DERIVE (3/3 committed tallies, both selftest kills, byte-for-byte). Neither
instrument is falsified; 3/8 tally mutants and 6/9 selftest mutants survive, two load-bearing (F1, F2).
Commands, from lane root: C1 = `python3 -B <counter copy> --selftest --root <lane> --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --work <fresh dir>`;
C2 = `c2-kill-counter.py --pristine P --mutant ID=R ...`. Each mutant = one `.replace(old,new)` on a scratch copy,
asserted to occur exactly once; X09/P1 added by census/round-73/apply-edit.py.
## Re-derivation (nothing taken from L1)
- c2-kill-counter.py sha256 fdb75c09…: replaying the three committed `command=` lines from committed receipts
  gives c2-after.txt `killed=6/6 pristine=PASS EXIT=0`, c2-K-do-nothing-r74.txt `killed=4 survived=2 EXIT=1`,
  c2-K-blanket-pristine-red.txt `pristine=FAIL EXIT=1` — all three MATCH the committed bodies.
- c1-counter.py sha256 90a3c7b2… --selftest: `SELFTEST cases=64 pass=64 fail=0` EXIT=0 (= pristine receipt);
  +X09 -> fail=1 on `witness (r75): a divergence off the row's forged paths is unwitnessed`; +P1 -> fail=1 on
  `witness run (r75): … new-slot row_fate witness is yes`. My P1 rebuild hashes fc91b5b3… = committed
  records/variants/r75-P1-counter.py; all 8 r75 variant counters match their receipt instrument_sha256.
## A. c2-kill-counter.py — 8 single edits over B1 c2-after, B2 do-nothing, B3 blanket, B4 wide (14 receipts),
B5 forged fg1 (`SELFTEST fail=1`, last line `EXIT=0`), B6 forged fg2 (two SELFTEST lines), B7 fg1 as pristine, B8 fg2 as pristine. Killed = any verdict/exit difference.
- M1 `e=="1"`->`e in ("1","2")`: no change B1..B8 | SURVIVOR (p9 `fail=1`+`EXIT=2`: KILLED vs base UNREAD)  ||  M2 `f>=1`->`f>=0`: no change | SURVIVOR =M8 (p10 `fail=0`+`EXIT=1`: KILLED vs base UNREAD)
- M3 drop `pv=="PASS"`: B3/B7/B8 exit 1->0, verdict lines identical | KILLED (exit code only)  ||  M4 first SELFTEST wins: B6 FG2 UNREAD->SURVIVED, B8 PRISTINE FAIL->PASS | KILLED
- M5 UNREAD->KILLED: B5/B6 forged UNREAD->KILLED, exit 1->0 | KILLED  ||  M6 `killed==n`->`killed>0`: B2/B4 exit 1->0 | KILLED (exit code only)
- M7 first `EXIT=` line: B5 FG1 UNREAD->KILLED, B7 pristine exit 0->1 | KILLED  ||  M8 drop `f>=1`: no change | SURVIVOR =M2
F1 MEDIUM: no committed receipt carries `EXIT=2` or (`fail=0`,`EXIT=1`), so the tally cannot distinguish a
mutant scoring a passing/aborted receipt KILLED (M2/M8) or a crashed one KILLED (M1); p9/p10 are the missing
controls. M3/M6 are killed on exit code alone — verdict lines carry no evidence of those defects.
## B. r75 selftest blocks (c1-counter.py:2019 row_fate check, :2037-2052 setup-only check) — 9 single edits,
each re-run; "kills" = fail>=1 after X09/P1 added to the same file.
- s1 `witness is not True`->`is False`: 64/64 SURVIVOR | X09 killed, P1 killed | LOW  ||  s2 drop `len(row_fate)==len(wrows)`: 64/64 SURVIVOR | kills both | LOW
- s3 setup-only rows FM1->FM2: 64/64 SURVIVOR | kills both | LOW  ||  s4 off-path->`tools/counter.py`: 64/64 SURVIVOR = EQUIVALENT (FM1's forge path is tools/notes.txt)
- s4b off-path->`tools/notes.txt`: 63/64 KILLED (the probe path is load-bearing)  ||  s5 restore `tree_divergence` before evaluate: 63/64 KILLED
- s6 drop `sc["new_unwitnessed"]==1`: 64/64 SURVIVOR | kills both | LOW  ||  s7 drop `row_fate[0]["witness"] is False`: 64/64 SURVIVOR | kills both | LOW
- s8 drop `and not unw`: 64/64 SURVIVOR | X09 killed, P1 SURVIVES (64/64) | MEDIUM  ||  s6+s7 pair (2 edits): 64/64 and X09 SURVIVES (64/64)
F2 MEDIUM: the P1 kill rests on the one term `and not unw` (s8 holds 64/64 and P1 survives: under P1 no other
check fails once X15 weakens (9a)) — the round's "second, independent detector" is the only detector for P1.
F3 LOW: the X09 kill needs s6 and s7 together; either alone is dispensable, so a one-term deletion reads clean.
F4 LOW (not mine): `tools/souji-pre-report-gate.sh` is dirty in the worktree (wave-repair patch, 9+/1-); the C1
domain trial must bind `git show <rev>:…`, never the worktree file.
Files: .ufo/waves/round-75/w1/S75MutCounter.md, .ufo/waves/round-75/w1/S75MutCounter/evidence.txt (run lines,
mutant sha256s, forged receipts, battery diffs). No install, no lane file edited, scratch removed.
