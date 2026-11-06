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
| M1 | evidence durability (mined from r69, routed D1 and M14): r69 cited seat evidence that lived only in the gitignored round-69 seat directory `w1/` (`.gitignore:1` ignores the whole wave tree), and its frozen preregistration cites probe paths that never existed (`probe/full-battery-out.txt`, `probe/c2-ambient`, and also `probe/fsm`, which r69 M14 did not list) | `corpus/lessons/round-69-verifier-spotcheck.md` D1; `census/round-69/preregistration.txt` lines 38, 40, 41, 92, 125 | none at r69 (no pointer-existence check ran on the lesson or the prereg) | (a) the r69 seat evidence is mirrored byte-identically into `census/round-69/records/wave-w1/` (commit `0d8ce29a`); (b) `tools/souji-pointer-check.py` resolves every cited lane path at a revision. Shown able to fail: at `e063a2fc` over `corpus/lessons/round-69.md` and `census/round-69/preregistration.txt` it prints 5 MISSING lines and `EXIT=1` (`census/round-70/records/pointer-check-r69.txt`); over this round's prereg, knowledge entry and lesson it prints `missing=0`, `EXIT=0` (`census/round-70/records/pointer-check-r70.txt`) |
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
