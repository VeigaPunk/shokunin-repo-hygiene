# Round 78 — git discovery sources that are not files (C1 operability), the LOG.md pointers resolve under a location-bound counter (C2 calibration)

Attempt 1 (`SoujiR78`). Lane base `a8558d410e9855a9d990d6542a24a9a3a365ab6c` (r77 admitted, spot-check committed).
Staged commits in the order the preregistration binds: P `a0dcfa8d7da794e821b22a421584ac2a03c611c0` (counters,
populations, forgery sets, control variants, every control receipt, prefreeze forgery battery, S323/S324
captures, census-before); F `007404ea363461a76ff23afcf6173b3281532dd3` (preregistration; freeze-check
`--substance --chronology` `SUMMARY claims=2 findings=0`, `census/round-78/records/freeze-check-at-F.txt`); W
`ed22dc9cb7a6b61a7d0bd150db4a95191b1333aa` (C1 candidate gate); K `d90740fec1862556ed504aafcd21e89d5dece0f0` (C2
captures, 240 files); L `a0f3b91fe59129802c48f7e4db750960ddeaa408` (C2 ledger, defective — M1); L2
`87d456179668738ca59e607c3176de056e6a9991` (ledger repaired); A `319109b0ddc836c6cf3364fdde3ab99796f21f32`
(after-arms). Frozen claims, counters and predicates are in `census/round-78/preregistration.txt` and are not
restated here.

## Inherited

The r77 spot-check routed five defects (`corpus/lessons/round-77-verifier-spotcheck.md`, Routed defects):

