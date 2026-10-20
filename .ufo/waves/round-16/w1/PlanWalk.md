# PlanWalk — round-16 integration checklist (planner data-walk)

Role: revenger item carrying L1's bounded planning data-walk (the validator rejects a
`planner` swarm role; L1 holds the canonical §3 planner seat). Scope: ordered list of every
artifact r16 must land, its dependency order, and the evidence each needs. Read-only walk;
no execution of the census, gate, fixtures or checkers.

## 1. Verified starting state (2026-10-20)

| item | observation | command |
|---|---|---|
| lane HEAD | `cbf688a` round-16 C1 commit; parent `58ace9f` (r15 non-author closure) | `git log --oneline -8` |
| C1 landed bytes | `tools/souji-census.sh` 989-line rewrite, `tests/fixtures/r15-census-config.py` +151, `census/round-16/run-matrix.py` +129 | `git show --stat --format='%H %an %s' cbf688a` |
| C1 measured evidence | `census/round-16/c1-matrix.json` exists but is **untracked** | `git status --porcelain` |
| C2 tooling | `tools/souji-landing-gate.py`, `tests/fixtures/r16-landing-gate.py` **absent** (executors in flight) | `ls -la tools/souji-landing-gate.py …` |
| lesson/claims/report | `corpus/lessons/round-16.md`, `census/round-16/claims.json`, fleet report **absent** | same |
| source registry | 42 rows, A/B/C 38/3/1, mined/queued/rejected 25/15/2, digest `5185720f…` at `b410186` | `grep -cE '^\|\s*S[0-9]{3,}\s*\|' corpus/SOURCES.md` |
| wave 1 | 65 items dispatched, one unchanged payload, registry present; role mix scout 17, reviewer 14, connector 9, critic 6, scribe 6, revenger 5, executor 3, sentinel 2, mutation-tester 2, simplifier 1 | `.ufo/waves/round-16/w1-spec.json`, `w1/swarm-registry.json` |
| untracked set | `.ufo/waves/round-16/`, `census/round-16/c1-matrix.json`, `census/operator-sweep-20261019/` (operator; never touch) | `git status --porcelain` |

L2 floor is met inside wave 1 (planner = L1 + this walk; connector, executor ×3, scribe, scout,
reviewer, critic all present). **Executor count is exactly at the 3-seat floor** — one dead
executor breaks §3; report it and do not respawn under a new identity.

### 1.1 Measured C1 arms (the only current behavioral evidence; from `c1-matrix.json`)

All arms run the same current fixtures; `fixtures_sha256` = r15-config `9151cde8…`, r14-namespace
`e6a984b1…`, and the worktree equals `cbf688a` for census + both fixtures (`git diff --quiet`
rc 0; `sha256sum` agrees).

| arm | rev / digest | bash -n | shellcheck -S warning | legacy --selftest | r15-config (20) | r14-namespace (12) |
|---|---|---|---|---|---|---|
| changed | `cbf688a`, `fed43c71…` | rc 0 | rc 0, 0 findings | 38 checks / 0 failed | **20 PASS, 0 fail** | **12 PASS, 0 fail** |
| pre-harm | `a31642d`, `6a000c59…` | rc 0 | rc 0 | 36 / 0 | 8 fail: 02,03,08,11,14,17,18,19 | 10 fail: 01–06,09–12 |
| r14-harm | `cc21683`, `fcff8b05…` | rc 0 | rc 0 | 38 / 0 | 16 fail: 01,03,04,06–10,12–16,18–20 | 12 PASS |
| r15-baseline | `b410186`, `dab4122c…` | **rc 2** (line 1368) | **rc 1, 4 findings** | **rc 2** | 20 fail | 12 fail |

Three consequences L1 must not lose when writing evidence:

1. **pre-harm is not a green baseline.** It fails 8 r15-config cases and 10 r14-namespace cases
   — r16 safety properties (env pin, namespace reach, degrade token) postdate it. Use it as a
   *contraction* control, never as a "before" that passed.
2. **r14-harm's legacy selftest is 38/38 green.** The legacy `--selftest` does **not**
   discriminate the r14 value-blind harm; only the r15-config fixture does. Do not cite the
   selftest count as C1 proof.
3. r15-baseline's failure shape is exact: `bash -n` rc 2, `shellcheck` rc 1 with 4 findings,
   `--selftest` rc 2 — the r15 report's "unverified candidate" was an understatement, and this
   is the R1 correction's factual core.

### 1.2 Stale pins that the R4 work must close

