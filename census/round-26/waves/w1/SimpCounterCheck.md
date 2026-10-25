# SimpCounterCheck — r26 counter minimality and correctness review

Seat: read-only reviewer. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Reviewed revisions: freeze `89e0fce`, then `d6c13b0`, `c594901`, `0c92c2e`, `33e6807`, latest observed HEAD `166baa1` at review close (the lane moved five times during the review; counter digests below are the latest-HEAD bytes).
Base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`. No lane bytes written except this report; no git mutation; scratch `/var/tmp/souji-r26-SimpCounterCheck{,2}` removed.

## Status

STATUS: PASS — review complete. All three counters were executed at the freeze rev, at intermediate tips and at latest HEAD in extracted copies; every base/tip value reproduces the committed receipts. Sixteen findings are recorded: one breaks the receipt contract for five of the six counter receipts, two make a frozen command unexecutable, three are predicate-observability defects, the rest are robustness, round-pin, receipt-completeness and hygiene. No instrument was edited (read-only seat; any change to a frozen instrument is amendment-grade).

Direct answers: c1's awk DOES match the real headings (prefix match against the parenthetical suffix), c2's `grep -l` DOES count files, c3 DOES print the marker plus the tool stdout and `axis_check_exit` IS the tool's real exit — but the counter's own exit is always 0, and the printed lines are outside the receipt verifier's counts vocabulary.

## Evidence

Counter digests at latest observed HEAD `166baa1` (`git show HEAD:…` piped through `sha256sum`):

```
c1-counter.sh  c8dbb76cc4495b81…  == freeze blob f02b441a  (unchanged)
c2-counter.sh  e3f7a67703cb9060…  == freeze blob 01f7af38  (unchanged)
c3-counter.sh  fcf954f09d2d0c10…  <- 86808c06 (freeze) -> c7d6260f (d2e6253) -> fcf954f0 (c594901)
tools/souji-axis-check.py and tests/fixtures/r26-axis-check.py absent at 89e0fce (git cat-file -e fails)
counters also absent at the prereg's base 0eca7c8 (added at 12fd90b)
```

Frozen-argv runs (extracted trees; same shape at 89e0fce, d6c13b0 and 33e6807):

```
BASE 89e0fce c1: markers=2  headings=17 175 231  rc 0
BASE 89e0fce c2: grounded_f1=0  registry_rows=127  rc 0
BASE 89e0fce c3: axis_check_tool=absent  rc 0
TIP  166baa1 c1: markers=0  headings=17 44 78  rc 0
TIP  166baa1 c2: grounded_f1=2  registry_rows=132  rc 0
TIP  166baa1 c3: axis_check_tool=present / claims=3 flags=0 / axis_check_exit=0 /
                 cases=12 pass=12 control=FALSE-GREEN-REJECTED / fixture_exit=0  rc 0
```

Values match `c1-before` (12fd90b), `c1-after` (07f83e6), `c2-before` (89e0fce), `c2-after` (e0f8dcd), `c3-before` (89e0fce), `c3-after` (c594901).

c1 match target — real heading bytes at the freeze rev, with the fence state at each match:

```
89e0fce:17  ### Round 23 measurements (2026-10-25, lane base 1208bfb…)   fenced=0
89e0fce:175 ### Round 24 measurements (2026-10-25, lane base a65fac9…)   fenced=1
89e0fce:231 ### Round 25 measurements (2026-10-25; base a6d2d15…)         fenced=0
33e6807:17 Round 25 fenced=0 ; 33e6807:44 Round 24 fenced=0 ; 33e6807:78 Round 23 fenced=0
```

So the regex matches all three real headings (suffix is tolerated by the prefix match) and at the base also matches the fenced scaffold copy.

Line/file counting probes:

```
grep -c on one line holding the marker twice -> 1  (counts lines, not occurrences)
one file with 3 matching ground lines + one file with 1 -> files=2, lines=4
ground: F1 files at HEAD -> git-auto-maintenance-trigger-set.md, …-r23.md
git grep -l '^ground: F1' 0eca7c8 -- corpus/knowledge/ -> 0 ; at HEAD -> 2
```

Ordering-ambiguity probe (the frozen K2 output cannot distinguish a misordered file):

```
file with Round 24 first, Round 25 second, Round 23 third -> awk prints "1 5 9 "
passing tip                                                -> awk prints "17 44 78 "
```

c3 exit capture probes at latest HEAD (tool replaced by exit-7 printer, fixture by exit-5 printer):

```
tool exit 7, real fixture:  axis_check_exit=7  cases=12 pass=1 control=FALSE-GREEN-REJECTED  fixture_exit=1  counter-rc=0
tool exit 7, fixture exit 5: axis_check_exit=7  cases=0 pass=0                              fixture_exit=5  counter-rc=0
bash c3-counter.sh --stub   -> runs the default arm, rc 0 (no argv refusal)
```

c1 awk minimality: dropping ` END{print ""}` leaves the command-substitution result byte-identical (`17 44 78 ` both ways), because the substitution strips the newline.

Fixture arms at latest HEAD: normal `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0; per-case lines show case 12 as `control-always-green-stub PASS stub_passed=2/11 discriminator=PASS`.

