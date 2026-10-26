# SimpCounterCheck — r26 counter minimality and correctness review

Seat: read-only reviewer. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Freeze rev `89e0fceeefcf28db313c94120be6d25e03c60094`; lane HEAD `d6c13b0`; base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`.
No lane bytes written except this report; no git mutation; scratch under `/var/tmp/souji-r26-SimpCounterCheck/`, removed.

## Status

STATUS: PASS — all three counters were executed at the freeze rev and at HEAD (extracted copies); all six base/tip literals reproduce the committed receipts exactly, and the four questions asked are answered with executed evidence. Three counter defects and one unreachable frozen literal are reported; no counter was edited (read-only seat, and any change to a frozen instrument is amendment-grade).

## Evidence

Revision facts (`git rev-parse`, `git ls-tree`, `sha256sum`):

```
c1-counter.sh  89e0fce f02b441a…  HEAD f02b441a…  sha256 c8dbb76c…   (identical)
c2-counter.sh  89e0fce 01f7af38…  HEAD 01f7af38…  sha256 e3f7a677…   (identical)
c3-counter.sh  89e0fce 86808c06…  HEAD c7d6260f…  sha256 7d40f5d8… -> b60bced7…  (changed at d2e6253)
tool/fixture absent at 89e0fce: `git cat-file -e 89e0fce:tools/souji-axis-check.py` fails; same for tests/fixtures/r26-axis-check.py
```

Counter runs in `git archive` extractions (base = 89e0fce, tip = HEAD), as the frozen argv:

```
BASE  c1: markers=2  headings=17 175 231 (trailing space)  rc 0
BASE  c2: grounded_f1=0  registry_rows=127                  rc 0
BASE  c3: axis_check_tool=absent                            rc 0
TIP   c1: markers=0  headings=17 44 78 (trailing space)     rc 0
TIP   c2: grounded_f1=2  registry_rows=132                  rc 0
TIP   c3: axis_check_tool=present / claims=3 flags=0 / axis_check_exit=0   rc 0
```

These match `census/round-26/records/c1-before.tsv` (rev 12fd90b), `c1-after.tsv` (a529c76), `c2-before.tsv` (89e0fce), `c2-after.tsv` (e0f8dcd), `c3-before.tsv` (89e0fce), `c3-after.tsv` (d2e6253).

Question 1 — does c1's awk match the headings the file really contains? Yes. Real heading bytes at the freeze rev carry a parenthetical suffix, so the frozen pattern matches as a prefix:

```
89e0fce SCORECARD.md:17  ### Round 23 measurements (2026-10-25, lane base 1208bfb…)
89e0fce SCORECARD.md:175 ### Round 24 measurements (2026-10-25, lane base a65fac9…)
89e0fce SCORECARD.md:231 ### Round 25 measurements (2026-10-25; base a6d2d15…)
```

Fence-state probe (toggle on every fence line, print the flag at each match):

```
89e0fce: line=17 fenced=0 | line=175 fenced=1 (inside the ```markdown scaffold) | line=231 fenced=0
HEAD:    line=17 fenced=0 Round 25 | line=44 fenced=0 Round 24 | line=78 fenced=0 Round 23
```

So the freeze triple is two real headings plus one fenced copy; the HEAD triple is three real headings.

Question 1b — line counting: the K1 grep counts matching lines, not occurrences. Probe: one line containing the marker twice yields 1; two marker lines yield 2 (matches base lines 172 and 217).

Question 2 — does c2's `grep -l … | wc -l` count files? Yes. Probe: one file with 3 matching lines plus a second file with 1 line gives `files=2 lines=4`; the 3-match file alone counts 1. At HEAD the two files are `corpus/knowledge/git-auto-maintenance-trigger-set.md` and `…-r23.md`, one `ground: F1` line each.

Question 3 — c3 marker plus tool stdout, and `axis_check_exit`: both are printed (post pattern above). `axis_check_exit` is the tool's real exit. Probe: replace the tool with one that prints `claims=3 flags=1` and exits 7:

```
axis_check_tool=present / claims=3 flags=1 / FLAG C1 R2 probe / axis_check_exit=7
counter-rc=0
```

The label is correct; the counter's own rc is not (Finding 8).

Question 4 — cross-checks:

```
git grep -l '^ground: F1' 0eca7c8 -- corpus/knowledge/   -> 0
git grep -l '^ground: F1' HEAD -- corpus/knowledge/       -> 2  (still 2 with an untracked stray present)
SOURCES.md rows: 0eca7c8 -> 127; HEAD -> 132; unique ids S001..S132 = 132; rows S128..S132 = 5
sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji -> rc 0, last line "ok <lane>/corpus/SOURCES.md" (no row-count line printed)
fixture normal arm: cases=11 pass=11, rc 0, no control line
fixture stub arm:   cases=11 pass=4, control=FALSE-GREEN-REJECTED, rc 1
```

Missing-input probes (scratch copies of the counters, inputs removed):

```
no SCORECARD.md      -> markers=  headings=                          rc 0 (awk fatal on stderr only)
no SOURCES.md        -> registry_rows=                               rc 0
no corpus/knowledge  -> grounded_f1=0                                rc 0
```

Simplification probe: dropping ` END{print ""}` from the awk yields byte-identical output (`17 44 78 ` both ways), because the command substitution strips the newline.

Hygiene probe: neither counter arm creates `__pycache__` in a pristine tip copy. The lane nevertheless carries untracked `tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc` (14:26 local) and `tools/__pycache__/souji-axis-check.cpython-314.pyc` (14:25 local), one tracked pyc (`census/round-10/__pycache__/…cpython-314.pyc`), and no `.gitignore` rule; host is Python 3.14.8.

## Findings

1. **C1 K2 cannot falsify the ordering it claims to test.** Location: `census/round-26/c1-counter.sh:8`; prereg C1 K2. The awk prints `NR` in file order with no round label, while the prereg reads the triple as `(n25, n24, n23)`. Its own base literal `17 175 231` is file order 23, 24, 25 — the labelled reading is already false at the base. Probe: a file with Round 24 above Round 25 prints `1 5 9`, shape-identical to the passing tip `17 44 78`. Minimal fix (stricter, amendment-grade): key `NR` by the matched round and print `n23=… n24=… n25=…`.

2. **C1 K2 is fence-blind.** Location: `c1-counter.sh:8`; base `SCORECARD.md:174-175` and `:208`. "Exactly three headings" therefore means "three lines starting with the heading text", including a fenced duplicate (base 175 is `fenced=1`). At HEAD all three are real, so the after literal holds in fact; the scaffold-still-fenced case is excluded only by amendment 2's span diff, not by this counter.

3. **C1 prints a trailing space absent from the frozen literal.** Location: `c1-counter.sh:8` and `:10`. Receipts read `headings=17 175 231 `, the prereg literal is `17 175 231`; string-equality scoring fails. The ` END{print ""}` clause is also redundant — removing it is byte-identical (verified) and is the one deletion candidate with no behaviour change.

4. **C1 silent pass on a missing file.** Location: `c1-counter.sh:4-10`. With `SCORECARD.md` absent it prints empty values and rc 0; a receipt cannot distinguish that from a scored value.

5. **C2 K1 does not implement the frozen command, and the frozen literal cannot produce the after value.** Location: prereg C2 K1 vs `c2-counter.sh:7`. The frozen command greps revision `0eca7c8`, so run at any tip it returns 0 (measured), never the claimed 2. The counter substitutes a working-tree glob, which is inflatable by untracked bytes: an untracked `corpus/knowledge/zz-untracked-probe.md` raised `grounded_f1` to 3 while the rev-scoped grep stayed 2. Rev-scoping to `HEAD` reproduces 0 at base and 2 at tip.

6. **C2's `2>/dev/null` turns a missing tree into the red-before literal.** Location: `c2-counter.sh:7`. With `corpus/knowledge` absent it prints `grounded_f1=0`, rc 0 — exactly the base value, so absence is indistinguishable from a true red.

7. **C2 `registry_rows` is a count-only proxy, and the census validator prints no count.** Location: `c2-counter.sh:8`; validator output last line is `ok …/corpus/SOURCES.md`. The value is correct today (132 matching lines, 132 unique ids S001..S132, exactly 5 rows S128..S132), but a delete plus an add keeps 132. Hardening: print the max id (`S132`) or the S128..S132 count, one line each.

8. **C3's tool-exit label is right; the counter's own exit is not.** Location: `c3-counter.sh:19-21`. `axis_check_exit` is the real tool exit (probe: 7). But the last command is `printf`, so the script always exits 0 — present-pass, present-flag and absent are rc-identical, and the committed `c3-before`/`c3-after` receipts both carry rc 0. Minimal fix: `rc=$?` after the tool run, print, then `exit "$rc"`; exit nonzero on absent.

9. **C3's counter was changed after the freeze without an amendment, and the added arm omits `-B`.** Location: `c3-counter.sh:11-17` (added at d2e6253; blob 86808c06 -> c7d6260f). The frozen C3 artifact list defines only the tool run and the fixture `--tool` CLI; `--stub` is new. The added line `c3-counter.sh:12` runs `python3` without `-B`, against the lane's run-lane-Python-with-`-B` rule. Observed effect: none — a pristine tip copy produced no `__pycache__` from either arm. `LOG.md` has no round-26 section (last entry is 2026-10-25 Round 25), so the change is not logged there; the round lesson records the separate labelled commit (`corpus/lessons/round-26.md:49`).

10. **Frozen C3 K2 literal is unreachable.** Location: prereg C3 K2 vs `tests/fixtures/r26-axis-check.py:4`, `:213`, `:219-221`. The fixture has 11 CASES and prints `cases=11`; `control=` is printed only in the stub arm, which necessarily fails cases. Measured: normal arm `cases=11 pass=11` rc 0 with no control line; stub arm `cases=11 pass=4` with `control=FALSE-GREEN-REJECTED` rc 1. No single execution emits `cases=12 pass=12 control=FALSE-GREEN-REJECTED` with exit 0, so C3 K2 fails as frozen. The lesson discloses the 11-case fixture (`corpus/lessons/round-26.md:6`). This is a claim-level defect, not a counter bug.

11. **Two receipts named by C2's prereg are not in the tree.** Location: prereg C2 RECEIPTS vs `git ls-tree -r --name-only HEAD census/round-26/records/`. `c2-gate.tsv` and `c2-k4-after.tsv` are absent; d6c13b0 added only `c2-after.tsv` and edited `c2-before.tsv`, while its message asserts "real gate rc=0". Nothing committed binds K2 or K4 at the tip.

12. **Green receipts are not at the final tip, though the measured bytes are unchanged.** c1-after at a529c76, c2-after at e0f8dcd, c3-after at d2e6253, HEAD d6c13b0. `git diff --stat a529c76 HEAD -- SCORECARD.md` and `git diff --stat d2e6253 HEAD -- SCORECARD.md tools/souji-axis-check.py .ufo/waves/round-26/preregistration.txt` are both empty, so the recorded values still describe HEAD's measured bytes. Calibration nit only.

13. **Hygiene: pycache in a hygiene lane.** Locations: `tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc` (untracked), `tools/__pycache__/souji-axis-check.cpython-314.pyc` (untracked), `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (tracked), no `.gitignore` rule. Timestamps 17:25-17:26Z sit four minutes before the 17:29Z receipts, but the counters' own arms create none, so attribution is another seat's direct invocation. Not removed: read-only seat, and deletion outside this assignment.

## Attack log

- **A1 — C1 K2 ordering is vacuously satisfiable.** A file with Round 24 above Round 25 produces the same-shaped triple as the passing tip (slope ascending either way). Kill-rule impact: calibration. The claim still holds in fact (Round 25 at 17, Round 24 at 44, Round 23 at 78, verified from the heading text), but this counter did not prove the ordering; only amendment 2's byte-span diff does. Required fix class: label the triple by round (stricter, no predicate change).
- **A2 — C2 K1's frozen literal measures the base at every revision, and the counter's working-tree substitute is untracked-inflatable.** Kill-rule impact: coverage. Required fix class: rev-scope the grep to the receipt revision.
- **A3 — C3's counter rc carries no signal.** Both the red-before and green-after receipts are rc 0; a flagged tool yields rc 0. Kill-rule impact: operability (the receipt field that should bind the verdict cannot). Required fix class: propagate the tool exit.
- **A4 — C3 K2's `cases=12 pass=12` is unproducible** by an 11-case fixture whose control arm is a separate mode. Kill-rule impact: the frozen claim fails as written unless the L1 records a stricter-only re-expression: add the control as a 12th case that the normal arm evaluates as a passing case while still printing the rejected-control line. Not a relaxation.
- **A5 — C2's 127->132 row literal is swap-stable** under a count-only regex. Impact: coverage. Required fix class: print the id span or max id; the census validator supplies no count to cross-check.

## Preserved contract

- C1/C2 counters are byte-identical to the freeze; C3's no-argument path (the receipt-bound argv) is byte-identical in behaviour to the frozen version (presence marker, tool stdout, tool exit label), verified at base and tip.
- Frozen predicates, targets and case sets are unchanged; nothing was relaxed. Every proposal above is stricter or label-only.
- Deletions made: none (read-only seat). Deletion candidates: the redundant awk ` END{print ""}`; the `2>/dev/null` suppression. No frozen line can be removed without losing a predicate.
- Scratch `/var/tmp/souji-r26-SimpCounterCheck/` removed. Tool installs/upgrades: none.
