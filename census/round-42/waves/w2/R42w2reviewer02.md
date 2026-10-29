# R42w2reviewer02 — fact-check of `corpus/lessons/round-42.md` `## Mistakes` (M42-1..M42-6), the Q103–Q105 rows, and the preregistration misstatements

Seat: R42w2reviewer02 (reviewer, leaf, no subagent dispatch). Judged on: calibration.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Landed tip attacked: `3105a63b23481fccf7df58e74d14a6681e0ea0c8`. Base `bf618f6c5c09d302994871c94903abbea2deb60d`. Freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`. Instruments commit `b7408095543579ac71b33ecf7b80b0cb8ef45036`.

Receipts (seat directory, all commands and their verbatim output):
- `.ufo/waves/round-42/w2/R42w2reviewer02/receipts/reproduce.sh` — the script that runs every command in this report (scratch clones under a seat scratch dir, toplevel asserted before every clone mutation, removed on exit).
- `.ufo/waves/round-42/w2/R42w2reviewer02/receipts/reproduce.txt` — its output (292 lines, `SCRIPT_RC=0`).
- `receipts/c3-counter-tip-run-bg-8of8.txt`, `receipts/c3-counter-tip-run-2-8of8.txt` — two full C3 counter runs at the tip (both `prior=8/8`).

Scratch: `/fast/scratch/hyaku/souji-r42/R42w2reviewer02/` removed before yield. No tool installed or upgraded. Nothing written to the lane, the fleet, `.ufo/state`, or any tracked file. Temporary files under `/tmp` were removed. Evidence pointers below are to committed paths or to this seat directory.

## Verdict

**Calibration: MISSES — the numbers mostly reproduce, but the lesson's Mistakes section carries several material misstatements, and two of them change the stated meaning of the round's own gate evidence.**

What reproduces: the declared-evidence counts at base, at the r22/r23/r24/r25/r30/r35/r38 tips and at r41 (M42-1); the gate readings in both modes at base, at both repoint commits and at the r41 and landed tips (M42-2 numbers); the C1 counter at the tip and its do-nothing and forged controls; the blank-line sentinel (`rewritten=1` for a non-blank base append, `rewritten=0` for a blank-prefixed one); the seven-mutant prior-fixture survey table; every CORRECTION-DE digest except one revision label; the CORRECTION-SC header revisions; the S259 snapshot and its two line locations.

What does not: the points the lesson uses as its *evidence* for the three Mistakes that matter most:

1. **M42-2 / Q103 — the "green in one mode" R1 repair did not exist.** The literal three-row candidate that scored `findings=0 … rows_added=3` is malformed under the loader: the gate exits 2 with a zeroed `SUMMARY findings=0` in **both** modes (`COULD-NOT-EVALUATE … malformed exemption row`). The frozen R1 counter reads that zeroed line as a pass. No loader-admissible exemption set reads green in plain mode.
2. **M42-3 — the round's own appends were never measured at the landed tip.** `census/round-42/records/c1-after.txt` measures `34e33a6`, the revision *before* the SCORECARD/LOG append (its header says so). The lesson's fix sentence cites it as the measurement of the appends.
3. **M42-1 / Q104 — the round did not run the instrument at its own tip.** At `3105a63` the instrument reads `assertions=490 resolved=420 skipped=810 mismatches=70`. No committed file quotes that line (`git grep` finds none). Q104 requires exactly that quote.
4. **M42-5 — the attribution errors are wrong in kind, not wording**: "committed at `410316c`" for `controls/c1-control.txt` is false (the cited `git show` fails); "four receipts were added" is three; and two prereg Target strings and the instrument-commit sentence are also wrong.
5. **M42-4 — the survey pointer and the "13 left" count are wrong, and the F1 claim is not reproduced.** The 7-mutant survey lives in `records/survey-prior.txt`, not `controls/c3-control.txt`; of the 17 G-class mutants 12 survive, not 13 (the 13th population mutant is D4); F1 is killed by no fixture in the survey or in three direct runs.

Q103–Q105 are assessed in §4. Q103 cites the right M-id but its motivating sentence is the wrong fact (item 1) and the lesson itself quotes an abbreviated `--rev` (Q103 requires 40 hex). Q104 cites the right M-ids, but the round does not satisfy the row's own check (items 2–3). Q105 cites the right M-id and is satisfied in the lesson, with one attribution slip (`-P`).

## 1. Claim table

Columns: claim | command | reproduced? | note. "Script" = `receipts/reproduce.sh`, output in `receipts/reproduce.txt` (section named).

| # | claim (where) | command | reproduced? | note |
|---|---|---|---|---|
| 1 | base counts `assertions=474 resolved=404 skipped=780 mismatches=70` (M42-1 pointer, lesson:110–113) | `python3 -B tools/souji-declared-evidence.py --root . --rev bf618f6c5c09d302994871c94903abbea2deb60d --file SCORECARD.md --format counts` (Script §M42-1) | YES | exact |
| 2 | r22 tip `63/63/40/0` (M42-1 "r22 attempt 2 … mismatches=0") | same at `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` and at `9301d98c1c689c79741f0f1ba1f171138d20af07` (SCORECARD tip record) | YES | both give `63 63 40 0` |
| 3 | first nonzero at the r23 tip (M42-1) | same at `d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7` | YES | `82 80 69 2` exit 1 — matches scout table |
| 4 | rising sequence r24–r38 (scout04 table, cited by M42-1) | same at a6d2d157 (13), 0eca7c8a (15), 9f17a1ef (21), 94b5e96a (30), ed30b7f5 (52) | YES | all match |
| 5 | r41 tip reads 70 (M42-1) | same at `0c9581a44a2e` | YES | `474 404 780 70` |
| 6 | round tip count quoted (Q104 check) | same at `3105a63`; `git grep -n -E 'resolved=420\|assertions=490\|skipped=810' 3105a63 -- .` | **YES, absent** | instrument reads `490 420 810 70`; no committed quote of it; lesson grep for `assertions=` finds only the base line (Script §M42-1) |
| 7 | gate plain `findings=3`, fleet `findings=0` at base (M42-2, Q103 motivation) | `tools/souji-landing-gate.py --root . --rev bf618f6c… --round 41` [± `--fleet-root /home/vgpnk/Projects/shokunin`] | YES | the three findings are `corpus/README.md:217` ×2, `corpus/knowledge/jj-colocation-receipts.md:148` |
| 8 | r41 tip gate same as base (M42-2 "findings=3" at r41) | same at `0c9581a44a2e` | YES | `3` plain / `0` fleet |
| 9 | repoint `e95b13b` (not in lesson) | same at `e95b13beb5b690f0bf80034c12c1ac7b6650bb45` | YES, new | plain `findings=2` (directory-row wording); fleet `0`. The wording token was removed in `51f204f` |
| 10 | repoint `51f204f` both modes `findings=0` (M42-2 fix) | same at `51f204fb7c633b691a3ca9cd8c0bf025f6e0a093` | YES | `0` / `0` |
| 11 | landed tip both modes `findings=0` | same at `3105a63…` | YES | `checked_reg=113` (tip) |
| 12 | "frozen exemption repair read green in one mode and `findings=2` in the other" (M42-2, Q103) | clone at tip with the literal three `../`-spelled rows; `tools/souji-landing-gate.py` both modes (Script §M42-2 correction) | **NO** | both modes `COULD-NOT-EVALUATE corpus/pointer-exemptions.tsv:5 malformed exemption row`, exit 2, zeroed `SUMMARY findings=0` |
| 13 | frozen R1 counter scores that candidate as green | `bash census/round-42/score-candidate.sh r1 <scratch> corpus/pointer-exemptions.tsv=<literal rows>` | YES (as a pass-through) | `SUMMARY findings=0 deleted=2 rows_added=3 stale=0`, counter rc 1 only because `deleted=2` is the repoint's deleted lines in the clone's HEAD (scoring clones HEAD, not base). Counter never reads the gate's exit code (`census/round-42/r1-counter.py`, the `gate = subprocess.run(…)` block) |
| 14 | loader-admissible variant (`.ufo/waves/hyaku/…` spelling) reads `findings=2` with fleet (M42-2 "findings=2") | clone at base with the variant rows; both modes | YES, but corrected | plain `findings=4` (`LG-DANGLING-PTR` ×2 + `LG-DANGLING-PTR-EXEMPT-STALE` ×2), fleet `findings=2` (the two STALE rows). Not green in plain mode either |
| 15 | frozen R1 counter at tip `findings=0 deleted=2 rows_added=0 stale=0` (M42-2) | `python3 -B census/round-42/r1-counter.py --root . --rev 3105a63… --scratch <dir>` (run at the tip, not in script) | YES | red by its letter, as stated |
| 16 | C1 counter at tip `items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` (M42-3, Q104) | `python3 -B census/round-42/c1-counter.py --root . --rev 3105a63… --scratch <dir>` (Script §M42-3) | YES | rc 0 |
| 17 | control A at the instruments commit `registered=0 class_ok=0` (M42-1 fix) | same at `b7408095…` | YES | rc 1 |
| 18 | forged register `class_ok=42` (M42-1 fix) | `score-candidate.sh c1 … census/round-42/c1-register.tsv=census/round-42/controls/c1-forged-register.tsv` | YES | `class_ok=42` |
| 19 | non-blank append to base SCORECARD → `rewritten=1` (M42-3) | `score-candidate.sh c1 … SCORECARD.md=<base + "| probe …" with no leading newline>` | YES | `rewritten=1 new_mismatches=0` |
| 20 | blank-prefixed append to base → `rewritten=0` (M42-3) | same with a leading `\n` | YES | `rewritten=0 new_mismatches=0` |
| 21 | non-blank append to the **landed tip** SCORECARD → `rewritten=0` (not in lesson) | `score-candidate.sh c1 … SCORECARD.md=<tip + non-blank row>` | YES, new | the tip already carries the blank at line 840 (the round's own blank-prefixed append), so the sentinel does not fire |
| 22 | bad row at line 840 (first line past base, no blank prefix) → `new_mismatches=0` (not in lesson; N-C1c) | `score-candidate.sh c1 … SCORECARD.md=<base + "`no/such/path`" row, no newline>` | YES, new | `rewritten=1 new_mismatches=0`: the `> 840` threshold does not see line 840. Red only through `rewritten` |
| 23 | bad row at line 841 (blank-prefixed) → `new_mismatches=1` (not in lesson) | same with two leading `\n` | YES, new | `rewritten=0 new_mismatches=1` |
| 24 | `c1-after.txt` measured the round's SCORECARD/LOG appends (M42-3 fix) | read `census/round-42/records/c1-after.txt` line 1–2 | **NO** | header: `measurement at 34e33a66… (L1; the SCORECARD/LOG rows of this round are not yet appended)` — measured before the append |
| 25 | C1 CORRECTION-DE line 14 digest `65817d0d…` is a truncated tool digest (SCORECARD:14 / lesson) | `git log -- tools/souji-declared-evidence.py` blob sha loop (Script §C1) | YES | the full digest `65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4` is the sha256 of a committed blob (4a6ee90a…); the commit is not named by the lesson |
| 26 | line 92 `09bb8e0d` = sha256 of `tools/souji-size-census.py` at `778747eb` | `git show 778747eb…:tools/souji-size-census.py \| sha256sum` | YES | `09bb8e0d9906…ed6d` |
| 27 | line 68 `42259756` = fixture at `1efe406`; `71b89eb3` = tool at `1efe406`; `bb506469` = base tool | three `git show … \| sha256sum` | YES | all three digests match |
| 28 | line 68 "first `bb506469…` revision `604cd441`" | `git show 604cd441:tools/souji-coverage-agreement.py \| sha256sum`; `git merge-base --is-ancestor 604cd441 <base>` | **NO** | `604cd441` has the digest but is not an ancestor of the base (rc 1). In base history the blob first appears at `7e4dbef94061578fca2f58621f87908c886cc431` (ancestor rc 0; `round-25: C1 base-grounded kill-rule instrument…`) |
| 29 | line 175 `c2-after.tsv` matches five committed paths (`census/round-24..28/records/c2-after.tsv`) | `git ls-tree -r --name-only <base> \| grep '/c2-after.tsv$'` | YES | exactly five |
| 30 | SCORECARD:697 header revisions `6949319e` (c2-after4, c3-after3) and `9b443200` (a7-counter-fixes) | `git show <base>:census/round-38/records/…` head -1 | YES (3 of 5 receipts checked) | the other two receipts of the sentence not checked |
| 31 | S259 snapshot sha256 `620581fe…`; `sitecustomize` sentence at lines 418–419; `-S` sentence at 227–228 | `sha256sum`; `grep -n` (Script §M42-6) | YES | the located quote spans HTML tags on the served line, so it does not grep verbatim. Meaning matches |
| 32 | SOURCES 182 → 183 rows, S259 one row (lesson Gate / SCORECARD) | `git grep -c '^\| S259 '`; `git grep -c '^\| S' <tip>` (Script §C1) | YES | `1` and `183` |
| 33 | census start `rows=182 W04=52` (preregistration "Frontier step") | `head -4 census/round-42/records/census-before.txt` | YES | |
| 34 | freeze commit adds "c2-cases.tsv and the five control receipts" (prereg:5) | `git show --name-status afe17f4 -- census/round-42/controls census/round-42/c2-cases.tsv` (Script §M42-5) | **NO** | A: `c2-cases.tsv`, `c2-control.txt`, `c3-control.txt`, `r1-control.txt`; M: `c1-control.txt`. Four control receipts exist in all, three added at the freeze |
| 35 | "four receipts were added" (lesson M42-5) | same | **NO** | three added; `c1-control.txt` modified |
| 36 | `controls/c1-control.txt` committed at `410316c` and rewritten in place at `b740809` (lesson M42-5) | `git show 410316c:census/round-42/controls/c1-control.txt` (Script §M42-5) | **NO** | `fatal: path … exists on disk, but not in '410316c'`. First added at `b740809` (scored at 410316c: `registered=62 class_ok=34`), rewritten at the freeze commit `afe17f4` (`class_ok=42`) |
| 37 | "every Counter … is the blob at its adding commit" is false for `c1-counter.py` (lesson M42-5) | `git show <rev>:census/round-42/c1-counter.py \| sha256sum` at 3105a63, b740809, 410316c | YES | frozen `0ab07cd3…` = blob at b740809; 410316c blob `5e07eda1…` |
| 38 | C2 Target omits `tool_sha=` (lesson M42-5) | `census/round-42/records/c2-after.txt` line 44 (measured at `5ad7046`, not re-run at the tip): `SUMMARY cases=37 … patches=3/3 tool_sha=9ddd596b98fb`; prereg:30 | YES (receipt) | the counter prints `tool_sha=`; the C2 Target does not |
| 39 | C3 Target ends `(exit 0)` and omits `cases=` and `tool_sha=` (not in lesson) | prereg:41 vs C3 counter output `… anchors=ok cases=13 tool_sha=b2a603cf4247` (saved receipts) | YES, new | `(exit 0)` is not printed by any counter |
| 40 | R1 Target ends `(exit 0)` (not in lesson) | prereg:51 vs r1-counter print statement | YES, new | the counter prints no exit suffix |
| 41 | prereg:5 instruments commit `b740809` "adds counters, c1/c3 populations, pinned tool" (not in lesson; connector P8) | `git log --diff-filter=A` for `census/round-42/{c1-items.tsv,c3-mutants.tsv,c2-counter.py,c3-counter.py,r1-counter.py,c1-counter.py}` → 410316c; `git show --name-only b740809` → only `c1-counter.py`, `controls/c1-control.txt`; `tools/souji-worktree-drift.py` added at `42ea92e` | YES, new | the counters and populations were added at 410316c; b740809 edits `c1-counter.py` only; the pinned tool is older |
| 42 | prereg:56 census receipt "committed at the instruments commit" (not in lesson; connector P8) | `git ls-tree -r --name-only 410316c census/round-42/` | YES, new | `census-before.txt` is in 410316c |
| 43 | lesson M42-5 header "six small misstatements" | count the enumerated items in M42-5 | **NO** | three are enumerated in the lesson |
| 44 | C2 selftest 31 cases (lesson Gate) | not re-run (not in the M42 scope; receipt `census/round-42/records/c2-after.txt`) | not run | |
| 45 | C3 survey: D3, F2 killed by `r38-drift-write-envelope`; H3, N1 by r36/r37/r40/r41-record-order; J5 by r41-record-order; T2 by r40/r41-record-order; F1 by none (M42-4) | `census/round-42/records/survey-prior.py --lane . --scratch <dir>` (Script §M42-4) | YES | identical to `records/survey-prior.txt` |
| 46 | the survey is in `controls/c3-control.txt` (M42-4 evidence pointer) | `grep -n 'MUTANT D3\|T2' census/round-42/controls/c3-control.txt` | **NO** | `c3-control.txt` prints `prior=` only for the 13 population mutants and 6 equivalents. The 7-mutant survey is `records/survey-prior.txt` |
| 47 | "the 13 left survive all eight" (M42-4) | survey + C3 tip runs (`prior=-` on all 13 population mutants in both saved runs) | **PARTLY** | of the 17 G-class mutants 12 survive (E2 E4 B1 J9 G2 G3 G4 G5 H1 H2 I1 M1); the 13 population mutants are those 12 plus D4 (M40-12), which is not from the 17 |
| 48 | pristine prior fixtures `cases … fail=0` (prior=8/8) | each of the eight fixtures against the pristine tool at the tip (Script §M42-4) | YES | `12, 6, 10, 12, 7, 8, 12, 21 probes` all pass; `rc 0` |
| 49 | F1 killed by `r36-worktree-drift.py` (M42-4; prereg "F1 is killed by r36") | survey (row 45) + three direct runs of r36 against the F1 mutant (Script §M42-4) | **NO** | `SUMMARY cases=12 pass=12 fail=0` in all four runs. The lesson's "L1's first survey run" kill has no committed receipt, so the "load-sensitive flake" explanation is unestablished |
| 50 | C3 counter at tip `mutants=13 killed=13 survived=0 pristine=ok prior=8/8 …` | `python3 -B census/round-42/c3-counter.py --root . --rev 3105a63… --scratch <dir>` (~200 s each; saved outputs) | YES in 2 of 3 runs | one of three full runs read `prior=7/8` (transcript only; the output was not saved); the two saved runs read `8/8`. See named limit L-C3-prior |
| 51 | C2 freeze check at freeze `claims=3 findings=0` (lesson Gate) | `python3 -B tools/souji-freeze-check.py --root . --prereg census/round-42/preregistration.txt --rev afe17f4…` (Script §C2) | YES | |
| 52 | r1 Target `SUMMARY findings=0 deleted=0 rows_added=3 stale=0` as a repair (prereg Target, M42-2) | row 12 | **NO** | a reached target by a could-not-evaluate gate (row 12) |
| 53 | M42-6 "docs 3.15.2, host 3.14.8; `-I`/`-E`/`-S` unpatched" (S259 scope) | `census/round-42/waves/w1/R42scribe07/receipts/python-startup-probe.txt` (read) and `R42sentinel02.md` premise table | YES | M42-6 attributes `-P` to the scribe07 receipt; that receipt covers `-B -I -S -E -s` only. `-P` is in the sentinel02 premise table (`python3 -P -B` → yes) |
| 54 | Q103 "the receipt block carries … a full40 `--rev`" | read lesson M42-2 pointer | **NO** | M42-2 writes `--rev bf618f6… --round 41`, abbreviated |
| 55 | N-C1c `new_mismatches` threshold `> 840` (named limit) | row 22 | YES | consequence not stated in the lesson: a bad row on line 840 is not counted by `new_mismatches` |
| 56 | r1-counter ignores the gate's exit code (named limit missing from the lesson; scout03 finding) | read `census/round-42/r1-counter.py` gate block; row 12 | YES | not in the lesson's named limits |

## 2. Misstatements and the corrected text to append

Each entry gives where the wrong text is, what was measured, and the text to append (the lesson and the prereg are frozen or append-only; these are append-only errata).

**E1 — M42-2 (and Q103 motivating text): the "green in one mode" repair.**
- Wrong: "R42scout03 measured the frozen R1 repair (three `corpus/pointer-exemptions.tsv` rows): green without `--fleet-root` and `findings=2` with it"; "the frozen R1 predicate was wrong (it trades the fleet-root mode for the plain mode)"; Q103 "the frozen exemption repair read green in one mode and `findings=2` in the other".
- Measured (rows 12–14): the literal `../`-spelled three-row candidate is malformed; both modes exit 2 with zeroed `SUMMARY findings=0` (`COULD-NOT-EVALUATE`). The frozen R1 counter scores that as `findings=0 … rows_added=3`. The loader-admissible `.ufo/`-spelled variant reads `findings=4` plain and `findings=2` fleet. Exemption rows cannot reach the two `../` pointers in either mode (the loader rejects `..` components).
- Append: "Erratum (r42 review): the 'green without `--fleet-root`' reading of the R1 candidate was a could-not-evaluate run (`COULD-NOT-EVALUATE corpus/pointer-exemptions.tsv:5 malformed exemption row`, exit 2, zeroed `SUMMARY findings=0`). Both modes of the literal three-row candidate are exit 2; the frozen R1 counter scores the zeroed line as a pass because it does not read the gate's exit code (named limit below). A loader-admissible spelling (`.ufo/waves/hyaku/jj-w1/reports/…`) reads `findings=4` without `--fleet-root` and `findings=2` with it (`LG-DANGLING-PTR-EXEMPT-STALE`). No exemption set reads green in plain mode. The repoint (`51f204fb7c63…`) is the only green reading in both modes. Q103's motivating evidence is corrected accordingly."

**E2 — M42-2 (Q103 check): abbreviated revision.**
- Wrong: "`python3 -B tools/souji-landing-gate.py --root . --rev bf618f6… --round 41` prints `findings=3`".
- Append: "Full revision: `--rev bf618f6c5c09d302994871c94903abbea2deb60d --round 41` (Q103 requires the full 40-hex revision)."

**E3 — M42-2 (named limit missing).**
- Append: "Named limit (r42 review): `census/round-42/r1-counter.py` reads the gate's `SUMMARY` line and never its exit code or stderr; a could-not-evaluate gate (exit 2, zeroed `SUMMARY findings=0`) scores as `findings=0`. The R1 target is therefore not a measurement of the gate until that is repaired (frozen; reported, not edited)."

**E4 — M42-3: the round's appends were not measured at the landed tip.**
- Wrong: "the round's SCORECARD/LOG appends were landed blank-prefixed and measured (`census/round-42/records/c1-after.txt`)".
- Measured: `c1-after.txt` is at `34e33a662cd0d6931e5aa006bd90364e7852c0d5`, before the append (its header says "the SCORECARD/LOG rows of this round are not yet appended"). The landed tip measures `items=70 … rewritten=0 new_mismatches=0` (row 16, `receipts/reproduce.txt` §M42-3). Also the blank-prefix convention is what keeps `rewritten=0` at the tip (row 21).
- Append: "Erratum (r42 review): `census/round-42/records/c1-after.txt` measures `34e33a6…`, the revision before the SCORECARD/LOG append in `3105a63`. The landed tip measures `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` at `3105a63b23481fccf7df58e74d14a6681e0ea0c8` (`.ufo/waves/round-42/w2/R42w2reviewer02/receipts/reproduce.txt` §M42-3)."

**E5 — M42-3 (named limit N-C1c, consequence not stated).**
- Append: "Named limit (r42 review): a bad row written to line 840 (the first line past the base, with no blank prefix) reads `rewritten=1 new_mismatches=0`; the `> 840` threshold does not count it. The red comes only from `rewritten`. A blank-prefixed bad row (line 841) reads `new_mismatches=1`."

**E6 — M42-1 / Q104: the instrument count at the round's own tip.**
- Wrong (by omission): the lesson quotes the counts at base only; the round's own tip is not quoted.
- Measured: `3105a63` reads `assertions=490 resolved=420 skipped=810 mismatches=70` (row 6). The C1 register accounts for the 70 for the counter; the instrument still reports 70 at the tip, because it does not read CORRECTION lines.
- Append: "Erratum (r42 review): at the landed tip `3105a63b23481fccf7df58e74d14a6681e0ea0c8` the instrument reads `python3 -B tools/souji-declared-evidence.py --root . --rev 3105a63… --file SCORECARD.md --format counts` → `assertions=490 resolved=420 skipped=810 mismatches=70`. The 70 are still reported by the instrument; the register accounts for them for the C1 counter only."

**E7 — M42-1: "no round re-running the instrument".**
- Wrong: "R42scout04's sweep … with no round re-running the instrument" (and the stronger "no committed receipt" reading is correct).
- Measured: `corpus/lessons/round-31-verifier-spotcheck.md:120` (read at base) says "`souji-declared-evidence` reads 21 mismatches at both base and tip (SwarmExecutor27)". That is a run claim in prose with no committed receipt.
- Append: "Erratum (r42 review): no committed receipt records the instrument's counts at any round tip from r24 to r41. `corpus/lessons/round-31-verifier-spotcheck.md:120` reports `21 mismatches at both base and tip` in prose (no receipt). The M42-1 claim is about receipts, not about runs."

**E8 — M42-4: survey pointer and the "13 left".**
- Wrong: the survey is at `census/round-42/controls/c3-control.txt`; "the 13 left survive all eight" for "the 17 G-class mutants".
- Measured: the 7-mutant survey is `census/round-42/records/survey-prior.txt` (row 45, 46). Of the 17 G-class mutants, 12 survive (E2 E4 B1 J9 G2 G3 G4 G5 H1 H2 I1 M1); the population's 13th mutant is D4 (M40-12).
- Append: "Erratum (r42 review): the seven-mutant survey (D3 F2 H3 J5 N1 T2 F1) is `census/round-42/records/survey-prior.txt` (`records/survey-prior.py`), not `controls/c3-control.txt`, which prints `prior=` only for the 13 population mutants and 6 equivalents. Of the 17 G-class mutants, five are killed by an older fixture (D3, F2 by `r38-drift-write-envelope`; H3, N1 by r36/r37/r40/r41-record-order; J5 by `r41-drift-record-order`); twelve survive all eight. The 13 population mutants are those twelve plus D4 (M40-12)."

**E9 — M42-4: F1.**
- Wrong: "F1 … was killed by `r36-worktree-drift.py` in the L1's first survey run (under a loaded host)"; the prereg sentence "F1 is killed by r36".
- Measured: no committed receipt of the first run. F1 is killed by no fixture in `survey-prior.txt`, and three direct runs of `r36-worktree-drift.py` against the F1 mutant read `cases=12 pass=12 fail=0` (rows 45, 49).
- Append: "Erratum (r42 review): F1 is killed by no committed prior fixture (`records/survey-prior.txt`: `killed-by-prior-fixtures=-`). Three direct runs of `r36-worktree-drift.py` against the F1 mutant also read `pass=12 fail=0`. The earlier kill has no committed receipt; a fixture flake is not established. F1 is in neither population, so no verdict changes."

**E10 — M42-4 / named limit L-C3-prior (new).**
- Append: "Named limit (r42 review): the C3 counter's `prior=8/8` leg is timing-sensitive, not only `old_killed`. One of three full runs at the tip read `prior=7/8` (the output was not saved; the transcript line reads `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=7/8 old_killed=0 …`). The other two full runs read `8/8` (`receipts/c3-counter-tip-run-*.txt`). Six concurrent isolated runs of the eight prior fixtures were clean. The Target is therefore not reproducible under load as written; the cause is not isolated."

**E11 — M42-5: the control receipts.**
- Wrong: "four receipts were added by the freeze commit"; "`controls/c1-control.txt` was committed at `410316c` and rewritten in place at `b740809` after the duplicate-token fix"; "M42-5 … carried six small misstatements".
- Measured: row 34–36. Three control receipts were added at the freeze (`c2-control`, `c3-control`, `r1-control`); `c1-control.txt` was first added at `b740809` and rewritten at `afe17f4`; `git show 410316c:…` fails.
- Append: "Erratum (r42 review): the freeze commit `afe17f4` adds `census/round-42/c2-cases.tsv`, `controls/c2-control.txt`, `controls/c3-control.txt`, `controls/r1-control.txt`, `preregistration.txt`, and modifies `controls/c1-control.txt`. There are four control receipts (c1, c2, c3, r1), not five. `controls/c1-control.txt` was first added at `b740809` (scored at `410316c`: `registered=62 class_ok=34`) and rewritten at `afe17f4` (scored at `b7408095…`: `registered=70 class_ok=42`). `git show 410316c:census/round-42/controls/c1-control.txt` fails: the path is absent at `410316c`."

**E12 — M42-5 (not in the lesson): C3 and R1 Target strings.**
- Append: "Erratum (r42 review): the C3 Target (prereg:41) ends `(exit 0)`, which `c3-counter.py` does not print, and omits `cases=` and `tool_sha=`, which it does print. The R1 Target (prereg:51) ends `(exit 0)`, which `r1-counter.py` does not print. The counters' SUMMARY lines are the Targets' authority."

**E13 — M42-5 (not in the lesson): instruments commit and census receipt.**
- Append: "Erratum (r42 review): the prereg's sentence (prereg:5) that the instruments commit `b7408095…` adds 'counters, c1/c3 populations, pinned tool' is wrong: `census/round-42/c1-items.tsv`, `c3-mutants.tsv`, `c2-counter.py`, `c3-counter.py`, `r1-counter.py` and `c1-counter.py` were added at `410316c`; `b740809` edits only `c1-counter.py` and `controls/c1-control.txt`; the pinned tool `tools/souji-worktree-drift.py` was added at `42ea92e`. Likewise prereg:56's 'committed at the instruments commit' is false for `census/round-42/records/census-before.txt`, which is in `410316c`."

**E14 — M42-5 header count.**
- Append: "Erratum (r42 review): the section enumerates three attributions and this list of errata (E11–E13) is the complete set the review found; 'six' is not the count."

**E15 — M42-6: attribution of `-P`.**
- Wrong: "`census/round-42/waves/w1/R42scribe07/receipts/python-startup-probe.txt` … (an injected `sitecustomize` runs under `python3 -B`, `-s`, `-P`; not under `-I`, `-E`, `-S`)".
- Measured (row 53): the scribe07 receipt covers `-B -I -S -E -s`; `-P` is in the `R42sentinel02.md` premise table only.
- Append: "Erratum (r42 review): `-P` is evidenced by `R42sentinel02.md` (`python3 -P -B` → sitecustomize runs), not by the scribe07 receipt, which covers `-B`, `-I`, `-S`, `-E` and `-s`."

**E16 — C1 CORRECTION line 68 (lesson, `corpus/lessons/round-42.md`).**
- Wrong: "The tool was edited later (first `bb506469…` revision `604cd441`)".
- Measured (row 28): `604cd441` has the digest but is not an ancestor of the base; the base-history first revision of that blob is `7e4dbef94061578fca2f58621f87908c886cc431`.
- Append: "Erratum (r42 review): the first base-ancestor revision with the `bb506469…` digest of `tools/souji-coverage-agreement.py` is `7e4dbef94061578fca2f58621f87908c886cc431`. `604cd441` has the same digest but is not an ancestor of the base."

**E17 — Q103 row (QUALITY.md:264) motivating text.**
- Wrong: "the frozen exemption repair read green in one mode and `findings=2` in the other".
- Append (to the QUALITY row's motivating evidence, as a correction line): "Correction (r42 review): the 'green' reading was a could-not-evaluate gate run (zeroed SUMMARY, exit 2); no loader-admissible exemption set is green in plain mode; the exemption route cannot reach the `../` pointers. See lesson M42-2 erratum E1."

**E18 — Q104 row (QUALITY.md:265) check.**
- Wrong (by omission): the row's own check requires "the instrument's counts line at the tip with its revision" and "the reachability run names the files it appended". Neither is in committed bytes at `3105a63`.
- Append: "Correction (r42 review): this round did not satisfy Q104's own check: no committed counts line at the landed tip (`3105a63`: `assertions=490 resolved=420 skipped=810 mismatches=70`), and no reachability receipt naming the appended files (the `c1-after.txt` measurement predates the append). See M42-1 and M42-3 errata E4 and E6."

**E19 — Q105 row (QUALITY.md:266).** No defect found beyond E15 (the `-P` attribution). Q105's check is satisfied in the lesson (the unreached classes are listed beside the count in M42-6 and in the S259 registry row).

## 3. Named limits to add (not in the lesson)

- **L-r1-exit** (row 12, row 13): R1 counter reads the gate's SUMMARY and not its exit code.
- **L-c1-line840** (row 22): `new_mismatches` does not count a bad row on line 840.
- **L-c1-tipinstrument** (row 6, E6): the instrument still reads 70 at the tip; the register is for the counter only.
- **L-c3-prior** (row 50, E10): the `prior=` leg is timing-sensitive; the lesson names only `old_killed`.

## 4. Quality rows Q103–Q105 (`corpus/QUALITY.md:264–266`)

| row | M-id cited | does the cited lesson row say what the criterion says? | check the row requires | satisfied by the round? |
|---|---|---|---|---|
| Q103 | M42-2 | yes in form (count without mode; repair in both modes) | the receipt block: `--round`, full 40-hex `--rev`, fleet-root flag | receipts yes (`gate-both-modes.txt`); the lesson's M42-2 pointer uses an abbreviated rev (E2); the motivating sentence is wrong (E1) |
| Q104 | M42-1, M42-3 | yes (instrument not run at tip; blank-line sentinel) | tip counts line with revision; `new_mismatches=0`; blank-prefixed appends; reachability run names the appended files | **no**: no tip counts line in committed bytes (row 6); the measurement cited for the appends predates them (row 24) |
| Q105 | M42-6 | yes (unreached classes beside the count) | unreached classes listed beside the count; probe table cited | yes, with the `-P` attribution slip (E15) |

Note on the motivating column of Q104: "70 unresolvable tokens accumulated r23-r41" is reproduced (row 4–5).

## 5. What was not checked

- The 65/5 register derivation beyond the counter's `class_ok=70 unresolved=5` (the five-reader and independent re-derivation are the wave's; not re-derived here, row 16).
- The C2 counter and its 37 cases (row 44 not run).
- The "L1's first survey run" for F1 (no receipt exists).
- `CORRECTION-SC` line 839 and the rest of the r41 plan-vs-actual.
- The remaining two receipts in the SCORECARD:697 list.
- The lesson's named-limit list N-C1a..N-adj beyond the items above (the wave reports were read only where the lesson cites them for the items checked).
- The prereg's "21 r41 cases retained" versus the counter's 19 + 2 split (critic06 note; not re-checked).

## 6. Commands run (exact; full output in `receipts/reproduce.txt`)

The full set is `receipts/reproduce.sh`. Representative commands with their observed output:

```
$ python3 -B tools/souji-declared-evidence.py --root <lane> --rev bf618f6c5c09d302994871c94903abbea2deb60d --file SCORECARD.md --format counts
assertions=474 resolved=404 skipped=780 mismatches=70
$ python3 -B tools/souji-declared-evidence.py --root <lane> --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --file SCORECARD.md --format counts
assertions=490 resolved=420 skipped=810 mismatches=70
$ python3 -B tools/souji-declared-evidence.py --root <lane> --rev d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7 --file SCORECARD.md --format counts
assertions=82 resolved=80 skipped=69 mismatches=2
$ git grep -n -E 'resolved=420|assertions=490|skipped=810' 3105a63b23481fccf7df58e74d14a6681e0ea0c8 -- .   → grep-exit=1 (no match)

