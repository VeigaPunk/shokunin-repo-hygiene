# Round 71 — verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Dispatched 2026-11-06T16:32:01-03:00, completed 2026-11-06T17:25:05-03:00 (`launch souji round=71 pgid=3816621 driver=hyaku-inline attempt=1` / `complete souji round=71; hyaku-inline attempt=1`, `.ufo/watchdog.log`, digest copied because the log is mutable). Lane base `8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0`, lane tip at closure `9332fde2df586d33fd2717fda4821d99e7fb3bd1`. The closure ran every check below on 2026-11-06 (~20:25Z) over committed bytes. It executed no sibling gate. The only live runs were two throwaway temp-repo probes of the mechanism and a re-fetch of the three cited pages.

## Conformance

| check | command | result |
|---|---|---|
| report landed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H %ci' -- .ufo/reports/round-71/souji.md` | `souji-shokunin <souji@shokunin.local>` `a651cdd64abf9648180768c80f12acff781911a5`, committed 17:24:26 -0300. That is after lane tip `9332fde2` (17:23:16) and before the `complete` line (17:25:05) |
| `SHONEN` heading, one line per box | read the report; `grep -c '^- \[' SHONEN.md` → 4 | `## SHONEN` has 4 `[~]` lines, one per box, each with a pointer. No `[x]` |
| cited lane commits exist and are ancestors of the branch ref | `git rev-parse --verify <c>^{commit}` and `git merge-base --is-ancestor <c> master` for `8b9345b1`, `aa91d1ca`, `a1db6c85`, `52e8c3fa`, `1c2239cd`, `45a94c83`, `f13d575e`, `c0dd4476`, `9332fde2` | All 9 resolve and are ancestors of `master`. All 8 round commits are authored by `souji-shokunin` (`git log --format=%an 8b9345b1..9332fde2 \| sort \| uniq -c` → `8 souji-shokunin`) |
| no uncommitted round work | `git -C <lane> status --porcelain` | empty |
| pushed | `scripts/hyaku/jj-lane.sh state <lane>` | `branch=master local=9332fde2… remote=9332fde2… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git ls-remote origin refs/heads/master` → `9332fde2…` |
| prompt carries the template contract | read `.ufo/prompts/souji-round-71.md` §1–§5 | Present: §1 MISSION/AXES binding, §2 1–3 claims including the lowest-axis rule, §2b frontier step, §3 L2 floor of ≥8 in one batched swarm, §4 report path, sections, SHONEN and marker rule, §5 commit-then-push, push scope and L0 channel; write scope at :448; report-lands-last with the pushed hash at :516. The hyaku addendum §6 follows. The prompt was committed by the lane identity (`40c338c0`, 16:31:59) |
| writer bytes | `git show <rev>:tools/souji-receipt-write.py \| sha256sum` | candidate `a1db6c85` → `56b6be03…5207`, which equals the `# slot new=` sha in `c1-after.txt`. Repaired `f13d575e` and tip `9332fde2` → `b7790001…244d`, which equals the slot sha in `c1-at-repair.txt` and the `REPAIRED` sha in `repair-canfail.txt` |
| frozen instruments unchanged after the freeze | `git diff --stat aa91d1ca 9332fde2 -- census/round-71/{c1-counter.py,c1-matrix.tsv,c2-harness.py,c2-mutants.json,preregistration.txt,controls}`; `sha256sum` | Empty diff. Counter `7e5a694a…a3cc` at both `aa91d1ca` and `9332fde2`, equal to `instrument_sha256` / `counter_sha256` in `c1-after`, `c1-at-repair` and `c2-after` |

## Claim re-checks

**C1 — operability: the writer's clean-tree witness can no longer be forged through a clean filter driver or a repository-local `core.fileMode=false` (sourced S306–S308).** VERIFIED: re-measured, plus mechanism reproduced and gate evidence verified.

- Writer surface (`grep -c` over `tools/souji-receipt-write.py`):

  | pattern | base `8b9345b1` | candidate `a1db6c85` | tip `9332fde2` |
  |---|---|---|---|
  | `GIT_ATTR_SOURCE` | 0 | 7 | 7 |
  | `core.fileMode=true` | 0 | 2 | 2 |
  | `RECEIPT-FILTER-DRIVER-SET` | 0 | 2 | 2 |
  | `RECEIPT-CHECKIN-CONVERSION-SET\|core.checkStat=default\|core.trustctime=true` | — | 0 | 5 |

  The wave repairs landed after measurement, as the report says.