`tests/fixtures/r15-preservation-frozen/expected.json` currently pins:
`tools/souji-census.sh` `b5187351…` (matches **no** committed revision), `tests/fixtures/r15-census-config.py`
`6314d45d…` (r15 bytes; committed bytes now `9151cde8…`), `tests/fixtures/r14-census-boundary.py`
`e6a984b1…` (matches), `record_sha256` `4749ad07…` (r15 record). Target values after re-pin:
census `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`, fixture
`9151cde8817d283376f089797ededd5896bc8812feb05f180ccc59760e1eb1af`, boundary
`e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`, plus the **new**
`record.json` digest. `tools/souji-preservation-evidence.py` currently has no `degrade` class
(`grep -n degrade` → no match), so the checker cannot yet accept case `R15CFG-03` as
`harm FAIL / changed PASS`; that is the in-flight PreservationRepin delta, not done work.

## 2. Ordered integration checklist

Dependency rule that governs the whole round: **pinned bytes freeze → re-pin → final matrix →
lesson carry → commit → gate green → report**. Any edit to `tools/souji-census.sh`,
`tests/fixtures/r15-census-config.py` or `tests/fixtures/r14-census-boundary.py` after the re-pin
invalidates it; any edit to the fixture after the final matrix invalidates the matrix; any new
`.md` under `.ufo/waves/round-16/` after the gate-green run invalidates LG-SEAT-UNCARRIED.

### P0 — baseline and declarations (before the first r16 integration commit)

| # | artifact | depends on | evidence it needs |
|---|---|---|---|
| P0.1 | `census/round-16/before-sources.json` (start census) | nothing | exact stdout+exit of `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` (exit 0; W04 S035/S036/S038 advisory) plus re-derived counts 42 / A38 B3 C1 / 25-15-2 and the SHA-256 of `corpus/SOURCES.md` at the measured rev |
| P0.2 | `census/round-16/claims.json` | nothing | C1 operability + C2 calibration, each with counting command, arms (`a31642d`, `cc21683`, `b410186`, changed), base rev, falsifier, and the X/12-line claim wording (Q23: no boundary inflation) |
| P0.3 | inherited-state paragraph (LOG + report) | P0.1 | names current untracked wave dir + `c1-matrix.json` + operator sweep; earlier-attempt leftovers only from L1's own driver record — seats never read `.ufo/watchdog.log` |

### P1 — commit the C1 evidence already measured

| # | artifact | depends on | evidence it needs |
|---|---|---|---|
| P1.1 | commit `census/round-16/c1-matrix.json` (or regenerate under a new name) | P0 | JSON contains `lane_head`, `changed`, `fixtures_sha256`, `fixtures_dirty` (must be empty), `git_version`, and all four arms; summary lines pasted in LOG |
| P1.2 | LOG entry (C1) | P1.1 | the four arm lines verbatim: `changed … r15=20/0fail r14=12/0fail`, `pre-harm …`, `r14-harm …`, `r15-baseline …`, plus `bash-n`/`sc` fields |

### P2 — integrate wave-1 source artifacts (executors)

| # | artifact | depends on | evidence it needs |
|---|---|---|---|
| P2.1 | `tools/souji-landing-gate.py` (C2 gate) | none | `--selftest` tally ≥12 cases, 0 fail; runs: `--rev b410186 --round 15` → exit 1 with LG-PARSE-REG on `tools/souji-census.sh` **and** LG-FROZEN-PIN on the r15 frozen census pin; `--rev cc21683 --round 15` advisory; `--rev cbf688a --round 16 --base cc21683` advisory. Store raw stdout/exit |
| P2.2 | `tests/fixtures/r16-landing-gate.py` | P2.1 | external self-invocation fixture run: historical replay red/green discrimination, pin-mismatch case, uncarried/carried marker pair, bad-rev → 2; report exit and case ids |
| P2.3 | `tools/souji-preservation-evidence.py` + `tests/fixtures/r15-preservation-evidence.py` (R4) | r16 case universe at `cbf688a` (`EXPECTED_IDS` 128–154, `HARM_CASES` 161–165, `CASE_CLASSES` 168–176) | `--selftest` tally; external fixture; `--frozen` run — all three, with exits |
| P2.4 | `tests/fixtures/r15-preservation-frozen/record.json` + `expected.json` re-pin | P2.3; **last** edit of the three pinned files | record built from real three-arm fixture runs (`pre-harm`/`r14-harm`/`changed`); new pins in §1.2; `--frozen` exit 0 tally |
| P2.5 | L1 code corrections to seat-authored tools | P2.1–P2.4 | every L1 edit re-runs that tool's own selftest/fixture; a fix without its post-fix run is not evidence |