$ python3 -B tools/souji-landing-gate.py --root <lane> --rev bf618f6c5c09d302994871c94903abbea2deb60d --round 41
SUMMARY	findings=3 …      rc=1
$ … --fleet-root /home/vgpnk/Projects/shokunin
SUMMARY	findings=0 …      rc=0
$ … --rev e95b13beb5b690f0bf80034c12c1ac7b6650bb45 --round 41        SUMMARY findings=2 …  rc=1
$ … --rev 51f204fb7c633b691a3ca9cd8c0bf025f6e0a093 --round 41        SUMMARY findings=0 …  rc=0  (and with --fleet-root: findings=0)

$ literal three-row candidate, clone at 3105a63 (cd02a5f9…):
COULD-NOT-EVALUATE	corpus/pointer-exemptions.tsv:5 malformed exemption row (expected unique path<TAB>reason)   rc=2   (both modes)
$ bash census/round-42/score-candidate.sh r1 <scratch> corpus/pointer-exemptions.tsv=<literal rows>
SUMMARY findings=0 deleted=2 rows_added=3 stale=0      rc=1

$ .ufo/-spelled variant, clone at base (a8072540…):
SUMMARY findings=4 …   rc=1   (plain)
SUMMARY findings=2 …   rc=1   (--fleet-root)