- Mechanism, re-derived by the closure in a fresh temp repo (git 2.56.0):
  - fileMode: with local `core.fileMode false` and `chmod +x f`, `git status --porcelain` → empty; `git -c core.fileMode=true status --porcelain` → ` M f`.
  - filter: a same-size edit of `g` with a clean driver that emits the committed bytes, and `.gitattributes` supplied only through a `GIT_ATTR_SOURCE` tree. `GIT_ATTR_SOURCE=<tree> git status --porcelain` → empty; plain `git status --porcelain` → ` M g`.
  - Both forgery routes are real. A size-changing edit was reported even under the filter, which agrees with the lane's size-changing probe.
- `grep -E '^(SUMMARY|EXIT=)' census/round-71/records/c1-after.txt` → `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, `EXIT=0`. This is byte-equal to the frozen predicate (`preregistration.txt` :73–76) and to the report. Receipt `rev=a1db6c85…`.
- Before: `controls/c1-do-nothing.txt` → `new_forgeries=7 … class_mismatches=7`, `EXIT=1`. Controls, all `EXIT=1` as preregistered:
  - F1 blanket refusal: `new_forgeries=0 new_honest=16 class_mismatches=11`.
  - F2 scrub only: `new_forgeries=5`.
  - F3 pin only: `new_forgeries=5`.
- `c1-at-repair.txt` at `f13d575e` prints the same SUMMARY with `EXIT=0`, so the repairs regressed no frozen row.
- Gate evidence (not executed):
  - Writer selftest receipts `writer-selftest.txt` `cases=40 pass=40 fail=0` and `writer-selftest-repair.txt` `cases=42 pass=42 fail=0`.
  - Counter selftest `counter-selftest.txt` `cases=39 pass=39 fail=0`.
  - `repair-canfail.txt`: R1, R2, R3a, R3b and R4 each `cases=42 pass=41 fail=1`.
  - SKILL.md registry rows at :928–930.
- Qualifications accepted as disclosed, not counted as passes:
  - Three filter-class routes and one stat route forged the frozen candidate. The repairs are measured by selftest and probe, not by the matrix.
  - The predicate is mechanism-agnostic.
  - Honest-repo over-refusal with a driver on a tracked path is unmeasured.
  - AS1/AS2 cannot separate a scrub from an unfiltered dirty tree.
  - The counter rc does not bind the base slot.
  - A same-second in-place edit is a named residual.

  These narrow C1. They do not falsify it.

**C2 — calibration (lowest owned axis, 7): the counter's own selftest kills the five r70-surviving counter mutants X6–X10.** VERIFIED: evidence-verified, with receipt bytes and provenance re-read.

- `grep -E '^(SUMMARY|EXIT=)' census/round-71/records/c2-after.txt` → `SUMMARY label=c2-after-r71 positive_selftest=PASS x_mutants=5 x_killed=5 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0`, `EXIT=0`. This is byte-equal to the report. `counter_sha256=7e5a694a…` is the frozen counter.
- Before: `controls/c2-before-r70.txt` → `x_killed=0 x_survived=5 … score=5`, `EXIT=1`; every X mutant `SELFTEST cases=29 pass=29 fail=0 fate=survived`. The invalidity control CF1 (`positive_selftest=FAIL`) → `EXIT=2`, so a blanket-failing counter is refused.
- Provenance: `c2-mutants.json` names `census/round-70/records/wave-w1/seats/S70MutCounter/mutants/X6.py`…`X10.py`. Those seat files exist at the base `8b9345b1` (`git grep -l X6 8b9345b1 -- census/round-70`), so the mutants predate this round and were not authored with the tests that kill them. This closes the r70 qualification (same-round mutants).
- Ruling on the label: the move is the instrument's ability to report known defects in itself, which is self-assessment, so it counts as calibration.
- C2 is qualified:
  - The counter under test was frozen in the same commit as the before-arm (prereg disclosure iii).
  - A neighbouring `clean_env` defect still passes the selftest (S71CriticClaims), so the claim is specific to this mutant set.

**Harm check.** `git diff --numstat 8b9345b1 9332fde2 -- SCORECARD.md LOG.md SKILL.md` → `14 0`, `10 0`, `3 0`: additions only, comprising two capability rows, the r71 bullet and measurement table, and the R70-D1 correction. No axis score changed (calibration 7, coverage 8, operability 8). The 59 carried rows keep their class (`class_mismatches=0`), and the regress fixture is PASS on both slots.

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 re-measured; both mechanisms reproduced by the closure; frozen predicate byte-equal |
| calibration | improved | C2 receipt bound to frozen counter bytes; mutants provably from r70 |
| coverage | unchanged | no claim; the 11 new matrix rows are instrument rows for C1 |

## Discernment spot-check (sources re-opened by the closure)

The live pages were re-fetched on 2026-11-06. Each is byte-identical to the committed capture (sha256 `37aa8407…9226` git-config, `534c674f…f9d1` git, `0a1e8015…6aee` gitattributes). Quotes were located in the tag-stripped, whitespace-normalized text.

| item | lane decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S308 git-config(1) `core.fileMode` | admit, A, mined | live https://git-scm.com/docs/git-config (830605 bytes) | agree | Quote found at offset 82016 exactly; 17 words. It grounds what the closure's temp-repo probe showed: a local `false` hides a mode change, and a per-call `-c` pin overrides it |
| S306 gitattributes(5) `filter` clean | admit, A, mined | live https://git-scm.com/docs/gitattributes (131046 bytes) | agree | Quote found at offset 17513; 15 words. The narrowed `teaches` (check-in conversion only, the status consequence attributed to the probe) is the honest scope |
| S309 git(1) ENVIRONMENT `GIT_ATTR_SOURCE` | reject (row kept) | live https://git-scm.com/docs/git (244227 bytes) | agree | Offset 40119 reads "GIT_ATTR_SOURCE Sets the treeish that gitattributes will be read from." That sentence omits "instead of the worktree"; the OPTIONS entry (S307, found at 13322) carries it with the env equivalence. The duplicate-anchor reason and the flip condition are correct |

Newly written rows re-checked:
- S310 quote "When the GIT_ATTR_SOURCE environment variable or --attr-source command line option are used, this configuration variable has no effect." was found at the re-anchored offset 54097; 18 words.
- S311 `ident` quote was found at offset 17004; 21 words.
- Both are ≤25 words.

Counts and census:
- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `ok`, EXIT=0, with W04 duplicate-URL warnings only.
- Rows 228 → 234 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` at `8b9345b1` and the tip).

