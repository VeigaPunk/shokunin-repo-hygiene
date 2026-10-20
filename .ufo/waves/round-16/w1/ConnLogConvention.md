# ConnLogConvention — round 16 LOG entries (draft)

Seat `SoujiR16.ConnLogConvention` (connector, leaf). Owned file: this report.
Draft only: `LOG.md` was read, never edited; the lane's correction discipline
(`LOG.md:31-32`) makes new entries append-only and L1 owns the append.

STATUS: draft complete; three append-ready LOG entries below; `LOG.md` not modified; no census, fixture, gate or test run by this seat.

## Axes (named)

- **A1 calibration** — the judged axis (lowest, 7). The durable record must
  state what was measured, at which revision, and what a green means.
- **A2 traceability** — every name, number and byte in an entry resolves to a
  committed artifact or an exact command.
- **A3 correction fidelity** — corrections are new entries; the r15 seat's
  reported failure must survive verbatim, not as "unverified candidate".
- **A4 vacuity resistance** — a green gate run must prove it scanned a
  non-empty set; a run over an uncommitted wave directory proves nothing.
- **A5 no-harm on operability/coverage** — entries add no code, no source
  rows, and no claim beyond the declared surface.

## Evidence measured by this seat

Parse ladder, measured on committed bytes (`git show <rev>:tools/souji-census.sh`
piped to `bash -n`; no copy written):

| arm | revision | census blob sha256 | `bash -n` |
|---|---|---|---|
| pre-harm | `a31642d14006830ec62edf40b0354c3699728c4a` | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` | 0 |
| r14 harm | `cc2168325768d5356a82c039dcdf787377c55784` | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` | 0 |
| r15 baseline | `b410186cea626a67c92396ac58fbd57fb86876ac` | `dab4122c997db9b921e036ec8e2adf4c0e4743d8722ba9b2a28739bda9397810` | **2**, line 1368 |
| changed | `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` | 0 |

Worktree `tools/souji-census.sh` is byte-identical to `cbf688a`
(`git diff --quiet` exit 0; `sha256sum` `fed43c71…`), so the changed arm is
the landed bytes.

Other measured facts:

- `census/round-16/c1-matrix.json` (untracked at read time) records four arms:
  pre-harm selftest 36/36, r15-config 12/20 failed, r14-boundary 10/12 failed;
  r14-harm selftest 38/38, 16/20 failed, 0/12 failed; r15-baseline `bash -n`
  2, ShellCheck 1 (4 findings), selftest rc 2 with no tally, 20/20 and 12/12
  failed; changed selftest 38/38, 0/20 and 0/12 failed, ShellCheck 0.
- `census/round-16/live-fleet.json` (untracked, L1-run, root
  `/home/vgpnk/Projects/shokunin`): `cc21683` and `cbf688a` both rc 0, 23
  rows, 0 stderr lines, `rows_identical_excluding_mtime: true`; `b410186`
  recorded as `bash -n` rc 2, "cannot produce a census"; pre-harm explicitly
  `not_run` because it lacks hooks/fsmonitor neutralization.
- Fixture semantics: `tests/fixtures/r15-census-config.py:168-175`
  (`CASE_CLASSES`) maps 20 ids: benign 01/04/06/07/09/10/12/13/15/16,
  refusal 02/11/17/19, degrade 03, preserve 05/18/20, safety 08/14. The
  matrix's per-case observations match: 02 `path-protected:include-protected`,
  11 `path-protected:git-config-unsupported`, 19 `path-protected:credential-store`,
  17 `path-protected:include-protected`, 03 `config-unsupported:git-config-unparsed`
  with exit 0, 14 `status-skipped:filter-driver-bound`, 20 malformed exit 2
  with no finding (the matrix records the last sub-invocation only).
- Gate contract (from `.ufo/waves/round-16/w1-spec.json`, item 0): CLI
  `--root LANE --rev REV --round N [--base REV]` / `--selftest`; finding ids
  `LG-PARSE-REG`, `LG-MISSING-REG`, `LG-PARSE-CHANGED`, `LG-FROZEN-PIN`,
  `LG-SEAT-UNCARRIED`; `SUMMARY findings=K checked_reg=A checked_pins=B
  checked_markers=C`; exit 0/1/2. `LG-SEAT-UNCARRIED` scans every `*.md`
  under `.ufo/waves/round-N/` **at REV** against `corpus/lessons/round-N.md`.
