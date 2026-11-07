# S75Scribe — r75 corpus drafts (SOURCES S318/S319, knowledge r75, census validate)

VERDICTS (all numbers re-derived by this seat from committed bytes; none trusted from the receipts alone)
- C1 W arm REPRODUCED: 25 rows, mismatches=0, EXIT=0 (gate blob 620ed97e from rev 1ad737b4).
- C1 base arm REPRODUCED: mismatches=2 [f-info-exclude f5-info-exclude-dir], EXIT=1 (gate 062b6d39, rev 52d3f07d).
- C1 K-b blanket REPRODUCED: mismatches=3 [f2 f6 f7], EXIT=1 (variant gate e0d2e149).
- C2 kills REPRODUCED: r75 6/6 + pristine PASS EXIT=0; do-nothing r74 4 killed / 2 survived EXIT=1; r75 selftest 64/64 EXIT=0.
- Drafts WRITTEN; census validate EXIT=0. No frozen claim falsified. No HIGH finding.

COMMANDS (lane root /home/vgpnk/Projects/shokunin/souji-shokunin; scratch /fast/scratch/hyaku/souji-r75/S75Scribe)
- D=$(mktemp -d -p S fx.XXXXXX); git show 1ad737b4:tools/souji-pre-report-gate.sh > D/…; same for souji-receipt-write.py;
  python3 -B census/round-75/c1-evade-counter.py --gate-dir D --work S/c1w → `SUMMARY rows=25 mismatches=0 errors=0` `EXIT=0`
- same with rev 52d3f07d → `mismatches=2 [f-info-exclude f5-info-exclude-dir]` `EXIT=1`; with controls/variants/gate-K-b-blanket-ignored.sh → `mismatches=3 [f2 f6 f7]` `EXIT=1`
- python3 -B census/round-75/c2-kill-counter.py --pristine records/c2-after-pristine-selftest.txt --mutant X09/P1/M08/M14/M15/M17=records/… →
  `SUMMARY mutants=6 killed=6 survived=0 unread=0 pristine=PASS` `EXIT=0`; r74 receipts → `killed=4 survived=2` `EXIT=1`
- python3 -B census/round-75/c1-counter.py --selftest --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1 --work S/st-pristine →
  `SELFTEST cases=64 pass=64 fail=0` `EXIT=0`
- sha256sum census/round-75/srcs/*.adoc = 338221577b4f… (9535 B) / 56af3aad88df… (12123 B); curl -sSL re-fetch of both v2.56.0 raw URLs → HTTP 200, byte-identical.
- git archive HEAD corpus | tar -x; appended rows after S317 (NF=13 each); sources-census.sh validate --file <copy>/corpus/SOURCES.md with lane tools//SKILL.md mirrored → `file ok` 0 E, 86 W04 `EXIT=0`.

EVIDENCE
- Gate mechanism: tools/souji-pre-report-gate.sh:85-101 at rev 1ad737b4 (two `git ls-files -z --others --ignored` listings, set difference).
- Populations: census/round-75/c1-population.tsv (25 rows, frozen expectations); c2-mutants.json (X09, X15; P1=X15∘M17); records/c2-after.txt (SUMMARY 6/6).
- Rulings: census/round-75/preregistration.txt § C1 Labels; source defects corpus/lessons/round-74-verifier-spotcheck.md:112 (defect 2, n-filemode-config) and :122 (defect 4, f2-gitignore stated limit).
- Counter diff: census/round-75/c1-counter.py vs census/round-74/c1-counter.py = 33 changed lines (header + two selftest checks, census/round-75/c1-counter.py:2015-2053); no evaluate()/verdict change.

FINDINGS
- MEDIUM: the uncommitted r75 knowledge section already in the worktree freezes "25867 paths each" for the lane's two ignore listings. Measured 25993 then 25996 minutes apart (git ls-files -o -i --exclude-standard = per-directory variant), because .ufo/waves/ is ignored by committed .gitignore:1 and seats keep writing there. Corpus text must state the predicate (equality), not the count.
- MEDIUM: prereg C1 target (iii) domain trial check-clean=PASS has no committed receipt at rev A/5d10e09. At the dirty wave tip the gate fails clean for tracked modifications (.ufo/waves/round-75/w1/S75ExecC1.md:8); I re-derived only the ignore-predicate equality (diff 0), which supports but does not replace that run at the report tip.
- LOW: corpus/SOURCES.md and corpus/knowledge/filter-filemode-witness.md already carry uncommitted S318/S319 rows and an r75 section from another seat. Both anchor offsets resolve (1699, 11681) and agree with my drafts; appending both sets duplicates ids (E03). My S319 quote was aligned to the stronger EXCLUDE PATTERNS sentence at 11681.
- LOW: the lane's cleanliness rests on the f7 stated limit — 13392 `.jj/` and 5 `.ruff_cache/` ignored paths are hidden by their untracked self-ignoring `.gitignore`, not by committed rules; the knowledge draft states this, the worktree draft says "all under committed rules or .jj/" without the count split.

FILES WRITTEN (all under .ufo/waves/round-75/w1/S75Scribe/ unless absolute)
- .ufo/waves/round-75/w1/S75Scribe.md (this report)
- .ufo/waves/round-75/w1/S75Scribe/sources-rows.md — S318/S319 rows + provenance paragraph (draft)
- .ufo/waves/round-75/w1/S75Scribe/knowledge-r75.md — r75 knowledge section (draft) + re-derivation appendix
- .ufo/waves/round-75/w1/S75Scribe/census-validate.txt — validation commands, exit codes, findings
- .ufo/waves/round-75/w1/S75Scribe/run-c1-W.txt, run-c1-base.txt, run-c1-Kb.txt, run-c2-pristine.txt, validate-mirror.out — receipts copied small text
- scratch /fast/scratch/hyaku/souji-r75/S75Scribe removed before yield; no lane file edited; no git/jj mutation; no tool installed.