## Trend verdicts

- **expansion: improved.** The new `corpus/knowledge/filter-filemode-witness.md` (58 lines) cites S306, S307, S308, S310 and S311, all `mined`, on ground no earlier entry held: attributes and stat settings as clean-tree witness routes. The README frontier section was added, along with two capability rows.
- **quality: improved.** Three items were found false and marked by appended corrections:
  - the false r67 sentence about `GIT_CONFIG_GLOBAL`/`NOSYSTEM` pinning a local `core.fileMode` (`common-dir-route-receipt-writer.md`, appended correction; M1);
  - the r70 D1 count (SCORECARD correction);
  - the r70 D2 line 55 (erratum in `round-70.md`).

  No admitted entry failed its re-check.
- **discernment: improved.** The non-author spot-check agrees with the gate on two admits (S306, S308) and the reject (S309). The two in-round row corrections (S309 reason, S310 status) were driven by seats and are recorded in the lesson. The lane filed `unchanged` only because no outside check had run.

## Routed defects (lane fixes next round)

- **D1 (report wording, LOW).** The report says the controls were committed "before any candidate bytes existed". For C2 the candidate is the r71 counter, frozen in the same commit `aa91d1ca` as its before-arm (prereg disclosure iii). Next report: state this per claim.
- **D2 (calibration, carried).** S71MutCounter F1: `claim_upheld` ignores the base slot, and Y6/Y10 drop `base_forgeries` 7 → 2 with EXIT=0. The lane routed this to r72; keep it on the queue until a counter binds the base-slot rc.
- **D3 (operability, measurement gap).** None of the following has a matrix row:
  - over-refusal of an honest repo with a configured driver on a tracked path;
  - the AS1/AS2 scrub-vs-unfiltered indistinguishability (S71MutCounter F2);
  - the three repaired filter-class routes and the stat routes, which are measured only by selftest and probe.

  The next counter should carry them as rows.
- **D4 (calibration).** The neighbouring `clean_env` defect passes the r71 counter selftest (S71CriticClaims). Add a killing case or a frozen mutant.
- **D5 (cross-lane, operator/aggregator).** S71Connector lists 13 sibling clean-tree gates (kaidoku, kama, mori, tameshi, audio) without a `GIT_ATTR_SOURCE` scrub, a `core.fileMode` pin or a filter-driver check (`census/round-71/records/wave-w1/seats/S71Connector.md`). Route this to the owning lanes. It is not souji's write scope.