- `tools/souji-landing-gate.py` and `tests/fixtures/r16-landing-gate.py` were
  **absent** in the worktree at read time; all gate outputs below are
  landing-fill cells, not observations.
- `b410186:.ufo/waves/round-15/w1/ConfigRepair.md` exists (`git cat-file -e`
  exit 0). `cbf688a:.ufo/waves/round-16/w1/swarm-registry.json` does not
  (`cat-file` exit 128), so `.ufo/waves/round-16/` is untracked there.
- `ConfigRepair.md:7-13` contains exactly three gate-marker lines (7, 9, 11,
  listed below). `corpus/lessons/round-15.md` contains zero `STATUS` lines
  and zero occurrences of the reported failure text (`grep -c` = 0).
- Frozen pins, current bytes: `tools/souji-census.sh` pinned `b5187351…`
  matches no committed revision; `tests/fixtures/r15-census-config.py` pinned
  `6314d45d…` but is now `9151cde8…`; `tests/fixtures/r14-census-boundary.py`
  pinned `e6a984b1…` still matches; `record_sha256` `4749ad07…` matches its
  `record.json`. `expected.json` blob is `93e48ab6…` at both `cbf688a` and
  worktree.
- `SKILL.md:138` (gate-registry row) and `SKILL.md:167` (repeatable fleet
  census line) cite `tools/souji-census.sh`.
- `LOG.md` uses prose and bullets, no tables (`grep -c '^|' LOG.md` = 0); the
  one existing `Re-verification (…):` precedent is `LOG.md:479`. The drafts
  below therefore use prose bullets, not tables.

## Contradictions and second-order effects

1. **The declared C1 wording is too flat.** "Only a protected-namespace reach
   keeps whole-run exit 2" is not what the fixture shows: R15CFG-20 also exits
   2 for a malformed `--compare` baseline (usage class). The draft narrows the
   sentence to configuration-value-driven exits.
2. **"Green at round end" is vacuous today.** The gate reads committed bytes
   via `git archive REV`, and `.ufo/waves/round-16/` is untracked at
   `cbf688a`. A `--round 16` run whose revision predates the committed wave
   reports has `checked_markers=0`: `LG-SEAT-UNCARRIED` cannot fire. Green
   must carry the SUMMARY counts, and the ending revision must be taken after
   the wave `.md` files are committed.
3. **C2 green is coupled to R4.** At `cbf688a` the frozen pins are stale
   (census and the revised fixture), so the gate must exit 1 with exactly two
   `LG-FROZEN-PIN` findings until the re-pin lands. Green is therefore also
   evidence that R4 landed; an intermediate red at `cbf688a` is expected and
   is not a gate defect. [INFERENCE from the pinned contract; the gate was
   absent, so this is unrun.]
4. **Carry obligation reaches this seat.** `LG-SEAT-UNCARRIED` scans every
   `.md` under `.ufo/waves/round-16/`, including this report. The correction
   entry must quote the r15 seat lines, so this report carries three marker
   lines; each must appear verbatim in `corpus/lessons/round-16.md` or the
   ending gate run is red. That is the mechanism working as designed (R3),
   but it means the lesson draft must be written after the last seat report,
   not before.
5. **"Append-only" vs. the sweep.** `LOG.md:31-32` forbids rewriting earlier
   entries, while the r15 closure asks the correction to sweep every mention.
   The draft reconciles this the way r13/r14 did: append correction notes to
   `SKILL.md`, `SCORECARD.md` and the r15 lesson; never edit the r15 bytes.
6. **`--selftest` is not held-out evidence.** A self-written gate tested by its
   own self-test is tautological; the external fixture and the time-held-out
   r15 replay are the discriminating evidence. Both are recorded separately.
