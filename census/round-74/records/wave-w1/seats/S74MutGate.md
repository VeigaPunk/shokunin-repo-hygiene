# S74MutGate — mutation test: stage-W gate check 4 (tools/souji-pre-report-gate.sh:35-57 @ ec13ba7f) vs the frozen r74 C1 gate counter

Verdict: C1(i) count REPRODUCED (mismatches=0 EXIT=0 from committed bytes); 15 single-edit mutants -> 11 KILLED, 4 SURVIVED. C1 is not falsified on its measured rows, but its declared fail-closed conjunct is unmeasured (F1). Nothing committed; no lane byte touched.

Binding: counter sha256=ac28f7d1… == records/c1-after.txt:5; gate copy sha256=3162de98… == `git show ec13ba7f:…gate.sh` == tip bytes (`git diff --stat ec13ba7f HEAD -- tools/` empty); writer 70bbf1c2… == tip tools/souji-receipt-write.py.

Commands (lane root; S=/fast/scratch/hyaku/souji-r74/S74MutGate; each mut dir = gate.sh + souji-receipt-write.py):
  python3 -B census/round-74/c1-gate-counter.py --gate $S/m/<id>/gate.sh --work $S/w/<id>
  python3 -B census/round-74/c1-gate-counter.py --gate $S/m/<id>/gate.sh --work $S/w/<id> --rows GH1,GF1   (D01/D02 only)
Baseline/controls re-derived: B00 pristine -> `SUMMARY rows=9 mismatches=0 errors=0` / `EXIT=0`; lane-base 43cd74bb gate -> `mismatches=3` (GF1 GF2 GF3) `EXIT=1` (== controls/c1-K-a-do-nothing.txt:1-2); K-b -> `mismatches=4` (GH1-4) `EXIT=1`; K-c -> `mismatches=1` (GF2) `EXIT=1` (both == committed controls).

Mutant table (full: .ufo/waves/round-74/w1/S74MutGate/mutants.tsv):
  KILLED (11): G01 drop truth call 3/GF1-3 · G02 heredoc rc ignored 3/GF1-3 · G03 `if msg:`->`if not msg:` 7 · G04 writer from `$lane/tools/` 4/GH1-4 · G08 `-n`->`-z` status 6 · G09 truth-FAIL prints but PASS 3/GF1-3 · G10 `gate_dir=.` 4/GH1-4 · G11 empty heredoc 3/GF1-3 · W01 skip symlinks 1/GF2 · W02 trust size==index object size 1/GF1 · W04 writer `!=`->`==` 4/GH1-4.
  SURVIVED (mismatches=0 EXIT=0): G05 `$PWD/tools/` writer · G06 try/except BaseException->exit 0 · G07 first-line status test · W03 missing path -> clean.

Findings
MEDIUM F1 (G06, fail-open unmeasured): gate:40-41 declares "A missing writer, a failed read or any mismatch fails `clean`". Writer removed beside gate, rows GH1,GF1: pristine -> `ROW GF1 expect=FAIL clean=FAIL rc=1` (D02); G06 -> `ROW GF1 expect=FAIL clean=PASS rc=0` — the stat-cache forgery is ACCEPTED (D01). The frozen harness always plants a readable writer beside every gate, so 9/9 green cannot observe this branch.
LOW F2 (binding): c1-gate-counter.py:214 prints only the gate sha256; the writer it exercised is never hashed there (W03 header shows gate 3162de98… while the writer was ed47dd02…). records/c1-after.txt:5's writer bind is run-receipt's, not the counter's observation.
LOW F3 (G05): cwd is fixed at the lane root and the counter prints no writer path, so a gate resolving the writer from `$PWD/tools/` instead of "beside this gate" (gate:39-40) is indistinguishable; it passes 9/9 on the lane's identical bytes.
LOW F4 (W03): no row reaches _truth_refusal's `not os.path.lexists` branch (writer:286-288); a vanished tracked path is listed by `git status` and skipped at writer:283, so the branch is unobservable — unverified defence-in-depth.
Not a finding: G07 is behaviourally equivalent (first status line non-empty iff status non-empty).

Files written: .ufo/waves/round-74/w1/S74MutGate.md · .ufo/waves/round-74/w1/S74MutGate/mutants.tsv · …/S74MutGate/logs/*.txt (21 counter outputs) · …/S74MutGate/builder.py · …/S74MutGate/run.sh. Tools installed: none. Scratch removed.
