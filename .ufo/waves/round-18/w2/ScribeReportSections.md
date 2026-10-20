STATUS: DONE — drafted the five round-18 report sections from committed records at 5efb519; four record-level calibration defects found (one unrecorded tip gate result, one SOURCES hash from before the round, one overstated SCORECARD "identical" claim, one non-discriminating leftover field); none fixed (lane files are read-only to this seat).

# Round 18 — Wave 2 scribe report (ScribeReportSections)

Scope: lane `souji-shokunin`, tip `5efb519f00075d958c3d1109ef6fcb24c487eb87`, baseline `b576341`. Judged on calibration: does each committed claim match the committed evidence. Sources: `corpus/lessons/round-18.md`, `SCORECARD.md`, `LOG.md` (round-18 entry, line 951), `census/round-18/*`, `corpus/SOURCES.md` (S064–S071), `SHONEN.md`, `.ufo/waves/round-18/w1/*` (committed at 3f822e8). Nothing was run against the live fleet; no lane file was edited; no git write, no `jj`.

Axes (SCORECARD lines 13–15, author-set, outside admission pending): calibration 7, operability 8, coverage 8.

## 1. Attacked claims and verdicts

| claim (where stated) | verdict | one-line reason |
|---|---|---|
| C1 operability: changed census passes r18-bounded 8/8 and keeps r17-hygiene, r15-config, r14-namespace at 0 failures | **holds** on the committed record (with caveats F4, F5, F7) | `c1-matrix-worktree.json` arms verified (§3) |
| C1 operability: "no lane fixture leaves a blocked process behind" (SCORECARD l.15: r15 2→0, r17 4→0) | **partial** | the 2→0 and 4→0 figures are in the wave-1 reap reports, not in the committed matrix record; the matrix's own leftover field is a host snapshot (F4); R17 figure is from a modified test copy (F5) |
| C2 calibration: 10 findings at b576341 round 18 → **0 at round tip** (lesson l.7; SCORECARD l.14) | **partial** | the b576341 half is verified; the tip half has **no committed record** (F1) |
| C2: gate selftest 33→53, pointer fixture 11/0, quarantine selftest 101→105 | **unverified in committed records** | no committed output file for these; not refuted |
| C2: pinned r17 replays all `match: True` with the changed gate | **holds** | `gate-replays-r18.json`; gate sha256 `f8a2ebe7…` equals tip (verified) |
| C3 coverage: 65 rows = blind counter 65, symmetric difference 0; 3 residue classes | **holds** | `proc-census-live-1721.tsv` (65 rows, boot_id line) vs `leak-count-live-1721.json` (total 65); pid sets reconciled by the lesson |
| C3: "blocked forever" (R18-M2) | **overstated wording** | states are `S` with wchans `do_wait` (26), `wait_for_partner` (26), `anon_pipe_read` (6) for the 58 cwd-deleted rows — blocked, but "forever" is unmeasured |
| R1 quarantine owner (J13 b576341 FAIL → PASS) | **holds** | `jj-receipts-r18-changed.txt` `SUMMARY total=35 failed=0 skipped=2` (verified); baseline record not re-read by this seat |
| Live fleet "identical on 21 repositories" (SCORECARD l.15) | **overstated** (F3) | the lesson's own wording is accurate; the SCORECARD is not |
| SOURCES validation "souji ok; SOURCES sha256 `25c91f68…`" (lesson l.43) | **stale** (F2) | `25c91f68…` is the pre-round file; committed SOURCES at 5efb519 is `ed82dafc…` |

## 2. Findings (calibration defects in committed records)

Each finding gives the evidence, the exact check, and the smallest fix. None were fixed here.

**F1 — The tip result for C2 is not recorded (highest severity).**
- Claim: lesson l.7 "After: the same command at the round tip — see Gate"; SCORECARD l.14 "after: 0 at the round tip (Gate in corpus/lessons/round-18.md)".
- Evidence: the lesson's Gate section (l.22–45) contains no tip run. `git grep` for `round tip|tip.*findings` over `census/round-18`, the lesson and LOG.md returns only lesson l.7. `census/round-18/` has one gate record, `gate-pointers-before-b576341.json`, and no tip counterpart.
- Verdict: **unverified in committed records**. The "0" may be true; nothing committed shows it.
- Smallest fix: run the same gate command at `5efb519` and commit the JSON as `census/round-18/gate-pointers-at-5efb519.json`, or withdraw the "0" from the lesson and SCORECARD.

