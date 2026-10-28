# Round 39 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Scope: souji round 39, hyaku run 11, attempt 1. Lane base `ed30b7f5b77939c9073348d810730bc4f355708d`;
lane tip and `origin/master` at closure `0242085909fb6a4ee041c5443d76316ac6d59d4b` (branch `master`,
jj-colocated). Report `.ufo/reports/round-39/souji.md` (commit `d21910cee371f22b4870b511d9c4fdb079da5404`).
This reviewer wrote no lane file, ran no lane counter (`c1-counter.py`, `c2-counter.py`,
`c3-counter.py`): a claim resting on a lane-owned instrument is evidence-verified against its committed
receipt and re-derived independently over committed bytes. The artifacts under test (the citation tool
bytes at base and tip, the two r39 fixtures, the five consumer fixtures) were executed read-only from a
scratch root, which is a plain measurement of the artifact, not the lane's counter. Every command below
was run 2026-10-28 from `/home/vgpnk/Projects/shokunin` (fleet root) or
`/home/vgpnk/Projects/shokunin/souji-shokunin` (lane); scratch root `/fast/scratch/hyaku/closure-r39`.

## Conformance (step 1)

| check | command | observed | verdict |
|---|---|---|---|
| report path + attribution | `git log --format='%an <%ae> %H %s' -- .ufo/reports/round-39/souji.md` | one commit `d21910c`, `souji-shokunin <souji@shokunin.local>`, "round-39: souji report" | pass |
| report lands last | `%cd` of `d21910c` vs of lane tip `0242085` | report committer `15:40:44 -0300` > tip committer `15:39:47 -0300` (report author date `15:37:48` predates the tip, the commit does not) | pass |
| cited lane commits exist and are ancestors of the branch | all 31 distinct hashes named in the report (22 round-39 + 9 errata r38 commits + base): `git rev-parse --verify <h>^{commit}` then `git merge-base --is-ancestor <h> master` | 31/31 resolve, 31/31 ancestor of `master` (`ed30b7f`, `b769bfb`, `bbd9b97`, `601195a`, `c0b007b`, `50972f0`, `094e531`, `790d16b`, `2201778`, `d4c1755`, `f8ba3f3`, `e9958ee`, `2605bf2`, `5230a34`, `a8e6d75`, `9440270`, `a6fe389`, `2f6e981`, `5441045`, `8f1c808`, `c2dcd62`, `0242085`, and `6949319 78ea25a f10a3a8 20eea73 a512efb 9b9e2f8 cb5737a be66886 c5050ea`) | pass |
| lane pushed, no uncommitted round work | `scripts/hyaku/jj-lane.sh state …/souji-shokunin`; `git -C souji-shokunin status --porcelain` | `branch=master local=0242085… remote=0242085… ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty; `ls-remote origin refs/heads/master` prints `0242085…` | pass |
| `SHONEN` heading, one line per box | `grep -c '^## SHONEN'` → 1; four following `- [~]` lines; `SHONEN.md` has 4 boxes | 1 heading, 4 `[~]` lines each with a resolvable pointer (`SKILL.md`, S247–S250, `LOG.md` §Round 39, `census/round-39/preregistration.txt`, `PROVINCE.md`); no `[x]`; `SHONEN.md` unchanged this round | pass |
| prompt carries the template contract | `.ufo/prompts/souji-round-39.md` §1–§5 + §6 addendum (committed `36d25db`, `souji-shokunin`) | round-level items present: mission/axes binding §1, L2 floor §3 (≥8, one batched call), commit-then-push §5, push scope §5, L0 side channel §5; five child-lane items present: report path/filename §4, commit-before-report §4 ("report lands last … cites the pushed lane hash"), `SHONEN` heading §4, commit-hash citation rule §4, lane write scope §3 | pass |
| L2 route map vs MISSION | `MISSION.md:53-65`; prompt §6 run-11 map | MISSION states the ≥8-one-batched-call floor and *advisory* role-class buckets with no alias pins; the prompt quotes the run-11 operator alias map (every role `@m_flash`, scout `@m_grok`, task `@m_zfl`) and defers to `task.agentModelOverrides`. No protocol conflict | pass (operator-owned routing) |
| report contract sections, in order | `grep -n '^## '` | Work performed · Landed changes · Before → after measurements · Sources & frontier · Trend verdicts · SHONEN, with Errata/Named limits/Tools installed after; required order holds | pass |
| wave shape and seat mix | `census/round-39/waves/w1-results.json` (`seats`/`results`, 71 each); `ls census/round-39/waves/w1` | 71 seats = executor 19, reviewer 10, scribe 10, critic 8, scout 8, mutation-tester 5, connector 4, simplifier 4, revenger 2, sentinel 1; attack 26 = 36.6 %; one v2 wave inside the 64–128 band; 70 seat reports + `swarm-registry.json` = 71 files; dead 0 | pass |
| wave evidence durable | `cd census/round-39/waves && sha256sum -c manifest.sha256` | 80 manifest entries, 80 `: OK`, 0 failures (`records=80 failed=0 uncovered=0` at `2f6e981`); spec, dispatch, ready marker, results and registry are committed here (`.ufo/waves/round-39/` stays lane runtime) | pass |
| driver digest (mutable log; this digest is the pointer) | `.ufo/watchdog.log` (copied into the closure entry notes) | `2026-10-28T14:34:25-03:00 launch souji round=39 pgid=686189 driver=hyaku-inline attempt=1`; `2026-10-28T15:41:19-03:00 complete souji round=39; hyaku-inline attempt=1` | pass |
| fleet-repo write scope | `git log --author=souji --since=2026-10-28T14:00 --name-only` | `.ufo/reports/round-39/souji.md` (`d21910c`), `.ufo/prompts/souji-round-39.md` (`36d25db`) — both in scope | pass |
| marker vs report | report body | three declared claims, 22 lane commits, receipts under `census/round-39/records/`, a checkable tip | real report → status `ok` |

## Per-claim re-check

### C1 calibration (7, the lowest non-retired axis) — **re-measured by this reviewer**

Command (this reviewer's own script, not `census/round-39/c1-counter.py`): for every row of
`census/round-39/c1-items.tsv`, `git show <rev>:<file>` and require one line that contains the anchor,
every `must` token and no `mustnot` token; whole-token boundary applied to alphanumeric token edges.

- at `0242085`: `SUMMARY items=16 open=0` (16/16 CLOSED).
- at base `ed30b7f`: `SUMMARY items=16 open=16` — the do-nothing control cannot reach the target.
- register `census/round-39/cells.tsv`: 6 rows; each row's `commit` (`a8e6d75…`) is a strict descendant
  of its `receipt_rev` (`5230a34…` ×5, `f8ba3f3…` ×1); each anchored line at the tip carries `expected`
  and not `stale` as a whole token; each receipt blob at its `commit` carries `expected`.
  `SUMMARY cells=6 mismatches=0` by this reviewer's re-derivation and by the tool itself:
  `python3 -B tools/souji-citation-reconcile.py --root <lane> --rev 0242085… --register <abs cells.tsv>`
  → `SUMMARY cells=6 mismatches=0`, rc 0.
- Reported values match: `items=16 open=0 register_cells=6 register_mismatches=0`. The reported
  `commit_distinct=6` is the counter's count of rows whose `commit` differs from `receipt_rev`; the
  register names **one** distinct commit hash (`a8e6d75…`) — see routed defect **D3**.

Verdict: **improved** (calibration). The 16 defects routed by the r38 spot-check each became a
falsifiable anchored predicate, and the control at base fails all 16.

### C2 operability (8) — **re-measured by this reviewer on the artifact bytes**

| leg | base bytes | tip bytes | report |
|---|---|---|---|
| `--rev` = a blob id (`9c670c2c31f6…`, `LOG.md`) over `cells.tsv` | `python3 -B <base tool> …` → rc 1, `SUMMARY cells=6 mismatches=12` | rc 2, `REFUSAL REV-UNRESOLVED: --rev 9c670c… does not resolve to a commit`, 0 findings | matches L1/L2 (report's control read "20 findings" on its own register; the direction and class are identical) |
| `--rev` = the tip commit | — | rc 0, `SUMMARY cells=6 mismatches=0` | matches |
| fixture `tests/fixtures/r39-citation-rev.py` | `SUMMARY cases=8 pass=4 fail=4` (rc 1; `register-rev-gone` misses `REV-UNRESOLVED`) | `SUMMARY cases=8 pass=8 fail=0` (rc 0) | matches L5 `new=(8,8,0,0) old=(8,4,4,1)` |
| drift docstring vs raised classes | `RECORD-MISSING "the record path cannot be read"` (no errno) | docstring: `RECORD-MISSING` = EACCES/ELOOP, `RECORD-MALFORMED` = ENOENT/non-regular; code: `except OSError` → `ENOENT` ⇒ `RECORD-MALFORMED`, else ⇒ `RECORD-MISSING`; `fstat` non-regular ⇒ `RECORD-MALFORMED` | matches L4 `new_maps=True old_maps=False` |
| five consumers at tip | — | `r38-drift-record 10/10`, `r36-worktree-drift 12/12 control=STUB-REJECTED`, `r38-drift-write-envelope 12/12`, `r37-citation-reconcile 16/16 control=FALSE-GREEN-REJECTED`, `r38-citation-commit 14/14 control=FALSE-GREEN-REJECTED`, all rc 0 | matches L6 exactly |

The unreachable `EISDIR` word is gone from the record-path line (`grep -c EISDIR` at tip = 2, both in the
`--json` write-envelope path where the class is `JSON-UNWRITABLE`, not `RECORD-MISSING`).

Verdict: **improved** (operability).

### C3 coverage (8) — **re-measured by this reviewer's own mutation run**

This reviewer applied the four mutant patches (`M11` trailing-space tolerance, `M12` CRLF splitting,
`M13` outside-root guard removed, `M14` indented comment) to the tip `tools/souji-worktree-drift.py` and
ran both fixtures per mutant from scratch:

| mutant | r39 fixture (`r39-drift-record-rules.py`) | r38 fixture (`r38-drift-record.py`) |
|---|---|---|
| M11 | rc 1, `cases=7 pass=6 fail=1` → killed | rc 0, `cases=10 pass=10` → survives |
| M12 | rc 1, `cases=7 pass=6 fail=1` → killed | rc 0, `10/10` → survives |
| M13 | rc 1, `cases=7 pass=6 fail=1` → killed | rc 0, `10/10` → survives |
| M14 | rc 1, `cases=7 pass=6 fail=1` → killed | rc 0, `10/10` → survives |
| pristine | rc 0, `cases=7 pass=7` | — |

Reported `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7` reproduces field for field.
The four earlier fixtures (`r36-worktree-drift`, `r37-citation-reconcile`, `r38-drift-record`,
`r38-citation-commit`) and `r38-drift-write-envelope` are byte-identical base→tip
(`git diff --stat ed30b7f 0242085 -- tests/fixtures/`).

Verdict: **improved** (coverage — four parser edge classes no earlier fixture asserted).

### No axis harmed

Owned scores unchanged (calibration 7, operability 8, coverage 8) and the r39 SCORECARD block says so
with its commands. `git diff ed30b7f 0242085 -- SCORECARD.md` is append-only (one finality-correction
block, two register blocks, one measurements block, one capabilities block, one planned block; no earlier
line edited). Frozen predicates were tightened only (amendment A1 moves `register-rev-gone` from the
substring `not at` to the class `REV-UNRESOLVED`; A3 fixes a punctuation-edged token boundary that made
item C1-04 unsatisfiable). Every consumer fixture stayed green (table above). No axis harmed.

## Discernment spot-check (LEARNING.md — non-author)

Sources re-opened by this reviewer on 2026-10-28, from the lesson's `## Gate` table and the
`corpus/SOURCES.md` rows it grounds:

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S247 gitrevisions `^{<type>}` | admit | `MANWIDTH=100 man 7 gitrevisions` (installed git 2.56.0), entry line 165, quote 166-168 | agree | The man page carries the quoted words verbatim; the quote stops before "anymore (in which case, barf)", which is exactly the truncation the lane self-corrected with S250 — the fact (type coercion refuses a non-commit) holds either way |
| S250 (supersedes S247) | admit (correction row) | same man page, lines 166-168; row is 11 columns (`awk -F'\|'` NF=13), quote 25 words | agree | The full sentence supports the could-not-evaluate class C2 relies on; the supersede reason names the defect in the filed row and keeps S247 as filed (CORPUS.md rule 2) |
| S248 `ast.get_docstring` | admit | https://docs.python.org/3/library/ast.html (Python 3.15.2 page): "Return the docstring of the given node (which must be a FunctionDef, AsyncFunctionDef, ClassDef, or Module node), or None if it has no docstring." | agree | Quote is located and verbatim; it grounds "a module without a docstring yields None, not an error", which is what the L4 analyser needs |
| S249 argparse `exit_on_error` | admit | https://docs.python.org/3/library/argparse.html § `exit_on_error`: "it will print a message to sys.stderr and exit with a status code of 2" | agree | Verbatim in the section the row anchors; the inference (exit 2 alone cannot mean could-not-evaluate) is sound |
| Python docs `ast.get_source_segment` | reject | same ast page: "Get source code segment of the source that generated node" | agree | It returns the node's source span, i.e. source slicing, which the r38 M5 finding forbids for a docstring check; the stated flip (read through `get_docstring`) is the right one |

