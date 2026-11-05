# Round 65 — two frozen claims, one post-freeze wave

Base `4a43a4d919c5b51ae9be859a1266ce4b11337b0b` (lane master at round start, clean, pushed). Attempt 1.
Chronology: instruments `2761f0aa`, controls `3c5bfdc0`, freeze `d2850b3e` (`census/round-65/preregistration.txt`),
landing `022cf979` → S2-literal wrap fix `40a371d8` (first measured rev), docstring-only key-scope fix `af81553f`
(final measured rev for C1/C2), chronology arm `16da2445` (landed after the freeze, see M1).

## Claim

Frozen at `census/round-65/preregistration.txt`; predicates are the sentences in that file and are not amended here.

- **C1, operability.** The receipt writer refuses (a) untracked-visibility concealment of the
  `status.showUntrackedFiles` KEY, (b) an in-run mode-only flip under `--allow-dirty`, (c) an in-run symlink
  retarget inside an untracked directory, and (d) a caller-set `GIT_INDEX_FILE` naming a nonexistent path.
  Target: `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0
  regress=PASS`, `EXIT=0`. Do-nothing (base bytes): `new_forgeries=12`, `EXIT=1`.
- **C2, calibration (lowest owned axis, score 7).** Four SKILL.md statements about the writer agree with its
  bytes under a live-marker (anchored) read. Target: `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0`.
  Do-nothing: `findings=2`, `EXIT=1`.

The C1 frozen predicate is scoped to the status KEY. The ignore routes (`core.excludesFile`, `.git/info/exclude`,
tracked `.gitignore`) and `GIT_CONFIG_*` passthrough for other keys are outside it and are named limits below.

Measured revision for both after receipts: `af81553f23086e3fa7556d552a0d26d4a995c216`. The C1 counter,
C2 counter and writer selftest (30/30) were re-run there after a docstring-only change; the writer's
behaviour bytes are unchanged from `40a371d8` (`git diff -U0` shows only the docstring lines 46–49).

## Gate

Source opened this round: git-config(1) `status.showUntrackedFiles`, https://git-scm.com/docs/git-config,
accessed 2026-11-05, HTTP 200, 830605 bytes, sha256 `37aa8407…9226` (fetched by two clients, byte-identical).
Captures and offset proofs are committed at `census/round-65/sources/` (`s297-git-config.html`,
`s297-git-config.txt`, `s297-git-config.man.txt`, `s297-located-quote.txt`, the recipes, `probe-log.txt`).

- **ADMIT (S297)** — `no - Show no untracked files.` (6 words, text offset 299360, slice assertion PASSED;
  byte-contiguous in the man carrier at 330781) and `all - Show also individual files in untracked directories.`
  (9 words, text offset 299437, PASSED). Reason: the page states what each value of the key displays; the
  V1 row exercises exactly the `no` value, and the V2 row the clean-tree polarity.
- **ADMIT (S297, primary)** — `So, this variable controls how the commands display the untracked files.`
  (11 words, text offset 299266, PASSED; not byte-contiguous in raw HTML — recorded in the registry row).
- **REJECT** — "a receipt writer must override `status.showUntrackedFiles`": the page assigns no duty to any
  consumer; the override is this lane's design. Flip: a git(1)/git-config sentence assigning that duty.
- **REJECT** — "`status.showUntrackedFiles=all` makes every untracked file visible": the page scopes `all` to
  files in untracked directories and says nothing about ignored paths; the measured `core.excludesFile` arm
  (sentinel F1, scribe arm B–E) shows ignored paths stay hidden. Flip: a page sentence stating that `all`
  surfaces ignored paths.
- **REJECT** — "an operator-injected config cannot hide untracked entries from a receipt writer's dirty check"
  as a GENERAL rule: false on the measured ignore-route arms; the page documents one key only. Flip: a sentence
  making the key the only switch governing untracked visibility.
