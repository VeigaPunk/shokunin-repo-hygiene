# R41w2critic06 — critic report: falsifying the round-41 claim verdicts (C1, C2, C3)

Seat: R41w2critic06 (role critic, wave 2). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Tip checked: 1d41c13574db80fdd9a4bde490b712da7ce2a85f.
Anchors: base 7eebc183f2685d1ea9b004b4de22c09a8a4035a7; measured bffcc0f660ff36eb8add3f61582748a7af019a5b; instruments 6682b98175b995ee4646ffd1ea6bd8a12cd353dd; freeze e2a74312af4233963e44e4dbb38838ece07b8bd2.
Receipts copied into `.ufo/waves/round-41/w2/R41w2critic06/` (c1/c2/c3/r1 counter runs at HEAD, sources census, C2 variant log, C3 class-swap log). Scratch dir `/fast/scratch/hyaku/souji-r41/R41w2critic06` deleted after copying. No tools installed or upgraded. Nothing written to the lane, tracked files, or fleet.

## Verdicts

| claim | counted target at tip | arguments that survive | verdict |
|---|---|---|---|
| C1 calibration (3 CORRECTION lines) | met: `items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`, rc 0 | A3 (I3 correction misdescribes the filed receipt and the filed token); A4 (I4 mismatch rests on a scope the filed line does not assert; N4 already names the scope gap) | Verified on the frozen target. Calibration defect survives in the correction prose: not clean for admission unless the L1 accepts A3 as a named limit. |
| C2 operability (freeze-check tool) | met: `cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red`, rc 0 | B1 (blank `Base:` is clean, although BASE-UNRESOLVED is a documented class); B2 (the tool never freezes the preregistration itself, Target, or Control: post-freeze edits are clean); B3/B4 (blank Counter/Population, dropped claim header, duplicate key are clean) | Verified on the frozen 21 cases. Operability axis is harmed by B1 (a documented finding is not emitted) and by B2 (a rule-1 freeze is not enforced). Not clean for admission unless the L1 files B1–B4 as named limits and accepts them. |
| C3 coverage (19-site battery) | met: `sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10`, rc 0 | none | Verified. Both attacks I ran fail (C3-X1, C3-X2 below). |

No Kill line of C1, C2 or C3 fires on the frozen counters. The survivors are arguments the frozen populations do not hold.

## Frozen-artifact identity (checked, all clean)

Commands:
```
git rev-parse HEAD                                   -> 1d41c13574db80fdd9a4bde490b712da7ce2a85f
git log --oneline --graph 7eebc18..HEAD              -> e9dc38d, 6682b98, e2a7431, a114412, 97eeb01, 119c26f, 31e4d3e, 1d41c13
git diff --stat e2a7431 HEAD                         -> 13 files changed, 3754 insertions(+)   (no deletions, no frozen file touched)
git rev-parse <freeze>:<p> vs HEAD:<p>               -> SAME for census/round-41/{c1,c2,c3,r1}-counter.py, {c1-items.tsv,c2-cases.tsv,c3-sites.tsv,preregistration.txt}, tools/souji-worktree-drift.py, census/round-41/controls, score-candidate.sh
git rev-parse <instr>:<p> vs <freeze>:<p>            -> SAME for the four counters, three populations, tool
sha256sum census/round-41/*-counter.py *.tsv tools/souji-worktree-drift.py
  8860dc7a… c1-counter   85ffe263… c2-counter   9ef99e8f… c3-counter   8352eed4… r1-counter
  2d2a548e… c1-items     4854335a… c2-cases     be363c0d… c3-sites     b2a603cf… drift tool
  (every digest matches the preregistration pin)
git merge-base --is-ancestor bffcc0f 7eebc18         -> ancestor (measured revision precedes base)
git merge-base --is-ancestor 7eebc18 6682b98         -> ancestor (base precedes instruments)
git merge-base --is-ancestor 6682b98 e2a7431         -> ancestor (instruments precede freeze)
git merge-base --is-ancestor e2a7431 1d41c13         -> ancestor (freeze precedes tip)
```
Registry: `git diff e2a7431 HEAD -- corpus/SOURCES.md` is a pure insertion (`@@ -209,6 +209,7 @@`, one S258 row, one paragraph appended under the round notes); no existing row changed.
Census: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` -> exit 0 (receipt `sources-census-validate-at-HEAD.txt`).
Not run: `tools/souji-registry-agreement.py` (N11). Its interface needs `--list-rev` and it returned `COULD-NOT-EVALUATE derived facts are trivial` at both 7eebc18 and HEAD with `--list-rev e2a7431`; I did not verify N11 further.

## Committed counters run by me at HEAD (receipts copied)

```
python3 -B census/round-41/c1-counter.py --root . --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1
rc=0