- 1 (correction not swept: S321's anchor cell and the r77 lesson Gate still said fstat reads the type) → the S321
  row's anchor parenthesis is reworded (the fstat feeds the size only) and an append-only `## Correction` closes
  `corpus/lessons/round-77.md`; the dir.c capture was re-read at lines 1164-1183 before rewording.
- 2 (C2 counter kill power: six forged single rows pass) → C2's instrument: `census/round-78/c2-pointer-counter.py`
  pins its populations by sha256, binds MOVED to round and last component, QUARANTINED to the token's directory and
  to fleet absence, TOKEN to the source text, and ships per-row forgery sets; the frozen r77 counter accepts all 7
  r77-population forgeries (`census/round-78/controls/c2-K-c-forge-r77-counter.txt`), the successor refuses them
  (`census/round-78/records/c2-prefreeze-r77-forge.txt`) and the G6 byte-equal copy
  (`census/round-78/controls/c2-K-e-g6-collision.txt`). G3 (FLEET label) is label-only: the class docstring now
  says "fleet-owned path". This landed pre-freeze as the instrument, not as a claimed gain.
- 3 (out-of-surface hangs: FIFO config, includes, HEAD, packed-refs, config.worktree; SIGTERM; frozen rows for XDG,
  relative path, backstop) → C1 (rows g1-g11, t1; XDG and HOME rows g9/g10/q5; relative include g7). SIGTERM is not
  taken (stated limit in the prereg); the 300 s check-4 backstop still has no frozen row.
- 4 (domain trial calls `bc`; trial receipt binds only the repaired blob) → `census/round-78/probes/domain-trial.sh`
  computes wall time from bash's EPOCHREALTIME and prints the W candidate blob beside the run blob
  (`amendment=none` or `<W> -> <run>`).
- 5 (carried: r76 K03/K04, status-trusting tools) → not taken; routed r79.

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=a8558d41… ahead=0 tracked=0 untracked=0`;
the watchdog log has no `lane-dead-no-report souji round=78`). No `considerthese/` directory exists in this lane;
no shokuknow theme taken (Assimilation: none).

## Measured

- C1: `controls/c1-K-a-do-nothing.txt` mismatches=12 hangs=12 [g1-g11 and t1 HANG at 75 s] EXIT=1 →
  `records/c1-after.txt` mismatches=0 hangs=0 EXIT=0 (W gate blob `b746bd9d…4eef`); K-b 14, K-c 10, K-d 11 stay
  red; `records/c1-regress-r77.txt` 16/16, `c1-regress-r76.txt` 30/30, `c1-regress-r36.txt` 21/21,
  `c1-regress-r27.txt` 4/4.
- C2: `controls/c2-K-a-no-ledger.txt` resolved=0 unresolved=22 EXIT=1 → `records/c2-after.txt` resolved=22,
  `FORGE-SUMMARY forged=12 matched=12 accepted=0`, EXIT=0; mechanical ledger 19 (`controls/c2-K-b-mechanical.txt`,
  L10 L14 L20 refused: bytes were on disk, no capture); K-c accepted=7 (r77 counter); K-d EXIT=2; K-e r78 refuses;
  `records/c2-regress-r77.txt` 35/35 and 7/7; pointer check over LOG.md missing 22 → 19
  (`records/c2-pointer-check-before.txt`, `records/c2-pointer-check-after.txt`).
- Ledger classes (19 rows + 3 captured): FLEET 5, ABSENT 6 (lost 2: L04 L05; prose 3: L07 L08 L19; removed 1:
  L17), MOVED 4, LOCAL-POLICY 2, QUARANTINED 1, TOKEN 1. The preregistration's label line groups L17 with the
  lost items; the ledger note calls it removed (the LOG line records its deletion). Both are ABSENT; the counter
  does not discriminate them.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | an anchored edit one line low (this round): the L19 note fix replaced line 19 of the ledger, which held L21, so commit L shipped two L19 rows and no L21 | `census/round-78/records/attempts/c2-at-L-duplicate-row.txt` (`resolved=21 unresolved=1 refused=1`, `LEDGER-REFUSED id=L19`, EXIT=1) | the frozen counter's duplicate-id rule (an unknown or duplicate ledger id is REFUSED) — it worked; the L1 caught it by re-running the counter before A | L2 `87d45617` restores L21 and keeps one L19; the after-arm was recorded only at L2. Rule kept: re-run the frozen counter on the committed bytes before recording any after-arm |
| M2 | a scan step that let git read an unchecked source (this round, pre-freeze): the draft include walk ran `git config --file <checked file>`, which still reads the caller's global config, so a FIFO `$HOME/.gitconfig` cost the full 45 s timeout before failing closed | scratch feasibility run `/fast/scratch/hyaku/souji-r78/L1/w-cand` (not committed: scratch); fixed before W | QUALITY Q70 (pre-freeze feasibility leg) — it worked | the walk runs with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` from `/`; rows g9/g10 refuse in 0.0 s at W (`records/c1-after.txt`) |
| M3 | a commit message miscount (this round): L's message says FLEET 6, ABSENT 7 [lost 3]; the ledger holds FLEET 5, ABSENT 6 [lost 2] | `git show -s a0f3b91f`; `census/round-78/c2-pointer-ledger.tsv` | none (commit messages are not counted) | counts in the README frontier, SCORECARD and this lesson are taken from the ledger file; the message stays as history |
| M4 | correction not swept (r77, routed by the closure): an accepted seat correction reached the row's claim column but not its anchor cell or the lesson Gate | `corpus/lessons/round-77-verifier-spotcheck.md` Routed defect 1 | PROTOCOL §Evidence standard ("Corrections sweep every mention") — the r77 L1 did not run it | this round: `grep -rn 'fstat type read' corpus/` before the rewording found SOURCES.md:280 and the round-77.md Gate line; after it, SOURCES.md no longer matches, and the remaining hits are the round-77.md Gate line (history, corrected by its appended `## Correction`), the closure's own spot-check and the quotes of the old wording in this lesson |

## Gate

- **S323 admit (A, mined)** — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config.adoc, sha256
  `a6e644cb2495df1f5e25f584e2cb7c06ec673e8b90acc52ae061a0fb6d42b2c9`, 21095 bytes, HTTP 200, accessed 2026-11-07 by
  the L1 (capture `census/round-78/srcs/git-config.adoc-v2.56.0`). Lines 99-100: "The contents of the included
  file are inserted immediately, as if they had been found at the location of the include directive." (22 words).
  Cited by `corpus/knowledge/git-discovery-sources.md` and QUALITY Q140; grounds the sourced claim C1 (rows g5-g7).
- **S324 admit (A, mined)** — https://raw.githubusercontent.com/git/git/v2.56.0/setup.c, sha256
  `8316b1ad961ac6b1fa29dfdf1094a344aec8673f6637e6c00ba913a6668fc589`, 83214 bytes, HTTP 200, accessed 2026-11-07 by
  the L1 (capture `census/round-78/srcs/git-setup.c-v2.56.0`). Lines 327-329 (get_common_dir_noenv): the commondir
  path is built, tested with file_exists and read with strbuf_read_file (12 whitespace tokens quoted in the
  row; first drafted here as "14 words", corrected per S78ScoutSources). Cited by
  `corpus/knowledge/git-discovery-sources.md` and Q140.
- **Rejected (L1): gitrepository-layout(5) at v2.56.0 as the commondir/config.worktree source** — fetched
  (`Documentation/gitrepository-layout.adoc`, sha256 `39ce8d13…9439`, 11890 bytes, HTTP 200) and read at lines
  122-150 and 268-273; it says what the files are, not that git opens them at discovery or how, and the lane
  already holds S124 for the commondir semantics. Not appended. Flip: a claim about layout rather than open
  behaviour.
- **Rejected (L1): Documentation/config/include.adoc** — HTTP 404 at v2.56.0 (the Includes text lives in
  config.adoc); nothing to admit.
- **S321 row corrected** (status unchanged `mined`, recheck unchanged `on-release`, used-by unchanged): anchor
  cell old "(the fstat type read follows at line 1169)" → new "(the fstat at line 1169 runs after open returns and
  feeds only the size and stat data, never a file-type test; …)"; scope cell old "add_patterns() open and type
  check" → new "add_patterns() open and the fstat size read that follows it" (swept after S78ScoutSources found
  the scope cell still carried the old wording).