- **REJECT (routed, not adopted)** — the `:(top)` code-kind row for `pathspec.c` (operator L0 still open).
- **Frontier step:** S297 is opened this round and cited by the knowledge entry
  `corpus/knowledge/untracked-visibility-concealment.md` (`source: S297`, `verified-at: af81553f…`, `status: mined`).
  S291's `used-by` gained the new entry path (old → new: `corpus/knowledge/skip-worktree-concealment.md` →
  `corpus/knowledge/skip-worktree-concealment.md, corpus/knowledge/untracked-visibility-concealment.md`), logged
  here as the required old→new record. `scripts/sources-census.sh validate --root <fleet> souji` → exit 0, 219 → 220 rows.
- **Assimilation: none.** `considerthese/` does not exist in this lane (`test -e` exit 1, connector seat
  `S65ConnectorOverlap`). `shokuknow/merge/souji/MERGE-REPORT.md` read read-only: one adjacent theme
  (`fleet-config-scope-resolved-r26`) named, not adopted; its id state (108 rows, first id S109) is stale against
  this registry (219 rows), so staged ids would collide. Nothing was run in shokuknow.
- **Non-author spot-check:** pending. The closure reviewer samples the ADMIT offsets against the committed capture
  and one REJECT flip against the page bytes.

## Wave evidence (w1, 9 seats, policy v1 band 8–16)

Seats: `S65ExecScore` (executor, clean-clone reproduction), `S65MutKill` (mutation-tester), `S65ReviewerDesign`,
`S65ReviewerC2` (reviewer ×2), `S65CriticClaims` (critic), `S65SentinelScope` (sentinel), `S65ScoutSources`
(scout), `S65ScribeEntry` (scribe), `S65ConnectorOverlap` (connector). Attack share 5/9 (≥25%). Planner seat held by
the L1 (validator refuses planner). Deliver dirs under `.ufo/waves/round-65/w1/`. Dispatch manifest
`w1-dispatch.json`, spec `w1-spec.json` (regenerated by `make-spec.py`). Wave directories are gitignored (`.ufo/waves/`); the seat outputs are committed as a durable mirror at `census/round-65/wave/w1/` (pointers in this lesson use that path where they name seat outputs).

