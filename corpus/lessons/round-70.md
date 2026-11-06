# Round 70 — pathspec-variable scrub in the receipt writer (C1 operability), counter self-check calibration (C2 calibration)

Attempt 1. Lane base `e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333` (r69 admitted). Freeze
`0243af04bbcd422302b4efc3473612073c9aa962` (`census/round-70/preregistration.txt`, controls and
probes committed in the same commit, all executed before it). Candidate writer
`93a051b2c936ff6eafca8e8b31d918e3d20fd3da`. After-arms `e84f691b9b022425449e2aecc2e7ae308aee4ffe`.
Frozen claims, counters and predicates are in the preregistration and are not restated here.

## Measured

- C1: `census/round-70/records/c1-after.txt` — `SUMMARY matrix=59 base_forgeries=4 base_honest=13
  new_forgeries=0 new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, `EXIT=0`
  (before, `controls/c1-do-nothing.txt`: `new_forgeries=4 new_honest=13 class_mismatches=5`,
  `EXIT=1`). Forgery controls stay red: F1 refuse-on-presence `new_honest=11`, F2 literal-only
  scrub `new_honest=13`, both `EXIT=1`.
- C2: `census/round-70/records/c2-after.txt` — `SUMMARY label=c2-after-r70 positive_selftest=PASS
  positive_battery=PASS mutants=4 killed=4 survived=0 tamper=detected score=0`, `EXIT=0` (before,
  `controls/c2-before-r69.txt`: the frozen r69 counter, 4 survived, tamper undetected, `score=5`,
  `EXIT=1`). Blanket-killing counters are refused as invalid: CF1 and CF2 `EXIT=2`.
- Selftests: writer `records/writer-selftest.txt` `SELFTEST cases=38 pass=38 fail=0` (receipt
  written by the writer at `93a051b2`); counter `records/counter-selftest.txt` `SELFTEST cases=29
  pass=29 fail=0` (rev `0243af04`). This closes r69 routed D2 (no committed selftest receipt).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | evidence durability (mined from r69, routed D1 and M14): r69 cited seat evidence that lived only in the gitignored round-69 seat directory `w1/` (`.gitignore:1` ignores the whole wave tree), and its frozen preregistration cites probe paths that never existed (`probe/full-battery-out.txt`, `probe/c2-ambient`, and also `probe/fsm`, which r69 M14 did not list) | `corpus/lessons/round-69-verifier-spotcheck.md` D1; `census/round-69/preregistration.txt` lines 38, 40, 41, 92, 125 | none at r69 (no pointer-existence check ran on the lesson or the prereg) | (a) the r69 seat evidence is mirrored byte-identically into `census/round-69/records/wave-w1/` (commit `0d8ce29a`), and this round's into `census/round-70/records/wave-w1/`; (b) `tools/souji-pointer-check.py` resolves every cited lane path at a revision. Shown able to fail: with its final bytes, at `e063a2fc` over `corpus/lessons/round-69.md` and `census/round-69/preregistration.txt` it prints 8 MISSING lines and `EXIT=1` (`census/round-70/records/pointer-check-r69.txt`: the 5 prereg probe pointers, plus the lesson's own mentions of two of them and of M7's discarded receipt name); over this round's prereg, knowledge entry and lesson at the landing tip it prints `missing=0`, `EXIT=0` (`census/round-70/records/pointer-check-r70.txt`) |
| M2 | destructive cleanup: an L1 sweep `find census -name __pycache__ -prune -exec rm -rf {} +` deleted a TRACKED file, `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` | `jj-lane.sh state` printed `tracked=1` after the sweep; `git status --porcelain` showed ` D census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` | the lane helper's `state` line (`tracked=` count), read before the next commit — it caught the deletion before anything landed | file restored from the branch (`git show master:<path> > <path>`), `tracked=0`; rule: a cache sweep in the lane deletes only paths `git ls-files` does not list. The sweep itself is the souji domain error class "delete by name pattern without a tracked-state receipt" |
| M3 | concurrency in evidence capture: the counter-selftest receipt was first run in parallel with three other jobs that wrote receipts into the lane; the writer refused `RECEIPT-STATE-CHANGED-DURING-RUN` (content of `records/c1-after.txt` and `records/writer-selftest.txt` changed during the wrapped command) | the refused run's stderr, quoted in this lesson; the serial re-run produced `records/counter-selftest.txt` | the writer's own in-run state check (round-63/64 protection) — it failed closed, no receipt written | state-bound receipts run serially, after every other lane write of the same round step |

## Gate

**Sources opened this round.** S304 git(1), https://git-scm.com/docs/git, accessed 2026-11-06,
HTTP 200, 244227 bytes, sha256 534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1
(capture `census/round-70/srcs/git-manual.html`; byte-identical to S303's r69 capture: the page has
not changed); section OPTIONS, dt `--literal-pathspecs`; located quote (20 words): "Treat pathspecs
literally (i.e. no globbing, no pathspec magic). This is equivalent to setting the
GIT_LITERAL_PATHSPECS environment variable to 1". gitglossary(7),
https://git-scm.com/docs/gitglossary, accessed 2026-11-06, HTTP 200, 109997 bytes, sha256
216bc0df7f50dc17d331ea2a9873daf65a08a2afddd797f73a300cc2e15f0129 (identical to S296's capture).

**Candidates considered.** (1) S304 — ADMIT, tier A, scope: the global pathspec switches and their
environment equivalents; it is the only located sentence that says the variable removes pathspec
MAGIC (which is what empties `:(top)`). (2) S305 — REJECT (row kept): the ENVIRONMENT VARIABLES
entry for GIT_LITERAL_PATHSPECS says "treat all pathspecs literally, rather than as glob patterns"
and never names magic, so it cannot ground the `:(top)` effect; flip: a release adds magic to that
entry. (3) gitglossary(7) `literal` magic word ("Wildcards in the pattern such as * or ? are
treated as literal characters") — REJECT, not appended: it is the per-pattern magic word, says
nothing about the global variable or about other magic being disabled; S296 (same page, `top`)
already grounds the reader side. Registry `corpus/SOURCES.md` 226 → 228 rows; `sources-census.sh
validate` exit 0 at round start (`census/round-70/records/census-before.txt`) and at round end
(`records/census-after.txt`).

**Status changes.** No existing row's `status`, `recheck` or `used-by` cell changed.

**Assimilation: none.** `considerthese/` is absent in this lane (`ls` → no such directory); the
`merge/souji/` package holds no pathspec material (`grep -ril pathspec
/home/vgpnk/Projects/shokuknow/merge/souji/` → 0 files), so no theme fits this round's claims.

**Mistakes found by the wave (appended; the frozen files are not edited).**

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M4 | non-reproducible anchors: the S304/S305 anchor cells first carried offsets (12133, 47046) from an ad-hoc normalization of the capture that no committed recipe reproduces; 12133 is the variable token inside the quote, not the quote start | `census/round-70/records/wave-w1/seats/S70ScoutSources.md` §2 (1152 recipe variants, none reproduces); `S70CriticDiscern.md` (byte 11413 and 46523 in `census/round-66/sources/git-environment.txt`, S298's basis) | the wave's source seats (not the gate: the registry check does not re-slice anchors) | the two cells now cite byte offsets 11413 (S304 quote), 46451 and 46523 (S305 entry and quote) in S298's committed text basis, re-sliced by the L1 (`python3` `bytes.find` over `census/round-66/sources/git-environment.txt`), with "corrected 2026-11-06" in the cell; the S305 reason wording was tightened (it does say "literally") |
| M5 | dead pointer inside the round that built the pointer check: the lesson cited `records/census-after.txt` and `records/pointer-check-r70.txt` before either was committed, and the first checker bytes skipped `records/` tokens outside `census/` files, so the check could not see it | `census/round-70/records/wave-w1/seats/S70Scribe.md` (HIGH), `S70CriticDiscern.md` (HIGH) | the wave (not the checker: its first bytes were blind to lesson-local tokens) | both receipts committed (`152b46c3`, and the r70 check at the landing tip); the checker resolves `probe(s)/`, `records/`, `controls/`, `battery/` tokens in `corpus/lessons/round-N*.md` against `census/round-N/` and counts unresolvable ones as skipped, never silently |
| M6 | seat containment: wave seat S70MutWriter ran a fixture with a `mktemp` template lacking `XXXXXX`; the empty `D` made `git -C ""` act on the fleet root and a throwaway-identity commit landed there (`cff0b4cb`, author `p <p@x>`), already pushed under later commits | `census/round-70/records/wave-w1/seats/S70MutWriter.md` (HIGH, incident); `git -C /home/vgpnk/Projects/shokunin show --stat cff0b4cb` (3 files, +235/−79, no deletion) | none — the wave context's fixture rule ("verify `rev-parse --show-toplevel` equals `$D` before the first commit") was not executable as written when `$D` is empty, and no guard refuses an empty `-C` argument | reported to the orchestrator and filed as an L0 question in the fleet repo (fleet commit `78c78a82`, line beginning "souji, round-70"); no recovery run by the lane. Rule for r71 wave contexts: create fixtures with `D=$(mktemp -d -p "$S" fx.XXXXXX) && [ -n "$D" ] && [ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ]` and exit on failure, before any commit |
| M7 | overreach in self-assessment: the SCORECARD r70 bullet first said the selftest kills "the four r69-found instrument blind spots"; S69MutTester recorded six survivors and two (e2/e4, a selftest weakening its own assertion) still survive; the README frontier said "no earlier entry covers pathspec semantics" while `lessons/round-69.md` already named the route | `S70CriticClaims.md` (MEDIUM, `st-e2.txt`); `S70Connector.md` §3 | the wave critics | SCORECARD bullet and README sentence rewritten before landing (this round's own text; old wording named in this row) |

**R69-D4 erratum (routed).** The r69 report and the SCORECARD r69 table call the C2 before-arm "6 flips": that is 6 diff-marker lines (`<`/`>`), i.e. 3 changed lines (`REGRESS`, `SUMMARY`, `EXIT=`). The r69 rows are not edited; this line supersedes the unit.

**Attacks on the round's claims (wave w1, 12 seats, all lane-dispatched: recorded as attacks, not as non-author discernment).**
- C1 reproduced byte for byte by S70ExecC1 (59 CASE lines, do-nothing, F1, F2 identical; chronology freeze 15:49:38 → candidate 15:50:28 → after-arms 15:54:09, committer dates), S70CriticClaims, S70Reviewer, S70Sentinel, S70MutWriter and S70ExecAmbient (also under hostile ambient tuples: 0 differing lines; template hook never copied). Qualifications: (i) the NOGLOB scrub is unmeasured — S70MutWriter W3 (NOGLOB dropped) and W7 (scrub skipped for `status`) survive the matrix and the writer selftest; (ii) the predicate is mechanism-agnostic — a pathspec-free rewrite with no scrub also reaches it (S70CriticClaims); (iii) writer selftest case 38 iterates the same `PATHSPEC_ENV` constant it tests, so dropping a variable drops its test (S70MutWriter MEDIUM); case 38 fails on the base writer (37/38), so it can fail.
- C2 reproduced byte for byte by S70ExecC2, S70CriticClaims, S70Reviewer, S70Sentinel, S70MutCounter. Qualifications: (i) the four mutants and the tests that kill them were written in the same round, and the CF1/CF2 controls already foreshadowed the after-arm (prereg disclosure ii) — S70CriticClaims rates C2 QUALIFIED and questions the calibration label under `AXES.md` ("SHONEN.md/SCORECARD entries match observed repo state"); (ii) S70MutCounter: 5 of 10 further counter mutants are killed by the selftest, 5 survive — X6 (`tally["error"]` gate), X7 (clean_env keeps the pathspec variables), X8 (case_env drops `pathspec_env`: `base_forgeries` 4 → 0 with `EXIT=0`, caught only by the frozen byte comparison of SUMMARY), X9, X10 (SHA256SUMS duplicate and malformed lines).
- Sources: S70ScoutSources and S70CriticDiscern re-fetched both pages (byte-identical), agree with S304 admit, S305 reject and the glossary reject; anchors corrected (M4); S304's teaches clause on `:(top)` rests on S296 and the probe, now cited by the knowledge entry (S296 `used-by`: `corpus/lessons/round-64.md` → `corpus/lessons/round-64.md, corpus/knowledge/pathspec-env-scrub.md`).
- Battery: the r70 counter over all 26 r69 members (`census/round-70/probes/battery-r69-members-r70-counter.txt`) classifies every member `forgery` (each base-era member forges the new LITERAL rows), 8 expectations miss, `all_match=false`, `EXIT=1` — inside the frozen named limit "the battery is not regenerated this round"; P-BATTERY samples only D01.

**Routed to round 71 (not repaired here; the writer and the instruments are frozen).** (a) HIGH (S70Sentinel F1, pre-existing): a `filter` attribute with a repository-local `filter.<x>.clean` (via `GIT_ATTR_SOURCE` or a committed `.gitattributes`) makes `git status` hide a modified tracked file and the writer writes the receipt; the writer neither scrubs nor refuses `GIT_ATTR_SOURCE`. (b) MEDIUM (F2, pre-existing): repository-local `core.fileMode=false` hides an in-run mode flip. (c) MEDIUM (F3/F4/F5): battery member names and harness labels are not validated (`../` escapes `--work` and runs out-of-dir bytes). (d) MEDIUM (S70MutCounter X7/X8): the counter's rc does not bind `base_forgeries`/`base_honest`, and no selftest case asserts the ambient pathspec scrub. (e) regenerate the battery from the r70 writer so its manifest matches the 59-row matrix. (f) a NOGLOB-observable row or a named limit for it. (g) writer case 38 must enumerate the variables independently of `PATHSPEC_ENV`. (h) r69 D5 (ambient receipt records no tuple) and the r69 list items (d) D06 isolating row, (g) writer `verify` subcommand remain open. (i) cross-lane, read-only report: S70Connector found `kaidoku-shokunin/tools/round-42/prefile-gate.py:311-327` and `kumitate-shokunin/scripts/round-gate.mjs:491,562` read the index through pathspecs with the caller's pathspec variables unscrubbed — documented in the report, not edited (domain trees are read-only).

**Discernment.** All seats are this lane's dispatched seats; no non-author discernment verdict is recorded by the lane. The discernment trend is left to the closure's spot-check.

**M3 refusal, verbatim (the first counter-selftest receipt attempt):** `refused: RECEIPT-STATE-CHANGED-DURING-RUN: worktree status (git status --porcelain) and content census/round-70/records/c1-after.txt and content census/round-70/records/writer-selftest.txt changed during the wrapped command; no receipt written`.
