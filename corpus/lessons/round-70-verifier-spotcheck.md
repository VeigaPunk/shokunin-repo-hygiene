# Round 70 — verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Dispatched 2026-11-06T15:39:19-03:00, completed 2026-11-06T16:28:34-03:00 (`launch souji round=70 pgid=1082372 driver=hyaku-inline attempt=1` / `complete souji round=70; hyaku-inline attempt=1`, `.ufo/watchdog.log`, digest copied because the log is mutable). Lane base `e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333`, lane tip at closure `3b7cce814afae197c7d7dc079f2bdfac3aa389a0`. All checks below were run by the closure on 2026-11-06 (~19:30Z) over committed bytes; no sibling gate was executed.

## Conformance

| check | command | result |
|---|---|---|
| report landed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H %ci' -- .ufo/reports/round-70/souji.md` | `souji-shokunin <souji@shokunin.local>` `3cc5d7c40aa525067d76d78c5293bc106ee66196` (committer 2026-11-06 16:28:06 -0300, after lane tip `3b7cce81` committed 16:26:54) |
| `SHONEN` heading, one line per box | read of the report; `grep -n '^- \[' SHONEN.md` (4 boxes) | `## SHONEN` with 4 `[~]` lines, one per box, each with a pointer; no `[x]` |
| cited lane commits exist and are ancestors of the branch ref | `git rev-parse --verify <c>^{commit}` + `git merge-base --is-ancestor <c> master` for `e063a2fc`, `0243af04`, `93a051b2`, `e84f691b`, `0d8ce29a`, `feb283ee`, `9167e02d`, `20c117ce`, `4c392c76`, `faac34e6`, `63ceb475`, `152b46c3`, `170ecb65`, `3b7cce81` | all 14 resolve and are ancestors of `master`; all 13 round commits authored `souji-shokunin <souji@shokunin.local>` |
| no uncommitted round work | `git -C <lane> status --porcelain` | empty |
| pushed | `scripts/hyaku/jj-lane.sh state <lane>` | `branch=master local=3b7cce81… remote=3b7cce81… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git ls-remote origin refs/heads/master` → `3b7cce81…` |
| prompt carries the template contract | `diff <(sed -n 1,140p templates/round-prompt.md) <(sed -n 1,140p .ufo/prompts/souji-round-70.md)` | placeholder substitutions only (`{{LANE}}`, `{{ROUND}}`, `{{FLEET_ROOT}}`, `{{AXES}}`); §1–§5 (axes binding, 1–3 claims, frontier step, L2 floor, report contract, commit/push scope/L0) present; hyaku addendum §6 follows; prompt committed by the lane identity (`6b7836cf`) |
| writer bytes | `git show e063a2fc:tools/souji-receipt-write.py \| sha256sum`; same at `93a051b2`; `git diff --stat 93a051b2 3b7cce81 -- tools/souji-receipt-write.py` | base `b811ee2a…a715a725` (= prereg), candidate `118597e0…52e71f` (= c1-after slot line); no writer change after the candidate |
| frozen instruments unchanged after freeze | `git diff --stat 0243af04 3b7cce81 -- census/round-70/{c1-counter.py,c1-matrix.tsv,c2-harness.py,make-controls.py,preregistration.txt,controls}`; `sha256sum` | empty diff; counter `3f684c3e…3ada`, harness `38c30eff…afb`, matrix `1607e4f8…7536` — each equal to the sha recorded in the after receipts |

## Claim re-checks

**C1 — operability: writer scrubs the four pathspec variables (sourced S304).** VERIFIED (re-measured + evidence-verified).

