# R42w2executor03 — held-out generation for the landed C2 tool (falsify)

Target: `tools/souji-freeze-check.py` at tip 3105a63b (git blob 384fc05f280f14496c7bf9e76a0bef699d9834f7, identical in the working tree; sha256 9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6).
Attack surface: the grammar in the docstring of `census/round-42/c2-counter.py` (lines 1-57) and the tool's own docstring (lines 2-29).
Seat directory (all evidence below lives here): `.ufo/waves/round-42/w2/R42w2executor03/`.

## Verdict
**The tool is wrong in one real, reproducible way (glob metacharacters in the preregistration path: wrong FREEZE-REV in 128 of 131 scenarios that had a glob-matching earlier file, including a false GREEN). Everywhere else it agrees with the oracle once five points the docstrings leave open are fixed to the tool's reading, and I judge the tool's reading right or defensible on four of those five; the fifth (Control is never checked for post-freeze edits) is a gap against the frozen rules.**
No tool crash (0 Tracebacks in 1600 scenarios), output always sorted, all 71 refusal scenarios exit 2 with `REFUSAL COULD-NOT-EVALUATE`, no SUMMARY line on exit 2.

## Method (what was actually built and run)
- `oracle.py` — independent implementation derived from the two docstrings only (no tool code read; I read the tool file only for lines 1-33 = docstring, 116-125 appeared in one grep context after the glob cause was already identified from scenario tags). It works on a scenario *model* (commit timeline), never asks git. It also contains the generator, the git fixture builder, and a driver.
- Generator (seeded `random.Random("<seed>:<index>")`, so any single scenario is reproducible with `--only`): per scenario 1-4 claims (0 for NO-CLAIMS), keys in random order with missing/empty/duplicate/spacing variants (`Key: v`, 3-space, tab, `Key:v`), decoy lines (`Baseline:`, `- Base:`, ` Base:`, `base:`, `Key :`), `###` lines, 9 malformed-heading shapes, stray malformed headings, a trailing `## Frontier` section carrying decoy keys, preamble decoy keys, LF/CRLF files with/without final newline, missing/duplicated `Round:`; git timelines with 0-2 pre-freeze and 0-3 post-freeze commits, files added at base / pre / freeze / post, edited (pre and post), edited-and-reverted, deleted, replaced by symlink, counter/population as symlinks (3 target kinds), counter reached through a symlinked directory component, shared paths between claims, paths with spaces / unicode / `[ ] * ? ' "` / leading `-` / double space; dispatch-class files (17 names incl. decoys `dispatch.txt`, `w1-spec.json.bak`, `round-420`, `round-41`), at any commit, deleted later, symlinked, mixed-case, and brought in through a side branch merged before or after freeze (branched before or after freeze); `--rev` = tip or a mid commit; prereg edited post-freeze, deleted and re-added, glob-named with a decoy file; Base = ancestor / unknown 40-hex / side-branch commit / non-hex / abbreviated; refusals (unknown rev, short rev, absent prereg).
- Comparison per scenario: exit code, (claim, CLASS) multiset, `SUMMARY claims=<n> findings=<m>`, plus the detail the docstring pins (`HEADING-MALFORMED line=<n>`, `KEY-DUPLICATE <key>`).
- Fixture rules honoured: every repo under `/fast/scratch/hyaku/souji-r42/R42w2executor03/`, every git call `-C <dir>`, `rev-parse --show-toplevel` asserted equal to the dir before the first commit, identity via `GIT_AUTHOR_*`/`GIT_COMMITTER_*` env only, `GIT_CONFIG_GLOBAL=/dev/null`; scratch deleted before yield (verified). Lane files untouched.
- Oracle readings (`CFGS` in oracle.py): `literal` = plainest reading of each undefined point; `calib` / `calib-noctl` / `calib-full` = literal plus the tool's observable behaviour on the open points (see causes). `analyze.py` finds, per scenario, the smallest flag subset that reconciles oracle and tool.