python3 -B census/round-41/c2-counter.py --root . --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch /fast/scratch/hyaku/souji-r41/R41w2critic06
(21 case lines, all PASS)  real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8
rc=0

python3 -B census/round-41/c3-counter.py --root . --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch /fast/scratch/hyaku/souji-r41/R41w2critic06
PRISTINE ok rc=0 probes=21 ... 19 SITE lines all "killed"
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2
rc=0

python3 -B census/round-41/r1-counter.py --root . --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch ...
SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106
rc=0
```
The do-nothing controls (`controls/c*-control.txt`) were read from their receipts and not re-run.

## C1 — arguments

**A1. "I1's 9 is right under some reading, so 'wrong by any reading' is false."** Survives? No. Counts at bffcc0f: registry rows containing `worktree.c` = 2; rows containing `v2.56.0/worktree.c` = 0; file-wide lines containing `worktree.c` = 3; rows containing `worktree` = 26; rows whose source cell contains `worktree` = 7; rows whose source, anchor and teaches cells together contain `worktree.c` = 1. None is 9. The derived `rows=2` is independent of the counter (grep at bffcc0f, not the counter).

**A2. "S258's sourced leg is fake (quote or snapshot wrong)."** Survives? No. Row S258 has 11 cells; cell 7 quotes `"prune missing working trees older than <time>"`, which matches `census/round-41/sources/git-v2.56.0-builtin-worktree.c` line 255 exactly (`grep -n -F`). Snapshot sha256 `af2bd523e1c8…` matches `SHA256SUMS`; the v2.55.0 snapshot sha `2c8e8a8e…` matches too. Line 229 is the `should_prune_worktree(the_repository, …)` call and line 259 is `expire = TIME_MAX;`, both as the row states. `diff` of lines 171–266 between v2.55.0 and v2.56.0 shows one change, at 59c59 (= line 229). Line count 1541 matches. Row tier A, status mined, opened 2026-10-28 (cells 3, 7, 8).

**A3. "The I3 correction misdescribes the filed statement and its receipt."** Survives. Facts: (a) `like-for-like` occurs 0 times in `SCORECARD.md` at bffcc0f; the filed claim is a before/after table row, so the `filed=like-for-like` token is the lesson's paraphrase, not a quote, and the counter checks only the anchor. (b) The SCORECARD C1 row (line 791) names `census/round-40/records/c1-before.txt` for the before column and `c1-after-d.txt` for the after column. The lesson's I3 prose and the counter's population both read `c1-after-h.txt` for the after value. (c) The values agree: `c1-after-d.txt` also reports `register_cells=3` on `--register census/round-40/cells.tsv`, and `c1-after-h.txt` reports `register_cells=3` on the same register, so the derived `before=6,after=3` is correct. The `before` register is `census/round-39/cells.tsv`, the after register is `census/round-40/cells.tsv` (command headers, verified). The defect is in the description of the filed text, not in the derived value. The counted target still passes.

**A4. "The I4 mismatch is a scope artefact: LOG.md:1909 records the error text, so 'error-text-recorded' is true."** Survives as a calibration defect, with N4 already naming the scope gap. Facts: `flagged as potentially` appears once in `LOG.md` (line 1909, which carries `Invalid prompt: your prompt was flagged as potentially violating our usage policy`) and 0 times under `census/round-40/waves/` (exact grep, and a whitespace-tolerant search across newlines, both 0). `Invalid prompt` appears 0 times in `census/round-40/`. The filed sentence at 1909 that is contradicted is "All wave evidence is captured under `census/round-40/waves/`", which the counter does not test by name. The CORRECTION line I4 reads `filed=error-text-recorded derived=occurrences=0`, which a reader takes as a retraction of a true statement. The lesson's prose (§ Corrections, I4) states the scope, so this is mitigated, not clean.

**A5. "The registry changed by more than a pure append, or CORRECTION lines are malformed/in a fence."** Survives? No. `git diff e2a7431 HEAD -- corpus/SOURCES.md` is one row plus one note appended; the three `CORRECTION` lines (round-41.md lines 57, 72, 88) are plain and well-formed; none is inside a code fence.

## C2 — arguments

Counter-level: all 21 cases, both stub controls, real and retro legs pass (receipt above). Hidden-case audit: I ran the frozen tool at HEAD over eight variants in a scratch clone of the lane (a `git clone` of the lane; each variant is one commit in the clone; the lane was not written; the tool bytes were unchanged). Commands: `python3 -B <clone>/tools/souji-freeze-check.py --root <clone> --prereg census/round-41/preregistration.txt --rev <variant tip>`. Output (receipt `c2-hidden-case-variants.txt`):

```
== V0-head                      rc 0  SUMMARY claims=3 findings=0
== V1-blank-Counter-C1          rc 0  SUMMARY claims=3 findings=0
== V2-blank-Base-C1             rc 0  SUMMARY claims=3 findings=0
== V3-blank-Population-C1       rc 0  SUMMARY claims=3 findings=0
== V4-target-edited-post-freeze rc 0  SUMMARY claims=3 findings=0
== V5-claim-header-typo         rc 0  SUMMARY claims=2 findings=0
== V6-dup-Counter-bad-digest    rc 0  SUMMARY claims=3 findings=0
== V7-control-edited-post-freeze rc 0 SUMMARY claims=3 findings=0
```

**B1. A blank `Base:` line is clean, although the documented class BASE-UNRESOLVED covers it.** Survives. c2-counter.py docstring: "BASE-UNRESOLVED Base is not a full40 that resolves to a commit". Tool `tools/souji-freeze-check.py` line 148 is `if f.get("Base"):`, so an empty value skips the check; FIELD-EMPTY (line 145) is applied to Target and Kill only. V2 is rc 0 with zero findings. No frozen case covers a blank value. This is a documented finding the tool does not emit. Strongest argument against the C2 operability axis.

**B2. The freeze is not enforced on the preregistration, Target, or Control.** Survives as a named omission. Rule 1 of the preregistration forbids changes to the file, its Counter, Population, Control and tool after freeze. The tool compares only Counter and Population blobs to the freeze (`check_path_sha`, lines 129–132); Control is read from the freeze blob (lines 168–169), so an edited control is invisible; the preregistration at --rev is never compared with the freeze. V4 (Target edited after freeze) and V7 (control last line changed to `EXIT=0`) are rc 0 clean. C2's documented scope does not include these, so the frozen target is not failed, but the lesson's M41-1 "fix" text does not disclose the gap.

**B3. Blank Counter / Population lines are clean (V1, V3).** Survives as a grammar hole (`if f.get("Counter")`, line 156; `if f.get("Population")`, line 159). The digest pin silently disappears.

**B4. A mistyped claim header silently drops the claim; a duplicate key silently keeps the first (V5, V6).** Survives. `HEADER` (line 26) rejects `## C2a`, so that block is not a claim and no finding is emitted (claims=2). `parse_claims` (line 76) keeps the first occurrence of each key, so the second `Counter:` line with a wrong digest (V6) is ignored.

