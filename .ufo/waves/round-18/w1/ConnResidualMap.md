STATUS: DONE — of the named r17 open items, r18 closes the census_one FIFO hang (C1) and closure R1–R4; the 120s-before-output clause stays open because it is list_repos, and C2/C3 close none of the carry-gate or receipt residuals.

# Axes

Judged axis: calibration. Companions, not scored here: operability (C1 hang bound), coverage (C3 process census).

Booking rule used below: an item is closed only when a round-18 claim or a routed fix names its outcome. A parenthetical "open (r18: …)" in the r17 lesson is a note to this round, not a claim this round adopted.

# Lesson table

Copy into the round-18 lesson. `closed by` means the r18 contract covers it; nothing below is landed at `b576341`.

| id | source | item | status | why (file:line) |
|---|---|---|---|---|
| RES-FIFO | residual :86 clause 1; seat :60 F3; closure R5 clause "TOCTOU" | After `guard_git_files`, a FIFO swapped in for `info/attributes` blocks `git status`/`check-attr` `open(2)`; rows are buffered, so the fleet emits nothing | closed by C1 | Contract: `emit_census` runs each `census_one` in its own process group with a watchdog (`--repo-timeout` / `SOUJI_CENSUS_REPO_TIMEOUT`, default 600). That is the hang. Sentinel smallest fix was `timeout` on the two git calls (`SentinelCensusD2.md:45`); C1 bounds the whole `census_one` instead. Current hole: `tools/souji-census.sh:1402-1410` (collect), `:1412-1415` (print only after the loop). C1's second clause (fixture `start_new_session` + `killpg` on timeout) is the orphan half of the same hang; it is not a separate r17 residual. C3 only lists residue and never signals, so it does not close this row. |
| RES-SCALE | residual :86 clause 4 | 10,000 bad repos exceed a 120s budget before any output | open | Not C1. Sentinel F7: N=10000 → rc 124 at 120.00s, 0 bytes stdout/stderr, because the `list_repos` guard pre-pass (~31 ms/repo) passes 120s and rows are emitted later (`SentinelCensusD2.md:71-79`). `emit_census` calls `list_repos` at `souji-census.sh:1400` before the `census_one` loop the C1 watchdog wraps (`:1402`). Default bound 600s is also not a 120s fleet budget. |
| RES-SYMLINK | residual :86 clause 2 | Symlink loop or out-of-gitdir symlink at `info/attributes` stays a whole-run symlink refusal | open | Documented fail-closed. `guard_git_links` still `protected_fail`s `git-metadata-symlink` (`souji-census.sh:522-536`) inside `list_repos`, before the per-repo watchdog. C1 keeps `census_one` exit 2 as a whole-run exit 2. No claim narrows this. |
| RES-ADMIN-ATTR | residual :86 clause 3 | An admin-dir `info/attributes` degrades that repo though git reads only the common `info/` | open | Fail-safe over-degrade, not the dot-admin hang (that one is `resolved@4f48343`, lesson :60 F4). Sentinel B2: FIFO admin attrs → rc 0 `error` row while `git check-attr` in the worktree does not read them (`SentinelCensusD2.md:68`, `:91`). No r18 claim names admin `info/attributes`. |
| RES-OPTIONAL | residual :87; closure R5 "contractions vs a31642d" | `:(optional)` stripped on `core.worktree` | open | Inherited vs `a31642d` under L0 `souji \| round-16`. Closure :16 and R5 (`round-17-verifier-spotcheck.md:154`) leave the set open. Not in C1/C2/C3 or R1–R4. |
| RES-PATHSPEC | residual :87 | Nested-layout pathspec excludes | open | Same inherited set. |
| RES-EMIT-COMPARE | residual :87 | `emit_compare` against `error` rows | open | Same inherited set. |
| RES-NEWLINE-WT | residual :87 | Newline worktree paths | open | Same inherited set. |
| RES-UNPUSHED | residual :88 | Census `unpushed` column stays branch-based on jj lanes | open | r17 C3 disclosed it (lesson :27). r18 C3 is process residue, not the column. |
| RES-HEAD-PIN | residual :88 | `census/round-13/run-verification.py:384` and `census/round-14/cache-demonstration.py:166` still pin `HEAD` | open | Historical runners. No r18 claim. |
| RES-STRUCT-COUNT | residual :88 | `souji-repo-structure.sh` counts inflate with keep refs | open | No r18 claim. |
| RES-KEEP-LIFE | residual :88; closure R5 | Keep-ref lifetime unmeasured (`jj util gc` only; helper never runs it) | open | L0 question (closure :39). r18 C3 does not measure refs. |
| RES-AUDIT-FRESH | residual :89 | Seat-audit precision on fresh transcripts unmeasured | open | r17 C2 scope (lesson :26; closure :18). r18 C2 is `LG-DANGLING-PTR` / frozen `measured_commit`, not the auditor. |
| RES-AUDIT-TRUNC | residual :89 | Truncated arguments still hide violations | open | Same. No r18 claim. |
| RES-CARRY-WRAP | residual :90; D5 wraps; D5 last clause | Carry gate sees only the first physical line, so wrap-truncated quotes pass | open | `check_carry` sets `needle = norm_line(raw)` on one `seat_failure_lines` row and tests that needle (`tools/souji-landing-gate.py:400-406`). Five r16 carries still stop mid-phrase without `…`: `corpus/lessons/round-16.md:73,74,78,79,84` (drafts in `RevD5Carry.md` C2, C7, C8, C9, C3). r18 C2 adds a path-token finding; it does not change `check_carry`. |
| RES-CARRY-VOCAB | residual :90; D5 `RevGateSpec.md:226` | Non-vocabulary STATUS lines are invisible | open | `FAILURE_STATUS_WORDS` is the pinned set at `souji-landing-gate.py:91-97`. `review` is not in it, so `RevGateSpec.md:226` (`STATUS: review complete — …`) is not a marker (`RevD5Carry.md:96-102`). |
| RES-OPERATOR | residual :91 | Disposition of `census/operator-sweep-20261019/` | open | Closure :37 moves it to L0 `souji \| round-17`. r18 seats are forbidden to open it. Not a claim. |
| SEAT-MUTCENS | seat :55 | `MutateCensusD2.md:1` BLOCKED: wrong r15 flag (`--tool`); fixture trees outside the seat root | open | Lesson says re-issue with both permitted. The r18 goal does not. D2 mutation coverage remains the hygiene red/green arms. C1's `killpg` makes a future FIFO arm safe to run; it does not run it. |
| SEAT-F4 | seat :63 | `RevGateTotality.md` F4 guarded, not self-tested | open | Guard is present: `rev-parse` rc other than 0 or 1 raises `EvalError` (`souji-landing-gate.py:548-566`). No selftest feeds rc 128. The comment `r17 F4` at `:1171` is the bold-STATUS case, a different mechanism. r18 C2 does not add this case. F1–F3 and F5 stay `resolved@4f48343` (not rows). |
| SEAT-MUT-RERUN | seat :64 | `MutateJjNovel.md` (8) and `MutateSeatAudit2.md` (4): killers landed, per-mutant re-run not done | open | Lesson :64 marks it open for r18. The goal does not re-run them. |
| SEAT-MATRIX | seat :65 | `RerunMatrixLanded.md` finding 2: `bash -n` / shellcheck / selftest not in `invalid_suites` | open | `census/round-17/run-matrix.py:189` `suite_keys = list(fixtures)`; `:233-235` invalid list is only those keys. `bash_n` (`:206`), `shellcheck_warning` (`:208`), `selftest` (`:212`) are recorded and not gated. A selftest crash can still exit 0 with `invalid_suites: []` (`RerunMatrixLanded.md:63-72`). Not in C1. |
| D5-BARE | D5 | `round-16.md:54` bare `resolved:` (no `@<hex>`) | open | Line is still `resolved: this lesson supersedes the skeleton.` Disposition is known: `resolved@163158a` (`RevD5Carry.md:62`). The gate never sees it (`skeleton` is not a failure word; `CARRY_TOKEN_RE` is only applied to markers). No r18 claim rewrites the historical line or the token rule. |
| D5-P3 | D5 | P3 `--report PATH` | open | Spec: optional `--report`; markers must also occur there; default `checked_report=0` (`RevGateSpec.md:99-103`). Argparse has `--json`, not `--report` (`souji-landing-gate.py:1353-1358`). |
| D5-P6 | D5 | P6 tree scan or mandatory `--base` | open | Spec: `LG-PARSE-TREE` over `tools/` + `tests/fixtures/`, or mandatory `--base` (`RevGateSpec.md:134-142`). `--base` help text is still "optional" (`souji-landing-gate.py:1356`). |
| R1 | closure R1 | `q_jj_commit_recipe` hardcodes `--as souji`; helper accepts only the recorded lane id or `protocol` | closed by routed R1 | `tools/souji-quarantine.sh:246-251`; `scripts/hyaku/jj-lane.sh:516-517`. Routed fix: owner id plus a fixture assertion. Not C3. |
| R2 | closure R2 | `LOG.md:916` and `SKILL.md:165` cite missing `census/round-17/gate-replays-ddb7347.json` | closed by routed R2; class enforced by C2 | Committed record is `gate-replays-4f48343.json` (closure :150). Routed fix: appended LOG correction and registry pointer. C2's `LG-DANGLING-PTR` (`--round` ≥ 18) is the class. Goal sweep at `b576341`: 281 tokens, 18 unresolved. R2 is one of them (`SKILL.md:163,165` in that sweep; closure cited `:165`). `census/round-17/jj-receipts-ddb7347.txt` (knowledge entry) is in the 18 and was not a closure route. Fixing R2 alone does not make the C2 before-count 0. |
| R3 | closure R3 | SCORECARD "22 repos" | closed by routed R3 | Closure :67: 22 rows including the header = 21 repositories. Lesson :7 "22 rows" is the row count and stays correct. The fix is the SCORECARD noun, 22 → 21 repos. |
| R4 | closure R4 | QUALITY Q7 prescribes `commit -- <paths>` for every lane | closed by routed R4 | Narrow Q7 to plain repos; jj-colocated commits stay on the helper (closure :101-106). |
| R5-REVIEWS | closure R5; closure :110 | Five dead wave-2 reviews not redone | open for three; not a product defect for two | Still unreviewed, and not in r18: `RevJjNovelPaths`, `RevVProbeRows`, `RevCensusHeaderTruth`. `RevQuarantineRunbook`: closure read the runbook and extracted R1, which routed R1 closes. `RevKnowledgeEntry`: disclosed covered by `CriticKnowledgeOverreach` and `ScribeKnowledgeFinal` (lesson :66; closure :19, :110). |
| R5-FIFO | closure R5 | TOCTOU FIFO | closed by C1 | Same row as RES-FIFO. Do not let this clause close RES-KEEP-LIFE or RES-OPTIONAL..RES-NEWLINE-WT. |
| R5-KEEP | closure R5 | Keep-ref lifetime | open | Same row as RES-KEEP-LIFE. |
| R5-A31642D | closure R5 | Inherited contractions vs `a31642d` | open | Same rows as RES-OPTIONAL, RES-PATHSPEC, RES-EMIT-COMPARE, RES-NEWLINE-WT. |

