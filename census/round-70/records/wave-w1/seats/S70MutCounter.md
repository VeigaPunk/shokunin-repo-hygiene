# S70MutCounter — r70 counter self-check: 10 further single-edit mutants + CM1-CM4 match counts

Baseline re-derived from committed bytes (lane /home/vgpnk/Projects/shokunin/souji-shokunin):
counter sha256 3f684c3ece0b2392b0a4fd2073720c5dcf1f701d30bbfc9a8b3f33296d3b3ada is identical at
0243af04 / 93a051b2 / e84f691b / feb283ee / 9167e02d; pristine selftest `SELFTEST cases=29 pass=29
fail=0`, `EXIT=0`; pristine C1 candidate arm prints the frozen `SUMMARY matrix=59 base_forgeries=4
base_honest=13 new_forgeries=0 new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS`
+ `EXIT=0`. Scratch S=/fast/scratch/hyaku/souji-r70/S70MutCounter (removed after the run; every
output, mutant source and script copied to this directory).

Commands (from the lane root; <lane>=/home/vgpnk/Projects/shokunin/souji-shokunin):
- selftest: `python3 -B $S/mut/<X>/c1-counter.py --selftest --root <lane> --matrix <lane>/census/round-70/c1-matrix.tsv --base-rev e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333 --work $S/mut/<X>/st`
- C1 arm:   `python3 -B <counter> --root <lane> --matrix <lane>/census/round-70/c1-matrix.tsv --base-rev e063a2fc… --rev 93a051b2c936ff6eafca8e8b31d918e3d20fd3da --tool tools/souji-receipt-write.py --work $S/c1-<tag>`
- harness:  `python3 -B $S/c2-harness.py --label c2-<X> --counter $S/mut/<X>/c1-counter.py --matrix <lane>/census/round-70/c1-matrix.tsv --root <lane> --base-rev e063a2fc… --battery-dir <lane>/census/round-69/battery --battery-manifest <lane>/census/round-69/battery-manifest.tsv --work $S/h-<X>`
- battery:  `<counter> … --battery-manifest <lane>/census/round-69/battery-manifest.tsv --battery-dir <lane>/census/round-69/battery [--only D01] --work $S/batt-<tag>`

| id | single edit in census/round-70/c1-counter.py | selftest | other frozen arm | verdict |
|----|----------------------------------------------|----------|------------------|---------|
| X1 | echo_violation body -> `return True` (850-854) | passes 27, FAIL 2 (echo judge x2), EXIT=1 | — | killed |
| X2 | verify_members `digest = listed[fname]` (1167) | passes 28, FAIL 1 (tampered member), EXIT=1 | — | killed |
| X3 | verify_members not-listed -> `continue` (1163) | passes 28, FAIL 1 (unlisted member), EXIT=1 | — | killed |
| X4 | classify_outcome label-only before over-refusal (1077-1081) | passes 28, FAIL 1 (honest outranks label flip), EXIT=1 | — | killed |
| X5 | classify_outcome echo before forgery (1073-1076) | passes 28, FAIL 1 (forgery outranks echo), EXIT=1 | — | killed |
| X6 | battery_verdict drops `tally["error"] == 0` (1135) | 29/29, EXIT=0 | harness EXIT=2 (CM4 apply=FAIL: pattern matched 0 times); full battery EXIT=1 for pristine AND X6 | survived selftest |
| X7 | clean_env keeps PATHSPEC_VARS (393) | 29/29, EXIT=0 | C1 arm clean ambient: frozen SUMMARY, EXIT=0; harness EXIT=0 | survived (blind) |
| X8 | case_env `ps = None` (729) | 29/29, EXIT=0 | C1 arm EXIT=0 but `base_forgeries=0 base_honest=15` (frozen 4/13); harness EXIT=0 | survived (blind) |
| X9 | verify_members drops duplicate-listing check (1156) | 29/29, EXIT=0 | battery D01 EXIT=0; real SHA256SUMS has no duplicate line | survived (blind) |
| X10 | verify_members drops malformed-line check (1154) | 29/29, EXIT=0 | battery D01 EXIT=0; real SHA256SUMS is 28 all-2-field lines | survived (blind) |

Survivor detail (measured, not inferred):
- X6 `battery_verdict([("E","error","error")])` -> pristine rc=1, X6 rc=0 (`all_match=True`); the
  frozen manifest has no `error` expectation, so only `all_match` guards it. X6's other-arm "catch"
  is a text collision: CM4's regex `all_match and tally["survived"] == 0 and ` no longer matches,
  so the harness returns INVALID (EXIT=2), not a semantic kill. Full-battery rc is 1 either way.
