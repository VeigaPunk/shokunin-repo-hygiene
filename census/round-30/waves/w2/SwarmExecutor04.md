# SwarmExecutor04 — r30 w2, operability no-harm sweep (fixtures at base vs lane tip)

## Status

STATUS: PASS — the assigned attack ran to completion: 18 C1-enumerated rows plus the 5 seat-named
fixtures/selftests executed at both 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b and
9dcd367655fc28ba73d679a0e2cadaff96d2bcb8 in one origin-less scratch clone. Result of the attack:
**0 operability harms** — every command's (rc, last stdout digit-bearing line) pair is identical at
base and tip; the two commands that are red are red at base as well. PASS denotes that the attack ran,
not that a lane claim held.

## Evidence

Clone `/fast/scratch/hyaku/souji-r30/NoHarmFixtures/c` (`git clone -q --no-local` of the lane, origin
removed, scratch identity set via `git -C` config). Per revision: `git checkout -qf REV` then
`git clean -fdxq`, run from the clone root, `timeout 900`, `TMPDIR` under the scratch dir. Tooling:
git 2.56.0, Python 3.14.8, jj 0.45.1. No installs, no pacman/uv/npm transactions; pacman guard
respected.

`deliver-no-harm-fixtures.tsv` (26 rows: 18 C1 rows + 5 seat-named + 3 supplementary):

- 21/23 commands green at both revisions; identical rc and identical last digit-bearing stdout line
  for 23/23.
- red at both revisions (not harms): `R16` `rc=2`, `E5` `rc=2`, both with empty stdout
  (sha256 `e3b0c44298fc1c14…`); supplementary `S3` likewise `rc=2`.
- supplementary green at both: `S1` `cases=9 pass=9 control=FALSE-GREEN-REJECTED` (r24-coverage-agreement
  with `--tool`), `S2` `cases=12 pass=12 control=FALSE-GREEN-REJECTED` (r26-axis-check with `--tool`).
- 5 commands differ in bytes while agreeing on rc and last line — `R04`, `R05`, `R08`, `R13`, `R18`;
  all diffs reviewed and are mktemp fixture paths, wall-clock utc stamps, synthetic commit ids, and one
  disclosed err-text reword (Finding 4).
- trees were clean (`git status --porcelain` empty) after each revision's sweep, so no fixture leaves
  tracked or untracked residue in the clone.
- wall time per command: max base 17 s (`R07`), max tip 16 s; no command regressed in cost beyond the
  1 s mktemp noise band.

Supplementary overlay sweep (`deliver-no-harm-fixtures-worktree-tip.tsv`): committed tip overlaid with
the lane's uncommitted worktree state at read time (3 files, sha256 recorded in the receipt) gives the
same 21 green / 2 red split and the same last lines — the pending edits move nothing.

R18 correction provenance, measured at the C1 landing commit with both counters (`--only R18`, both
`counter_rc=0`):

- v1 (`d4928ec:tools/souji-capability-agreement.py`): `observed=Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]` verdict `CORRECTED`.
- A3 (`9dcd367:tools/souji-capability-agreement.py`): `observed=cases=15 pass=15 control=TAMPER-REJECTED` verdict `MATCH`.
- both print `SUMMARY k1=0 k2=0 mismatches=0 … pointers=10` for the partial run.

## Findings

1. **No operability harm across the frozen command set.** 23/23 commands hold their rc and last
   stdout digit line between base and tip (`deliver-no-harm-fixtures.tsv`). This is the seat's target
   result: no green-at-base/red-at-tip command exists in the assigned set.

2. **`R16`'s frozen row argv is unrunnable as written.** `census/round-30/c1-rows.tsv` R16
   (`census/round-30/c1-rows.tsv:23`) names `python3 -B tests/fixtures/r24-coverage-agreement.py` with
   stated `9/9`; the fixture is argparse-mandatory and stderr says verbatim
   `r24-coverage-agreement.py: error: the following arguments are required: --tool` (rc=2, empty
   stdout) at **both** revisions. Wave 1 kept the row green with the append-only extension
   `cmd=python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py`
   (`SCORECARD.md:335`), and A3 permits an argv extension; my `S1` confirms that form prints
   `cases=9 pass=9 control=FALSE-GREEN-REJECTED` at both revisions. Defect is in the frozen row's
   command column, not in the tip.

3. **The seat-named `E5` command is likewise argument-incomplete.**
   `python3 -B tests/fixtures/r26-axis-check.py` exits 2 at both revisions with
   `r26-axis-check.py: error: the following arguments are required: --tool`; the `--tool` form (`S2`)
   is green at both (`cases=12 pass=12`). The assignment text, not the lane, omits the flag.