C3 (`tools/souji-proc-census.sh`, read-only, never signals) closes none of these rows. It governs a surface the r17 open list does not name.

Not a mapped residual, do not file it as one: Q25(b). The r18 C2 contract says a frozen `measured_commit` that does not resolve is `LG-FROZEN-MEASURED`. That id already exists for a different fact: digest or path mismatch at a commit that did resolve (`souji-landing-gate.py:570-597`). A commit that does not resolve is still silent (`:548-567`, rc 1 → `measured_ok = False`, no finding). Round-17 residuals :84-91 do not list Q25(b).

# Bounded proposal

Affected axis: calibration. Operability and coverage unchanged.

When the lesson books residual :86, split it. Close only the `census_one` hang (RES-FIFO). Leave RES-SCALE open. C1's text puts the watchdog on `census_one` inside `emit_census` (`:1394-1416`). The 120s zero-output failure is the `list_repos` pre-pass at `:1400` (sentinel F7). Calling that clause closed by C1 ships a false close on the lowest axis.

Smallest fix: one open row, the RES-SCALE line above. Do not move the watchdog onto `list_repos` under the C1 contract as written.

# Risks

- A later edit that bounds `list_repos` per repo would flip RES-SCALE. Until that is in the contract, the row stays open.
- Booking "R5 closed" because the FIFO clause moved would also close keep-ref lifetime and the `a31642d` contractions. Those four-plus-one stay open.
- Booking "C2 closes the carry gate" confuses `LG-DANGLING-PTR` with `check_carry`. Wrap quotes and non-vocabulary STATUS stay open (RES-CARRY-WRAP, RES-CARRY-VOCAB, D5-P3, D5-P6).
- Booking "C2 adds LG-FROZEN-MEASURED" is false as an introduction. The id is already the resolved-commit pin check. The new fact is the unresolved-commit case, which is Q25(b), outside this table.
- R2's pointer fix is not the C2 counting delta. The before-count is 18 unresolved tokens.

# Verification

Read-only. No `souji-census.sh`, landing gate, quarantine, vault, verify, or proc-census was run. No tool installed.

Commands and observed results:

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`
- `git -C … rev-parse b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` → same
- `git -C … diff --stat b576341… -- tools/souji-census.sh tools/souji-landing-gate.py census/round-17/run-matrix.py corpus/lessons/round-17.md corpus/lessons/round-16.md corpus/lessons/round-17-verifier-spotcheck.md` → empty (cited bytes are the base)

Line cites are from those worktree reads at that commit: `round-17.md:55,60,63-65,72,86-91`; closure `:16,18,37,39,67,101-106,110,149-154`; `souji-census.sh:522-536,1394-1415`; `souji-landing-gate.py:91-97,400-406,548-597,1353-1358`; `run-matrix.py:189,206-218,233-235`; `SentinelCensusD2.md:45,68,71-79,91`; `RevGateSpec.md:99-103,134-142`; `RevD5Carry.md:62,96-102`; `RerunMatrixLanded.md:63-72`; `round-16.md:54,73,74,78,79,84`.

Verdict: the map holds. The failure mode it blocks is treating RES-SCALE, the carry gate, or R5's non-FIFO clauses as closed by C1/C2/C3.
