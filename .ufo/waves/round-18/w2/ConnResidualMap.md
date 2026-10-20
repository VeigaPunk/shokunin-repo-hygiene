STATUS: DONE — r17 residuals, closure R1–R5, and r18 residuals mapped at 5efb519; R4 and the SCORECARD “identical” sentence fail as claimed, and B3 is closed while the lesson calls it open.

Attacked claim: round 18’s open/closed map. Baseline `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`. Tip `5efb519f00075d958c3d1109ef6fcb24c487eb87` (HEAD). Round commits: `3f822e8` build, `42d9ff3` docs, `2fc5f33` gate/lesson, `5efb519` frozen-record note. `corpus/lessons/round-17.md` and `corpus/lessons/round-17-verifier-spotcheck.md` are byte-identical to the baseline (`git diff --stat` empty). No tool installed. The landing gate and census were not executed (this seat has no ALLOWED-EXEC). Statuses below are from the tree at the tip.

Axes: calibration (judged); completeness of the three inventories; traceability to a commit and a line; no harm to operability or coverage (wording and one checklist cell, no tool behavior change in the proposal).

## Verdict

Partial. R1, the R3 count, the R2 append-and-registry fix, the FIFO-hang half of R5, and every round-18 residual that the lesson still calls open, hold. R4 does not: Q7’s prescription cell is the baseline text, and the lesson calls that “narrowed.” SCORECARD.md:15 calls the r18 live pair identical; the committed TSVs and the lesson’s own sentence disagree. Lesson line 56 calls B3 a silent skip; `check_frozen_pins` has emitted `LG-FROZEN-MEASURED` for that shape since `3f822e8`.

## Closure R1–R5 (`corpus/lessons/round-17-verifier-spotcheck.md:149-153`)

| Item | Tip status | Commit | Evidence |
|---|---|---|---|
| R1 recipe owner | closed | `3f822e8` | `tools/souji-quarantine.sh:246-280` reads `git config --get lane.id`, else a `<id>-shokunin` basename, else `<owning-lane-id>` plus a stderr note. Charset matches the helper (`scripts/hyaku/jj-lane.sh:508`, `516-517`). Init writes that key (`jj-lane.sh:440`). Fixture `tests/fixtures/r17-jj-receipts.sh:751-773` (`J13` wants `kama` and rejects `souji`; `J13-own` the reverse). Selftest `souji-quarantine.sh:1566-1599`. |
| R2 dangling `ddb7347` record names | closed, as the closure wrote it | pointers `3f822e8`; LOG append `42d9ff3` | Closure asked for an appended LOG correction and a registry fix (`spotcheck:150`). `LOG.md:951` states that `LOG.md:916` cites `gate-replays-4f48343.json` under the name `gate-replays-ddb7347.json`. The historical line `LOG.md:916` still contains `census/round-17/gate-replays-ddb7347.json`. The gate’s LOG window is the target-round heading only (`tools/souji-landing-gate.py:651-666`, `830-835`), so a round-18 scan does not see line 916. SKILL.md:165-168, `corpus/README.md:216`, and `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148` cite the `4f48343` records. A repo-wide search for `gate-replays-ddb7347.json` / `jj-receipts-ddb7347.txt` at the tip hits LOG:916, the round-18 correction prose, SCORECARD.md:14, QUALITY.md:80, and `corpus/lessons/round-18.md:7` as bare filenames beside a separate `` `census/round-17/` `` token. `POINTER_PATH_RE` (`landing-gate.py:124-129`) requires a `census/`/`tests/`/`tools/`/`corpus/`/`.ufo/waves/` prefix, so those bare names are invisible. That invisibility is the residual the lesson already states at `round-18.md:74`. |
| R3 “22 repos” | count closed; “identical” fails on the r18 files | wording `42d9ff3` | Each of `census/round-18/live-fleet-pairs/pair{1,2}-{base-b576341,changed-worktree}.tsv` is 22 lines: 1 header + 21 repository rows. Same 21 paths on both sides of each pair. SCORECARD.md:15’s prior clause now says 21 repositories and explains the header. `round-18.md:61` matches that count. |
| R4 narrow Q7 | claimed closed; the Q7 cell is unchanged | Q29 row `42d9ff3`; knowledge sentence `3f822e8` | `git diff -G '^\| Q7 \|' b576341 5efb519 -- corpus/QUALITY.md` is empty. QUALITY.md:31 still begins “Every lane or hygiene commit” and still checks `commit -- <paths>` plus `-c maintenance.auto=false`. QUALITY.md:78 (Q29) says it supersedes Q7 for colocated repos and that Q7 stays in force for plain repos. `round-18.md:3` calls this “R4 Q7 narrowed by Q29.” `round-18.md:62` says “Q7 is unchanged.” `jj-colocation-receipts.md:87` names both routes. The closure’s sentence (`spotcheck:152`) is a change to the Q7 cell. That cell is the baseline sentence. |
| R5 carried bundle | split | FIFO `3f822e8`; the rest open | See the rows below. The lesson’s routed list (`round-18.md:3`, LOG.md:951) names R1–R4 and does not say R5 is closed. |