Census run by this reviewer (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji`): `rc=0`, `rows=174`, `W04=48`; base `ed30b7f` rows=170, W04=47. The
committed `census/round-39/records/census-after.txt` reads `rows=173 W04=47` — see routed defect **D1**.

## Trend verdicts

- **expansion: unchanged** — agree. No `corpus/knowledge/` file was added or edited
  (`git diff --stat ed30b7f 0242085 -- corpus/knowledge/` empty), no `ground:` line moved, and the four
  new registry rows (S247–S250, all tier A `mined`) ground a tool repair and two disclosures rather than
  new coverage-map ground. Rows 170 → 174 is curation, not knowledge.
- **quality: improved** — agree. Two documented tool contracts were repaired against a base arm that
  reproduces each defect (blob `--rev` → findings vs refusal; docstring class map wrong vs agreeing),
  the unreachable `EISDIR` claim was dropped instead of argued, and the new fixture discriminates
  4/8 on the base bytes and 8/8 on the tip (reproduced above).
- **discernment: improved** — agree. Sixteen outside-routed defects became sixteen predicates with a
  failing control, the wave's own residual defect (`EISDIR`) was integrated, a truncated quote was
  superseded by S250 rather than defended, and this spot-check agrees on 4/4 sampled gate decisions.

## Routed defects the lane must fix next round (status-neutral)

1. **D1 — the "after" source census is stale by one row.** `census/round-39/records/census-after.txt`
   reads `rows=173 W04=47` (measured before S250 landed at `e9958ee`); the filed registry has 174 rows and
   **W04=48** (S250 is a second `git-scm.com/docs/gitrevisions` row). The report's Sources & frontier
   section and `LOG.md` both restate "170 → 174 rows, W04 47 → 47" citing that receipt, so the receipt
   cannot reproduce the filed number. Round-end exit 0 still holds (re-run above: rc 0). Fix: re-run the
   census after the final registry append and file the receipt, or name the revision it was measured at.
2. **D2 — the final-tip re-measure names a revision it did not measure.** The report says all three
   claims "were re-read at the tip `0242085` (`census/round-39/records/final-tip-measure.txt`)"; that
   receipt's own header reads "re-measure at `544104503a3ad70687ba399fcafd12bd30648169`". Only
   `corpus/lessons/round-39.md` and the receipt itself changed after `5441045`
   (`git diff --stat 5441045 0242085`), so the values stand, but a verdict must name the revision it was
   measured against. Fix: state `5441045` in the report, or re-run at the tip.
3. **D3 — `commit_distinct` is a row count, not a distinct-commit count.** The C1 `SUMMARY` field counts
   register rows whose `commit` ≠ `receipt_rev` (6); the register names one distinct commit hash. The
   lesson's named limits disclose the `>=2` semantics, but the report's after-value reads as six distinct
   commits. Fix: rename the field (`commit_rows=6` / `commit_hashes=1`) or print both.

Accepted, not a defect: the prompt asks for the wave spec and registry to be committed as wave
evidence under `.ufo/waves/round-39/`. The lane left those as lane runtime and captured them into
`census/round-39/waves/` with an 80-entry `manifest.sha256` that verifies clean (80/80 `: OK`), and the
report's wave paragraph names that capture path. Durability is satisfied; no action owed.

## Note for the operator (promotion is operator-owned)

`SHONEN.md` still carries four `[~]` self-assessments. Boxes 1–4 all look checkable by a non-author from
committed bytes (SKILL.md decision tables and the gate registry; the `LOG.md` round entry with receipts;
`census/round-39/preregistration.txt` + counter `--help`; `PROVINCE.md` round-39 boundary note). This
reviewer writes no `[x]`; the promotion decision remains the operator's.
