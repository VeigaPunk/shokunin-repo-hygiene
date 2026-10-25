author: hyaku closure (non-author integrator, @m_opus)

# Round 18 — non-author closure and verifier spot-check

## Decision

**Status: ok; admitted: true; verdict: admitted.** The report is real and committed, not a marker. All three declared claims verify within their declared, scoped boundaries:

- C1 (operability): every count was re-derived from the committed matrix, and the containment code was read statically.
- C2 (calibration): verified from committed gate receipts and the 11-finding decomposition. The gate was not executed.
- C3 (coverage/capability): verified from committed fixture and agreement records, plus a static list-only/read-only review. The tool was not executed.

No axis is harmed against the round baseline `b576341`. Fixture expectations and denominators were not weakened. Kills are confined to sessions the lane itself spawned. The r17 routed defects R1–R4 are fixed.

Scope of this admission:

- C1 bounds repository-content reads **after enumeration**, for descendants that stay in the assigned group or session. Escaping descendants, unresponsive filesystem/NSS calls during discovery, and D-state processes are not contained, and the lane says so.
- No no-harm claim is made against pre-harm `a31642d`. The inherited contractions stay open under L0 `souji | round-16`.
- Deletion certification stays **OFF**, and K5 stays **HELD**.
- The transcript audit is **not clean** (see below). The lane discloses this, and it is not admission authority.

