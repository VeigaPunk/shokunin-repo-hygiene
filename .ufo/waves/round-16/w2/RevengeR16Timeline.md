# RevengeR16Timeline — r16 timeline vs wave-1 seat revisions

Seat: `SoujiR16.RevengeR16Timeline` (revenger, leaf). Axis: calibration.
Method: read-only. `git log/show/diff/cat-file/ls-tree/rev-parse`, `sha256sum`,
`bash -n tools/souji-census.sh`, reads/greps on named files. No census, fixture,
gate, checker or audit was executed; no /var/tmp scratch; only this report written.

Lane HEAD at probe start: `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae` (as briefed).
**HEAD moved during the probe**: L1 committed
`163158a706352f1c0ee3521c4da2e5289970db57` ("round-16: lesson, sources S043-S050,
Q25/Q26, LOG correction and entries, SCORECARD, SKILL, README", 2026-10-20
12:03:21 -0300). Every "HEAD" statement below is at `163158a` unless a revision
is named. The window asked for is therefore six commits, not five.

## 1. Timeline `58ace9f..163158a`

| # | commit | time (-0300) | subject | paths that moved the evidence base |
|---|---|---|---|---|
| 0 | `58ace9f` | — | r15 non-author closure (base) | — |
| 1 | `cbf688a` | 11:13:47 | C1 restore | `tools/souji-census.sh` (1784 lines, `fed43c71…`), `tests/fixtures/r15-census-config.py` (`9151cde8…`), `census/round-16/run-matrix.py` (`87c9af0c…`) |
| 2 | `0a70bef` | 11:40:42 | C1 integration of wave-1 fixes | census (`64a60fd0…`, 1877 lines), fixture (`85de2a43…`), runner (`2815712b…`), adds untracked-at-the-time `c1-matrix.json` + `live-fleet.json` |
| 3 | `c6207bd` | 11:52:32 | R4 checker repair + frozen regenerator | `tools/souji-preservation-evidence.py` (`5942f689…`), `tests/fixtures/r15-preservation-evidence.py` (`1b21f642…`), fixture detail cap (`27474396…`), `regenerate.py`; **frozen record still old** (`93e48ab6…`/`4749ad07…`) |
| 4 | `7a79dc2` | 11:55:35 | C2 gate + fixture + seat audit + wave-1 evidence | gate (`2cbbe1ba…`), gate fixture (`8f07b16d…`), audit (`298813f2…`), 63 w1 reports + w1 spec/dispatch, `c1-matrix-final.json`, `live-fleet-final.json`, `seat-audit-w1.json`, **re-pinned** `expected.json` (`d955b18c…`)/`record.json` (`173db777…`) |
| 5 | `a6ec781` | 11:59:22 | C2 narrowing + R5 ALLOWED-EXEC | gate (`e7d2439d…`), gate fixture (`aae67c9c…`), audit (`c9ff355c…`) |
| 6 | `163158a` | 12:03:21 | lesson/registry landing | `corpus/lessons/round-16.md`, `corpus/SOURCES.md` (S043–S050), `LOG.md`, `SCORECARD.md`, `SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `c1-matrix-landing.json`, w2 spec/dispatch |

Artifact digests per commit (paths that wave-1 conclusions name; `git show <rev>:<path> | sha256sum`):

| path | cbf688a | 0a70bef | c6207bd | 7a79dc2 | a6ec781 | 163158a |
|---|---|---|---|---|---|---|
| `tools/souji-census.sh` | fed43c71 | 64a60fd0 | 64a60fd0 | 64a60fd0 | 64a60fd0 | 64a60fd0 |
| `tests/fixtures/r15-census-config.py` | 9151cde8 | 85de2a43 | 27474396 | 27474396 | 27474396 | 27474396 |
| `census/round-16/run-matrix.py` | 87c9af0c | 2815712b | 2815712b | 2815712b | 2815712b | 2815712b |
| `tools/souji-preservation-evidence.py` | 81ffd389 | 81ffd389 | 5942f689 | 5942f689 | 5942f689 | 5942f689 |
| frozen `expected.json` | 93e48ab6 | 93e48ab6 | 93e48ab6 | d955b18c | d955b18c | d955b18c |
| frozen `record.json` | 4749ad07 | 4749ad07 | 4749ad07 | 173db777 | 173db777 | 173db777 |
| `tools/souji-landing-gate.py` | ABSENT | ABSENT | ABSENT | 2cbbe1ba | e7d2439d | e7d2439d |
| `tests/fixtures/r16-landing-gate.py` | ABSENT | ABSENT | ABSENT | 8f07b16d | aae67c9c | aae67c9c |
| `tools/souji-seat-audit.py` | ABSENT | ABSENT | ABSENT | 298813f2 | c9ff355c | c9ff355c |

Consequence: **no wave-1 report could have seen `0a70bef` or later.** All 63
reports were committed at `7a79dc2`; 56 of them name `cbf688a`; the census they
describe (`fed43c71`) stopped being HEAD at 11:40:42, before any report was
committed. The reports were written 11:13–11:55 against **five different
worktree census digests**: `fed43c71` (committed), `feba44c7` (RevHeaderDocs:9,
ConnScorecard:26), `f7d0686c` (RevengeInertKeys:8), `d9762d55`
(RevFixtureR16Edits:11), and the landed `64a60fd0`. The lesson's R16-M6
(`corpus/lessons/round-16.md:9`) already states this class; the register below
makes it per-claim.

## 2. Stale-review register — do **not** cite as covering HEAD

Verdict key: **stale** = the claim describes bytes a later commit changed;
**stale-state** = true of the revision named but false at HEAD; **holds** =
still true at HEAD, safe to cite with the binding named.

### 2.1 Census / fixture / runner (measured `cbf688a`, landed `0a70bef`)

| report:line | claim | why stale | state at HEAD | verdict |
|---|---|---|---|---|
| `RevMatrixRunner.md:5-6` | worktree census is `fed43c71`, 1784 lines | `0a70bef` rewrote it | `64a60fd0`, 1877 lines | stale |
| `RevMatrixRunner.md` T1 (FIFO/device to `git status`) | status can block on a config-named non-regular file | `0a70bef` rewrote `status_info_file` | returns 3 on non-regular (`64a60fd0:953-957`) → `unverifiable` (`:1023-1026`); no fixture case targets it (`RevStatusInfoFile.md:213`) | stale as open; behavior unproven |
| `RevMatrixRunner.md` T2 (linked worktree soft degradation silent) | `guard_git_surface` rc 1 → `wt-dirty`, no diagnostic | `0a70bef` rewrote `worktree_extra_flags` | prints `config-unsupported: <reason>` before `saw_dirty=1` (`64a60fd0:1156-1160`) | fixed |
| `RevMatrixRunner.md` T5 (exit 2 not only for protected reaches) | TAB/CR/LF and unresolvable config paths exit 2 | `0a70bef` made those return 3 | 3 → `unverifiable` (`64a60fd0:545,558`); usage/malformed baseline still exit 2 | stale as open; claim still overbroad |
| `RevMatrixRunner.md` F1–F4 (runner fail-open, parse fragility, TOCTOU, no producer id) | runner cannot distinguish healthy from unparsed | `0a70bef` rewrote the runner | `valid`/`invalid_suites` + exit 2, split stdout/stderr, `open("x")`, `runner_sha256`/versions (`run-matrix.py:53-60,85-96,128-141`) | fixed |
| `RevMatrixRunner.md` F5 (no tool preflight) | missing `git`/`shellcheck` aborts with traceback | no later commit changed `run()` | still catches only `TimeoutExpired` (`run-matrix.py:37-43`) | **holds** |
| `DraftOperatorQuestion.md:13` | worktree census == HEAD `cbf688a` | changed at `0a70bef` | census is `64a60fd0`; worktree clean | stale-state |
| `DraftOperatorQuestion.md:31` | `~user`/`%(prefix)` on `core.excludesFile`/`core.attributesFile` abort the whole run | `0a70bef` added the return-3 degrade | `|| return 3` → one `error` row (`64a60fd0:946-949,1023-1026`); fixture coverage of this path unproven | stale as open; coverage unproven |
| `RevFixtureR16Edits.md:9-13` | fixture/census `cbf` blobs; in-flight `d9762d55`/`7f3b05cf` | two more integrations landed after that snapshot | `64a60fd0`/`27474396` | stale snapshot (report itself says "acceptance must run committed bytes") |
| `CriticFixtureOverfit.md:29` | `HARM_CASES` omits 18 and 20 | `0a70bef` added both (`r15-census-config.py:161-166`) | fixed | stale |
| `CriticFixtureOverfit.md:31` | `souji-preservation-evidence.py` still holds the r15 class table | `c6207bd` migrated it (03→safety, 07→benign, 14→safety, 18/20 in `CONFIG_HARM_FAILS`; tool:323-357) | fixed | stale |
| `CriticNamespaceWeakening.md:20-23` | soft config return pre-empts later protected guards; "make soft failure sticky" | `0a70bef` accumulates `soft` and continues (`64a60fd0:722-730,828-899,1156-1160`) | fixed | stale as a defect; cite as the implemented correction |
| `SentinelCommandExec.md:91` | F1 "open": fsmonitor may run on non-status git calls | `GIT_CONFIG_COUNT` exports fsmonitor/hooks neutralization for every call (`64a60fd0:162-163`) | fixed | stale |
| `MutateScanConfig.md:2` | m4/m6 survived | fixture gained `r-inc-tilde-store`, `r-tilde-then-store`, `r-inc-twice`, mixed-degrade case_03 (`0a70bef`) | fixed | stale |
| `MutateDirtyFilters.md:5` | M02 survived (XDG default not disabled) | fixture gained `FL_NEUTRAL/r-xdg-default` + case_04 assertion | fixed | stale |
| `ConnFrontier.md:94-104` | "At `cbf688a` … only a config-named path reaching a protected root refuses" | false of `cbf688a` (DraftOperatorQuestion:31 shows the excludes abort); true of `0a70bef`+ | label wrong, content holds at HEAD | partial |
| `DraftSkillSection.md:3` | pinned source is the `cbf688a` header | header rewritten at `0a70bef` (Refused/Degraded split, status_info_file degrade, soft-finding rule) | content matches HEAD; the pinned revision does not | stale pointer |

### 2.2 R4 / frozen pins / checker (measured `cbf688a`, landed `c6207bd`+`7a79dc2`)

| report:line | claim | why stale | state at HEAD | verdict |
|---|---|---|---|---|
| `ConnQualityCriterion.md:157-160,204-205` | "Q25(b) is RED at HEAD `cbf688ab`" | `7a79dc2` re-pinned and regenerated the record | **GREEN**: pins `64a60fd0`/`27474396`/`e6a984b1` equal `git show c6207bd:<path>`; `record_sha256` `173db777` matches `record.json` | stale-state |
| `ConnRoutedLedger.md:18` | pins still `b5187351`/`6314d45d`, record stale | same | re-pinned; measured_commit `c6207bd`; every pin resolves | stale-state |
| `ConnRoutedLedger.md:30` | R4 = **GAP**, "no re-pin commit exists" | `c6207bd` + `7a79dc2` landed R4 | landed | stale-state |
| `ConnShonen.md:52-53` | R4 open at `cbf688a`; pins stale | same | landed | stale-state |
| `ConnSkillRegistry.md:38` | r15 frozen pin stale at HEAD | same | landed | stale-state |
| `ConnScorecard.md:19` | pins stale at HEAD | same | landed | stale-state |
| `CriticDisclosureR3.md:21` | pins still stale; "belongs to R4 until R4 lands" | same | landed | stale-state |
| `DistillRoutedEvidence.md:92-96` | two of three pins stale, lineage open | same | landed | stale-state |
| `DraftLessonMistakes.md:15-16,21` | R16-M2 (pin) and R16-M3 (fixture oracles) open at HEAD `cbf688a` | M2 re-pinned at `7a79dc2`; M3's errno/oracle fixes landed `0a70bef` | both fixed | stale-state |
| `RevengeFrozenPin.md:202` | pin unattested, "still unrepaired at `cbf688ab`" | historical facts hold; the current-state clause is false | record regenerated from real runs at `c6207bd`, committed `7a79dc2`; `declared_consistency_only: true` | historical holds / current-state stale |
| `RevengeR15Landing.md:171-174` | D3: no revision binding at landing | r15 fact; r16 now binds `measured_commit` | holds as r15 history only | holds (historically bound) |

### 2.3 C2 gate / fixture / audit (measured `7a79dc2` or `cbf688a`, landed `a6ec781`)

| report:line | claim | why stale | state at HEAD | verdict |
|---|---|---|---|---|
| `LandingGate.md:38-40` | failure channel includes phrase markers (`do not ship`, `does not parse`, `snapshot_tampered`, …) | `a6ec781` deleted `PHRASE_MARKER_RE` entirely | phrase markers are not a channel | stale |
| `LandingGate.md:62-64` | `b410186 --round 15` → 34 findings, `checked_markers=30` | phrase channel removed | L1's landing measurement: **5 findings** (1 parse, 3 pin, 1 STATUS) | stale |
| `LandingGate.md:73-74,83-84` | `cbf688a --round 15` → 34 findings; `--base` run → 35 | same | not reproducible at HEAD | stale |
| `LandingGateFixture.md:39,45,63,73` | `marker-rewordings` = 5 rows (SeatA–E), total 15, replay "36 LG rows" | fixture case 9 rewritten at `a6ec781`: needs SeatA/B/E/G, excludes C/D/F/H; `lg_rows` and replay counts differ; rows are still 15 | test count holds, contents stale | stale (counts/semantics) |
| `CriticGateVacuity.md:18,20-31,32-37` | pinned regex incl. phrases; "0/12 precision"; predictions: `a31642d` r13 and `cc21683` r14 each exit 1 with 2 false positives | predicate no longer exists; L1's rerun/lesson records **0 findings** at both | predictions falsified at HEAD | stale (measurements) |
| `RevGateSpec.md:32-33` | `b410186` → 5 findings "1 parse + 1 pin + 3 seat"; `cbf688a` → 2 pin findings | composition changed with the narrowing | HEAD output is 1 parse + 3 pin + 1 seat | partial (total coincides, composition wrong) |
| `ConnScorecard.md:24,90,97,99` | gate precision 0/12; marker over-breadth; worktree drift `feba44c7` | drift landed as `0a70bef`; phrase breadth dropped | see §3 | stale-state (the rerun warning at :97 was correct) |
| `ConnRoutedLedger.md:51` | C2 can be vacuously green because the wave dir is uncommitted | wave dir committed at `7a79dc2`; gate exits 2 on a missing dir | fixed | stale |
| `ConnLogConvention.md:92-102` | green at `cbf688a` is vacuous; "exactly two `LG-FROZEN-PIN` until re-pin" | wave dir and re-pin landed | fixed | stale |
| `ConnSkillRegistry.md:40`, `ConnScorecard.md:21`, `ConnRoutedLedger.md:19`, `PlanWalk.md:15` | gate tooling absent | present since `7a79dc2` | present | stale-state |
| `RevengeProbeRecurrence.md:96-101` | "no ledger, no transcript audit, no consequence" | audit tool + `seat-audit-w1.json` exist | 65 seats / 3173 calls / 1 major / 19 minor | stale-state (its V-class design is what landed) |

### 2.4 "HEAD/untracked" claims that a later commit falsified

| report:line | claim | state at HEAD |
|---|---|---|
| `ConnRoutedLedger.md:12` | `c1-matrix.json` untracked (`561393aa`) | committed at `0a70bef`; digest unchanged, but it is a **`cbf688a`** measurement against fixture `9151cde8` (its `R15CFG-03` detail is `git-config-unparsed`; HEAD's is `git-include-cycle`) — cite `c1-matrix-final`/`c1-matrix-landing` instead |
| `PlanWalk.md:14` | matrix untracked | committed |
| `ConnRoutedLedger.md:31`, `ConnScorecard.md:25` | w1 spec / wave dir untracked | committed at `7a79dc2` (63 `.md`) |
| `ConnRoutedLedger.md:31`, `ConnShonen.md:52` | R5 = GAP, no audit artifact | `tools/souji-seat-audit.py` + `seat-audit-w1.json` committed |
| `ConnShonen.md:20`, `ConnScorecard.md:13`, `ConnLogConvention.md:276`, `ConnRoutedLedger.md:13` | changed-arm results at `cbf688a` (`fed43c71`) | still numerically true at `0a70bef`+ (identical totals) but not the same bytes; bind to `c1-matrix-final`/`landing` |
| `PlanWalk.md` P6.3/P6.4 | `census/round-16/landing-gate-final.json` stored, then rerun | **artifact absent** at HEAD (`git ls-tree HEAD census/round-16/` has no gate run) |

## 3. What survives at HEAD (safe citations)

- **No frontier advance.** `58ace9f..163158a` touches no `corpus/knowledge/`,
  `PROVINCE.md`, `corpus/README.md` frontier row or `SHONEN.md`; `ConnFrontier`
  holds at HEAD. Its revision label (`cbf688a`) is wrong only for the config
  paragraph (§2.1).
- **Census parses.** `bash -n tools/souji-census.sh` → rc 0 (seat-run at HEAD).
  `ConnSkillRegistry.md:39`, `ConnShonen.md:20`'s box-3 conclusion holds; their
  digest is stale.
- **C1 discrimination.** `c1-matrix-final.json` (`lane_head 0a70bef`, fixture
  `85de2a43`) and `c1-matrix-landing.json` (`lane_head 7a79dc2`, fixture
  `27474396`) have identical arm outcomes: changed 20/0 + 12/0 + 38/38;
  pre-harm 8 + 10 fails; r14-harm 16 + 0 fails; r15-baseline parse rc 2.
  The `c6207bd` fixture diff only caps the human-readable detail at 400 chars,
  so it cannot alter verdicts. Cite the final/landing files, not
  `c1-matrix.json`.
- **R4/Q25 green** (proof in §2.2).
- **RevStatusInfoFile.md:9-11,186,199,213** is correctly self-bound: cbf688a
  line numbers, live-delta addendum, F1/F6 fixed-in-worktree, F2 fixed but
  untested, F3/F4/F5 live. At HEAD, F4's excludes/attributes base is still
  `${dir%/*}` (`64a60fd0:652`), so F3/F4/F5 remain credible open findings.
- **RevHeaderDocs.md:9-11** and **RevBoundFilters.md:15-18** explicitly treat
  their bytes as a snapshot; use them as cbf688a reviews, never as HEAD.
- **RevMatrixRunner F5** and **T3** still hold: `run()` has no preflight
  (`run-matrix.py:37-43`); `--include-root` still emits `.git`-file roots
  (`64a60fd0:1275-1277`, `RevHeaderDocs` F1).
- **CriticGateVacuity structural findings F3/F4/F5** were implemented at
  `7a79dc2` (HTML-comment strip, pinned heading, disposition token,
  LG-OPEN-ADMITTED; exit 2 on missing wave dir + `checked_reports`;
  `LG-FROZEN-MEASURED`). Its F2 survives **in inverted form**: the delivered
  predicate is now too narrow (see §4). Its measured 0/12 does not.

## 4. C2 at HEAD: the r16 wave's own failure channel is empty

The gate's channel at HEAD (`tools/souji-landing-gate.py:257-270`, vocabulary
`:72-80`) is: a line whose stripped text starts with `STATUS` + `:`/`—`,
outside fences and table rows, whose **first value word** (lowercased) is one of
{incomplete, fail, failed, fails, failing, failure, blocked, broken, partial,
harmed, red, unrun, error, regression, known}.

Applying that predicate to the 63 committed w1 reports (source read, not a gate
run):

- The only matches are bullet/table lines: `CriticGateVacuity.md:41-44,118`
  (each begins `- \`STATUS:` or is an `| A4 |` table row) and
  `LandingGateFixture.md:63` (a table row). The gate excludes all of them:
  table rows because `in_table` is true, bullets because after `strip()` the
  leading `- ` prevents `STATUS_PREFIX_RE` from matching. `ConnLogConvention.md:385`
  is indented inside a 4-backtick fence opened at `:375`, so it is excluded.
- Every one of the 12 r16 STATUS lines L1 carried in
  `corpus/lessons/round-16.md:43-53` starts with a non-vocabulary token
  (`F1`, `residual`, `SURVIVED`, `Probe`, `Source`, `` `b5187351…` ``, `r16`,
  `PROBE`, `live`, `gate`, `skeleton`, `all`).
- Therefore `--round 16` at `163158a` has `checked_markers = 0`
  [INFERENCE: predicate applied by reading; the gate was not run]. A green
  `SUMMARY findings=0 checked_markers=0 checked_reports=63` would mean the
  carry check saw **no** r16 failure, which is false of the wave: 12 seats
  declared defects on STATUS lines and all 12 are dispositioned in the lesson
  (three marked `— open`, plus `MutateScanConfig`'s m2 open as a reason-only
  difference).

This is the same vacuity class `CriticGateVacuity` F1/F4 raised, reintroduced by
the `a6ec781` narrowing. Two consequences for L1:

1. Do not cite a green `--round 16` run as evidence that R3/carry is enforced.
   Report `checked_markers` explicitly; 0 is a could-not-evaluate for seat-carry
   even though exit 0.
2. The lesson's carry section is **truncated** for most long lines, e.g.
   `MutateScanConfig.md:2` continues past "fixture gaps" with "; 0 inconclusive.
   Every pristine and restored detector run passed…"; `SentinelCommandExec.md:91`
   continues past "did not run it." with "As a result, the C1 statement…".
   The gate's carry rule is a normalized full-line substring match
   (`check_carry`: `needle in nl`), so if the channel is broadened those carries
   would fail. Copy the full normalized source lines before broadening.

Smallest fix (one change, two files): make the channel "any `STATUS:` line
outside fences/tables unless its first word is in a benign allowlist"
(`ok none complete completed pass passed clean done draft advisory
design-only`), then copy the 12 full lines into the lesson verbatim and add a
selftest case using the actual r16 shape (`STATUS: F1 is open` →
LG-SEAT-UNCARRIED). Until then, the gate's r16 reach is the r15 shape only.

## 5. Defects in the committed integration artifacts

1. **Mis-bound `resolved@` dispositions** (`corpus/lessons/round-16.md`):
   - `:49` `RevengeFrozenPin.md:202` — `resolved@c6207bd`; the pinned files
     changed at `7a79dc2` (`expected.json` `93e48ab6`→`d955b18c`,
     `record.json` `4749ad07`→`173db777`). Should be `resolved@7a79dc2`.
   - `:60` `AdmissionChecker.md:73-75` — same: the clean record lands at
     `7a79dc2`, not `c6207bd`.
   - `:51` `SrcGitCheckAttr.md:113` — `resolved@a6ec781`; S046/SOURLCES were
     re-derived in `corpus/SOURCES.md` at `163158a`. Should be
     `resolved@163158a`.
   All three are mechanically valid hex ancestors, so LG-SEAT-UNCARRIED will not
   catch them; they are timeline errors, not gate errors.
2. **`landing-gate-final.json` absent.** `PlanWalk` P6.3/P6.4 required the run
   stored and rerun; `census/round-16/` has no gate artifact. Either store the
   run L1 used for the lesson's 5/0/0 + 18/18 + 15/15 numbers (recommended; it is
   also the artifact that would expose `checked_markers`), or stop treating P6.3
   as discharged.
3. **`c1-matrix.json` is committed but is a pre-integration measurement**
   (fixture `9151cde8`, `R15CFG-03` detail `git-config-unparsed`). It stays in the
   tree next to `c1-matrix-final`/`c1-matrix-landing`; the lesson cites the right
   ones, but a report that cites `561393aa` as HEAD evidence would be wrong.

## 6. Verdicts against the assignment

| item | verdict | basis |
|---|---|---|
| Timeline reconstruction | **holds** | six commits, times, paths and per-commit digests in §1; HEAD moved `a6ec781`→`163158a` mid-probe |
| Wave-1 revision binding | **fails as HEAD coverage** | every report predates `0a70bef`; 56/63 name `cbf688a`; five distinct census digests appear |
| Stale-review flagging | **holds** | 24 named stale/partial claims in §2 with the commit that changed the bytes |
| Stale claims L1 should not cite as open | **fails for 15 conclusions** | RevMatrixRunner T1/T2/F1–F4, DraftOperatorQuestion:31, CriticFixtureOverfit:29/31, CriticNamespaceWeakening, SentinelCommandExec, MutateScanConfig, MutateDirtyFilters, Q25/R4 (5 reports), LandingGate/LandingGateFixture/CriticGateVacuity numbers |
| Conclusions safe to cite | **holds** | §3 |
| C2 round-16 carry claim | **fails if claimed green** | `checked_markers=0` by source; §4 |
| R4/Q25 at HEAD | **holds green** | pins equal `git show c6207bd:<path>`; `record_sha256` matches |

Status of the two calibration traps most likely to be repeated:
- **Training-set replay**: `b410186` red is the gate's construction case; the
  held-out history (`a31642d`, `cc21683`) now returns 0 findings, so the gate's
  r16-specific value is the *pin/measured* check and the parse check, not the
  marker check.
- **Digest-only re-pin**: `RevengeFrozenPin` D5 warned it would launder the
  transcript; the landed `regenerate.py` + record captured from real runs
  (`record.runs.{changed,preharm,baseline}` with `TOOL … sha256=` matching each
  arm) is the counter-evidence. Cite that, not the warning as an open defect.

STATUS: ok — timeline reconstructed at `163158a`; 24 stale/partial seat
conclusions flagged with the later commit; 15 "open defect" conclusions shown
fixed at HEAD; C2's round-16 carry channel shown empty by source read; three
lesson `resolved@` pointers mis-bound; `landing-gate-final.json` still absent.

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %ad %s' --date=iso 58ace9f..HEAD
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 58ace9f && git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --format='%h %H %ad %s' --date=iso 58ace9f..HEAD && echo '--- files per commit ---' && for c in cbf688a 0a70bef c6207bd 7a79dc2 a6ec781; do echo "== $c"; git show --stat --format='%h %s' $c | tail -n +2; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for p in tools/souji-census.sh tests/fixtures/r15-census-config.py census/round-16/run-matrix.py tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-preservation-frozen/expected.json tests/fixtures/r15-preservation-frozen/record.json tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py tools/souji-seat-audit.py; do echo "## $p"; for r in 58ace9f cbf688a 0a70bef c6207bd 7a79dc2 a6ec781; do printf '  %s ' "$r"; if git cat-file -e "$r:$p" 2>/dev/null; then git show "$r:$p" | sha256sum | cut -c1-12; else echo ABSENT; fi; done; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show a6ec781 --stat --format='%h %s' && echo '=== GATE DIFF ===' && git show a6ec781 -- tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py tools/souji-seat-audit.py | sed -n '1,200p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== fixture diff cbf688a..HEAD ===' && git diff cbf688a a6ec781 -- tests/fixtures/r15-census-config.py | sed -n '1,180p' && echo '=== matrix diff ===' && git diff cbf688a a6ec781 -- census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688a 0a70bef -- tools/souji-census.sh | grep -nE '^\+' | grep -E 'Sentinel|Mutate|Critic|Rev|Revenge|Scout|Src|Conn|Sibling|m[0-9]|M[0-9]{2}|F[0-9]|r16|R16' | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== HEAD anchors in census ==' && grep -nE '^(scan_config_file|cfg_soft|guard_config_file_kind|guard_git_config|guard_bound_filters|count_dirty|census_one)\(\)|GIT_NO_LAZY_FETCH=1|core\.hooksPath=/dev/null|core\.fsmonitor=false|^#   repo|^# Exit codes|status-unverifiable|config-unsupported' tools/souji-census.sh | sed -n '1,60p' && echo '== HEAD header 1-30 ==' && sed -n '1,30p' tools/souji-census.sh && echo '== HEAD line count ==' && wc -l tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
for p in ('census/round-16/c1-matrix.json','census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json','census/round-16/live-fleet.json','census/round-16/live-fleet-final.json','census/round-16/seat-audit-w1.json'):
    try:
        d=json.load(open(p))
    except Exception as e:
        print(p,'ERR',e); continue
    keys=[k for k in d if k not in ('arms','cases','seats','runs')]
    print('##',p)
    print(' keys',keys)
    for k in ('lane_head','changed','observed','git_version','bash_version','shellcheck_version','python_version','runner_sha256','invalid_suites','fixtures_dirty','summary','totals'):
        if k in d: print('  ',k,'=',json.dumps(d[k])[:300])
    if 'arms' in d:
        for a,v in d['arms'].items():
            print('   arm',a,{kk:v.get(kk) for kk in ('sha256','bash_n','shellcheck_warning','selftest','r15-config','r14-namespace') if kk in v})
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== expected.json @HEAD ==' && git show HEAD:tests/fixtures/r15-preservation-frozen/expected.json && echo '== record.json head fields ==' && python3 -c "
import json;d=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'));print(json.dumps({k:d[k] for k in ('measured_commit','record_sha256','fixture','tool','verdict') if k in d},indent=1)[:900]);print('keys',list(d))"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff -U0 cbf688a 0a70bef -- tools/souji-census.sh | grep -E '^(@@|\+[^+])' | sed -n '1,220p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
def summ(p):
    d=json.load(open(p)); out={}
    for a,v in d['arms'].items():
        out[a]={k:(v[k].get('total'),v[k].get('failed'),v[k].get('rc')) for k in ('r15-config','r14-namespace') if isinstance(v.get(k),dict)}
        out[a]['selftest']=(v.get('selftest') or {}).get('checks'),(v.get('selftest') or {}).get('failed')
        out[a]['sha']=v.get('sha256','')[:12]
    return d.get('lane_head'),d.get('changed'),out
for p in ('census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json','census/round-16/c1-matrix.json'):
    print('##',p)
    print(summ(p))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== HEAD status_info_file ==' && sed -n '930,985p' tools/souji-census.sh && echo '== cbf688a status_info_file ==' && git show cbf688a:tools/souji-census.sh | sed -n '870,895p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
print('measured_commit',d['measured_commit'])
print('runs keys',list(d.get('runs',{})))
for k,v in d.get('runs',{}).items():
    if isinstance(v,dict):
        print(' run',k,{kk:(vv if not isinstance(vv,(dict,list)) else type(vv).__name__) for kk,vv in v.items()})
print('namespace_controls keys',list(d.get('namespace_controls',{})))
print('declared',d.get('declared_consistency_only'))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== HEAD run-matrix 40-150 ==' && sed -n '40,150p' census/round-16/run-matrix.py && echo '== HEAD T2 worktree_extra_flags ==' && grep -n -A16 'worktree_extra_flags()' tools/souji-census.sh && echo '== HEAD T3 list_repos ==' && grep -n -A20 'list_repos()' tools/souji-census.sh | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== HEAD guard_config_path ==' && sed -n '536,566p' tools/souji-census.sh && echo '== HEAD guard_bound_filters body ==' && sed -n '983,1030p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== gate selftest check() calls ==' && grep -c '^        check(' tools/souji-landing-gate.py && grep -n '^        check(' tools/souji-landing-gate.py | sed -n '1,25p' && echo '== fixture CASE_CLASSES at HEAD ==' && grep -n 'CASE_CLASSES\|HARM_CASES\|EXPECTED_IDS' tests/fixtures/r15-census-config.py | sed -n '1,10p' && echo '== preservation CONFIG classes HEAD ==' && sed -n '323,360p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '== files naming cbf688a ==' && grep -l 'cbf688a' *.md | wc -l && echo '== files naming stale pin literals ==' && grep -lE 'b5187351|6314d45d' *.md | wc -l && echo '== files saying gate/tool absent ==' && grep -lE 'landing-gate\.py[^\n]*(absent|not exist)|absent[^\n]*landing-gate|ENOENT' *.md | wc -l && echo '== RevengeProbeRecurrence audit-tool state ==' && grep -nE 'no tool|tool exists|absent|seat-audit|ledger|transcript audit' RevengeProbeRecurrence.md | head -20 && echo '== RevengeR15Landing pin/checker claims ==' && grep -nE 'pin|frozen|checker|b5187351|6314d45d|re-pin|R4' RevengeR15Landing.md | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo 'w1 md count:' && ls .ufo/waves/round-16/w1/*.md | wc -l && echo 'bash -n census:' && bash -n tools/souji-census.sh; echo "rc=$?" && echo '== cbf688a preservation classes ==' && git show cbf688a:tools/souji-preservation-evidence.py | grep -nE 'CONFIG_(SAFETY|BENIGN)_IDS|R15CFG-18|R15CFG-20' | sed -n '1,30p' && echo '== gate extra selftest names ==' && grep -nE 'uncited-nonparsing-not-flagged|bad-rev-exit2|no-skill-exit2' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n '^STATUS:' RevengeFrozenPin.md RevengeR15Landing.md RevengeProbeRecurrence.md RevBoundFilters.md RevMatrixRunner.md ConnFrontier.md 2>/dev/null | cut -c1-190; echo '== R4-gap carriers ==' && grep -lE 'R4[^|]{0,80}(GAP|open)|still open at (cbf688a|HEAD)|pin.*(stale|unrepaired)' *.md | sort | tr '\n' ' '; echo; echo '== gate-absent carriers ==' && grep -lE 'landing-gate\.py[^\n]{0,80}(absent|not exist|ENOENT)|(absent|not exist|ENOENT)[^\n]{0,80}landing-gate\.py' *.md | sort | tr '\n' ' '
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -nE '^([#*]{0,3} ?)?\*{0,2}STATUS' *.md | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo 'lesson at HEAD?'; git cat-file -e HEAD:corpus/lessons/round-16.md && echo PRESENT || echo ABSENT; echo 'SOURCES at HEAD rows:'; git show HEAD:corpus/SOURCES.md | grep -c '^| S0'; echo 'worktree SOURCES rows:'; grep -c '^| S0' corpus/SOURCES.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree HEAD -- corpus/lessons/round-16.md corpus/SOURCES.md; echo '--- log for those paths ---'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3 -- corpus/lessons/round-16.md corpus/SOURCES.md; echo '--- status ---'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- corpus/lessons/round-16.md corpus/SOURCES.md; echo '--- HEAD SOURCES tail ---'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:corpus/SOURCES.md | tail -2 | cut -c1-120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --format='%h %ad %s' --date=iso 58ace9f..HEAD && echo '=== 163158a stat ===' && git show --stat --format='%h %s' 163158a | tail -n +2 && echo '=== which window paths changed at 163158a ===' && git diff --name-only a6ec781 163158a
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== digests at 163158a for key paths ==' && for p in tools/souji-census.sh tests/fixtures/r15-census-config.py census/round-16/run-matrix.py tools/souji-preservation-evidence.py tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py tools/souji-seat-audit.py census/round-16/c1-matrix-final.json; do printf '%s ' "$p"; git show 163158a:$p | sha256sum | cut -c1-12; done; echo '== lesson STATUS/failure channel refs =='; grep -nE '^## Seat-reported failures|open$|resolved@' corpus/lessons/round-16.md | sed -n '1,30p'; echo '== lesson length =='; wc -l corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '== ConnLogConvention INCOMPLETE ==' && grep -n 'INCOMPLETE' ConnLogConvention.md && echo '== context 375-390 ==' && sed -n '375,390p' ConnLogConvention.md | cat -n && echo '== fences near ==' && awk 'NR>=360 && NR<=392 && /^[[:space:]]*```/{print NR": "$0}' ConnLogConvention.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '== RevR14NamespaceRetention F1 ==' && grep -n -A6 '### F1' RevR14NamespaceRetention.md | head -20 && echo '== RevIncludeResolve headline ==' && grep -nE '^### |^## |F[0-9] ' RevIncludeResolve.md | head -12 && echo '== RevStatusInfoFile F2/F5 ==' && grep -nE '^### F[0-9]|already fixed|live' RevStatusInfoFile.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '== RevStatusInfoFile drift ==' && grep -nE 'worktree|live|in-flight|drift|fixed' RevStatusInfoFile.md | head -20 && echo '== RevHeaderDocs drift ==' && grep -nE 'worktree|live|in-flight|drift|moving' RevHeaderDocs.md | head -12 && echo '== RevengeInertKeys drift ==' && grep -nE 'worktree|live|in-flight|drift|moving' RevengeInertKeys.md | head -12 && echo '== RevBoundFilters drift ==' && grep -nE 'worktree|in-flight|moving|snapshot' RevBoundFilters.md | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== lesson admitted ==' && grep -nE 'admitted|admission' corpus/lessons/round-16.md | head -10; echo '== gate check_carry ==' && sed -n '300,362p' tools/souji-landing-gate.py; echo '== SKILL cited paths at HEAD ==' && grep -oE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' SKILL.md | sort -u
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== census/round-16 at HEAD ==' && git ls-tree -r --name-only HEAD census/round-16/ && echo '== landing-gate-final anywhere? ==' && git ls-tree -r --name-only HEAD | grep -E 'landing-gate-final|gate.*json' ; ls census/round-16/ | grep -i gate; echo rc=$?
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== gate HEAD phrase refs ==' && grep -nE 'PHRASE|do not ship|does not parse|selftest|Case [0-9]+' tools/souji-landing-gate.py | sed -n '1,80p' && echo '== gate HEAD is_failure_line ==' && sed -n '250,290p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'CONFIG_(HARM|REFUSAL|BENIGN|SAFETY|PRESERVE)|HARM_CASES|EXPECTED_IDS|CASE_CLASSES' tools/souji-preservation-evidence.py | sed -n '1,60p' && echo '== fixture heads ==' && grep -nE 'CONFIG_(HARM|REFUSAL|BENIGN|SAFETY|PRESERVE)|HARM_CASES|EXPECTED_IDS|CASE_CLASSES|def case_0' tests/fixtures/r15-preservation-evidence.py | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '80,120p' .ufo/waves/round-16/w1/ConnLogConvention.md && echo '=== 150-175 ===' && sed -n '150,175p' .ufo/waves/round-16/w1/ConnLogConvention.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== fixture case count HEAD ==' && grep -c 'CASE\\t' tests/fixtures/r16-landing-gate.py; grep -nE 'def main|CASE\b|marker-rewordings' tests/fixtures/r16-landing-gate.py | head -20; echo '== LandingGateFixture line refs ==' && grep -nE 'marker-rewordings|15 cases|SUMMARY|marker-one-char|phrase' .ufo/waves/round-16/w1/LandingGateFixture.md | head -20; echo '== LandingGate design phrase lines ==' && grep -nE 'phrase|pinned phrase|do not ship|18/18|findings=34|checked_markers' .ufo/waves/round-16/w1/LandingGate.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== T2 remainder HEAD ==' && sed -n '1143,1180p' tools/souji-census.sh && echo '== ALLOWED-EXEC in w1 spec/dispatch ==' && grep -c 'ALLOWED-EXEC' .ufo/waves/round-16/w1-spec.json .ufo/waves/round-16/w1-dispatch.json ; grep -n 'ALLOWED-EXEC' .ufo/waves/round-16/w1-spec.json | cut -c1-180
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== protected_fail ==' && grep -n -A10 'protected_fail()' tools/souji-census.sh && echo '== gate selftest case count HEAD ==' && sed -n '748,770p' tools/souji-landing-gate.py && grep -c '^        case(' tools/souji-landing-gate.py; echo '== fixture case() calls HEAD ==' && grep -c '^        case(' tests/fixtures/r16-landing-gate.py; grep -n '^        case(' tests/fixtures/r16-landing-gate.py | sed -n '1,25p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== lesson 39-62 ==' && sed -n '39,62p' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== gate fixture case 9 HEAD ==' && sed -n '390,420p' tests/fixtures/r16-landing-gate.py && echo '== gate selftest marker cases ==' && grep -nE 'marker|fence|STATUS|does not|phrase' tools/souji-landing-gate.py | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== status_info_file callers ==' && grep -n 'status_info_file' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '552,564p' tools/souji-census.sh | nl -ba -v552 && echo '--- worktree print ---' && sed -n '1150,1162p' tools/souji-census.sh | nl -ba -v1150
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -nE 'STATUS[*[:space:]]*[:—][[:space:]*]*(incomplete|fail|failed|fails|failing|failure|blocked|broken|partial|harmed|red|unrun|error|regression|known)\b' *.md | cut -c1-160
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w2/RevengeR16Timeline.md && grep -n '11 are\|STATUS: ok\|## Commands\|## 6\.' .ufo/waves/round-16/w2/RevengeR16Timeline.md && git status --porcelain | grep -v 'operator-sweep' | head -20
```

Non-shell reads (exact named files): `LandingGate.md`, `LandingGateFixture.md`,
`CriticGateVacuity.md`, `RevengeFrozenPin.md`, `RevMatrixRunner.md`,
`DraftSkillSection.md`, `corpus/lessons/round-16.md`, `CriticGateVacuity.md:36-50:raw`,
`ConnLogConvention.md:380,390:raw`, `tools/souji-landing-gate.py:60,70-80`,
`census/round-16/c1-matrix.json?q=…`, plus `grep` on `w1/*.md` (non-recursive),
`RevFixtureR16Edits.md`, `CriticFixtureOverfit.md`, `RevGateSpec.md`,
`DraftR15Correction.md`, and the named `tools/souji-census.sh` ranges.