### P3 — wave 2 (falsify), after wave 1 returns

| # | artifact | depends on | evidence it needs |
|---|---|---|---|
| P3.1 | `.ufo/waves/round-16/w2-spec.json` | wave-1 outputs | ≥64 distinct attack items each naming what it attacks (re-run counting commands, re-open new source rows, attack each claim, mutation-test each new gate); if fewer, one ordinary ≤8-seat reviewer/critic task instead — never pad |
| P3.2 | validator + dispatch | P3.1 | policy v2 validator exit 0 (band 64–100); one `task` call with the validator's `taskCall` unchanged; `w2-dispatch.json` + `w2/swarm-registry.json` committed |
| P3.3 | wave/seat accounting | P3.2 | seat count, role mix, dead seats with their errors, round total ≤200, planner mapping named (no `planner` role, no `model` parameter) |

### P4 — post-wave-2 source freeze, then final evidence

| # | artifact | depends on | evidence it needs |
|---|---|---|---|
| P4.1 | fixes to census/fixtures forced by falsifiers | P3 | each fix names the attacking seat and case; then the re-pin and matrix are redone from the fixed bytes |
| P4.2 | final re-pin (§1.2 values, adjusted to final bytes) | P4.1 | `--frozen` exit 0 (clean) with tally; `expected.json` `record_sha256` = regenerated `record.json` digest |
| P4.3 | `census/round-16/c1-matrix-final.json` | P4.1 | `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py --changed <final-rev> --output <new.json>` (refuses overwrite); changed 20/0, 12/0, 38/0, `bash -n` 0, shellcheck 0 findings; `fixtures_dirty` empty; red arm sets exactly as §1.1 |
| P4.4 | checker acceptance triple | P4.2 | `--selftest`, external fixture, `--frozen`; all exits and tallies recorded, none "UNRUN" |
| P4.5 | gate acceptance (advisory pass) | P4.2 | gate selftest; fixture; b410186 red; cbf688a green; recorded verbatim — these are advisory, L1's final run is P6.3 |

### P5 — prose and bookkeeping (scribes/connectors draft; L1 writes)