Reviewed: before `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, after `8be65236a4b61fffe9c0d05d30043650848c0a60` (code final at `4800fd7`, counter fix at `2d4c7f8`).

The closure ran no lane gate, selftest, fixture, census, proc census or counter (§Gate standard, Closure consequence). It ran no live probe of the census either: a b576341-arm FIFO probe can leave blocked host processes, and this closure must not reap. It ran no jj command, sent no signal, and read no `/proc/*/environ`. It did not open `census/operator-sweep-20261019/`. Four read-only reviewer seats (RevC1Containment, RevC2PointerGate, RevC3ProcCensus, RevCarryR1R4) parallelised the static reads; every number below was either re-derived by this integrator or cross-checked against the cited committed bytes.

Driver digest (copied from mutable `.ufo/watchdog.log`, lines 507 and 524):
- `2026-10-20T16:24:51-03:00 launch souji round=18 pgid=1861869 driver=hyaku-inline attempt=1`
- `2026-10-20T20:26:38-03:00 complete souji round=18; hyaku-inline attempt=1`

## Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report landed by lane | `git log --format='%an %H' -- .ufo/reports/round-18/souji.md` | `souji-shokunin 856e4f6bd41ddad513bc2a77f936f82972d430c5` (20:26:07 -03); ancestor of fleet `refs/heads/master` | ok |
| report after lane tip | lane `8be6523` 20:24:18 -03 < report 20:26:07 < driver complete 20:26:38 | | ok |
| cited hashes ancestors | `git cat-file -t <h>; git merge-base --is-ancestor <h> refs/heads/master` for 3f822e8 42d9ff3 2fc5f33 5efb519 4800fd7 2d4c7f8 74f9adb 8be6523 | all `commit`, all ancestors, author/committer `souji-shokunin`; `rev-list --count b576341..8be6523` = 8 = table rows | ok |
| L0 questions | fleet `52b3863` ancestor of fleet master | `.ufo/l0-questions.md:70-71` (orphan-reap approval; r14 pin procedure) | ok |
| pushed | `jj-lane.sh state` | `branch=master local=remote=8be6523… ahead=0 behind=0 head=detached tracked=0 untracked=1`; `ls-remote origin refs/heads/master` → `8be6523…` | ok |
| no uncommitted round work | `git status --porcelain` | only `?? census/operator-sweep-20261019/`: operator-owned, inherited, unopened. It is not unfinished author work. | ok |
| SHONEN heading | report `## SHONEN` | 4 lines, all `[~]`; `git diff b576341 8be6523 -- SHONEN.md` empty | ok |
| prompt fidelity | Python `difflib`: `templates/round-prompt.md` (fleet copy = kimi copy; LANE/ROUND/FLEET_ROOT substituted) vs `.ufo/prompts/souji-round-18.md` before `## 6.` | 4 diff lines: the `<souji-repo>` working-dir expansion and the `{{AXES}}` expansion; §6 hyaku addendum present; prompt committed by souji-shokunin `0befd1a` | ok |
| SCORECARD | `git diff b576341 8be6523 -- SCORECARD.md` (8+/3−) | coverage 8 / calibration 7 / operability 8 unchanged ("numeric delta 0, legacy-unmapped"); 3 capability rows; r18 done; r19 **planned, not started** (no r19 prompt, report or watchdog line exists) | ok |
| append-only files | `git diff b576341 8be6523 -- LOG.md corpus/QUALITY.md corpus/SOURCES.md` | 0 deleted lines in each (LOG +17, QUALITY +12, SOURCES +19) | ok |

## Transcript and wave evidence

| check | command | observed |
|---|---|---|
| waves | `ls census/round-18/transcripts/w1 w2 \| wc -l` | 91 + 79 = 170 files; `MANIFEST.sha256` 170 lines, `sha256sum -c --quiet` ok |
| dead seats | `git show 8be6523:.ufo/waves/round-18/dead-seats.json` | `wave1_initial_dead 0`, `wave2_initial_dead 0`; one same-identity follow-up `ScribeRowsGit-5` failed on a Haiku 429 (retry-after 8,152,000 ms), `replaced: false`. L1 completed the source re-opens itself (S072–S078). |
| secrets | `gitleaks git --redact --log-opts=b576341..8be6523` (gitleaks already installed) | 8 commits, ~5.58 MB, `no leaks found`; committed `transcript-secret-scan.json` exit 0, ~1.80 MB |
| raw audit | `jq` over `seat-audit-w1.json`, `seat-audit-w2.json` | w1 4,132 calls, 139 major, 18 minor; w2 2,859 calls, 92 major, 16 minor (nonzero, retained) |
| adjudication | `jq '[.adjudications[].decision] \| group_by(.)'` | 231 = 139 + 92: 196 false-positive, 26 contract-deviation, 9 confirmed-read-violation (RevMisrootRisk driver-state reads). `extra_undetected_violation`: MatrixR18 SIGKILLed four prefix-matched processes it did not start (R18-M6). Its measurements are void; the final matrix was L1-run. |
| misroot | `misroot-final.json` | `state_files_opened: false`, `souji_seat_misroots_found: []` |

Verdict: the audit is **not clean**, and that is disclosed rather than hidden. The violations are adjudicated per call. No claim number rests on a seat that violated its contract, because L1 re-ran every installed acceptance check (`final-verification-4800fd7.json`: 15 checks, all exit 0). No private values were copied here.

## Per-claim re-check

### C1 operability: improved, bounded (counts re-derived from the committed matrix; containment statically verified)

| measurement | command | observed | vs claim |
|---|---|---|---|
| matrix tallies | `jq -r '.arms[] … [suite].total/.failed/.leftover_procs_count'` over `census/round-18/c1-matrix-4800fd7.json` | r17-base b576341: r18-bounded 12/**9**, r17-hygiene 29/0, r15-config 20/0, r14-namespace 12/0, selftest 49/0. changed 4800fd7: 12/**0**, 29/0, 20/0, 12/0, **69**/0. pre-harm r18-bounded 10, r14-harm 9. New residue 0 in every arm × suite; `invalid_suites` [] | agrees |
| failing ids | RevC1Containment over case rows | baseline fails B1–B4 and B8–B12; B5–B7 pass in every arm (preserved controls) | agrees |
| binding | `changed_rev` / `fixtures_sha256` vs `sha256(git show 8be6523:<fixture>)` | `changed_rev` = 4800fd7; all 4 fixture digests equal committed bytes; r14 fixture digest `e6a984b1…14b2` identical at b576341 and 8be6523 (revert-to-pin confirmed) | agrees |
| code freeze | `git diff --stat 4800fd7 8be6523 -- tools tests` | only `r15-preservation-frozen/{expected,record}.json` change; census tool and runner frozen | agrees |
| expectation weakening | `git diff b576341 8be6523 -- tests/fixtures/r15-census-config.py tests/fixtures/r17-census-hygiene.py` | only session-runner plumbing and `kill_session` added; 0 assertion, expected-value or case-count edits. The runner requires `total>0` and `sum(FAIL)==failed`. | none found |
| containment | static read of r15/r17 fixtures, `run-matrix.py:87-174`, `r18-census-bounded.py:484-518`, `souji-census.sh` watchdog | SIGKILL is armed only on timeout, and only for pids whose stat session equals the spawned leader. run-matrix adds a same-uid check and a start-time recheck. Argv-prefix matches are counted as residue, never as kill targets. No `pkill`, `killall` or name matching. The watchdog signals only its own `set -m` worker group. | agrees |
| fail capability | static read of `r18-census-bounded.py` | `EXPECTED_IDS` B1–B12: error rows, exact `repo-timeout` stderr, neighbour rows equal, B10 parent TERM/KILL with no partial TSV, B11 rc 2 refusal. The runner materialises each arm's tool from `git show <rev>:tools/souji-census.sh`, so 9/12 at b576341 is genuine. | agrees |

