# S72MutCounter — mutation test of the r72 counter additions (souji r72, w1)

VERDICT: 14 single-edit mutants of the r72 additions; 11 killed, 3 survive every frozen predicate
(MF HIGH, MB2 MEDIUM, MJ/MK LOW). All four frozen predicates re-derive true on the committed bytes.

Frozen predicates re-derived (my bytes, my scratch):
- C1(i) harness repro: `SUMMARY label=c1-pristine-repro positive_selftest=PASS x_mutants=11 x_killed=11
  x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0` EXIT=0; the 11 mutants applied by hand
  give the same 11 kills and the same mutant sha256s as records/c1-after.txt.
- C1(ii): Y6 composites print `base_forgeries=2 … base_mismatches=10` EXIT=1 == records/c1-Y6-main-arm.txt.
- C2(i): `BATTERY mutants=5 kills=5 label_only=0 over_refusal=0 echo_violation=0 survived=0 error=0
  all_match=true` EXIT=0, MUTANT sha256s 27daa4b3/b88c8471/b21ccdd2/a9c1fa16/798f9344 == records/c2-after-battery.txt.
- C2(ii): `SUMMARY matrix=75 base_forgeries=12 base_honest=19 base_mismatches=0 new_forgeries=0
  new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` EXIT=0 == records/c2-honest-writer.txt.

Table: .ufo/waves/round-72/w1/S72MutCounter/mutants.tsv (14 rows: id, edit, selftest, main, battery,
verdict). Selftest-killed MA MC ML; killed outside the selftest MB (frozen Y4) MD (frozen Z1) MM
(C1(ii) N>0) ME MG MH MI (main arm and/or battery); survivors MF MB2 MJ MK.

HIGH — FWi's forgery is unverified and WM4's "kill" is an honest-tree accept.
  MF: inrun_argv("create-driver-forge") `_b(FORGED_SAMESIZE)`->`_b(SEED_COUNTER)` (c1-counter.py:515).
  selftest 44/44; kills all 11 frozen mutants; main arm EXIT=0 bm=0 cm=0; battery kills=5 all_match=true.
  In the WM4 fixture the worktree tools/counter.py is byte-identical to HEAD:tools/counter.py,
  `git status --porcelain` empty, an 804-byte receipt written — yet `MUTANT WM4 outcome=forgery
  forgeries=1` (classify_outcome counts expect=refuse & verdict=accept, c1-counter.py:1315; FWi is
  WM4's only such row). C2(i)'s kills=5 does not require five actual forgeries.
MEDIUM — the base-witness row list is self-referential. MB2: `WITNESS_ROWS=("AS1","AS2")`
  (c1-counter.py:283) drops FC1 FC2 FC3 FM1 FM2; the (9a) gate `len(wrows)==len(WITNESS_ROWS)`
  (c1-counter.py:1747) is a tautology. MB2: selftest 44/44, kills all 11 frozen mutants, main EXIT=0,
  battery kills=5 — all four predicates true on 2 of 7 witness rows. MB/MD are caught only because
  frozen Y4/Z1 target exactly AS1/AS2 and GIT_DIR (MB+Y4, MD+Z1 44/44 green vs P+Y4, P+Z1 43/44 red).
LOW — MJ: load_matrix's base_expect check (c1-counter.py:1120) is read by no selftest section and no
  frozen mutant (all 11 edits land outside 1103-1132); a bad value still gives base_mismatches>0 -> EXIT=1.
LOW — MK: the build-error `c["base_mismatches"] += 1` (c1-counter.py:1211) is dead defence (all_new_match
  already fails the claim; no arm reaches it; no frozen mutant lands in 1205-1213).
INFO — ME's battery run prints base_mismatches=1 on all five MUTANT lines while WM3/WM4/WM6/WM8 still
  score forgery: the declared separability (battery rc ignores base_mismatches) holds.
INFO — WM7: a corrupt index makes `git check-attr` fail (rc=128) but the writer refuses earlier ("cannot
  read index flags … index file smaller than expected"); unreadable .gitattributes or a directory there
  gives rc=0 "unspecified" (git ignores it, the filter stops applying). No fail-open path found.

Commands (cwd /home/vgpnk/Projects/shokunin/souji-shokunin; scratch /fast/scratch/hyaku/souji-r72/S72MutCounter):
  python3 -B <mut> --selftest --root . --matrix census/round-72/c1-matrix.tsv --base-rev 8b9345b1… --work <S>/w-<id>
  python3 -B <mut> --root . --matrix … --base-rev 8b9345b1… --rev 0bf098dd… --tool tools/souji-receipt-write.py --work <S>/m-<id>
  python3 -B <mut> --root . --matrix … --base-rev 8b9345b1… --work <S>/b-<id> --battery-manifest census/round-72/battery-manifest.tsv --battery-dir census/round-72/battery
  python3 -B census/round-71/c2-harness.py --label c1-pristine-repro --counter census/round-72/c1-counter.py --matrix … --mutants census/round-72/c1-mutants.json --work <S>/h-pristine

Files: .ufo/waves/round-72/w1/S72MutCounter.md; .ufo/waves/round-72/w1/S72MutCounter/{mutants.tsv,
results.txt, build-mutants.py, mf-wm4-proof.txt}. Lane tracked files untouched (counter 7578447d…a912,
matrix cd8490b4…33b8, writer b7790001…244d, harness 6c7bf41d…75fb); scratch removed.