7. **The marker regex over-fires on honest command logs.** The contract
   requires every seat to list its shell commands verbatim; any seat that
   greps for the marker wording (the natural way to verify carry) puts the
   literal phrases into its own report. This report does exactly that: six
   `grep` invocations in `## Commands` contain the marker phrases, so if the
   gate scans fenced blocks they become six additional carry obligations on
   `corpus/lessons/round-16.md` — unrelated to any seat failure. The set is
   self-amplifying: verifying carry adds lines that a later verification pass
   must then carry. Resolve it in
   the gate, not by hiding commands: skip fenced code blocks in
   `LG-SEAT-UNCARRIED` and report the skipped count in `SUMMARY`, so the
   exclusion is visible and auditable. Dodge risk (a seat fenced away a real
   failure) is real and must be traded explicitly in the lesson: the pinned
   regex on prose is the floor, and the fixture should include one fenced
   marker case to pin the chosen policy.

## Proposed move (one bounded)

**Make the C2 green SUMMARY the joint discharge record for R1/R3/R4, with a
non-vacuity cell, and cite its `LG-PARSE-REG` pass as the C1 entry's parse
re-check at the landing revision.**

Concretely, three edits already embodied in the drafts:

1. Entry (c) records the whole `SUMMARY` line, not just exit 0, and requires
   `checked_markers > 0`, `checked_pins` equal to the number of frozen `files`
   entries at REV (currently 3 plus the record), and `checked_reg` equal to
   the count of SKILL-cited paths. A green without those numbers is not
   recorded as green.
2. Entry (b) cites entry (c)'s `LG-PARSE-REG` pass at the ending revision as a
   second, independently implemented parse check of the landed census, while
   keeping the fixture matrix and the fleet run as the behavioural basis.
3. Entry (a) states the landing-state convention going forward: an entry that
   lands a registry-cited script records its `bash -n` result at the landed
   revision in the same entry. This is the r15 defect inverted — the record
   that admitted the break now has to name the parse state.

Why it is non-obvious: it rewires the evidence topology from three independent
entries to one mutually checking set, and it closes the vacuity hole that a
plain "green at round end" would leave open (the wave directory is untracked
today, so a green run right now would prove nothing about seat carry). It also
resolves the ordering hazard: the gate must run after the last wave report is
committed and after the re-pin, so its revision is the ending HEAD.

## Risks

- **Single point of failure.** Three entries citing one gate share its bugs.
  Mitigation: behavioural evidence stays with the fixture matrix and the fleet
  run; the external fixture (`tests/fixtures/r16-landing-gate.py`) supplies
  held-out cases; the LOG says the gate checks parse/pins/carry, not behaviour.
- **Late seat reports flip green to red.** Mitigation: run last, and have the
  lesson carry marker lines as they land (second-order effect 4).
- **Self-authored gate.** It was designed knowing the r15 defects; the r15
  replay is time-held-out, not design-held-out. The lesson must say so.
- **Marker dodging.** Rewording a seat failure evades the pinned regex; the
  gate is a floor, not a ceiling. Disclose in the lesson.
- **Marker over-fire.** Verbatim command logs spell the marker phrases; a
  whole-file scan turns them into phantom carry obligations and rewards hiding
  commands. Mitigation: skip fenced blocks and report the skipped count, or
  record the false-positive class openly (contradiction 7, carry contingency).
- **Count semantics.** "checked_pins" must mean frozen `files` entries plus
  `record_sha256`, or the guard is a vibe. The drafts say so explicitly.

## Verification for L1

After the gate and fixture exist and the re-pin has landed:

1. `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --selftest`
   → expect `SELFTEST pass=X fail=Y`, exit 0; paste both verbatim.
2. Same gate `--root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b410186cea626a67c92396ac58fbd57fb86876ac --round 15`
   → expect exit 1 and the three findings `LG-PARSE-REG` (`tools/souji-census.sh`),
   `LG-FROZEN-PIN` (`tests/fixtures/r15-preservation-frozen`), `LG-SEAT-UNCARRIED`
   (`.ufo/waves/round-15/w1/ConfigRepair.md`).
3. Same gate `--rev <ENDING_REV> --round 16` after committing the wave reports
   and the re-pin → expect exit 0 with `checked_markers>0`; paste SUMMARY.
4. Record the fenced-block policy actually implemented (skip with a reported
   skipped count, or whole-file) and apply the matching carry contingency.
5. Confirm the three marker lines below appear verbatim in
   `corpus/lessons/round-16.md` at that revision.