No live census probe was run (see Decision). C1 is graded on committed evidence that has been re-derived.

### C2 calibration: improved within the declared grammar (gate receipts verified; gate not executed)

| measurement | command | observed | vs claim |
|---|---|---|---|
| before receipt | `jq` over `gate-pointers-before-finalgrammar-b576341.json` | exit 2 (no round-18 reports at b576341, which is could-not-evaluate by design), findings **11**, pointer tokens 320, fleet 3, exemptions 0 | agrees |
| after receipt | `jq` over `gate-pointers-after-final.json` | exit 0, findings **0**, pointer tokens **468** (larger denominator), fleet 3, exemptions 4; `resolved_rev` = `74f9adb489fcf…`, base b576341; reg 33, changed 13, pins 13, measured 3, markers 10, reports 175 | agrees |
| 11 = 7 + 4 | finding list vs `git ls-tree -r 8be6523` and `corpus/pointer-exemptions.tsv` | 7 LG-DANGLING-PTR citations of never-committed `ddb7347` records (SKILL.md:163,165; README.md:216; jj-colocation-receipts:2,44,126,148) now point to committed targets. 4 exemptions: exactly 4 rows, exact-path membership (no globs or prefixes), reasons given, each consumed. A stale-exemption check (`LG-DANGLING-PTR-EXEMPT-STALE`) exists. | agrees |
| scope | gate diff b576341..8be6523 | the check is new for round ≥18; no narrowing of the scanned path classes; gate sha `f0f7bf2f…` identical at 4800fd7, 74f9adb and 8be6523 | no weakening |
| selftest / fixtures | `final-verification-4800fd7.json` | gate selftest `pass=61 fail=0`; r18 pointer fixture `total=11 failed=0`; r16 fixture 15/0. Fixture cases assert nonzero exits with exact finding ids, and a vacuity stub must fail. | agrees |
| replays | `gate-replays-final-4800fd7.json` | 5 replays `match: true` (semantic exit/multiset; byte identity not claimed) | agrees |
| registry | `SKILL.md:172` @8be6523 | `souji-landing-gate` row: verdict map 0/1/2, `--selftest` spelling, LG-DANGLING-PTR and EXEMPT-STALE named | conformant |

### C3 coverage/capability: improved, list-only frontier (fixture and agreement records verified; tool not executed)

| measurement | command | observed | vs claim |
|---|---|---|---|
| before | `git ls-tree -r b576341 \| grep -c 'proc-census\|leak-count'` | 0 | agrees (no surface) |
| list-only | static read of `tools/souji-proc-census.sh` and `leak-count.py` @8be6523; `grep -c environ` | census mode reads stat/status/cmdline/cwd/fd/wchan and prints to stdout. `kill` appears only in `--selftest` cleanup of its own identity-checked workers. environ hits 0/0/0 (tool, counter, fixture). | agrees: list-only, no reap path |
| fixture | `final-verification-4800fd7.json` proc-fixture; tool sha vs `git show 4800fd7:` | `SUMMARY total=19 failed=0`; tool digest `37c3316a…` equals the 4800fd7 and 8be6523 bytes. A header-only stub fails 12/19 cases, including P1 and P2. | agrees |
| classes | static | cwd-deleted, argv-path-gone, fd-path-gone (0→3) | agrees |
| agreement | `jq` over `proc-agreement-final.json`, `proc-agreement-counterfix.json`, `counter-exclusion-repair.json` | The failed pair (66 vs 65, stable missing PID 1659, `pass:false`) is retained. After the fix: two pairs 66=66 with identical pid sets and empty stable diffs. The seeded repair goes 66→67. | agrees |
| counter fix | `git diff 4800fd7 2d4c7f8 -- census/round-18/leak-count.py` | ancestor-set exclusion replaced by own-PID-only exclusion. This widens what the counter observes, so it does not manufacture agreement. | agrees |
| redaction | class-only scan of 5 committed proc TSVs | 0 credential-shaped hits | agrees |