**B5. The retro leg does not discriminate.** Survives as a weakness only. Any tool that exits 1 with ≥3 findings on round-40 passes retro; the real leg checks only `claims=3 findings=0`. The stub controls do reject always-clean and always-findings tools, so the operability verdict is not void.

## C3 — arguments

**C3-X1. The fixture sniffs the `ZZ-MUTANT` label or the `mut-S<NN>.py` name, so only label-sentinel mutants are killed.** Does not survive. I wrote 19 mutants, each rewriting one site's class to the next real class in sorted order (no ZZ label, file names `tNN.py`), and ran the frozen fixture on each. Every mutant is KILLED-EXACT: the failing probe set equals the frozen c3-sites.tsv mapping, rc 1 (receipt `c3-real-label-class-swap.txt`; pristine rc 0, 21/21). The fixture asserts `REFUSAL <expected class>:` with rc 2 per probe (fixture lines 74–82); it does not read the tool's file name or bytes (no basename or sha logic found).

**C3-X2. The tool has refusal sites outside the 19-site population.** Does not survive. Site count from the tool at HEAD: `grep -c 'Refusal('` = 19, which is the class definition (line 92) plus 18 `raise Refusal(` sites (lines 136, 137, 140, 161, 173, 175, 178, 180, 182, 271, 276, 286, 300, 317, 341, 348, 425, 435), plus the literal `"REFUSAL USAGE: --timeout must be >= 1"` at line 448, which is site S19 in the population. Exit-2 returns are only lines 449 and 454. `REGS-CHANGED` and `PRUNABLE-CHANGED` (lines 374, 376) are drift rows (exit 1), not refusals. `except` clauses that map OSError to Refusal (line 134 → RECORD-MISSING, line 267 → JSON-NOT-REGULAR) are inside the population.