## Commands run and observed output
```
python3 -B oracle.py --seed 4242 --n 1000 --scratch <scratch> --out results-seed4242.json     (summary-seed4242.txt)
SEED 4242 N 1000 TOOL /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py
CFG literal      SCENARIOS 1000 agree 505 disagree 423 undetermined 72
CFG calib        SCENARIOS 1000 agree 666 disagree 262 undetermined 72
CFG calib-noctl  SCENARIOS 1000 agree 854 disagree 74 undetermined 72
CFG calib-full   SCENARIOS 1000 agree 901 disagree 99 undetermined 0
python3 -B oracle.py --seed 777 --n 600 ...                                                   (summary-seed777.txt)
CFG literal      SCENARIOS 600 agree 321 disagree 238 undetermined 41
CFG calib        SCENARIOS 600 agree 416 disagree 143 undetermined 41
CFG calib-noctl  SCENARIOS 600 agree 514 disagree 45 undetermined 41
CFG calib-full   SCENARIOS 600 agree 540 disagree 60 undetermined 0
python3 -B analyze.py --seed 4242 --n 1000 --results results-seed4242.json ...  > analysis-seed4242.json
python3 -B analyze.py --seed 777  --n 600  --results results-seed777.json  ...  > analysis-seed777.json
bash repro-glob-freeze.sh <tool> <scratch>                                                     (repro-glob-freeze.out)
python3 -B probe-value-forms.py <tool> <scratch>                                               (probe-value-forms.out)
python3 -B probe-gaps.py <tool> <scratch>                                                      (probe-gaps.out)
```
(An earlier 400-scenario run of an earlier generator revision, seed 4242, produced the first cause list; its raw file was discarded. The numbers in this report are from the two final files above, produced by the committed `oracle.py`.)
"undetermined" = the oracle declines to predict because a Counter/Population value is out of grammar (`amb:value-*` scenarios); they are scored by `calib-full`.

## Counts
Scenarios: **1600** (seed 4242 x 1000, seed 777 x 600; 200 required). Every scenario ran the tool once.

| view | agree | disagree | note |
|---|---|---|---|
| literal docstring reading | 826 | 661 | 113 undetermined |
| fully calibrated (`calib-full`) | **1441** | **159** | 0 undetermined |
| of the 159 calibrated disagreements: not cause G and not cause V | | **0** | every one of the 159 is G (128) or V (31) |

The 159 `calib-full` disagreements split exactly: **128 = glob-in-prereg-path (cause G)** (seed 4242: 79 of its 82 glob-decoy scenarios, 9 of them also carry a malformed value; seed 777: 49 of 49, 6 also malformed value), **31 = malformed-value diagnostic variance without a glob (cause V)** (seed 4242: 20, seed 777: 11). Unexplained (neither G nor V): **0 / 1600**.

## Mismatches grouped by cause, with the verdict on each

Scenarios needing the flag (a scenario can need several; seed 4242 / seed 777):

| # | cause (literal oracle vs tool) | scenarios | who is right against the docstring |
|---|---|---|---|
| G | **PATH containing `[ ] * ?` is treated as a git pathspec glob when finding FREEZE-REV** | 79 / 49 | **TOOL WRONG.** Docstring: "FREEZE-REV is the oldest commit reachable from --rev that adds PATH"; a file named `pre[ab].txt` is added by the freeze commit, not by an earlier commit that added `prea.txt`. |
| C | Control is never checked for post-freeze edits/deletion (oracle: FROZEN-EDITED on Control) | 188 / 98 | **Docstring silent; oracle's assumption.** Not a docstring contradiction, but a gap against preregistration rule 1 ("No Counter, Population, Control ... changes after the freeze commit"). Tool evaluates Control only at FREEZE-REV: `probe-gaps.out`: red -> green after freeze = exit 0 clean. |
| P | header-only (and header + blank lines, and whitespace-only) population is POPULATION-EMPTY (tool: fewer than 2 non-blank lines); oracle literal: only 0 bytes/blank | 162 / 95 | **Docstring silent; tool's reading is defensible** (population = header + >=1 row; `probe-gaps.out`: header+1 row clean, header only red, "has 1 non-blank line(s)"). Needs one docstring sentence. |
| R | CONTROL-NOT-RED reads the *last non-blank line* (`EXIT=<nonzero>`); oracle literal: any/all `EXIT=` lines | 65 / 35 | **Docstring silent; tool stricter and defensible** (`EXIT=0` then `EXIT=1` clean; `EXIT=1` then prose is red; `EXIT=-1`, `exit=1`, empty file red; CRLF/leading/trailing blank clean). Needs one docstring sentence. |
| D | DISPATCH-BEFORE-FREEZE counts a file that was first added at/before freeze even if it no longer exists at --rev; oracle literal required existence at --rev | 24 / 14 | **TOOL RIGHT**: docstring wording "was first added by FREEZE-REV or an ancestor", "covers every file", no existence condition. Oracle assumption wrong. |
| H | a malformed heading that starts with `##` but not `## ` (`##C1`, `##C 1`) closes the open claim in the tool; oracle literal: only a `## ` line closes | 16 / 10 | **Docstring ambiguous** ("runs to the next `## ` line" vs "opens no claim"). Tool's behaviour is the safer one (a typo'd heading must not donate its keys to the previous claim, which would raise spurious KEY-DUPLICATE / mask FIELD-MISSING). Tool right in effect; docstring should say it. |
| V | out-of-grammar Counter/Population value: with a path containing a space the tool falls back to the first whitespace token as the path, so the finding is `COUNTER-MISSING census/c` instead of `COUNTER-DIGEST ... has no sha256=<64 hex>`; no-space paths give the DIGEST diagnostic (`probe-value-forms.out`) | 20 / 11 | **Docstring silent.** Both are red (exit 1); diagnostic is misleading, class inconsistent between space/no-space paths. Low severity. Not a false green/red. |

