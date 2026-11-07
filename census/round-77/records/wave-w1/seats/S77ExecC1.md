# S77ExecC1 — C1 reproduction (round 77)

Commands: from /home/vgpnk/Projects/shokunin/souji-shokunin,
`python3 -B census/round-77/c1-nonreg-counter.py --gate-dir <D> --work <W>` with D holding
gate+writer from `git show <rev>:tools/...` (W gate rev 9b496b08, base rev d4f51563,
K-b/K-c/K-d variants copied from census/round-77/controls/variants/ beside base writer);
`python3 -B census/round-76/c1-evade-counter.py --gate-dir <W-dir> --work <dir>`;
`python3 -B tests/fixtures/r36-report-gate.py --work <dir> --gate <W gate>`;
`bash tests/fixtures/r27-pre-report-gate.sh`; lane timing run of
`tools/souji-pre-report-gate.sh --lane ... --branch master --report .../preregistration.txt --prereg .../preregistration.txt`.

## Verdicts (all REPRODUCED)
- C1 W gate: `SUMMARY rows=16 mismatches=0 errors=0 hangs=0`, `EXIT=0`; ROW lines identical
  to census/round-77/records/c1-after.txt (secs normalized). REPRODUCED.
- C1 base gate: `SUMMARY rows=16 mismatches=9 errors=0 hangs=8`, `BASE-EXIT=1`; ROW lines
  identical to controls/c1-K-a-do-nothing.txt. REPRODUCED.
- K-b refuse-all: `SUMMARY rows=16 mismatches=7 errors=0 hangs=0`, `EXIT=1`; ROW lines
  identical to controls/c1-K-b-refuse-all.txt; variant sha256
  e9db75803b5b46aa20c5e5ba98c6379eebed0a1d000da2b67a955c4edd84c4d8 matches receipt `# gate`
  line. REPRODUCED.
- K-c M09 one-path: `SUMMARY rows=16 mismatches=11 errors=0 hangs=8`, `EXIT=1`; ROW lines
  identical to controls/c1-K-c-m09-one-path.txt; variant sha256
  b1eab89f88653ce1ee2b41b4218c5718585707e931725db20d02bce9ddcce570 matches. REPRODUCED.
- K-d blanket: `SUMMARY rows=16 mismatches=7 errors=0 hangs=4`, `EXIT=1`; ROW lines
  identical to controls/c1-K-d-blanket-nonregular.txt; variant sha256
  d90ef98820b42a47a75948bf8602524cfc7d170ebff0e4f6788eb296742e3428 matches. REPRODUCED.
- Regressions (W gate): r76 `SUMMARY rows=30 mismatches=0 errors=0` EXIT=0; r36
  `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` EXIT=0; r27 `cases=4 pass=4
  control=FALSE-GREEN-REJECTED` EXIT=0. All REPRODUCED.
- Gate blob digests: W 28a5135573091a253c69809c4134a3a031da014f7e1bccea5860975d127616be,
  base 90bdd8c74e38c525f2ef75b7c22fb95667035515f44724fbd3a2b1addfcc47f3 (matches prereg K-a).
- Orphans: `ps -eo pid,args | grep /fast/scratch/hyaku/souji-r77/S77ExecC1` → none after
  every base-gate run (K-c, K-d, final). `ORPHANS=none`.
- Timing (lane, read-only): WALL=0.47s, rc=1; check-tip=PASS, check-report=PASS,
  check-shonen=FAIL (`detail-shonen: found 0 headings, expected 1`), check-clean=FAIL
  (modified SKILL.md corpus/QUALITY.md corpus/README.md corpus/SOURCES.md
  corpus/knowledge/filter-filemode-witness.md; untracked census/round-77 artifacts) —
  reflects the lane's current dirty state, not a gate hang; check-prereg=PASS. The
  prereg's domain-trial conjunct (check-clean=PASS on the lane) is therefore NOT
  reproduced in the current lane state; L1 owns the tip-state trial. No HIGH finding.

## Files written
.ufo/waves/round-77/w1/S77ExecC1.md; receipts copied to
.ufo/waves/round-77/w1/S77ExecC1/{c1W.out,c1Base.out,kb.out,kc.out,kd.out,r76.out,r36.out,r27.out,timing.out,variant-sha.txt}.