Independent reproduction (`S65ExecScore`, clean `git clone --shared`, rev `16da2445` = tip before the docstring
fix): C1 `SUMMARY matrix=19 … new_forgeries=0 … regress=PASS` EXIT=0; C2 `findings=0 verdict=PASS` EXIT=0; writer
selftest 30/30; C1 selftest 8/8; C2 selftest 13/13; regress r60 `pass=8 fail=0`; default-mode freeze-check
output byte-identical to the pre-round bytes over 34 preregistrations. Sentinel and scribe reproduced the
same C1/C2 numbers independently.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | Post-freeze landing miss: the freeze-check `--chronology` candidate was validated at `.ufo/waves/round-64/w1/S64ExecFreeze/` and listed as "to land"; the instruments commit `2761f0aa` carried only `census/round-65/**`, so the production `tools/souji-freeze-check.py` was unchanged through the freeze. The arm reached the tree at `16da2445`, after `d2850b3e`. The first chronology selftest run failed (`unrecognized arguments: --chronology`), which is how the miss surfaced. | `git show 2761f0aa --stat` (no `tools/` path); `git show 2761f0aa:tools/souji-freeze-check.py \| grep -c chronology` → 4 (the r61 arm only); `census/round-65/records/freeze-check-selftest-chronology.txt`; scribe `S65ScribeEntry.md` Finding 2 | none — no checklist step compared the landed bytes to the candidate before freeze | Q125 (landing steps compare `git show <rev>:<path>` to the candidate sha and check `--stat`). The arm is landed (`16da2445`, selftest 52/52). Disclosed: the freeze commit was checked with the default and `--substance` arms only. |
| M2 | Pre-freeze probe ordering error: the first N2 probe created the untracked file BEFORE the writer launched, so the in-run shape was never exercised; both arms read as "accept" and looked like a polarity pair. Re-run with the file created in-run, and the pre-run polarity arm kept. | `census/round-65/probes/n4-n2-dispute-results.txt` (fixed run; the superseded run's output was overwritten) | the probe's output read as confirmation without a per-arm expected verdict | probe arms carry an expected verdict and a mismatch exits non-zero; both N2 shapes now have in-run and pre-run arms |
| M3 | C2 after-literal wrapped across a source line in `SKILL.md`: the first landing (`022cf979`) reported `GOVERNED-STATEMENT-UNRESOLVED s2` and the first after receipt was FAIL. Fixed in `40a371d8`; the after receipt re-taken there. The substring design makes a wrapped literal a silent FAIL, not a parse error. | `census/round-65/records/c2-after.txt` at `022cf979` (superseded) and at `40a371d8` (PASS) | the counter's substring rule; no landing check greps each after-literal at the landed rev | a landing check greps each after-literal byte-contiguously before the receipt is taken (named limit of the substring design) |
| M4 | Scribe draft cited wrong offsets: `no - Show no untracked files.` at "text 322916" and "all …" at "text 323005", plus raw HTML 762518. The scout's slice assertions give text 299360 and 299437, and HTML 762618 bytes (the 762518 figure is a character offset in the decoded string, not a byte offset). The scribe's draft was corrected to the scout's asserted offsets before landing. | `S65ScribeEntry.md` Finding 3 and §9; `census/round-65/sources/s297-located-quote.txt`; committed knowledge entry Gate block | the scribe's offsets had no slice assertion; the L1 did not re-run one before landing | rule: every offset in a Gate block is a slice assertion against the committed capture, re-run at landing (done for S297: text 299266/299360/299437, man 330781/330890) |
| M5 | Landed writer docstring overclaimed: "an operator-injected config cannot hide untracked entries from the dirty check". The sentinel (F1, HIGH) and the scribe (arms B, C, E accept on both slots) measured the ignore routes and a `GIT_CONFIG_COUNT` `core.excludesFile` route as live bypasses. The frozen V1 row is key-scoped, so C1's counts were unaffected, but the header was a calibration defect on C2's axis. Fixed by a docstring-only correction at `af81553f` (diff: lines 46–49 only); C1 and C2 re-measured there. The behaviour fix (`GIT_CONFIG_*` isolation, ignore-source pinning) is NOT made this round. | `git diff -U0 40a371d8..af81553f -- tools/souji-receipt-write.py`; `census/round-65/records/c1-after-af81553f.txt`; `census/round-65/records/c2-after-af81553f.txt`; `S65SentinelScope.md` F1; `S65ScribeEntry.md` Finding 1 | the frozen predicate's key scope did not cover the docstring sentence; C2's population does not include the writer header | wording corrected (done); behaviour route routed to round 66 as its own claim with a do-nothing control |
| M6 | S291 `used-by` ordering: the new knowledge entry cites S291, so the S291 row's `used-by` had to name the new path in the same landing (the K1-style check fires in the other direction otherwise). Fixed in the same registry commit as the new row. | `corpus/SOURCES.md` row S291 (old → new as recorded in `## Gate`) | the L1 relied on the scout's integration note, not on a check | the registry and its knowledge entry land in one commit (done, `a3f98054`) |
| M7 | Frozen preregistration states a false chronology: its preamble says `tools/souji-freeze-check.py --chronology` "landed pre-freeze" and that the selftest "stays … 52/52 with --chronology". At the freeze `d2850b3e` the CLI arm is absent (`git show d2850b3e:tools/souji-freeze-check.py \| grep -c -- '--chronology'` → 0; the freeze-check selftest there is 41/41). The prereg is frozen and is not amended. | `census/round-65/preregistration.txt` preamble; `w1/S65CriticClaims.md` §1 H1, evidence `w1/S65CriticClaims/freeze-check-selftest-at-freeze.txt` | the freeze-record checker verifies controls and `After:` bytes, not the prose claims about other tools | erratum below (append-only, R65-ERRATUM-PREREG). Predicates unaffected: no Target or Kill line depends on the chronology arm. Q125 applies. |
| M8 | Q59 axis instrument refused: `python3 tools/souji-axis-check.py --prereg census/round-65/preregistration.txt --scorecard SCORECARD.md` → `refused: no ## MACHINE BLOCK ... END section found`, rc 2. The round-64 prereg has none either. The L1 scored the axis by hand, which Q59 does not allow. | `w1/S65CriticClaims.md` §4 H2 | the L1 did not run the Q59 instrument before freeze | disclosed; the MACHINE BLOCK requirement is the operator's open L0 (existing, rounds 63–64). Routed round 66 with a MACHINE BLOCK added to the next preregistration only. |
| M9 | C2 after-wording overclaims S3: "a flag set, or a file edited, while the wrapped command runs is refused with `RECEIPT-STATE-CHANGED-DURING-RUN`". Matrix row T4 (edit then exact restore) is accepted by design, and a gitignored file edited in-run is accepted (critic probe `ign-receipt-inrun-gitignored.txt`). C2 passes it because the marker is present; C2 calibrates marker presence, not statement breadth. | SKILL.md round-62 writer-rule sentence (line 840) carrying the frozen `S3_AFTER` literal; `census/round-65/records/c1-after-af81553f.txt` row T4; `w1/S65CriticClaims.md` §6 H3 | C2's population checks marker presence in both directions, not whether an enumerated class is complete | the frozen literal is not amended. Named limit below states the qualification; round 66 adds a C2 row that pins the qualifier ("exact restore", "tracked") with its own control. |
| M10 | C2 live-marker read fooled by a substring: the emission token `return` matches `returncode` in the writer's own selftest line (landed writer, `returncode` at the selftest's `r.returncode != 2`), so the env needle reads live from a test line. Mutant m4 (env refusal deleted outright) gives C2 `findings=0`; C1 kills it (N3, P13). The frozen predicate reads `return` literally, so the counter did what its predicate says; the predicate word is too loose. | `w1/S65MutKill.md` §4 (HIGH); `w1/S65MutKill/c2-polarity.txt`; the frozen counter's `EMISSION_TOKENS` | the C2 selftest did not include a deleted-refusal mutant; the dead-token falsifier covers comments and literals only | C2 verifies on its frozen predicate and is reported with this HIGH kill-power gap; the claim's calibration verdict is left to the closure judge. Round 66: match `return` as a statement token, add a deleted-refusal row, re-pin. |
| M11 | C1 matrix misses a same-content symlink retarget: SY2 retargets to `../instr.sh` (bytes differ), so a read-through symlink hasher (mutant m3) also refuses. A same-content retarget (`../copy.txt`, identical bytes) is accepted by m3 and refused by the landed writer (probe `w1/S65MutKill/mutants/m3probe.sh`). | `w1/S65MutKill.md` §2 and §3 (HIGH); `w1/S65MutKill/m3probe-landed.out`, `m3probe-m3.out` | the matrix's SY2 target was chosen without a same-content variant | C1 verifies on its frozen matrix; the kill-power gap is recorded. Round 66: add a same-content retarget row with a do-nothing control. |
| M12 | Mode claim overstated: the snapshot records `oct(st_mode & 0o777)`, so setuid, setgid and sticky bits are invisible. `755 → 4755` and `644 → 4644` are accepted (rc 0). Git does not track those bits either, so porcelain is blind too. Q126 said "a mode-only in-run change refuses", which is false for those bits. The four frozen arms (0600, 0444, 0755, 4755 from 644) do refuse. | `w1/S65MutKill.md` §5 (HIGH); `w1/S65MutKill/mode-matrix.txt`, `mode-setuid-from755-to4755.out`; `_snapshot_entry` mask | the mode claim was scoped by the arms actually run (permission bits) and the wording generalised past them | Q126 wording corrected in this round to the permission-bit scope (non-frozen QUALITY). Setuid/setgid/sticky rows routed to round 66 with a do-nothing control. |

