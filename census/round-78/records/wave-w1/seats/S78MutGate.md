# S78MutGate — C1 gate mutant kill power (souji r78, w1)

VERDICT: the frozen 17-row C1 counter kills 13 of 15 mutants of the W gate's r78 block; 2 SURVIVE — m13 (HIGH: the row set has no duration predicate) and m14 (LOW: no /etc route). Every refusal route except the one the prereg itself names is genuinely covered.

Bindings re-derived from committed bytes: gate `ed22dc9cb7a6b61a7d0bd150db4a95191b1333aa:tools/souji-pre-report-gate.sh` sha256=b746bd9d…, writer 70bbf1c2…, counter e53dd0ca…, c1-population.tsv 0d3c66ff…, probe 09e18d8a… — equal to records/c1-after.txt:2-9. Pristine baseline, frozen invocation (`SUMMARY rows=17 mismatches=0 errors=0 hangs=0` counter_exit=0) = detector sound. Per-mutant command: `cd LANE && python3 -B census/round-78/c1-gitsrc-counter.py --gate-dir <mutant+W writer> --work <dir>` (15 mutants + baseline, each its own `--work`; every kill/survival re-run alone).

| mutant (seat dir; sha256 in mutants.tsv) | batch SUMMARY | verdict / killed by |
|---|---|---|
| m01 drop $HOME/.gitconfig scan | 1/0 | killed: g9 HANG 75.1s |
| m02 drop XDG git/config scan | 1/0 | killed: g10 HANG 75.1s |
| m03 no include recursion | 3/1 | killed: g5,g6,g7 |
| m04 relative include unresolved | 1/0 | killed: g7 HANG 75.1s |
| m05 drop commondir | 1/0 | killed: g4 HANG 75.1s |
| m06 drop packed-refs | 1/0 | killed: g3 HANG 75.1s |
| m07 `-f` -> `-e` | 3/1 | killed: g2,g3,g4 |
| m08 check-4 gitsrc skip removed | 10/8 | killed: g1,g3,g4,g5,g6,g7,g8,g9,g10,g11 |
| m09 ls-remote timeout removed | 1/0 | killed: t1 HANG 75.1s |
| m10 timeout 45 -> 300 | 1/0 | killed: t1 HANG 75.1s |
| m11 RECEIPT-GIT-TIMEOUT message removed | 1/0 | killed: t1 FAIL rc=1 class=- secs=45.1 |
| m12 refuse only when gitsrc_n>1 | 11/9 | killed: g1..g11 |
| m13 scan without GIT_CONFIG_GLOBAL=/dev/null | alone 0/0 exit=0 | SURVIVED |
| m14 drop /etc/gitconfig scan | alone 0/0 exit=0 | SURVIVED |
| m15 drop config.worktree scan | 1/0 | killed: g8 HANG 75.1s |

Deciding lines: baseline 17x `match=yes`; every kill row `match=no`. The ODD rc=-9 rows of the 16-wide batch (gate SIGKILLed at 15-60 s) are contention noise, not the gate — `timeout -k 5 10` around a FIFO-blocked git in a session/group-LEADER script returns rc=124 with the caller alive (evidence/pg5.log) — and all 8 such rows re-run alone read `HANG 75.1s match=no` (evidence/rerun-*.log).

SURVIVOR m13 (`m13-no-gitconfig-isolation.sh`, drops the inline `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` at gate:55): 17/17 exit 0 alone while g9, g10, t1 each burn secs=45.0 vs 0.0 pristine — it re-introduces the exact draft defect preregistration.txt:9-10 says was found and kept out. HIGH: `run_gate` accepts on `verdict==expect and class in text` only, so a 0 s refusal replaced by a 45 s timeout still passes; mechanism confirmed — `git config --file X` does open the global config (evidence/gitconfig-file-global-probe.txt, rc=124 at the bound). Proposed row/assertion: add `secs < 5` to `ok` for the 11 g-rows (all 0.0 on pristine), or a g12 row on g10's fixture that must refuse in <5 s; the same predicate closes the MEDIUM residual m07 leaves — 8 of its rows still read `match=yes` at secs=45.0 (a 45 s stall per source in place of a refusal).

SURVIVOR m14 (`m14-drop-etc-gitconfig.sh`): no row can put a FIFO at /etc/gitconfig (needs root) and the gate unsets GIT_CONFIG_SYSTEM/NOSYSTEM (gate:4), so a caller cannot redirect it — LOW, real gap. Proposed row: static scan-list parity — assert `gitsrc_one "/etc/gitconfig" 0` and the other ten frozen source kinds remain present, since /etc is unwritable in the harness.

MEDIUM (detector, found in cleanup): the counter's HANG path `os.killpg(p.pid)` kills the gate's group only, and `timeout` puts the blocked git in its own pgroup (pgid = the timeout pid), so a HANG row leaks the blocked git for as long as its own bound allows and forever when that bound was the mutated-away one (m09) — evidence/leaked-after-hang-rows.txt; I killed those PIDs.

Files under the seat dir: m01..m15-*.sh, mutants.tsv, evidence/{results.tsv, rerun-*.log, solo-*.log, pg5.log, gitconfig-file-global-probe.txt, leaked-after-hang-rows.txt}. No lane/tracked file touched; no tool installed.
