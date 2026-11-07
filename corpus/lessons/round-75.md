# Round 75 — what an ignore rule may hide from the pre-report gate (C1 operability), a second detector for the counter's witness (C2 calibration)

Attempt 1 (`SoujiR75`). Lane base `52d3f07d08422689464598f8be7e2c957fcf0805` (r74 admitted, spot-check committed).
Staged commits in the order the preregistration binds: P `7ba5217d6fc754201615e04e8dfc88cf07c33fd3` (instruments,
populations, every control receipt, mutant variants, S318/S319 captures, census-before); F
`be599cbb02854b9d669a1a2699f15657fd70b336` (preregistration in Q99 grammar); I `f6ec0d7140e0976b8128af803520b895a14a64e0`
(C2 candidate counter); W `1ad737b4a9ac71bd44b6ac849f73387fdc3ab9c5` (C1 candidate gate); A
`5d10e09ed7749f5706eade39ac9a0ae2355aa1f3` (after-arms). Frozen claims, counters and predicates are in
`census/round-75/preregistration.txt` and are not restated here.

## Inherited

The r74 spot-check routed four defects (`corpus/lessons/round-74-verifier-spotcheck.md`, Routed defects):

- 1 (the domain trial bound a gate revision the prereg did not name) → this prereg names the gate revision
  the domain trial binds (the C1 candidate commit's gate blob; a later blob only by recorded amendment).
- 2 (`OVER-REFUSAL=1` on `n-filemode-config` undisclosed) → ruled in the prereg: a mode change is a lane
  change, expected FAIL; the r75 counter freezes an expected verdict per route instead of the probe's
  bytes-only truth (Mistakes M3).
- 3 (routed items (a)-(e) of the r74 lesson) → (b) X09/X15 taken as C2; (e) Q99 freeze-check grammar met
  by this round's prereg (`census/round-75/records/freeze-check.txt`, `SUMMARY claims=2 findings=0`, with
  `--substance --chronology`); (a), (c), (d) and the `PATH`/`BASH_ENV` limit stay routed.
- 4 (ignored-untracked forgeries a stated limit) → C1 for the repository-local sources; QUALITY Q136
  supersedes Q135's ignored-files limit clause.

No inherited lane leftovers (`jj-lane.sh state`: tracked=0 untracked=0). No `considerthese/` directory exists
in this lane; no shokuknow theme taken (Assimilation: none).

## Measured

- C1: `census/round-75/controls/c1-K-a-do-nothing.txt` (lane-base gate) `SUMMARY rows=25 mismatches=2 errors=0`
  (f-info-exclude, f5-info-exclude-dir `clean=PASS`), EXIT=1; blanket control
  `controls/c1-K-b-blanket-ignored.txt` mismatches=3 (f2, f6, f7 honest rows `clean=FAIL`), EXIT=1; after
  `records/c1-after.txt` mismatches=0, EXIT=0.
- C2: `controls/c2-K-do-nothing-r74.txt` `SUMMARY mutants=6 killed=4 survived=2 unread=0 pristine=PASS`
  (X09 and P1 SURVIVED), EXIT=1; blanket control `controls/c2-K-blanket-pristine-red.txt` pristine=FAIL,
  EXIT=1; after `records/c2-after.txt` `killed=6 survived=0 unread=0 pristine=PASS`, EXIT=0; X15 alone
  `records/c2-after-X15-selftest.txt` 64/64 (informational, survives by design).
- Wave repair (after measurement): `census/round-75/records/wave-repair/c1-at-repair.txt` mismatches=0, EXIT=0;
  core.worktree route `coreworktree-W.txt` `check-clean=PASS` → `coreworktree-R.txt` `RECEIPT-WORKTREE-REDIRECTED`;
  r36 fixture original at W `regress-r36-original-at-W.txt` 18/21 EXIT=1 → amended at base and at the repair 21/21
  (`regress-r36-amended-at-base.txt`, `regress-r36-amended-at-repair.txt`); r27 4/4 (`regress-r27-at-repair.txt`).
  The original-fixture receipt's `# bind` line hashes the amended lane file; the bytes it ran are
  `git show 5d10e09ed7749f5706eade39ac9a0ae2355aa1f3:tests/fixtures/r36-report-gate.py` (command= names the copy).
- Freeze grammar: `census/round-75/records/freeze-check.txt` — `tools/souji-freeze-check.py --substance --chronology`
  over this prereg, `SUMMARY claims=2 findings=0`, EXIT=0 (Q99 NOT MET r72-r74).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | a shell variable bound in a chain that the trailing `&` backgrounded (this round): the first control launch `S=… && R=… && ( rec K-a ) & ( rec K-b ) & …` ran the whole assignment chain in the background, so the K-b and C2 arms saw `$R` empty and printed `command not found` | L1 session 2026-11-06 ~21:24 -03; the receipts from that launch were deleted and every control re-run from a script file (`census/round-75/controls/*.txt` are the re-runs, each with `command=`/`rev=`/`instrument=` lines) | none (no receipt was written, so nothing could be scored) | multi-arm launches run from one script file; the wave context now names the slip in its variable-binding rule |