## Routed-defect carry (r17 closure R1–R4)

| item | evidence @8be6523 | result |
|---|---|---|
| R1 recipe owner | `q_jj_commit_recipe` reads local `lane.id`, falls back to the `<id>-shokunin` basename, else a placeholder plus a note; 7 R1 selftest cases; fixture J13 FAIL on b576341 (`jj-receipts-r18-baseb576341.txt` total=35 failed=1), PASS on the changed tools; final 37/0/0 | fixed |
| R2 dangling records | SKILL r17-gate-replays row re-pointed to `gate-replays-4f48343.json`; README:216 and knowledge:2 labeled corrections; `LOG.md:916` untouched and corrected by an appended entry; remaining `ddb7347` mentions are labeled provenance only | fixed |
| R3 22→21 | SCORECARD operability row "21 repositories" | fixed |
| R4 Q7 | Q29 supersedes Q7 for colocated repos; Q7 text unchanged | fixed |

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1: bounded fixture 9→0 failed, census selftest 49→69, no other suite regressed, 0 new residue; bounded scope disclosed |
| calibration | improved | C2: pointer findings 11→0 with the denominator 320→468; 7 real repairs plus 4 exact exemptions; selftest 61/0 and fixture 11/0 receipts; R1–R4 fixed |
| coverage | improved | C3: process residue governed 0→3 classes, fixture 19/0, retained failed observation and a repaired agreement; list-only F5 frontier |
| depth | unchanged | not claimed (Q29–Q35 and SKILL rows are not measured as a move) |
| freshness | unchanged | not claimed (S038 anchor drift is routed, not fixed) |
| adjacency | unchanged | not claimed. PROVINCE routes liveness to mori, host repair to tsukuroi and credentials to kagi; listing is not reap authority. |

## Discernment spot-check (LEARNING.md)

| item | gate decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S064 git attr.c | admit (mined) | `curl https://raw.githubusercontent.com/git/git/v2.56.0/attr.c`, lines 702–716 | agree | The `READ_ATTR_NOFOLLOW` open/`open(path, O_RDONLY)` lines are verbatim, and `fstat` follows the blocking open. A type guard cannot bound git's own open, which grounds the watchdog. |
| S076 proc_pid_exe (supersedes S069) | admit (mined) | https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html | agree | "If the pathname has been unlinked … ' (deleted)' appended to the original pathname." is verbatim (20 words by `wc -w`). The narrowed teaches (exe only; cwd/fd measured; inode identity for literal names) matches R18-M9. |
| S074 subprocess.run timeout (supersedes S067) | admit (mined) | https://docs.python.org/3.14/library/subprocess.html | agree | "If the timeout expires, the child process will be killed and waited for." is present. It names the child only, so descendant cleanup needs the session kill the fixtures add. |
| S073 kill(2) (supersedes S066) | admit (mined) | https://man7.org/linux/man-pages/man2/kill.2.html (man-pages 6.19, 2026-06-05) | agree | The RETURN VALUE sentence is verbatim, 17 words. "At least one signal was delivered" correctly blocks reading a group kill as proof of a full reap. |
| reject: S066 teaches "group signal = whole-tree reap" | reject (superseded by S073) | same kill(2) page | agree | The page guarantees only that at least one signal was delivered. Escaping descendants are a measured limit, not covered. |
| reject: S071 teaches "gate enumerates via `cat-file -e`" | reject (superseded by S078) | `tools/souji-landing-gate.py:200` and https://git-scm.com/docs/git-ls-tree | agree | The gate enumerates with `ls-tree -r -z --full-tree` and reads blobs via `cat-file blob`, never `-e`. The S078 quote "Show tree entries even when going to recurse them." is present. |

