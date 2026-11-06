# S70Reviewer — round-70 post-landing falsification (C1 pathspec scrub, C2 counter self-check)

Seat: S70Reviewer. All runs from lane root, scratch /fast/scratch/hyaku/souji-r70/S70Reviewer (removed after copying evidence here). Working tree clean; post-tip commits (feb283ee..HEAD) touch none of the instruments run.

## Verdicts

1. **Writer scrub — SOUND.** Every verdict-path git call goes through `git()` (tools/souji-receipt-write.py:108-119), which drops `PATHSPEC_ENV` (line 105: GIT_LITERAL/GLOB/NOGLOB/ICASE_PATHSPECS) plus GIT_DIR/GIT_WORK_TREE/GIT_COMMON_DIR, and pins GIT_OPTIONAL_LOCKS=0, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1, GIT_NO_REPLACE_OBJECTS=1. Call sites: :131, :170, :316, :359, :384, :393, :405, :426, :445, :506, :507 — all `git(...)`. The only other verdict-path subprocess is the wrapped command `subprocess.Popen(argv, stdout=..., stderr=...)` at :478 with NO `env=` — inherits os.environ untouched (claim "wrapped command still sees the variable" verified live by selftest case 38). Remaining subprocess uses (:601-:1457) are selftest-only helpers on selftest-created fixtures. Writer selftest reproduced: `SELFTEST cases=38 pass=38 fail=0`.

2. **Counter — SOUND.** `_row_env` body is byte-identical to r69 `case_env` (diff: def line only); r70 `case_env` (:726-735) returns it unchanged for the 47 carried rows (no `pathspec_env` key; CASE_SPECS diff is pure insertion 240a272,298; ROWS list appends 12). `clean_env`'s 8 new ambient drops (:391-394) cannot change a carried row: no `_row_env` branch sets them, row env is applied after the scrub (`if extra: e.update(extra)` :400), and this host's ambient GIT_* are only GIT_EDITOR/GIT_PAGER/GIT_SEQUENCE_EDITOR/GIT_TERMINAL_PROMPT. Battery arm: `--only` filters the manifest, unknown names fatal (:1502-1508), `verify_members` runs over selected names only (:1516), `battery_verdict` is pure (:1125-1137). **LOW:** `--only ,` (empty selection) yields vacuous `BATTERY mutants=0 ... EXIT=0` (:1502-1508 + :1537-1542) — instrument edge, not exercised by any frozen claim.

3. **Harness — SOUND.** Positive arms require unmutated counter `--selftest` rc=0 and battery-arm rc=0 else EXIT=2 (c2-harness.py:144-149, 182-186); a blanket-refusing counter fails both (committed controls CF1/CF2 both EXIT=2, reproduced in receipts). T1 is meaningful: manifest shows D01 and D05 both `forgery`; tamper replaces D01.py with D05.py bytes, SHA256SUMS untouched — detection is solely the sha256 binding (observed `member D01.py sha256 8c1ecef2bd30 != listed 913f6a611d6a`, rc=2). MUTANTS regexes each match exactly once in both counters (grep counts 1/1/1/1/1/1 for the five literals; runs show no apply=FAIL); CM1 uses literal-block swap with count==1 guards (:54-63).

4. **Prereg vs receipts — SOUND.** Every prereg number matches the committed receipt byte-for-byte, and my six independent runs reproduce every deciding line identically (diffs vs receipts differ only in the 4-line receipt headers and the wrapper-appended EXIT line): C1 candidate `SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=0 new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS` + `EXIT=0`; `--new-tool` form identical; do-nothing/F1/F2/c2-before/CF1/CF2 controls match; writer selftest 38/38; counter selftest 29/29. Base writer sha256 b811ee2a… verified at e063a2fc; git 2.56.0; S304 capture sha256 534c674f…f9d1 matches SOURCES.md; matrix = header + 59 rows.

5. **SKILL.md — SOUND, one LOW.** r70 C1 row verdict map matches `claim_upheld` (:1044-1048; errors==0 is implied via all_new_match since an error verdict never equals accept/refuse). r70 C2 row map matches harness :182-186; **LOW:** it omits the early argument-validation EXIT=2 cases (bad --base-rev, --work under /tmp//var/tmp/TMPDIR/lane root). r69 battery row (routed D3): verdict map matches the r69 counter's battery rc (`all_match and survived==0 and error==0`, r69 :1369-1370; fatal→EXIT=2 :1077-1080); "(16 checks)" confirmed by c2-before P-SELFTEST `cases=16`; pinned path census/round-69/records/c1-after-battery.txt exists (511477 B). Entry/self-test commands follow the registry placeholder convention and are runnable from the lane root.

## Findings
- LOW: counter `--only` with an empty selection passes vacuously (mutants=0, EXIT=0) — census/round-70/c1-counter.py:1502-1508,1537-1542.
- LOW: SKILL.md r70 C2 verdict map does not mention argument-validation EXIT=2 — SKILL.md r70 table.
- Residual risk (observed, not a claim defect): the r70 counter's battery arm over the FULL r69 battery reclassifies base-era members on the 12 new pathspec rows — `--only D02` gave `outcome=forgery expected=label-only ... EXIT=1` (evidence d02-battery-probe.txt). This is honest Q131 signal consistent with the prereg named limit ("the battery is not regenerated this round"); C2's frozen predicate scopes P-BATTERY to D01, which still passes.

## Commands run (all from lane root; <SCRATCH>=/fast/scratch/hyaku/souji-r70/S70Reviewer)
- `python3 -B census/round-70/c1-counter.py --root . --matrix census/round-70/c1-matrix.tsv --base-rev e063a2fc… --rev 93a051b2… --tool tools/souji-receipt-write.py --work $S/c1` → SUMMARY/EXIT=0 above (RC=0).
- Same with `--new-tool $S/newtool.py` (copy of candidate writer) → identical SUMMARY, EXIT=0.
- `TMPDIR=$S/wst python3 -B tools/souji-receipt-write.py --selftest --work $S/wst` → cases=38 pass=38, RC=0.
- `python3 -B census/round-70/c1-counter.py --selftest --root . --matrix … --base-rev e063a2fc… --work $S/st` → cases=29 pass=29, EXIT=0.
- `python3 -B census/round-70/c2-harness.py --label c2-after-r70 --counter census/round-70/c1-counter.py --matrix … --base-rev e063a2fc… --battery-dir census/round-69/battery --battery-manifest census/round-69/battery-manifest.tsv --work $S/c2` → score=0, EXIT=0.
- Same with `--label c2-before-r69 --counter census/round-69/c1-counter.py --matrix census/round-69/c1-matrix.tsv --base-rev 36390879…` → score=5, EXIT=1.
- Probe: r70 counter `--battery-manifest … --battery-dir … --only D02 --work $S/d02` → forgery vs label-only, EXIT=1.
- Static: `diff census/round-69/c1-counter.py census/round-70/c1-counter.py` (full, saved as r69-vs-r70-counter.diff); sed-extracted function-body diffs; grep uniqueness counts for all five MUTANTS literals; sha256sum of writer at both revs, S304 capture, battery SHA256SUMS.

## Files written (this seat dir)
c1-candidate-run.txt, c1-newtool-run.txt, writer-selftest-run.txt, counter-selftest-run.txt, c2-after-run.txt, c2-before-run.txt, r69-vs-r70-counter.diff, d02-battery-probe.txt, S70Reviewer.md.
