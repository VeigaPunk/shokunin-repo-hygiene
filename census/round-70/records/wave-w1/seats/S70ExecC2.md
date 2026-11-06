# S70ExecC2 — C2 falsification (souji r70)

Verdict: C2 REPRODUCED byte for byte. Lane HEAD moved 20c117ce -> 152b46c3 mid-wave; instruments at both observed
tips equal the freeze blobs (counter 3f684c3e…, harness 38c30eff…, matrix 1607e4f8…) and worktree sha256 matched my runs.

Commands (from /home/vgpnk/Projects/shokunin/souji-shokunin; scratch /fast/scratch/hyaku/souji-r70/S70ExecC2):
1 `c2-harness.py --label c2-after-r70 --counter census/round-70/c1-counter.py --matrix census/round-70/c1-matrix.tsv --root <lane> --base-rev e063a2fc… --battery-dir census/round-69/battery --battery-manifest census/round-69/battery-manifest.tsv --work $S/c2`
2 same --label c2-before-r69 --counter census/round-69/c1-counter.py --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917ea…
3-4 same (r70 matrix, e063a2fc) --label c2-CF1 --counter census/round-70/controls/variants/CF1-selftest-always-fails.py; then --label c2-CF2 --counter census/round-70/controls/variants/CF2-battery-always-fatal.py
5 `TMPDIR=$S/wst python3 -B tools/souji-receipt-write.py --selftest --work $S/wst`
6 `python3 -B census/round-70/c1-counter.py --selftest --root <lane> --matrix census/round-70/c1-matrix.tsv --base-rev e063a2fc… --work $S/st`

Observed:
- C2 after EXIT=0 — `SUMMARY label=c2-after-r70 positive_selftest=PASS positive_battery=PASS mutants=4 killed=4 survived=0 tamper=detected score=0`; P-SELFTEST 29/29; P-BATTERY forgeries=9; CM1–CM4 killed (sha256 6d7fbf0c/4fc11293/d3a6a825/c18efbc6); T1 rc=2 `D01.py sha256 8c1ecef2bd30 != listed 913f6a611d6a`.
- C2 before EXIT=1 — `SUMMARY label=c2-before-r69 … killed=0 survived=4 tamper=undetected score=5`; P-SELFTEST 16/16.
- CF1 EXIT=2 — positive_selftest=FAIL positive_battery=PASS killed=4 survived=0 tamper=detected score=0.
- CF2 EXIT=2 — positive_selftest=PASS positive_battery=FAIL killed=4 survived=0 tamper=detected score=0.
- Writer selftest rc=0 — `SELFTEST cases=38 pass=38 fail=0` (pathspec-env case ok).
- Counter selftest rc=0 — `SELFTEST cases=29 pass=29 fail=0`, `EXIT=0`.

Diffs (full filtered diff in S70ExecC2/diffs.txt):
- c2-after-r70 vs records/c2-after.txt: IDENTICAL (POSITIVE/MUTANT/TAMPER/SUMMARY/EXIT/# lines).
- c2-before-r69 vs controls/c2-before-r69.txt: IDENTICAL.
- c2-CF1/CF2 vs controls/c2-CF1-selftest-always-fails.txt / c2-CF2-battery-always-fatal.txt: label-field-only
  difference (my assigned labels c2-CF1/c2-CF2); every metric identical.
- Both SELFTEST lines match their receipts exactly.

Findings:
- LOW: selftest receipts are not verbatim stdout — writer-selftest.txt:44 and counter-selftest.txt:35-36 carry a
  trailing `EXIT=0` the instruments do not emit (writer cmd_selftest prints none, tools/souji-receipt-write.py:1569-1593;
  counter prints exactly one, census/round-70/c1-counter.py:1410, hence the double EXIT in its receipt). Likely a
  capture wrapper's `EXIT=$?`. SELFTEST lines and rc=0 unaffected; no frozen predicate cites these lines.
- LOW: CF control receipt labels differ from the seat-invocation labels (…-selftest-always-fails / …-battery-always-fatal);
  label field only.
- No C2 number failed to reproduce; no HIGH/MEDIUM finding. No risk/blocker.

Files written: .ufo/waves/round-70/w1/S70ExecC2.md; .ufo/waves/round-70/w1/S70ExecC2/{c2-after-r70.out,c2-after-r70.err,
c2-before-r69.out,c2-before-r69.err,c2-CF1.out,c2-CF1.err,c2-CF2.out,c2-CF2.err,writer-selftest.out,writer-selftest.err,
counter-selftest.out,counter-selftest.err,diffs.txt}. No lane file edited; scratch removed. Tooling: none installed.