Sweep for mistakes (round end): `git log --oneline 4a43a4d9..16da2445 -- tools/souji-freeze-check.py` shows the
arm's only landing (`16da2445`), confirming M1. `grep -c 'RECEIPT-INDEX-UNMERGED' SKILL.md` → the s4 clause is
present at the tip. `git diff -U0 40a371d8..af81553f -- tools/souji-receipt-write.py` → docstring lines only (M5).

## Named limits (carried as observed; none claimed as admitted)

- **C1, env redirects.** Only `GIT_INDEX_FILE` is refused. `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`
  and `GIT_REPLACE_REF_BASE` are unread.
- **C1, `GIT_CONFIG_*` passthrough (sentinel F1, HIGH; outside the frozen matrix).** The writer's `git()` passes
  `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_GLOBAL` and
  `HOME` through. The `-c status.showUntrackedFiles=all` override outranks an injected value for THAT key (measured),
  so the frozen V1 row is not forged. For other keys, the route is live: an injected `core.excludesFile` makes an
  untracked file ignored, the writer accepts (rc 0), and the base writer accepts too. Probes:
  `census/round-65/wave/w1/S65SentinelScope/` (`probe-env-config.sh`, `probe-replace-excludes.sh`, outputs in
  `probe-env-output.txt`). Smallest remediation (sentinel): set `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`,
  refuse `GIT_CONFIG_COUNT`/`GIT_CONFIG_PARAMETERS`/`GIT_CONFIG_KEY_*` presence, pin `-c core.excludesFile=/dev/null`.