$ bash census/round-42/score-candidate.sh c1 <scratch> SCORECARD.md=<base + non-blank row>
SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=1 new_mismatches=0
$ … SCORECARD.md=<base + blank-prefixed row>            rewritten=0 new_mismatches=0
$ … SCORECARD.md=<tip + non-blank row>                  rewritten=0 new_mismatches=0
$ … SCORECARD.md=<base + bad row at line 840, no blank>  rewritten=1 new_mismatches=0
$ … SCORECARD.md=<base + bad row at line 841, blank>     rewritten=0 new_mismatches=1
$ python3 -B census/round-42/c1-counter.py --root <lane> --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch <dir>
SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0   rc=0

$ python3 -B census/round-42/records/survey-prior.py --lane <lane> --scratch <dir>
MUTANT D3 killed-by-prior-fixtures=r38-drift-write-envelope.py
MUTANT F2 killed-by-prior-fixtures=r38-drift-write-envelope.py
MUTANT H3 killed-by-prior-fixtures=r36-worktree-drift.py,r37-drift-discrimination.py,r40-drift-record-branches.py,r41-drift-record-order.py
MUTANT J5 killed-by-prior-fixtures=r41-drift-record-order.py
MUTANT N1 killed-by-prior-fixtures=r36-worktree-drift.py,r37-drift-discrimination.py,r40-drift-record-branches.py,r41-drift-record-order.py
MUTANT T2 killed-by-prior-fixtures=r40-drift-record-branches.py,r41-drift-record-order.py
MUTANT F1 killed-by-prior-fixtures=-