Receipt verification at latest HEAD (committed bytes, `python3 -B tools/souji-receipt-run.py verify --root .`):

```
c1-before  RECEIPT-COUNTS-ABSENT
c1-after   RECEIPT-COUNTS-ABSENT
c2-before  RECEIPT-COUNTS-ABSENT
c2-after   RECEIPT-COUNTS-ABSENT
c3-before  RECEIPT-COUNTS-ABSENT
c2-k4-base verify=ok
c2-gate     verify=ok  (rev 33e6807, added at 9a6e0f1)
c2-k4-after verify=ok  (rev 33e6807, added at 9a6e0f1)
c3-after   verify=ok
```

Run/verify symmetry probe at latest HEAD (`run --root . --rev HEAD --tool … --out /var/tmp/…`):

```
c1 run -> counts=none ; verify -> RECEIPT-COUNTS-ABSENT
c2 run -> counts=none ; verify -> RECEIPT-COUNTS-ABSENT
c3 run -> counts=cases=12 pass=12 ; verify=ok
```

Patched-vocabulary probe: a SCRATCH copy of the runner with three added counts alternatives (`markers=\d+`, `grounded_f1=\d+`, and an `axis_check_tool=` prefix accepting either present or absent) verifies all five failing receipts `verify=ok` at their own revs and digests. The lane tool was not modified.

Frozen receipt recipe as written:

```
python3 -B tools/souji-receipt-run.py run --root . --rev 0eca7c8… --label census/round-26/c1-counter.sh -- bash census/round-26/c1-counter.sh
-> rc 2, argparse: the following arguments are required: --tool, --out
run --help: --root, --rev, --tool, --out, command   (no --label)
```

Cross-checks: `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` exits 0, last line `ok <lane>/corpus/SOURCES.md`, and prints no row count. SOURCES.md matching rows 127 at 0eca7c8/89e0fce and 132 at HEAD; 132 unique ids S001..S132; exactly 5 rows S128..S132. SCORECARD bytes identical at 0eca7c8 and 12fd90b (empty diff); headings `17 175 231`, markers 2 at 0eca7c8.

Hygiene probe: neither counter arm creates `__pycache__` in a pristine copy, yet the lane holds untracked `tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc` and `tools/__pycache__/souji-axis-check.cpython-314.pyc`, one tracked pyc from round 10, and no `.gitignore` rule. Host Python 3.14.8.

## Findings