R3 flag, same sentence as the count fix. SCORECARD.md:15 says “live fleet pair identical on 21 repositories” and points at `census/round-18/live-fleet-pairs/`. Lesson `round-18.md:6` says pair 1 is identical excluding mtime, and pair 2 differs in `mado-shokunin` dirty 10 → 13. Column compare of the four committed TSVs:

- pair 1: one difference, `tameshi-shokunin` `mtime_iso` `2026-10-20T17:29:36-03:00` → `2026-10-20T17:29:48-03:00`.
- pair 2: `mado-shokunin` dirty `10` → `13` and mtime `17:29:30` → `17:29:56`; `tameshi-shokunin` mtime `17:29:56` → `17:30:08`.
- The lesson’s non-mtime account matches. SCORECARD’s “identical” does not. Pair 2’s mtime deltas are also outside the lesson’s “differs only in … dirty” clause.

## Round-17 Residuals (`corpus/lessons/round-17.md:86-91`)

| Clause | Tip status | Commit | Evidence |
|---|---|---|---|
| TOCTOU FIFO swap hangs the run with no output (`:86`) | closed for the hang; D-state carried open | `3f822e8` | `run_repo_with_watchdog` (`tools/souji-census.sh:1470-1651`) wraps `guard_repo_candidate` and `census_one` (`:1670-1710`). Timeout row and `souji-census: repo-timeout <N>s <repo>` are in the header (`:157-163`). `list_repos` (`:1386-1438`) is outside the watchdog and only stats (`-d`/`-L`/`-f`, glob). Round 18 claims this closure (R18-M4, C1) and carries the D-state case at `round-18.md:73`. Fixture case B8 is a list-phase config FIFO (`tests/fixtures/r18-census-bounded.py:1069-1103`). Not re-run. |
| Symlink loop or out-of-gitdir symlink at `info/attributes` keeps the whole-run refusal (`:86`) | open, documented, absent from the r18 residual list | — | `souji-census.sh:109-110`. |
| Admin-dir `info/attributes` degrades the owner (`:86`) | open, documented, absent from the r18 residual list | — | `souji-census.sh:111-119`. |
| 10,000 bad repos exceed a 120 s budget before any output (`:86`) | open, carried in stronger form | — | `round-18.md:73`: `list_repos` scaling unmeasured; default bound 600 s times repositories (`souji-census.sh:174-175`). Header is printed after the repo loop (`:1719`). |
| Inherited contractions vs `a31642d` (`:87`): `:(optional)` on `core.worktree`; nested-layout pathspec excludes; `emit_compare` on `error` rows; newline worktree paths | open, carried as one clause | — | Still in the census: `core.worktree` strips `:(optional)` at `:781-787`; `emit_compare` applies `numeric_change` to the numeric columns of every differing row including an `error` placeholder (`:1857-1859`); worktree side flags read line-oriented `worktree list --porcelain` (`:1296`). `git diff --stat b576341 5efb519` is empty for the r13/r14 runners and `souji-repo-structure.sh`. `round-18.md:26` and `:73` say these contractions are unchanged. |
| `unpushed` is branch-based in jj lanes (`:88`) | open, absent from the r18 residual list | — | `count_unpushed` is `rev-list --count --branches --not --remotes` (`souji-census.sh:1047-1058`). |
| r13 `run-verification.py:384` and r14 `cache-demonstration.py:166` pin `HEAD` (`:88`) | open, carried | — | Those lines are still `rev-parse HEAD` / `rev-parse --verify HEAD`. `round-18.md:76`. Diff stat vs baseline empty. |
| `souji-repo-structure.sh` counts inflate with keep refs (`:88`) | open, absent from the r18 residual list | — | The probe’s own comment: `git repo structure` seeds from references (`tools/souji-repo-structure.sh:31-32`). No `refs/jj` exclusion. File unchanged since `b576341`. |
| Keep-ref lifetime unmeasured (`:88`) | open, absent from the r18 residual list | — | `jj-colocation-receipts.md:108` and `corpus/README.md:216` still say the helper never runs `jj util gc` and expiry is unmeasured. This is the R5 keep-ref clause. |
| Seat-audit precision on fresh transcripts unmeasured; truncated arguments hide violations (`:89`) | open; the r18 residual is a different seat-audit hole | — | `tools/souji-seat-audit.py:41` still states the `…` truncation limit. SCORECARD.md:86 schedules fresh-transcript precision as r19. `round-18.md:77` adds the patch-delivery / clone-write false majors (`ScoutSeatAuditR18.md:30-32`) and does not restate truncation. |
| Carry-gate wrap-truncated quotes and non-vocabulary STATUS lines (`:90`) | open; wrap carried, non-vocabulary only as “carried by reading” | — | `check_carry` walks physical lines (`landing-gate.py:388-419`). `round-18.md:74` says wrap truncation is still open and the ScoutCarryWrap rule is drafted. `round-18.md:56` says non-vocabulary findings were carried by reading. The benign-status selftest still expects non-vocabulary STATUS to produce no finding (`landing-gate.py:1843-1849`). |
| Disposition of `census/operator-sweep-20261019/` (`:91`) | open; gate exemption is not a disposition | — | `corpus/pointer-exemptions.tsv:1` still calls it operator-owned and unopened (L0 `souji \| round-17`). Not named in `round-18.md:73-77`. This seat did not open the directory. |