**F2 — The SOURCES validation hash predates the round's registry.**
- Claim: lesson l.43 "SOURCES sha256 `25c91f68…`", "end recorded in the report" (no end sha is recorded anywhere committed).
- Evidence (`git show <rev>:corpus/SOURCES.md | sha256sum`): b576341 `25c91f68e22aa36f`; 3f822e8 `25c91f68e22aa36f`; 42d9ff3, 2fc5f33, 5efb519 all `ed82dafcb023190a`. The S064–S071 rows landed at 42d9ff3. So the "souji ok" run validated the file without the round's rows.
- Verdict: **stale**. The validation cannot be cited as covering S064–S071.
- Smallest fix: rerun `scripts/sources-census.sh validate` against 5efb519, record start and end sha256 in the lesson.

**F3 — "Identical" overstates the live-fleet pair.**
- Claim: SCORECARD l.15 "live fleet pair identical on 21 repositories".
- Evidence (`cmp`/`diff` of the four TSVs in `census/round-18/live-fleet-pairs/`): pair 1 differs only at line 21 (tameshi-shokunin mtime `17:29:36` vs `17:29:48`). Pair 2 differs at line 16 (mado-shokunin `dirty` 10 → 13, mtime `17:29:30` vs `17:29:56`) and line 21 (tameshi mtime). Both pairs: `verdict_flags` identical on all 21 rows.
- The lesson (l.6) says "pair 1 base vs changed rows identical excluding mtime; pair 2 differs only in mado dirty 10 → 13" — the second half omits the tameshi mtime difference in pair 2.
- Verdict: SCORECARD **overstated**; lesson **nearly accurate** (add the pair-2 mtime).
- Smallest fix: SCORECARD l.15 → "verdict flags identical on 21 of 21 rows in both pairs; mtime and, in pair 2, mado dirty count differ (a lane wrote during the run)."

**F4 — The matrix's leftover field is a host snapshot, so it cannot show per-fixture cleanup.**
- Evidence (`census/round-18/c1-matrix-worktree.json`, `arms.*.r15-config.leftover_procs_count` and `r17-hygiene`): all four arms (changed, pre-harm, r14-harm, r17-base) report `leftover_procs_count` 44 (r15-config) and 14 (r17-hygiene), with the **same pid sets** in each arm. Those pids have start times from 14:22 onward, before the matrix ran (~17:29 -03). `session_cleanup.killed` is `[]` in every arm.
- So the field counts pre-existing host residue. It does not show that the changed arm leaves 0 processes. The lesson's "Session cleanup killed 0 processes in every suite" is the accurate per-suite field.
- Verdict: the record **does not support** a per-fixture "no blocked process left behind" reading. Support for that claim lives in the separate reap reports (F5, F6).
- Smallest fix: in the lesson, say explicitly that `leftover_procs_count` is a suite-start/suite-end host count and that the changed arm's 44/14 are pre-existing pids; or record a before/after delta per suite.

**F5 — The R17 "4 → 0" figure has a caveat the SCORECARD and R18-M2 omit.**
- Evidence: `.ufo/waves/round-18/w1/FixtureReapR17.md` lines 20–26 and 56: the base 4-process residue was measured on a **test copy** of the census with the info/attributes guard removed, with job control (`set -m`-style per-repo background jobs) modelled by the seat, and a **10-second** fixture timeout instead of the landed timeout. The report's own Risk section: "the untouched 5fa revision guards this FIFO before `status`, so its direct arm cannot reproduce the leak."
- The lesson's C1 measurement line (l.6) does say "on a guard-removed census copy". SCORECARD l.15 ("r17 4 → 0") and R18-M2 (l.16: "r17 forced hang 4 → 0") do not.
- Verdict: **overstated** in SCORECARD and R18-M2; the claim is a demonstration of the session-kill mechanism on a modelled copy, not a measurement on the landed fixture.
- Smallest fix: add "(modelled copy, guard removed, 10 s timeout)" to SCORECARD l.15 and R18-M2.

**F6 — The R15 "2 → 0" is one case on the pre-harm tool.**
- Evidence: `FixtureReapR15.md` l.49–50 (baseline own count 2 for R15CFG-03), l.58/l.87 (fixed run, still red on pre-harm), l.104 (limits: "run as R15CFG-03, not as the full 20-case fixture suite").
- Verdict: **holds for the narrow claim**; SCORECARD l.15 "r15 2 → 0 leftover" should say "one case (R15CFG-03), pre-harm census".
- Also note: the seat killed pids 515827 and 515853 by exact unique scratch path, which it started itself (l.49). Compliant with the probe rule.