Total involvement counts for P/R/D/H/C come from `analysis-seed*.json` (`causes` = minimal flag subsets; sum of scenarios whose minimal subset contains the flag).

### Cause G in detail (the defect)
- Mechanism (observed behaviour): the freeze commit is found with `git log --diff-filter=A ... -- <prereg path>`, and the path is evidently passed as a glob pathspec. Whenever an earlier commit added another file the glob matches, that earlier commit becomes "FREEZE-REV".
- Effect 1 (false RED): artefacts added in the true freeze commit read as `COUNTER-/POPULATION-/CONTROL-MISSING ... not present at freeze <earlier commit>`, and `BASE-NOT-ANCESTOR` for a correct Base (96 spurious in seed 4242).
- Effect 2 (false GREEN): dispatch files committed in the true freeze commit, or in between, are "after freeze" for the wrong FREEZE-REV: 111 DISPATCH-BEFORE-FREEZE findings missed across 58 of 82 glob-decoy scenarios in seed 4242. Minimal reproduction, run: `repro-glob-freeze.out`:
  - part A: `census/pre[ab].txt` + decoy `census/prea.txt` added one commit earlier => `FINDING C1 CONTROL-MISSING/COUNTER-MISSING/POPULATION-MISSING ... not present at freeze a0dcb1f04959`, exit 1; the same bytes under the glob-free name `census/pre-ab.txt` => `SUMMARY claims=1 findings=0`, exit 0.
  - part B: counter/population/control exist before the decoy, a dispatch file `.ufo/waves/round-7/w1-spec.json` is added in the freeze commit: glob-named prereg => `SUMMARY claims=1 findings=0` exit 0 (**false GREEN**); glob-free name => `FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-7/w1-spec.json first added at 130192bae8c5, not after freeze 130192bae8c5`, exit 1.
- Scope: affects `[`, `*`, `?` in the --prereg path only if another file the pattern matches was added earlier (`census/pre[ab].txt`, `pre*.txt`, `pre?.txt`: 79 of 82 decoy scenarios disagreed in seed 4242 and 49 of 49 in seed 777; the 3 that agreed did not depend on the freeze index). Counter/Population/Control paths with the same metacharacters (`c[3]-counter.py`, `c3*counter.py`, `c3?.py`, quotes, unicode, leading `-`, double spaces, spaces) were exercised in 289 + 168 scenarios and are handled correctly (no cause-G effect there, because they are read by `rev:path`, not by pathspec). The real preregistrations (`census/round-42/preregistration.txt`) contain no metacharacter, so the landed `real`/`retro_clean` legs are unaffected; this is an operability hole for future preregistration paths, and a hole the 37 counter cases do not cover.
- Fix direction (finding for the L1, no tool edit made): pass the path as a literal pathspec (`:(literal)PATH` or `--literal-pathspecs`).

### Cause C in detail
`probe-gaps.out`, section "control edited AFTER freeze": red -> green: `exit=0 (clean)`; red -> different red: `exit=0 (clean)`. Control deleted at the tip is likewise clean (scenarios 7, 18, ... in seed 4242, tag `deleted-at-tip:control`). FROZEN-EDITED is only ever reported for Counter and Population.