- Writer diff: `git show 3b7cce81:tools/souji-receipt-write.py | grep -n PATHSPEC` → `PATHSPEC_ENV = ("GIT_LITERAL_PATHSPECS", "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS", "GIT_ICASE_PATHSPECS")` at :105 and `k not in PATHSPEC_ENV` in `git()` at :111; the same grep at `e063a2fc` → 0 hits.
- Mechanism, independently re-derived by the closure (fresh temp repo, git 2.56.0, one skip-worktree entry `f`): `git ls-files -v ':(top)'` → `[S f]` with no variable, GLOB, NOGLOB, ICASE; `[]` under `GIT_LITERAL_PATHSPECS=1`; `GIT_GLOB_PATHSPECS=1 git ls-tree HEAD -- f` → `fatal: f: pathspec magic not supported by this command: 'glob'`. Matches `census/round-70/probes/lp-ls-files-probe.txt` line for line.
- `grep -E '^(SUMMARY|EXIT=)' census/round-70/records/c1-after.txt` → `SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=0 new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, `EXIT=0` — byte-equal to the frozen predicate (prereg) and the report. Receipt header `rev=93a051b2…`, `instrument_sha256=3f684c3e…` (= frozen counter).
- Before / controls: `controls/c1-do-nothing.txt` `new_forgeries=4 new_honest=13 class_mismatches=5`, `EXIT=1`; F1 `new_honest=11 class_mismatches=8` EXIT=1; F2 `new_honest=13` EXIT=1 — all as reported.
- Per-row: `grep '^CASE (LD|LN4|LG1|LA9)'` → `base=accept new=refuse` with `RECEIPT-INDEX-FLAG-CONCEALED` / `RECEIPT-GITLINK-CONCEALED` / `RECEIPT-INDEX-CONCEALED-ABSENT`; GA, ICA `base=refuse new=accept`; NGA/NGD unchanged base→new (confirms the "NOGLOB unmeasured" qualification).
- `awk -F'\t' 'NR>1' census/round-70/c1-matrix.tsv | wc -l` → 59.
- Gate evidence (not executed): writer selftest receipt `records/writer-selftest.txt` `SELFTEST cases=38 pass=38 fail=0`, `EXIT=0`; counter selftest `records/counter-selftest.txt` `cases=29 pass=29 fail=0`; frozen run = c1-after at `93a051b2`; SKILL.md registry row "r70 pathspec-env matrix (C1)" present.
- Qualifications accepted as disclosed, not counted as passes: NOGLOB scrub unmeasured (W3/W7 survive); the predicate is mechanism-agnostic; case 38 iterates the constant it tests.

**C2 — calibration: counter's own selftest kills four frozen instrument mutants; battery arm detects a swapped member (lowest owned axis, 7).** VERIFIED (evidence-verified; receipt bytes re-read).

- `grep -E '^(SUMMARY|EXIT=)' census/round-70/records/c2-after.txt` → `SUMMARY label=c2-after-r70 positive_selftest=PASS positive_battery=PASS mutants=4 killed=4 survived=0 tamper=detected score=0`, `EXIT=0` — byte-equal to the frozen predicate. `counter_sha256=3f684c3e…` (frozen bytes), `MUTANT CM1..CM4 fate=killed` with selftest fail counts 3/1/1/1; `TAMPER T1 … C1-COUNTER-FATAL: battery members unverified … fate=detected`.
- Before: `controls/c2-before-r69.txt` → `killed=0 survived=4 tamper=undetected score=5`, `EXIT=1`. Invalidity controls CF1, CF2 → `EXIT=2` (a blanket-failing counter is refused, not scored).
- Gate evidence (not executed): harness frozen at `0243af04`, receipt label and counter sha bind the revision; SKILL.md registry row "r70 counter self-check harness (C2)" present.
- Ruling on the calibration label (S70CriticClaims' question): the move is the instrument's ability to report its own known defects (the r69-wave-found precedence/expectation/echo blind spots), which is self-assessment quality; the before-arm is the shipped r69 counter, not a strawman. Accepted as calibration, qualified: the mutants and the killing tests were authored in the same round (prereg disclosure ii), and 5 of 10 further counter mutants survive (S70MutCounter X6–X10). These narrow the claim's reach, they do not falsify it.

**Harm check.** `git diff e063a2fc 3b7cce81 -- SCORECARD.md` → additions only (two capability rows, r70 done bullet, r70 measurement table); no axis score changed (calibration 7, coverage 8, operability 8). No owned surface regressed: the 47 carried r69 rows keep verdict and class (`class_mismatches=0`), regress fixture PASS on both slots.

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 re-measured; mechanism reproduced by the closure |
| calibration | improved | C2 receipt verified against frozen bytes; qualified (same-round mutants) |
| coverage | unchanged | no claim; 12 matrix rows added are instrument rows for C1, not a coverage move |

## Discernment spot-check (sources re-opened by the closure)

| item | lane decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S304 git(1) OPTIONS `--literal-pathspecs` | admit, tier A, mined | live https://git-scm.com/docs/git (HTTP 200, 244227 bytes, sha256 prefix `534c674f9929280d` = capture); `census/round-66/sources/git-environment.txt` byte 11413 | agree | quote found verbatim in the live page (tag-stripped offset 12034) and at byte 11413 of the committed basis; 20 words (≤25); it is the only located sentence that says the variable removes pathspec *magic*, which is exactly the `:(top)` effect the closure reproduced in a fresh repo |
| S305 git(1) ENVIRONMENT `GIT_LITERAL_PATHSPECS` | reject (row kept, flip on-release) | same live page; basis bytes 46451/46523 | agree | live entry reads "will cause Git to treat all pathspecs literally, rather than as glob patterns. For example … `*.c`" and never mentions magic, so it cannot ground the `:(top)` failure; the flip condition is concrete |
| gitglossary(7) `literal` magic word | reject (not appended) | live https://git-scm.com/docs/gitglossary (HTTP 200, 109997 bytes, sha256 prefix `216bc0df7f50dc17` = capture) | agree | "Wildcards in the pattern such as * or ? are treated as literal characters" found (offset 17932); it is per-pattern magic and says nothing about the global variable disabling other magic |

Newly written row re-checked: S304 quote "Treat pathspecs literally (i.e. no globbing, no pathspec magic). This is equivalent to setting the GIT_LITERAL_PATHSPECS environment variable to 1" — 20 words, located at the cited offset (line breaks in the basis text only). `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → EXIT=0, `ok` + 77 W04 duplicate-URL warnings (no error class). Rows 226 → 228 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` at `e063a2fc` and `3b7cce81`), malformed rows 0.

## Trend verdicts

- **expansion: improved.** `corpus/knowledge/pathspec-env-scrub.md` (new) cites S304 (`mined`, `used-by` = this entry) on ground no earlier knowledge entry held (four-variable table incl. GLOB/ICASE over-refusal polarity); README frontier section added; two capability rows.
- **quality: improved.** r69 dead prereg/lesson pointers are now caught by a committed check (`records/pointer-check-r69.txt`: `missing=8`, EXIT=1) and marked in lesson M1; r69 "6 flips" unit corrected by erratum (D4); r69 seat evidence made resolvable (`census/round-69/records/wave-w1/`, D1). No admitted entry failed its re-check.
- **discernment: improved.** Non-author spot-check agrees with the gate on the admit (S304) and both rejects (S305, glossary `literal`).

## Routed defects (lane fixes next round)

- **D1 (calibration surface, LOW).** `SCORECARD.md:181` capability row says `pointer-check-r69.txt (5 missing, EXIT=1)`; the committed receipt at `3b7cce81` reads `SUMMARY files=2 checked=59 missing=8 … EXIT=1` (the 5 is the superseded `9167e02d`/`63ceb475` receipt). The report says 8. Append a correction.
- **D2 (LOW).** `corpus/lessons/round-70.md:55` "No existing row's `status`, `recheck` or `used-by` cell changed" contradicts `:75` and the report (S296 `used-by` changed). Append an erratum naming line 55.
- **D3 (Gate standard).** `tools/souji-pointer-check.py` exits 1 on missing pointers (a gate by behaviour) but has no SKILL.md registry row (`grep -n souji-pointer-check SKILL.md` → 0 hits) and no self-test mode. Register it (gate or probe) with a self-test over fixtures.
- **D4 (carried from the lesson, routed r71).** S70Sentinel F1 (`filter` attribute / `GIT_ATTR_SOURCE` hides a modified file, HIGH), F2 (`core.fileMode=false`), F3–F5 (battery member names escape `--work`); S70MutCounter X7/X8 (counter rc does not bind `base_forgeries`/`base_honest`); NOGLOB scrub has no measuring row.
- **D5 (fleet incident, operator-owned).** Seat S70MutWriter committed `cff0b4cbe684ce702bca2a126b579d602f0cd6ae` ("seed", `p <p@x>`) into the fleet root; contained in `origin/main` and `origin/master`. L0 filed (`78c78a82`). Not lane content; ruling stays with the operator. The lane should add an empty-`-C`/toplevel guard to its seat fixture rule.