| # | artifact | depends on | evidence it needs |
|---|---|---|---|
| P5.1 | `corpus/lessons/round-16.md` `## Mistakes` | P3/P4 findings | R16-M1 non-parsing landing despite seat disclosure (captured-by `none` → C2 gate shown able to fail on `b410186`); R16-M2 frozen pin on uncommitted bytes; R16-M3 fixture oracle bugs in a never-run fixture; R16-M4 probe rule recorded but not enforced — each with file:line pointer |
| P5.2 | lesson `## Gate` | P5.1, P5.3, P5.4 | admit/reject C1/C2 with measured evidence or honest `unprovable`; every opened S-row's URL, access date 2026-10-20, served version and ≤25-word located quote; old→new for every status/recheck/used-by change; source-census before/after command block; process deviations; **every seat marker line verbatim** |
| P5.3 | `corpus/SOURCES.md` rows S043+ | P5.2 quotes | adjudicated from the scout drafts: bash `set -n` (required — C2's sourced claim), gitattributes filter, git-check-attr `-z`, gitignore XDG, Python `ast.parse`, SC1046 (admit or reject), git-status(1) as a `rejected` row (R7) with reason+flip; S042 and S036 are recheck/used-by updates, not new rows; required final `validate … souji` exit 0 |
| P5.4 | `corpus/QUALITY.md` Q25/Q26 | P5.1 | Q25 landing gate (non-parsing registry-cited script, stale frozen pin, uncarried seat failure block a landing); Q26 seat probe rule enforced by transcript audit, not self-report; same table shape as Q22–Q24 |
| P5.5 | `SKILL.md` | P4.1 (bytes frozen) | line 138 census verdict map corrected (exit 2 only for protected-path refusal/usage/malformed baseline; degraded `error` rows exit 0); line 167 repeatable-census note; new `Census config semantics (r16)` subsection (Refused/Degraded/Accepted, `error`/`status-unverifiable` meaning); gate-registry rows for `souji-landing-gate` and `r16-landing-gate`; r15 "unverified candidate" correction in place. Every cited path must exist and parse (gate LG-PARSE-REG/LG-MISSING-REG) |
| P5.6 | `SCORECARD.md` | P4.3, P4.5 | operability row: r15 "numeric delta 0" corrected, C1 measured at cbf688a/final rev (20/20, 12/12, 38/38, parse clean; arm discrimination), r14 harm discharged-or-not stated; calibration row: C2 red on b410186 → green at round end, with commands; capabilities table: landing gate (new) and protected-namespace census row update; `## Planned` **r17** row; saturation prose equals table scores; appended `Correction (r16)` note. Q10 checks: `awk '/^## Planned/,/^## Saturation/' SCORECARD.md \| grep -c r17` ≥1; every prose number appears in its row |
| P5.7 | `LOG.md` | P5.6 | (a) correction entry naming the b410186 landing and the seat disclosure omission, append-only wording; (b) C1 evidence entry; (c) C2 entry; (d) ending source census; each with re-verification line, named pathspec, `-c maintenance.auto=false` |
| P5.8 | `corpus/README.md` frontier / `PROVINCE.md` | ConnFrontier | honest line: r16 admits a capability (landing gate), not a coverage-map ground; F2 wider size attribution and unexercised quarantine sites stay frontier; K5 HELD; if unchanged, the reason, not silence |
| P5.9 | r15 corrections (R1/R3) | P5.7 | §1.1 failure shape carried into lesson + SCORECARD + SKILL + LOG; the r15 report is a non-author-adjudicated fleet artifact — name its understatement in the r16 report, do not rewrite its bytes; any r15-lesson note is append-only |

### P6 — marker carry, commit, gate-green (the ordering-critical block)

| # | artifact | depends on | evidence it needs |
|---|---|---|---|
| P6.1 | lesson marker carry | P5.1, P5.2, all wave-1/2 seat reports committed | extract every `.md` under `.ufo/waves/round-16/` line matching the pinned marker regex in the LandingGate contract (five marker classes: a status tag for incomplete/failed/blocked/broken; the two non-parsing phrases; the parser-diagnostic phrase) and paste each stripped line verbatim into the lesson; list them in the report (R3). Re-scan after wave 2 and after every L1 edit to a seat report |
| P6.2 | lane commit + push | P6.1 | `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel` = lane; souji identity; named pathspecs; `-c maintenance.auto=false`; `git show --stat --format= <hash>` lists only approved paths; push; record HEAD |
| P6.3 | `census/round-16/landing-gate-final.json` | P6.2 | `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <pushed-HEAD> --round 16 --base cc21683` → exit 0, `SUMMARY findings=0 checked_reg=… checked_pins=… checked_markers=…`; stdout+exit+rev+digest stored |
| P6.4 | evidence commit + confirm | P6.3 | commit the JSON (no `.md` change), push, rerun the gate on the new HEAD → still 0 findings; both runs named in LOG/report |

C2 is green only at P6.3/P6.4. A green run on `cbf688a` alone is advisory: it predates the lesson
and seat reports that LG-SEAT-UNCARRIED must see, and it predates the re-pin that LG-FROZEN-PIN
must see.

### P7 — report and fleet landing

| # | artifact | depends on | evidence it needs |
|---|---|---|---|
| P7.1 | misroot sweep | P6.2/P6.4 | `git -C /home/vgpnk/Projects/shokunin status --porcelain` (no pathspec); classify every untracked path by content; only souji-authored files get copy → `cmp` → delete fleet copy; other lanes' paths untouched and named as untouched |
| P7.2 | `/home/vgpnk/Projects/shokunin/.ufo/reports/round-16/souji.md` | P7.1 | sections in order: Work performed (claims first, verdicts), Landed changes (commit↔LOG table + pushed HEAD), Before → after measurements (per claim: command + commit; three-arm discrimination; **no** pre-harm-as-green), Sources & frontier (before/after counts, tiers, S043+ by tier, old→new, frontier), Trend verdicts (one each for expansion/quality/discernment), SHONEN (one line per box, `[~]` pointers only, never `[x]`); plus Stale-lane line, cross-domain evidence line (R6: contested scope, owning lane, pointer — reported not absorbed), seat-reported failures verbatim (R3), wave sizes/role mix/dead seats/round total, planner mapping, inherited state, tool installs (likely none), open L0 questions |
| P7.3 | fleet commit | P7.2 | `/home/vgpnk/Projects/shokunin/scripts/hyaku/fleet-commit.sh --as souji -m "round-16: souji report" -- .ufo/reports/round-16/souji.md` (same helper for any l0 append) |
| P7.4 | L0 question (conditional) | DraftOperatorQuestion + CriticNoHarmPreharm | only if residual safety-motivated contractions vs `a31642d` remain (e.g. bound filter drivers now skip status; `~user` include targets now degrade): `souji \| round-16 \| <question>` appended, routed around, named open in the report |

## 3. Routed-obligation closing matrix (R1–R7)

| routed | closes with | gate at |
|---|---|---|
| R1 parse restore | cbf688a census + §1.1 matrix + LOG correction + the four correction sweeps | P1.2, P5.5, P5.6, P5.7 |
| R2 value-blind harm | r15-config 20/20 changed vs 16 red r14-harm; benign/preserve case classes enumerated | P4.3 |
| R3 verbatim seat failure | marker carry block + report section | P6.1, P7.2 |
| R4 frozen pins | re-pin §1.2 + `--frozen` clean | P4.2, P4.4 |
| R5 probe rule enforced | Q26 (transcript audit) + wave-2 contract + report deviations | P3.1, P5.4 |
| R6 cross-domain line | report section from SiblingOverlap | P7.2 |
| R7 git-status row | `rejected` registry row with reason+flip | P5.3 |

Still-open non-routed obligations to state honestly: F2 wider size attribution, unexercised
quarantine sites, K5 HELD, certification OFF, no deletion authority. The operator-sweep directory
disposition stays operator-owned (r15 routed defect 8) — never staged, moved or deleted.

## 4. Wording traps for the evidence tables

- Say "b410186 `bash -n` rc 2 at line 1368, shellcheck rc 1/4 findings, `--selftest` rc 2", not
  "it did not work".
- Say "changed green on 20/20 + 12/12 + 38/38 with parse clean"; call pre-harm/r14-harm
  *discriminating controls* and give their exact red sets; never imply a sequential
  before→after across arms.
- The inert-key claim is scoped: `core.hooksPath`/`core.fsmonitor` any value, `core.alternateRefsCommand`
  any value (case 12), promisor/partial-clone markers on a **complete** repo under
  `GIT_NO_LAZY_FETCH=1` (cases 06/07/09). Do not generalize to partial repos.
- "Only a protected-namespace reach keeps whole-run exit 2" is true *among repository configs*;
  usage and malformed `--compare` baseline remain exit 2 by contract.
- Score policy: verdict changes carry evidence; numeric score only if a reproducible mapping
  exists. Prior rounds kept the legacy-unmapped numbers with delta 0 — do not invent a delta.

## 5. Marker carry block (L1: paste these stripped lines verbatim into the lesson)

The C1 gate scans every `.md` under `.ufo/waves/round-16/`, including this file. Every unique
line in this report that matches the gate's marker pattern is listed below; the lesson must
contain each unique stripped line verbatim. The first line is the actual seat-diagnostic
evidence; the rest are this report's own scan-command provenance and may be carried in a
provenance block.

```text
/var/tmp/souji-r16-matrix.sc9ho6nz/r15-baseline/tools/souji-census.sh: line 1368: syntax error near unexpected token `}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/w1/ && grep -nEi 'STATUS:[[:space:]]*(INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN)|does NOT parse|syntax error' .ufo/waves/round-16/w1/PlanWalk.md; echo "marker-grep rc=$?"; wc -l .ufo/waves/round-16/w1/PlanWalk.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nEi 'STATUS:[[:space:]]*(INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN)|does NOT parse|syntax error' .ufo/waves/round-16/w1/PlanWalk.md; echo "marker-grep rc=$?"; ls tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nEi 'STATUS:[[:space:]]*(INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN)|does NOT parse|syntax error' .ufo/waves/round-16/w1/PlanWalk.md | sed -e 's/^\([0-9]*\):.*/\1/' ; echo '---'; sed -n '176,200p' .ufo/waves/round-16/w1/PlanWalk.md; echo '--- tail ---'; tail -n 4 .ufo/waves/round-16/w1/PlanWalk.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nEi 'STATUS:[[:space:]]*(INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN)|does NOT parse|syntax error' .ufo/waves/round-16/w1/PlanWalk.md | cut -d: -f1
```

Wave-1 reports had already begun landing (22 `.md` files present, executors' gate/re-pin files
still absent); wave-2 reports will add more, so the carry pass in P6.1 must run after wave 2
returns, and its grep is exactly what P6.1's extractor must reproduce.

## 6. Process disclosure (probe rule)

Read-only walk. Files were opened only by exact path. No census, gate, fixture or checker was
executed; no repository code ran; nothing was written except this report; no tool was installed;
no pacman transaction occurred. Two command classes may fall outside the probe rule's enumerated
allowlist and are disclosed for L1 adjudication: (a) `sed -n`, `tail`, `cat`, `wc -l`, `ls -la`
and `grep -n/-c/-E` through the shell on exact named files (read-only, no recursive lane or fleet
search); (b) `python3 -c` / heredoc invocations that parsed named JSON files (wave spec, C1
matrix, swarm registry, frozen pins) — read-only, no target code executed. No forbidden path was
opened or modified: `.ufo/watchdog.log`, `~/.omp`, `.ufo/state`, `MANIFEST.json`,
`census/operator-sweep-20261019/` and sibling repos remain unread and untouched.

## Commands

```sh
wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md /home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md /home/vgpnk/Projects/shokunin/souji-shokunin/SOURCES.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-15.md 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== QUALITY head ===' && sed -n '1,80p' corpus/QUALITY.md && echo '=== QUALITY tail ===' && tail -n 60 corpus/QUALITY.md
sed -n '700,815p' /home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls corpus/ && echo '--- SOURCES tail ---' && tail -n 30 corpus/SOURCES.md && echo '--- ROWS ---' && grep -cE '^\|\s*S[0-9]{3,}\s*\|' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== SHONEN ===' && cat SHONEN.md 2>/dev/null | head -60 && echo '=== README frontier ===' && sed -n '1,120p' corpus/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "import json; s=json.load(open('.ufo/waves/round-16/w1-spec.json')); print(type(s), list(s)[:20] if isinstance(s,dict) else len(s)); print(json.dumps(s, indent=1)[:2000])"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "import json; s=json.load(open('census/round-16/c1-matrix.json')); print(list(s) if isinstance(s,dict) else type(s)); print(json.dumps(s, indent=1)[:3000])"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools/souji-* 2>/dev/null; echo '--- landing gate? ---'; ls -la tools/souji-landing-gate.py corpus/lessons/round-16.md census/round-16/claims.json .ufo/reports/round-16/souji.md 2>&1; echo '--- git show cbf688a stat ---'; git show --stat --format='%H %an %s' cbf688a
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '120,200p' SKILL.md && echo '=== SKILL headings ===' && grep -n '^#' SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "import json,collections; s=json.load(open('.ufo/waves/round-16/w1-spec.json')); its=s['items']; print('n=',len(its)); print('keys:',list(its[0])); c=collections.Counter(i.get('role') for i in its); print(c); [print(i.get('name'),'|',i.get('role')) for i in its]" 2>&1 | head -120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,60p' census/round-16/run-matrix.py && echo '=== matrix summary ===' && python3 -c "import json; d=json.load(open('census/round-16/c1-matrix.json')); [print(arm, {k:(len(x.get('cases',{})) if isinstance(x,dict) else x) for k,x in v.items() if k in ('bash_n','r15-config','r14-namespace','selftest','shellcheck')}) for arm,v in d['arms'].items()]; print('changed', list(d['changed'])); print('lane_head', d.get('lane_head'), 'git', d.get('git_version'))"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,re
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for i in s['items']:
    p=i['prompt']
    outs=[l for l in p.splitlines() if re.search(r'Report:|write|WRITE|produce|artifact', l)]
    print('###', i['name'], '|', i['role'], '|', i.get('axes'))
    for l in outs[:6]: print('   ', l.strip()[:240])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