1. **Five of the six counter receipts do not verify; only the post-freeze c3 green does.** Location: `tools/souji-receipt-run.py:67-77` (counts vocabulary) and the counters' print lines (`c1-counter.sh:10-11`, `c2-counter.sh:9-10`, `c3-counter.sh:16`). `markers=`, `headings=`, `grounded_f1=`, `registry_rows=`, `axis_check_tool=absent` match no counts alternative, so `verify` returns `RECEIPT-COUNTS-ABSENT`; `run` records `counts=none` and writes the receipt anyway. The prereg states each receipt is `verify=ok`; five are not, including both C1 receipts and both C2 receipts. The scratch-vocabulary probe shows digests, revs, argv labels and durability are otherwise sound, so the fix is three alternatives in the verifier (or a counts-shaped final line per counter), not a counter rewrite. This is the highest-impact finding: without it the counters are not receipt-bound at all.
2. **C1 K2 cannot falsify the ordering it claims to test.** Location: `c1-counter.sh:8`; prereg C1 K2. The awk prints `NR` in file order with no round label while the prereg reads the triple as `(n25, n24, n23)`; its own base literal `17 175 231` is file order 23, 24, 25. A file with Round 24 above Round 25 prints the same-shaped ascending triple as the passing tip (`1 5 9` vs `17 44 78`). Minimal stricter fix: key `NR` by the matched round and print `n23=… n24=… n25=…` (amendment-grade).
3. **C1 K2 is fence-blind.** Location: `c1-counter.sh:8`; base `SCORECARD.md:174-175`, `:208`. Base line 175 is inside the ` ```markdown ` scaffold, so "exactly three headings" at the base includes a fenced copy. At HEAD all three matches are real (fenced=0 at 17, 44, 78), so the after literal holds in fact; the still-fenced case is excluded only by amendment 2's span diff.
4. **C1 prints a trailing space the frozen literal does not have, and carries a redundant awk clause.** Location: `c1-counter.sh:8` and `:10`. Receipts read `headings=17 175 231 ` versus prereg `17 175 231`; string-equality scoring fails. Dropping ` END{print ""}` is byte-identical (verified) and is the one deletion with no behaviour change.
5. **C1 silently passes on a missing file.** Location: `c1-counter.sh:4-11`. With `SCORECARD.md` absent it prints `markers=` and `headings=` and exits 0 (awk's fatal goes to stderr only).
6. **C2 K1 does not implement the frozen command, and the frozen literal cannot produce the after value.** Location: prereg C2 K1 versus `c2-counter.sh:7`. The frozen grep names revision `0eca7c8`, so at any tip it returns 0; the counter substitutes a working-tree glob. A stray untracked file in `corpus/knowledge` raises `grounded_f1` to 3 while a rev-scoped grep stays 2. Rev-scope the grep (`git grep -l '^ground: F1' HEAD -- corpus/knowledge/`) reproduces 0 at base and 2 at tip.
7. **C2's `2>/dev/null` turns a missing tree into the red-before literal.** Location: `c2-counter.sh:7`. With `corpus/knowledge` absent it prints `grounded_f1=0` and exits 0 — indistinguishable from a true red. `registry_rows` on a missing SOURCES.md prints empty with rc 0 as well.
8. **C2 `registry_rows` is a count-only proxy.** Location: `c2-counter.sh:8`. Correct today (132 lines, 132 unique ids, 5 rows S128..S132) but swap-stable: delete one row, add one, and 132 still passes. The census validator prints no row count to cross-check. One-line hardening: print the max id or the S128..S132 count.
9. **C3's labels are right; its exit status is not.** Location: `c3-counter.sh:12` (`axis_check_exit`), `:13-14` (fixture line and `fixture_exit` via PIPESTATUS). Probes show `axis_check_exit=7` and `fixture_exit=5` captured exactly, but the counter exits 0 in both cases because the last command is `printf`. Present-pass, present-flag, fixture-failure and absent are rc-identical, and the committed `c3-before`/`c3-after` receipts both record rc 0. Minimal fix: `exit "$rc"` after printing, and nonzero for absent.
10. **The printer removes argument refusal.** Location: `c3-counter.sh:6-17`. The pre-c594901 version refused unknown argv with usage and exit 2; the current one has no argument handling, so `bash c3-counter.sh --stub` silently runs the default arm and exits 0. A typo is now a silent pass.
11. **The frozen receipt recipe is unexecutable as written.** Location: prereg C1 DO-NOTHING and C3 DO-NOTHING commands. They pass `--label` and omit `--out`; the runner's `run` requires `--tool` and `--out`, so the argv exits 2 under argparse. In addition the counters do not exist at the named `--rev 0eca7c8`, so even with `--tool` the runner would refuse `TOOL-ABSENT`. The committed receipts therefore use different revs (c1-before at 12fd90b, c2-before and c3-before at 89e0fce) and a different argv, with no amendment recording the substitution. The values are unaffected — SCORECARD bytes are identical at 0eca7c8 and 12fd90b, and the base literals `markers=2`, `17 175 231`, rows 127, F1=0 all reproduce at 0eca7c8.
12. **C3's frozen K2 literal was unreachable at the freeze rev and became reachable only through a post-freeze instrument change.** Location: prereg C3 K2 versus `tests/fixtures/r26-axis-check.py` at d6c13b0 (11 cases, control line only in the `--stub` arm) versus latest HEAD. At d6c13b0 the fixture printed `cases=11 pass=11` with no control line, and the counter's `--stub` arm printed `cases=11 pass=4`. At c594901 a 12-case fixture and a fixture arm were adopted and the literal now appears (`cases=12 pass=12 control=FALSE-GREEN-REJECTED`, `fixture_exit=0`). The change is disclosed in `corpus/lessons/round-26.md:6` but not in `LOG.md` (no round-26 section) and not in an amendment; the frozen C3 CLI lists only the tool and fixture `--tool` invocations.
13. **C2's two tip receipts landed one commit late, and two receipts predate the bytes they measure.** Location: `git ls-tree -r --name-only HEAD census/round-26/records/`. `c2-gate.tsv` and `c2-k4-after.tsv` are present at HEAD 166baa1 (added at 9a6e0f1, after the c2-after commit) and both `verify=ok` at rev 33e6807; `c2-k4-base.tsv` verifies. `c2-after` is at rev e0f8dcd, while `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` changed afterwards (24/17 at ea0bbe6, +9 at 33e6807); the count was re-measured at HEAD and still reads 2. `c1-after` is at 07f83e6 while HEAD moved; `SCORECARD.md` was unchanged through 33e6807 (empty diff) but changed by 166baa1 (+10 lines), so the receipt no longer covers the tip. The counter re-run at 166baa1 still reads `markers=0` and `headings=17 44 78`, so the value holds.
14. **Missing-input and crash blind spots share one root: no counter can fail.** Locations: `c1-counter.sh:4-11`, `c2-counter.sh:4-10`, `c3-counter.sh:6-17`. All three print diagnostics and exit 0 whether the input tree is missing, the tool flags, or the fixture crashes; `tail -n 1` in c3 additionally replaces the counts line with a traceback line on a crash.
15. **Hygiene: pycache in the lane.** `tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc` (untracked), `tools/__pycache__/souji-axis-check.cpython-314.pyc` (untracked), `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (tracked), no `.gitignore` rule. Timestamps 17:25-17:26Z, four minutes before the 17:29Z receipts, but the counters create none; attribution is another seat's direct invocation. Not removed: read-only seat.