| M2 | an instrument launched without its precondition, recurring (r74 M2): three C2 before-arms ran with a `--work` directory that did not exist and read `C1-COUNTER-FATAL … EXIT=2` | L1 session ~21:25 -03; deleted and re-run after `mkdir -p` | the counter's own guard (exit 2), and from this round `census/round-75/c2-kill-counter.py`, which reads an EXIT=2 receipt as UNREAD, never a kill | the launch scripts create every `--work` dir; r74's "disclosure only" fix did not prevent the recurrence, so the tally's UNREAD class is now the fix (S75MutCounter M1/M2: the UNREAD boundary itself has no committed receipt yet — routed r76) |
| M3 | a probe that labels routes by worktree bytes alone (mined from r74): `evade-R.txt` called `n-filemode-config` OVER-REFUSAL (a real mode change) and `f2-gitignore` FORGERY (hidden by a committed rule) | `corpus/lessons/round-74-verifier-spotcheck.md` routed defect 2; `census/round-74/records/wave-repair/evade-R.txt` | none (no rule asked a probe to freeze its expected verdicts) | the r75 counter freezes an expected verdict per route (`census/round-75/c1-population.tsv`, rulings in the prereg); shown able to fail: lane-base gate mismatches=2, blanket control mismatches=3 |
| M4 | a stated limit that lumps two kinds of rule (mined from r74): Q135 says ignored untracked files "(`.gitignore`, `info/exclude`)" are not lane changes, though gitignore(5) places only `.gitignore` among versioned rules (S318) | `corpus/QUALITY.md` Q135 limits clause; `census/round-75/controls/c1-K-a-do-nothing.txt` (info/exclude-hidden rows pass the lane-base gate) | none | QUALITY Q136 supersedes the clause; shown able to fail: the lane-base gate scores mismatches=2 on the frozen counter |
| M5 | a gate population that samples the ignore sources but not the tree git resolves, and a regression fixture not re-run before the after-arms (this round): a repository-local `core.worktree` forged both the lane-base and the W gate, and the W gate red four (S75MutGate) or three (L1 re-run) of the r36 fixture's honest cases | `.ufo/waves/round-75/w1/S75ExecEvade.md` HIGH-1, `S75Sentinel.md` F1, `S75CriticClaims.md` 3; `S75MutGate.md` HIGH F1; `census/round-75/records/wave-repair/` | none (the r74 `l-core-worktree` row modifies a tracked file and fails on a copy artifact, so it never tested an untracked payload) | repaired after measurement: work-tree check (`coreworktree-W.txt` PASS → `-R.txt` FAIL), fixture harness symlink declared by a committed rule (18/21 → 21/21); the frozen counter still 0 at the repair; next prereg names the r27/r36 regressions as a conjunct |
| M6 | a frozen description stronger than the tree (this round): prereg C1 says the lane carries ignored untracked files "under committed .gitignore rules only"; 13 397 of 26 032 such paths sit under the untracked self-ignoring `.jj/.gitignore` and `.ruff_cache/.gitignore` | `.ufo/waves/round-75/w1/S75CriticDiscern.md` (HIGH, `git check-ignore -v` over the listing) | none (no check ties a prereg's descriptive clause to a measurement) | not edited (frozen); the knowledge entry, Q136 and the report state the self-ignoring shape; the domain-trial predicate itself (check-clean=PASS) is unaffected |

## Gate

- **S318 admit (A, mined)** — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitignore.adoc, sha256
  `338221577b4f…5e71`, 9535 bytes, accessed 2026-11-06 by the L1 (capture `census/round-75/srcs/gitignore.adoc`),
  re-fetched by S75ScoutSources (sha256 equal). Offset 3807 of the whitespace-normalized capture (raw lines 98-99):
  "Patterns read from exclude sources that are outside the working tree, such as $GIT_COMMON_DIR/info/exclude and
  core.excludesFile" (16 words). Cited by `corpus/knowledge/filter-filemode-witness.md` r75; grounds the sourced claim C1
  (the two local sources are outside the tree, never committed).
- **S319 admit (A, mined)** — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-ls-files.adoc, sha256
  `56af3aad88df…a74b`, 12123 bytes, accessed 2026-11-06 (capture `census/round-75/srcs/git-ls-files.adoc`), re-fetched by
  S75ScoutSources (sha256 equal; builtin/ls-files.c and dir.c `setup_standard_excludes` at v2.56.0 confirm the reading).
  Offset 11458 of the whitespace-normalized capture (raw lines 329-334): "give `--exclude-per-directory=.gitignore`, and
  then specify: 1. The file specified by the `core.excludesfile` configuration variable, if exists, or the
  `$XDG_CONFIG_HOME/git/ignore` file. 2. The `$GIT_COMMON_DIR/info/exclude` file." (24 words). Grounds the gate's set
  difference.
- **Rejected anchors (S75ScoutSources, MEDIUM: each stopped before the clause the claim rests on)** — S318 first filed
  at raw offset 1699, "Patterns which are specific to a particular repository but which do not need to be shared with
  other related repositories" (20 words; the destination, info/exclude, lies outside the quote); S319 first filed at raw
  offset 11681, "To emulate what `--exclude-standard` specifies, you can give `--exclude-per-directory=.gitignore`,
  and then specify:" (12 words; the list naming the two sources lies outside). Both replaced before the rows landed;
  offsets now follow the house whitespace-normalized convention (S75ScoutSources LOW).
- **Rejected anchor (L1)** — for S318, "Patterns which should be version-controlled and distributed to other repositories
  via clone (i.e., files that all developers will want to ignore) should go into a `.gitignore` file" (27 words, over
  the 25-word bar).