for arm,v in d['arms'].items():
    print('==',arm)
    for suite in ('r15-config','r14-namespace','selftest','shellcheck','legacy'):
        if suite in v:
            x=v[suite]
            if isinstance(x,dict) and 'cases' in x:
                fails={k:c for k,c in x['cases'].items() if c['verdict']!='PASS'}
                print(' ',suite,'rc',x.get('rc'),'total',x.get('total'),'failed',x.get('failed'),'nonpass',len(fails))
                for k,c in list(fails.items())[:4]: print('     ',k,c['verdict'],c['detail'][:120])
            else:
                print(' ',suite, str(x)[:200])
    print('  keys:', list(v))
print('fixtures_dirty', d.get('fixtures_dirty'))
print('fixtures_sha', d.get('fixtures_sha256'))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
for arm,v in d['arms'].items():
    print(arm, 'bash_n', v['bash_n'], 'shellcheck', v.get('shellcheck_warning'), 'selftest', v['selftest'], 'rev', v.get('rev'), 'sha', str(v.get('sha256'))[:16])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for i in s['items']:
    if i['name'] in ('LandingGate','LandingGateFixture','PreservationRepin'):
        print('#'*20, i['name'], i['role'])
        print(i['prompt'])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,textwrap
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
want={'DraftReportSkeleton','DraftSkillSection','DraftOperatorQuestion','ConnQualityCriterion'}
for i in s['items']:
    if i['name'] in want:
        print('#'*10, i['name'])
        p=i['prompt'].split('IMMEDIATELY STOP',1)[-1]; p=p.split('\n\n',1)[-1]
        for chunk in textwrap.wrap(p, 240): print(chunk)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,textwrap
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
want={'DraftLessonMistakes','DraftLessonGate','DraftR15Correction'}
for i in s['items']:
    if i['name'] in want:
        print('#'*10, i['name'])
        p=i['prompt'].split('IMMEDIATELY STOP',1)[-1]; p=p.split('\n\n',1)[-1]
        for chunk in textwrap.wrap(p, 240): print(chunk)
