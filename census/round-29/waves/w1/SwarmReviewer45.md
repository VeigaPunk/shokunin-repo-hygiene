# SwarmReviewer45 — defect disposition (r29 w1)

## Status

STATUS: PASS — all six routed defects disposed with located evidence; 4 addressed by a claim/item, 1 (defect 3) is unclaimed and given the minimal honest report handling plus the cited gate code for a next-round pointer, 1 (defect 6) is addressed only in prose with no counter. Two counter gaps reported as attacks.

## Evidence

Base revision `691dd29211c53d0ef94fa072394cb9c8a69fe92e` (prereg commit `b8cb4b31ce80e2e3314b88e85d40ea9873180804`). All runs lane-local, `python3 -B`, read-only.

| # | command | observed |
|---|---|---|
| E1 | `python3 -B tools/souji-registry-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 691dd29… --list-rev b8cb4b3…` | `K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md`, 5×K1 cited-not-in-used-by, `K2 uncorrected LOG.md:1758` + `SCORECARD.md:23` + `round-28.md:22` + `:40`, `SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29…`, rc 1 |
| E2 | `python3 -B census/round-29/c2-counter.py --root … --rev 691dd29…` | `r26 records=1382 failed=152 uncovered=14 floor_violation=0`, r27/r28 clean, `SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0`, rc 1 |
| E3 | `python3 -B tools/souji-landing-gate.py --root … --rev 691dd29… --round 28 --fleet-root /home/vgpnk/Projects/shokunin` | `SUMMARY findings=3 checked_reg=52 checked_pins=13 checked_markers=0 status_lines=0 carry_heading=0 checked_reports=0`; `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-28/ at 691dd29211c5`; rc 2 |
| E4 | `python3 -B tools/souji-coverage-agreement.py --root … --rev 691dd29…` | `grounded=13 mapped=13 dangling=0 mismatches=0`, rc 0 (equals prereg's quoted base) |
| E5 | `python3 -B tools/souji-axis-check.py --prereg census/round-29/records/preregistration.txt --scorecard SCORECARD.md` | `claims=3 flags=0`, rc 0 |
| E6 | `git -C … ls-tree -r --name-only 691dd29… -- census/round-28/waves` / `-- .ufo/waves/round-28` | 76 files, of which 61 `waves/w1/*.md`; 0 files under `.ufo/waves/round-28` |
| E7 | `ls .ufo/waves/round-28/w1/*.md \| wc -l` | 61 (capture is report-complete for r28) |
| E8 | `cat -n .gitignore` | 1 `.ufo/waves/`, 2 `census/operator-sweep-*/`, 3 `__pycache__/` |
| E9 | `grep -n 'check-ignore\|ls-files\|ignored' tools/souji-wave-evidence-capture.sh` | 0 matches (203-line base tool never consults git's ignore rules) |
| E10 | `grep -n 'R29-CORRECTION' tools/souji-registry-agreement.py` | line 96: `any(x.startswith('R29-CORRECTION ') and tag in x for x in lines[ln:])` |
| E11 | `ls /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/operator-*.md` | `No such file or directory`, rc 2 |
| E12 | `find /home/vgpnk/Projects/shokunin/souji-shokunin -iname '*operator*' -not -path './.git/*'` | 9 hits, none in `corpus/lessons/`: `./census/operator-sweep-20261018`, `./census/operator-sweep-20261019`, `./census/round-16/transcripts/w1/DraftOperatorQuestion.txt`, `./census/round-16/transcripts/w2/DraftOperatorQuestion2.txt`, `./census/round-3/operator-approval-list.tsv`, `./.ufo/waves/round-13/w1/SafetyOperator.md`, `./.ufo/waves/round-16/w1/DraftOperatorQuestion.md`, `./.ufo/waves/round-16/w2/DraftOperatorQuestion2.md`, `./.ufo/waves/round-17/w1/RevOperatorSweepFp.md` |
| E13 | `grep -cE '^\| Q6[0-9] \|' corpus/QUALITY.md`; `ls corpus/lessons/round-29.md` | `0`; `No such file or directory` (QUALITY.md stops at Q59, line 143) |
| E14 | `git ls-tree -r --name-only 691dd29… -- census/round-29/waves` | empty — the r29 receipt is post-landing |

## Findings

1. **Defect 3 is unclaimed and the landing gate is not merely "unevaluable" — it is red at base.** Same run as E3 also emits three `LG-DANGLING-PTR` findings created by the r28 spot-check lesson itself: `.ufo/waves/round-28/` (lesson:34, a quoted gate message), `corpus/knowledge/registry` (lesson:36, a quoted grep pattern), and `census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:fixture/` (lesson:71, a path carrying an inline locator). No claim or wave item edits `tools/souji-landing-gate.py` (grep of `.ufo/waves/round-29/make-spec.py` for `landing-gate` returns only `BaselineGates:49` and `PreReportGateReadiness:54`, both documentation-only), so the round report must quote `findings=3` and must not claim a clean gate. Location: `tools/souji-landing-gate.py:1153-1165` for the SUMMARY shape, `:1138` for `exit = 2 if error`; `corpus/lessons/round-28-verifier-spotcheck.md:34,36,71`.

2. **Report discovery is hardcoded to the gitignored tree.** `check_carry` builds `prefix = ".ufo/waves/round-%d/"` at `tools/souji-landing-gate.py:469`, filters `p.startswith(prefix) and p.endswith(".md")` at `:470-472`, and raises `EvalError("no .md reports under %s at %s")` at `:474`; the caller swallows that for `round_no >= 18` at `:1118-1126` and leaves `checked_reports=0 / carry_heading=0`, with rc 2 from `:1138`. With `.gitignore:1` = `.ufo/waves/` and 0 tracked files under `.ufo/waves/round-28` (E6), the carry channel can never evaluate — permanently, not just this round. The CLI (`:2283-2289`) offers `--root --rev --round --base --fleet-root --json --selftest` and no prefix/fallback option.

3. **Pointing the gate at `census/round-N/waves/` next round is feasible and already report-complete for r28.** 61 `.md` reports are committed under `census/round-28/waves/w1` at base, equal to the 61 on disk (E6, E7), and the capture copies byte-exact contents (`tools/souji-wave-evidence-capture.sh:7-8`), so `seat_failure_lines` / `status_line_count` would see the same bytes. Two conditions must hold: (a) the capture is post-run — `census/round-29/waves` is absent at base (E14), so only a completed round is evaluable; (b) it is honest only after C2 makes the capture complete, otherwise `checked_reports` silently undercounts — the same silent-exclusion class defect 3 is about. Minimal change is a prefix parameter at `:469` (default unchanged), not a rewrite.

4. **K2 accepts a content-free correction marker.** `tools/souji-registry-agreement.py:96` requires only a line starting `R29-CORRECTION ` that contains the `file:line` tag; nothing binds the correction to the observed facts. The lane's own junk control already demonstrates it: `census/round-29/records/controls.tsv` `C1-junk1(markers only)` prints `k2=0`. So `k2=0` closes defect 2 only if the landed correction text states 152 absent records of 1382 and the GNU-escape finding; the counter cannot show that. Location: `tools/souji-registry-agreement.py:96,119`.

5. **Defect 6 is prose-only with no counter.** `corpus/lessons/round-29.md` does not exist and `QUALITY.md` has no Q6x row at base (E13), while the frozen C1/C2/C3 targets contain no observable over the lesson. The row exists in the plan (`make-spec.py:67`, `MistakesRows` row (c): "captured-by none (Q58 covers target derivation, not exclusion reading); fix = Q60") and Q60 is drafted by `QualityCriteria:66` and proven failable by `QCriteriaRedBefore:55`, but closure will rest on reading the lesson. Recommend the landed row carry the two numbers (frozen clause excludes S215; closure verified 138 vs the lane self-ruled 139) so one `git grep` can spot-check it.

6. **Defect 4 is satisfied, with a low-severity shape imprecision.** The prereg quotes each counter's own output and the base literals reproduce exactly (E1, E2, E4, all equal `controls.tsv`); `axis-check` is clean (E5). But the C1/C2 shapes are quoted without the trailing `rev=<full40>` field both tools print (`tools/souji-registry-agreement.py:119`; `census/round-29/c2-counter.py` SUMMARY line), so "the counter's own shape" is a prefix rather than verbatim. No action required; noted for next round's Q58 rows.

7. **Defect 1's observable is weaker than its statement.** `c2-counter.py` reads `manifest.sha256`, `symlinks.tsv` and the tree; it never reads `excluded.tsv` (stated in C2's predicate, prereg line 6). `failed=0 uncovered=0` therefore cannot distinguish "accounted as excluded with source sha256" from "silently dropped"; that evidence lives only in the v2 tool's `excluded.tsv` plus its `--verify --rev` mode. The base tool has no git-ignore consultation at all (E9), and the fixture is at `cases=6` (`tests/fixtures/r28-wave-evidence-capture.sh:6,149`), so a pass on the frozen counter alone would not close routed defect 1 as worded.

8. **No `operator-*.md` teaching file exists in `corpus/lessons/`.** Sweeps E11/E12: zero matches; the nine operator-named artifacts elsewhere are census/wave transcripts and one approval list, none a lesson, so there is no unreflected operator teaching to fold into QUALITY.md or SKILL.md from that directory.

## Attack log

A1 (C1, defect 2). Reach `k2=0` with no true statement: append a single line `R29-CORRECTION LOG.md:1758` to each file. Passes `:96`; the do-nothing/junk pair in `controls.tsv` already shows the mechanism (`markers only` → `k2=0`). Stricter-only fix: require the marker line to also contain the literal `152` and `1382`, or the sha256 of the committed r26 manifest.

A2 (C2, defect 1). `failed=0 uncovered=0 floor_violations=0` is reachable while capture evidence is lost, because the counter reads none of `excluded.tsv`. Any capture that routes dropped files into `excluded.tsv` scores clean. Counter-side fix must read `excluded.tsv` and require a source sha256 per row (this is `AttackC2`'s mandate; recorded here because defect 1's closure claim depends on it).

A3 (C1/defect 3, gate pointer). Pointing `check_carry` at `census/round-N/waves/` creates a circularity: the receipt is produced by the same tool whose completeness C2 measures, and a capture that under-collects reports would lower `checked_reports` silently instead of failing. Honest form: keep the prefix default, add an explicit `--wave-prefix`, and require the capture's `summary.tsv` seat count to equal the report count scanned before the carry channel is treated as green.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-defect-disposition.tsv` (6 rows × 8 columns: defect, routed_statement, addressed_by, addressed, observable_command, base_observation, residual_and_handling, location)
- `.ufo/waves/round-29/w1/SwarmReviewer45.md` (this report)

No scratch repository was created; nothing outside these two files was written. No tool installs.
