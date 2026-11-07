# Round 77 — an exclude source that is not a file (C1 operability), every self-assessment pointer resolves to verified bytes (C2 calibration)

Attempt 1 (`SoujiR77`). Lane base `d4f515637884695b3aa016da169d859d3ece6ac4` (r76 admitted, spot-check committed).
Staged commits in the order the preregistration binds: P `43822328ec27b429b68c21d9c3a995e0a09b9d77` (counters,
populations, control variants, every control receipt, S321/S322 captures, census-before); F
`a9979807fd5d9f80851c0f1fc6481e9bf0334644` (preregistration, Q99 grammar; freeze-check `--substance --chronology`
`SUMMARY claims=2 findings=0`, `census/round-77/records/freeze-check-at-F.txt`); W
`9b496b0883b255573175726f1463ce5634960a04` (C1 candidate gate); K `6690cb5ad96d11a7b528a62a98ba42fad7783d35` (C2
capture); L `8bf42fc6233cc4fee28c170d57e5d38a80f6d2bc` (C2 ledger); A `ef04ca6c66af02b98bc061290b8028c6c0654a4b`
(after-arms). Frozen claims, counters and predicates are in `census/round-77/preregistration.txt` and are not
restated here.

## Inherited

The r76 spot-check routed five defects (`corpus/lessons/round-76-verifier-spotcheck.md`, Routed defects):

- 1 (domain-trial receipt binds no digest of the trial script) → `census/round-77/probes/domain-trial.sh` must be
  run at its committed path (it refuses any other) and its receipt prints `trial_script=… sha256=…` and the blob
  digest at master (`census/round-77/records/c1-domain-trial.txt`).
- 2 (the trial graded report bytes that differ from the filed report) → the trial receipt prints
  `report_lines=N report_sha256=…` of the graded bytes; a verifier re-derives them as `head -n N <filed report> |
  sha256sum`, so lines added after the trial are visible, not hidden.
- 3 (kill power of the frozen instruments: M09; K03/K04; filename-separable C2 population) → M09 killed by frozen
  rows o1-o2 (`controls/c1-K-c-m09-one-path.txt`, o1 o2 PASS under the mutant). K03/K04 and the r76 C2 population
  were not taken this round (routed r78).
- 4 (S76Sentinel MEDIUM-2: a FIFO `.gitignore`/`core.excludesFile` hangs the gate) → C1. The r75 routed defect 2
  (core.excludesFile arm discrimination) → partly: rows n4 (FIFO excludesFile, NONREG class), o3 (regular
  excludesFile hiding one path, the writer's pinned-status class) and p2 (regular excludesFile matching nothing,
  PASS) separate the three arms by class; the gate's own `RECEIPT-UNTRACKED-LOCAL-EXCLUDE` arm for an excludesFile
  is still shadowed by the writer's pinned status (o3).
- 5 (sibling `.jj/.gitignore` note) → report only; not souji's to fix.