EOF
cd /home/vgpnk/Projects/shokunin && sed -n '1,80p' .ufo/reports/round-15/souji.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,40p' corpus/SOURCES.md && echo '=== S041/S042 ===' && grep -nE '^\|\s*S04[12]\s*\|' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'Correction (r' SCORECARD.md LOG.md | head -20; echo '=== report sections r15 ==='; grep -n '^#\|^##' /home/vgpnk/Projects/shokunin/.ufo/reports/round-15/souji.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '120,240p' corpus/lessons/round-15-verifier-spotcheck.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -8 && echo '=== STATUS ===' && git status --porcelain | head -50 && echo '=== R16 WAVE DIR ===' && ls -la .ufo/waves/round-16/ 2>/dev/null && ls -R .ufo/waves/round-16/ 2>/dev/null | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== CENSUS R16 ===' && ls -la census/round-16/ 2>/dev/null && echo '=== TOOLS ===' && ls -la tools/ && echo '=== FIXTURES R15/R16 ===' && ls -la tests/fixtures/ | tail -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,120p' corpus/lessons/round-15-verifier-spotcheck.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '"Round-16 revisions"\|HARM_CASES\|CASE_CLASSES\|EXPECTED_IDS' tests/fixtures/r15-census-config.py | head -20 && sed -n '1,60p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== expected.json ===' && cat tests/fixtures/r15-preservation-frozen/expected.json && echo '=== sha at cbf688a ===' && git show cbf688a:tools/souji-census.sh | sha256sum && sha256sum tools/souji-census.sh && echo '=== frozen files ===' && ls -la tests/fixtures/r15-preservation-frozen/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== SKILL 130-175 at cbf688a ===' && git show cbf688a:SKILL.md | sed -n '130,175p' | cat -n && echo '=== r15 lesson 85-105 ===' && sed -n '85,105p' corpus/lessons/round-15.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,textwrap
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for i in s['items']:
    if i['name'] in ('SrcBashSetN','SrcGitStatusRejected','ConnRoutedLedger','ConnFrontier'):
        print('#'*10, i['name'])
        p=i['prompt'].split('IMMEDIATELY STOP',1)[-1].split('\n\n',1)[-1]
        for c in textwrap.wrap(p,240): print(c)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,textwrap
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
want={'SrcGitattributesFilter','SrcGitCheckAttr','SrcGitignoreXdg','SrcGitConfigIncludesRecheck','SrcGitNoLazyFetch','SrcShellcheckSC1046','SrcPythonAst'}
for i in s['items']:
    if i['name'] in want:
        print('#'*8, i['name'])
        p=i['prompt'].split('IMMEDIATELY STOP',1)[-1].split('\n\n',1)[-1]
        for c in textwrap.wrap(p,230): print(c)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'degrade' tools/souji-preservation-evidence.py | head -10; echo '--- fixture cases ---'; grep -n 'degrade\|HARM_CASES\|CASE_CLASSES\|EXPECTED' tests/fixtures/r15-preservation-evidence.py | head -20; echo '--- py sizes ---'; wc -l tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('.ufo/waves/round-16/w1/swarm-registry.json'))