New SOURCES row re-opened: **S077** open(2) ENXIO, https://man7.org/linux/man-pages/man2/open.2.html. The quote "O_NONBLOCK | O_WRONLY is set, the named file is a FIFO, and no process has the FIFO open for reading." is present and 20 words (≤25). Agree.

Registry counts were re-derived by splitting `| S### |` rows into 11 cells at both revisions. b576341: 63 rows, A59/B3/C1, mined 44, queued 15, rejected 4, malformed 0. 8be6523: 78 rows, A74/B3/C1, mined 59, queued 15, rejected 4, malformed 0. SOURCES sha256 changed `25c91f68…` → `74c5e01e…`, and 0 lines were deleted. All of this agrees with the report.

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0, `souji ok`. There are 14 W04 shared-URL warnings (S035, S036, S038, S049, S057, S058, S059, S063, S065, S072, S073, S075, S076, S077), as reported.

The quality criteria are grounded. Q29 cites closure R1/R4. Q33 and Q34 supersede Q32 and Q30 with lesson-backed narrowing (R18-M8, R18-M9). Q35 extends Q31 to exemptions.

## Trend verdicts

- **expansion: improved.** Three capabilities enter with committed evidence: the bounded census, the dangling-pointer gate and the list-only process census. F5 is newly observed, and SOURCES grows 63→78 with 15 newly mined rows. No knowledge-entry growth is claimed, and this closure grants none.
- **quality: improved.** R1–R4 are fixed, with append-only corrections. Seven over-attributed teaches cells are visibly superseded rather than rewritten. The frozen preservation record was regenerated from real runs, and the r14 fixture was restored to its pinned bytes. The failed proc observation is retained instead of overwritten.
- **discernment: improved.** This spot-check agrees on 4 admits and 2 rejects. The r17 closure disagreements became lesson-backed Q29–Q31, and wave-2 falsification produced Q33–Q35.

## Routed defects (souji owes these next round)

- **D1 (evidence binding).** Report line 70 says the gate was rechecked at tip `8be6523` with exit 0 and identical counts, but no committed receipt binds `8be6523` (`git grep 8be652 8be6523` = 0). The committed receipt binds `74f9adb`. A static read of the 5-file tip delta supports the claim, but either commit a receipt for the cited revision in a later commit or cite only `74f9adb`.
- **D2 (pin).** `proc-agreement-counterfix.json` records only the tool base `4800fd7`. The post-fix counter bytes (`2d4c7f8`, sha256 `a2653019…`) are bound only by `counter-exclusion-repair.json`'s `measured_commit`, with no digest. Pin the counter digest in agreement records.
- **D3 (baseline receipt).** The gate selftest baseline "33" comes from a wave-2 static count (`w2/RevGatePointerCode.md:19`), not a committed run receipt. The final 61/0 is receipt-backed. Label the baseline as static or commit its run.
- **D4 (audit coverage).** The seat auditor has no signal class, so MatrixR18's foreign-prefix SIGKILL (R18-M6) was caught only by self-disclosure. There were 9 confirmed driver-state reads. Add a signal/kill call class to `souji-seat-audit.py` and re-state the forbidden-read rule in the next dispatch.
- **D5 (minor containment).** The r15/r17 fixture `kill_session` lacks run-matrix's (pid, starttime) recheck, which leaves a theoretical pid-recycle window between the timeout and the session scan.
- **Carried and disclosed (not closure remediation).** These stay open:
  - S038 anchor drift and carry-gate wrap truncation.
  - HEAD-pinned r13/r14 runners.
  - Inherited contractions vs `a31642d`, jj keep refs, operator-sweep disposition, orphan-reap approval (58 listed, none reaped) and the r14 control-pin procedure. These are operator-owned L0 lines 59, 66, 67, 70 and 71.
  - Certification OFF; K5 HELD.

Operator note: the 4 SHONEN boxes remain `[~]`, and they look checkable by a non-author from committed evidence. Promotion is operator-owned and was not acted on here.

Tool installs by this closure: none (gitleaks, jq and curl were already present).
