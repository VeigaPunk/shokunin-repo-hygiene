STATUS: DONE — every tagged `open (r17…)` in round-16.md:41-109 is mapped to a named r17 wave-1 item, an r18 route with a reason, or a why-not; 5 fixed-by-item, 2 split/partial, 14 routed, plus the header channel open and 5 untagged opens in the same section; one bounded move proposed that closes the dangling-measured open inside r17.

# ConnOpenResiduals — r16 open dispositions → r17

Scope: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-16.md:41-109`, mined against the round-17 wave-1 dispatch `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-17/w1-spec.json` (80 items, `reportDir` `.ufo/waves/round-17/w1`) and the r17 context (C1 operability, C2 calibration, C3 coverage, routed D3/D5/D6/D7).

Disposition vocabulary. **FIXED-BY** = a wave-1 item's `OWN ONLY`/instructions name the defect and a runnable check; it is a disposition, not a claim that the item passed. **SPLIT** = the row contains two defects with different fates. **ROUTED-R18** = no wave-1 item owns the file or the check; the reason is named. **WHY-NOT** = deliberately not done, with the reason. **PARTIAL** = one clause owned, one not.

Line inventory method: `grep -n "open (r17" corpus/lessons/round-16.md` returned exactly 21 lines: 59, 60, 62, 63, 67, 68, 69, 70, 71, 73, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86. Line 43 (the wave-1 header) carries the section's only other r17-tagged open but not the literal parenthetical; it is row H1.

## Table A — the 21 tagged opens (paste into the r17 carry section)

| # | r16 line | seat row | open clause | r17 disposition | named wave-1 item(s) | verification / why |
|---|---|---|---|---|---|---|
| A1 | :59 | `CriticC1NoHarm2.md:26` | "The contractions themselves stay open (r17; L0 question)" — A1 hook symlink and `info/attributes` | **SPLIT** | `info/attributes` → **CensusD1D2** + **FixtureR17Census** (D2 cases) + **MatrixR17**; A1 hook symlink → **RevL0Status** evidence only | D2's declared shape keeps *every other* `guard_git_files` entry at whole-run exit 2 (context C1-D2), so A1 is not fixable inside C1. Check: `run-matrix.py --changed WORKTREE` → R17 D2 hardlink/FIFO/symlink-to-FIFO rows exit 0 with a/b/c neighbours unchanged, control hardlinked `config` still exit 2. |
| A2 | :60 | `CriticFixtureRound2.md:109` | size-preserving bound-filter controls so R15CFG-14 can fail | **ROUTED-R18** | none | No `OWN ONLY` covers `tests/fixtures/r15-census-config.py`; the C1 counting command runs it unchanged and **MatrixR17** binds a per-arm fixture sha256, so changing its oracle mid-round decouples r17's record from the r16 comparison. Fix shape: size-preserving control bytes plus a three-arm re-run. |
| A3 | :62 | `CriticR4Laundering.md:75` | fixture `CASE_CLASSES` disagreement with the checker on 18/19/20 | **ROUTED-R18** | none; **RegenerateVerdict** is explicitly barred from `expected.json` | The open is *which side is right* (fixture classes or checker), an oracle re-derivation, not an edit; no wave-1 item owns `tests/fixtures/r15-preservation-frozen/expected.json`. |
| A4 | :63 | `CriticSeparability2.md:193` | dangling `measured_commit` passes the gate | **ROUTED-R18 unless the move in §Move is adopted** | `GateExactIds` owns the file but its instructions stop at lines 75-80 | Measured: `5fa6017:tools/souji-landing-gate.py:457-477` verifies the rev and then silently skips all measured checks when it does not resolve (`if measured_ok:` with no `else`). One live instance at HEAD: `tests/fixtures/r14-cache-frozen` (`0123456789abcdef…`, dangling). |
| A5 | :67 | `MutateGateCarry.md:3` | detector cases for the 7 carry-channel survivors | **ROUTED-R18** | none | No item names the survivors. GateExactIds' new cases may kill some incidentally; booking that as coverage would be unfounded without a mutant replay. |
| A6 | :68 | `MutateGateFrozen.md:2` | detector cases for the 7 frozen-channel survivors | **ROUTED-R18** | none | Same. |
| A7 | :69 | `MutateGateParse.md:3` | detector cases for the 5 parse survivors | **ROUTED-R18** | none | Same. |
| A8 | :70 | `MutateSeatAudit.md:3` | selftest cases for the 7 auditor survivors | **FIXED-BY** | **SeatAuditPrecision** | Its `OWN ONLY` says: extend `--selftest` with "cases for the 7 survivors in `.ufo/waves/round-16/w2/MutateSeatAudit.md`". Check: `souji-seat-audit.py --selftest` count grows; the 7 cases asserted. |
| A9 | :71 | `ReopenS044.md:65` | repo-local `status.showUntrackedFiles` census gap | **FIXED-BY** | **CensusD1D2** + **FixtureR17Census** (local, `include.path`, `extensions.worktreeConfig`+`config.worktree`; `=no` and `=all`; ignored-only control) + **MatrixR17**; evidence items `ScoutStatusCallSites`, `ScoutFleetUntrackedCfg`, `RevD1Static`, `RevengeCountDirtyHistory` | Check: R17-01.. D1 rows dirty on changed, every D1 repair case fails at `5fa6017`, `=all` keeps the one collapsed directory line. |
| A10 | :73 | `ReopenS048.md:102` | narrow the rejected row's scope and anchor cells | **ROUTED-R18** | `RevD5Carry` drafts only the *lesson* carry line; `ScribeSourcesRows` is report-only rules | No wave-1 item owns `corpus/SOURCES.md` (scan of all 80 `OWN ONLY` clauses). Fix is two cell edits in row S048 (`corpus/SOURCES.md:62`), verdict stays REJECTED. |
| A11 | :75 | `RerunGateReplayR14.md:176` | SUMMARY branch counts | **FIXED-BY** | **GateExactIds** clause (3) | Check: SUMMARY reports measured-pin runs, STATUS lines scanned, carry-heading found; r14 replay still 0 findings. |
| A12 | :76 | `RerunGateSelftest.md:182` | fence/table cases, a clean measured check, bold-only carry | **FIXED-BY** | **GateExactIds** clause (2) | Check: `souji-landing-gate.py --selftest` with exact id sets and the three new shapes. |
| A13 | :77 | `RerunLegacySelftest.md:9` | mode-stripped invocation (F1) and host-independence wording (F3) | **ROUTED-R18** | none | No `OWN ONLY`; it changes the fixture's documented invocation contract and a SKILL/lesson claim ("host-independent"), not census code; system gitattributes/init templates/toolchain floors need a separate measurement. |
| A14 | :79 | `RevCensusStatusFinal.md:359` | F1-F4 and the relative `gitdir` base | **ROUTED-R18** | none; C1 is declared D1/D2-only | F1 = newline worktree paths; F2 = relative `XDG_CONFIG_HOME`/empty `HOME`; F3 = `wt-dirty` meaning; F4 = `--include-root` on a gitfile root; plus the relative-`gitdir` guard base (report §Residual risk). Needs new census code and fixture cases. |
| A15 | :80 | `RevGateSnapshot.md:109` | exit-2 totality S1/S2, ambient `GIT_DIR` S3 | **FIXED-BY** | **GateExactIds** clause (4) | Check: failed git read → exit 2; falsy `files` → exit 2; revision lookups with `GIT_DIR`/`GIT_WORK_TREE` unset. |
| A16 | :81 | `RevMatrixRunnerFinal.md:248` | rc/SUMMARY tie, `fixtures_dirty` gate, id-set row, `c1-matrix.json` schema | **FIXED-BY 3/4 + WHY-NOT** | **MatrixR17** for the first three | `c1-matrix.json` is the committed r16 record; rewriting it would falsify the r16 landing evidence. The r17 record documents its own schema and supersedes it — add a one-line "superseded" note if wanted; do not edit the r16 bytes. |
| A17 | :82 | `RevengeSeatViolations.md:260` | SOURCES 2.55.0 cells | **ROUTED-R18** | `ScribeSourcesRows` (registry rules only) | Rows whose anchor/version cells name 2.55.0 — S001–S010, S031–S033, S035, S037, S042, S047 (`corpus/SOURCES.md:15-24,45-47,49,51,56,61`) — while the host is git 2.56.0; the r16 freshness note already discloses it. Closing needs a 2.56.0 re-verification sweep per row. |
| A18 | :83 | `ScoutLsFilesPathspec.md:179` | nested-layout pathspec excludes (F2) | **ROUTED-R18** | none | Census code plus fixture change; both consumers; unowned. |
| A19 | :84 | `ScoutOptionalPrefix.md:238` | stop stripping `:(optional)` for `core.worktree` | **ROUTED-R18** | none | One-line census change, but outside C1's declared D1/D2 scope. Cheapest fold if L1 widens C1; otherwise r18 with a fixture case. |
| A20 | :85 | `ScoutXdgEmpty.md:112` | measure F3-F5 | **ROUTED-R18** | none | **FixtureR17Census** isolates `XDG`/`HOME` but does not measure relative `XDG_CONFIG_HOME` or empty `HOME`; F3/F4 are fail-closed divergences, F5 is unmeasured. |
| A21 | :86 | `SentinelGateSafety.md:131` | F1, F2, F4, F5, F6 | **ROUTED-R18** | `SentinelFifoHostile` probes C1-D2 (census FIFO), not the gate | Gate hardening: unbounded resource use on hostile blobs, crash exit 1 instead of 2, a symlinked registry script that parses, changed paths lost to quoting/spaces/renames. r16's C2 scope disclosed the gate as not robust to hostile content; r17's D6 covers evidence pinning only, and no r17 item owns hostile-content robustness. |
| H1 | :43 | section header | 9 non-vocabulary wave-1 lines uncarried; "widen the channel or carry by reading" | **PARTIAL** | count → **ScoutGateUncarriedCount** + **ScribeLogCorrections** (D3, 28→29); format → **RevD5Carry** (D5) | No item reads the 9 lines; **GateExactIds**' fence/table cases *narrow* what counts as a STATUS line, they do not widen the channel. The chosen arm is carry-by-reading, which must be done by L1 at landing; channel widening → R18. |

## Table B — the five untagged opens in the same section

The section also contains `open:` rows without the r17 parenthetical; mapping them keeps the carry section complete.

| r16 line | seat row | open | disposition | reason |
|---|---|---|---|---|
| :44 | `CriticNoHarmPreharm.md:14` | "residual contraction … needs operator scope adjudication" | **ROUTED (operator L0)** | `RevL0Status` reads `.ufo/l0-questions.md` and reports whether an answer exists; no lane fix is legitimate before the ruling. |
| :46 | `MutateScanConfig.md:2` | m2 (cycle check removed) is an equivalent mutant behind the depth cap | **WHY-NOT** | Reason-only difference: the mutant cannot be distinguished by behaviour; close by recording the reason, not by a detector case. |
| :50 | `RevengeInertKeys.md:245` | fixture docstring still carries pre-r16 refusal bullets | **ROUTED-R18** | Unowned (`tests/fixtures/r15-census-config.py` again); the r16 revisions paragraph supersedes the bullets but the bullets are stale text. Fold into A2's fixture packet. |
| :52 | `SrcBashSetN.md:129` | live gnu.org unreachable; S043 rests on Wayback + installed manual | **ROUTED-R18** | A re-open on a reachable host is a source-freshness action (365d/on-release), not a wave-1 edit; `ScribeSourcesRows` supplies the recheck column rules. |
| :66 | `DraftTrendVerdicts.md:102` | trend verdicts were author drafts pending the non-author closure | **CLOSED-BY-R16-CLOSURE** | `round-16-verifier-spotcheck.md` §Trend verdicts issues the non-author expansion/quality/discernment verdicts; no r17 action. |

## Residual surfaces from :105-109 not already in Tables A/B

`:105-107` (L0 contractions vs `a31642d`): whole-run guards (including A1), unread global/system config, `--ignore-submodules=all`, repo-local bound-filter `status-unverifiable`, `~user`/`%(prefix)` degrade — **operator L0**, no r17 fix; `info/attributes` is the one carve-out (row A1, C1-D2).

`:109` (routed to round 17), by disposition:

- **FIXED-BY** — `status.showUntrackedFiles=no` false clean (A9); gate S1/S2/S3 (A15); matrix rc/SUMMARY + `fixtures_dirty` + id-set row (A16); seat-audit 7 mutants (A8).
- **PARTIAL** — "hardlinked metadata aborts the fleet (S5)": D2 degrades only `info/attributes`; the rest is the declared whole-run design under L0.
- **ROUTED-R18 (unowned census surface)** — `core.worktree` `:(optional)`; nested-layout pathspec excludes; `scan_config_file` second-`git config` producer status (S1); `..`-after-symlink lexical collapse (S2); `emit_compare` deltas against `error` rows (S6); newline worktree paths, relative `XDG_CONFIG_HOME`/empty `HOME`, `wt-dirty` meaning, `--include-root` gitfile rows, relative `gitdir` base; the r15-config fixture packet (case 03 no-git-command claim, rc-3 witness, unbuilt hardlink/include-depth/`%(prefix)` worlds, `HARM_CASES` missing 19, stale docstring bullets, unguarded `f[6]`, store-unscoped `EACCES`, passwd-derived home).
- **ROUTED-R18 (gate hardening)** — hostile-blob resource exhaustion, crash exit 1 not 2, symlinked registry script, quoting/space/rename path loss; gate mutant survivors 5/7/7.
- **ROUTED-R18 (source freshness)** — knowledge entries and the rows naming 2.55.0 (S001–S010, S031–S033, S035, S037, S042, S047).
- **MOVE CANDIDATE** — dangling `measured_commit` (§Move), otherwise R18.

Counts: Table A 21 rows = 5 FIXED-BY, 2 SPLIT/PARTIAL, 14 ROUTED-R18. Table B 5 rows = 1 closed by the r16 closure, 1 why-not, 3 routed. Header H1 partial. `:109` adds no tagged row; it is the same open set in prose.

## Move — one bounded proposal

**Observation (non-obvious).** The gate's own clean-pass selftest world is built on the defect it should detect: `5fa6017:tools/souji-landing-gate.py:725` writes `record = {"measured_commit": "0" * 40}` — a commit that cannot exist — and `:783-784` asserts that world exits 0. The measured cross-check at `:457-477` silently skips when the rev does not resolve. **GateExactIds is about to pin per-case exact finding-id sets** (`:770` today is membership only). If it does so without this move, r17 lands a selftest that *asserts* a clean pass over a record whose measured revision does not exist.

**Evidence that a blanket fix is not free.** Enumerating every `tests/fixtures/*-frozen/expected.json` at `5fa6017`:

| frozen dir | `record` key | `measured_commit` | resolves |
|---|---|---|---|
| `tests/fixtures/r13-cert-frozen` | none | — | not checked (no record key) |
| `tests/fixtures/r14-cache-frozen` | `record.json` | `0123456789abcdef0123456789abcdef01234567` | **dangling** |
| `tests/fixtures/r15-preservation-frozen` | `record.json` | `c6207bd…` | commit |

`r14-cache-frozen/expected.json` sha256-pins `record.json` in its own `files` map (no `record_sha256` key), so its bytes cannot be repaired without editing a pinned historical record. The exception path is present at every replay revision that carries the frozen fixture — `cc21683`, `6ff91f5`, `79bbe7a` (verified with `git cat-file -e`) — so it is exactly what keeps those replays at 0, 0 and 29 findings. The other replays are unaffected: the r15 fixture is **absent** at `a31642d` (r13) and `cc21683` (r14); at `b410186` (r15) its `measured_commit` `fc3a8d4` resolves; at `5fa6017`/`6ff91f5` it resolves to `c6207bd`.

**Proposed move (one file, same owner).** In GateExactIds' edit of `tools/souji-landing-gate.py`:

1. Replace the silent skip with a finding: when a frozen dir has a `record` whose `measured_commit` is a 4-64 hex string and that rev does not resolve via `git rev-parse --verify <m>^{commit}`, emit the **existing** id `LG-FROZEN-MEASURED` with detail `measured_commit <m> does not resolve` — no new finding id, so the pinned id vocabulary and every replay id set stay stable. Out of scope here: a files-only frozen dir with no `record` key (r13-cert-frozen), and a record with no `measured_commit` key; those keep today's behaviour.
2. Carry exactly one explicit exception, keyed by the exact path `tests/fixtures/r14-cache-frozen/expected.json`, with the reason "r14 placeholder measured_commit; record is sha256-pinned by its own files map; measured dimension is not asserted". Assert in the selftest that the exception table has exactly one entry and that each entry has a non-empty reason, so a second exception is a visible edit rather than a silent allowlist.
3. Rebuild the clean-pass world so `measured_commit` is the base commit (commit 1 holds the pinned files, commit 2 holds `record.json`/`expected.json`; `record_sha256` recomputed), and add exact-id cases: real measured → exit 0; a bogus 40-hex rev outside the exception → exit 1 with exactly `{LG-FROZEN-MEASURED}`; the r14 exception path → exit 0.

**Affected axes.** Calibration **improves**: the r16 `:63` open closes inside r17, and the gate stops passing an unverifiable measured claim while its selftest stops pinning that pass. Operability, coverage, depth, freshness and adjacency are untouched (no census, source or knowledge change; no claim wording changes).

**Risks.** (a) Mid-flight scope addition to a running executor — mitigate by L1 applying the clause now or making the three edits at integration; the gate change must land with its selftest cases, not alone. (b) A loosely keyed exception is an evasion channel — key it by exact path and require the reason string. (c) Skipping the clean-pass rebuild makes the new rule fail the existing selftest (the defect is load-bearing); that rebuild is the whole cost. (d) A future record that legitimately uses a placeholder must declare an exception or fail — intended, and the detail names the rev. (e) Do not "fix" `b410186`'s two `LG-FROZEN-MEASURED` findings: its measured rev resolves and the findings are byte mismatches, a different class.

**Verification (all runnable).**
- `python3 tools/souji-landing-gate.py --selftest` → exact-id cases green, including the three new ones; the clean-pass measured rev now resolves.
- `python3 census/round-17/gate-replays.py --gate-rev WORKTREE` (GateReplayFrozen) → the five sets identical to `gate-replays-expected.json`: `b410186/15` same 5 ids, `a31642d/13` 0, `cc21683/14` 0, `6ff91f5/16` 0, `79bbe7a/16` 29 `LG-SEAT-UNCARRIED`.
- Negative control on a scratch copy under `/var/tmp`: a record with `measured_commit` `deadbeef…` outside the exception → exit 1, exactly `{LG-FROZEN-MEASURED}`.
- Round-end gate run on the lane worktree → 0 findings (the r14 exception covers the only dangling record at HEAD).

## Commands run (exact, condensed outputs)

```text
grep -n "open (r17" corpus/lessons/round-16.md
  -> 21 lines: 59 60 62 63 67 68 69 70 71 73 75 76 77 79 80 81 82 83 84 85 86
grep -n "^## \|Open defects found\|open (r17\|- \`RevengeInertKeys\|- \`SrcBashSetN\|- \`CriticNoHarmPreharm\|- \`MutateScanConfig\|- \`DraftTrendVerdicts" corpus/lessons/round-16.md
  -> :5 Mistakes, :16 Gate, :39 Seat-reported failures, :43 header, :44/:46/:50/:52/:66 untagged opens,
     :95 Corrections, :99 Process, :105 Residuals (open), :109 routed-to-r17 paragraph
python3 (json) over .ufo/waves/round-17/w1-spec.json: 80 items; keyword ownership scan
  measured_commit -> ScoutHeadPinConsumers (read-only scout)
  CASE_CLASSES -> NONE; MutateGate -> NONE; SentinelGateSafety -> NONE; 2.55.0 -> NONE
  f.bin -> NONE; R15CFG-14 -> NONE; mode-stripped -> NONE; host-independent -> NONE
  pathspec -> NONE; :(optional) -> NONE; ScoutLsFilesPathspec -> NONE; ScoutXdgEmpty -> NONE
  RevCensusStatusFinal -> NONE; scan_config_file -> NONE; emit_compare -> NONE; wt-dirty -> NONE
  include-root -> NONE; newline-containing -> NONE; relative gitdir -> NONE
  ReopenS048 -> RevD5Carry (lesson carry only); ScoutOptionalPrefix -> RevD5Carry (quote check only)
  non-vocabulary -> RevD5Carry (RevGateSpec line only); "widen the channel"/"carry by reading" -> NONE
python3 (json): OWN ONLY clause of all 80 items
  -> tests/fixtures/r15-census-config.py, tests/fixtures/r15-preservation-frozen/expected.json,
     corpus/SOURCES.md, census/round-16/c1-matrix.json are owned by NO item
read w1-spec.json?q=.items[]|select(.name=="…")|.prompt for CensusD1D2, FixtureR17Census, MatrixR17,
  SeatAuditPrecision, TranscriptBundle, GateExactIds, GateReplayFrozen, RegenerateVerdict, RevD5Carry,
  ScribeSourcesRows, RevSeatAuditW1Recall, CriticHonestyWhyNot, ConnClaimSeparability
  -> ownership clauses and verification commands quoted in Tables A/B and §Move
git show 5fa6017:tools/souji-landing-gate.py | sed -n '380,505p'
  -> :457 measured cross-check; :464-476 rev-parse --verify, measured_ok bool; :477 if measured_ok:
     (no else -> silent skip); :391 files = expected.get("files") or {}
git show 5fa6017:tools/souji-landing-gate.py | sed -n '745,800p'
  -> :770 ok = exit == expect_exit and all(i in ids for i in expect_ids)   (membership, not exact set)
git show 5fa6017:tools/souji-landing-gate.py | grep -n "measured_commit\|cat-file\|def _resolve\|files"
  -> :725 record = {"measured_commit": "0" * 40}; :96-102 ids LG-PARSE-REG .. LG-OPEN-ADMITTED
git cat-file -t for fc3a8d4 c6207bd b5187351 6ff91f5
  -> commit / commit / fatal: Not a valid object name b5187351 / commit
for r in 6ff91f5 79bbe7a cc21683: tests/fixtures/r14-cache-frozen/expected.json
  -> present / present / present   (exception path is load-bearing for all three replays)
for r in a31642d cc21683 b410186 5fa6017: tests/fixtures/r15-preservation-frozen/expected.json
  -> absent / absent / present / present
for each *-frozen/expected.json at 5fa6017: record key + measured_commit + rev-parse
  -> r13-cert-frozen rec=None; r14-cache-frozen 0123… DANGLING; r15-preservation-frozen c6207bd commit
git show 5fa6017:tests/fixtures/r14-cache-frozen/record.json
  -> {"dependencies": {...}, "matched": true, "measured_commit": "0123…", "name": "r14-cache-frozen"}
git show 5fa6017:tests/fixtures/r14-cache-frozen/expected.json (json keys)
  -> ['files', 'record', 'verdict']; record_sha256 absent; files = dependency.txt, record.json
sed -n '300,380p' .ufo/waves/round-16/w2/RevCensusStatusFinal.md
  -> F1 newline worktree path truncation; F2 relative XDG/empty HOME; F3 wt-dirty meaning;
     F4 --include-root gitfile row; + relative-gitdir guard base (adjacent defect)
grep -n "2\.55\.0\|2\.56\.0" corpus/SOURCES.md
  -> S001-S010 (:15-24), S031-S033 (:45-47), S035 (:49), S037 (:51), S042 (:56), S047 (:61);
     S048 row at :62; S043-S050 provenance at :9
```

Probe compliance: exact named files only; shell `grep`/`sed` used only on those files (no `-r`, no `find`); the only recursive listing is `git ls-tree -r` on the named lane repo, which the probe rule allows; no `jj`; no git write; no lane tool (census, verify, vault-verify, quarantine) executed; no credential file read; no operator-sweep directory opened. Tool installs/updates: none.