6. `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py --changed cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --output <new.json>`
   → re-derives the four-arm matrix; compare with `c1-matrix.json`.

## Draft LOG entries (append-ready)

Append these three sections to `LOG.md` only after the landing-fill cells are
filled and L1 acceptance is recorded. Do not append with `[L1-FILL]` left in.

````markdown
## 2026-10-20 — round 16 correction: r15 landed a non-parsing census

Appended correction, not a rewrite of the r15 entries (`LOG.md:31-32`).
Commit `b410186cea626a67c92396ac58fbd57fb86876ac` landed
`tools/souji-census.sh` as blob
`dab4122c997db9b921e036ec8e2adf4c0e4743d8722ba9b2a28739bda9397810`;
`bash -n` on those bytes exits 2 at line 1368. The pre-harm arm `a31642d`
(`6a000c59…`) and the r14 harmed arm `cc21683` (`fcff8b05…`) both pass
`bash -n`, so the break is r15-only and was admitted by that landing.
Warning-level ShellCheck (0.11.0) reports four findings on the landed
bytes; the r15 closure locates SC1046 at line 1324, the unclosed `if` in
`list_repos` (`corpus/lessons/round-15-verifier-spotcheck.md`).

The second defect is disclosure. Seat `SoujiR15.ConfigRepair` reported the
state at `.ufo/waves/round-15/w1/ConfigRepair.md:7-13`:

    ## STATUS: INCOMPLETE — file has an unresolved syntax error

    `bash -n` reports: `line 1368: syntax error near unexpected token '}'` (the
    `}` closing `list_repos`). Edits were in flight when the operator wrap-up
    halted work. **The file in tree does NOT parse.** L1 must either complete the
    repair or revert to `cc21683` before any acceptance run; do not ship this
    state as working.

The landing record never carried it. `corpus/lessons/round-15.md` has zero
`STATUS` lines and no occurrence of the reported failure text; its line 95
calls the source an "unverified candidate, not a working repair". The r15
LOG entries report the claims as unprovable without naming the non-parsing
state. The seat file is tracked at `b410186` (`git cat-file -e` exit 0), so
the omission happened at landing, not in the artifact.

Sweep, appended not rewritten: `SKILL.md:138` gate-registry row and
`SKILL.md:167` repeatable-census line; `SCORECARD.md` operability and
calibration rows and the "Round-14 outside disposition" paragraph;
`corpus/lessons/round-15.md` §Final disposition. The measured repair is the
C1 entry below; the r15 per-axis "numeric delta 0" wording is superseded
there by measured values without touching the r15 bytes.

Landing-state convention from this round: an entry that lands a
registry-cited script records its `bash -n` result at the landed revision in
the same entry. That is the inverse of this defect and the only durable
guard that does not depend on a later reader re-running history.

Re-verification (parse state): extract each arm with
`git -C <lane> show <rev>:tools/souji-census.sh > <tmp>/census.sh` and run
`bash -n <tmp>/census.sh`; `a31642d` and `cc21683` exit 0, `b410186` exits 2
at line 1368, `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` exits 0. The same
four-arm result and byte digests are in `census/round-16/c1-matrix.json`,
re-derived by the C1 counting command.

## 2026-10-20 — round 16 measured C1 evidence: parsing value/effect-aware census

Changed revision `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`:
`tools/souji-census.sh` blob `fed43c71…`, revised fixture
`tests/fixtures/r15-census-config.py` `9151cde8…`, counting command
`census/round-16/run-matrix.py` `87c9af0c…`. The worktree bytes equal the
commit (`git diff --quiet` exit 0).

Counting command, run by L1, result `census/round-16/c1-matrix.json`:

`python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py --changed cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --output <new.json>`

Each arm runs the same current fixtures, its own `--selftest`, `bash -n` and
warning-level ShellCheck. Observed:

- pre-harm `a31642d` (`6a000c59…`): parse 0, ShellCheck 0, selftest 36/36;
  r15-config 12/20 failed, r14-boundary 10/12 failed.
- r14 harmed `cc21683` (`fcff8b05…`): parse 0, ShellCheck 0, selftest 38/38;
  r15-config 16/20 failed, r14-boundary 0/12 failed.