print(type(r), list(r)[:10] if isinstance(r,dict) else len(r))
print(json.dumps(r, indent=1)[:1200])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,textwrap
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
want={'ConnScorecard','ConnLogConvention','ConnSkillRegistry','ConnShonen','SiblingOverlap','DistillRoutedEvidence','RevengeInertKeys','MutateScanConfig'}
for i in s['items']:
    if i['name'] in want:
        print('#'*8, i['name'])
        p=i['prompt'].split('IMMEDIATELY STOP',1)[-1].split('\n\n',1)[-1]
        for c in textwrap.wrap(p,230): print(c)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && read -r -d '' _ < /dev/null; cat tests/fixtures/r14-cache-frozen/expected.json && echo '=== r13 cert frozen ===' && cat tests/fixtures/r13-cert-frozen/expected.json 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,textwrap
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
want={'CriticGateVacuity','CriticNoHarmPreharm','RevGateSpec','SentinelStoreAccess','CriticDisclosureR3','CriticClaimSeparability','CriticNamespaceWeakening','RevLegacySelftestGap','RevR14NamespaceRetention'}
for i in s['items']:
    if i['name'] in want:
        print('#'*8, i['name'])
        p=i['prompt'].split('IMMEDIATELY STOP',1)[-1].split('\n\n',1)[-1]
        for c in textwrap.wrap(p,230): print(c)
