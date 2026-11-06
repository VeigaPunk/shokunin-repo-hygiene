# S73ExecC2 — r73 C2: reproduce from committed bytes + attack the defang set

Verdict: C2 REPRODUCED (10/10 receipts, probe 15/15, selftest 52/52); 2 undeclared witness blind spots (MEDIUM).

## 1. D1..D5 after-arms (r73 counter, committed sha 3809ee7d)
cmd: `python3 -B census/round-73/apply-edit.py --set census/round-73/c2-defang.json --id Dk --src census/round-73/c1-counter.py --out <S>/after/counter-Dk.py`, then `python3 -B <S>/after/counter-Dk.py --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1… --rev a789486d… --tool tools/souji-receipt-write.py --work <S>/after/wk` (cwd = lane root; <S> = my scratch)
observed, k=1..5 all identical: `SUMMARY matrix=80 base_forgeries=15 base_honest=21 base_mismatches=0 base_unwitnessed=1 new_unwitnessed=0 new_forgeries=3 new_honest=21 class_mismatches=3 new_echo=0 errors=0 regress=PASS` / `EXIT=1`
edited rows D1 FWr, D2 FWi, D3 FWp, D4 FWs, D5 FC3: each `base_witness=no new_witness=no`
body diff vs records/c2-after-D*.txt: identical on every counter line (only the receipt runner's appended duplicate EXIT differs); APPLIED out_sha256 match receipts (e36f4bdf, 27f2ce03, 94f41aea, e3e55100, ddec2096)
=> REPRODUCED

## 2. Before-controls (r72 counter, committed sha 7578447d)
cmd: same, `--src census/round-72/c1-counter.py`, `--matrix census/round-72/c1-matrix.tsv`
observed, k=1..5: `SUMMARY matrix=75 base_forgeries=12 base_honest=19 base_mismatches=0 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0`; body identical to controls/c2-before-r72-D*.txt
`grep -c 'base_witness\|tree_divergence' census/round-72/c1-counter.py` = 0
=> REPRODUCED (0 of 5 detected)

## 3. Probe, selftest, positive control
probe: `witness-probe.py --counter census/round-73/c1-counter.py --matrix census/round-73/c1-matrix.tsv --slot <8b9345b1:tools/souji-receipt-write.py, sha 118597e0…> --work <S>/probe` -> `SUMMARY refuse_rows_accepted=15 witnessed=15 unwitnessed=0` => REPRODUCED
selftest: `c1-counter.py --selftest --root . --matrix … --base-rev 8b9345b1… --work <S>/st` -> `SELFTEST cases=52 pass=52 fail=0` / `EXIT=0` => REPRODUCED
positive control (unmutated counter, lane-base writer): `base_unwitnessed=0 … base_forgeries=15` => REPRODUCED (C2 ii)

## 4. My defangs (extra-defang.json, applied by the frozen apply-edit.py; each ONE edit, driver/attribute set-up kept)
X1 AS1 forged->SEED_COUNTER: base_unwitnessed=1, `CASE AS1 … base_witness=no` -> FLAGGED
X2 FM1 drop chmod_notes: base_unwitnessed=1, `CASE FM1 … base_witness=no` -> FLAGGED
X3 FWw forged->SEED_COUNTER: base_unwitnessed=0, `CASE FWw … base_witness=yes` -> NOT FLAGGED [MEDIUM]
X4 FC1 forged->SEED_COUNTER: base_unwitnessed=0, `CASE FC1 … base_witness=yes` -> NOT FLAGGED [MEDIUM]
X5 AS2+FC2 in-run write->SEED_COUNTER: `CASE AS2 base_witness=no` (flagged) but `CASE FC2 base_witness=yes` (missed) [MEDIUM]
all five keep the row shape base=accept / new=refuse RECEIPT-FILTER-DRIVER-SET

## Finding MEDIUM — the witness is tree-global, not row-specific
tree_divergence counts any worktree-vs-rev difference anywhere (census/round-73/c1-counter.py:1063-1120, `untracked` included). FC1/FC2: .gitattributes is committed in a child of the row's rev (build_case returns the seed rev, :686 and :1028-1036; mutate commits it, :955-968), so it is always `untracked`; FWw: the worktree copy is overwritten with filter lines (:996-1000), so it always diverges. Measured: probe FC2 pre=1 `first=.gitattributes:untracked`; FC1 pre=2; FWw pre=2.
Consequence: a defanged FC1/FC2/FWw still prints base_witness=yes and stays inside base_forgeries=15 — the S72MutCounter MF defect is fixed for 12 of the 15 base-accepted refuse rows, not all 15. The frozen D1..D5 predicate is unaffected (5/5 flagged).
LOW: base_forgeries stays 15 in every defang run (the defanged row is still counted there); detection lives only in base_unwitnessed.
LOW: the selftest's witness cases are synthetic fate dicts (:2020-2030), so they cannot catch this class.

## Files written (under /home/vgpnk/Projects/shokunin/souji-shokunin/)
.ufo/waves/round-73/w1/S73ExecC2.md
.ufo/waves/round-73/w1/S73ExecC2/{after-D1..5,before-D1..5,extra-X1..X5,extra-pos,probe,probe-key-rows,selftest,divergence-rows,fww-fixture}.txt + extra-defang.json
Scratch /fast/scratch/hyaku/souji-r73/S73ExecC2 removed; no tool installs; no lane tracked file touched.