- r15 baseline `b410186` (`dab4122c…`): `bash -n` 2, ShellCheck 1 with four
  findings, selftest rc 2 with no tally; both fixtures fail every id.
- changed `cbf688a` (`fed43c71…`): parse 0, ShellCheck 0, selftest 38/38;
  r15-config 20/20, r14-boundary 12/12, both exit 0.

The ladder is the evidence, not a scalar. Pre-harm loses 10 of 12 namespace
cases and 8 of 20 config cases; the r14 harmed arm keeps all 12 namespace
cases and refuses 16 of 20 config cases; the r15 baseline cannot start; the
changed arm keeps every namespace case and passes every config case. R14's
rejected-harmed config debt (routed R2) is discharged on this measured
surface only — synthetic fixtures plus the read-only fleet run — not as a
general value-support claim.

Fixture behaviour at `cbf688a`, by case class (schema at
`tests/fixtures/r15-census-config.py:168-175`): benign 01/04/06/07/09/10/12/
13/15/16, refusal 02/11/17/19, degrade 03, preserve 05/18/20, safety 08/14.
Refusals 02/11/17/19 exit 2 `path-protected:include-protected`,
`path-protected:git-config-unsupported`,
`path-protected:include-protected`, `path-protected:credential-store`; 03
turns a could-not-evaluate config into one `error` row with exit 0; 14 emits
`status-skipped:filter-driver-bound` for that repository only; 16 emits the
exact mixed-fleet row set and 17 refuses the mixed fleet whole; 08 records no
configured hook or fsmonitor sentinel run; 12 never consumes
`alternateRefsCommand`; 09/10 exercise complete-repo promisor/partialClone and
worktreeConfig values; 20's malformed baseline exits 2 with no finding (the
matrix records the last sub-invocation). Whole-run exit 2 is kept only for a
protected/unsupported-namespace reach and for the pre-existing usage or
malformed-baseline class; no benign value aborts its repository or hides
unaffected peer rows.

Real read-only fleet run, same root, `census/round-16/live-fleet.json`:
`cc21683` and `cbf688a` both exit 0 with 23 rows, zero stderr lines and
identical rows excluding mtime; `b410186` cannot run (`bash -n` exit 2). The
pre-harm arm was deliberately not run live because it lacks hooks/fsmonitor
neutralization and could execute sibling repositories' configured commands;
that absence is a recorded limit, not a pass.

Axis verdict: operability improved on the declared surface, replacing the r15
row's unprovable state and its "numeric delta 0"; the score row is updated by
the closing entry. Calibration follows the C2 entry. Coverage unchanged.
Certification stays OFF, K5 HELD; no deletion, no operator-sweep content and
no sibling mutation.