## Round-18 Residuals (`corpus/lessons/round-18.md:73-77`)

All five bullets are open at the tip. None is secretly closed by `2fc5f33` or `5efb519`.

| Bullet | Why it is still open |
|---|---|
| `:73` inherited contractions; D-state unreaped; `list_repos` scaling; 600 s × repositories | Contractions as in the r17 row. Unreaped path is `souji-census.sh:1640-1642` (`repo-timeout-unreaped`) after KILL. No 10,000-repo fixture. The per-repo loop is sequential under `REPO_TIMEOUT` default 600. |
| `:74` elided tokens and prefix-less prose; fleet paths vs the working tree; carry-gate wrap | `POINTER_PATH_RE` stops at a backtick and requires a root prefix (`landing-gate.py:124-129`). Fleet hits use `os.path.exists` under `--fleet-root` (`:850-864`), not a revision. Wrap is line-oriented `check_carry`. |
| `:75` 58 fixture orphans listed, not reaped; no F5 knowledge entry | `tools/souji-proc-census.sh:1-3` is list-only outside its selftest. The only `kill` is `cleanup_selftest` (`:363-368`). `corpus/knowledge/` at the tip is eight entries, none a process-residue entry (`git ls-tree 5efb519:corpus/knowledge`). Live orphan count not re-measured. |
| `:76` HEAD-pinned r13/r14 runners | Lines cited above, unchanged. |
| `:77` seat-audit r18 shapes are false majors | `souji-seat-audit.py` still returns `V-WRITE-SCOPE` for a target outside the allowed set (`:197-202` region; scout table at `.ufo/waves/round-18/w1/ScoutSeatAuditR18.md:30-32`). No patch-path or clone-root exception landed in the auditor. |

## Claimed open, actually closed

`round-18.md:56` carries `CriticRoundAdmission.md` B3 as “non-hash `measured_commit` — still silent, open.” The critic’s text (`.ufo/waves/round-18/w1/CriticRoundAdmission.md:63-72`) describes a skip: hex regex fails, `measured_ok = False`, no finding. At the tip the finding is unconditional once the key is present and `measured_ok` is false, for `--round >= 18`:

```590:606:tools/souji-landing-gate.py
            if (
                round_no >= 18
                and isinstance(record, dict)
                and "measured_commit" in record
                and not measured_ok
            ):
                ...
                            "LG-FROZEN-MEASURED",
```

`git blame -L 585,606` puts `588-589` (`else: measured_ok = False`) on `7a79dc2` and `590-606` on `3f822e8`. The lesson commit `42d9ff3` is later and still says silent. What remains is the diagnostic: a non-hex name is reported as “does not resolve” because `rev-parse` runs only inside the hex branch (`:566-587`). Silence is gone.

## Routed “open (r18)” lines that are outside the Residuals heading

