# S79ExecC2 — C2 reproduction (souji r79)
Lane tip 2827fbe51274c93d35350e7c10fa25166892d84f; W2 17009fa1f9d335a1bdde1e22ff3894c5d571c250.
VERDICT: C2 REPRODUCES. No HIGH findings. Two LOW findings (pointer-check misses; instrument notes).

Bytes: r79 counter sha256 f597909b…ed703 = W2 blob = tip blob. Harness 5d5bd236…eeb1a290adeea and population 7c108820…6afdb match bind lines. Variant sha256 match bind lines (K-b 192beb…, moved bfc673…, nextline 41ca01…, quarantine 464210…, range a45894…).

Receipts reproduced (body compared, minus #/command/rev/instrument/EXIT lines):
1. controls/c2-K-a-r78-counter.txt: YES. SUMMARY rows=9 mismatches=5 accepted=5, rc=1.
2. records/c2-after.txt (r79 @W2): YES. SUMMARY rows=9 mismatches=0 accepted=0, rc=0.
3. Fixture rev 6436db6a…: YES, identical in all 7 harness runs.
4. controls/c2-K-b-refuse-all.txt: YES body, 9/9 (exit not re-verified).
5. c2-K-c-without-{moved,nextline,quarantine,range}.txt: YES body. Mismatch/accepted = 1/1, 1/1, 1/1, 2/2; none at 0. Direct rc moved=1.
6. controls/c2-K-b-refuse-all-regress-r78.txt: YES at W2 and tip. resolved=3/22, FORGE 12/12 accepted=0, rc=1.
7. records/c2-regress-r78.txt (r79 @W2): YES. resolved 22/22, FORGE 12/12 accepted=0, rc=0.
8. records/c2-regress-r77.txt (r79 @W2): YES. resolved 35/35, FORGE 7/7 accepted=0, rc=0.
9. Same regressions at tip 2827fbe, both counters: identical counts. YES.

ITEM-line diff, r78 vs r79 counter at tip: r78 set 22 vs 22 lines IDENTICAL; r77 set 35 vs 35 IDENTICAL. Zero ledger verdicts change.

Pointer check (tools/souji-pointer-check.py, LOG/SCORECARD/SKILL/QUALITY/README):
- base e65538e7: checked=2837 missing=46 rc=1. W2 17009fa1: checked=2837 missing=46 rc=1.
- tip 2827fbe5: checked=2880 missing=48 skipped=219 rc=1 (LOG 20, SCORECARD 9, SKILL 7, QUALITY 8, README 4).
- The two tip-only misses are round-79: LOG.md:3047 census/round-79/records/c1-domain-trial.txt (absent, pending) and SCORECARD.md:287 census/round-79/records/foreground/c1-at-W1-fg-run1..3.txt (shorthand; run1/2/3.txt exist).
- Ledger effect: no ITEM status changes, so no r77/r78 verdict moves. Mapping is aggregate: ITEM lines carry no path.

Findings:
- LOW: tip pointer check exits 1 (48 MISSING; base 46); both new misses are round-79 pointers. Not a C2 verdict change.
- LOW: LOG.md:27 is ITEM L01 (status=FLEET); its cited path is MISSING to the lane pointer check. Not reconciled (fleet root not checked).
- LOW (my instrument): `setsid … &` returned before harness completion and my variant-batch rc values were invalid. Re-ran with `setsid -w` and direct `$?`: a=1 (r78), b=0 (r79), m=1 (K-c moved).
- Observation: uncommitted change in corpus/knowledge/gate-signal-handling.md; not in the C2 population.

Commands (lane root; scratch /fast/scratch/hyaku/souji-r79/S79ExecC2, removed):
  python3 -B census/round-79/c2-false-row-harness.py --counter <ctr> --lane <lane> --fleet-root /home/vgpnk/Projects/shokunin --work <scratch>
  python3 -B census/round-79/c2-pointer-counter.py --root <lane> --rev <rev> --fleet-root … --population census/round-7{7,8}/c2-population.tsv --ledger census/round-7{7,8}/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r7{8,7}.tsv
  python3 -B tools/souji-pointer-check.py --root <lane> --rev <rev> LOG.md SCORECARD.md SKILL.md corpus/QUALITY.md corpus/README.md

Files written: .ufo/waves/round-79/w1/S79ExecC2.md; .ufo/waves/round-79/w1/S79ExecC2/receipts/ (20 .out/.txt receipts). Tools installed: none. No processes left by this seat.