Re-verification (behavioural): re-run the counting command with
`--changed cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (or `WORKTREE`) and a
new output path; it refuses to overwrite an existing file. Compare the four
arm blocks and per-case verdicts against `c1-matrix.json`. The live-fleet
artifact is L1-run only and is never a seat probe.

## 2026-10-20 — round 16 measured C2 evidence: mechanical landing gate

New `tools/souji-landing-gate.py` (stdlib only; extracts committed bytes
with `git -C LANE archive REV` into a private `/var/tmp` snapshot removed in
`finally`; runs only `bash -n` and `ast.parse`, never repository code). CLI
`--root LANE --rev REV --round N [--base REV]` and `--selftest`; per-finding
TSV `ID<TAB>path<TAB>detail`, then
`SUMMARY<TAB>findings=K<TAB>checked_reg=A<TAB>checked_pins=B<TAB>checked_markers=C`;
exit 0 clean, 1 findings, 2 could-not-evaluate. Finding ids: LG-PARSE-REG,
LG-MISSING-REG, LG-PARSE-CHANGED, LG-FROZEN-PIN, LG-SEAT-UNCARRIED.

Historical red over the r15 landing:
`python3 tools/souji-landing-gate.py --root <lane> --rev b410186cea626a67c92396ac58fbd57fb86876ac --round 15`
exits 1 and reports [L1-FILL: exact sorted TSV]. The findings are the three
defects the non-author closure found by hand:

- `LG-PARSE-REG` `tools/souji-census.sh`: `bash -n` exit 2 at line 1368,
  blob `dab4122c…`.
- `LG-FROZEN-PIN` `tests/fixtures/r15-preservation-frozen/expected.json`:
  census pin `b5187351…` matches no committed revision (`cc21683`
  `fcff8b05…`, `b410186` `dab4122c…`, `cbf688a` `fed43c71…`), while
  `record_sha256` `4749ad07…` does match its `record.json`.
- `LG-SEAT-UNCARRIED` `.ufo/waves/round-15/w1/ConfigRepair.md:7-13`: three
  marker lines, none present in `corpus/lessons/round-15.md`, which also has
  zero `STATUS` lines.

Green at round end, after the R4 re-pin and after the last wave report is
committed: `--rev <ENDING_REV> --round 16` exits 0 with
[L1-FILL: SUMMARY, including checked_reg / checked_pins / checked_markers];
`--selftest` prints `SELFTEST<TAB>pass=X<TAB>fail=Y` and exits 0,
[L1-FILL]. Non-vacuity is part of the record: `checked_markers` must be
greater than zero, `checked_pins` equals the frozen `files` entries plus
`record_sha256`, and the r15 replay must still exit 1 — otherwise the green
run scanned no seat reports and proves nothing. The wave reports are
untracked at `cbf688a` (`.ufo/waves/round-16/w1/swarm-registry.json` is
absent from that tree), so the ending revision must postdate their commit.

The gate's own selftest is not held-out evidence; `tests/fixtures/r16-landing-gate.py`
supplies the external replay and synthetic held-out cases, tally
[L1-FILL]. The gate checks parse state, frozen pins and seat carry only; it
does not authenticate behaviour, which stays with the C1 fixture matrix and
fleet run. Sourced on the GNU Bash `set -n` manual row opened this round in
`corpus/SOURCES.md` (row number assigned by the round-16 sources commit): the
shell check is the documented no-execution syntax read, not a heuristic.
At `cbf688a` the gate is expected to exit 1 with exactly two `LG-FROZEN-PIN`
findings until the re-pin lands; that intermediate red is expected and is not
a gate defect. [L1-FILL: confirm at the recorded revisions.]

Axis: calibration improved, since the three r15 landing defects are now
detected mechanically from committed bytes. Operability and coverage
unchanged. Certification stays OFF, K5 HELD.
[L1-FILL: score/trend sentence for the closing entry.]
````

## Carry obligation for the round-16 lesson

Because this report lives under `.ufo/waves/round-16/` and is committed, the
ending gate run (`--round 16`) requires each of the following lines, stripped,
to appear verbatim in `corpus/lessons/round-16.md`. They are the r15 seat's
own lines; copy them byte-for-byte (including the em dash, backticks and the
spacing):

    ## STATUS: INCOMPLETE — file has an unresolved syntax error

    `bash -n` reports: `line 1368: syntax error near unexpected token '}'` (the

    halted work. **The file in tree does NOT parse.** L1 must either complete the

The first and third lines are the ones carrying the failure wording; the
second is the location line. Do not reflow them. If the lesson is drafted
before later wave reports land, its marker section must be extended to carry
those later `STATUS:` lines too — the gate scans every `*.md` in the wave
tree, not only this report.

Contingency, because of contradiction 7: if `LG-SEAT-UNCARRIED` scans fenced
code blocks, this report contributes six more obligations — the `grep`
invocations in `## Commands` that spell the marker wording. They are ordinary
shell lines and must not be pasted into a lesson. The recommended resolution
is the gate change stated above (skip fences, report the skipped count); if
the gate owner keeps a whole-file scan, L1 must either carry those four shell
lines or record them as a known false-positive class in the lesson. That
choice is part of the C2 record, not a silent omission.

Non-shell reads: `skill://godspeed`; `LOG.md:20-45`, `:470-485`,
`:555-640`, `:640-700`, `:-120`; `census/round-15/ConfigRepair.md` (absent at
`census/round-15/`); `.ufo/waves/round-15/w1/ConfigRepair.md`;
`corpus/lessons/round-15-verifier-spotcheck.md`; `census/round-16/run-matrix.py`;
`census/round-16/c1-matrix.json`; `census/round-16/live-fleet.json`;
`.ufo/waves/round-16/w1/DraftReportSkeleton.md`;
`tests/fixtures/r15-preservation-frozen/expected.json`; `SCORECARD.md:1-45`,
`:49-106`; `SKILL.md:130-172`; `corpus/QUALITY.md:52-70`;
`.ufo/waves/round-16/w1/swarm-registry.json`.