`corpus/lessons/round-17.md:55,60,64,65` and the spotcheck dead-review list (`:110`).

| Item | Tip status | Commit |
|---|---|---|
| Sentinel F3 TOCTOU (`:60`) | closed, same watchdog as the residual | `3f822e8` |
| `RerunMatrixLanded` finding 2: `bash -n` / shellcheck / selftest absent from `invalid_suites` (`:65`) | closed in the r18 runner; the r17 runner is unchanged | `3f822e8` |
| `MutateCensusD2` blocked (`:55`); per-mutant re-run of 8+4 survivors (`:64`) | open, not in the r18 residual list | — |
| Five dead wave-2 reviews: RevJjNovelPaths, RevVProbeRows, RevQuarantineRunbook, RevCensusHeaderTruth, RevKnowledgeEntry (`spotcheck:110`) | open, not in the r18 residual list. Spotcheck already said no claim number depended on them (`:112`) | — |
| `ScoutGitOpens` `GIT_ATTR_NOSYSTEM` unset (`round-18.md:56`, marked open) | open. `git`-style search of `souji-census.sh` for `GIT_ATTR` is empty. Not copied into `## Residuals` | — |

r17 `invalid_suites` is still fixture-validity only (`census/round-17/run-matrix.py:233-235`). r18 appends bash-n, shellcheck-warning, and selftest (`census/round-18/run-matrix.py:415-420`). Diff stat of the r17 runner vs `b576341` is empty.

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline b5763415cc67ecff1e8fe56c58c39a6fb106d7a3..5efb519f00075d958c3d1109ef6fcb24c487eb87
# 5efb519 round-18: r15 frozen preservation record regenerated at 2fc5f33
# 2fc5f33 round-18: gate comma line-lists, exemption keyed on record, ...
# 42d9ff3 round-18: docs — lesson, LOG, SCORECARD, QUALITY Q29-Q32, ...
# 3f822e8 round-18: build — C1 ... R1 recipe owner, R2 pointer repairs

git diff --stat b576341 5efb519 -- corpus/lessons/round-17.md \
  corpus/lessons/round-17-verifier-spotcheck.md \
  census/round-17/run-matrix.py tools/souji-repo-structure.sh \
  census/round-13/run-verification.py census/round-14/cache-demonstration.py
# empty

git diff -G '^\| Q7 \|' --stat b576341 5efb519 -- corpus/QUALITY.md
# empty (exit 0)

git log --oneline -S 'Supersedes Q7' b576341..5efb519 -- corpus/QUALITY.md
# 42d9ff3
git log --oneline -S 'Q29, r18' b576341..5efb519 -- corpus/knowledge/jj-colocation-receipts.md
# 3f822e8
git blame -L 585,606 5efb519 -- tools/souji-landing-gate.py
# 588-589 7a79dc2; 590-606 3f822e8
```

Live pairs, extracted with `git show 5efb519:census/round-18/live-fleet-pairs/<file>` and compared as TSV columns: 21 data rows each; differences as in the R3 flag. Scratch under `/var/tmp/souji-r18w2-ConnResidualMap-6` removed after the compare.

## Proposed move

One documentation erratum, no tool change. Scope the Q7 cell to plain repositories (subject and check column), which is the closure sentence at `round-17-verifier-spotcheck.md:152` and is what Q29 already claims is true. In the same erratum, replace SCORECARD.md:15 “identical” with the lesson’s pair result including pair 2’s mtime deltas, and replace `round-18.md:56` “B3 still silent” with “finding since `3f822e8`; rev-parse still skipped for non-hex.” Append the uncarried opens (dead reviews, keep-ref lifetime, branch-based `unpushed`, repo-structure keep refs, symlink-loop refusal, admin-dir degrade, operator-sweep disposition, non-vocabulary STATUS, seat-audit truncation) to the round-18 residual list so a later round cannot read their absence as closure.

Risks: a rewritten Q7 row moves a historical incident citation; keep the incident examples and change the subject and the check. Calling B3 fully closed would hide the skipped `rev-parse` on names like `master`. Carrying the dropped clauses is a map correction; it does not reopen C1–C3 measurements.

Verification for whoever lands it: `git diff -G '^\| Q7 \|'` against `b576341` shows a subject limited to plain repos; re-diff the four live-pair TSVs against the SCORECARD sentence; read `check_frozen_pins` `:566-606` and confirm a non-hex `measured_commit` still takes the finding branch. Do not treat an unrun gate or census invocation as confirmation.
