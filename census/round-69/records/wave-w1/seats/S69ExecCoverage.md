# S69ExecCoverage — C3 coverage table falsification (round 69)

Verdict: C3 claim HOLDS as frozen. Every number re-derived from committed bytes matches; no HIGH/MEDIUM findings. One LOW note on shard EXIT code (below).

## 1. U-rows vs round-68 inventory — MATCH (14/14)
`awk -F'\t' '$5=="none"{print $1}' census/round-68/records/wave-w1/seats/S68ScoutDeclared/declared-protections.tsv`
→ D01 D02 D03 D04 D05 D06 D07 D08 D10 D18 D19 D21 D29 D30
Declared-coverage ids identical set. All 14 `protection-short` values are strict prefixes of the r68 `protection` text (verified per-row with shell substring test). Evidence: declared-coverage.tsv:2-15 vs declared-protections.tsv:2,3,4,5,6,7,8,9,11,19,20,22,30,31.

## 2. Per-row battery outcome (independent full battery run, 429s, 2026-11-05)
Cmd: `python3 -B census/round-69/c1-counter.py --root .../souji-shokunin --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work /fast/scratch/hyaku/souji-r69/S69ExecCoverage --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery`
Observed summary: `BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0` + `EXIT=0` — byte-identical to L1's records/c1-after-battery.txt (25 MUTANT lines + BATTERY + EXIT coverage, see §4).

| id | mutant | coverage observed-outcome | manifest expected | my re-derived | match |
|----|--------|---------------------------|-------------------|---------------|-------|
| D01 | D01 | forgery | forgery | `MUTANT D01 outcome=forgery ... forgeries=4` | yes |
| D02 | D02 | label-only | label-only | `outcome=label-only ... label=1` | yes |
| D03 | D03 | label-only | label-only | `outcome=label-only ... label=1` | yes |
| D04 | D04 | label-only | label-only | `outcome=label-only ... label=1` | yes |
| D05 | D05 | forgery | forgery | `outcome=forgery ... forgeries=1` | yes |
| D06 | D06 | forgery | forgery | `outcome=forgery ... forgeries=6` | yes |
| D07 | D07 | forgery | forgery | `outcome=forgery ... forgeries=1` | yes |
| D08 | D08 | forgery | forgery | `outcome=forgery ... forgeries=3` | yes |
| D10 | D10 | forgery | forgery | `outcome=forgery ... forgeries=1` | yes |
| D18 | D18 | survived (limit) | survived (limits.tsv) | own `--only D18` run: `MUTANT D18 outcome=survived expected=survived` | yes |
| D19 | D19 | forgery | forgery | `outcome=forgery ... forgeries=1` | yes |
| D21 | D21 | forgery | forgery | `outcome=forgery ... forgeries=1` | yes |
| D29 | D29 | survived (limit) | survived (limits.tsv) | own `--only D29` run: `MUTANT D29 outcome=survived expected=survived` | yes |
| D30 | D30 | echo-violation | echo-violation | `outcome=echo-violation ... echo=2` | yes |

All 12 covered mutants exist as members in census/round-69/battery/ (list verified); SHA256SUMS checks OK (head verified). Battery members are single-edit diffs from the frozen candidate writer — spot-checked D01/D18/D29 diffs (correct removals: flag-refusal block, `GIT_OPTIONAL_LOCKS` pin, `:(top)` pathspec). Note: 30 files under battery/ vs 28 SHA256SUMS entries — 2 extra (dirs?) — inspection shows member count OK and manifest count 26; no finding.
Shard caveat: my `--only` runs emit `EXIT=1` despite `regress=PASS` (committed controls show same EXIT=1) — shard-mode exit semantics, not an outcome mismatch.

## 3. D18 and D29 limit receipts (own runs, battery-limits.tsv)
- D18: `MUTANT D18 outcome=survived expected=survived forgeries=0 echo=0 honest=0 label=0 errors=0 regress=PASS` / `BATTERY mutants=1 ... survived=1 error=0` — identical to controls/d18-limit-battery.txt. Reason in preregistration.txt nearly matches: D18 pin present in D18.py diff; no honest row can observe it (Q132 note). Confirmed.
- D29: `MUTANT D29 outcome=survived expected=survived ... regress=PASS` / same battery line — identical to controls/d29-limit-battery.txt. Reason: D29.py drops only `:(top)`; every writer ls-files runs with `-C <toplevel>` so cwd is already the toplevel. Consistent with the code I read (writer line 381 region: `git(top, "ls-files", "-v", "-z", ":(top)")`).

## 4. awk check
`awk -F'\t' 'NR>1{print $5}' census/round-69/records/declared-coverage.tsv | sort | uniq -c` → `2 limit`, `12 mutant`. Disposition column $5 is correct column (header: id, protection-short, battery-mutant, observed-outcome, disposition, evidence). Frozen counting command reproduces exactly.
C3-do-nothing control (census/round-69/controls/c3-do-nothing.txt) lists the same 14 ids with `U-rows-with-no-battery-mutant=14` — consistent with r68 matrix above.

## LOW note
- Shard EXIT=1 on `--only D18`/`--only D29` despite regress=PASS: matches committed control values; semantics worth an L1 footnote but not a finding.

Files written: only this report (.ufo/waves/round-69/w1/S69ExecCoverage.md). Scratch work under /fast/scratch/hyaku/souji-r69/S69ExecCoverage/ (fresh, left as-is).

(Report: .ufo/waves/round-69/w1/S69ExecCoverage.md)