4. **C2's gate change rewords two selftest `err=` tails; the check surface did not shrink.**
   `python3 tools/souji-landing-gate.py --selftest` prints `SELFTEST pass=65 fail=0` at both revisions,
   and the 65 `CASE` ids are identical sets. Exactly two lines change, base
   `no .md reports under .ufo/waves/round-18/` vs tip `under .ufo/waves/round-18/ or census/round-18/waves/`
   (same for round-16). This is the disclosed A1 exception; it confirms the A1 `err=` exclusion in
   `regress_full` is load-bearing rather than cosmetic.

5. **`SCORECARD.md:336`'s R18 correction cites a usage banner that only the v1 counter can see.**
   The landed line records `observed=Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]`.
   Under v1 that is exactly what the counter observes (verdict `CORRECTED`); under A3 the observation
   is the green tally and the row is `MATCH` before any correction is consulted, while
   `tools/souji-capability-agreement.py:197` (`# A3: a usage/help/argparse banner is never an accepted observation`)
   would discard that banner. Both counters give `k1=0`, so the line is inert under A3 — a
   provenance note, not a target breach.

6. **The r30 lesson is not in the tip commit; the "final lane tip" state is dirty.** At read time
   `git status --porcelain` in the lane reports `M SKILL.md`, `M corpus/QUALITY.md`,
   `?? corpus/lessons/round-30.md`, and `git cat-file` against the tip answers
   `path 'corpus/lessons/round-30.md' exists on disk, but not in '9dcd367655fc28ba73d679a0e2cadaff96d2bcb8'`
   (file is 11104 bytes on disk). `9dcd367` itself carries only three record files
   (`c3-after-v1.txt`, `c3-after-v2.txt`, `m1-r29-carry-red-before.txt`). The prereg Frontier step
   requires the mined mistake in `corpus/lessons/round-30.md`, so any "at the final lane tip" reading
   must say whether it means the commit or the worktree; my sweep covers both and they agree
   (Evidence, overlay) — but the lesson bytes are unverifiable from committed state until landed.

7. **One empty fixture scratch dir survives.** `/var/tmp/souji-r29-wave-capture-fixture` is left as an
   empty directory (`du -sh` = 0, no entries) after `R18` at both revisions; the fixture traps its
   per-run `run.*` subtree (`tests/fixtures/r28-wave-evidence-capture.sh:53-54`) but not its base dir.
   `r26-axis-check` cleans its base. Identical at base, so not a harm; hygiene note only.

## Attack log

| # | Attack | Verdict |
|---|--------|---------|
| A1 | base-vs-tip sweep of all 18 C1 rows + 5 seat-named fixtures/selftests, clean tree per revision | HOLDS (0 harms, 23/23 identical rc and last line) |
| A2 | byte-diff review of the 5 outputs whose hashes differ, to catch a shrunken-but-green check surface | HOLDS (paths, timestamps, synthetic ids, one disclosed err reword; 65/65 selftest case ids equal) |
| A3 | R18 correction `observed=` banner re-measured under both v1 and A3 counters at 7b16731 | HOLDS (v1 CORRECTED, A3 MATCH, k1=0 both) |
| A4 | tip sweep repeated with the lane's uncommitted worktree files overlaid | HOLDS (identical verdicts; pending edits move nothing) |
| A5 | `R16` frozen argv and `E5` seat argv run literally | DEFECT-NOT-FATAL (rc=2 at base and tip; argument-incomplete invocation, not a regression) |
| A6 | fixture scratch residue + clone cleanliness after sweep | DEFECT-NOT-FATAL (empty `/var/tmp` base dir only; clone clean both revisions) |
| A7 | committed-vs-worktree divergence of the round's lesson and SKILL/QUALITY edits | DEFECT-NOT-FATAL (lesson absent from tip commit; flag for L1 before scoring "final lane tip") |

## Deliveries

- `.ufo/waves/round-30/w2/deliver-no-harm-fixtures.tsv` — per command and revision: rc, last digit
  stdout line, equality flags, stdout sha256 prefixes, stderr delta, harm verdict, note.
- `.ufo/waves/round-30/w2/deliver-no-harm-fixtures-worktree-tip.tsv` — supplementary tip+worktree
  overlay sweep with the three overlaid file hashes.
- `.ufo/waves/round-30/w2/receipt-noharm-R18-counter-v1-at-7b16731.txt`
- `.ufo/waves/round-30/w2/receipt-noharm-R18-counter-A3-at-7b16731.txt`

Scratch `/fast/scratch/hyaku/souji-r30/NoHarmFixtures/` removed after the receipts above were copied.
No lane commit, no `git add`, no `jj` mutation, nothing written outside the w2 directory and scratch.
