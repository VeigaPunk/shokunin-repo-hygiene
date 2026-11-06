# S69MutTester — mutation test of the round-69 counter's own gates

Scope: census/round-69/c1-counter.py (frozen sha256 40757709…f5130, verified). Scratch copies only; lane untouched.
Pristine baseline re-derived by me, not the L1. After-arm receipts were NOT read.

## Mutants (single edits of the counter, built in scratch; each diff verified)
- a_precedence: classify_outcome lines 1000-1009: `forgery` block moved below `over-refusal` block (honest checked before forgeries).
- b_echo_false: echo_violation (line 774): `return False` inserted before the noecho loop.
- c_env_no_home: clean_env line 331: `"HOME", "XDG_CONFIG_HOME"` removed from the scrub tuple.
- d_battery_no_cmp: battery branch line 1359: `if obs != exp:` -> `if False:` (expectation comparison dropped).
- e1_tags_dropped: selftest check (6) line 1228: `"SUMMARY matrix=2 "` and `"EXIT="` removed from the tag tuple.
- e2_count_rc_dropped: selftest check (6) line 1233: `len(emitted) == 5 and rc_line == rc` -> `len(emitted) >= 3`.
- extra e3_drop_summary_emit: main line 1409 `emit(summary_line(rows, res))` removed.
- extra e4 = e2 + e3.

## Selftest (`python3 -B <mut>/c1-counter.py --selftest --root <lane> --matrix c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work <scratch>/st/<name>`)
| mutant | selftest EXIT | selftest caught | battery caught |
|---|---|---|---|
| pristine | 0 (`SELFTEST cases=16 pass=16 fail=0`) | — | — |
| a precedence swap | 0 | NO | NO (see below) |
| b echo always False | 0 | NO | YES (D30 -> survived, EXIT=1) |
| c HOME/XDG not scrubbed | 0 | NO | not run (not asked); git-equivalent, see below |
| d battery no comparison | 0 | NO | YES only with a wrong manifest (D01 expected label-only: pristine EXIT=1, mutant EXIT=0); frozen manifest: EXIT=0 both, gate unexercised |
| e1 tags dropped | 1 (`pass=15 fail=1`) | YES, but only via hard-coded `len==5` (line 1233) | n/a |
| e2 count+rc assertion dropped | 0 | NO | n/a |
| e3 SUMMARY emit removed (extra) | 1 | YES (tags missing) | n/a |
| e4 e2 + e3 (extra) | 0 | NO | n/a |

Selftest survivors: a, b, c, d, e2, e4. Battery survivors: a (battery blind), d (gate blind on the frozen manifest).

## Battery runs (`--battery-manifest` / `--battery-dir` on a copy of census/round-69/battery, SHA256SUMS verified rc=0)
- pristine full (frozen manifest, 26 mutants): `BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0`, `EXIT=0`. Reproduced the prereg counts (18/5/2/1/0).
- a (short: M-CD-NCABS, M-CD-NCRAW, D01): identical to pristine (over-refusal 2, forgery 1), EXIT=0. Reason: every forgery member has honest=0 (all 18) and both over-refusal members have forgeries=0, so no member can distinguish the precedence.
- b (short: D30): pristine `outcome=echo-violation echo=2`, EXIT=0; mutant `outcome=survived expected=echo-violation echo=0`, EXIT=1.
- d (wrong manifest D01=label-only): pristine `outcome=forgery expected=label-only`, EXIT=1; mutant EXIT=0 with the same mismatch printed.

## Findings
- MEDIUM — The Q131 precedence (forgery vs over-refusal) is untested by both selftest and battery. Selftest checks (4) (lines 1181-1193) never feed a fate set containing both a forgery and an honest refusal; the frozen battery has zero such members. A precedence regression would be silent.
- MEDIUM — The battery predicate "every outcome matches its manifest expectation" (EXIT=0) is not enforced under mutation: mutant d passes a deliberately wrong expectation. The selftest never runs the battery branch or a mismatched manifest. Consequence: the C1 EXIT=0 claim cannot detect expectation drift, only survivors and errors.
- MEDIUM — echo_violation has no selftest coverage: check (4) (line 1188) tests classify_outcome with a synthetic `echo=True` fate; check (5) (lines 1195-1203) tests only the env key presence. Only the D30 battery member exercises the judge, and a blind judge is reported as `survived`, not as a missing echo (inflating the survived class).
- LOW — Selftest check (6) assertion is weaker than it reads: removing the SUMMARY/EXIT tags is caught only by the hard-coded count 5 (e1), and removing the count and rc match (e2) survives; a dropped SUMMARY emit is still caught (e3) only because the count is 5.
- LOW — clean_env HOME/XDG scrub is redundant for git: probe `fx-c` with ambient HOME containing `[status] showUntrackedFiles = no` showed under pristine and mutant-c `git status --porcelain` = `?? untracked.txt` (identical); without the GIT_CONFIG_GLOBAL=/dev/null pin the same ambient hides the untracked file (control empty). The pin, not the scrub, does the work; HOME now reaches writer env, but the writer at 893b8ef4 has no HOME/XDG/expanduser references (grep empty). No selftest covers clean_env.

## Commands / evidence
- Mutants: scratch `$S/mut/<name>/c1-counter.py`, diffs printed by my build step; py_compile/ast.parse rc=0 each.
- Selftest logs: seat `S69MutTester.logs/selftest-*.txt`; battery logs: `S69MutTester.logs/battery-*.txt`; mutant sources: `S69MutTester.logs/mutant-*.py`.
- Tools installed: none (no installs or upgrades; no pacman).

## Files written
- .ufo/waves/round-69/w1/S69MutTester.md (this file)
- .ufo/waves/round-69/w1/S69MutTester.logs/ (24 files: selftest-*.txt, battery-*.txt, mutant-*.py)
- Scratch under /fast/scratch/hyaku/souji-r69/S69MutTester/m-1978295 (removed after copy).