EOF
cd /home/vgpnk/Projects/shokunin && tail -n 20 .ufo/reports/round-15/souji.md; echo '=== fleet status ==='; git status --porcelain -- .ufo/waves .ufo/reports | head -20; echo '=== round16 report dir ==='; ls -la .ufo/reports/round-16/ 2>&1 | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --quiet cbf688a -- tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tools/souji-census.sh; echo "worktree-eq-cbf688a rc=$?"; sha256sum tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tools/souji-census.sh; echo '=== SKILL cites at cbf688a ==='; git show cbf688a:SKILL.md | grep -n 'souji-census.sh\|souji-landing-gate'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## \|^### ' LOG.md | tail -12; echo '=== LOG last 6 lines ==='; tail -n 6 LOG.md; echo '=== SCORECARD operability row ==='; grep -n '^| operability\|^| calibration\|^| coverage' SCORECARD.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '60,106p' SCORECARD.md | cat -n | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:SKILL.md | grep -oE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' | sort -u
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only cbf688a -- tools tests/fixtures census/round-13 census/round-14 | grep -E '\.(sh|py)$' | sort
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,40p' corpus/lessons/round-14.md; echo '=== gate heading ==='; grep -n '^## ' corpus/lessons/round-14.md corpus/lessons/round-13.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'Correction' corpus/lessons/round-12.md corpus/lessons/round-13.md corpus/lessons/round-14.md | head -15; echo '=== r13 lesson correction sample ==='; grep -n -A4 'Post-review fixes\|Correction (r' corpus/lessons/round-12.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '60,129p' census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'CASE_CLASSES = \|HARM_CASES = \|EXPECTED_IDS = ' -A28 tests/fixtures/r15-census-config.py | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
for arm,v in d['arms'].items():
    for suite in ('r15-config','r14-namespace'):
        x=v[suite]
        fails=sorted(k for k,c in x['cases'].items() if c['verdict']!='PASS')
        print(arm,suite,'fail',len(fails),':',','.join(fails) if fails else '-')
    print(arm,'selftest',v['selftest'])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/w1/ && grep -nEi 'STATUS:[[:space:]]*(INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN)|does NOT parse|syntax error' .ufo/waves/round-16/w1/PlanWalk.md; echo "marker-grep rc=$?"; wc -l .ufo/waves/round-16/w1/PlanWalk.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## ' .ufo/waves/round-16/w1/PlanWalk.md; wc -l .ufo/waves/round-16/w1/PlanWalk.md; git status --porcelain -- .ufo/waves/round-16/w1/PlanWalk.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'synta[x] error|does NO[T] parse|STATU[S]:[[:space:]]*(INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN)' .ufo/waves/round-16/w1/PlanWalk.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nEi 'STATUS:[[:space:]]*(INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN)|does NOT parse|syntax error' .ufo/waves/round-16/w1/PlanWalk.md; echo "marker-grep rc=$?"; ls tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nEi 'STATUS:[[:space:]]*(INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN)|does NOT parse|syntax error' .ufo/waves/round-16/w1/PlanWalk.md | sed -e 's/^\([0-9]*\):.*/\1/' ; echo '---'; sed -n '176,200p' .ufo/waves/round-16/w1/PlanWalk.md; echo '--- tail ---'; tail -n 4 .ufo/waves/round-16/w1/PlanWalk.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nEi 'STATUS:[[:space:]]*(INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN)|does NOT parse|syntax error' .ufo/waves/round-16/w1/PlanWalk.md | cut -d: -f1
```