- No other row's status, recheck or used-by cell changed. Within-scope duplicates: `git show
  a8558d41:corpus/SOURCES.md | grep -c 'config.adoc'` = 0 and `… | grep -c 'setup\.c'` = 0 before append; the
  same-proposition overlaps S78ScoutSources found (S323 with S042, S324 with S300's URL and capture) are
  different scopes, declared in the SOURCES `Round-78 provenance` line.
- **Non-L1 re-open (S78ScoutSources):** both captures re-fetched sha256-identical; S323's quote verbatim at lines
  99-100 (22 words); S324's at 327-329; both admitted. Its git-code reading (config.c handle_path_include skips a
  missing include silently; a FIFO passes access(R_OK) and is opened by a blocking fopen; validate_headref opens
  HEAD with O_RDONLY at setup.c:373; commondir is read only when it exists) corrected the knowledge entry.
  Accepted correction: the preregistration's Surface attributes the HEAD read to S324, whose quoted lines cover
  commondir only; HEAD rests on setup.c:373 read by the seat (not a row) and on rows g2/g11 measured by the
  counter. The preregistration is frozen and not amended.
- **Discernment check (S78CriticDiscern):** 19/19 ledger classes agree. Admit recorded: the `~user/` and
  `%(prefix)/` include forms S323 names are a real gap of the W gate (repaired, `--type=path`). Reject recorded:
  "L04 should be FLEET" — the round-16 build directories found under the fleet root belong to other lanes'
  repositories (kama, tsukuroi, mori), not this lane's token.

## Wave

One v1 wave, 12 seats (connector 1, scout 1, executor 3, mutation-tester 2, reviewer 1, critic 2, sentinel 1,
scribe 1; attack seats 5 of 12). Spec, dispatch, results and every seat report are mirrored byte-exact under
`census/round-78/records/wave-w1/` (seat files under `seats/`, `__pycache__` excluded). WAVE-DONE received; 0 dead
seats.

- Reproduced from committed bytes: C1 17/17 at W and the four regressions (S78ExecC1, S78Reviewer, S78MutGate,
  S78CriticClaims, S78CriticDiscern, S78Scribe); K-a 12/12 hangs on a solo serial run (S78ExecC1; a 4-way
  parallel run turned two HANG rows per run into ODD rc=-9 rows under load, mismatches unchanged); C2 22/22, 12/12,
  35/35, 7/7, K-a..K-e and the pointer check 22 → 19 (S78ExecC2, S78MutCounter, S78CriticClaims); the K captures are
  exact (disk-only 0, committed-only 0; S78ExecC2); causal separation SEPARABLE (S78Connector).
- Repaired after measurement (R `3221566c`, receipts `census/round-78/records/wave-repair/`): an includeIf
  condition with a space split the W gate's record parse and let a FIFO through (S78Reviewer HIGH); a value with a
  newline did the same (S78Sentinel MEDIUM-1); `~user/` and `%(prefix)/` include values were never checked
  (S78Reviewer, S78CriticDiscern); the include walk had no total bound and a string-keyed seen-set, so a fan-out
  tree forked without limit (S78Sentinel HIGH-1, LOW-2); scan errors were counted as non-regular files (S78Sentinel
  MEDIUM-2); the gitfile and commondir reads raced their `-f` test (S78Reviewer LOW); a FIFO loose ref hung
  check 1 and check 4 (S78CriticClaims evidence 6, S78ExecEvade route b). `repair-probes.txt` 10/10 (run 1 kept,
  `attempts/repair-probes-run1.txt`, 8/9); frozen C1 still 17/17 at R, r77 16/16, r76 30/30, r36 21/21, r27 4/4.
  The run-1 R gate (sha256 `07784129…`) was an uncommitted draft erased by a seat (M7); R was re-applied and
  committed before its receipts.
- Accepted as qualifications (not repaired): C1's hang-to-zero move is also reached by bounding every git call
  with no pre-check (S78CriticClaims variant B: hangs=0, mismatches=11 on the class token only), so what separates
  the candidate is the refusal ordering and class; K-d's hangs come from check 4's 300 s bound, not from the absent
  pre-check, and the honest control (candidate minus the check-1 timeout) reads 16/17 with t1 HANG (S78CriticClaims
  MEDIUM-3); the counter has no duration predicate, so the m13 mutant (walk without global-config isolation) passes
  17/17 while three rows take 45 s (S78MutGate HIGH; pinned outside the frozen rows by probe arm a6); the counter's
  killpg misses `timeout`'s own process group, so HANG rows leak the blocked git (S78MutGate, S78ExecC1; the L1
  reaped three such processes); a lying `check-gitsource` line passes (S78Reviewer LOW). C2: the claimed delta over
  the mechanical control is the three captures — at the after revision the generator reaches 22/22 because the
  captures exist (S78CriticClaims MEDIUM-1; the prereg's K-b is the base receipt); 9 of 22 items are byte-verified,
  the rest existence, absence or source text (S78CriticClaims MEDIUM-2); four counter mutants survive every frozen
  artifact (MOVED basename, QUARANTINED fleet refusal, template literal, forge match rule; S78MutCounter) and five
  false single rows pass (one TOKEN target of a range, a range endpoint outside the span, MOVED for a token with
  no round, a wrong quarantine leaf, a TOKEN prefix of the wrapped continuation; S78MutCounter NF1-NF5).
- The append-only LOG.md correction the preregistration names as claimed work landed at I `bbd199da`, after the
  after-arm A (S78CriticClaims HIGH-1 and S78CriticDiscern HIGH read LOG.md at A); no counted number depends on it
  (R0 reads the base blob).
- Out of surface (stated limits, now evidenced): FIFO `objects/info/alternates` and `shallow` hang W (S78ExecEvade
  routes a, c; R does not check them either, untested on R); remote-side FIFOs (HEAD, packed-refs, loose ref, include) are bounded by check 1's
  timeout to about 45 s (S78ExecEvade k-k5); SIGTERM leaves the git child for at most its own timeout (S78Sentinel
  MEDIUM-3); other lane tools that run git (receipt writer, pointer and freeze checks, landing gate) carry no scan
  (S78Connector HIGH/MEDIUM).
- Sibling overlap (S78Connector, report only; `census/round-78/records/wave-w1/seats/S78Connector/sibling-overlap.tsv`):
  10 sibling gates run git with no discovery-source guard (6 of them with no timeout either); 17 siblings' LOG.md
  files cite `.ufo/waves` paths that are not committed.

## Mistakes (wave)

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M5 | a repair-probe expectation written before observing the W arm (this round, repeat of r77 M5): the diamond arm expected W HANG; W passed in 13.3 s because its depth cap bounds that size | `census/round-78/records/wave-repair/attempts/repair-probes-run1.txt` (8 of 9, EXIT=1) | the probe's computed verdict | relabelled to the observed W verdict with a comment pointing at run 1; the fan-out bound is pinned by the separate wide arm (W PASS, R SCAN) |
| M6 | a frozen counter without a duration predicate (pre-freeze, this round): a refusal that takes 45 s instead of 0 s matches the same row | S78MutGate survivor m13 | none (Q70 feasibility saw the 45 s draft but the population carries no time bound) | probe arm a6 requires R to refuse within 5 s; a frozen time bound is routed to r79 |
| M7 | a seat wrote a lane tracked file (this round): S78ExecC1 ran `git restore` on the gate, erasing the L1's uncommitted repair; the L1's first repair receipts were recorded from the restored W bytes and discarded | `census/round-78/records/wave-w1/seats/S78ExecC1.md` item 7 | the L1's digest check before trusting a receipt (the gate copy hashed to the W blob) | receipts deleted before commit; the L1 messaged the seat; the repair was re-applied and committed (R) before any receipt; rule kept: commit a repair before recording against it |

## Routed to round 79

- (a) C1 instrument successor: a per-row duration bound (m13), process-group cleanup that also kills `timeout`'s
  group, an exact `check-gitsource` line assertion, rows for the repair arms (space subsection, newline value,
  `~user/`, loose ref, fan-out) and for `objects/info/alternates` and `shallow`.
- (b) SIGTERM: a TERM/EXIT trap with git calls run as background jobs so `wait` is interruptible.
- (c) C2 instrument successor: MOVED binding for tokens without a round, range span binding, every-target TOKEN,
  quarantine leaf binding, an expect=MISMATCH forgery row (S78MutCounter M02/M04/M07/M09, NF1-NF5).
- (d) carried: r76 K03/K04; the status-trusting and unguarded lane tools (receipt writer, pointer and freeze
  checks, landing gate, `souji-verify.sh:550,594`, `souji-census.sh`).