Tool installs/updates by this seat: none. `census/operator-sweep-20261019/`
was not opened, listed, grepped or copied. No sibling repository, host
service, credential path or `.ufo/state` was touched. No commit, stage or
reset was performed.

## Commands

Every shell command run by this seat, verbatim, in order (failed commands
included). Each ran in a fresh shell; `cd` is shown where used. Post-
finalization audits of this report used the read/grep tools, not the shell,
so the self-amplifying marker obligation described in contradiction 7 does
not grow past this list.

```
wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md && grep -n -i "correction" /home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md
find /home/vgpnk/Projects/shokunin/souji-shokunin -name 'ConfigRepair.md' -o -name 'round-15-verifier-spotcheck.md' 2>/dev/null
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>/dev/null; echo ---; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh 2>&1; echo ---; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -6
grep -n -iE 're-verif|reverif|re-verify|Revision|pin' /home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md | tail -40; echo ---; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/ 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "import json;d=json.load(open('census/round-16/c1-matrix.json'));print(json.dumps({k:{kk:d[k][kk] for kk in ('rev','sha256') if kk in d[k]}|{'bash_n':d[k]['bash_n'],'shellcheck':d[k]['shellcheck_warning'],'selftest':d[k].get('selftest'),'r15':(d[k]['r15-config']['total'],d[k]['r15-config']['failed'],d[k]['r15-config']['rc']),'r14':(d[k]['r14-namespace']['total'],d[k]['r14-namespace']['failed'],d[k]['r14-namespace']['rc'])} for k in d['arms'] if k!='changed'},indent=1))"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix.json'))
a=d['arms']
for k,v in a.items():
    print(k, v.get('rev'), v.get('sha256','')[:12], 'bash_n', v['bash_n']['rc'], 'sc', v['shellcheck_warning'], 'self', v.get('selftest'), 'r15', (v['r15-config']['total'],v['r15-config']['failed'],v['r15-config']['rc']), 'r14', (v['r14-namespace']['total'],v['r14-namespace']['failed'],v['r14-namespace']['rc']))
"
grep -n "set -n\|bash -n\|GNU Bash\|S0[4-9][0-9]" /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | tail -25; echo ---; sed -n '470,485p' /home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md
grep -n "C1\|C2\|set -n\|landing-gate\|correction" /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/prompts/souji-round-16.md 2>/dev/null | head -40; echo ---; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>/dev/null
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/prompts/ 2>/dev/null | tail -8
grep -c '^| S[0-9]' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md; grep -oE '^\| S[0-9]+' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | tail -3; echo ---; grep -n 'set -n' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/*.md 2>/dev/null | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum && git diff --quiet cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh; echo "diff_rc=$?"; bash -n tools/souji-census.sh; echo "bashn_rc=$?"; git status --porcelain | grep -v operator-sweep
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show --stat --oneline cbf688ab2ab28e38103e5a9417ca525b5f2ed423 | head -20
grep -n -A6 -iE '"SoujiR16\.(LandingGate|LandingGateFixture|DraftR15Correction)"' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/swarm-registry.json | head -60
grep -n -iE 'set -n|landing-gate|SOURCES|S043' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/swarm-registry.json | head -30
grep -n -E 'R15CFG-|EXPECTED|observed_exit|observed_finding|CASE' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py | head -50
grep -n -E 'R14C2-|EXPECTED|CASE' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py | head -30
grep -n '^' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-15/w1/ConfigRepair.md | sed -n '5,16p'
grep -rn "sweep every mention" /home/vgpnk/Projects/shokunin/souji-shokunin/PROTOCOL.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-15.md 2>/dev/null; echo ---; grep -n '^' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-15.md | sed -n '90,100p'
grep -n -iE 'correction|sweep|re-verif' /home/vgpnk/Projects/shokunin/souji-shokunin/PROTOCOL.md | head -20
grep -n -iE 're-verif|verbatim|disclosure|known failure' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD | grep -iE 'PROTOCOL|STATE|SHONEN' | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186cea626a67c92396ac58fbd57fb86876ac:tools/souji-census.sh | sha256sum && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sha256sum && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:census/round-16/run-matrix.py | sha256sum && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r14-census-boundary.py | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && bash -n <(git show b410186cea626a67c92396ac58fbd57fb86876ac:tools/souji-census.sh) 2>&1; echo "b410186 bashn_rc=$?"; bash -n <(git show cc2168325768d5356a82c039dcdf787377c55784:tools/souji-census.sh) 2>&1; echo "cc21683 bashn_rc=$?"; bash -n <(git show a31642d14006830ec62edf40b0354c3699728c4a:tools/souji-census.sh) 2>&1; echo "a31642d bashn_rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json;d=json.load(open('census/round-16/c1-matrix.json'))
for k,v in d['arms'].items():
    print(k, '|', v.get('rev'), '|', v.get('sha256'), '|', json.dumps(v['shellcheck_warning']))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c -iE 'syntax error|does not parse' LOG.md corpus/lessons/round-15.md; ls -la .ufo/waves/round-16/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -o '.\{0,150\}set -n.\{0,300\}' .ufo/waves/round-16/w1-spec.json | head -6
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -o '.\{0,200\}landing-gate.\{0,400\}' .ufo/waves/round-16/w1-spec.json | head -6
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items(): yield from walk(v,p+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): yield from walk(v,p+'/'+str(i))
    elif isinstance(o,str) and 'souji-landing-gate.py --root LANE' in o:
        yield p,o
for p,s in walk(d):
    print('PATH',p); print(s[:3000]); break
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -e b410186cea626a67c92396ac58fbd57fb86876ac:.ufo/waves/round-15/w1/ConfigRepair.md; echo "r15seat_at_b410186_rc=$?"; git cat-file -e cbf688ab2ab28e38103e5a9417ca525b5f2ed423:.ufo/waves/round-16/w1/swarm-registry.json; echo "r16wave_at_cbf688a_rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
s=d['items'][0]['prompt']
print(len(s))
print(s[2400:6000])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
s=d['items'][0]['prompt']
print(s[1400:2600])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -o '.\{0,300\}LG-SEAT-UNCARRIED.\{0,500\}' .ufo/waves/round-16/w1-spec.json | head -4
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -o '.\{0,200\}verbatim.\{0,400\}' .ufo/waves/round-16/w1-spec.json | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'souji-census\.sh' SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '(?i)\bSTATUS:\s*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b' .ufo/waves/round-15/w1/ConfigRepair.md --ignore-case; echo ---; grep -c 'STATUS' corpus/lessons/round-15.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E '\bSTATUS:[[:space:]]*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b' .ufo/waves/round-15/w1/ConfigRepair.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-preservation-frozen/record.json | sha256sum && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-preservation-frozen/expected.json | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1; git status --porcelain | grep -v '^?? census/operator-sweep'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E '\bSTATUS:[[:space:]]*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b' .ufo/waves/round-16/w1/DraftReportSkeleton.md .ufo/waves/round-16/w1/DraftSkillSection.md; echo "rc=$?"; sha256sum tests/fixtures/r15-preservation-frozen/expected.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json;d=json.load(open('census/round-16/live-fleet.json'))
print(list(d))
for k,v in d['arms'].items():
    print(k, v['rev'], v['tool_sha256'][:12], v['result'], 'stderr',v['stderr_lines'],'rows',v['row_count'], 'summary', v.get('summary'))
print({k:v for k,v in d.items() if k!='arms'})
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c '^|' LOG.md; grep -n '^## 2026' LOG.md | tail -8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E '\bSTATUS:[[:space:]]*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b' .ufo/waves/round-16/w1/ConnLogConvention.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## ' .ufo/waves/round-16/w1/ConnLogConvention.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E '\bSTATUS:[[:space:]]*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b' .ufo/waves/round-16/w1/ConnLogConvention.md | sed 's/^[0-9]*://' | sed 's/^[[:space:]]*//' | sort -u
```