**F7 — The C1 r14 column measured bytes that are not landed.**
- Evidence: `c1-matrix-worktree.json` `fixtures_sha256["r14-namespace"]` = `6c1c0cfde846be2f9c56402eddf24de0337350f007998d0c48da3ce9eb6fb5e3`. At tip, `tests/fixtures/r14-census-boundary.py` hashes `e6a984b1daf1f79a…` (16-char prefix; equal to b576341's). Commit 2fc5f33 "r14 fixture back to pinned bytes" confirms the revert. Lesson l.6 discloses the matrix ran the patched copy ("same 12 verdicts").
- Verdict: the lesson discloses it; the SCORECARD l.15 "r14-namespace 12/0 kept" does not. The landed r14 fixture's result is **not in any committed record**.
- Smallest fix: rerun the r14 arm against the tip fixture bytes and commit the result, or label the SCORECARD figure "patched copy".

**F8 — Numbers with no committed record.**
- "leak count after 66; the one new pid is another lane's live omp runner (`/tmp/kr20-scout-…`)" (lesson l.6): `leak-count-live-1721.json` records 65 only. Unverified.
- "the whole live fleet takes about 11 s" (lesson l.26): no timing field in the committed pair TSVs. Unverified.
- "quarantine selftest 101 → 105", "gate selftest 33 → 53 (exact id sets)", "r18-landing-pointers.py 11/0", "r18-proc-census.sh 11/0": no committed output file. Unverified (not refuted).
- Verified in committed records: C1 selftests `pre-harm 36`, `r14-harm 38`, `r17-base 49`, `changed 62` (all `checks`, `failed 0`); r17-hygiene 21/14/0/0; r15-config 8/16/0/0; r14-namespace 10/0/0/0; r18-bounded 6/5/5/0 (B1–B8 verdicts in `arms.*.r18-bounded.cases`).

**F9 — Precision points, no status change.**
- Lesson l.6 places the "B1, B2, B3, B4, B8 hit the 40 s deadline" parenthetical after the **r17-base** arm. Verified: in r17-base, B1, B2, B3, B4, B8 have `observed_exit=124`. In pre-harm, B1, B3, B4 hit 124 and B2, B7, B8 fail on other grounds. The wording is correct only for r17-base; the sentence reads as if it covered all arms.
- Lesson l.45 notation "r15-landing 1/5, r16-precarry 1/29" means exit 1 / 5 findings and exit 1 / 29 findings (verified: `gate-replays-r18.json` `exit` 1, `finding_count` 5 and 29). Write it out.
- SOURCES S064 (row l.82) cites `raw.githubusercontent.com/git/git/v2.56.0/attr.c`; the lesson (l.32) cites `github.com/.../blob/v2.56.0/attr.c`. Same file; align the URL.
- Replay record `lane_head` is `42d9ff3`, not the tip; the gate sha256 is identical at both (verified), so the replay still applies to the tip gate.

**F10 — Source quotes were not re-opened here.** This seat drafted from committed records only (its scope). The S064–S071 quotes and access records (lesson l.30–39) are **unverified by this seat**. Their rows exist in SOURCES (l.82–89).

## 3. Verified checks (exact commands, observed output)

All read-only; every committed file came from `git show 5efb519f00075d958c3d1109ef6fcb24c487eb87:<path>` into `/var/tmp/souji-r18w2-ScribeReportSections/`.

- Gate and tool hashes at tip: `tools/souji-landing-gate.py` `f8a2ebe7695e600959ebfcd060ba99b6558a2f1149cbdcff8ad01a1467f2d27a`; `tools/souji-census.sh` `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; `tools/souji-proc-census.sh` `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc`; `corpus/SOURCES.md` `ed82dafcb023190a860e84e1fd8f55b7bd5e840a41b9029743ff35c0f91b044e`.
- Fixture and runner hashes at tip (16-char prefixes): `r15-census-config.py` `61208dbd53367fa8` (= record); `r17-census-hygiene.py` `716ad2395b74275e` (= record); `r18-census-bounded.py` `2249616641f4a1b9` (= record); `census/round-18/run-matrix.py` `da61f6be8f6f544b` (= record `runner_sha256`); `r14-census-boundary.py` `e6a984b1daf1f79a` (= b576341; ≠ record, F7).
- C1 record provenance: `git_head` and `lane_head` `b5763415…`; `changed_rev` `WORKTREE`; `fixtures_dirty` lists the uncommitted r14/r15/r17 edits and untracked r18 fixture at measurement time; the changed arm's `sha256` equals the tip census (`7e6a92d4…`).
- Per-arm (`jq` on `.arms`): changed 0 failures (r14 12, r15 20, r17 29, r18 8 cases); pre-harm 10/8/21/6; r14-harm 0/16/14/5; r17-base 0/0/0/5.
- Gate record: `checked_ptrs 319`, `ptr_fleet 3`, `findings 10`; the 7 `LG-DANGLING-PTR` citations are `SKILL.md:163,165` and `corpus/README.md:216`, `knowledge/jj-colocation-receipts.md:2,44,126,148` (all `census/round-17/…ddb7347…`), plus `census/operator-sweep-20261019/` and `SKILL.md:110` (`tests/vault/vadv54-run/p/p6repo/.git`), and 1 `LG-FROZEN-MEASURED` (`0123456789ab…` placeholder in `r14-cache-frozen`).
- Live leak snapshot: `proc-census-live-1721.tsv` has 67 lines (boot_id, header, 65 rows); reasons: 58 `cwd-deleted`, 7 `fd-path-gone`; the 58 are 26 `do_wait`, 26 `wait_for_partner`, 6 `anon_pipe_read`; `leak-count-live-1721.json` `total 65`, families `r15-census-config 44`, `r17-census-hygiene 14`, `other 7`.
- Landed files at 5efb519 (from `git show --stat`): `tools/souji-census.sh` 631 lines changed; `tools/souji-landing-gate.py` 651; `tools/souji-proc-census.sh` 495 (new); `tools/souji-quarantine.sh` 67; `tests/fixtures/r18-census-bounded.py` 1271 (new); `r18-landing-pointers.py` 337 (new); `r18-proc-census.sh` 505 (new); `r14`/`r15`/`r17` fixtures modified; `r17-jj-receipts.sh` 93; census/round-18 records; corpus and SKILL/PROVINCE/SCORECARD/LOG rows.
- Wave-1 records at tip: 91 `.md` and 13 `.patch` under `.ufo/waves/round-18/w1/`.

No test, build, lint or formatter was run by this seat (scope forbids it; the main agent should run the checks in §7).

## 4. Draft — Work performed

Round 18 (lane `souji-shokunin`, baseline `b576341`, round-17 closure tip) declared three claims: C1 operability (per-repository bound on the fleet census and session-wide kill in lane fixtures), C2 calibration (landing-gate `LG-DANGLING-PTR` at `--round` ≥ 18 and unresolvable `measured_commit` as `LG-FROZEN-MEASURED`), C3 coverage (`tools/souji-proc-census.sh`, a list-only census of own-uid process residue, F5). It routed R1 quarantine recipe owner, R2 never-committed record names, R3 repository count and R4 Q7 narrowing (Q29). Work ran as one 91-seat wave 1 (build and falsifiers, per the lesson's Process section) followed by lane integration. Wave 1 produced one committed build at `3f822e8`, three documentation and record commits (`42d9ff3`, `2fc5f33`, `5efb519`), and the `.ufo/waves/round-18/w1/` seat records. Six mistakes (R18-M1–M6) are logged with evidence pointers. [Unverified by this seat: the wave-1 seat count and dispatch history, which rest on `w1-dispatch.json` and the lesson's Process section.]

## 5. Draft — Landed changes

- Commit `3f822e8` (build): `tools/souji-census.sh` (per-repository process-group watchdog, `--repo-timeout`, default 600 s, list-phase guards and `census_one`); `tools/souji-landing-gate.py` (`LG-DANGLING-PTR`, `LG-FROZEN-MEASURED`, `--fleet-root`); `tools/souji-proc-census.sh` (new); `tools/souji-quarantine.sh` (recipe owner from `git config lane.id`); `tests/fixtures/r18-census-bounded.py`, `r18-landing-pointers.py`, `r18-proc-census.sh` (new); `r15-census-config.py`, `r17-census-hygiene.py`, `r17-jj-receipts.sh` (session kill and receipt cases); `census/round-18/*` records; `corpus/README.md`, `corpus/knowledge/jj-colocation-receipts.md`, `corpus/pointer-exemptions.tsv` (R2 re-pointing and exemptions); `SKILL.md` (4 lines).
- Commit `42d9ff3` (docs): `corpus/lessons/round-18.md` (75 lines), `LOG.md` (5 lines), `SCORECARD.md`, `SKILL.md` (11 lines), `PROVINCE.md` (F5), `corpus/QUALITY.md` (Q29–Q32), `corpus/README.md` (Round 18), `corpus/SOURCES.md` (S064–S071); also the gate totality fix.
- Commit `2fc5f33`: gate comma line-lists and exemption keyed on record; `tests/fixtures/r14-census-boundary.py` reverted to pinned bytes; `census/round-18/gate-replays-r18.json`; lesson carry quotes.
- Commit `5efb519`: `tests/fixtures/r15-preservation-frozen/{expected.json,record.json}` regenerated at `2fc5f33` (changed census and fixture bytes).
- Not landed: carry-gate wrap truncation (`ScoutCarryWrap.md`, drafted); HEAD-pinned r13/r14 runners; `:(optional)` core.worktree; nested-layout pathspec excludes; `GIT_ATTR_NOSYSTEM` (ScoutGitOpens, open); B3 non-hash `measured_commit` (open).

## 6. Draft — Before → after measurements

| measure | before (b576341 or pre-harm, as recorded) | after (tip, as recorded) | source | status |
|---|---|---|---|---|
| r18-bounded 8 cases | 5 FAIL on r17-base (b576341), B1–B4, B8 rc 124; 6 FAIL pre-harm a31642d; 5 FAIL r14-harm cc21683 | 0 FAIL (changed worktree = tip census bytes) | `c1-matrix-worktree.json` | verified |
| r17-hygiene 29 | 21 / 14 / 0 / 0 (pre-harm / r14-harm / r17-base / changed) | — | same | verified |
| r15-config 20 | 8 / 16 / 0 / 0 | — | same | verified |
| r14-namespace 12 | 10 / 0 / 0 / 0 | fixture bytes not landed (F7) | same | partially verified |
| census selftest checks | 36 / 38 / 49 | 62, failed 0 | same | verified |
| `bash -n` / `shellcheck -S warning` | — | rc 0 all arms | same (`bash_n`, `shellcheck_warning`) | verified |
| C2 gate findings at b576341 round 18 | — | 10 (7 citations, 2 non-files, 1 placeholder) | `gate-pointers-before-b576341.json` | verified |
| C2 gate findings at tip round 18 | 10 | "0" claimed | none committed | **unverified** (F1) |
| pinned r17 replays | — | 5/5 `match: True` | `gate-replays-r18.json` | verified |
| proc census live | blind counter 65 | 65 rows, symmetric diff 0 | `proc-census-live-1721.tsv`, `leak-count-live-1721.json` | verified |
| leak count around the matrix | 65 before | 66 after (lesson only) | none | **unverified** (F8) |
| residue classes governed | 0 (no tool at b576341) | 3 | SCORECARD l.13, lesson l.8 | verified in tool and fixture terms |
| J13 recipe | FAIL (`--as souji`) | PASS (35/0 skipped 2) | `jj-receipts-r18-*.txt` | verified (changed); b576341 record not re-read |
| quarantine selftest | 101 | 105 | none | unverified |
| gate selftest | 33 | 53 | none | unverified |
| R15 forced hang | 2 leftover (1 case) | 0 leftover (1 case) | `FixtureReapR15.md` | verified, narrow (F6) |
| R17 forced hang | 4 leftover (modelled copy) | 0 leftover (modelled copy) | `FixtureReapR17.md` | verified, caveated (F5) |

## 7. Draft — Sources & frontier

Sources opened this round (registry, `corpus/SOURCES.md` l.82–89): S064 git `attr.c` at v2.56.0 (blocking open before any type check); S065 GNU Bash `set -m` (via Wayback capture, live site timed out); S066 `kill(2)` negative pid; S067 Python `subprocess` `start_new_session` and timeout behavior; S068 `proc_pid_stat(5)` starttime and session fields; S069 `proc_pid_exe(5)` deleted suffix; S070 `open(2)` ENXIO for a reader-less FIFO; S071 `git-cat-file -e` and `ls-tree`. S038 rechecked, row unchanged, anchor drift routed to r19. Quotes and access records in the lesson are [unverified by this seat] (F10); the SOURCES registry rows are committed.

Frontier (not claimed as landed):
- F5 process residue: list-only; no knowledge entry; the 58 souji orphans listed, not reaped (operator decision).
- Carry-gate wrap truncation; HEAD-pinned r13/r14 runners; D-state (unkillable) children reported as `repo-timeout-unreaped` but not induced; 10,000-repository scaling of `list_repos` unmeasured.
- Pointer gate: elided tokens and prose without path prefix invisible; fleet paths checked against the fleet working tree, not a revision.

## 8. Draft — Trend verdicts

Author-set, outside admission pending (SCORECARD l.13–15). This seat does not re-score.

- **Calibration (7), C2.** Improved on the b576341 side: the gate now finds the seven stale record citations the r17 closure missed (verified). The tip side is unrecorded (F1), so the "improved to 0" trend is **not established** from committed records.
- **Operability (8), C1.** Improved on the verified matrix (r18-bounded 5 → 0 failures; no regression in the three older suites at tip). "No lane fixture leaves a blocked process behind" is **partially** established (F4–F6).
- **Coverage (8), C3.** Improved on the record: residue classes 0 → 3, live list matches blind counter 65 = 65. Coverage of the residue itself (the 58 orphans) is observed, not reaped.

## 9. Draft — SHONEN for souji round 18

SHONEN.md was last changed at round 13 (`6ed10a7`). The four promotion items are all `[~]`:

- SKILL.md decision tables, error patterns, checklists, sources: unchanged status. Round 18 touched four SKILL rows (3f822e8) and eleven (42d9ff3); no promotion evidence is added.
- End-to-end domain task logged in LOG.md: unchanged. The round-18 LOG entry (line 949–951) is a round record, not a domain task; the existing pointer (LOG.md:362) stands.
- Executable without oral context: unchanged; the round-18 fixtures and runners are runnable from the committed records (verified: paths exist at tip).
- No cross-domain bleed (PROVINCE.md): round 18 added F5 to PROVINCE.md; the boundary entries (RevC3Province) are resolved in the commit (lesson l.53).

Result: **no status change proposed**. [INFERENCE] Promotion would need a domain task logged end-to-end, which round 18 does not supply.

## 10. Smallest-fix list (for the L1 owner; this seat changed nothing)

1. Run the landing gate at `5efb519` and commit the JSON (F1), or remove "0 at tip" from lesson l.7 and SCORECARD l.14.
2. Rerun the SOURCES validation at tip; record start and end sha256 (F2).
3. Reword SCORECARD l.15 "identical" to the lesson's wording (F3).
4. Add to the lesson that `leftover_procs_count` is a host snapshot; record per-suite deltas or rename the field (F4).
5. Add the modelled-copy caveat to SCORECARD l.15 and R18-M2 for R17 (F5); narrow R15 to one case (F6).
6. Rerun the r14 arm against the tip fixture bytes, or label the SCORECARD figure "patched copy" (F7).
7. Commit records for or remove: leak count 66, live-fleet 11 s, quarantine 105, gate 53, pointer 11/0, proc 11/0 (F8).
8. Precision: the 40 s deadline parenthetical belongs to r17-base; write "exit 1 / findings N" in the replay line; align the S064 URL (F9).

## 11. Checks the main agent should run (not run by this seat)

- `python3 tools/souji-landing-gate.py --root <tip clone> --rev 5efb519 --round 18 --fleet-root /home/vgpnk/Projects/shokunin --json <f>` (F1; expected 0 findings if the claim holds).
- `python3 tools/souji-landing-gate.py --selftest` (expect 53/0) and `tests/fixtures/r18-landing-pointers.py` (11/0).
- `bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh` (11/0) and `bash tools/souji-proc-census.sh` vs `census/round-18/leak-count.py` (65 = 65).
- `python3 tests/fixtures/r18-census-bounded.py --census tools/souji-census.sh` (8/0).
- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` at tip (F2).

## Out of scope / cleanup / tools

- No lane file was edited; no git write; no `jj`; no census or gate run against a real directory; no process signalled by this seat.
- Tool installs/updates by this seat: none.
- Scratch: `/var/tmp/souji-r18w2-ScribeReportSections/` holds `git show` copies of committed records; removed after this report was written.
- Probe-rule compliance: only `git show|cat-file|ls-tree|grep|diff|cmp` on named files, `sha256sum`, the `_read` JSON queries on the scratch copies, and `git grep` on named paths.
