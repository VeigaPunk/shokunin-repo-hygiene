# S82Reviewer — r82 falsification review (round 82, wave w1)

## Chronology: PASS (one disclosed defect M1, no new defect)
Order verified by parents: 488956c4→1cb7c7d1(P)→d302b4f3(F)→28fd32c0(F2)→1ec433c6(F3)→
51a5e7fa→f5bc4197(W1)→73110f6f(W2)→9881676a(A). Commits f5bc4197/73110f6f/9881676a are linear descendants.
- Frozen instruments: `git rev-parse` F vs W2 identical for c1 harness, c1 TSV, c2 counter, c2
  population, all 6 control receipts + 4 variants. Only new files F→W2: W1 counter, W2 tool, freeze-check
  receipt, lesson M1/M2, prereg edits.
- Prereg bytes: P=ebfdf65a (freeze line absent), F=3f4cc670 (freeze line +2), F2=revert to P
  bytes, F3=b939f989 (Control: parenthetical "(recorded under `env SHELLOPTS=monitor`…)"
  removed, 1 line). F→W2 prereg diff = only that 1-line fix + removal of trailing Freeze line
  (which F2 already removed). No predicate text changes. Prereg digests stable F3→A.

## Freeze-check: PASS as a falsification report
- Committed `records/freeze-check-at-P.txt`: rev=1ec433c6, `SUMMARY claims=2 findings=3`, EXIT=1.
- **Rerun** (same command, `--rev 9881676a` and `--rev 1ec433c6`):
  byte-identical 3 findings. F0 frozen-edit = the F3 1-line prereg fix (freeze tool's
  `freeze_rev()` returns first prereg-add commit = P, so F3 edit vs F divisons is C0
  FROZEN-EDITED). C1/C2 = P landed control bytes with same commit as prereg, so no strict-ancestor
  copy exists. **M1 is genuine, disclosed, not manufactured.** `substance`/`chronology` modes
  (the assigned reruns) both fire; mode-adjacent flags do not hide it. Freeze digest unchanged
  (d2a9b590… → b939f989 blob; instrument sha d2a9b590 cited at P; no tool edit after F3).

## C1 predicate (W1, f5bc4197): HONOURED
- Target counter `census/round-82/c1-pointer-counter.py` is byte-identical to the P-time draft in
  `prefreeze/c1-candidate-draft.txt` (same sha256 cbfdc07c…). Mechanism: `_owntree_ok` /
  `_capture_ok` (CAPTURE=`waves/|wave/|records/wave-<w>/` + whole suffix ≤ len(have)) added; own-tree
  branch runs **after** basename check, not before — prereg text "runs BEFORE the basename test"
  is overstated. Order is basename-first, then owntree, then capture. **LOW**: wording vs code
  mismatch, predicates still hold on every row.
- `records/c1-after.txt` (rev=73110f6f, harness a45a9022…): 32 rows, all match=yes; NF-F/NF-G/NF-H/
  NF-I refused; TF3/TF4/TF5 and PF-1 kept MOVED, exactly as predicates require. `SUMMARY rows=32
  mismatches=0 accepted=0 refused_true=0 errors=0`, EXIT=0. C1 K-a (r81 counter): NF-F/NF-G
  accepted=2, mismatches=2, EXIT=1 — matches prereg. Regressions in A receipts: r78 items=22,
  forged=12 matched=12 accepted=0; r77 items=35, forged=7; r79 9 rows; r80 18; r81 25/25 — all
  zero mismatches (per receipts; `diff` W1-vs-r81 confirms only the two new branches).
- K-b docstring says "red by accepted=3" but receipt is accepted=2/[NF-F,NF-G] — docstring-level
  imprecision (PF-1 is MOVED in K-b too, not refused, so accepted set is 2 not 3). **LOW.**
  K-c receipt exactly matches prereg: [NF12c, NF-I] accepted=2, mismatches=2, EXIT=1. K-b/K-c
  receipts: mismatches=2/receipt row sets identical to prereg.