- **C1, ignore routes (sentinel F2 MEDIUM; scribe arms C–E).** A repo-local `.git/info/exclude`, `core.excludesFile`
  or a tracked `.gitignore` hides an untracked file from every status read; the writer accepts on both slots.
  The writer's dirty check is a status check; ignored content is outside it by design.
- **C1, refs/replace (sentinel F3 MEDIUM; requires `--allow-dirty` and write access to `refs/replace`).** A replace
  ref on the instrument blob makes the worktree-vs-committed check read the replacement; the receipt records the
  replacement's digest (`aea35bbe…`) against committed blob `8f513b9f…`. The base-slot outcome was not measured.
  Remediation: `GIT_NO_REPLACE_OBJECTS=1` on the reads.
- **C1, secret-shaped echo (sentinel F4 MEDIUM, r21 privacy boundary).** `RECEIPT-INDEX-ENV-SET` prints the env value
  verbatim (`repr(os.environ['GIT_INDEX_FILE'])`), with no Q49 pattern filter and no bound (a 300-character probe
  path produced 497 bytes of stderr). The value is a path today, not a secret. Preferred remediation: name the
  variable, never its value.
- **Counter excerpt bound (sentinel F5 LOW).** `one_line(text, limit=160)` caps each slot's stderr per slot, so a
  `# detail` line can reach 417 characters. The Q49 wording "whole reason bounded to 160 bytes" is not what the counter does.
- **Fixture host config (sentinel F6 LOW).** `clean_env` does not isolate `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM`;
  fixture git calls read the host's `~/.config/git/config`. No hook execution observed (no `core.hooksPath`).
- **`--receipt` / `--out` unconfined (sentinel F7 LOW, by design).** Caller-chosen paths; records are committed under `census/`.
- **C2, lexical liveness.** A needle on a line that also carries `refuse(`/`return` counts live even if an
  `if False:` guard disables it. That reachability is the C1 matrix's job, not C2's.
- **Ignored files are not untracked.** The writer's dirty check says nothing about ignored content (scribe).
- **Chronology arm landed post-freeze (M1).** The freeze commit was checked with the default and `--substance` arms.
- **Scout fixture shape.** Probes ran on git 2.56.0 on this host, one committed file, one untracked file, one
  untracked directory. Sparse checkout, submodules, worktrees and `GIT_WORK_TREE` were not probed.

## Routed to round 66

1. **Behaviour fix for the ignore and config routes (sentinel F1–F3, scribe arms B–E)** as its own frozen claim with a
   do-nothing control that accepts the route on the base and must refuse on the candidate; include the
   `GIT_CONFIG_*` refusal and the `refs/replace` read (`GIT_NO_REPLACE_OBJECTS=1`). Candidate matrix rows for the
   ignore routes so the general claim gets its own predicate.
2. **Redaction of the env value in `RECEIPT-INDEX-ENV-SET` (sentinel F4)**, and the Q49 wording on the counter's
   excerpt bound (F5), each with a control.