16. **C1 K2 is round-pinned, so the new Round 26 block is invisible to it.** Location: `c1-counter.sh:8` (the alternation names only rounds 23, 24, 25) and `SCORECARD.md:233`, `:239`, `:264` at HEAD 166baa1. The r26 block was appended after `## Retired` (append-only corrections at 239, measurements at 264), while the layout contract the C1 background cites is newest first above Round 23. The counter cannot see this: it reports the 23/24/25 positions, which are unchanged (17, 44, 78) and still ordered. Amendment 2's span order is not violated (the named base spans remain verbatim and in order), so this is a layout departure only a wider measurement would catch. Fix class: match every `### Round N measurements` heading (stricter, amendment-grade).

## Attack log

- **A1 — C1's K2 output is round-agnostic, so the after-condition is vacuously satisfiable.** A misordered file passes with the same output shape. Calibration impact: the claim still holds in fact (Round 25 at 17, Round 24 at 44, Round 23 at 78, read from the heading text), but this counter did not prove it; amendment 2's byte-span diff did. Fix class: labelled triple (stricter).
- **A2 — Receipt binding is broken at the counts vocabulary.** Five receipts named by the prereg cannot verify; the instrument is not receipt-bound for C1, C2 or the C3 red arm. Proven fix: the three-alternative vocabulary extension (no counter or predicate change).
- **A3 — The frozen receipt recipe cannot run.** `--label` is not an option, `--out` is missing, and the counters are absent at the named base rev. Everything the prereg says about pre-after-data red receipts is therefore unexecutable as written; the receipts that exist used an undisclosed different recipe.
- **A4 — C2 K1's frozen literal measures the base at every revision and the working-tree substitute is untracked-inflatable.** Coverage impact: coverage. Fix class: rev-scoped grep at the receipt rev.
- **A5 — C3's counter rc carries no signal in any arm.** Operability impact: the receipt field that should bind the verdict cannot.
- **A6 — C2's 127->132 row literal is swap-stable** and the validator supplies no count to cross-check. Fix class: print the id span or max id.
- **A7 — C1's K2 is round-pinned: the r26 block appended below `## Retired` is invisible.** Calibration impact: newest-first placement is the contract the C1 integration was measured against, yet the counter cannot report the new block's position. Fix class: match all `### Round N measurements` headings (stricter).

## Preserved contract and weight removed

- c1 and c2 are byte-identical to the freeze; c3's no-argument path preserves the frozen behaviour (presence marker, tool stdout, tool exit label) and gained the fixture line and `fixture_exit`, which is what makes the C3 green receipt verify.
- The post-freeze c3 simplification (deleting the old `--stub` arm, 11 lines) is weight removed without losing a frozen predicate; the tradeoff is the lost argv refusal (Finding 10).
- Deletions made: none (read-only seat). Deletion candidates: the redundant awk ` END{print ""}`; the `2>/dev/null` suppression.
- Frozen predicates, targets and case sets unchanged; every proposal is stricter, label-only or vocabulary-only. Scratch removed. Tool installs/upgrades: none.
