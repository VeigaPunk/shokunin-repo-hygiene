# S79MutGate — W1 gate signal-path mutation test (C1), souji r79 w1

VERDICT: 12 one-change mutants of tools/souji-pre-report-gate.sh at W1 c8c3fbca (base sha256 ae5022c5…; per-mutant
sha256 in MANIFEST.tsv). Frozen C1 counter kills 7/12 (58.3%); the proposed rows kill 4 of the 5 survivors; M04 is
equivalent. Baseline green: SUMMARY rows=11 mismatches=0 errors=0 orphans=0, EXIT=0. Commands (lane root,
S=/fast/scratch/hyaku/souji-r79/S79MutGate): python3 -B census/round-79/c1-signal-counter.py --gate-dir $S/base/g
--work $S/work/base-fg; per mutant env --default-signal=INT python3 -B <same> --gate-dir $S/mutants/<id>/g --work
$S/work/<id>; r78 python3 -B census/round-78/c1-gitsrc-counter.py --gate-dir <g> --work <w>; r36 python3 -B
tests/fixtures/r36-report-gate.py --work <w> --gate <g>/souji-pre-report-gate.sh
mutant | change (gate line) | C1 counter | killed by | r78 | r36
M01 | drop group kill (49) | 0/11 | SURVIVED | - | -
M02 | drop pid kill (50) | 0/11 | SURVIVED | - | -
M03 | exit 128 fixed (55) | 10 mism | s1-s10 | - | -
M04 | no gate_cleanup in handler (52) | 0/11 | SURVIVED-equivalent | 17/17 | 21/21
M05 | trap only TERM (58-59) | 2 mism (s4 rc=-2, s8 rc=-1) | s4,s8 | - | -
M06 | gate_child never set (69) | 7 mism + 4 err | s1-s5,s10,p1; s6-s9 err | 9 mism | 17/21
M07 | check-signal=PASS (53) | 10 mism | s1-s10 | - | -
M08 | find in foreground (247) | 1 mism (s6) | s6 | 17/17 | 21/21
M09 | no <&0 (66-67) | 0/11 | SURVIVED | 17/17 | 21/21
M10 | no newline strip (80) | 1 mism (p1) + 3 err | p1; s7-s9 err | 5 mism | 17/21
M11 | no trap '' guard (47) | 0/11 | SURVIVED | - | -
M12 | no EXIT trap (60) | 1 mism (p1, tmpleft=2) | p1 | 17/17 | 21/21
Proposed rows, verified (probes/rows-ABCD.txt, rowE.txt, repro-base.txt): A grandchild blocker (shim `sleep 600 &
wait`): base survivors=0, M01 1. B `timeout` on PATH without setpgid: base 0, M02 1. C untracked file hidden by
.git/info/exclude: base rc=1 check-clean=FAIL RECEIPT-UNTRACKED-LOCAL-EXCLUDE, M09 rc=0 check-clean=PASS (a real
forgery). D TERM/HUP burst (40 signals, 0.5 ms): base rc=143 10/10, M11 rc=129 8/10 (5/5 idle, 3/5 loaded).
M04: no row can kill it — the EXIT trap (60) already runs gate_cleanup; the handler's call is redundant.
Findings: HIGH: M09 survives C1 11/11, r78 17/17, r36 21/21 and makes check 4's byte-truth block vacuous (without `<&0` the
heredoc python reads /dev/null and exits 0); row C shows the gate PASSes a lane hiding an untracked file, so the
claim's "no signal -> verdicts unchanged" conjunct is not covered by p1 or the regressions.
MEDIUM: M01 survives because every frozen row's blocker is timeout's DIRECT child and coreutils timeout sets
PR_SET_PDEATHSIG (srcs/coreutils-timeout.c-v9.12:608-610), so the pid kill alone suffices; the group kill's real
target (a child that forks, e.g. git -> upload-pack) is untested. M02 survives: no frozen row distinguishes it.
LOW: M11's guard is unobservable under one signal; only the mixed TERM/HUP burst shows it.
LOW: s3/s4 block at check 0's `git config --file <rowdir>/clone/.git/config` (probes/argv-s3.txt: FIRST-MATCH
index=1), not at ls-remote; 25/25 git calls match because the rowdir name carries the pattern.
CONFIRMED (R2): `set +m` + `&` reproduces mismatches=1, s4 only, survivors=3, tmpleft=2; foreground 11/11.
Files: .ufo/waves/round-79/w1/S79MutGate.md + S79MutGate/{MANIFEST.tsv,mutants.diff,mutants/*.sh,build_mutants.py,probes_rows.py,
c1/*.txt,regress/*.txt,probes/*.txt}. Restoration: base gate sha256 == W1 blob == lane HEAD blob; no lane file
written (git status shows only a sibling's corpus/knowledge/gate-signal-handling.md). No installs; scratch removed.