3. **Fixture isolation of `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` in `clean_env` (F6).**
4. **Operator L0 (open):** `:(top)` code-kind registry row (`pathspec.c` `parse_long_magic`, S296 named limit).
5. **Env redirects** (`GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE`), as their own
   claim with a do-nothing control (round-64 connector item 9).
6. **Dead-token falsifier for the writer's own refusal lines** (the `if False:` shape), per the C1 kill plan.

## Remaining wave items

Seat findings still arriving at round close (mutation kill matrix, reviewer design and C2 attacks, critic
falsification, polarity sweep) are recorded in the report's Named limits and the next round's routing when the
wave settles; any severity C/H item that contradicts a filed assertion is added to this table before the report
lands (Q121).

## Erratum (append-only; wave close)

R65-ERRATUM-PREREG: `census/round-65/preregistration.txt` (freeze `d2850b3e`) states that
`tools/souji-freeze-check.py --chronology` "landed pre-freeze" and that its selftest "stays … 52/52 with --chronology".
Both sentences are false at the freeze commit: the `--chronology` arm first exists at `16da2445`, and the freeze-check selftest at
`d2850b3e` is 41/41 (`w1/S65CriticClaims/freeze-check-selftest-at-freeze.txt`). The prereg bytes are unchanged; no Target,
Kill, counter or matrix line depends on the arm. Recorded as M7. The same correction is appended to `SCORECARD.md`.

## Named limits added at wave close

- **C2 kill-power (M10, HIGH).** The frozen emission token `return` matches `returncode`; a deleted env refusal (mutant m4) gives `findings=0`. C1 catches it (N3, P13). The C2 verdict stands on its frozen predicate and is reported with this gap.
- **C1 kill-power (M11, HIGH).** A same-content symlink retarget is not a matrix row; a read-through symlink hasher survives the frozen matrix. The landed writer refuses it (`w1/S65MutKill/m3probe-landed.out`).
- **Mode permission bits only (M12, HIGH).** Setuid, setgid and sticky bits are masked out (`st_mode & 0o777`); `755 → 4755` and `644 → 4644` are accepted. Porcelain is blind to those bits too. The four frozen arms refuse.
- **C2 after-wording S3 (M9).** "a file edited, while the wrapped command runs is refused" is true for tracked and untracked content visible to porcelain and the snapshot. It is false for a transient edit restored before the snapshot (matrix row T4, accepted by design) and for a gitignored in-run edit (critic probe). C2 checks marker presence, not statement breadth.
- **Predicate sentences overreach (critic M1, M2).** The live-marker docstring example ("returned") counts live; the dead-token selftest does not exercise that path. V1's `expected_class` is the generic `lane worktree is dirty`, so V1 does not show that the override was the cause; V2's fixture contains no untracked file (it tests a clean tree with the concealing config).
- **Separability (critic §5): NOT SEPARABLE as written.** C2's green depends on C1's landed writer bytes (its REQUIRED markers and after-literals name refusal tokens that exist only at `022cf979`); C1 does not depend on C2. Stated here as the named limit the prereg did not state.
- **Q59 instrument (M8).** `souji-axis-check.py` refuses this prereg (no MACHINE BLOCK). The axis was judged by hand; this does not satisfy Q59.
- **Counter build-failure path (critic L2).** A `CaseError` increments no counter; only `all_new_match=False` sets EXIT. A SUMMARY line can read Target-shaped with EXIT=1; the Target's EXIT clause catches it.
- **Class check is a stderr substring (critic L3, mutation seat).** A writer printing every class token in every refusal would pass the class column.
- **C1 regress fixture is taken from the lane clone's HEAD (critic L1).** Divergence from the base blob is reported, not fatal; currently `match`.
- **N4/N2 probe output incomplete (critic L5).** Some `n4-R`/`n4-C` lines have empty stderr (the `head` read a path that did not exist at the time); rc and output existence are recorded.
- **Sentinel F1–F7** (see `## Named limits` above and `## Routed to round 66`).
