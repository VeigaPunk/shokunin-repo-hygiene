# S72ExecC1 — C1 falsification from committed bytes

Verdict: **C1(i), C1(ii), C2(i), C2(ii) and controls (a)-(d) all REPRODUCE; no frozen claim falsified.**
Lane HEAD 2ec8b63d; all runs from /home/vgpnk/Projects/shokunin/souji-shokunin with `--work` under /fast/scratch/hyaku/souji-r72/S72ExecC1 (removed after receipts were copied).

Runs (exact commands in the evidence files; `<S>` = my scratch):
1. C1 harness (`census/round-71/c2-harness.py --label c1-after-r72 --counter census/round-72/c1-counter.py --matrix census/round-72/c1-matrix.tsv --base-rev 8b9345b1… --mutants census/round-72/c1-mutants.json --work <S>/h`):
   `SUMMARY label=c1-after-r72 positive_selftest=PASS x_mutants=11 x_killed=11 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0` / `EXIT=0` — MATCH.
   `POSITIVE P-SELFTEST rc=0 SELFTEST cases=44 pass=44 fail=0 verdict=PASS`; every MUTANT line has `fail>=1` (no `crashed` pseudo-kill).
2. Y6 main arm — I built the mutant myself from the JSON Y6 entry (count asserted == 1) and ran it with `--rev 0bf098dd… --tool tools/souji-receipt-write.py`:
   `SUMMARY matrix=75 base_forgeries=2 base_honest=19 base_mismatches=10 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=1` — MATCH (N=10 > 0). `cmp` vs `census/round-72/records/variants/r72-Y6-counter.py`: IDENTICAL (sha256 45f3afdb…).
3. Before control (r71 counter, r71 matrix, r72 mutants): `x_killed=5 x_survived=6 … score=6` / `EXIT=1` — MATCH; survivors Y1 Y4 Y6 Y9 Y10 Z1.
4. CF1 control (`--counter census/round-71/controls/variants/CF1-selftest-always-fails.py --matrix census/round-71/c1-matrix.tsv`): `positive_selftest=FAIL … score=6` / `EXIT=2` — MATCH (only my label differs: `c1-CF1` vs committed `c1-CF1-selftest-always-fails`; label is a CLI arg).
Extra (same bytes, cheap): battery `mutants=5 kills=5 … all_match=true` / `EXIT=0`; honest main arm `base_mismatches=0 … new_honest=19` / `EXIT=0`; selftest `cases=44 pass=44 fail=0` / `EXIT=0`; control (c) `kills=0 survived=5 all_match=false` / `EXIT=1`; control (d) `EXIT=0 base_forgeries=2`; probe 35 lines / 10 accepts, PROBE lines byte-identical.

Provenance (6 cmps, all IDENTICAL, each applied to `census/round-71/c1-counter.py` with count==1): Y1 49f660c4 → S71MutCounter/mutants/Y1.py; Y4 65a0eac6; Y6 2e38ca9d; Y9 fca159ca; Y10 99c0ed7f; Z1 0396bfb1 → S71CriticClaims/counter-Y1.py. `mk-counter.py` regenerates `c1-counter.py` (7578447d) and `c1-matrix.tsv` (cd8490b4) byte-identically; WM3/4/5/6/8 are single edits of the lane-base writer (b7790001…244d) and byte-identical to the committed members (SHA256SUMS verified).

Chronology: `merge-base --is-ancestor` 0bf098dd→23372f36 rc=0, 23372f36→06df4f97 rc=0, 06df4f97→2ec8b63d rc=0; `c1-counter.py` and `c1-matrix.tsv` absent at the freeze (`git cat-file -e` rc=128); frozen-input diff 23372f36→2ec8b63d empty (rc=0); `census/round-71/` + `tools/` diff 0bf098dd→2ec8b63d empty; writer sha b7790001…244d at base, freeze and HEAD. Matrix cross-check: 75 rows, `base_expect` = r71 receipt `base=` for all 70 carried rows, `accept` for the 5 FW rows (probe-verified); mismatches NONE; 31 accept = 19 honest + 12 forgery rows (AS1 AS2 FC1 FC2 FC3 FM1 FM2 + FWr FWi FWp FWw FWs).

Findings:
- LOW — receipt fidelity: `census/round-72/c1-counter.py:1481` writes `instrument=COUNTER_REL` (constant, :191) and the `command=` line names `census/round-72/c1-counter.py` even when the executed bytes are the Y6 variant; `instrument_sha256=45f3afdb…` is the true binding, so the receipt stays verifiable but its command line is reconstructed, not literal.
- LOW — WM7: no condition found where `check-attr` fails while `ls-files` succeeds (corrupt index → `ls-files` rc=128 first; unreadable `info/attributes`, `.gitattributes`-as-directory, bad `attr.tree`, `core.attributesFile`-as-directory → git rc=0, silently ignored; `GIT_ATTR_SOURCE` scrubbed at `tools/souji-receipt-write.py:135-136`). The named limit holds; WM7 stays unmeasurable as a forgery.
- LOW — my CF1 label differs from the committed receipt's label (my CLI choice, not a receipt defect).
- Note — battery kills are row-specific (WM3→FWr, WM4→FWi, WM5→FWp, WM6→FWs, WM8→FWw; `forgeries=1` each, all other FW rows refused), so C2(i) is not a blanket-refusal artifact.

Files written: `.ufo/waves/round-72/w1/S72ExecC1.md`; `.ufo/waves/round-72/w1/S72ExecC1/01-c1-after-harness.txt`, `02-c1-before-control.txt`, `03-c1-CF1-control.txt`, `04-y6-main-arm.txt`, `05-main-arm-honest-writer.txt`, `06-battery.txt`, `07-battery-before-r71.txt`, `08-selftest.txt`, `09-probe.txt`, `10-control-d-r71-Y6-main-arm.txt`, `11-provenance.txt`, `12-chronology.txt`, `13-diffs-vs-committed.txt`, `14-wm7-reachability.txt`, `15-matrix-base-expect.txt`. No lane tracked file was modified; no tool installed.