- X7 with ambient `GIT_LITERAL_PATHSPECS=1 GIT_GLOB_PATHSPECS=1 GIT_NOGLOB_PATHSPECS=1
  GIT_ICASE_PATHSPECS=1`: pristine prints the frozen SUMMARY EXIT=0 (scrub holds); X7 prints
  `new_forgeries=0 new_honest=15 ... regress=FAIL`, EXIT=1. No selftest case calls clean_env, so the
  scrub is only caught by an ambient-poisoned C1 run, which no round receipt performs.
- X8 is the strongest blind spot: the counter ignores every row's `pathspec_env`, the 4 base
  forgeries (LD LN4 LG1 LA9) vanish and the 2 base over-refusals (GA ICA) turn honest
  (`base_forgeries` 4->0, `base_honest` 13->15), and the counter
  still reports `regress=PASS` and `EXIT=0` — `claim_upheld` (1044-1049) never binds the base counts,
  so only a byte comparison of SUMMARY against the frozen receipt betrays it.
- X9 accepts a SHA256SUMS listing M1.py twice (pristine: `SHA256SUMS line 2 lists M1.py twice`).
- X10 accepts a SHA256SUMS with `GARBAGE-LINE-NOT-A-DIGEST` beside a valid M1.py line (pristine:
  `SHA256SUMS line 2 malformed`); a single malformed-only file is still refused only incidentally
  ("member M1.py is not listed").

CM1-CM4 match counts (harness `apply_mutant`, `cm-match-and-mutant-build.txt`): r70 counter
forgery_block=1 honest_block=1, CM2/CM3/CM4 matches=1 each; r69 counter identically 1/1 and 1/1/1.
Harness-applied r70 shas 6d7fbf0c51179658 / 4fc112933dd8e2ea / d3a6a825fff9d485 / c18efbc60f5a8319
reproduce census/round-70/records/c2-after.txt byte for byte; r69 shas 2f4af242…/7cd52090…/e38167ba…/443df0c7….

Findings (survivors are coverage findings, not claim failures):
- HIGH none. MEDIUM X8 — the counter's own rc does not bind base_forgeries/base_honest, so a counter
  that drops a row's caller env self-certifies EXIT=0; selftest section (5) checks only noecho_env.
- MEDIUM X7 — the PATHSPEC_VARS ambient scrub has no selftest assertion; only an ambient-poisoned
  run (EXIT=1 via regress=FAIL) distinguishes it, and the frozen invocations set no ambient pathspec
  variable, so neither the C1 receipt nor the C2 harness would ever see the regression.
- MEDIUM (round-70 instrument) — the frozen r69 battery over the 59-row matrix classifies all 26
  members as `forgery` (18 kills / 5 label-only / 2 over-refusal / 1 echo in census/round-69/records/
  c1-after-battery.txt), 8 expectations miss (M-CD-NCABS, M-CD-NCRAW, K1, M-CD-ROOTREL, D02, D03,
  D04, D30), `all_match=false`, EXIT=1; C2's P-BATTERY samples only D01, so this divergence is
  unreported in every round-70 receipt (within the prereg's "battery not regenerated" limit, but never
  measured).
- LOW X6 — the `tally["error"]` gate has no selftest case; the frozen manifest cannot exercise it.
- LOW X9/X10 — SHA256SUMS duplicate- and malformed-line checks are untested; the frozen battery is
  clean, so no arm can catch them.

Files written under .ufo/waves/round-70/w1/S70MutCounter/: S70MutCounter.md; build_mutants.py;
probe_functions.py; mutants/X1.py..X10.py; cm-match-and-mutant-build.txt; probe-functions.txt;
probe-x10-refined.txt; selftest-X1..X10.txt; c1-base.txt, c1-X8.txt, c1-pristine-poison.txt,
c1-X7-poison.txt, c1-X7-clean.txt; c2-harness-X6..X10.txt; battery-batt-pristine-summary.txt,
battery-batt-X6-summary.txt, battery-batt-X9-summary.txt, battery-batt-X10-summary.txt,
battery-pristine-full.txt.
Lane tracked files untouched; no git/jj mutation; no tool installed (python3 3.14.8, git 2.56.0 used
as frozen).