**C3-X3. The fixture does not execute the tool (N6).** Does not survive. Shim audit `census/round-41/records/shim-audit.txt` shows 21 tool invocations for the landed candidate (R41executor04), and my mutant runs changed the tool's output for each probe, so the probes execute the tool.

Note: C3 kills by label only, as the predicate states ("rewriting any one site's class label"); site deletion or exit-code mutants are outside the claim.

## Named limits this report adds (not in N1–N12)

- C2: B1 (blank Base false-clean vs documented BASE-UNRESOLVED), B2 (prereg/Target/Control unfrozen-checked), B3 (blank Counter/Population), B4 (dropped header, duplicate key).
- C1: A3 (I3 correction names after-h, the SCORECARD row names after-d; `like-for-like` not in SCORECARD).

## Commands run (exact)

1. `git rev-parse HEAD`; `git log --oneline --graph 7eebc18..HEAD`; `git diff --stat e2a7431 HEAD`; blob comparisons with `git rev-parse <rev>:<path>`; `git merge-base --is-ancestor` checks (the first attempt was garbled by a shell redirect; re-run cleanly, results above).
2. `sha256sum census/round-41/*.py census/round-41/*.tsv census/round-41/preregistration.txt tools/souji-worktree-drift.py tools/souji-freeze-check.py`.
3. `git show bffcc0f:corpus/SOURCES.md | grep -E '^\| S[0-9]+ ' | grep -c 'worktree\.c'` (= 2) and the `v2\.56\.0/worktree\.c` form (= 0); `git show bffcc0f:corpus/SOURCES.md | grep -c 'worktree\.c'` (= 3); `git show bffcc0f:LOG.md | grep -n 'flagged as potentially'` (= line 1909); `git grep -c 'Invalid prompt' bffcc0f -- census` (= none); `git show bffcc0f:census/round-40/records/c1-{before,after-h,after-d}.txt` headers and `register_cells=` values.
4. `git show HEAD:corpus/SOURCES.md | grep -E '^\| S258 '` with awk cell split; `sha256sum census/round-41/sources/*.c`; `grep -n -F 'prune missing working trees older than <time>'`; `sed -n 253,260p`; `diff <(sed -n 171,266p v2.55) <(sed -n 171,266p v2.56)`.
5. The committed counters at HEAD (c1, c2 with `--scratch`, c3 with `--scratch`, r1 with `--scratch`) — receipts above.
6. Scratch-clone hidden-case audit of the freeze check (V0–V7), run as an inline Python driver in the scratch clone; each variant committed only in the clone (`GIT_AUTHOR_*`/`GIT_COMMITTER_*` set through the environment); the clone was restored to HEAD after each variant.
7. Real-label class-swap audit of the C3 fixture (19 mutants) through an inline Python driver; fixture run as `python3 -B <fixture> --tool <tNN.py> --work <scratch>/work-NN`, `TMPDIR` in scratch.
8. Tool site enumeration: `grep -n -E 'REFUSAL|Refusal|refus|exit\(2\)|return 2|COULD|sys\.exit|raise ' tools/souji-worktree-drift.py` at HEAD (copied to scratch).
9. `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` -> exit 0.
10. `tools/souji-registry-agreement.py --root . --rev <r> --list-rev e2a7431` at 7eebc18 and HEAD -> `COULD-NOT-EVALUATE derived facts are trivial`, rc 2 (N11 not verified).

## Checks the L1 should run before admission

- `python3 -B census/round-41/c1-counter.py --root . --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f` (done here, rc 0).
- `python3 -B census/round-41/c2-counter.py …` and `c3-counter.py …` (done here, rc 0).
- Decide whether B1–B4 are named limits for C2 and whether A3 is a named limit for C1. I recommend they be named (not fixed: the instruments are frozen).
- Lane-wide test suite: not run by me (not in my assignment). Note: the lesson's claim that C2/C3 are reproducible in the lane is confirmed only for the four counters listed above.

Verdict for R41w2critic06: C3 survives falsification; C1 and C2 meet their frozen targets, and the arguments that survive (A3, A4 for C1; B1–B4 for C2) are real calibration/operability defects the L1 must weigh before admission.
