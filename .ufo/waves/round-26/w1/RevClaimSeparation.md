# RevClaimSeparation — causal separability review (w1, round 26)

## Status
STATUS: PASS — C1/C2/C3 are causally separable: each counterfactual reversion leaves the other claims'
frozen counters byte-identically re-derivable. No cross-claim input dependency exists; the only
shared read (C3 R3 -> SCORECARD axes table) sits inside C1's kill-rule-protected bytes, verified
byte-identical base<->tip.

## Evidence
- C2 K4 tool input set (tools/souji-coverage-agreement.py, read this run): `README = "corpus/README.md"`,
  `KNOWLEDGE = "corpus/knowledge"` (lines 30-31); `knowledge_tree()` = `git ls-tree <rev> -- corpus/knowledge/`
  (lines 58-64); `measure()` maps rows from `show(root, rev, README)` and grounds from knowledge blobs
  (lines 135-172). `grep -n 'SCORECARD|scorecard'` over the file -> 0 matches. It reads ONLY corpus/README.md +
  corpus/knowledge/*.md at two revisions; never SCORECARD.md.
- C3 tool R3 input (tools/souji-axis-check.py lines 83-98, 124-128): `parse_scores()` opens `--scorecard PATH`
  read-only, extracts `## Axes` section, parses owned-axis score rows; R3 flags only if NO claim declares the
  lowest-scoring non-retired axis. C1 declares calibration (7 = lowest), so R3 is satisfied; the tool never writes.
- C1 kill rule (preregistration.txt lines 48-56 + amendment 2 block 1): any byte change inside base SCORECARD.md
  lines 1-171 (Axes table through "None." Retired) other than the two planned bullets is a kill; amendment 2 pins
  base lines 1-16 (title through `## Axes` table) verbatim. Live check: `diff <(git show 0eca7c8:SCORECARD.md | sed -n '1,16p') <(sed -n '1,16p' SCORECARD.md)` -> `IDENTICAL_1_16`. Axes table bytes base == tip.
- Live counters at HEAD 07f83e69979b1032f9de4fe876739a8dccc7242b:
  - `bash census/round-26/c1-counter.sh` -> `markers=0`, `headings=17 44 78` (newest-first, exactly 3).
  - `bash census/round-26/c2-counter.sh` -> `grounded_f1=2`, `registry_rows=132`.
  - `bash census/round-26/c3-counter.sh` -> `axis_check_tool=present`, `claims=3 flags=0`, exit 0.
  - `python3 -B tools/souji-coverage-agreement.py --root . --rev 07f83e6... --base-rev 0eca7c8...`
    -> `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, rc 0 (matches K4 after-literal).
- C2 gate-check (K2) dependencies (tools/souji-gate-check.py lines 28-38, 118-155): stdlib imports only; reads
  entries, `corpus/SOURCES.md`, snapshot dir, slice/verdicts files. No SCORECARD.md, no tools/souji-axis-check.py.
- C3 fixture (tests/fixtures/r26-axis-check.py lines 3-8, 44-56): self-contained; writes scratch preregs into temp
  dir; uses a SYNTHETIC axes table (coverage 8, calibration 7, operability 8); never reads the lane's corpus or
  real SCORECARD.md.
- c1-counter.sh: grep/awk over SCORECARD.md only. c2-counter.sh: grep over corpus/knowledge/*.md + corpus/SOURCES.md only.

## Findings
1. (i) Reverting C2's assimilation would not change C1's counter or C3's fixture. C1's counter reads only
   SCORECARD.md (c1-counter.sh lines 7-8); C2 touched corpus/knowledge/*.md, corpus/SOURCES.md, corpus/README.md,
   census/round-26/sources + records — disjoint from SCORECARD.md. C3's 12-case fixture uses a synthetic scorecard
   in /var/tmp scratch and never reads the lane's corpus (fixture lines 5-8); C3's self-host counter reads prereg
   + SCORECARD.md only (c3-counter.sh line 20). No shared input.
2. (ii) Reverting C1's SCORECARD surgery would leave C2's K4 = grounded=9 and C3's self-host green. K4's inputs are
   corpus/README.md + corpus/knowledge/ at --rev and --base-rev (tool evidence above); SCORECARD.md is not read —
   the tool contains zero SCORECARD/scorecard references. The 2 F1 entries that make grounded=9 are C2's own
   admitted entries, not C1 artifacts. C3's self-host reads the axes table, which is C1 kill-rule protected:
   base lines 1-16 byte-identical at tip (IDENTICAL_1_16), so R3's input is unchanged either way. Stronger: all
   three owned axes are declared (C1=calibration, C2=coverage, C3=operability), so R3 cannot fail for this prereg
   under any score assignment; but the byte-identity already settles it.
3. (iii) Reverting C3's tool (tools/souji-axis-check.py + tests/fixtures/r26-axis-check.py + c3-counter.sh) would
   leave C1/C2 counters byte-for-byte the same: c1-counter.sh and c2-counter.sh never reference tools/ or the
   fixture; K2 gate-check imports only stdlib and reads entries/SOURCES.md/snapshots/slices; K4 reads corpus/ only.
   C3's artifacts are additive and read none of C1/C2's inputs.
4. Confirm the ordering premise: the only conceivable cross-claim read is C3 R3 -> SCORECARD axes table, and C1's
   kill rule (prereg lines 49-56, amendment 2 block 1) forbids any axes-table byte change, verified identical.
5. Live state at HEAD 07f83e6 (head advanced during review from d6fe8a1): all four counters green — C1 markers=0
   headings newest-first (triple 17 44 78), C2 F1=2 rows=132, C3 tool present flags=0, K4 grounded=9 kill_violations=0.

## Attack log
None. No predicate, target, case set or axis appears wrong or gameable.

## Residual risk / gaps
- K2 gate-check was not re-run live this review (its dependency map shows no cross-claim inputs; receipts
  c2-gate.tsv exist per lane records). Counterfactual conclusions rest on tool-read dependency analysis, not on
  re-execution of the full gate.
- K4 was run at tip 07f83e6 (not the earlier d6fe8a1 observed in the first log read); both are post-landing commits.