## C2 predicate (W2, 73110f6f): HONOURED
- W2 diff is exactly `cli_kill_tree` + `$!` drop (`local pid=${CLI_PID:-}` vs `${CLI_PID:-${!:-}}`).
  Code review (`set -euo pipefail`):
  - pgrep absent → `kids=$(pgrep …) || kids=""` ⇒ stack=[pid], tree=[pid]; TERM/KILL to pid then
    group kill — degrades to base behaviour, no crash. **No crash path found.**
  - pgrep failing (rc≠0) similarly empties children.  `2>/dev/null` present.
  - pid exits during snapshot: all kills `|| true`; `kill -0` loop polls group/pid; stale pids
    only get harmless signals. No `-e` escape: both `|| true`.
  - empty-stack / arithmetic: `kids` unquoted-for split is safe (pids are digits); `${stack[@]:0…}`
    arithmetic works under `-u` (array initialized). No `set -u` unbound-variable path.
  - **CLI_PID window**: trap armed at line 287, `timeout … &` then `CLI_PID=$!`; a signal between
    `trap` and `CLI_PID=$!` runs `cli_on_signal` with empty pid ⇒ skips kills but still exits
    128+n and deletes `$CLI_OUT` — correct cleanup, CLI may briefly outlive (not a row; window
    ≪ 5 s settle).
  - trap reset: `trap - TERM INT HUP` after wait; cli_on_signal traps '' first (no re-entry).
  - foreground fallback (`cli_tmp_ok` false → `$(timeout …)`): unchanged, no traps armed.
  - `cli_tmp_ok` interplay: W2 does not change `cli_tmp_ok` or the foreground gate; signal
    behaviour in the refused configuration unchanged (stated limit, admitted).
- `records/c2-after.txt` + `records/c2-after-monitor.txt` (tool sha256 556ad94a…, both launches):
  16 rows, all match=yes, survivors=0 throughout, `SUMMARY rows=16 mismatches=0 errors=0 orphans=0`,
  EXIT=0 under both. v9/v10+TERM-ignoring CLI: KILL fallback after 2 s ends them (already in receipts).
- Controls: K-a (Base tool, monitor) mismatches=4 orphans=4 (v7/v8/m1/m2 survivors=1) — exactly the
  prereg text; K-b traps-only ≥8 is observed 12/12; K-c = 1 mismatch p3 cli=empty as bound.
  Regression: selftest 57/0 (committed file, TMPDIR=<scratch>), r17 37/0/0, probe D successor 6/6
  (two new arms present). `census-after` ok, EXIT=0; `registry-agreement-at-W2` k1=1 k2=1 EXIT=1
  (carried accepted-red, as stated — not a regression).
- **Selftest gap (LOW, by-design)**: no selftest step fires `cli_kill_tree` directly; the
  `selftest: 57 checks, 0 failed` line is the pre-existing suite, unverified against monitor
  job-control. All monitor evidence comes solely from the C2 counter receipts.

## Findings
- LOW (wording/code): prereg says "_owntree_ok runs BEFORE the basename test"; code runs basename
  (line 349) before `_owntree_ok` (line 353). Conjuncts unaffected. `c1-pointer-counter.py:340-353`.
- LOW (docstring): C1 K-b variant header claims "accepted=3"; receipt is accepted=2 / 2 mismatches.
  `controls/variants/c1-K-b-owntree-dropped.py:2`.
- LOW (prereg trailing): F3 removes freeze-line "(Recorded under … monitor)" note from C2
  Control line; disclosed M1 covers the chronology element of this edit. Not a new freeze defect:
  F3 rectifies the FROZEN-EDITED cause partially, but does not retract chronology M1, which stands.
- No HIGH or MEDIUM findings. No new frozen-file drift, no hidden commit mutation.

## Commands run
git log/show/diff/stat (P–A chain); sha256sum (4 frozen instruments + 2 candidates);
freeze-check reruns at 9881676a and 1ec433c6 `--substance --chronology` (byte-identical 3 findings);
receipt summary/row greps (c1-after, c2-after, c2-after-monitor, c1/c2 regress, controls, probe D,
census-after, registry); W1-vs-r81 diff; K-variant diffs; TSV row extraction; bash `--version` +
pgrep probe (`pgrep 0.2.0`, `bash 5.3.20`); disk-guard (rc=0). No heavy counter reruns (peers own
C1/C2 reruns); `ps` at yield: only siblings' jobs, nothing under my scratch.

## Verdict
Chronology/ freeze-check / C1 / C2 predicates are all HONOURED as frozen. 0 HIGH, 0 MEDIUM, 3 LOW.
M1 is confirmed by rerun; round's C1/C2 claims hold on the committed receipts.

Files written: (1) /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-82/w1/S82Reviewer.md
(this report). No other files created under the lane; scratch dir empty-removed.