- No existing row's status, recheck or used-by cell changed. Assimilation: none (no `considerthese/` in this lane;
  no shokuknow theme fits the frozen claims).

## Wave

One v1 wave `w1`, 12 seats, validated under `ufo-wave-policy.json` (band 8-16) and dispatched through the inline
handoff (`census/round-75/records/wave-w1/w1.ready.dispatched`); WAVE-DONE received; `w1-results.json` carries output
for all 12 seats; 12 report files (`census/round-75/records/wave-w1/seats/`). Roles: connector 1, scout 1, executor 3,
mutation-tester 2, reviewer 1, critic 2, sentinel 1, scribe 1; attack seats 5 of 12. Dead seats: 0. The L1 holds the
planner seat.

- Reproduced from committed bytes: C1 25-row counter at base (2), W (0) and K-b (3) — S75ExecC1, S75ExecEvade,
  S75MutGate, S75CriticClaims; C2 tally 6/6 and do-nothing 4/6 — S75ExecC2, S75Reviewer, S75CriticClaims,
  S75CriticDiscern; freeze-check `claims=2 findings=0` — S75Reviewer, S75CriticClaims, S75CriticDiscern (Q99, Q120 PASS).
- Forged or regressed outside the frozen rows, repaired after measurement (M5): repository-local `core.worktree`
  (S75ExecEvade HIGH-1, S75Sentinel F1, S75CriticClaims 3); the r36 fixture's honest cases (S75MutGate HIGH F1).
- Attribution (S75MutGate F2, S75CriticClaims 2, S75Reviewer O1): f3 (core.excludesFile) is refused at base by the
  writer's pinned status (`-c core.excludesFile=/dev/null`), so the new block's own catch is the info/exclude arm;
  an info/exclude-only gate would meet the target. Recorded in Q136, not a re-scored claim.
- Unmeasured branches (S75MutGate F3/F4): the ls-files failure branch (W07/W14 survive: no route makes ls-files fail
  after status succeeds) and the refusal class/order (the counter reads `check-clean=` only).
- C2 qualifications: post-only new-slot witness (Y4) and row_fate aliased to the base witness (Y5) survive the r75
  selftest (S75ExecC2); four selftest-block mutants survive while still killing X09/P1 (S75MutCounter s1-s3, s6); the
  tally cannot tell EXIT=2 `fail=1` or `fail=0 EXIT=1` receipts (no such receipt committed, S75MutCounter M1/M2) and
  does not bind a receipt to its mutant (S75Reviewer O2).
- S75ScoutSources: both first-filed anchors stopped before the clause the claim rests on; re-anchored before landing.
- S75Connector: 12 sites in 9 sibling lanes decide "clean" from plain `git status --porcelain` (documented, not edited).
- S75Scribe: drafts validated (`census-validate` exit 0); its "25867 paths each" note caught the knowledge entry's
  frozen count, reworded.

## Routed to round 76

- (a) new-slot post-only witness and row_fate aliasing (S75ExecC2 Y4/Y5); selftest-block survivors (S75MutCounter).
- (b) kill tally: committed receipts for the UNREAD boundary; receipt-to-mutant binding (S75MutCounter M1/M2, S75Reviewer O2).
- (c) gate: ls-files failure branch and refusal-class/order measurement (S75MutGate F3/F4); the r27/r36 regressions
  as a frozen conjunct of any gate claim (M5).
- (d) carried: witness set derived from the builders (r74 M3); the other status-trusting lane tools and writer survivor
  M03; caller `PATH`/`BASH_ENV` trust (S74Sentinel, S75Sentinel F3).