r76 lesson `## Routed to round 77`: (a) taken as C1; (b) not taken (routed r78); (c) the status-trusting tools
`tools/souji-verify.sh:550,594` and `souji-census.sh` not taken (routed r78).

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=d4f51563… ahead=0 tracked=0 untracked=0`;
the fleet watchdog log has no `lane-dead-no-report souji round=77`). No `considerthese/` directory exists in this
lane; no shokuknow theme taken (Assimilation: none).

## Measured

- C1: `controls/c1-K-a-do-nothing.txt` mismatches=9 hangs=8 [n1-n7 n10 HANG at 30 s; n8 PASS] EXIT=1 →
  `records/c1-after.txt` mismatches=0 hangs=0 EXIT=0; K-b 7, K-c 11, K-d 7 stay red; `records/c1-regress-r76.txt`
  30/30, `c1-regress-r36.txt` 21/21, `c1-regress-r27.txt` 4/4.
- C2: `controls/c2-K-a-no-ledger.txt` resolved=0 unresolved=35 EXIT=1 → `records/c2-after.txt` resolved=35 EXIT=0;
  K-b refused 31, K-c refused 4, K-d mismatched 4, K-e refused 3, all EXIT=1; pointer check missing 35 → 31
  (`records/c2-pointer-check-after.txt`).
- Hang rows versus the policy row are counted apart: 8 rows hung the lane-base gate; n8 is refused by ruling (git
  never opens a `.gitignore` inside an ignored directory; the base gate passes it in 0.1 s).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | self-assessment rows citing evidence that exists only on one host's disk (rounds 32-64): 14 base pointers name `.ufo/waves/…` paths under the committed ignore rule `.ufo/waves/`, never committed; 4 of them had no committed copy at all | `census/round-77/c2-population.tsv` P04-P35 rows with an `f:`/`d:` digest; `controls/c2-K-a-no-ledger.txt` | none: `tools/souji-pointer-check.py` exists since r70 but no landing step runs it over SCORECARD/SKILL/QUALITY/README/PROVINCE | captured at the cited paths (K `6690cb5a`) and a verified ledger (L `8bf42fc6`); QUALITY Q139; the counter can fail: K-a unresolved=35, K-c refused 4, K-d mismatched 4 |
| M2 | an instrument rule accepting a weaker class than the truth (this round, pre-freeze): the first C2 counter let ABSENT stand for parse-artefact tokens, so a blanket-ABSENT ledger resolved 10 of 35; its range rule also rejected a true `D1..D5` expansion | L1 session, pre-freeze feasibility in `/fast/scratch/hyaku/souji-r77/L1/c2/` (not committed: scratch) | QUALITY Q70 (pre-freeze feasibility leg) — it worked | both rules fixed before P; the committed blanket control reads resolved=4 (P02 P03 P14 P24, true absences), the six TOKEN items refused under ABSENT (`controls/c2-K-b-blanket-absent.txt`) |
| M3 | a population label chosen without the base observation (this round, pre-freeze): the first C1 draft ruled a FIFO `.gitmodules` (n9) FAIL and gave o3 the gate's own class; the base run showed git never opens that `.gitmodules` (PASS in 0.2 s) and that the writer's pinned status refuses o3 first | first base run in `/fast/scratch/hyaku/souji-r77/L1/w-base` (scratch); final population `census/round-77/c1-population.tsv` | QUALITY Q70 feasibility | n9 dropped and o3 relabelled before P; the remaining policy row n8 is ruled in the preregistration and counted apart from the hang rows |
| M4 | a receipt recorded with a missing `--work` directory (this round): the first r36 regression receipt ended in `FileNotFoundError`, EXIT=1 | `census/round-77/records/attempts/c1-regress-r36-attempt1-missing-workdir.txt` | the receipt's own EXIT line (rec.sh records the failure, it does not hide it) | re-recorded with the directory created (`records/c1-regress-r36.txt` 21/21 EXIT=0); the failed receipt is kept |

## Gate

- **S321 admit (A, mined)** — https://raw.githubusercontent.com/git/git/v2.56.0/dir.c, sha256
  `53e5ed2b3b65409331021ec0075d9405fdd690598ba96cc5ec8077c03b6220a6`, 115474 bytes, HTTP 200, accessed 2026-11-07 by
  the L1 (capture `census/round-77/srcs/git-dir.c-v2.56.0`). Lines 1164-1167: "if (flags & PATTERN_NOFOLLOW) fd =
  open_nofollow(fname, O_RDONLY); else fd = open(fname, O_RDONLY);" (13 words); the fstat type read follows at line
  1169. Cited by `corpus/knowledge/filter-filemode-witness.md` r77 and QUALITY Q138; grounds the sourced claim C1.
- **S322 admit (A, mined)** — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-add.adoc, sha256
  `42089b80b378a7e9711dde024b7ec94a6863378164ea434a34c6af07632e65db`, 16586 bytes, HTTP 200, accessed 2026-11-07 by
  the L1 (capture `census/round-77/srcs/git-add.adoc-v2.56.0`). Line 78: "Allow adding otherwise ignored files." (5
  words). Cited by `corpus/knowledge/self-assessment-pointer-resolution.md`.
- **Rejected anchor (L1, carries pipes)** — dir.c line 1169 "if (fd < 0 || fstat(fd, &st) < 0) {": the census
  parser counts the `||` as cell separators (E01 `S321 fields=13` in a scratch validate), so it is paraphrased in
  the row's claim column, not quoted.
- No existing row's status, recheck or used-by cell changed. Within-scope duplicates: `git show
  d4f51563:corpus/SOURCES.md | grep -c 'dir\.c'` = 1 (a mention inside S319's text, no dir.c row) and `… | grep -c
  'git-add'` = 0.
- **S77ScoutSources (non-L1 re-open):** both captures sha256-identical to its own fetch and to a v2.56.0 clone;
  S321's quote verbatim at lines 1164-1167 (13 words); S322's at line 78 (5 words); both admitted, no duplicate.
  Accepted corrections (applied to the rows before landing): add_patterns never tests the file type — fstat feeds
  the size only (LOW); S322's "knows" cell first attributed jj's `file track --include-ignored` to git-add(1)
  (MEDIUM) and now names jj's own help for the helper and git-add(1) only for git. Noted, not changed: S064's
  line anchors drift at v2.56.0 (`read_attr_from_file` :693-733, `bootstrap_attr_stack` :910-948) — routed r78.

## Wave

One v1 wave, 12 seats (connector 1, scout 1, executor 3, mutation-tester 2, reviewer 1, critic 2, sentinel 1,
scribe 1; attack seats 5 of 12). Seat reports are mirrored byte-exact under `census/round-77/records/wave-w1/seats/`.
WAVE-DONE received; 0 dead seats.

- Reproduced from committed bytes: every frozen number (S77ExecC1, S77ExecC2, S77Reviewer, S77CriticClaims,
  S77CriticDiscern, S77MutGate and S77MutCounter baselines, S77Scribe).
- Repaired after measurement (`844b2d70`, receipts `records/wave-repair/`): common-dir info files, symlink by
  target, scan failure fails closed, `/dev/null`, index and sparse-checkout, timed pre-check calls, fsmonitor off
  in status. `repair-probes.txt` 10/10; frozen counters still 0 at the repair.
- Accepted as qualifications (not repaired): C1's before count 9 = 8 hang rows + the n8 policy row; the 300 s
  backstop and the XDG/relative-path branches have no frozen row (S77MutGate F1-F3 survivors; probe arms
  xdg/relative/fsmonitor now cover them outside the frozen counter); o1-o3/p1-p4 are anti-mutant guards, not
  evidence of change (S77CriticClaims). C2: 31 of 35 items resolve with no new byte and a mechanical 30-line
  ledger generator reaches 35/35 (S77CriticClaims MEDIUM "thin"); 17 items are verified by bytes, 18 by
  existence/absence/parse (S77CriticDiscern); the frozen counter's controls are aggregate-red, so 9 of 10
  counter mutants survive them and six forged single rows pass (S77MutCounter HIGH-1..3: QUARANTINED target
  unbound, TOKEN prefix-only, MOVED location-free, R0 unexercised); P15/P16 rest on empty-directory digests and
  stop resolving at the lane's next quarantine.
- Out of surface (stated limit, now evidenced): FIFO `.git/config`, `include.path`, `HEAD`, `packed-refs`,
  `config.worktree` hang check 1 before the pre-check (S77ExecEvade, S77Sentinel MEDIUM-2); SIGTERM leaves
  check-4 children alive (S77Sentinel MEDIUM-3).
- Seat mishap (self-reported, S77Sentinel): one probe script briefly landed at the fleet root under
  `.ufo/waves/round-77/w1/S77Sentinel/` (dead: removed by the seat) and was removed the same minute; the misroot sweep finds nothing.
- Sibling overlap (S77Connector, report only): kaidoku and tabi pre-report gates call `git status` with neither
  guard nor timeout; every sampled sibling self-assessment cites uncommitted `.ufo/waves` paths.

## Mistakes (wave)

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M5 | a repair-probe expectation written before observing the W arm (this round): the unreadable-directory arm expected W PASS; git status lists the unreadable untracked directory, so W fails through status | `census/round-77/records/wave-repair/attempts/repair-probes-run1.txt` (`as_expected=8` of 9, EXIT=1) | the probe's computed verdict (exit 1) | arm relabelled to the observed W verdict with a comment pointing at run 1, and a fail-open arm added under a tracked ignore rule (W PASS, R SCAN) — `repair-probes.txt` 10/10 |
| M6 | a guard scoped to the per-worktree git dir while git reads the common dir (this round): W checked `--absolute-git-dir/info/exclude` | S77Reviewer MEDIUM-1, S77Sentinel MEDIUM-1 | none in the frozen 16 rows (all fixtures are non-linked) | `rev-parse --git-path`; arm commondir-info-exclude W TIMEOUT / R NONREG |

## Routed to round 78

- (a) C2 instrument successor: per-row expected verdicts for forged ledgers (S77MutCounter G1-G6), QUARANTINED
  target bound to the token, TOKEN targets bound to the sentence's named revision/template, R0 exercised and the
  population digest pinned; a do-nothing control at the mechanical-ledger ceiling (31/35).
- (b) gate: checks 1-3 and the pre-check under one timeout or a pre-check of `.git/config`/`HEAD`/
  `packed-refs`/includes; a TERM/EXIT trap killing the group; frozen rows for XDG, relative path and the backstop.
- (c) carried: r76 C2 binding counter K03/K04 and name-swapped cases; `tools/souji-verify.sh:550,594`,
  `souji-census.sh`, `souji-receipt-write.py` status/ls-files calls without guard or timeout (S77Connector);
  S064 line anchors; empty-quarantine digests P15/P16.