## Everything that agreed (the independent part)
After the five docstring-open points are fixed to the tool's reading and malformed values are excluded, **0** disagreements remain outside G in 1600 scenarios. That covers: all 18 class names that are reachable in the generator, the exact claim label and class multiset, KEY-DUPLICATE per key with the key as detail and "the key is then not evaluated", HEADING-MALFORMED with correct `line=<n>` for the 9 malformed shapes + stray ones, `##C1` vs `## c1` distinctions, `###` not closing/opening, key-order permutations, CRLF files, spacing/tab variants, `Key:v` without space, decoy key lines, keys after a closing `## Frontier` ignored, preamble decoy keys ignored, claim counts 0-4 (`SUMMARY claims=<n>` matched in every non-refusal scenario), dispatch rule across 17 names, `round-420`/`round-41` decoys, mid-history `--rev`, side-branch merges (merged-dispatch scenarios, 134 + 91, branched before or after freeze, merged before or after freeze; agree except where cause G co-occurs), symlinked Counter/Population (COUNTER-/POPULATION-SYMLINK alone, no digest comparison, 3 link-target kinds, incl. link-text-digest decoy), symlink replaced by file / file replaced by symlink (FROZEN-EDITED), counter behind a symlinked directory component (COUNTER-MISSING, 80 + 53), shared paths between claims, prereg edited after freeze, prereg deleted and re-added (oldest add wins), Base unknown / side-branch / non-hex / abbreviated (all BASE-UNRESOLVED or BASE-NOT-ANCESTOR as predicted), post-freeze edit/revert/delete of Counter and Population, late-added Counter/Population (MISSING at freeze), refusal modes.

## The oracle's own known gaps
1. **Calibration is not independence.** For causes C, P, R, D, H and V the docstrings do not decide; I recorded the tool's observable behaviour as the `calib*` readings. Agreement under `calib*` on those points proves consistency of the tool with itself, not correctness. Only G and the unexplained residual (0) are independent results.
2. Not generated: BOM or leading zeros in `Round:`, `Round:` after a claim heading, `## C01`-style labels, unicode digits/NBSP/tab in headings (`##\tC1`), headings in fenced code, non-UTF-8 prereg bytes, `\r`-only line ends, exec-bit/mode-only changes (so an edit that changes only the mode is untested), a prereg first added on a side branch or in a merge commit, two parallel adds of the same prereg path, `--rev` as a tag/tree, shallow clone, SHA-256 object format repos, `--root` as worktree/bare repo, repo paths with `\t` or newline, `--selftest` (not attacked here), the exact detail text of any finding other than `line=` and the key.
3. Same-label duplicate headings (`amb:dup-label`, 3 %) are generated, but the oracle only models them as two independent claims with one label; they agreed in every sample, which shows nothing about label-keyed internal state.
4. `Round: abc` / `round: 7` are modelled as "missing Round" (FIELD-MISSING C0); that is my reading, they agreed.
5. Digest-equality, base ancestry and the dispatch set are checked by the model's own replay of the timeline; if the model and the builder shared a defect (e.g. mis-ordering merge commits) both would agree and be wrong. Mitigated only by the independent shapes of the git calls.
6. Exit-2 scenarios compare exit code and absence of SUMMARY only; stderr text was checked for the REFUSAL prefix, not for the reason.
7. No attempt to time-bound the tool or feed it large histories.

## Findings for the L1
- **F1 (defect, tool):** literal-pathspec hole in FREEZE-REV detection; false RED and false GREEN; reproduction `repro-glob-freeze.sh`. Not covered by any of the 37 counter cases.
- **F2 (gap):** Control path is never compared between FREEZE-REV and --rev; preregistration rule 1 names Control as frozen. `probe-gaps.out`.
- **F3 (doc gaps, tool defensible):** docstrings do not define POPULATION-EMPTY, "red" control, whether a malformed heading closes the open claim, or whether deleted dispatch files count; each is a one-sentence fix; the tool's readings are listed above.
- **F4 (diagnostic):** out-of-grammar Counter/Population value with a spaced path is reported as `COUNTER-MISSING <first token>` (misleading) rather than the DIGEST message (`probe-value-forms.out`).

## Evidence pointers (all inside the seat directory)
`oracle.py`, `analyze.py`, `results-seed4242.json`, `results-seed777.json` (per scenario: tags, tool findings, oracle prediction under each reading, diff atoms), `summary-seed4242.txt`, `summary-seed777.txt`, `analysis-seed4242.json`, `analysis-seed777.json`, `repro-glob-freeze.sh` + `.out`, `probe-value-forms.py` + `.out`, `probe-gaps.py` + `.out`.
Reproduce a scenario: `python3 -B oracle.py --seed 4242 --n 1000 --only 266 --scratch <dir>` (seed printed in every run).
Tooling installed/updated: none.