$ F1 mutant vs r36 (three runs): SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED   rc=0  (x3)

$ python3 -B census/round-42/c3-counter.py --root <lane> --rev 3105a63… --scratch <dir>      (two saved runs)
SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
(transcript-only third run: prior=7/8)

$ git -C <lane> show --name-status --format= afe17f4 -- census/round-42/controls census/round-42/c2-cases.tsv census/round-42/preregistration.txt
A census/round-42/c2-cases.tsv / M census/round-42/controls/c1-control.txt / A …c2-control.txt / A …c3-control.txt / A …r1-control.txt / A census/round-42/preregistration.txt
$ git -C <lane> show 410316c:census/round-42/controls/c1-control.txt
fatal: path 'census/round-42/controls/c1-control.txt' exists on disk, but not in '410316c'      rc=128
$ git -C <lane> merge-base --is-ancestor 604cd441 bf618f6c5c09d302994871c94903abbea2deb60d; echo $?   → 1
$ git -C <lane> merge-base --is-ancestor 7e4dbef94061578fca2f58621f87908c886cc431 bf618f6c5c09d302994871c94903abbea2deb60d; echo $?   → 0
```

## 7. Misstatement list (summary for the L1)

| id | where | wrong text (short) | corrected by |
|---|---|---|---|
| E1 | lesson M42-2; QUALITY Q103 motivation | "green without `--fleet-root`, `findings=2` with it" | zeroed exit-2 run; no admissible green plain; variant 4/2 |
| E2 | lesson M42-2 pointer | `--rev bf618f6…` (abbreviated) | full 40-hex (Q103) |
| E3 | lesson M42-2 (named limit missing) | r1 counter ignores gate exit | added limit |
| E4 | lesson M42-3 fix | `c1-after.txt` measured the appends | measured at 34e33a6, before the append; tip measured in receipts |
| E5 | lesson N-C1c (consequence) | `> 840` | line 840 not counted by `new_mismatches` |
| E6 | lesson M42-1 (omission); QUALITY Q104 | counts at base only | tip reads `490 420 810 70` |
| E7 | lesson M42-1 | "no round re-running the instrument" | r31 prose run claim with no receipt |
| E8 | lesson M42-4 | survey in `c3-control.txt`; "13 left" | `records/survey-prior.txt`; 12 of 17 G-class; D4 is the 13th |
| E9 | lesson M42-4; prereg F1 sentence | F1 killed by r36 (first run) | not reproduced; no receipt |
| E10 | lesson (named limits) | prior leg not timing-sensitive | `prior=7/8` once in three tip runs |
| E11 | lesson M42-5 | four receipts added; c1 committed at 410316c; "six" misstatements | three added; c1 added at b740809, rewritten at afe17f4 |
| E12 | prereg C3/R1 Targets (not in lesson) | `(exit 0)` not printed; C3 omits `cases=`, `tool_sha=` | counters' SUMMARY lines |
| E13 | prereg:5, :56 (not in lesson) | instrument commit adds counters/populations/pinned tool; census at instruments commit | 410316c / 42ea92e |
| E14 | lesson M42-5 header | "six" | the enumerated list is the set |
| E15 | lesson M42-6 | `-P` in the scribe07 receipt | sentinel02 |
| E16 | lesson CORRECTION-DE line 68 | first `bb506469` revision `604cd441` | `7e4dbef` (604cd441 not an ancestor of base) |

## 8. Residual risk

- The C3 `prior=` leg reached 7/8 once in three full runs. An L1 re-measurement under load can read a miss on the frozen target; the cause is unisolated.
- R1 counts as green any run whose gate exits 2; the frozen counter is red only through its `deleted=2` in the current clone (row 13).
- The round's instrument still reads 70 at the tip. The C1 register is a counter-scoped accounting; an L1 reading of "the declared-evidence instrument is clean" would be false.
- Nothing in this review tests the C2 counter (row 44 not run) or the 65/5 register beyond the counter's aggregate.
