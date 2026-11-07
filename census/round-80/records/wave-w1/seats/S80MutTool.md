# S80MutTool — mutation test of the W2 front/worker (tools/souji-quarantine.sh @836dac3) vs the frozen C2 counter
Verdict: 12 single-change mutants; the counter kills 9 (ratio 0.75); survivors M01, M02, M09. Pristine and restored
bytes both print `SUMMARY rows=15 mismatches=0 errors=0 orphans=0` rc=0; hashes-before == hashes-after (restoration
exact). Base tool sha256=67ec160b97b4…, counter sha256=32cf0c72… (== census/round-80/records/c2-after.txt:12,
census/round-80/preregistration.txt:67).
Ran from the lane root, one counter at a time, each in its own session:
  setsid -w timeout -k 5 600 python3 -B census/round-80/c2-signal-counter.py --tool-dir <mutant dir> --work <fresh>
  bash tests/fixtures/r13-quarantine-bounds.sh --tool <mutant>; env TMPDIR=<scratch> bash <mutant> --selftest
mutant (one change) | verdict | deciding output
M01 no SIGSTOP pass | SURVIVED | 0/0/0 rc=0; fork-bomb row probe survivors=0
M02 single kill pass | SURVIVED | 0/0/0 rc=0; fork-bomb row probe survivors=0
M03 q_kill_session never called (pid kill only) | killed | q1 rc=143 survivors=3 match=no; mismatches=12 orphans=12 (== K-c receipt)
M04 kill -- -worker (worker pgrp) | killed | q1 rc=143 survivors=2; mismatches=12 orphans=12
M05 exit 1 instead of 128+n | killed | q1 rc=1 signal_line=y; mismatches=12
M06 no SIGNAL line | killed | q1 rc=143 signal_line=n; mismatches=12
M07 SIGNAL wrong class | killed | q1 signal_line=n; mismatches=12
M08 trap TERM only | killed | q2 rc=-2 signal_line=n survivors=4; mismatches=8 orphans=8 (INT/HUP rows only)
M09 no rm -rf in handler | SURVIVED | 0/0/0 rc=0; probe: private dir present during, empty after (EXIT trap removes it)
M10 no setsid | killed | q1-q12 match=error "hang point never reached"; p1-p3 mismatches (rc=2); mismatches=3 errors=12
M11 wait -> foreground run | killed | q1 exited=n rc=None survivors=5 tmpleft=2; mismatches=12 orphans=12
M12 q_proc_sid field 5 (pgrp) | killed | q1 survivors=2; mismatches=12 orphans=12; selftest 81/47
No-signal-path regressions (M10/M11/M12 only): M10 r13 `SUMMARY total=5 failed=5`, selftest rc=2 "worker is not a
session leader (pid …); refusing"; M11 r13 5/5 pass, selftest 81 checks 47 failed; M12 r13 5/5 pass, selftest 81/47.
Survivors — proposed rows (lane files untouched):
 q13-term-file-digest-forkbomb: sha256sum shim (exact last arg = target) marks, then `( while :; do sleep 600 & done ) &`
 then `exec sleep 600`; expect SIGNALED/143, survivors=0. MEASURED (probe-q13.py) on pristine/M01/M02: survivors=0 all
 three -> the row does NOT kill M01/M02. They are equivalent under the frozen predicate: SIGSTOP and the 7 extra passes
 only narrow a sub-ms fork tail race (a child's pid sorts after its parent in `/proc/[0-9]*`), so no static hang-point
 row distinguishes them; one that did would be racy, not a verdict.
 M09: no row can kill it — the handler `rm -rf` is redundant with `trap 'rm -rf -- "$q_front_tmp"' EXIT` (probe-m09:
 during=['souji-quarantine.…'] after=[] for pristine and M09 alike).
Findings: LOW — the population measures "kills every process it started" only for static hang points; the STOP pass and
 the repeat passes are unmeasured (M01/M02). LOW — tools/souji-quarantine.sh:229 is dead weight (the EXIT trap already
 removes the dir). LOW — r13 stays green for M11 (front blocked in a foreground wait), so only C2 covers wait/trap.
Files: .ufo/waves/round-80/w1/S80MutTool.md; S80MutTool/{probe-q13.py,probe-m09.py}; mutants/{BASE-67ec160b,M01…M12}.sh;
 diffs/<M01…M12>.diff; logs/{pristine,M01…M12,restored}.{out,err}, logs/{M10,M11,M12}.{r13,selftest}.out,
 logs/{probe-q13,probe-m09}.out, logs/{sweep,regress}.tsv, logs/hashes-{before,after}.txt.
